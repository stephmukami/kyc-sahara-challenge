"""initial schema

Revision ID: b0cded8f4ad7
Revises:
Create Date: 2026-09-11 16:53:34.679640

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b0cded8f4ad7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    admin_role = postgresql.ENUM("super_admin", "app_admin", name="admin_role")
    app_status = postgresql.ENUM("active", "inactive", name="app_status")
    block_category = postgresql.ENUM(
        "identity", "biometric", "compliance", "consent", "financial", name="block_category"
    )
    channel = postgresql.ENUM("app", "call", "ussd", name="channel")
    session_status = postgresql.ENUM(
        "created",
        "in_progress",
        "pending_review",
        "abandoned",
        "completed",
        "approved",
        "rejected",
        name="session_status",
    )
    session_decision = postgresql.ENUM("approved", "rejected", name="session_decision")
    block_execution_status = postgresql.ENUM(
        "pending",
        "awaiting_input",
        "processing",
        "passed",
        "failed",
        "skipped",
        name="block_execution_status",
    )
    consent_type = postgresql.ENUM("general_kyc", "biometric", name="consent_type")
    actor_type = postgresql.ENUM("admin", "user", "system", name="actor_type")

    # Each ENUM below is created automatically by SQLAlchemy's DDL events the
    # first time it's referenced as a column type in op.create_table — no
    # separate CREATE TYPE step needed (and doing so would double-create it).

    op.create_table(
        "admin_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", admin_role, nullable=False),
        sa.Column(
            "assigned_app_ids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=False,
        ),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_admin_users_email", "admin_users", ["email"])

    op.create_table(
        "end_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("preferred_language", sa.String(length=10), nullable=True),
        sa.UniqueConstraint("phone_number"),
    )
    op.create_index("ix_end_users_phone_number", "end_users", ["phone_number"])

    op.create_table(
        "kyc_block_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("category", block_category, nullable=False),
        sa.Column("supports_channels", postgresql.JSONB, nullable=False),
        sa.Column("input_schema", postgresql.JSONB, nullable=False),
        sa.Column("default_config", postgresql.JSONB, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_kyc_block_definitions_code", "kyc_block_definitions", ["code"])

    op.create_table(
        "apps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("status", app_status, nullable=False),
        sa.Column("allowed_channels", postgresql.JSONB, nullable=False),
        sa.Column("phone_trigger_number", sa.String(length=32), nullable=True),
        sa.Column("default_language", sa.String(length=10), nullable=False),
        sa.Column("webhook_url", sa.String(length=2048), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["admin_users.id"]),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_apps_slug", "apps", ["slug"])

    op.create_table(
        "app_kyc_block_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("app_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("block_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("config_overrides", postgresql.JSONB, nullable=False),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["app_id"], ["apps.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["block_id"], ["kyc_block_definitions.id"]),
        sa.ForeignKeyConstraint(["updated_by_id"], ["admin_users.id"]),
        sa.UniqueConstraint("app_id", "block_id", name="uq_app_block"),
    )

    op.create_table(
        "kyc_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("app_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", channel, nullable=False),
        sa.Column("status", session_status, nullable=False),
        sa.Column("current_order_index", sa.Integer(), nullable=False),
        sa.Column("external_call_id", sa.String(length=255), nullable=True),
        sa.Column("decision", session_decision, nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["app_id"], ["apps.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["end_users.id"]),
    )

    op.create_table(
        "kyc_block_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("app_block_config_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", block_execution_status, nullable=False),
        sa.Column("provider_used", sa.String(length=50), nullable=True),
        sa.Column("raw_input_ref", sa.String(length=2048), nullable=True),
        sa.Column("extracted_data", postgresql.JSONB, nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["kyc_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["app_block_config_id"], ["app_kyc_block_configs.id"]),
    )

    op.create_table(
        "consent_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("consent_type", consent_type, nullable=False),
        sa.Column("text_version", sa.String(length=50), nullable=False),
        sa.Column("audio_ref", sa.String(length=2048), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("given_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["kyc_sessions.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_type", actor_type, nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=100), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("audit_logs")
    op.drop_table("consent_records")
    op.drop_table("kyc_block_executions")
    op.drop_table("kyc_sessions")
    op.drop_table("app_kyc_block_configs")
    op.drop_table("apps")
    op.drop_table("kyc_block_definitions")
    op.drop_table("end_users")
    op.drop_table("admin_users")

    # Table drops do NOT auto-drop the ENUM types they referenced (unlike
    # CREATE TABLE, which does auto-create them) — drop them explicitly.
    bind = op.get_bind()
    for enum_name in (
        "actor_type",
        "consent_type",
        "block_execution_status",
        "session_decision",
        "session_status",
        "channel",
        "block_category",
        "app_status",
        "admin_role",
    ):
        postgresql.ENUM(name=enum_name).drop(bind, checkfirst=True)
