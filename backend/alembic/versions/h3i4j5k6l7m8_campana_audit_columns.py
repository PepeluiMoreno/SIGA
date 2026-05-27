"""Añade columnas de auditoría a las nuevas tablas de campañas.

Idempotente: usa `ADD COLUMN IF NOT EXISTS` y `CREATE INDEX IF NOT EXISTS`.
La versión original con `op.add_column` directa fallaba en entornos donde
la columna ya había sido creada por otra vía (en staging la columna
`fecha_creacion` ya existía cuando se intentó aplicar la migración).

Revision ID: h3i4j5k6l7m8
Revises: g2h3i4j5k6l7
Create Date: 2026-05-16 13:00:00.000000
"""

from alembic import op


revision: str = 'h3i4j5k6l7m8'
down_revision: str = 'g2h3i4j5k6l7'
branch_labels = None
depends_on = None

AUDIT_TABLES = [
    'tipos_meta_campania',
    'tipos_canal_difusion',
    'metas_campania',
    'canales_difusion_campania',
    'partidas_presupuesto_campania',
    'plantillas_campania',
    'plantilla_metas',
    'plantilla_partidas',
    'plantilla_actividades',
    'plantilla_tareas',
]


def _add_audit_columns(table_name: str) -> None:
    """Añade columnas de auditoría idempotentemente.

    Cada sentencia va por separado: asyncpg no admite múltiples comandos
    por prepared statement.
    """
    op.execute(
        f"ALTER TABLE {table_name} "
        "ADD COLUMN IF NOT EXISTS fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()"
    )
    op.execute(
        f"ALTER TABLE {table_name} "
        "ADD COLUMN IF NOT EXISTS fecha_modificacion TIMESTAMP"
    )
    op.execute(
        f"ALTER TABLE {table_name} "
        "ADD COLUMN IF NOT EXISTS fecha_eliminacion TIMESTAMP"
    )
    op.execute(
        f"ALTER TABLE {table_name} "
        "ADD COLUMN IF NOT EXISTS eliminado BOOLEAN NOT NULL DEFAULT FALSE"
    )
    op.execute(
        f"ALTER TABLE {table_name} "
        "ADD COLUMN IF NOT EXISTS creado_por_id UUID REFERENCES usuarios(id)"
    )
    op.execute(
        f"ALTER TABLE {table_name} "
        "ADD COLUMN IF NOT EXISTS modificado_por_id UUID REFERENCES usuarios(id)"
    )
    op.execute(
        f"CREATE INDEX IF NOT EXISTS ix_{table_name}_eliminado "
        f"ON {table_name}(eliminado)"
    )


def _drop_audit_columns(table_name: str) -> None:
    op.execute(f"DROP INDEX IF EXISTS ix_{table_name}_eliminado")
    for col in (
        'modificado_por_id', 'creado_por_id', 'eliminado',
        'fecha_eliminacion', 'fecha_modificacion', 'fecha_creacion',
    ):
        op.execute(f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {col}")


def upgrade() -> None:
    for t in AUDIT_TABLES:
        _add_audit_columns(t)


def downgrade() -> None:
    for t in reversed(AUDIT_TABLES):
        _drop_audit_columns(t)
