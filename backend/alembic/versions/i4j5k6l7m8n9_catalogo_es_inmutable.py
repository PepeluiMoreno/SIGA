"""Añade es_inmutable a todos los catálogos del sistema y actualiza colores de estados.

Idempotente: usa `ADD COLUMN IF NOT EXISTS`. Las tablas pueden no existir
aún en algunos entornos parcialmente migrados; se ignoran con WHERE EXISTS.

Revision ID: i4j5k6l7m8n9
Revises: h3i4j5k6l7m8
Create Date: 2026-05-16 14:00:00.000000
"""

from alembic import op

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

# Colores para estados de campaña (hex reales)
ESTADOS_CAMPANIA_COLORES = [
    ('Borrador',    '#6B7280'),
    ('Programada',  '#3B82F6'),
    ('En curso',    '#10B981'),
    ('Pausada',     '#F59E0B'),
    ('Finalizada',  '#6366F1'),
    ('Cancelada',   '#EF4444'),
]


def upgrade() -> None:
    # Idempotente: solo añade la columna si no existe y la tabla existe.
    for table in CATALOG_TABLES:
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables
                           WHERE table_name = '{table}') THEN
                    ALTER TABLE {table}
                      ADD COLUMN IF NOT EXISTS es_inmutable BOOLEAN NOT NULL DEFAULT FALSE;
                    UPDATE {table} SET es_inmutable = TRUE
                      WHERE eliminado = FALSE OR eliminado IS NULL;
                END IF;
            END$$;
        """)

    # Colores de estados_campania (solo si la tabla existe).
    bind = op.get_bind()
    for nombre, color in ESTADOS_CAMPANIA_COLORES:
        bind.exec_driver_sql(
            "UPDATE estados_campania SET color = "
            f"'{color}' WHERE nombre = '{nombre}'"
        )


def downgrade() -> None:
    for table in reversed(CATALOG_TABLES):
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS es_inmutable")
