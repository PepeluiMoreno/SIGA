"""Crea tabla categorias_habilidad y migra columna categoria de habilidades a FK

Revision ID: m028
Revises: m027
Create Date: 2026-05-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'm028'
down_revision = 'm027'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'categorias_habilidad',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('nombre', sa.String(100), nullable=False, unique=True),
        sa.Column('descripcion', sa.String(300), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
    )

    # Añadir columna categoria_id (nullable, FK) a habilidades
    op.add_column('habilidades', sa.Column(
        'categoria_id', UUID(as_uuid=True),
        sa.ForeignKey('categorias_habilidad.id', ondelete='SET NULL'),
        nullable=True,
    ))
    op.create_index('ix_habilidades_categoria_id', 'habilidades', ['categoria_id'])

    # Eliminar la antigua columna categoria (texto libre)
    op.drop_index('ix_habilidades_categoria', table_name='habilidades')
    op.drop_column('habilidades', 'categoria')


def downgrade():
    op.add_column('habilidades', sa.Column('categoria', sa.String(100), nullable=True))
    op.create_index('ix_habilidades_categoria', 'habilidades', ['categoria'])
    op.drop_index('ix_habilidades_categoria_id', table_name='habilidades')
    op.drop_column('habilidades', 'categoria_id')
    op.drop_table('categorias_habilidad')
