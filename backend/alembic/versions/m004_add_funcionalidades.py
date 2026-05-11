"""add funcionalidades, roles_funcionalidades, funcionalidades_transacciones, flujos_aprobacion

Revision ID: m004
Revises: m003
Create Date: 2026-05-05

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'm004'
down_revision: Union[str, Sequence[str], None] = 'm003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _audit():
    return [
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('creado_por_id', sa.Uuid(), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        'funcionalidades',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('codigo', sa.String(100), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('modulo', sa.String(100), nullable=False),
        sa.Column('activa', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sistema', sa.Boolean(), server_default='false', nullable=False),
        *_audit(),
    )
    op.create_index('ix_funcionalidades_codigo', 'funcionalidades', ['codigo'], unique=True)
    op.create_index('ix_funcionalidades_modulo', 'funcionalidades', ['modulo'])
    op.create_index('ix_funcionalidades_activa', 'funcionalidades', ['activa'])
    op.create_index('ix_funcionalidades_eliminado', 'funcionalidades', ['eliminado'])
    op.create_foreign_key(None, 'funcionalidades', 'usuarios', ['creado_por_id'], ['id'])
    op.create_foreign_key(None, 'funcionalidades', 'usuarios', ['modificado_por_id'], ['id'])

    op.create_table(
        'roles_funcionalidades',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('rol_id', sa.Uuid(), nullable=False),
        sa.Column('funcionalidad_id', sa.Uuid(), nullable=False),
        sa.UniqueConstraint('rol_id', 'funcionalidad_id', name='uq_rol_funcionalidad'),
        *_audit(),
    )
    op.create_index('ix_roles_funcionalidades_rol_id', 'roles_funcionalidades', ['rol_id'])
    op.create_index('ix_roles_funcionalidades_funcionalidad_id', 'roles_funcionalidades', ['funcionalidad_id'])
    op.create_index('ix_roles_funcionalidades_eliminado', 'roles_funcionalidades', ['eliminado'])
    op.create_foreign_key(None, 'roles_funcionalidades', 'roles', ['rol_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'roles_funcionalidades', 'funcionalidades', ['funcionalidad_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'roles_funcionalidades', 'usuarios', ['creado_por_id'], ['id'])
    op.create_foreign_key(None, 'roles_funcionalidades', 'usuarios', ['modificado_por_id'], ['id'])

    op.create_table(
        'funcionalidades_transacciones',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('funcionalidad_id', sa.Uuid(), nullable=False),
        sa.Column('transaccion_id', sa.Uuid(), nullable=False),
        sa.Column('ambito', sa.Enum('GLOBAL', 'TERRITORIAL', 'PROPIO', name='ambito_transaccion'), nullable=False, server_default='TERRITORIAL'),
        sa.UniqueConstraint('funcionalidad_id', 'transaccion_id', name='uq_funcionalidad_transaccion'),
        *_audit(),
    )
    op.create_index('ix_funcionalidades_transacciones_funcionalidad_id', 'funcionalidades_transacciones', ['funcionalidad_id'])
    op.create_index('ix_funcionalidades_transacciones_transaccion_id', 'funcionalidades_transacciones', ['transaccion_id'])
    op.create_index('ix_funcionalidades_transacciones_eliminado', 'funcionalidades_transacciones', ['eliminado'])
    op.create_foreign_key(None, 'funcionalidades_transacciones', 'funcionalidades', ['funcionalidad_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'funcionalidades_transacciones', 'transacciones', ['transaccion_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'funcionalidades_transacciones', 'usuarios', ['creado_por_id'], ['id'])
    op.create_foreign_key(None, 'funcionalidades_transacciones', 'usuarios', ['modificado_por_id'], ['id'])

    op.create_table(
        'flujos_aprobacion',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('codigo', sa.String(100), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('transaccion_inicio_id', sa.Uuid(), nullable=False),
        sa.Column('transaccion_aprobacion_id', sa.Uuid(), nullable=False),
        sa.Column('transaccion_rechazo_id', sa.Uuid(), nullable=True),
        sa.Column('rol_aprobador_id', sa.Uuid(), nullable=False),
        sa.Column('entidad', sa.String(100), nullable=False),
        sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sistema', sa.Boolean(), server_default='false', nullable=False),
        *_audit(),
    )
    op.create_index('ix_flujos_aprobacion_codigo', 'flujos_aprobacion', ['codigo'], unique=True)
    op.create_index('ix_flujos_aprobacion_rol_aprobador_id', 'flujos_aprobacion', ['rol_aprobador_id'])
    op.create_index('ix_flujos_aprobacion_eliminado', 'flujos_aprobacion', ['eliminado'])
    op.create_foreign_key(None, 'flujos_aprobacion', 'transacciones', ['transaccion_inicio_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key(None, 'flujos_aprobacion', 'transacciones', ['transaccion_aprobacion_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key(None, 'flujos_aprobacion', 'transacciones', ['transaccion_rechazo_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'flujos_aprobacion', 'roles', ['rol_aprobador_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key(None, 'flujos_aprobacion', 'usuarios', ['creado_por_id'], ['id'])
    op.create_foreign_key(None, 'flujos_aprobacion', 'usuarios', ['modificado_por_id'], ['id'])


def downgrade() -> None:
    op.drop_table('flujos_aprobacion')
    op.drop_table('funcionalidades_transacciones')
    op.execute("DROP TYPE IF EXISTS ambito_transaccion")
    op.drop_table('roles_funcionalidades')
    op.drop_table('funcionalidades')
