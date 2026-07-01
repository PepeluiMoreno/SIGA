"""Publicación web (satélite 1:1 de Actividad): contenido de la página pública
de una recogida de firmas (título/lema/descripción/imagen con fallback a la
campaña + manifiesto, destinatario, aviso RGPD, PDF y texto para compartir).

Aditiva.

Revision ID: pubweb1act2land3
Revises: tag1etiq2civi3
"""
from alembic import op
import sqlalchemy as sa


revision = "pubweb1act2land3"
down_revision = "tag1etiq2civi3"
branch_labels = None
depends_on = None


def _audit_cols():
    return [
        sa.Column("fecha_creacion", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("fecha_modificacion", sa.DateTime(), nullable=True),
        sa.Column("fecha_eliminacion", sa.DateTime(), nullable=True),
        sa.Column("eliminado", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("creado_por_id", sa.Uuid(), nullable=True),
        sa.Column("modificado_por_id", sa.Uuid(), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "publicaciones_web",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("actividad_id", sa.Uuid(), nullable=False),
        # Overrides con fallback a la campaña.
        sa.Column("titulo", sa.String(length=300), nullable=True),
        sa.Column("lema", sa.String(length=300), nullable=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("imagen_url", sa.String(length=500), nullable=True),
        # Propios de la página pública.
        sa.Column("destinatario", sa.String(length=300), nullable=True),
        sa.Column("manifiesto", sa.Text(), nullable=True),
        sa.Column("aviso_rgpd", sa.Text(), nullable=True),
        sa.Column("hoja_firmas_url", sa.String(length=500), nullable=True),
        sa.Column("comparte_texto", sa.String(length=300), nullable=True),
        sa.Column("publicar", sa.Boolean(), server_default="false", nullable=False),
        *_audit_cols(),
        sa.ForeignKeyConstraint(["actividad_id"], ["actividades.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["modificado_por_id"], ["usuarios.id"]),
        sa.UniqueConstraint("actividad_id", name="uq_publicaciones_web_actividad"),
    )
    op.create_index("ix_publicaciones_web_actividad_id", "publicaciones_web", ["actividad_id"])


def downgrade() -> None:
    op.drop_index("ix_publicaciones_web_actividad_id", "publicaciones_web")
    op.drop_table("publicaciones_web")
