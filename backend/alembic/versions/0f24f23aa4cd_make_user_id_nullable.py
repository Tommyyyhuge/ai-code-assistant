"""make_user_id_nullable

Revision ID: 0f24f23aa4cd
Revises: 20260515_submissions_testcases
Create Date: 2026-05-15 17:12:55.935480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f24f23aa4cd'
down_revision: Union[str, None] = '20260515_submissions_testcases'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('submissions', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('submissions', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
