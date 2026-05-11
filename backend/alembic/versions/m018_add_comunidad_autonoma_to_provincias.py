"""Añade comunidad_autonoma a provincias

Revision ID: m018
Revises: m017
Create Date: 2026-05-08
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'm018'
down_revision: Union[str, None] = 'm017'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('provincias', sa.Column('comunidad_autonoma', sa.String(100), nullable=True))
    op.create_index('ix_provincias_comunidad_autonoma', 'provincias', ['comunidad_autonoma'])


def downgrade() -> None:
    op.drop_index('ix_provincias_comunidad_autonoma', table_name='provincias')
    op.drop_column('provincias', 'comunidad_autonoma')
