"""Añade columnas de auditoría a las nuevas tablas de campañas.

Revision ID: h3i4j5k6l7m8
Revises: g2h3i4j5k6l7
Create Date: 2026-05-16 13:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = 'h3i4j5k6l7m8'
down_revision: str = 'g2h3i4j5k6l7'
branch_labels = None
depends_on = None

AUDIT_TABLES = [
    'tipos_meta_campania',
    'tipos_canal_difusion',
    'metas_campania',
    'canales_difusion_campania',
    'partidas_presupuesto_campania',
    'plantillas_campania',
    'plantilla_metas',
    'plantilla_partidas',
    'plantilla_actividades',
    'plantilla_tareas',
]


def _add_audit_columns(table_name: str) -> None:
    op.add_column(table_name, sa.Column('fecha_creacion', sa.DateTime, server_default=sa.text('NOW()'), nullable=False))
    op.add_column(table_name, sa.Column('fecha_modificacion', sa.DateTime, nullable=True))
    op.add_column(table_name, sa.Column('fecha_eliminacion', sa.DateTime, nullable=True))
    op.add_column(table_name, sa.Column('eliminado', sa.Boolean, server_default='false', nullable=False))
    op.add_column(table_name, sa.Column('creado_por_id', UUID(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=True))
    op.add_column(table_name, sa.Column('modificado_por_id', UUID(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=True))
    op.create_index(f'ix_{table_name}_eliminado', table_name, ['eliminado'])


def _drop_audit_columns(table_name: str) -> None:
    op.drop_index(f'ix_{table_name}_eliminado', table_name)
    for col in ('modificado_por_id', 'creado_por_id', 'eliminado', 'fecha_eliminacion', 'fecha_modificacion', 'fecha_creacion'):
        op.drop_column(table_name, col)


def upgrade() -> None:
    for t in AUDIT_TABLES:
        _add_audit_columns(t)


def downgrade() -> None:
    for t in reversed(AUDIT_TABLES):
        _drop_audit_columns(t)
