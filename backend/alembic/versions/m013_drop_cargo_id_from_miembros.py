"""drop cargo_id from miembros (ya no referencia tipos_cargo)

Revision ID: m013
Revises: m011
Create Date: 2026-05-06

"""
from typing import Sequence, Union
from alembic import op
from sqlalchemy import text

revision: str = 'm013'
down_revision: Union[str, None] = 'm011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(text(
        "SELECT 1 FROM information_schema.columns WHERE table_name='miembros' AND column_name='cargo_id'"
    ))
    if result.fetchone():
        op.drop_column('miembros', 'cargo_id')


def downgrade() -> None:
    pass
