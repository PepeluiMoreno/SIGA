"""Estados de secretaría: reuniones, actas y ejecución de acuerdos.

Revision ID: l7m8n9o0p1q2
Revises: k6l7m8n9o0p1
Create Date: 2026-05-20 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'l7m8n9o0p1q2'
down_revision = 'k6l7m8n9o0p1'
branch_labels = None
depends_on = None

AUDITORIA = [
    sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
    sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
    sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
    sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
    sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
    sa.Column('es_inmutable',       sa.Boolean(),  nullable=False, server_default='false'),
]

BASE_COLS = [
    sa.Column('id',          sa.Uuid(),      nullable=False),
    sa.Column('nombre',      sa.String(100), nullable=False),
    sa.Column('descripcion', sa.Text(),      nullable=True),
    sa.Column('orden',       sa.Integer(),   nullable=False, server_default='0'),
    sa.Column('es_inicial',  sa.Boolean(),   nullable=False, server_default='false'),
    sa.Column('es_final',    sa.Boolean(),   nullable=False, server_default='false'),
    sa.Column('activo',      sa.Boolean(),   nullable=False, server_default='true'),
    sa.Column('color',       sa.String(20),  nullable=True),
    sa.Column('codigo',      sa.String(30),  nullable=False),
]


def upgrade() -> None:
    # ── Tabla estados_reunion ──────────────────────────────────────────────
    op.create_table(
        'estados_reunion',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nombre',      sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(),      nullable=True),
        sa.Column('orden',       sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('es_inicial',  sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('es_final',    sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('activo',      sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('color',       sa.String(20),  nullable=True),
        sa.Column('codigo',      sa.String(30),  nullable=False),
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('es_inmutable',       sa.Boolean(),  nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo'),
    )
    op.create_index('ix_estados_reunion_activo', 'estados_reunion', ['activo'])

    # ── Tabla estados_acta ────────────────────────────────────────────────
    op.create_table(
        'estados_acta',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nombre',      sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(),      nullable=True),
        sa.Column('orden',       sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('es_inicial',  sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('es_final',    sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('activo',      sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('color',       sa.String(20),  nullable=True),
        sa.Column('codigo',      sa.String(30),  nullable=False),
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('es_inmutable',       sa.Boolean(),  nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo'),
    )
    op.create_index('ix_estados_acta_activo', 'estados_acta', ['activo'])

    # ── Tabla estados_ejecucion_acuerdo ───────────────────────────────────
    op.create_table(
        'estados_ejecucion_acuerdo',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nombre',      sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(),      nullable=True),
        sa.Column('orden',       sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('es_inicial',  sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('es_final',    sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('activo',      sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('color',       sa.String(20),  nullable=True),
        sa.Column('codigo',      sa.String(30),  nullable=False),
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('es_inmutable',       sa.Boolean(),  nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo'),
    )
    op.create_index('ix_estados_ejecucion_activo', 'estados_ejecucion_acuerdo', ['activo'])

    # ── FKs en tablas de secretaría ───────────────────────────────────────
    op.add_column('sec_reuniones', sa.Column('estado_id', sa.Uuid(), nullable=True))
    op.add_column('sec_reuniones', sa.Column('estado_codigo', sa.String(30),
        nullable=False, server_default='CONVOCADA'))
    op.create_foreign_key('fk_sec_reuniones_estado', 'sec_reuniones',
        'estados_reunion', ['estado_id'], ['id'])
    op.create_index('ix_sec_reuniones_estado_codigo', 'sec_reuniones', ['estado_codigo'])
    # Eliminar la columna string antigua
    op.drop_index('ix_sec_reuniones_estado', 'sec_reuniones')
    op.drop_column('sec_reuniones', 'estado')

    op.add_column('sec_actas', sa.Column('estado_id', sa.Uuid(), nullable=True))
    op.add_column('sec_actas', sa.Column('estado_codigo', sa.String(30),
        nullable=False, server_default='BORRADOR'))
    op.create_foreign_key('fk_sec_actas_estado', 'sec_actas',
        'estados_acta', ['estado_id'], ['id'])
    op.create_index('ix_sec_actas_estado_codigo', 'sec_actas', ['estado_codigo'])
    op.drop_index('ix_sec_actas_estado', 'sec_actas')
    op.drop_column('sec_actas', 'estado')

    op.add_column('sec_acuerdos', sa.Column('estado_ejecucion_id', sa.Uuid(), nullable=True))
    op.add_column('sec_acuerdos', sa.Column('estado_ejecucion_codigo', sa.String(30),
        nullable=False, server_default='PENDIENTE'))
    op.create_foreign_key('fk_sec_acuerdos_estado_ejecucion', 'sec_acuerdos',
        'estados_ejecucion_acuerdo', ['estado_ejecucion_id'], ['id'])
    op.create_index('ix_sec_acuerdos_estado_ejecucion_codigo', 'sec_acuerdos', ['estado_ejecucion_codigo'])
    op.drop_index('ix_sec_acuerdos_estado_ejecucion', 'sec_acuerdos')
    op.drop_column('sec_acuerdos', 'estado_ejecucion')


def downgrade() -> None:
    # Restaurar columnas string
    op.add_column('sec_acuerdos', sa.Column('estado_ejecucion', sa.String(20),
        nullable=False, server_default='PENDIENTE'))
    op.drop_constraint('fk_sec_acuerdos_estado_ejecucion', 'sec_acuerdos')
    op.drop_column('sec_acuerdos', 'estado_ejecucion_id')
    op.drop_column('sec_acuerdos', 'estado_ejecucion_codigo')

    op.add_column('sec_actas', sa.Column('estado', sa.String(20),
        nullable=False, server_default='BORRADOR'))
    op.drop_constraint('fk_sec_actas_estado', 'sec_actas')
    op.drop_column('sec_actas', 'estado_id')
    op.drop_column('sec_actas', 'estado_codigo')

    op.add_column('sec_reuniones', sa.Column('estado', sa.String(30),
        nullable=False, server_default='CONVOCADA'))
    op.drop_constraint('fk_sec_reuniones_estado', 'sec_reuniones')
    op.drop_column('sec_reuniones', 'estado_id')
    op.drop_column('sec_reuniones', 'estado_codigo')

    op.drop_table('estados_ejecucion_acuerdo')
    op.drop_table('estados_acta')
    op.drop_table('estados_reunion')
