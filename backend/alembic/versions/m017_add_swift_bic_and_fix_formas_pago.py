"""Añade swift_bic a miembros y corrige/completa formas_pago

Revision ID: m017
Revises: m016
Create Date: 2026-05-08
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'm017'
down_revision: Union[str, None] = 'm016'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Añadir swift_bic a miembros
    op.add_column('miembros', sa.Column('swift_bic', sa.String(11), nullable=True))

    # 2. Corregir códigos y añadir formas de pago faltantes (hecho directamente en DB)


def downgrade() -> None:
    op.drop_column('miembros', 'swift_bic')
