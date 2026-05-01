"""add_eventos_domain

Nuevo dominio de Eventos: tipos, estados, eventos, participantes, materiales,
grupos, tareas y gastos por evento. Soporte de recurrencia y presupuesto propio.

Revision ID: a2b3c4d5e6f7
Revises: f5g6h7i8j9k0
Create Date: 2026-05-01 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, None] = 'f5g6h7i8j9k0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- tipos_evento ---
    op.create_table(
        'tipos_evento',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('requiere_inscripcion', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('requiere_aforo', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tipos_evento_activo', 'tipos_evento', ['activo'])

    # --- estados_evento ---
    op.create_table(
        'estados_evento',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('es_final', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_estados_evento_activo', 'estados_evento', ['activo'])

    # --- eventos ---
    op.create_table(
        'eventos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('descripcion_corta', sa.String(500), nullable=True),
        sa.Column('descripcion_larga', sa.Text(), nullable=True),
        sa.Column('tipo_evento_id', sa.Uuid(), nullable=False),
        sa.Column('estado_id', sa.Uuid(), nullable=False),
        # Recurrencia
        sa.Column('recurrente', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('periodo_recurrencia', sa.String(20), nullable=True),
        sa.Column('evento_plantilla_id', sa.Uuid(), nullable=True),
        # Programación
        sa.Column('fecha_inicio', sa.Date(), nullable=False),
        sa.Column('fecha_fin', sa.Date(), nullable=True),
        sa.Column('hora_inicio', sa.Time(), nullable=True),
        sa.Column('hora_fin', sa.Time(), nullable=True),
        sa.Column('es_todo_el_dia', sa.Boolean(), nullable=False, server_default='true'),
        # Lugar
        sa.Column('lugar', sa.String(200), nullable=True),
        sa.Column('direccion', sa.String(500), nullable=True),
        sa.Column('ciudad', sa.String(100), nullable=True),
        sa.Column('es_online', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('url_online', sa.String(500), nullable=True),
        # Inscripciones
        sa.Column('aforo_maximo', sa.Integer(), nullable=True),
        sa.Column('requiere_inscripcion', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_limite_inscripcion', sa.Date(), nullable=True),
        # Presupuesto
        sa.Column('dotacion_economica', sa.Numeric(12, 2), nullable=False, server_default='0.00'),
        sa.Column('partida_id', sa.Uuid(), nullable=True),
        # Organización
        sa.Column('responsable_id', sa.Uuid(), nullable=True),
        sa.Column('campania_id', sa.Uuid(), nullable=True),
        sa.Column('agrupacion_id', sa.Uuid(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tipo_evento_id'], ['tipos_evento.id']),
        sa.ForeignKeyConstraint(['estado_id'], ['estados_evento.id']),
        sa.ForeignKeyConstraint(['responsable_id'], ['miembros.id']),
        sa.ForeignKeyConstraint(['campania_id'], ['campanias.id']),
        sa.ForeignKeyConstraint(['agrupacion_id'], ['agrupaciones_territoriales.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    # Autorreferencia evento_plantilla_id después de crear la tabla
    op.create_foreign_key('fk_eventos_plantilla', 'eventos', 'eventos', ['evento_plantilla_id'], ['id'])
    op.create_index('ix_eventos_nombre', 'eventos', ['nombre'])
    op.create_index('ix_eventos_fecha_inicio', 'eventos', ['fecha_inicio'])
    op.create_index('ix_eventos_tipo_evento_id', 'eventos', ['tipo_evento_id'])
    op.create_index('ix_eventos_estado_id', 'eventos', ['estado_id'])
    op.create_index('ix_eventos_campania_id', 'eventos', ['campania_id'])
    op.create_index('ix_eventos_plantilla_id', 'eventos', ['evento_plantilla_id'])

    # --- participantes_evento ---
    op.create_table(
        'participantes_evento',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('evento_id', sa.Uuid(), nullable=False),
        sa.Column('miembro_id', sa.Uuid(), nullable=False),
        sa.Column('rol', sa.String(50), nullable=False, server_default='ASISTENTE'),
        sa.Column('confirmado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('asistio', sa.Boolean(), nullable=True),
        sa.Column('fecha_inscripcion', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['evento_id'], ['eventos.id']),
        sa.ForeignKeyConstraint(['miembro_id'], ['miembros.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_participantes_evento_evento_id', 'participantes_evento', ['evento_id'])
    op.create_index('ix_participantes_evento_miembro_id', 'participantes_evento', ['miembro_id'])

    # --- materiales_evento ---
    op.create_table(
        'materiales_evento',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('evento_id', sa.Uuid(), nullable=False),
        sa.Column('tipo', sa.String(50), nullable=False),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('url', sa.String(1000), nullable=True),
        sa.Column('fecha_subida', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['evento_id'], ['eventos.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_materiales_evento_evento_id', 'materiales_evento', ['evento_id'])

    # --- grupos_evento ---
    op.create_table(
        'grupos_evento',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('evento_id', sa.Uuid(), nullable=False),
        sa.Column('grupo_trabajo_id', sa.Uuid(), nullable=False),
        sa.Column('responsabilidades', sa.Text(), nullable=True),
        sa.Column('horas_estimadas', sa.Numeric(6, 2), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['evento_id'], ['eventos.id']),
        sa.ForeignKeyConstraint(['grupo_trabajo_id'], ['grupos_trabajo.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_grupos_evento_evento_id', 'grupos_evento', ['evento_id'])

    # --- tareas_evento ---
    op.create_table(
        'tareas_evento',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('evento_id', sa.Uuid(), nullable=False),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('grupo_trabajo_id', sa.Uuid(), nullable=True),
        sa.Column('responsable_id', sa.Uuid(), nullable=True),
        sa.Column('completada', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_limite', sa.Date(), nullable=True),
        sa.Column('fecha_completada', sa.DateTime(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['evento_id'], ['eventos.id']),
        sa.ForeignKeyConstraint(['grupo_trabajo_id'], ['grupos_trabajo.id']),
        sa.ForeignKeyConstraint(['responsable_id'], ['miembros.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tareas_evento_evento_id', 'tareas_evento', ['evento_id'])

    # --- gastos_evento ---
    op.create_table(
        'gastos_evento',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('evento_id', sa.Uuid(), nullable=False),
        sa.Column('concepto', sa.String(500), nullable=False),
        sa.Column('importe', sa.Numeric(10, 2), nullable=False),
        sa.Column('proveedor_id', sa.Uuid(), nullable=True),
        sa.Column('factura_referencia', sa.String(100), nullable=True),
        sa.Column('pagado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_pago', sa.Date(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['evento_id'], ['eventos.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_gastos_evento_evento_id', 'gastos_evento', ['evento_id'])


def downgrade() -> None:
    op.drop_index('ix_gastos_evento_evento_id', table_name='gastos_evento')
    op.drop_table('gastos_evento')

    op.drop_index('ix_tareas_evento_evento_id', table_name='tareas_evento')
    op.drop_table('tareas_evento')

    op.drop_index('ix_grupos_evento_evento_id', table_name='grupos_evento')
    op.drop_table('grupos_evento')

    op.drop_index('ix_materiales_evento_evento_id', table_name='materiales_evento')
    op.drop_table('materiales_evento')

    op.drop_index('ix_participantes_evento_miembro_id', table_name='participantes_evento')
    op.drop_index('ix_participantes_evento_evento_id', table_name='participantes_evento')
    op.drop_table('participantes_evento')

    op.drop_constraint('fk_eventos_plantilla', 'eventos', type_='foreignkey')
    op.drop_index('ix_eventos_plantilla_id', table_name='eventos')
    op.drop_index('ix_eventos_campania_id', table_name='eventos')
    op.drop_index('ix_eventos_estado_id', table_name='eventos')
    op.drop_index('ix_eventos_tipo_evento_id', table_name='eventos')
    op.drop_index('ix_eventos_fecha_inicio', table_name='eventos')
    op.drop_index('ix_eventos_nombre', table_name='eventos')
    op.drop_table('eventos')

    op.drop_index('ix_estados_evento_activo', table_name='estados_evento')
    op.drop_table('estados_evento')

    op.drop_index('ix_tipos_evento_activo', table_name='tipos_evento')
    op.drop_table('tipos_evento')
