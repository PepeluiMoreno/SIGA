"""Renombra tabla skills → habilidades y miembros_skills → miembros_habilidades

Revision ID: m016
Revises: m015
Create Date: 2026-05-08
"""
from alembic import op

revision: str = 'm016'
down_revision = 'm015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('skills', 'habilidades')
    op.rename_table('miembros_skills', 'miembros_habilidades')
    op.execute("ALTER TABLE miembros_habilidades RENAME CONSTRAINT uq_miembro_skill TO uq_miembro_habilidad")
    op.execute("ALTER INDEX ix_skills_nombre RENAME TO ix_habilidades_nombre")
    op.execute("ALTER INDEX ix_skills_categoria RENAME TO ix_habilidades_categoria")
    op.execute("ALTER INDEX ix_skills_activo RENAME TO ix_habilidades_activo")
    op.execute("ALTER INDEX ix_skills_eliminado RENAME TO ix_habilidades_eliminado")
    op.execute("ALTER INDEX ix_miembros_skills_miembro_id RENAME TO ix_miembros_habilidades_miembro_id")
    op.execute("ALTER INDEX ix_miembros_skills_skill_id RENAME TO ix_miembros_habilidades_habilidad_id")
    op.execute("ALTER INDEX ix_miembros_skills_eliminado RENAME TO ix_miembros_habilidades_eliminado")


def downgrade() -> None:
    op.execute("ALTER INDEX ix_miembros_habilidades_eliminado RENAME TO ix_miembros_skills_eliminado")
    op.execute("ALTER INDEX ix_miembros_habilidades_habilidad_id RENAME TO ix_miembros_skills_skill_id")
    op.execute("ALTER INDEX ix_miembros_habilidades_miembro_id RENAME TO ix_miembros_skills_miembro_id")
    op.execute("ALTER INDEX ix_habilidades_eliminado RENAME TO ix_skills_eliminado")
    op.execute("ALTER INDEX ix_habilidades_activo RENAME TO ix_skills_activo")
    op.execute("ALTER INDEX ix_habilidades_categoria RENAME TO ix_skills_categoria")
    op.execute("ALTER INDEX ix_habilidades_nombre RENAME TO ix_skills_nombre")
    op.execute("ALTER TABLE miembros_habilidades RENAME CONSTRAINT uq_miembro_habilidad TO uq_miembro_skill")
    op.rename_table('miembros_habilidades', 'miembros_skills')
    op.rename_table('habilidades', 'skills')
