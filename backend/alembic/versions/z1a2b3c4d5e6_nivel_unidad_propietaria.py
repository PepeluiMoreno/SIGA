"""niveles_organizativos: unidad propietaria (estructura distribuida).

Cuando la estructura es distribuida, los sub-niveles que define cada agrupación
le pertenecen (unidad_id). Los niveles de plantilla global (la matriz) tienen
unidad_id NULL. ON DELETE CASCADE: al borrar una unidad se borran sus sub-niveles.

Revision ID: z1a2b3c4d5e6
Revises: y0z1a2b3c4d5
Create Date: 2026-06-26 00:00:00.000000
"""
from alembic import op

revision = 'z1a2b3c4d5e6'
down_revision = 'y0z1a2b3c4d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE niveles_organizativos "
        "ADD COLUMN IF NOT EXISTS unidad_id UUID REFERENCES unidades_organizativas(id) ON DELETE CASCADE"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_niveles_organizativos_unidad_id "
        "ON niveles_organizativos (unidad_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_niveles_organizativos_unidad_id")
    op.execute("ALTER TABLE niveles_organizativos DROP COLUMN IF EXISTS unidad_id")
