"""Añade tabla temas_ui para catálogo de temas de interfaz de usuario

Revision ID: m019
Revises: m018
Create Date: 2026-05-09
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'm019'
down_revision: Union[str, None] = 'm018'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # La tabla ya fue creada y poblada directamente en la BD.
    pass


def downgrade() -> None:
    op.drop_table('temas_ui')
