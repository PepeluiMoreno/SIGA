"""merge cabezas master + secretaria

Revision ID: d36a6ce11db3
Revises: b1c2d3e4f5a6, m8n9o0p1q2r3
Create Date: 2026-05-20 22:51:59.680319
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'd36a6ce11db3'
down_revision: Union[str, None] = ('b1c2d3e4f5a6', 'm8n9o0p1q2r3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
