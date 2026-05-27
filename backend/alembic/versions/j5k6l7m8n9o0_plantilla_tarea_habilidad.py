"""Añade habilidad_id y nivel_habilidad_id a plantilla_tareas.

Idempotente con ADD COLUMN IF NOT EXISTS.

Revision ID: j5k6l7m8n9o0
Revises: i4j5k6l7m8n9
Create Date: 2026-05-16 12:00:00.000000
"""

from alembic import op

revision: str = 'j5k6l7m8n9o0'
down_revision: str = 'i4j5k6l7m8n9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE plantilla_tareas "
        "ADD COLUMN IF NOT EXISTS habilidad_id UUID "
        "REFERENCES habilidades(id) ON DELETE SET NULL"
    )
    op.execute(
        "ALTER TABLE plantilla_tareas "
        "ADD COLUMN IF NOT EXISTS nivel_habilidad_id UUID "
        "REFERENCES niveles_habilidad(id) ON DELETE SET NULL"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_plantilla_tareas_habilidad_id "
        "ON plantilla_tareas(habilidad_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_plantilla_tareas_nivel_habilidad_id "
        "ON plantilla_tareas(nivel_habilidad_id)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE plantilla_tareas DROP COLUMN IF EXISTS nivel_habilidad_id")
    op.execute("ALTER TABLE plantilla_tareas DROP COLUMN IF EXISTS habilidad_id")
