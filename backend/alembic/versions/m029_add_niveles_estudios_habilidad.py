"""Añade tablas niveles_estudios y niveles_habilidad; migra campos de texto a FK.

Revision ID: m029
Revises: m028
Create Date: 2026-05-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'm029'
down_revision = 'm028'
branch_labels = None
depends_on = None


def upgrade():
    # ── Tabla niveles_estudios ───────────────────────────────────────────────
    op.create_table(
        'niveles_estudios',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.String(500), nullable=True),
        sa.Column('orden', sa.Integer, nullable=False, server_default='0'),
        sa.Column('activo', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_niveles_estudios_activo', 'niveles_estudios', ['activo'])

    # ── Tabla niveles_habilidad ──────────────────────────────────────────────
    op.create_table(
        'niveles_habilidad',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.String(500), nullable=True),
        sa.Column('orden', sa.Integer, nullable=False, server_default='0'),
        sa.Column('activo', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_niveles_habilidad_activo', 'niveles_habilidad', ['activo'])

    # ── miembros: reemplaza nivel_estudios (str) por nivel_estudios_id (FK) ──
    op.drop_index('ix_miembros_nivel_estudios', table_name='miembros', if_exists=True)
    op.drop_column('miembros', 'nivel_estudios')
    op.add_column('miembros', sa.Column(
        'nivel_estudios_id', UUID(as_uuid=True),
        sa.ForeignKey('niveles_estudios.id', ondelete='SET NULL'),
        nullable=True,
    ))
    op.create_index('ix_miembros_nivel_estudios_id', 'miembros', ['nivel_estudios_id'])

    # ── miembros_habilidades: reemplaza nivel (str) por nivel_id (FK) ────────
    op.drop_column('miembros_habilidades', 'nivel')
    op.add_column('miembros_habilidades', sa.Column(
        'nivel_id', UUID(as_uuid=True),
        sa.ForeignKey('niveles_habilidad.id', ondelete='SET NULL'),
        nullable=True,
    ))
    op.create_index('ix_miembros_habilidades_nivel_id', 'miembros_habilidades', ['nivel_id'])


def downgrade():
    op.drop_index('ix_miembros_habilidades_nivel_id', table_name='miembros_habilidades')
    op.drop_column('miembros_habilidades', 'nivel_id')
    op.add_column('miembros_habilidades', sa.Column('nivel', sa.String(20), nullable=True))

    op.drop_index('ix_miembros_nivel_estudios_id', table_name='miembros')
    op.drop_column('miembros', 'nivel_estudios_id')
    op.add_column('miembros', sa.Column('nivel_estudios', sa.String(255), nullable=True))

    op.drop_index('ix_niveles_habilidad_activo', table_name='niveles_habilidad')
    op.drop_table('niveles_habilidad')
    op.drop_index('ix_niveles_estudios_activo', table_name='niveles_estudios')
    op.drop_table('niveles_estudios')
