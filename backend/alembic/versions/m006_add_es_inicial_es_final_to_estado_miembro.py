"""add es_inicial and es_final to estados_miembro

Revision ID: m006
Revises: m005
Create Date: 2026-05-06

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'm006'
down_revision: Union[str, Sequence[str], None] = 'm005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('estados_miembro', sa.Column('es_inicial', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('estados_miembro', sa.Column('es_final', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('estados_miembro', 'es_final')
    op.drop_column('estados_miembro', 'es_inicial')
