"""Permite registrar miembros sin tipo_miembro_id ni estado_id (alta mínima).

Revision ID: m025
Revises: m024
Create Date: 2026-05-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'm025'
down_revision = 'm024'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('miembros', 'tipo_miembro_id',
                    existing_type=postgresql.UUID(as_uuid=True),
                    nullable=True)
    op.alter_column('miembros', 'estado_id',
                    existing_type=postgresql.UUID(as_uuid=True),
                    nullable=True)


def downgrade() -> None:
    # Antes de revertir, asegurarse de que no existan NULLs
    op.alter_column('miembros', 'estado_id',
                    existing_type=postgresql.UUID(as_uuid=True),
                    nullable=False)
    op.alter_column('miembros', 'tipo_miembro_id',
                    existing_type=postgresql.UUID(as_uuid=True),
                    nullable=False)
