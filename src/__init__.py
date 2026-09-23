import os
import logging
import asyncio
from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

VERSION = "0.1.0"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
APP_TOKEN = os.getenv("APP_TOKEN")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

from .schemas import VersionResponse, TrackResponse, TrackCreate
from .db import (
    init_db, get_db, list_tracks, info_track, create_track, patch_track,
    delete_track
)
from .log import init_log, close_log, load_last_logs, Check
from .monitor import monitor


security = HTTPBearer()


async def check_credentials(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> None:
    if credentials.credentials != APP_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authorization token.",
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_log()
    asyncio.create_task(monitor())
    yield
    await close_log()


router = APIRouter(dependencies=[Depends(check_credentials)])


@router.get("/tracks", response_model=list[TrackResponse])
async def tracks_list_view(
    db: AsyncSession = Depends(get_db)
) -> list[TrackResponse]:
    """
    List all tracks.
    """
    return await list_tracks(db, active_only=True)


@router.get("/tracks/{track_id}", response_model=TrackResponse)
async def tracks_info_view(
    track_id: int, db: AsyncSession = Depends(get_db)
) -> TrackResponse:
    """
    Track info.
    """
    return await info_track(db, track_id)


@router.post("/tracks", response_model=TrackResponse)
async def tracks_create_view(
    track_create: TrackCreate, db: AsyncSession = Depends(get_db)
) -> TrackResponse:
    """
    Create a new track.
    """
    return await create_track(db, track_create)


@router.patch("/tracks/{track_id}", response_model=TrackResponse)
async def tracks_patch_view(
    track_id: int, data: dict, db: AsyncSession = Depends(get_db)
) -> TrackResponse:
    """
    Update fields in track.
    """
    return await patch_track(db, track_id, data)


@router.delete("/tracks/{track_id}")
async def tracks_delete_view(
    track_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Delete the track.
    """
    return await delete_track(db, track_id)


@router.get("/checks", response_model=list[Check])
async def checks_view(count: int, track_id: int | None = None) -> list[Check]:
    """
    Last checks.
    """
    return await load_last_logs(count, track_id)


with open("./README.md") as f:
    DESCRIPTION = f.read()


app = FastAPI(
    title='logastra',
    description=DESCRIPTION,
    summary="Online service monitoring powered by Python + FastAPI + Swagger",
    version=VERSION,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/version", response_model=VersionResponse)
async def version_view() -> VersionResponse:
    """
    Version of the service.
    """
    return VersionResponse(version=VERSION)
