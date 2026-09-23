from datetime import datetime

from pydantic import BaseModel

from .db import TrackStatus


class VersionResponse(BaseModel):
    version: str


class TrackResponse(BaseModel):
    id: int
    name: str
    status: TrackStatus
    last_check: datetime | None
    last_fail: datetime | None
    fail_detail: str | None
    schedule: str
    handler: str
    options: str | None
    notify: bool
    active: bool


class TrackCreate(BaseModel):
    name: str
    schedule: str
    handler: str
    options: str | None
    notify: bool | None
    active: bool | None
