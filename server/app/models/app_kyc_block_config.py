import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class AppKYCBlockConfig(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "app_kyc_block_configs"
    __table_args__ = (UniqueConstraint("app_id", "block_id", name="uq_app_block"),)

    app_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("apps.id", ondelete="CASCADE")
    )
    block_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kyc_block_definitions.id")
    )
    order_index: Mapped[int] = mapped_column(Integer)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    config_overrides: Mapped[dict] = mapped_column(JSONB, default=dict)

    updated_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("admin_users.id")
    )

    app: Mapped["App"] = relationship(back_populates="block_configs")  # noqa: F821
    block: Mapped["KYCBlockDefinition"] = relationship(back_populates="app_configs")  # noqa: F821
    updated_by: Mapped["AdminUser"] = relationship()  # noqa: F821
    executions: Mapped[list["KYCBlockExecution"]] = relationship(  # noqa: F821
        back_populates="app_block_config"
    )
