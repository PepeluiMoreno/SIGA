"""Renombra skill_id → habilidad_id en miembros_habilidades.

La tabla se creó con el nombre de columna skill_id pero el modelo
SQLAlchemy espera habilidad_id. También corrige el nombre del índice
y del unique constraint.

Revision ID: m032
Revises: m031
Create Date: 2026-05-10
"""
from alembic import op

revision = 'm032'
down_revision = 'm031'
branch_labels = None
depends_on = None


def upgrade():
    # Renombrar columna
    op.alter_column('miembros_habilidades', 'skill_id', new_column_name='habilidad_id')
    # Renombrar índice
    op.execute('ALTER INDEX IF EXISTS "ix_miembros_habilidades_habilidad_id" RENAME TO "ix_miembros_habilidades_habilidad_id_old"')
    op.execute('DROP INDEX IF EXISTS "ix_miembros_habilidades_habilidad_id_old"')
    op.create_index('ix_miembros_habilidades_habilidad_id', 'miembros_habilidades', ['habilidad_id'])


def downgrade():
    op.drop_index('ix_miembros_habilidades_habilidad_id', table_name='miembros_habilidades')
    op.alter_column('miembros_habilidades', 'habilidad_id', new_column_name='skill_id')
    op.create_index('ix_miembros_habilidades_habilidad_id', 'miembros_habilidades', ['skill_id'])
