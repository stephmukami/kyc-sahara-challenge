import uuid

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import AppStatus


class App(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "apps"

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    status: Mapped[AppStatus] = mapped_column(
        Enum(AppStatus, name="app_status"), default=AppStatus.active
    )
    allowed_channels: Mapped[list[str]] = mapped_column(JSONB, default=list)
    phone_trigger_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    default_language: Mapped[str] = mapped_column(String(10), default="en-KE")
    webhook_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("admin_users.id")
    )

    created_by: Mapped["AdminUser"] = relationship(back_populates="created_apps")  # noqa: F821
    block_configs: Mapped[list["AppKYCBlockConfig"]] = relationship(  # noqa: F821
        back_populates="app", cascade="all, delete-orphan", order_by="AppKYCBlockConfig.order_index"
    )
    sessions: Mapped[list["KYCSession"]] = relationship(back_populates="app")  # noqa: F821
