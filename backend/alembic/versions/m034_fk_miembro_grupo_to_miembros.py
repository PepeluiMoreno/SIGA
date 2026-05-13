"""add FK miembros_grupo.miembro_id -> miembros.id

Revision ID: m034
Revises: m033
Create Date: 2026-05-11

"""
from alembic import op

revision = 'm034'
down_revision = 'm033'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        'fk_miembros_grupo_miembro_id',
        'miembros_grupo', 'miembros',
        ['miembro_id'], ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint('fk_miembros_grupo_miembro_id', 'miembros_grupo', type_='foreignkey')
