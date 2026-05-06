"""drop tablas obsoletas si existen: cargos_junta, historial_cargos_junta, tipos_cargo_roles

Los roles de tipo ORGANIZACION son ahora los cargos.

Revision ID: m011
Revises: m009
Create Date: 2026-05-06 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = 'm011'
down_revision: Union[str, None] = 'm009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    for table in ('cargos_junta', 'historial_cargos_junta', 'tipos_cargo_roles'):
        result = conn.execute(text(
            f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='{table}')"
        ))
        if result.scalar():
            op.drop_table(table)


def downgrade() -> None:
    pass
