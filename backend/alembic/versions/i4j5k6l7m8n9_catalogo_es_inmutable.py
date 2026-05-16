"""Añade es_inmutable a todos los catálogos del sistema y actualiza colores de estados.

Revision ID: i4j5k6l7m8n9
Revises: h3i4j5k6l7m8
Create Date: 2026-05-16 14:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision: str = 'i4j5k6l7m8n9'
down_revision: str = 'h3i4j5k6l7m8'
branch_labels = None
depends_on = None

# Todas las tablas de catálogo que reciben es_inmutable
CATALOG_TABLES = [
    # Configuración: estados
    'estados_cuota',
    'estados_campania',
    'estados_tarea',
    'estados_accion',
    'estados_actividad',
    'estados_participante',
    'estados_orden_cobro',
    'estados_remesa',
    'estados_donacion',
    'estados_notificacion',
    # Membresía
    'tipos_miembro',
    'estados_miembro',
    'motivos_baja',
    'categorias_habilidad',
    'niveles_estudios',
    'niveles_habilidad',
    'habilidades',
    # Financiero
    'formas_pago',
    # Campañas
    'tipos_campania',
    'tipos_meta_campania',
    'tipos_canal_difusion',
    'roles_participante',
    # Actividades
    'tipos_accion',
    'tipos_grupo',
    # Organizaciones
    'estados_convenio',
    # Usuarios
    'tipos_vinculacion',
]

# Colores para estados de campaña (hex reales — los existentes son NULL o "primary")
ESTADOS_CAMPANIA_COLORES = [
    ('Borrador',    '#6B7280'),   # gris      — draft/neutro
    ('Programada',  '#3B82F6'),   # azul      — scheduled
    ('En curso',    '#10B981'),   # verde     — activo
    ('Pausada',     '#F59E0B'),   # ámbar     — advertencia
    ('Finalizada',  '#6366F1'),   # índigo    — completado
    ('Cancelada',   '#EF4444'),   # rojo      — cancelado
]


def upgrade() -> None:
    # 1. Añadir es_inmutable a todas las tablas de catálogo
    for table in CATALOG_TABLES:
        op.add_column(
            table,
            sa.Column('es_inmutable', sa.Boolean, server_default='false', nullable=False)
        )

    # 2. Marcar todos los registros actuales como inmutables
    #    (fueron insertados en seeding, no por usuarios)
    for table in CATALOG_TABLES:
        op.execute(f"UPDATE {table} SET es_inmutable = true WHERE eliminado = false OR eliminado IS NULL")

    # 3. Actualizar colores de estados_campania con valores hex reales
    for nombre, color in ESTADOS_CAMPANIA_COLORES:
        op.execute(
            sa.text("UPDATE estados_campania SET color = :color WHERE nombre = :nombre").bindparams(color=color, nombre=nombre)
        )


def downgrade() -> None:
    for table in reversed(CATALOG_TABLES):
        op.drop_column(table, 'es_inmutable')
