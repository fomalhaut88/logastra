import os
import asyncio
from typing import ClassVar, BinaryIO, Self, Iterator
from struct import Struct
from datetime import datetime, timedelta

import aiofiles
from pydantic import BaseModel, computed_field

from .db import Track


CHECK_PATH = "./data/check.log"
TIMESTAMP_BASE = datetime(2020, 1, 1)


check_engine = None
check_lock = asyncio.Lock()


class Check(BaseModel):
    _struct: ClassVar[Struct] = Struct("<IHH")

    ts_min: int
    track_id: int
    ok: int

    @computed_field
    def timestamp(self) -> datetime:
        return TIMESTAMP_BASE + timedelta(minutes=self.ts_min)

    def pack(self) -> bytes:
        return self._struct.pack(self.ts_min, self.track_id, self.ok)

    @classmethod
    def size(cls) -> int:
        return cls._struct.size

    @classmethod
    def iter_load(cls, stream: BinaryIO) -> Iterator[Self]:
        for args in cls._struct.iter_unpack(stream):
            kwargs = dict(zip(cls.model_fields.keys(), args))
            yield cls(**kwargs)

    @classmethod
    def to_ts_min(cls, ts: datetime) -> int:
        return int((ts - TIMESTAMP_BASE).total_seconds() / 60 + 1e-3)

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        args = cls._struct.unpack(buffer)
        kwargs = dict(zip(cls.model_fields.keys(), args))
        return cls(**kwargs)

    @classmethod
    def from_track(cls, track: Track) -> Self:
        return cls(
            ts_min=cls.to_ts_min(track.last_check),
            track_id=track.id,
            ok=int(track.is_ok()),
        )


async def init_log():
    global check_engine
    check_engine = await aiofiles.open(CHECK_PATH, mode='a+b')


async def close_log():
    global check_engine
    await check_engine.close()
    check_engine = None


async def save_log(track: Track):
    check = Check.from_track(track)
    async with check_lock:
        await check_engine.write(check.pack())
        await check_engine.flush()


async def load_last_logs(
    count: int = 1, track_id: int | None = None
) -> list[Check]:
    offset = count * Check.size()

    async with check_lock:
        await check_engine.seek(-offset, os.SEEK_END)
        buffer = await check_engine.read(offset)

    check_iter = Check.iter_load(buffer)

    if track_id is None:
        return list(check_iter)
    else:
        return list(filter(
            lambda check: check.track_id == track_id,
            check_iter
        ))
