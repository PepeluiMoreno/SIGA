"""add es_socio_honor to miembros

Revision ID: d1e2f3a4b5c6
Revises: c78cdbdbfc93
Create Date: 2026-05-06 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, None] = 'c78cdbdbfc93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('miembros', sa.Column('es_socio_honor', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    op.drop_column('miembros', 'es_socio_honor')
