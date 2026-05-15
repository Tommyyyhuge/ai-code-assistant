"""add submissions, test_cases, and submission_results tables

Revision ID: 20260515_submissions_testcases
Revises: 20260515_add_problems_and_tags
Create Date: 2026-05-15 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260515_submissions_testcases'
down_revision: Union[str, None] = '20260515_add_problems_and_tags'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 test_cases 表
    op.create_table(
        'test_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('problem_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('input_data', sa.Text(), nullable=False),
        sa.Column('expected_output', sa.Text(), nullable=False),
        sa.Column('is_sample', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE')
    )
    op.create_index('idx_test_cases_problem', 'test_cases', ['problem_id', 'is_active', 'order_index'])

    # 创建 submissions 表
    op.create_table(
        'submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('problem_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('language', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='Pending'),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('runtime_ms', sa.Integer(), nullable=True),
        sa.Column('memory_kb', sa.Integer(), nullable=True),
        sa.Column('passed_count', sa.SmallInteger(), nullable=True),
        sa.Column('total_count', sa.SmallInteger(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('judge_log', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('judged_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE')
    )
    op.create_index('idx_submissions_user', 'submissions', ['user_id', 'submitted_at'])
    op.create_index('idx_submissions_problem', 'submissions', ['problem_id', 'status'])
    op.create_index('idx_submissions_status', 'submissions', ['status', 'submitted_at'])

    # 创建 submission_results 表
    op.create_table(
        'submission_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('test_case_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('test_case_order', sa.SmallInteger(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('runtime_ms', sa.Integer(), nullable=True),
        sa.Column('memory_kb', sa.Integer(), nullable=True),
        sa.Column('actual_output', sa.Text(), nullable=True),
        sa.Column('diff_info', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='SET NULL')
    )
    op.create_index('idx_submission_results_submission', 'submission_results', ['submission_id', 'test_case_order'])


def downgrade() -> None:
    op.drop_table('submission_results')
    op.drop_table('submissions')
    op.drop_table('test_cases')
