import enum
from typing import AsyncGenerator
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Text, select, update, delete
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


DATABASE_URL = "sqlite+aiosqlite:///./data/logastra.db"


engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class TrackStatus(str, enum.Enum):
    OK = "ok"
    FAILED = "failed"
    UNKNOWN = "unknown"


class Base(DeclarativeBase):
    pass


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    status: Mapped[TrackStatus] = mapped_column(
        String(20), default=TrackStatus.UNKNOWN, nullable=False
    )
    last_check: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    last_fail: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fail_detail: Mapped[str] = mapped_column(
        Text(), default=None, nullable=True
    )
    schedule: Mapped[str] = mapped_column(String(1000), nullable=False)
    handler: Mapped[str] = mapped_column(String(100), nullable=False)
    options: Mapped[str | None] = mapped_column(
        String(1000), default=None, nullable=True
    )
    notify: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    def __repr__(self):
        return f"Track(id={self.id},name=\"{self.name}\")"

    def is_ok(self) -> bool:
        return self.status == TrackStatus.OK


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def list_tracks(
    session: AsyncSession, active_only: bool = False
) -> list[Track]:
    query = select(Track)
    if active_only:
        query = query.where(Track.active == True)  # noqa: E712
    result = await session.execute(query)
    return list(result.scalars().all())


async def info_track(session: AsyncSession, track_id: int) -> Track:
    query = select(Track).where(Track.id == track_id)
    result = await session.execute(query)
    return result.scalar_one()


async def create_track(
    session: AsyncSession, track: "TrackCreate"  # noqa: F821
) -> Track:
    track = Track(**track.model_dump())
    session.add(track)
    await session.commit()
    await session.refresh(track)
    return track


async def patch_track(
    session: AsyncSession, track_id: int, data: dict
) -> Track:
    query = (update(Track).where(Track.id == track_id).values(**data)
                          .returning(Track))
    result = await session.execute(query)
    await session.commit()
    return result.scalar_one()


async def delete_track(session: AsyncSession, track_id: int):
    query = delete(Track).where(Track.id == track_id)
    await session.execute(query)
    await session.commit()
