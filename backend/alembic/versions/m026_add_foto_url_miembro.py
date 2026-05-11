"""add foto_url to miembros

Revision ID: m026
Revises: m025
Create Date: 2026-05-10
"""
from alembic import op
import sqlalchemy as sa

revision = 'm026'
down_revision = 'm025'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('miembros', sa.Column('foto_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('miembros', 'foto_url')
