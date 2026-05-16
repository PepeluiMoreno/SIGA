"""Añade campo notificacion_enviada a campanias (flag one-shot).

Revision ID: a7f3c9d8b2e4
Revises: f1a2b3c4d5e6
Create Date: 2026-05-15 18:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'a7f3c9d8b2e4'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'campanias',
        sa.Column('notificacion_enviada', sa.Boolean, nullable=False, server_default='false'),
    )


def downgrade() -> None:
    op.drop_column('campanias', 'notificacion_enviada')
