"""add problems and tags tables

Revision ID: 20260515_add_problems_and_tags
Revises: a88ab1bf29d6
Create Date: 2026-05-15 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260515_add_problems_and_tags'
down_revision: Union[str, None] = 'a88ab1bf29d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 tags 表
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_slug', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('is_lanqiao_special', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('name_slug'),
        sa.ForeignKeyConstraint(['parent_id'], ['tags.id'], ondelete='SET NULL')
    )
    op.create_index('idx_tags_category', 'tags', ['category'])
    op.create_index('idx_tags_parent', 'tags', ['parent_id'])

    # 创建 problems 表
    op.create_table(
        'problems',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('title_slug', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('input_format', sa.Text(), nullable=False),
        sa.Column('output_format', sa.Text(), nullable=False),
        sa.Column('constraints', sa.Text(), nullable=True),
        sa.Column('difficulty', sa.SmallInteger(), nullable=False, server_default='1'),
        sa.Column('time_limit_ms', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('memory_limit_mb', sa.Integer(), nullable=False, server_default='256'),
        sa.Column('source_oj', sa.String(50), nullable=True),
        sa.Column('source_problem_id', sa.String(100), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title_slug'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('difficulty >= 1 AND difficulty <= 10', name='check_difficulty_range')
    )
    op.create_index('idx_problems_difficulty', 'problems', ['difficulty'])
    op.create_index('idx_problems_source_oj', 'problems', ['source_oj'])
    op.create_index('idx_problems_published', 'problems', ['is_published', 'created_at'])

    # 创建 problem_tag_associations 表
    op.create_table(
        'problem_tag_associations',
        sa.Column('problem_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('problem_id', 'tag_id'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE')
    )


def downgrade() -> None:
    op.drop_table('problem_tag_associations')
    op.drop_table('problems')
    op.drop_table('tags')
