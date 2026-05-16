"""Añade habilidad_id y nivel_habilidad_id a plantilla_tareas.

Revision ID: j5k6l7m8n9o0
Revises: i4j5k6l7m8n9
Create Date: 2026-05-16 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision: str = 'j5k6l7m8n9o0'
down_revision: str = 'i4j5k6l7m8n9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('plantilla_tareas',
        sa.Column('habilidad_id', sa.Uuid(), sa.ForeignKey('habilidades.id', ondelete='SET NULL'), nullable=True, index=True)
    )
    op.add_column('plantilla_tareas',
        sa.Column('nivel_habilidad_id', sa.Uuid(), sa.ForeignKey('niveles_habilidad.id', ondelete='SET NULL'), nullable=True, index=True)
    )


def downgrade() -> None:
    op.drop_column('plantilla_tareas', 'nivel_habilidad_id')
    op.drop_column('plantilla_tareas', 'habilidad_id')
