"""Presupuestos Fase 3: prórroga presupuestaria.

Revision ID: r3s4t5u6v7w8
Revises: q2r3s4t5u6v7
Create Date: 2026-05-22 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'r3s4t5u6v7w8'
down_revision = 'q2r3s4t5u6v7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('planificaciones_anuales', sa.Column(
        'es_prorroga', sa.Boolean(), nullable=False, server_default='false'
    ))
    op.add_column('planificaciones_anuales', sa.Column(
        'ejercicio_origen_prorroga', sa.Integer(), nullable=True
    ))


def downgrade() -> None:
    op.drop_column('planificaciones_anuales', 'ejercicio_origen_prorroga')
    op.drop_column('planificaciones_anuales', 'es_prorroga')
