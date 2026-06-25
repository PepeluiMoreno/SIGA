"""usuarios: añade `username` (único) y hace `email` opcional.

Habilita el login por email O por username y la cuenta de sistema `superadmin`
(username fijo, sin email). Idempotente y segura sobre BD migrada en sitio.

Revision ID: w8x9y0z1a2b3
Revises: v7w8x9y0z1a2
Create Date: 2026-06-25 00:00:00.000000
"""
from alembic import op

revision = 'w8x9y0z1a2b3'
down_revision = 'v7w8x9y0z1a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # `username`: identidad alternativa al email (cuenta de sistema `superadmin`).
    op.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS username VARCHAR(150)")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_usuarios_username ON usuarios (username)"
    )
    # `email` pasa a opcional (el superadmin no tiene email). El índice único de
    # email se conserva: en Postgres varios NULL no colisionan.
    op.execute("ALTER TABLE usuarios ALTER COLUMN email DROP NOT NULL")


def downgrade() -> None:
    # Best-effort: si hay filas con email NULL (p. ej. superadmin) este SET NOT
    # NULL fallaría; límpialas antes de revertir.
    op.execute("ALTER TABLE usuarios ALTER COLUMN email SET NOT NULL")
    op.execute("DROP INDEX IF EXISTS ix_usuarios_username")
    op.execute("ALTER TABLE usuarios DROP COLUMN IF EXISTS username")
