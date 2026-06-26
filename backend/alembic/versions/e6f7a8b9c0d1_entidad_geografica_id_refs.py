"""Referencias a la geografía unificada: entidad_geografica_id en Contacto y UnidadOrganizativa.

Transitorio: convive con las FKs viejas (provincia_id / municipio_id) mientras se
migran los consumidores. La nueva FK apunta a `entidades_geograficas` (jerarquía
única recursiva). El backfill se hace por script (seed_geografia_refs).

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-06-26 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'e6f7a8b9c0d1'
down_revision = 'd5e6f7a8b9c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE contactos ADD COLUMN IF NOT EXISTS entidad_geografica_id UUID "
        "REFERENCES entidades_geograficas(id) ON DELETE SET NULL"
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_contactos_entidad_geografica_id ON contactos (entidad_geografica_id)")
    op.execute(
        "ALTER TABLE unidades_organizativas ADD COLUMN IF NOT EXISTS entidad_geografica_id UUID "
        "REFERENCES entidades_geograficas(id) ON DELETE SET NULL"
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_unidades_org_entidad_geografica_id ON unidades_organizativas (entidad_geografica_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_unidades_org_entidad_geografica_id")
    op.execute("ALTER TABLE unidades_organizativas DROP COLUMN IF EXISTS entidad_geografica_id")
    op.execute("DROP INDEX IF EXISTS ix_contactos_entidad_geografica_id")
    op.execute("ALTER TABLE contactos DROP COLUMN IF EXISTS entidad_geografica_id")
