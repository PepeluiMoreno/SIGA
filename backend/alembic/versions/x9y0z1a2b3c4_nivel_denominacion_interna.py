"""niveles_organizativos: denominación interna de la unidad (singular/plural).

Permite que la organización nombre su unidad en cada nivel/ámbito (p.ej. nivel
"Provincia" → "Agrupación Provincial" / "Agrupaciones Provinciales"). La UI usa
esta denominación como etiqueta dinámica de las unidades de ese nivel.

Revision ID: x9y0z1a2b3c4
Revises: w8x9y0z1a2b3
Create Date: 2026-06-26 00:00:00.000000
"""
from alembic import op

revision = 'x9y0z1a2b3c4'
down_revision = 'w8x9y0z1a2b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE niveles_organizativos ADD COLUMN IF NOT EXISTS denominacion_singular VARCHAR(100)")
    op.execute("ALTER TABLE niveles_organizativos ADD COLUMN IF NOT EXISTS denominacion_plural VARCHAR(100)")


def downgrade() -> None:
    op.execute("ALTER TABLE niveles_organizativos DROP COLUMN IF EXISTS denominacion_plural")
    op.execute("ALTER TABLE niveles_organizativos DROP COLUMN IF EXISTS denominacion_singular")
