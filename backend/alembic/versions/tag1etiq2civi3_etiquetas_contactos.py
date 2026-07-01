"""Etiquetas de contactos (tipo CiviCRM Tag): etiquetas + contactos_etiquetas.

Clasificación libre y transversal de contactos (simpatizante, prensa, ponente…).
Aditiva.

Revision ID: tag1etiq2civi3
Revises: contr1sat2rrhh3
"""
from alembic import op
import sqlalchemy as sa


revision = "tag1etiq2civi3"
down_revision = "contr1sat2rrhh3"
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
        "etiquetas",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("nombre", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        *_audit_cols(),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["modificado_por_id"], ["usuarios.id"]),
    )
    op.create_index("ix_etiquetas_nombre", "etiquetas", ["nombre"], unique=True)
    op.create_index("ix_etiquetas_activo", "etiquetas", ["activo"])

    op.create_table(
        "contactos_etiquetas",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("contacto_id", sa.Uuid(), nullable=False),
        sa.Column("etiqueta_id", sa.Uuid(), nullable=False),
        *_audit_cols(),
        sa.ForeignKeyConstraint(["contacto_id"], ["contactos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["etiqueta_id"], ["etiquetas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["modificado_por_id"], ["usuarios.id"]),
        sa.UniqueConstraint("contacto_id", "etiqueta_id", name="uq_contacto_etiqueta"),
    )
    op.create_index("ix_contactos_etiquetas_contacto_id", "contactos_etiquetas", ["contacto_id"])
    op.create_index("ix_contactos_etiquetas_etiqueta_id", "contactos_etiquetas", ["etiqueta_id"])


def downgrade() -> None:
    op.drop_index("ix_contactos_etiquetas_etiqueta_id", "contactos_etiquetas")
    op.drop_index("ix_contactos_etiquetas_contacto_id", "contactos_etiquetas")
    op.drop_table("contactos_etiquetas")
    op.drop_index("ix_etiquetas_activo", "etiquetas")
    op.drop_index("ix_etiquetas_nombre", "etiquetas")
    op.drop_table("etiquetas")
