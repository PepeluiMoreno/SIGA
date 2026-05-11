"""Add puede_planificar to tipos_miembro.

Permite filtrar qué tipos de miembro pueden actuar como responsable
de una actividad planificada (campaña, evento, etc.).

Revision ID: m021
Revises: m020
Create Date: 2026-05-09
"""

from alembic import op
import sqlalchemy as sa

revision = 'm021'
down_revision = 'm020'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'tipos_miembro',
        sa.Column('puede_planificar', sa.Boolean(), nullable=False, server_default='false'),
    )


def downgrade() -> None:
    op.drop_column('tipos_miembro', 'puede_planificar')
