"""Move puede_planificar from tipos_miembro to miembros.

El flag es individual (caso a caso) no categórico por tipo.

Revision ID: m022
Revises: m021
Create Date: 2026-05-09
"""

from alembic import op
import sqlalchemy as sa

revision = 'm022'
down_revision = 'm021'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('tipos_miembro', 'puede_planificar')
    op.add_column(
        'miembros',
        sa.Column('puede_planificar', sa.Boolean(), nullable=False, server_default='false'),
    )


def downgrade() -> None:
    op.drop_column('miembros', 'puede_planificar')
    op.add_column(
        'tipos_miembro',
        sa.Column('puede_planificar', sa.Boolean(), nullable=False, server_default='false'),
    )
