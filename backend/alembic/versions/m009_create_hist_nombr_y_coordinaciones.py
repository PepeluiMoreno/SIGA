"""create historial_nombramientos table

historial_nombramientos apunta directamente a roles (tipo ORGANIZACION)
en lugar de tipos_cargo, simplificando el modelo de nombramientos.

Revision ID: m009
Revises: f3a4b5c6d7e8
Create Date: 2026-05-06 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'm009'
down_revision: Union[str, None] = 'f3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('historial_nombramientos',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('miembro_id', sa.Uuid(), nullable=False),
    sa.Column('rol_id', sa.Uuid(), nullable=False),
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
    sa.Column('eliminado', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('creado_por_id', sa.Uuid(), nullable=True),
    sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['agrupacion_id'], ['agrupaciones_territoriales.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['miembro_id'], ['miembros.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_historial_nombramientos_agrupacion_id'), 'historial_nombramientos', ['agrupacion_id'], unique=False)
    op.create_index(op.f('ix_historial_nombramientos_eliminado'), 'historial_nombramientos', ['eliminado'], unique=False)
    op.create_index(op.f('ix_historial_nombramientos_miembro_id'), 'historial_nombramientos', ['miembro_id'], unique=False)
    op.create_index(op.f('ix_historial_nombramientos_rol'), 'historial_nombramientos', ['rol_id'], unique=False)
    op.create_index('ix_hist_nombr_vigente', 'historial_nombramientos', ['miembro_id', 'fecha_inicio', 'fecha_fin'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_hist_nombr_vigente', table_name='historial_nombramientos')
    op.drop_index(op.f('ix_historial_nombramientos_rol'), table_name='historial_nombramientos')
    op.drop_index(op.f('ix_historial_nombramientos_miembro_id'), table_name='historial_nombramientos')
    op.drop_index(op.f('ix_historial_nombramientos_eliminado'), table_name='historial_nombramientos')
    op.drop_index(op.f('ix_historial_nombramientos_agrupacion_id'), table_name='historial_nombramientos')
    op.drop_table('historial_nombramientos')
