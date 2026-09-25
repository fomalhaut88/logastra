import os
import json
import asyncio
import logging
import traceback
from datetime import datetime, timedelta

import aiohttp
from croniter import croniter

from .db import Track, TrackStatus, AsyncSessionLocal, list_tracks, patch_track
from .log import save_log
from .handlers import get_handler_class


SLEEP = 5.0
TIMEOUT = 15.0

NOTIFIER_URL = "https://notifier.alexfomalhaut.com/notify"
NOTIFIER_TOKEN = os.getenv("NOTIFIER_TOKEN")


def get_utcnow_minute() -> datetime:
    return datetime.utcnow().replace(second=0, microsecond=0)


async def monitor():
    if not NOTIFIER_TOKEN:
        logging.warning("NOTIFIER_TOKEN is not set")

    last = get_utcnow_minute()

    while True:
        try:
            now = get_utcnow_minute()

            while last < now:
                last += timedelta(minutes=1)
                await monitor_step(last)

        except Exception:
            logging.error(traceback.format_exc())

        finally:
            await asyncio.sleep(SLEEP)


async def monitor_step(dt: datetime):
    async with AsyncSessionLocal() as session:
        tracks = await list_tracks(session, active_only=True)

    for track in tracks:
        if croniter.match(track.schedule, dt):
            asyncio.create_task(handle_track(track, dt))


async def handle_track(track: Track, dt: datetime):
    try:
        # Prepare the handling
        handler_class = get_handler_class(track.handler)
        options = json.loads(track.options or "{}")
        handler = handler_class(**options)
        coro = handler.process()

        # Handle the track
        try:
            await asyncio.wait_for(coro, timeout=TIMEOUT)
        except Exception as exc:
            logging.info(f"Track {track.name} failed: {str(exc)}")
            fail_detail = f"{exc.__class__.__name__}\n{str(exc)}\n\n" \
                          f"{traceback.format_exc()}".strip()
        else:
            logging.info(f"Track {track.name} checked successfully")
            fail_detail = None

        has_failed = (
            fail_detail is not None and track.status == TrackStatus.OK
        )
        has_resumed = (
            fail_detail is None and track.status == TrackStatus.FAILED
        )

        # Save the track
        async with AsyncSessionLocal() as session:
            track = await patch_track(session, track.id, {
                'status': (
                    TrackStatus.OK if fail_detail is None
                    else TrackStatus.FAILED
                ),
                'last_check': dt,
                'last_fail': track.last_fail if fail_detail is None else dt,
                'fail_detail': fail_detail,
            })

        # Log the check
        await save_log(track)

        # Send notification
        if track.notify:
            if has_failed:
                await notify(
                    f"Service {track.name} failed:\n\n```\n{fail_detail}\n```"
                )
            if has_resumed:
                await notify(f"Service {track.name} resumed")

    except Exception:
        logging.error(traceback.format_exc())


async def notify(text: str):
    try:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                NOTIFIER_URL, data=text,
                headers={"Authorization": f"Bearer {NOTIFIER_TOKEN}"}
            ):
                pass
    except Exception:
        logging.error(f"Could not send notification: {text}")
        logging.error(traceback.format_exc())
