from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class EndUser(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "end_users"

    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferred_language: Mapped[str | None] = mapped_column(String(10), nullable=True)

    sessions: Mapped[list["KYCSession"]] = relationship(back_populates="user")  # noqa: F821
