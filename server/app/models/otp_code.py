import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import Channel, OTPPurpose


class OTPCode(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "otp_codes"

    end_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("end_users.id", ondelete="CASCADE")
    )
    code_hash: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[OTPPurpose] = mapped_column(Enum(OTPPurpose, name="otp_purpose"))
    channel: Mapped[Channel] = mapped_column(Enum(Channel, name="channel"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)

    end_user: Mapped["EndUser"] = relationship()  # noqa: F821
