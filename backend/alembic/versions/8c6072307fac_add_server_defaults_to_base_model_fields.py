"""add_server_defaults_to_base_model_fields

Revision ID: 8c6072307fac
Revises: 5c2912c2f427
Create Date: 2026-01-19 19:48:03.065863
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '8c6072307fac'
down_revision: Union[str, None] = '5c2912c2f427'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add server defaults for fecha_creacion and eliminado in ALL existing tables
    # These defaults are part of BaseModel's AuditoriaMixin

    # Only include tables that actually exist at this point in migration history
    tables = [
        # Core domain
        'estados_cuota', 'estados_campania', 'estados_tarea', 'estados_actividad',

        # Geographic domain
        'paises', 'provincias',

        # Miembros domain
        'tipos_miembro', 'estados_miembro',

        # Campanas domain
        'tipos_campania', 'roles_participante',

        # Auth domain (if they exist)
        'usuarios', 'roles', 'permisos'
    ]

    # Add defaults one table at a time
    op.execute("""
        DO $$
        DECLARE
            t text;
        BEGIN
            FOREACH t IN ARRAY ARRAY[
                'estados_cuota', 'estados_campania', 'estados_tarea', 'estados_actividad',
                'paises', 'provincias',
                'tipos_miembro', 'estados_miembro',
                'tipos_campania', 'roles_participante',
                'usuarios', 'roles', 'permisos'
            ]
            LOOP
                -- Check if table exists
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = t) THEN
                    -- Check if fecha_creacion column exists
                    IF EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name = t AND column_name = 'fecha_creacion') THEN
                        EXECUTE format('ALTER TABLE %I ALTER COLUMN fecha_creacion SET DEFAULT NOW()', t);
                    END IF;

                    -- Check if eliminado column exists
                    IF EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name = t AND column_name = 'eliminado') THEN
                        EXECUTE format('ALTER TABLE %I ALTER COLUMN eliminado SET DEFAULT FALSE', t);
                    END IF;
                END IF;
            END LOOP;
        END $$;
    """)


def downgrade() -> None:
    # Remove server defaults
    op.execute("""
        DO $$
        DECLARE
            t text;
        BEGIN
            FOREACH t IN ARRAY ARRAY[
                'estados_cuota', 'estados_campania', 'estados_tarea', 'estados_actividad',
                'paises', 'provincias',
                'tipos_miembro', 'estados_miembro',
                'tipos_campania', 'roles_participante',
                'usuarios', 'roles', 'permisos'
            ]
            LOOP
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = t) THEN
                    IF EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name = t AND column_name = 'fecha_creacion') THEN
                        EXECUTE format('ALTER TABLE %I ALTER COLUMN fecha_creacion DROP DEFAULT', t);
                    END IF;

                    IF EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name = t AND column_name = 'eliminado') THEN
                        EXECUTE format('ALTER TABLE %I ALTER COLUMN eliminado DROP DEFAULT', t);
                    END IF;
                END IF;
            END LOOP;
        END $$;
    """)
