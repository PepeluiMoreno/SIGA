"""Añade tabla tipos_vinculacion y campos vinculacion a usuarios.

Revision ID: m024
Revises: m023
Create Date: 2026-05-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'm024'
down_revision = 'm023'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabla catálogo de tipos de vinculación
    op.create_table(
        'tipos_vinculacion',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('nombre', sa.String(150), nullable=False, unique=True),
        sa.Column('requiere_entidad', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        # Auditoría (AuditoriaMixin)
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('creado_por_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('modificado_por_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_tipos_vinculacion_activo', 'tipos_vinculacion', ['activo'])

    # Añadir campos de vinculación a usuarios
    op.add_column('usuarios', sa.Column(
        'tipo_vinculacion_id', postgresql.UUID(as_uuid=True), nullable=True,
    ))
    op.add_column('usuarios', sa.Column(
        'entidad_vinculacion', sa.String(200), nullable=True,
    ))
    op.create_index('ix_usuarios_tipo_vinculacion_id', 'usuarios', ['tipo_vinculacion_id'])
    op.create_foreign_key(
        'fk_usuarios_tipo_vinculacion_id', 'usuarios', 'tipos_vinculacion',
        ['tipo_vinculacion_id'], ['id'], ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_usuarios_tipo_vinculacion_id', 'usuarios', type_='foreignkey')
    op.drop_index('ix_usuarios_tipo_vinculacion_id', table_name='usuarios')
    op.drop_column('usuarios', 'entidad_vinculacion')
    op.drop_column('usuarios', 'tipo_vinculacion_id')
    op.drop_index('ix_tipos_vinculacion_activo', table_name='tipos_vinculacion')
    op.drop_table('tipos_vinculacion')
