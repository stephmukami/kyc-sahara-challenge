import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AppStatus, Channel


class AppCreate(BaseModel):
    name: str
    slug: str = Field(pattern=r"^[a-z0-9-]+$")
    allowed_channels: list[Channel] = [Channel.app]
    phone_trigger_number: str | None = None
    default_language: str = "en-KE"
    webhook_url: str | None = None
    created_by_id: uuid.UUID


class AppUpdate(BaseModel):
    name: str | None = None
    status: AppStatus | None = None
    allowed_channels: list[Channel] | None = None
    phone_trigger_number: str | None = None
    default_language: str | None = None
    webhook_url: str | None = None


class AppRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    status: AppStatus
    allowed_channels: list[str]
    phone_trigger_number: str | None
    default_language: str
    webhook_url: str | None
    created_by_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class AppListItem(AppRead):
    active_session_count: int
