"""learning_path

Revision ID: 0c6694531135
Revises: 7e9140efa2a3
Create Date: 2026-05-16 14:08:39.284816

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0c6694531135'
down_revision: Union[str, None] = '7e9140efa2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "learning_paths",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("title_slug", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("estimated_days", sa.Integer(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_learning_paths_category", "learning_paths", ["category"])

    op.create_table(
        "learning_path_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("path_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False),
        sa.Column("knowledge_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("path_id", "knowledge_node_id"),
    )
    op.create_index("idx_path_nodes_path", "learning_path_nodes", ["path_id", "order_index"])

    op.create_table(
        "learning_path_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("path_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("learning_paths.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="not_started"),
        sa.Column("completed_nodes", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("total_nodes", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "path_id"),
    )


def downgrade() -> None:
    op.drop_table("learning_path_progress")
    op.drop_table("learning_path_nodes")
    op.drop_table("learning_paths")
