"""Corrige columnas de auditoría en categorias_habilidad.

m028 creó created_at/updated_at en lugar de las columnas BaseModel.

Revision ID: m031
Revises: m030
Create Date: 2026-05-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'm031'
down_revision = 'm030'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('categorias_habilidad', 'created_at', new_column_name='fecha_creacion')
    op.alter_column('categorias_habilidad', 'updated_at', new_column_name='fecha_modificacion',
                    nullable=True, server_default=None)
    op.add_column('categorias_habilidad', sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True))
    op.create_index('ix_categorias_habilidad_eliminado', 'categorias_habilidad', ['eliminado'])
    op.add_column('categorias_habilidad', sa.Column(
        'creado_por_id', UUID(as_uuid=True),
        sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True,
    ))
    op.add_column('categorias_habilidad', sa.Column(
        'modificado_por_id', UUID(as_uuid=True),
        sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True,
    ))


def downgrade():
    op.drop_column('categorias_habilidad', 'modificado_por_id')
    op.drop_column('categorias_habilidad', 'creado_por_id')
    op.drop_index('ix_categorias_habilidad_eliminado', table_name='categorias_habilidad')
    op.drop_column('categorias_habilidad', 'fecha_eliminacion')
    op.alter_column('categorias_habilidad', 'fecha_modificacion', new_column_name='updated_at',
                    nullable=False, server_default=sa.text('now()'))
    op.alter_column('categorias_habilidad', 'fecha_creacion', new_column_name='created_at')
