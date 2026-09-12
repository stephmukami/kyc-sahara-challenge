"""add auth models

Revision ID: c274f918a6b2
Revises: b0cded8f4ad7
Create Date: 2026-09-12 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c274f918a6b2'
down_revision: Union[str, Sequence[str], None] = 'b0cded8f4ad7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    otp_purpose = postgresql.ENUM("signup", "login", name="otp_purpose")

    # `channel` already exists (created by the initial migration) — reuse it
    # without letting SQLAlchemy try to CREATE TYPE a second time.
    channel = postgresql.ENUM("app", "call", "ussd", name="channel", create_type=False)

    op.add_column(
        "end_users",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "end_users", sa.Column("full_name_audio_ref", sa.String(length=2048), nullable=True)
    )

    op.create_table(
        "otp_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("end_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("purpose", otp_purpose, nullable=False),
        sa.Column("channel", channel, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["end_user_id"], ["end_users.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "admin_password_reset_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("admin_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "ix_admin_password_reset_tokens_token_hash",
        "admin_password_reset_tokens",
        ["token_hash"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("admin_password_reset_tokens")
    op.drop_table("otp_codes")
    op.drop_column("end_users", "full_name_audio_ref")
    op.drop_column("end_users", "is_verified")

    bind = op.get_bind()
    postgresql.ENUM(name="otp_purpose").drop(bind, checkfirst=True)
