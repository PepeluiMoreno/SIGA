"""add coordinador_id to grupos_trabajo

Revision ID: c1d2e3f4g5h6
Revises: b3c4d5e6f7a8
Create Date: 2026-05-02
"""
from alembic import op
import sqlalchemy as sa

revision = 'c1d2e3f4g5h6'
down_revision = 'b3c4d5e6f7a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'grupos_trabajo',
        sa.Column('coordinador_id', sa.Uuid(), nullable=True)
    )
    op.create_index(
        'ix_grupos_trabajo_coordinador_id',
        'grupos_trabajo',
        ['coordinador_id']
    )
    op.create_foreign_key(
        'fk_grupos_trabajo_coordinador_id',
        'grupos_trabajo',
        'miembros',
        ['coordinador_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_grupos_trabajo_coordinador_id', 'grupos_trabajo', type_='foreignkey')
    op.drop_index('ix_grupos_trabajo_coordinador_id', table_name='grupos_trabajo')
    op.drop_column('grupos_trabajo', 'coordinador_id')
