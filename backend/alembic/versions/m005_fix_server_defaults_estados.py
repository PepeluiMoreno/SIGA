"""fix server defaults for missing estados tables

Revision ID: m005
Revises: m004
Create Date: 2026-05-06

"""
from typing import Sequence, Union
from alembic import op


revision: str = 'm005'
down_revision: Union[str, Sequence[str], None] = 'm004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


MISSING_TABLES = [
    'estados_participante',
    'estados_orden_cobro',
    'estados_remesa',
    'estados_donacion',
    'estados_notificacion',
]


def upgrade() -> None:
    for table in MISSING_TABLES:
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = '{table}' AND column_name = 'fecha_creacion'
                ) THEN
                    ALTER TABLE {table} ALTER COLUMN fecha_creacion SET DEFAULT NOW();
                    ALTER TABLE {table} ALTER COLUMN eliminado SET DEFAULT FALSE;
                END IF;
            END $$;
        """)


def downgrade() -> None:
    for table in MISSING_TABLES:
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = '{table}' AND column_name = 'fecha_creacion'
                ) THEN
                    ALTER TABLE {table} ALTER COLUMN fecha_creacion DROP DEFAULT;
                END IF;
            END $$;
        """)
