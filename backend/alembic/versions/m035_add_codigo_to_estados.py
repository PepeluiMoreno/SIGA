"""add codigo to all estado tables and populate estados_campania

Revision ID: m035
Revises: m034
Create Date: 2026-05-12

"""
import sqlalchemy as sa
from alembic import op

revision = 'm035'
down_revision = 'm034'
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

# Códigos para estados_campania (upsert por nombre normalizado)
CODIGOS_CAMPANIA = {
    'Borrador':   'BORRADOR',
    'Programada': 'PROGRAMADA',
    'En curso':   'EN_CURSO',
    'Pausada':    'PAUSADA',
    'Finalizada': 'FINALIZADA',
    'Cancelada':  'CANCELADA',
    'Abortada':   'ABORTADA',
    'Cerrada':    'CERRADA',
}


def upgrade() -> None:
    for table in ESTADO_TABLES:
        op.add_column(table, sa.Column('codigo', sa.String(50), nullable=True))
        op.create_index(f'ix_{table}_codigo', table, ['codigo'])

    # Poblar códigos en estados_campania
    conn = op.get_bind()
    for nombre, codigo in CODIGOS_CAMPANIA.items():
        conn.execute(
            sa.text("UPDATE estados_campania SET codigo = :codigo WHERE nombre = :nombre"),
            {'codigo': codigo, 'nombre': nombre},
        )


def downgrade() -> None:
    for table in ESTADO_TABLES:
        op.drop_index(f'ix_{table}_codigo', table_name=table)
        op.drop_column(table, 'codigo')
