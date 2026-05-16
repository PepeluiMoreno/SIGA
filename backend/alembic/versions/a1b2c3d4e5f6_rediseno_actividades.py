"""Rediseño módulo actividades: Accion→Actividad, recurrencia, recursos, skill drop.

Revision ID: a1b2c3d4e5f6
Revises: ce07b20ae5d3
Create Date: 2026-05-14

"""
from __future__ import annotations
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ce07b20ae5d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Renombrar tabla acciones → actividades
    op.rename_table('acciones', 'actividades')

    # 2. Renombrar columna iniciativa_id → campania_id en actividades
    op.alter_column('actividades', 'iniciativa_id', new_column_name='campania_id')

    # 3. Añadir campos de recurrencia a actividades
    op.add_column('actividades', sa.Column('padre_id', sa.Uuid(), nullable=True))
    op.add_column('actividades', sa.Column('es_recurrente', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('actividades', sa.Column('periodicidad', sa.String(20), nullable=True))

    # FK auto-referencial
    op.create_foreign_key(
        'fk_actividades_padre_id', 'actividades', 'actividades',
        ['padre_id'], ['id'],
    )
    op.create_index('ix_actividades_padre_id', 'actividades', ['padre_id'])

    # 4. Renombrar tipo_accion_id → tipo_actividad_id en actividades
    #    (la tabla tipos_accion no cambia de nombre)
    op.alter_column('actividades', 'tipo_accion_id', new_column_name='tipo_actividad_id')

    # 5. Tareas: renombrar accion_id → actividad_id, actualizar FK
    op.drop_constraint('tareas_accion_id_fkey', 'tareas', type_='foreignkey')
    op.alter_column('tareas', 'accion_id', new_column_name='actividad_id')
    op.create_foreign_key(
        'fk_tareas_actividad_id', 'tareas', 'actividades',
        ['actividad_id'], ['id'],
    )

    # 6. grupo_iniciativa: renombrar iniciativa_id → campania_id
    op.drop_constraint('grupo_iniciativa_iniciativa_id_fkey', 'grupo_iniciativa', type_='foreignkey')
    op.alter_column('grupo_iniciativa', 'iniciativa_id', new_column_name='campania_id')
    op.create_foreign_key(
        'fk_grupo_iniciativa_campania_id', 'grupo_iniciativa', 'campanias',
        ['campania_id'], ['id'],
    )

    # 7. Campañas: campos de recurrencia
    op.add_column('campanias', sa.Column('padre_id', sa.Uuid(), nullable=True))
    op.add_column('campanias', sa.Column('es_recurrente', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('campanias', sa.Column('periodicidad', sa.String(20), nullable=True))
    op.add_column('campanias', sa.Column('anio_edicion', sa.Integer(), nullable=True))

    op.create_foreign_key(
        'fk_campanias_padre_id', 'campanias', 'campanias',
        ['padre_id'], ['id'],
    )
    op.create_index('ix_campanias_padre_id', 'campanias', ['padre_id'])

    # 8. Nueva tabla requisitos_recurso
    op.create_table(
        'requisitos_recurso',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('grupo_id', sa.Uuid(), sa.ForeignKey('grupos_trabajo.id'), nullable=False, index=True),
        sa.Column('especialidad_id', sa.Uuid(), nullable=False, index=True),
        sa.Column('nivel_id', sa.Uuid(), nullable=False, index=True),
        sa.Column('horas_necesarias', sa.Numeric(8, 2), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        # BaseModel columns
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    )

    # 9. Nueva tabla aportaciones_horas
    op.create_table(
        'aportaciones_horas',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('requisito_id', sa.Uuid(), sa.ForeignKey('requisitos_recurso.id'), nullable=False, index=True),
        sa.Column('miembro_id', sa.Uuid(), sa.ForeignKey('miembros.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('horas_comprometidas', sa.Numeric(6, 2), nullable=False),
        sa.Column('horas_reales', sa.Numeric(6, 2), nullable=False, server_default='0'),
        sa.Column('confirmado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_compromiso', sa.Date(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        # BaseModel columns
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    )

    # 10. Nueva tabla compromisos_presupuestarios
    op.create_table(
        'compromisos_presupuestarios',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('partida_id', sa.Uuid(), sa.ForeignKey('partidas_presupuestarias.id'), nullable=False, index=True),
        sa.Column('campania_id', sa.Uuid(), nullable=True, index=True),
        sa.Column('actividad_id', sa.Uuid(), nullable=True, index=True),
        sa.Column('importe_comprometido', sa.Numeric(12, 2), nullable=False),
        sa.Column('concepto', sa.String(500), nullable=True),
        sa.Column('fecha_compromiso', sa.Date(), nullable=False),
        sa.Column('estado', sa.String(20), nullable=False, server_default='activo'),
        # BaseModel columns
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    )

    # 11. Eliminar tablas skill si existen (pueden no existir si no se crearon)
    op.execute('DROP TABLE IF EXISTS miembros_skills')
    op.execute('DROP TABLE IF EXISTS skills')


def downgrade() -> None:
    # Invertir en orden contrario — restaurar skills
    op.create_table(
        'skills',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('nombre', sa.String(150), nullable=False),
        sa.Column('descripcion', sa.String(500), nullable=True),
        sa.Column('categoria', sa.String(100), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'miembros_skills',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('miembro_id', sa.Uuid(), sa.ForeignKey('miembros.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_id', sa.Uuid(), sa.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False),
        sa.Column('nivel', sa.String(20), nullable=True),
        sa.Column('validado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('validado_por_id', sa.Uuid(), nullable=True),
        sa.Column('fecha_validacion', sa.Date(), nullable=True),
        sa.Column('notas', sa.String(500), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    )

    op.drop_table('compromisos_presupuestarios')
    op.drop_table('aportaciones_horas')
    op.drop_table('requisitos_recurso')

    op.drop_index('ix_campanias_padre_id', 'campanias')
    op.drop_constraint('fk_campanias_padre_id', 'campanias', type_='foreignkey')
    op.drop_column('campanias', 'anio_edicion')
    op.drop_column('campanias', 'periodicidad')
    op.drop_column('campanias', 'es_recurrente')
    op.drop_column('campanias', 'padre_id')

    op.drop_constraint('fk_grupo_iniciativa_campania_id', 'grupo_iniciativa', type_='foreignkey')
    op.alter_column('grupo_iniciativa', 'campania_id', new_column_name='iniciativa_id')
    op.create_foreign_key(None, 'grupo_iniciativa', 'campanias', ['iniciativa_id'], ['id'])

    op.drop_constraint('fk_tareas_actividad_id', 'tareas', type_='foreignkey')
    op.alter_column('tareas', 'actividad_id', new_column_name='accion_id')
    op.create_foreign_key(None, 'tareas', 'actividades', ['accion_id'], ['id'])

    op.alter_column('actividades', 'tipo_actividad_id', new_column_name='tipo_accion_id')
    op.drop_index('ix_actividades_padre_id', 'actividades')
    op.drop_constraint('fk_actividades_padre_id', 'actividades', type_='foreignkey')
    op.drop_column('actividades', 'periodicidad')
    op.drop_column('actividades', 'es_recurrente')
    op.drop_column('actividades', 'padre_id')
    op.alter_column('actividades', 'campania_id', new_column_name='iniciativa_id')
    op.rename_table('actividades', 'acciones')
