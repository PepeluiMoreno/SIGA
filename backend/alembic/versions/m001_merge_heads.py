"""merge heads: fa3b91c72d08 + c1d2e3f4g5h6

Revision ID: m001
Revises: fa3b91c72d08, c1d2e3f4g5h6
Create Date: 2026-05-05

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'm001'
down_revision: Union[str, Sequence[str], None] = ('fa3b91c72d08', 'c1d2e3f4g5h6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
