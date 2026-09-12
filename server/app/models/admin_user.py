import uuid

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import AdminRole


class AdminUser(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "admin_users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[AdminRole] = mapped_column(
        Enum(AdminRole, name="admin_role"), default=AdminRole.app_admin
    )
    assigned_app_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), default=list
    )

    created_apps: Mapped[list["App"]] = relationship(back_populates="created_by")  # noqa: F821
