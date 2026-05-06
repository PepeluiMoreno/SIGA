"""remove es_final from estados_miembro

Revision ID: m007
Revises: m006
Create Date: 2026-05-06

"""
from typing import Sequence, Union
from alembic import op


revision: str = 'm007'
down_revision: Union[str, Sequence[str], None] = 'm006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('estados_miembro', 'es_final')


def downgrade() -> None:
    import sqlalchemy as sa
    op.add_column('estados_miembro', sa.Column('es_final', sa.Boolean(), nullable=False, server_default='false'))
