"""m037: modelo Accion unificado (tipos_accion, estados_accion, acciones, tareas, participaciones, grupo_iniciativa)

Revision ID: m037
Revises: m036
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa
import uuid

revision = 'm037'
down_revision = 'm036'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── tipos_accion ──────────────────────────────────────────────────────────
    op.create_table(
        'tipos_accion',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('tiene_lugar', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('tiene_participantes', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_tipos_accion_activo', 'tipos_accion', ['activo'])

    # ── estados_accion ────────────────────────────────────────────────────────
    op.create_table(
        'estados_accion',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('es_inicial', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('es_final', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_estados_accion_activo', 'estados_accion', ['activo'])

    # ── acciones ──────────────────────────────────────────────────────────────
    op.create_table(
        'acciones',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('tipo_accion_id', sa.Uuid(), sa.ForeignKey('tipos_accion.id'), nullable=False),
        sa.Column('estado_id', sa.Uuid(), sa.ForeignKey('estados_accion.id'), nullable=False),
        # temporal
        sa.Column('fecha_inicio', sa.Date(), nullable=True),
        sa.Column('hora_inicio', sa.Time(), nullable=True),
        sa.Column('fecha_fin', sa.Date(), nullable=True),
        sa.Column('hora_fin', sa.Time(), nullable=True),
        # lugar
        sa.Column('lugar', sa.String(200), nullable=True),
        sa.Column('direccion', sa.String(500), nullable=True),
        sa.Column('aforo', sa.Integer(), nullable=True),
        sa.Column('es_online', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('url_online', sa.String(500), nullable=True),
        # económico
        sa.Column('presupuesto_estimado', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('presupuesto_ejecutado', sa.Numeric(12, 2), nullable=False, server_default='0'),
        # relaciones
        sa.Column('iniciativa_id', sa.Uuid(), sa.ForeignKey('campanias.id'), nullable=True),
        sa.Column('grupo_id', sa.Uuid(), sa.ForeignKey('grupos_trabajo.id'), nullable=True),
        sa.Column('responsable_id', sa.Uuid(), sa.ForeignKey('miembros.id'), nullable=True),
        # audit
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_acciones_nombre', 'acciones', ['nombre'])
    op.create_index('ix_acciones_fecha_inicio', 'acciones', ['fecha_inicio'])
    op.create_index('ix_acciones_tipo_accion_id', 'acciones', ['tipo_accion_id'])
    op.create_index('ix_acciones_estado_id', 'acciones', ['estado_id'])
    op.create_index('ix_acciones_iniciativa_id', 'acciones', ['iniciativa_id'])
    op.create_index('ix_acciones_grupo_id', 'acciones', ['grupo_id'])
    op.create_index('ix_acciones_responsable_id', 'acciones', ['responsable_id'])

    # ── tareas (unificada) ────────────────────────────────────────────────────
    op.create_table(
        'tareas',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('titulo', sa.String(200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('prioridad', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('estado_id', sa.Uuid(), sa.ForeignKey('estados_tarea.id'), nullable=False),
        sa.Column('responsable_id', sa.Uuid(), sa.ForeignKey('miembros.id'), nullable=True),
        sa.Column('horas_estimadas', sa.Numeric(6, 2), nullable=True),
        sa.Column('horas_reales', sa.Numeric(6, 2), nullable=True),
        sa.Column('fecha_limite', sa.Date(), nullable=True),
        sa.Column('fecha_completada', sa.DateTime(), nullable=True),
        # padre (exactamente uno)
        sa.Column('accion_id', sa.Uuid(), sa.ForeignKey('acciones.id'), nullable=True),
        sa.Column('grupo_id', sa.Uuid(), sa.ForeignKey('grupos_trabajo.id'), nullable=True),
        # audit
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_tareas_estado_id', 'tareas', ['estado_id'])
    op.create_index('ix_tareas_responsable_id', 'tareas', ['responsable_id'])
    op.create_index('ix_tareas_accion_id', 'tareas', ['accion_id'])
    op.create_index('ix_tareas_grupo_id', 'tareas', ['grupo_id'])

    # ── participaciones ───────────────────────────────────────────────────────
    op.create_table(
        'participaciones',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('accion_id', sa.Uuid(), sa.ForeignKey('acciones.id'), nullable=False),
        sa.Column('miembro_id', sa.Uuid(), sa.ForeignKey('miembros.id'), nullable=True),
        sa.Column('nombre_externo', sa.String(200), nullable=True),
        sa.Column('email_externo', sa.String(200), nullable=True),
        sa.Column('rol', sa.String(50), nullable=False, server_default='asistente'),
        sa.Column('confirmado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('asistio', sa.Boolean(), nullable=True),
        sa.Column('horas_aportadas', sa.Numeric(6, 2), nullable=False, server_default='0'),
        # audit
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_participaciones_accion_id', 'participaciones', ['accion_id'])
    op.create_index('ix_participaciones_miembro_id', 'participaciones', ['miembro_id'])

    # ── grupo_iniciativa ──────────────────────────────────────────────────────
    op.create_table(
        'grupo_iniciativa',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('grupo_id', sa.Uuid(), sa.ForeignKey('grupos_trabajo.id'), nullable=False),
        sa.Column('iniciativa_id', sa.Uuid(), sa.ForeignKey('campanias.id'), nullable=False),
        sa.Column('rol', sa.String(50), nullable=False, server_default='colaborador'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('grupo_id', 'iniciativa_id', name='uq_grupo_iniciativa'),
    )
    op.create_index('ix_grupo_iniciativa_grupo_id', 'grupo_iniciativa', ['grupo_id'])
    op.create_index('ix_grupo_iniciativa_iniciativa_id', 'grupo_iniciativa', ['iniciativa_id'])


def downgrade() -> None:
    op.drop_table('grupo_iniciativa')
    op.drop_table('participaciones')
    op.drop_table('tareas')
    op.drop_table('acciones')
    op.drop_table('estados_accion')
    op.drop_table('tipos_accion')
