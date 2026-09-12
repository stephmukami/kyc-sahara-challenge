import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import Channel, SessionDecision, SessionStatus


class KYCSession(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "kyc_sessions"

    app_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("apps.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("end_users.id")
    )
    channel: Mapped[Channel] = mapped_column(Enum(Channel, name="channel"))
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status"), default=SessionStatus.created
    )
    current_order_index: Mapped[int] = mapped_column(Integer, default=0)
    external_call_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decision: Mapped[SessionDecision | None] = mapped_column(
        Enum(SessionDecision, name="session_decision"), nullable=True
    )
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    app: Mapped["App"] = relationship(back_populates="sessions")  # noqa: F821
    user: Mapped["EndUser"] = relationship(back_populates="sessions")  # noqa: F821
    block_executions: Mapped[list["KYCBlockExecution"]] = relationship(  # noqa: F821
        back_populates="session", cascade="all, delete-orphan"
    )
