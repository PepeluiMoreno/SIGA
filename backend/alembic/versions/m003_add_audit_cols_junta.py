"""add missing audit columns to junta directiva tables

Revision ID: m003
Revises: m002
Create Date: 2026-05-05

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'm003'
down_revision: Union[str, Sequence[str], None] = 'm002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_tables = ['tipos_cargo_roles', 'juntas_directivas', 'cargos_junta', 'historial_cargos_junta']


def upgrade() -> None:
    for table in _tables:
        op.add_column(table, sa.Column('creado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True))
        op.add_column(table, sa.Column('modificado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True))


def downgrade() -> None:
    for table in _tables:
        op.drop_column(table, 'modificado_por_id')
        op.drop_column(table, 'creado_por_id')
