"""create coordinaciones_territoriales and historial_nombramientos tables

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-05-06 14:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, None] = 'e2f3a4b5c6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Coordinaciones Territoriales ──
    op.create_table('coordinaciones_territoriales',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('miembro_id', sa.Uuid(), nullable=False),
    sa.Column('agrupacion_id', sa.Uuid(), nullable=False),
    sa.Column('fecha_asignacion', sa.Date(), nullable=True),
    sa.Column('observaciones', sa.String(length=500), nullable=True),
    sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
    sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('creado_por_id', sa.Uuid(), nullable=True),
    sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['agrupacion_id'], ['agrupaciones_territoriales.id'], ),
    sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['miembro_id'], ['miembros.id'], ),
    sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coordinaciones_territoriales_miembro_id'), 'coordinaciones_territoriales', ['miembro_id'], unique=False)
    op.create_index(op.f('ix_coordinaciones_territoriales_agrupacion_id'), 'coordinaciones_territoriales', ['agrupacion_id'], unique=False)

    # ── Histórico de Nombramientos ──
    op.create_table('historial_nombramientos',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('miembro_id', sa.Uuid(), nullable=False),
    sa.Column('tipo_cargo_id', sa.Uuid(), nullable=False),
    sa.Column('agrupacion_id', sa.Uuid(), nullable=True),
    sa.Column('fecha_inicio', sa.Date(), nullable=False),
    sa.Column('fecha_fin', sa.Date(), nullable=True),
    sa.Column('tipo_origen', sa.String(length=50), nullable=True),
    sa.Column('origen_id', sa.Uuid(), nullable=True),
    sa.Column('motivo', sa.String(length=500), nullable=True),
    sa.Column('observaciones', sa.Text(), nullable=True),
    sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
    sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('creado_por_id', sa.Uuid(), nullable=True),
    sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['agrupacion_id'], ['agrupaciones_territoriales.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['miembro_id'], ['miembros.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['tipo_cargo_id'], ['tipos_cargo.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hist_nombr_miembro'), 'historial_nombramientos', ['miembro_id'], unique=False)
    op.create_index(op.f('ix_hist_nombr_agrupacion'), 'historial_nombramientos', ['agrupacion_id'], unique=False)
    op.create_index(op.f('ix_hist_nombr_vigente'), 'historial_nombramientos', ['miembro_id', 'fecha_inicio', 'fecha_fin'], unique=False)


def downgrade() -> None:
    # Historial Nombramientos
    op.drop_index(op.f('ix_hist_nombr_vigente'), table_name='historial_nombramientos')
    op.drop_index(op.f('ix_hist_nombr_agrupacion'), table_name='historial_nombramientos')
    op.drop_index(op.f('ix_hist_nombr_miembro'), table_name='historial_nombramientos')
    op.drop_table('historial_nombramientos')

    # Coordinaciones Territoriales
    op.drop_index(op.f('ix_coordinaciones_territoriales_agrupacion_id'), table_name='coordinaciones_territoriales')
    op.drop_index(op.f('ix_coordinaciones_territoriales_miembro_id'), table_name='coordinaciones_territoriales')
    op.drop_table('coordinaciones_territoriales')
