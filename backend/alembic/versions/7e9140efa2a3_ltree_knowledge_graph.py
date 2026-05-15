"""ltree_knowledge_graph

Revision ID: 7e9140efa2a3
Revises: 0f24f23aa4cd
Create Date: 2026-05-15 21:32:55.668816

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7e9140efa2a3'
down_revision: Union[str, None] = '0f24f23aa4cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 启用 ltree 扩展
    op.execute("CREATE EXTENSION IF NOT EXISTS ltree")

    # ── knowledge_nodes ──
    op.create_table(
        "knowledge_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("title_slug", sa.String(255), unique=True, nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("level", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("core_concept", sa.Text(), nullable=False),
        sa.Column("applicable_scenarios", sa.Text(), nullable=True),
        sa.Column("algorithm_steps", sa.Text(), nullable=True),
        sa.Column("code_template_cpp", sa.Text(), nullable=True),
        sa.Column("code_template_py", sa.Text(), nullable=True),
        sa.Column("code_template_java", sa.Text(), nullable=True),
        sa.Column("time_complexity", sa.String(100), nullable=True),
        sa.Column("space_complexity", sa.String(100), nullable=True),
        sa.Column("common_mistakes", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    # ltree path 列手工添加（SQLAlchemy 无原生 ltree 类型）
    op.execute("ALTER TABLE knowledge_nodes ADD COLUMN path ltree NOT NULL DEFAULT 'root'")
    op.execute("CREATE INDEX idx_knowledge_nodes_path ON knowledge_nodes USING GIST (path)")
    op.create_index("idx_knowledge_nodes_title_slug", "knowledge_nodes", ["title_slug"])
    op.create_index("idx_knowledge_nodes_category", "knowledge_nodes", ["category", "order_index"])
    op.create_index("idx_knowledge_nodes_published", "knowledge_nodes", ["is_published"])

    # ── knowledge_edges ──
    op.create_table(
        "knowledge_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("from_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("to_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("edge_type", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_knowledge_edges_from", "knowledge_edges", ["from_node_id", "edge_type"])
    op.create_index("idx_knowledge_edges_to", "knowledge_edges", ["to_node_id", "edge_type"])

    # ── knowledge_problem_associations ──
    op.create_table(
        "knowledge_problem_associations",
        sa.Column("knowledge_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("problems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("difficulty_level", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("knowledge_node_id", "problem_id"),
    )

    # ── user_progress ──
    op.create_table(
        "user_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("knowledge_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="not_started"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("practice_count", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("last_practiced_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "knowledge_node_id"),
    )
    op.create_index("idx_user_progress_user", "user_progress", ["user_id", "status"])
    op.create_index("idx_user_progress_node", "user_progress", ["knowledge_node_id"])


def downgrade() -> None:
    op.drop_table("user_progress")
    op.drop_table("knowledge_problem_associations")
    op.drop_table("knowledge_edges")
    op.execute("DROP INDEX IF EXISTS idx_knowledge_nodes_path")
    op.drop_table("knowledge_nodes")
    op.execute("DROP EXTENSION IF EXISTS ltree")
