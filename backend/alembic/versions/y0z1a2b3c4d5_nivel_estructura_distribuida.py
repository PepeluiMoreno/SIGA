"""niveles_organizativos: modelo de estructura centralizada/distribuida.

Bandera recursiva por nivel que decide cómo se define el subárbol que cuelga de
él: False = CENTRALIZADA (la matriz define aquí toda la subestructura),
True = DISTRIBUIDA (cada unidad de ese nivel define su propia subestructura).

Revision ID: y0z1a2b3c4d5
Revises: x9y0z1a2b3c4
Create Date: 2026-06-26 00:00:00.000000
"""
from alembic import op

revision = 'y0z1a2b3c4d5'
down_revision = 'x9y0z1a2b3c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE niveles_organizativos "
        "ADD COLUMN IF NOT EXISTS estructura_distribuida BOOLEAN NOT NULL DEFAULT false"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE niveles_organizativos DROP COLUMN IF EXISTS estructura_distribuida")
