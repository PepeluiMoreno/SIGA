"""add_junta_directiva_models

Añade los modelos de junta directiva:
  - permite_multiples en tipos_cargo
  - juntas_directivas
  - cargos_junta
  - historial_cargos_junta
  - tipos_cargo_roles

Revision ID: a1b2c3d4e5f6
Revises: f5g6h7i8j9k0
Create Date: 2026-05-04 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f5g6h7i8j9k0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- tipos_cargo: añadir permite_multiples ---
    op.add_column(
        'tipos_cargo',
        sa.Column('permite_multiples', sa.Boolean(), nullable=False, server_default='false'),
    )

    # --- juntas_directivas ---
    op.create_table(
        'juntas_directivas',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('agrupacion_id', UUID(as_uuid=True), sa.ForeignKey('agrupaciones_territoriales.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('fecha_constitucion', sa.Date(), nullable=False),
        sa.Column('fecha_disolucion', sa.Date(), nullable=True),
        sa.Column('activa', sa.Boolean(), nullable=False, server_default='true', index=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        # BaseModel audit fields
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_juntas_directivas_agrupacion_id', 'juntas_directivas', ['agrupacion_id'])
    op.create_index('ix_juntas_directivas_activa', 'juntas_directivas', ['activa'])

    # --- cargos_junta ---
    op.create_table(
        'cargos_junta',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('junta_id', UUID(as_uuid=True), sa.ForeignKey('juntas_directivas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('tipo_cargo_id', UUID(as_uuid=True), sa.ForeignKey('tipos_cargo.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('miembro_id', UUID(as_uuid=True), sa.ForeignKey('miembros.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('posicion', sa.Integer(), nullable=False, server_default='0', index=True),
        sa.Column('fecha_inicio', sa.Date(), nullable=False),
        sa.Column('fecha_fin', sa.Date(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true', index=True),
        # BaseModel audit fields
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('junta_id', 'tipo_cargo_id', 'posicion', name='uq_cargo_junta_posicion'),
    )

    # --- historial_cargos_junta ---
    op.create_table(
        'historial_cargos_junta',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('junta_id', UUID(as_uuid=True), sa.ForeignKey('juntas_directivas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('tipo_cargo_id', UUID(as_uuid=True), sa.ForeignKey('tipos_cargo.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('miembro_id', UUID(as_uuid=True), sa.ForeignKey('miembros.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('posicion', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('fecha_inicio', sa.Date(), nullable=False),
        sa.Column('fecha_fin', sa.Date(), nullable=True),
        sa.Column('motivo_cambio', sa.String(500), nullable=True),
        # BaseModel audit fields
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    )

    # --- tipos_cargo_roles ---
    op.create_table(
        'tipos_cargo_roles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tipo_cargo_id', UUID(as_uuid=True), sa.ForeignKey('tipos_cargo.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('rol_id', UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True),
        # BaseModel audit fields
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('tipo_cargo_id', 'rol_id', name='uq_tipo_cargo_rol'),
    )


def downgrade() -> None:
    op.drop_table('tipos_cargo_roles')
    op.drop_table('historial_cargos_junta')
    op.drop_table('cargos_junta')
    op.drop_table('juntas_directivas')
    op.drop_column('tipos_cargo', 'permite_multiples')
