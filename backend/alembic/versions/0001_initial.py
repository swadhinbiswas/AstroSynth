"""Initial schema — mirrors database/schema.sql (users, datasets, models, predictions, experiments, reports, feedback, audit_logs)."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.create_table("users", sa.Column("id", UUID(as_uuid=True), primary_key=True), sa.Column("email", sa.String(255), nullable=False, unique=True), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("full_name", sa.String(255), server_default=""), sa.Column("role", sa.String(32), nullable=False, server_default="scientist"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.CheckConstraint("role IN ('admin','scientist','viewer')", name="ck_users_role"))
    op.create_table("datasets", sa.Column("id", UUID(as_uuid=True), primary_key=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("mission", sa.String(32), nullable=False), sa.Column("version", sa.String(32), server_default="v1"), sa.Column("rows_count", sa.Integer, server_default="0"), sa.Column("storage_uri", sa.Text, server_default=""), sa.Column("checksum", sa.String(128), server_default=""), sa.Column("meta", JSONB, server_default="{}"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("models", sa.Column("id", UUID(as_uuid=True), primary_key=True), sa.Column("name", sa.String(128), nullable=False), sa.Column("version", sa.String(32), nullable=False), sa.Column("algorithm", sa.String(64), nullable=False), sa.Column("metrics", JSONB, server_default="{}"), sa.Column("params", JSONB, server_default="{}"), sa.Column("artifact_uri", sa.Text, server_default=""), sa.Column("is_active", sa.Boolean, server_default="false"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("predictions", sa.Column("id", UUID(as_uuid=True), primary_key=True), sa.Column("user_id", UUID(as_uuid=True)), sa.Column("model_id", UUID(as_uuid=True)), sa.Column("input_features", JSONB, nullable=False), sa.Column("predicted_class", sa.String(32), nullable=False), sa.Column("confidence", sa.Float, nullable=False), sa.Column("probabilities", JSONB, server_default="{}"), sa.Column("explanations", JSONB, server_default="{}"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("experiments", sa.Column("id", UUID(as_uuid=True), primary_key=True), sa.Column("user_id", UUID(as_uuid=True)), sa.Column("name", sa.String(255), nullable=False), sa.Column("config", JSONB, server_default="{}"), sa.Column("results", JSONB, server_default="{}"), sa.Column("status", sa.String(32), server_default="completed"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("reports", sa.Column("id", UUID(as_uuid=True), primary_key=True), sa.Column("user_id", UUID(as_uuid=True)), sa.Column("title", sa.String(255), nullable=False), sa.Column("content_md", sa.Text, server_default=""), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("feedback", sa.Column("id", UUID(as_uuid=True), primary_key=True), sa.Column("prediction_id", UUID(as_uuid=True)), sa.Column("user_label", sa.String(32), nullable=False), sa.Column("comment", sa.Text, server_default=""), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("audit_logs", sa.Column("id", sa.Integer, primary_key=True, autoincrement=True), sa.Column("actor", sa.String(255), server_default=""), sa.Column("action", sa.String(128), nullable=False), sa.Column("resource", sa.String(255), server_default=""), sa.Column("meta", JSONB, server_default="{}"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    for t, c in [("users", "email"), ("datasets", "mission"), ("models", "name"), ("predictions", "predicted_class"), ("audit_logs", "action")]:
        op.create_index(f"ix_{t}_{c}", t, [c])


def downgrade() -> None:
    for t in ["audit_logs", "feedback", "reports", "experiments", "predictions", "models", "datasets", "users"]:
        op.drop_table(t)
