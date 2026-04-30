"""add militancia tables: skills, disponibilidad, historial_agrupaciones, traslados

Revision ID: a2b3c4d5e6f7
Revises: 0b338d94c1f5
Create Date: 2026-04-30 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, None] = '0b338d94c1f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AUDIT_COLS = [
    sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
    sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('creado_por_id', sa.Uuid(), nullable=True),
    sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
]


def upgrade() -> None:
    # skills
    op.create_table(
        'skills',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.Column('descripcion', sa.String(length=500), nullable=True),
        sa.Column('categoria', sa.String(length=100), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        *AUDIT_COLS,
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_skills_nombre', 'skills', ['nombre'])
    op.create_index('ix_skills_categoria', 'skills', ['categoria'])
    op.create_index('ix_skills_activo', 'skills', ['activo'])
    op.create_index('ix_skills_eliminado', 'skills', ['eliminado'])

    # miembros_skills
    op.create_table(
        'miembros_skills',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('miembro_id', sa.Uuid(), nullable=False),
        sa.Column('skill_id', sa.Uuid(), nullable=False),
        sa.Column('nivel', sa.String(length=20), nullable=True),
        sa.Column('validado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('validado_por_id', sa.Uuid(), nullable=True),
        sa.Column('fecha_validacion', sa.Date(), nullable=True),
        sa.Column('notas', sa.String(length=500), nullable=True),
        *AUDIT_COLS,
        sa.ForeignKeyConstraint(['miembro_id'], ['miembros.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['validado_por_id'], ['usuarios.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('miembro_id', 'skill_id', name='uq_miembro_skill'),
    )
    op.create_index('ix_miembros_skills_miembro_id', 'miembros_skills', ['miembro_id'])
    op.create_index('ix_miembros_skills_skill_id', 'miembros_skills', ['skill_id'])
    op.create_index('ix_miembros_skills_eliminado', 'miembros_skills', ['eliminado'])

    # franjas_disponibilidad
    op.create_table(
        'franjas_disponibilidad',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('miembro_id', sa.Uuid(), nullable=False),
        sa.Column('dia_semana', sa.Integer(), nullable=False),
        sa.Column('hora_inicio', sa.String(length=5), nullable=False),
        sa.Column('hora_fin', sa.String(length=5), nullable=False),
        sa.Column('notas', sa.String(length=200), nullable=True),
        sa.Column('activa', sa.Boolean(), nullable=False, server_default='true'),
        *AUDIT_COLS,
        sa.ForeignKeyConstraint(['miembro_id'], ['miembros.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_franjas_disponibilidad_miembro_id', 'franjas_disponibilidad', ['miembro_id'])
    op.create_index('ix_franjas_disponibilidad_eliminado', 'franjas_disponibilidad', ['eliminado'])

    # historial_agrupaciones
    op.create_table(
        'historial_agrupaciones',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('miembro_id', sa.Uuid(), nullable=False),
        sa.Column('agrupacion_id', sa.Uuid(), nullable=False),
        sa.Column('fecha_inicio', sa.Date(), nullable=False),
        sa.Column('fecha_fin', sa.Date(), nullable=True),
        sa.Column('motivo', sa.String(length=500), nullable=True),
        *AUDIT_COLS,
        sa.ForeignKeyConstraint(['miembro_id'], ['miembros.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agrupacion_id'], ['agrupaciones_territoriales.id']),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_historial_agrupaciones_miembro_id', 'historial_agrupaciones', ['miembro_id'])
    op.create_index('ix_historial_agrupaciones_agrupacion_id', 'historial_agrupaciones', ['agrupacion_id'])
    op.create_index('ix_historial_agrupaciones_eliminado', 'historial_agrupaciones', ['eliminado'])

    # solicitudes_traslado
    op.create_table(
        'solicitudes_traslado',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('miembro_id', sa.Uuid(), nullable=False),
        sa.Column('agrupacion_origen_id', sa.Uuid(), nullable=False),
        sa.Column('agrupacion_destino_id', sa.Uuid(), nullable=False),
        sa.Column('motivo', sa.Text(), nullable=False),
        sa.Column('estado', sa.String(length=30), nullable=False, server_default='PENDIENTE'),
        sa.Column('fecha_solicitud', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_efectiva_deseada', sa.Date(), nullable=True),
        sa.Column('aprobado_origen', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_aprobacion_origen', sa.DateTime(), nullable=True),
        sa.Column('coordinador_origen_id', sa.Uuid(), nullable=True),
        sa.Column('observaciones_origen', sa.Text(), nullable=True),
        sa.Column('aprobado_destino', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_aprobacion_destino', sa.DateTime(), nullable=True),
        sa.Column('coordinador_destino_id', sa.Uuid(), nullable=True),
        sa.Column('observaciones_destino', sa.Text(), nullable=True),
        sa.Column('motivo_rechazo', sa.Text(), nullable=True),
        sa.Column('fecha_ejecucion', sa.DateTime(), nullable=True),
        sa.Column('usuario_ejecutor_id', sa.Uuid(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        *AUDIT_COLS,
        sa.ForeignKeyConstraint(['miembro_id'], ['miembros.id']),
        sa.ForeignKeyConstraint(['agrupacion_origen_id'], ['agrupaciones_territoriales.id']),
        sa.ForeignKeyConstraint(['agrupacion_destino_id'], ['agrupaciones_territoriales.id']),
        sa.ForeignKeyConstraint(['coordinador_origen_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['coordinador_destino_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['usuario_ejecutor_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_solicitudes_traslado_miembro_id', 'solicitudes_traslado', ['miembro_id'])
    op.create_index('ix_solicitudes_traslado_estado', 'solicitudes_traslado', ['estado'])
    op.create_index('ix_solicitudes_traslado_eliminado', 'solicitudes_traslado', ['eliminado'])


def downgrade() -> None:
    op.drop_table('solicitudes_traslado')
    op.drop_table('historial_agrupaciones')
    op.drop_table('franjas_disponibilidad')
    op.drop_table('miembros_skills')
    op.drop_table('skills')
