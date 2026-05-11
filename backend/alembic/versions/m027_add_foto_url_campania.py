"""add foto_url to campanias

Revision ID: m027
Revises: m026
Create Date: 2026-05-10
"""
from alembic import op
import sqlalchemy as sa

revision = 'm027'
down_revision = 'm026'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('campanias', sa.Column('foto_url', sa.String(500), nullable=True))


def downgrade():
    op.drop_column('campanias', 'foto_url')
