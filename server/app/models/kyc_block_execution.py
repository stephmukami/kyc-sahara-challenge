import uuid

from sqlalchemy import Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import BlockExecutionStatus


class KYCBlockExecution(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "kyc_block_executions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kyc_sessions.id", ondelete="CASCADE")
    )
    app_block_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("app_kyc_block_configs.id")
    )
    status: Mapped[BlockExecutionStatus] = mapped_column(
        Enum(BlockExecutionStatus, name="block_execution_status"),
        default=BlockExecutionStatus.pending,
    )
    provider_used: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_input_ref: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    extracted_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    session: Mapped["KYCSession"] = relationship(back_populates="block_executions")  # noqa: F821
    app_block_config: Mapped["AppKYCBlockConfig"] = relationship(  # noqa: F821
        back_populates="executions"
    )
