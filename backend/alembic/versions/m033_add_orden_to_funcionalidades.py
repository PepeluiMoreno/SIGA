"""add orden to funcionalidades

Revision ID: m033
Revises: m032
Create Date: 2026-05-11

"""
from alembic import op
import sqlalchemy as sa

revision = 'm033'
down_revision = 'm032'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'funcionalidades',
        sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_column('funcionalidades', 'orden')
