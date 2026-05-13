"""drop codigo from all estado tables

Revision ID: m036
Revises: m035
Create Date: 2026-05-12

"""
import sqlalchemy as sa
from alembic import op

revision = 'm036'
down_revision = 'm035'
branch_labels = None
depends_on = None

ESTADO_TABLES = [
    'estados_cuota',
    'estados_campania',
    'estados_tarea',
    'estados_actividad',
    'estados_participante',
    'estados_orden_cobro',
    'estados_remesa',
    'estados_donacion',
    'estados_notificacion',
]


def upgrade() -> None:
    for table in ESTADO_TABLES:
        op.drop_index(f'ix_{table}_codigo', table_name=table)
        op.drop_column(table, 'codigo')


def downgrade() -> None:
    for table in ESTADO_TABLES:
        op.add_column(table, sa.Column('codigo', sa.String(50), nullable=True))
        op.create_index(f'ix_{table}_codigo', table, ['codigo'])
