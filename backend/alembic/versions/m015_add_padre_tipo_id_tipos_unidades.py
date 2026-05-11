"""Añade padre_tipo_id a tipos_unidades_organizativas (árbol de tipos)

Revision ID: m015
Revises: m014
Create Date: 2026-05-07
"""
from alembic import op
import sqlalchemy as sa

revision: str = 'm015'
down_revision: str = 'm014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'tipos_unidades_organizativas',
        sa.Column('padre_tipo_id', sa.Uuid(), nullable=True),
    )
    op.create_index(
        'ix_tipos_unidades_org_padre',
        'tipos_unidades_organizativas',
        ['padre_tipo_id'],
    )
    op.create_foreign_key(
        None,
        'tipos_unidades_organizativas',
        'tipos_unidades_organizativas',
        ['padre_tipo_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_index('ix_tipos_unidades_org_padre', table_name='tipos_unidades_organizativas')
    op.drop_column('tipos_unidades_organizativas', 'padre_tipo_id')
