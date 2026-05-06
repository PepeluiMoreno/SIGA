"""Add password reset token fields to usuarios

Revision ID: m008
Revises: m007
Create Date: 2026-05-06
"""
from alembic import op
import sqlalchemy as sa

revision = 'm008'
down_revision = 'm007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('usuarios', sa.Column('reset_token', sa.String(128), nullable=True))
    op.add_column('usuarios', sa.Column('reset_token_expira_en', sa.DateTime(), nullable=True))
    op.add_column('usuarios', sa.Column('reset_token_solicitado_en', sa.DateTime(), nullable=True))
    op.create_index('ix_usuarios_reset_token', 'usuarios', ['reset_token'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_usuarios_reset_token', table_name='usuarios')
    op.drop_column('usuarios', 'reset_token_solicitado_en')
    op.drop_column('usuarios', 'reset_token_expira_en')
    op.drop_column('usuarios', 'reset_token')
