"""add activo column to usuarios_roles

Revision ID: m002
Revises: m001
Create Date: 2026-05-05

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'm002'
down_revision: Union[str, Sequence[str], None] = 'm001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('usuarios_roles',
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true')
    )
    op.create_index('ix_usuarios_roles_activo', 'usuarios_roles', ['activo'])


def downgrade() -> None:
    op.drop_index('ix_usuarios_roles_activo', table_name='usuarios_roles')
    op.drop_column('usuarios_roles', 'activo')
