"""Presupuestos: vinculación de partida a actividad/campaña.

Revision ID: p1q2r3s4t5u6
Revises: o0p1q2r3s4t5
Create Date: 2026-05-21 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'p1q2r3s4t5u6'
down_revision = 'o0p1q2r3s4t5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('partidas_presupuestarias', sa.Column('actividad_id', sa.Uuid(), nullable=True))
    op.add_column('partidas_presupuestarias', sa.Column('campania_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_partida_actividad', 'partidas_presupuestarias',
        'actividades', ['actividad_id'], ['id']
    )
    op.create_foreign_key(
        'fk_partida_campania', 'partidas_presupuestarias',
        'campanias', ['campania_id'], ['id']
    )
    op.create_index('ix_partidas_actividad_id', 'partidas_presupuestarias', ['actividad_id'])
    op.create_index('ix_partidas_campania_id', 'partidas_presupuestarias', ['campania_id'])


def downgrade() -> None:
    op.drop_index('ix_partidas_campania_id', 'partidas_presupuestarias')
    op.drop_index('ix_partidas_actividad_id', 'partidas_presupuestarias')
    op.drop_constraint('fk_partida_campania', 'partidas_presupuestarias', type_='foreignkey')
    op.drop_constraint('fk_partida_actividad', 'partidas_presupuestarias', type_='foreignkey')
    op.drop_column('partidas_presupuestarias', 'campania_id')
    op.drop_column('partidas_presupuestarias', 'actividad_id')
