"""initial_tables

Revision ID: c2ac3ba0363d
Revises: 
Create Date: 2026-03-22 20:27:42.851300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c2ac3ba0363d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("openrouter_id", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("context_length", sa.Integer()),
        sa.Column("pricing_input", sa.Numeric(20, 10)),
        sa.Column("pricing_output", sa.Numeric(20, 10)),
        sa.Column("pricing_image", sa.Numeric(20, 10)),
        sa.Column("pricing_request", sa.Numeric(20, 10)),
        sa.Column("modalities", postgresql.JSONB()),
        sa.Column("supported_parameters", postgresql.JSONB()),
        sa.Column("max_completion_tokens", sa.Integer()),
        sa.Column("architecture", postgresql.JSONB()),
        sa.Column("is_free", sa.Boolean(), server_default="false"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_models_provider", "models", ["provider"])
    op.create_index("idx_models_pricing_input", "models", ["pricing_input"])
    op.create_index("idx_models_context_length", "models", ["context_length"])
    op.create_index("idx_models_is_active", "models", ["is_active"])

    op.create_table(
        "model_benchmarks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("models.id"), nullable=False),
        sa.Column("benchmark_name", sa.String(100), nullable=False),
        sa.Column("score", sa.Numeric(10, 4), nullable=False),
        sa.Column("max_score", sa.Numeric(10, 4)),
        sa.Column("source_url", sa.String(500)),
        sa.Column("measured_at", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("model_id", "benchmark_name"),
    )
    op.create_index("idx_benchmarks_model_id", "model_benchmarks", ["model_id"])
    op.create_index("idx_benchmarks_name", "model_benchmarks", ["benchmark_name"])

    op.create_table(
        "model_tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("models.id"), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("strength_level", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("model_id", "category"),
        sa.CheckConstraint("strength_level BETWEEN 1 AND 5", name="ck_model_tags_strength_level"),
    )
    op.create_index("idx_tags_model_id", "model_tags", ["model_id"])
    op.create_index("idx_tags_category", "model_tags", ["category"])


def downgrade() -> None:
    op.drop_table("model_tags")
    op.drop_table("model_benchmarks")
    op.drop_table("models")
