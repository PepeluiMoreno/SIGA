"""actividad_campania_approval_valuation_fields

Revision ID: e7e5bec87533
Revises: 031b5617936a
Create Date: 2026-05-15 08:04:31.377371
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'e7e5bec87533'
down_revision: Union[str, None] = '031b5617936a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('actividades', sa.Column('aprobado_por_id', sa.Uuid(), nullable=True))
    op.add_column('actividades', sa.Column('fecha_aprobacion', sa.Date(), nullable=True))
    op.add_column('actividades', sa.Column('notas_aprobacion', sa.Text(), nullable=True))
    op.add_column('actividades', sa.Column('valoracion', sa.Text(), nullable=True))
    op.add_column('actividades', sa.Column('objetivos_cumplidos', sa.Boolean(), nullable=True))
    op.add_column('actividades', sa.Column('asistencia_real', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_actividades_aprobado_por_id'), 'actividades', ['aprobado_por_id'], unique=False)
    op.create_foreign_key(None, 'actividades', 'usuarios', ['aprobado_por_id'], ['id'], ondelete='SET NULL')
    op.add_column('campanias', sa.Column('presupuesto_estimado', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('campanias', sa.Column('presupuesto_ejecutado', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('campanias', sa.Column('aprobado_por_id', sa.Uuid(), nullable=True))
    op.add_column('campanias', sa.Column('fecha_aprobacion', sa.Date(), nullable=True))
    op.add_column('campanias', sa.Column('notas_aprobacion', sa.Text(), nullable=True))
    op.add_column('campanias', sa.Column('valoracion', sa.Text(), nullable=True))
    op.add_column('campanias', sa.Column('objetivos_cumplidos', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_campanias_aprobado_por_id'), 'campanias', ['aprobado_por_id'], unique=False)
    op.create_foreign_key(None, 'campanias', 'usuarios', ['aprobado_por_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint(None, 'campanias', type_='foreignkey')
    op.drop_index(op.f('ix_campanias_aprobado_por_id'), table_name='campanias')
    op.drop_column('campanias', 'objetivos_cumplidos')
    op.drop_column('campanias', 'valoracion')
    op.drop_column('campanias', 'notas_aprobacion')
    op.drop_column('campanias', 'fecha_aprobacion')
    op.drop_column('campanias', 'aprobado_por_id')
    op.drop_column('campanias', 'presupuesto_ejecutado')
    op.drop_column('campanias', 'presupuesto_estimado')
    op.drop_constraint(None, 'actividades', type_='foreignkey')
    op.drop_index(op.f('ix_actividades_aprobado_por_id'), table_name='actividades')
    op.drop_column('actividades', 'asistencia_real')
    op.drop_column('actividades', 'objetivos_cumplidos')
    op.drop_column('actividades', 'valoracion')
    op.drop_column('actividades', 'notas_aprobacion')
    op.drop_column('actividades', 'fecha_aprobacion')
    op.drop_column('actividades', 'aprobado_por_id')
