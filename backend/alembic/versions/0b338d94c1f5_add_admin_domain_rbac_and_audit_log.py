"""add admin domain rbac and audit log

Revision ID: 0b338d94c1f5
Revises: f5g6h7i8j9k0
Create Date: 2026-04-29 20:45:22.445287
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0b338d94c1f5'
down_revision: Union[str, None] = 'f5g6h7i8j9k0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # logs_auditoria
    op.create_table(
        'logs_auditoria',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('usuario_id', sa.Uuid(), nullable=True),
        sa.Column('username_snapshot', sa.String(length=255), nullable=True),
        sa.Column('transaccion_codigo', sa.String(length=50), nullable=True),
        sa.Column('accion', sa.Enum('CREAR', 'EDITAR', 'ELIMINAR', 'VER', 'APROBAR', 'RECHAZAR', 'EXPORTAR', 'LOGIN', 'LOGOUT', 'OTRO', name='tipo_accion_auditoria'), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('entidad', sa.String(length=100), nullable=True),
        sa.Column('entidad_id', sa.Uuid(), nullable=True),
        sa.Column('datos_anteriores', sa.Text(), nullable=True),
        sa.Column('datos_nuevos', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('exitoso', sa.Boolean(), nullable=False),
        sa.Column('mensaje_error', sa.Text(), nullable=True),
        sa.Column('fecha_hora', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_logs_auditoria_accion'), 'logs_auditoria', ['accion'], unique=False)
    op.create_index(op.f('ix_logs_auditoria_entidad'), 'logs_auditoria', ['entidad'], unique=False)
    op.create_index(op.f('ix_logs_auditoria_exitoso'), 'logs_auditoria', ['exitoso'], unique=False)
    op.create_index(op.f('ix_logs_auditoria_fecha_hora'), 'logs_auditoria', ['fecha_hora'], unique=False)
    op.create_index(op.f('ix_logs_auditoria_transaccion_codigo'), 'logs_auditoria', ['transaccion_codigo'], unique=False)
    op.create_index(op.f('ix_logs_auditoria_usuario_id'), 'logs_auditoria', ['usuario_id'], unique=False)

    # roles
    op.create_table(
        'roles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.String(length=1000), nullable=True),
        sa.Column('tipo', sa.Enum('SISTEMA', 'ORGANIZACION', 'TERRITORIAL', 'FUNCIONAL', 'PERSONALIZADO', name='tipo_rol'), nullable=False),
        sa.Column('nivel', sa.Integer(), nullable=False),
        sa.Column('es_territorial', sa.Boolean(), nullable=False),
        sa.Column('nivel_territorial', sa.String(length=50), nullable=True),
        sa.Column('sistema', sa.Boolean(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('creado_por_id', sa.Uuid(), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_roles_activo'), 'roles', ['activo'], unique=False)
    op.create_index(op.f('ix_roles_codigo'), 'roles', ['codigo'], unique=True)
    op.create_index(op.f('ix_roles_eliminado'), 'roles', ['eliminado'], unique=False)

    # transacciones
    op.create_table(
        'transacciones',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('descripcion', sa.String(length=1000), nullable=True),
        sa.Column('modulo', sa.String(length=100), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('activa', sa.Boolean(), nullable=False),
        sa.Column('sistema', sa.Boolean(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('creado_por_id', sa.Uuid(), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_transacciones_activa'), 'transacciones', ['activa'], unique=False)
    op.create_index(op.f('ix_transacciones_codigo'), 'transacciones', ['codigo'], unique=True)
    op.create_index(op.f('ix_transacciones_eliminado'), 'transacciones', ['eliminado'], unique=False)
    op.create_index(op.f('ix_transacciones_modulo'), 'transacciones', ['modulo'], unique=False)

    # roles_transacciones
    op.create_table(
        'roles_transacciones',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('rol_id', sa.Uuid(), nullable=False),
        sa.Column('transaccion_id', sa.Uuid(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('creado_por_id', sa.Uuid(), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['transaccion_id'], ['transacciones.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rol_id', 'transaccion_id', name='uq_rol_transaccion'),
    )
    op.create_index(op.f('ix_roles_transacciones_eliminado'), 'roles_transacciones', ['eliminado'], unique=False)
    op.create_index(op.f('ix_roles_transacciones_rol_id'), 'roles_transacciones', ['rol_id'], unique=False)
    op.create_index(op.f('ix_roles_transacciones_transaccion_id'), 'roles_transacciones', ['transaccion_id'], unique=False)

    # usuarios_roles: rol_id Integer → Uuid (vacío en BD, USING NULL fuerza), FKs
    op.execute('TRUNCATE usuarios_roles')
    op.alter_column(
        'usuarios_roles', 'rol_id',
        existing_type=sa.Integer(),
        type_=sa.Uuid(),
        existing_nullable=False,
        postgresql_using='NULL::uuid',
    )
    op.create_index(op.f('ix_usuarios_roles_agrupacion_id'), 'usuarios_roles', ['agrupacion_id'], unique=False)
    op.create_foreign_key(
        'fk_usuarios_roles_rol_id_roles', 'usuarios_roles', 'roles',
        ['rol_id'], ['id'],
    )
    op.create_foreign_key(
        'fk_usuarios_roles_agrupacion_id_agrupaciones', 'usuarios_roles', 'agrupaciones_territoriales',
        ['agrupacion_id'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_usuarios_roles_agrupacion_id_agrupaciones', 'usuarios_roles', type_='foreignkey')
    op.drop_constraint('fk_usuarios_roles_rol_id_roles', 'usuarios_roles', type_='foreignkey')
    op.drop_index(op.f('ix_usuarios_roles_agrupacion_id'), table_name='usuarios_roles')
    op.alter_column(
        'usuarios_roles', 'rol_id',
        existing_type=sa.Uuid(),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using='NULL::integer',
    )

    op.drop_index(op.f('ix_roles_transacciones_transaccion_id'), table_name='roles_transacciones')
    op.drop_index(op.f('ix_roles_transacciones_rol_id'), table_name='roles_transacciones')
    op.drop_index(op.f('ix_roles_transacciones_eliminado'), table_name='roles_transacciones')
    op.drop_table('roles_transacciones')

    op.drop_index(op.f('ix_transacciones_modulo'), table_name='transacciones')
    op.drop_index(op.f('ix_transacciones_eliminado'), table_name='transacciones')
    op.drop_index(op.f('ix_transacciones_codigo'), table_name='transacciones')
    op.drop_index(op.f('ix_transacciones_activa'), table_name='transacciones')
    op.drop_table('transacciones')

    op.drop_index(op.f('ix_roles_eliminado'), table_name='roles')
    op.drop_index(op.f('ix_roles_codigo'), table_name='roles')
    op.drop_index(op.f('ix_roles_activo'), table_name='roles')
    op.drop_table('roles')

    op.drop_index(op.f('ix_logs_auditoria_usuario_id'), table_name='logs_auditoria')
    op.drop_index(op.f('ix_logs_auditoria_transaccion_codigo'), table_name='logs_auditoria')
    op.drop_index(op.f('ix_logs_auditoria_fecha_hora'), table_name='logs_auditoria')
    op.drop_index(op.f('ix_logs_auditoria_exitoso'), table_name='logs_auditoria')
    op.drop_index(op.f('ix_logs_auditoria_entidad'), table_name='logs_auditoria')
    op.drop_index(op.f('ix_logs_auditoria_accion'), table_name='logs_auditoria')
    op.drop_table('logs_auditoria')

    op.execute('DROP TYPE IF EXISTS tipo_accion_auditoria')
    op.execute('DROP TYPE IF EXISTS tipo_rol')
