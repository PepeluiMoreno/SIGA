"""Payload de acuerdo de presupuesto de campaña

Tabla satélite 1:1 con `sec_acuerdos` (patrón de `sec_acuerdos_nombramiento`) que guarda
lo que la máquina necesita para ejecutar un acuerdo de APROBACION_PRESUPUESTO: qué campaña,
cuánto se reserva y contra qué partida anual. El `compromiso_id` se rellena al ejecutar
(idempotencia).

Revision ID: camp2acuerdoppto
Revises: camp1madurez
"""
from alembic import op
import sqlalchemy as sa


revision = "camp2acuerdoppto"
down_revision = "camp1madurez"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sec_acuerdos_presupuesto_campania",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("acuerdo_id", sa.Uuid(), nullable=False),
        sa.Column("campania_id", sa.Uuid(), nullable=False),
        sa.Column("partida_id", sa.Uuid(), nullable=False),
        sa.Column("importe", sa.Numeric(12, 2), nullable=False),
        sa.Column("compromiso_id", sa.Uuid(), nullable=True),
        # Columnas de BaseModel
        sa.Column("fecha_creacion", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("fecha_modificacion", sa.DateTime(), nullable=True),
        sa.Column("fecha_eliminacion", sa.DateTime(), nullable=True),
        sa.Column("eliminado", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("creado_por_id", sa.Uuid(), nullable=True),
        sa.Column("modificado_por_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["acuerdo_id"], ["sec_acuerdos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["campania_id"], ["campanias.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["partida_id"], ["partidas_presupuestarias.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["compromiso_id"], ["compromisos_presupuestarios.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["modificado_por_id"], ["usuarios.id"]),
        sa.UniqueConstraint("acuerdo_id"),
    )
    op.create_index("ix_sec_acuerdos_ppto_campania_acuerdo", "sec_acuerdos_presupuesto_campania", ["acuerdo_id"])
    op.create_index("ix_sec_acuerdos_ppto_campania_campania", "sec_acuerdos_presupuesto_campania", ["campania_id"])
    op.create_index("ix_sec_acuerdos_ppto_campania_partida", "sec_acuerdos_presupuesto_campania", ["partida_id"])


def downgrade() -> None:
    op.drop_table("sec_acuerdos_presupuesto_campania")
