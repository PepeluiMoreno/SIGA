"""Modelo Relationship (contacto↔contacto): tipos_relacion + relaciones. Depura taxonomía de vinculaciones.

- Crea `tipos_relacion` (catálogo direccional) y `relaciones` (vínculo A→B).
- Desactiva los tipos de vinculación FIRMANTE y SIMPATIZANTE: "firmante /
  participante / simpatizante" son condiciones derivadas, no afiliaciones.
  (ORGANIZACION_AMIGA y los tipos de relación se crean vía seed.)

Aditiva/no destructiva: no borra vinculaciones existentes, solo desactiva
catálogo.

Revision ID: rel1model2civi3
Revises: grup1cat2act3
"""
from alembic import op
import sqlalchemy as sa


revision = "rel1model2civi3"
down_revision = "grup1cat2act3"
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
        "tipos_relacion",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("nombre_directo", sa.String(length=100), nullable=False),
        sa.Column("nombre_inverso", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        *_audit_cols(),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["modificado_por_id"], ["usuarios.id"]),
    )
    op.create_index("ix_tipos_relacion_codigo", "tipos_relacion", ["codigo"], unique=True)
    op.create_index("ix_tipos_relacion_activo", "tipos_relacion", ["activo"])

    op.create_table(
        "relaciones",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("contacto_a_id", sa.Uuid(), nullable=False),
        sa.Column("contacto_b_id", sa.Uuid(), nullable=False),
        sa.Column("tipo_relacion_id", sa.Uuid(), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=True),
        sa.Column("fecha_fin", sa.Date(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("notas", sa.Text(), nullable=True),
        *_audit_cols(),
        sa.ForeignKeyConstraint(["contacto_a_id"], ["contactos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contacto_b_id"], ["contactos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tipo_relacion_id"], ["tipos_relacion.id"]),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["modificado_por_id"], ["usuarios.id"]),
    )
    op.create_index("ix_relaciones_contacto_a_id", "relaciones", ["contacto_a_id"])
    op.create_index("ix_relaciones_contacto_b_id", "relaciones", ["contacto_b_id"])
    op.create_index("ix_relaciones_tipo_relacion_id", "relaciones", ["tipo_relacion_id"])
    op.create_index("ix_relaciones_activo", "relaciones", ["activo"])

    # Depuración de taxonomía: firmante/simpatizante dejan de ser afiliaciones.
    op.execute(sa.text(
        "UPDATE tipos_vinculacion SET activo = false "
        "WHERE codigo IN ('FIRMANTE', 'SIMPATIZANTE')"
    ))


def downgrade() -> None:
    op.execute(sa.text(
        "UPDATE tipos_vinculacion SET activo = true "
        "WHERE codigo IN ('FIRMANTE', 'SIMPATIZANTE')"
    ))
    op.drop_table("relaciones")
    op.drop_table("tipos_relacion")
