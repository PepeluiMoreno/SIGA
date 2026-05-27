"""Actividad: soporte de plataforma telemática.

Una reunión es una actividad. Toda actividad online puede tener una
plataforma del mismo catálogo que las reuniones + datos de conexión.

Idempotente. Una sentencia por op.execute (asyncpg).

Revision ID: f3d4e5f6a7b8
Revises: f2c3d4e5f6a7
Create Date: 2026-05-27 18:33:00.000000
"""
from alembic import op


revision = 'f3d4e5f6a7b8'
down_revision = 'f2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE actividades "
        "ADD COLUMN IF NOT EXISTS plataforma_telematica_id UUID "
        "REFERENCES sec_plataformas_telematicas(id) ON DELETE SET NULL"
    )
    op.execute(
        "ALTER TABLE actividades "
        "ADD COLUMN IF NOT EXISTS datos_conexion_telematica TEXT"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_actividades_plat_telem "
        "ON actividades(plataforma_telematica_id)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE actividades DROP COLUMN IF EXISTS datos_conexion_telematica")
    op.execute("ALTER TABLE actividades DROP COLUMN IF EXISTS plataforma_telematica_id")
