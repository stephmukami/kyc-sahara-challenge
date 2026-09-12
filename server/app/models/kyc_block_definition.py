from sqlalchemy import Enum, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import BlockCategory


class KYCBlockDefinition(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "kyc_block_definitions"

    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[BlockCategory] = mapped_column(
        Enum(BlockCategory, name="block_category")
    )
    supports_channels: Mapped[list[str]] = mapped_column(JSONB, default=list)
    input_schema: Mapped[dict] = mapped_column(JSONB, default=dict)
    default_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)

    app_configs: Mapped[list["AppKYCBlockConfig"]] = relationship(  # noqa: F821
        back_populates="block"
    )
