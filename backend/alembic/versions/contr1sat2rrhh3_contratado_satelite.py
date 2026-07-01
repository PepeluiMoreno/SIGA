"""Satélite Contratado (EMPLEADO): cierra el invariante 'requiere_satelite ⇒ modelo'.

Crea la tabla `contratados` (satélite 1:1 de Vinculacion(EMPLEADO)): datos del
contrato con la organización (laboral para PF, mercantil para PJ).

Aditiva.

Revision ID: contr1sat2rrhh3
Revises: rel1model2civi3
"""
from alembic import op
import sqlalchemy as sa


revision = "contr1sat2rrhh3"
down_revision = "rel1model2civi3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contratados",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("vinculacion_id", sa.Uuid(), nullable=False),
        sa.Column("numero_empleado", sa.String(length=50), nullable=True),
        sa.Column("tipo_contrato", sa.String(length=20), server_default="LABORAL", nullable=False),
        sa.Column("jornada", sa.String(length=20), nullable=True),
        sa.Column("categoria", sa.String(length=150), nullable=True),
        sa.Column("fecha_alta_contrato", sa.Date(), nullable=True),
        sa.Column("fecha_baja_contrato", sa.Date(), nullable=True),
        sa.Column("numero_seguridad_social", sa.String(length=30), nullable=True),
        sa.Column("salario_bruto_anual", sa.Numeric(12, 2), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
        # Auditoría (BaseModel)
        sa.Column("fecha_creacion", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("fecha_modificacion", sa.DateTime(), nullable=True),
        sa.Column("fecha_eliminacion", sa.DateTime(), nullable=True),
        sa.Column("eliminado", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("creado_por_id", sa.Uuid(), nullable=True),
        sa.Column("modificado_por_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["vinculacion_id"], ["vinculaciones.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["modificado_por_id"], ["usuarios.id"]),
        sa.UniqueConstraint("vinculacion_id", name="uq_contratados_vinculacion"),
    )
    op.create_index("ix_contratados_vinculacion_id", "contratados", ["vinculacion_id"])
    op.create_index("ix_contratados_eliminado", "contratados", ["eliminado"])


def downgrade() -> None:
    op.drop_index("ix_contratados_eliminado", "contratados")
    op.drop_index("ix_contratados_vinculacion_id", "contratados")
    op.drop_table("contratados")
