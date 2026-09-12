import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import ConsentType


class ConsentRecord(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "consent_records"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kyc_sessions.id", ondelete="CASCADE")
    )
    consent_type: Mapped[ConsentType] = mapped_column(
        Enum(ConsentType, name="consent_type")
    )
    text_version: Mapped[str] = mapped_column(String(50))
    audio_ref: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    given_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    session: Mapped["KYCSession"] = relationship()  # noqa: F821
