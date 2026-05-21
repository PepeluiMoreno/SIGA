"""Merge de los tres heads del árbol de migraciones.

Revision ID: d0e1f2a3b4c5
Revises: m8n9o0p1q2r3, a7f3c9d8b2e4, c1a2b3d4e5f6
Create Date: 2026-05-21 10:45:00.000000

Merge sin cambios de esquema. Reconcilia las tres ramas que quedaron abiertas:
  - m8n9o0p1q2r3  (taxonomía de actividades de gobierno)
  - a7f3c9d8b2e4  (campaña: notificación enviada)
  - c1a2b3d4e5f6  (comunicación: estados y vista de nombramientos vigentes)
Tras esta revisión el árbol vuelve a tener un único head.
"""
from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

revision = 'd0e1f2a3b4c5'
down_revision = ('m8n9o0p1q2r3', 'a7f3c9d8b2e4', 'c1a2b3d4e5f6')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
