"""add pais_nacimiento_id to miembros

Revision ID: 9096dc619f8c
Revises: m008
Create Date: 2026-05-06 10:43:49.311348
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '9096dc619f8c'
down_revision: Union[str, None] = 'm008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('miembros', sa.Column('pais_nacimiento_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'miembros', 'paises', ['pais_nacimiento_id'], ['id'])
    op.create_index(op.f('ix_miembros_pais_nacimiento_id'), 'miembros', ['pais_nacimiento_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_miembros_pais_nacimiento_id'), table_name='miembros')
    op.drop_constraint(None, 'miembros', type_='foreignkey')
    op.drop_column('miembros', 'pais_nacimiento_id')
