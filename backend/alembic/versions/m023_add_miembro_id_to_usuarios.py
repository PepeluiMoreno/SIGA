"""Add miembro_id to usuarios + revert puede_planificar from miembros.

Establece la relación 1:1 entre Usuario y Miembro.
Un usuario técnico (admin) puede no tener miembro asociado.
Un miembro puede no tener cuenta de usuario.

Revision ID: m023
Revises: m022
Create Date: 2026-05-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'm023'
down_revision = 'm022'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Revertir puede_planificar (movido a rol del sistema de acceso)
    op.drop_column('miembros', 'puede_planificar')

    # FK 1:1 Usuario → Miembro
    op.add_column(
        'usuarios',
        sa.Column('miembro_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_unique_constraint('uq_usuarios_miembro_id', 'usuarios', ['miembro_id'])
    op.create_index('ix_usuarios_miembro_id', 'usuarios', ['miembro_id'])
    op.create_foreign_key(
        'fk_usuarios_miembro_id', 'usuarios', 'miembros',
        ['miembro_id'], ['id'], ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_usuarios_miembro_id', 'usuarios', type_='foreignkey')
    op.drop_index('ix_usuarios_miembro_id', table_name='usuarios')
    op.drop_constraint('uq_usuarios_miembro_id', 'usuarios', type_='unique')
    op.drop_column('usuarios', 'miembro_id')

    op.add_column(
        'miembros',
        sa.Column('puede_planificar', sa.Boolean(), nullable=False, server_default='false'),
    )
