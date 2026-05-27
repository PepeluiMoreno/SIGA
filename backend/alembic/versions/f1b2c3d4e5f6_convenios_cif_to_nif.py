"""Convenios institucionales: rename cif_contraparte → nif_contraparte.

En España las personas jurídicas usan NIF (Ley 58/2003); el CIF se derogó.

Idempotente: detecta la columna existente y solo renombra si procede.

Revision ID: f1b2c3d4e5f6
Revises: f0a1b2c3d4e5
Create Date: 2026-05-27 18:31:00.000000
"""
from alembic import op


revision = 'f1b2c3d4e5f6'
down_revision = 'f0a1b2c3d4e5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'sec_convenios' AND column_name = 'cif_contraparte'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'sec_convenios' AND column_name = 'nif_contraparte'
            ) THEN
                ALTER TABLE sec_convenios RENAME COLUMN cif_contraparte TO nif_contraparte;
            END IF;
        END$$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'sec_convenios' AND column_name = 'nif_contraparte'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'sec_convenios' AND column_name = 'cif_contraparte'
            ) THEN
                ALTER TABLE sec_convenios RENAME COLUMN nif_contraparte TO cif_contraparte;
            END IF;
        END$$;
    """)
