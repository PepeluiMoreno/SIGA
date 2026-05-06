"""fix activo columns from Integer to Boolean

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-05-06 13:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e2f3a4b5c6d7'
down_revision: Union[str, None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL: cast Integer to Boolean (0=false, non-zero=true)
    op.execute("ALTER TABLE paises ALTER COLUMN activo TYPE boolean USING activo::boolean")
    op.execute("ALTER TABLE provincias ALTER COLUMN activo TYPE boolean USING activo::boolean")
    op.execute("ALTER TABLE municipios ALTER COLUMN activo TYPE boolean USING activo::boolean")
    op.execute("ALTER TABLE importes_cuota_anio ALTER COLUMN activo TYPE boolean USING activo::boolean")
    op.execute("ALTER TABLE agrupaciones_territoriales ALTER COLUMN activo TYPE boolean USING activo::boolean")


def downgrade() -> None:
    op.execute("ALTER TABLE agrupaciones_territoriales ALTER COLUMN activo TYPE integer USING activo::integer")
    op.execute("ALTER TABLE importes_cuota_anio ALTER COLUMN activo TYPE integer USING activo::integer")
    op.execute("ALTER TABLE municipios ALTER COLUMN activo TYPE integer USING activo::integer")
    op.execute("ALTER TABLE provincias ALTER COLUMN activo TYPE integer USING activo::integer")
    op.execute("ALTER TABLE paises ALTER COLUMN activo TYPE integer USING activo::integer")
