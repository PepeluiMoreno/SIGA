"""Corrige columnas de auditoría en niveles_estudios y niveles_habilidad.

La migración m029 creó created_at/updated_at en lugar de las columnas
estándar del BaseModel (fecha_creacion, fecha_modificacion, eliminado, etc.).

Revision ID: m030
Revises: m029
Create Date: 2026-05-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'm030'
down_revision = 'm029'
branch_labels = None
depends_on = None

TABLES = ['niveles_estudios', 'niveles_habilidad']


def upgrade():
    for tabla in TABLES:
        # Renombrar created_at → fecha_creacion
        op.alter_column(tabla, 'created_at', new_column_name='fecha_creacion')
        # Renombrar updated_at → fecha_modificacion
        op.alter_column(tabla, 'updated_at', new_column_name='fecha_modificacion')
        # Hacer fecha_modificacion nullable (BaseModel la tiene nullable)
        op.alter_column(tabla, 'fecha_modificacion', nullable=True,
                        server_default=None)
        # Añadir columnas faltantes
        op.add_column(tabla, sa.Column(
            'fecha_eliminacion', sa.DateTime(), nullable=True
        ))
        op.add_column(tabla, sa.Column(
            'eliminado', sa.Boolean(), nullable=False,
            server_default='false',
        ))
        op.create_index(f'ix_{tabla}_eliminado', tabla, ['eliminado'])
        op.add_column(tabla, sa.Column(
            'creado_por_id', UUID(as_uuid=True),
            sa.ForeignKey('usuarios.id', ondelete='SET NULL'),
            nullable=True,
        ))
        op.add_column(tabla, sa.Column(
            'modificado_por_id', UUID(as_uuid=True),
            sa.ForeignKey('usuarios.id', ondelete='SET NULL'),
            nullable=True,
        ))


def downgrade():
    for tabla in TABLES:
        op.drop_column(tabla, 'modificado_por_id')
        op.drop_column(tabla, 'creado_por_id')
        op.drop_index(f'ix_{tabla}_eliminado', table_name=tabla)
        op.drop_column(tabla, 'eliminado')
        op.drop_column(tabla, 'fecha_eliminacion')
        op.alter_column(tabla, 'fecha_modificacion', new_column_name='updated_at',
                        nullable=False, server_default=sa.text('now()'))
        op.alter_column(tabla, 'fecha_creacion', new_column_name='created_at')
