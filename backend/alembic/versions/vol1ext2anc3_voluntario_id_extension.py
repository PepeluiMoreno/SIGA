"""Ancla los datos de voluntario a la extensión Voluntario (miembro_id -> voluntario_id).

Los documentos, competencias, formación, habilidades y franjas de disponibilidad
del voluntario colgaban de un `miembro_id` residual de la era pre-CRM (unos sin FK,
otros apuntando a contactos). Pasan a colgar de la extensión `Voluntario`
(`voluntario_id` -> voluntarios.id, ondelete CASCADE), coherente con que son datos
del vínculo de voluntario.

Backfill: mapea miembro_id (= contacto) -> su Voluntario vía Vinculacion VOLUNTARIO.
Si una fila no tiene vinculación de voluntario, se elimina (dato huérfano del modelo
viejo). En BD recién creadas estas tablas están vacías y el backfill es no-op.

Revision ID: vol1ext2anc3
Revises: e6f7a8b9c0d1
"""
from alembic import op
import sqlalchemy as sa


revision = "vol1ext2anc3"
down_revision = "e6f7a8b9c0d1"
branch_labels = None
depends_on = None


# (tabla, nombre del índice/constraint viejo a limpiar si aplica)
_TABLAS = [
    "documentos_miembro",
    "miembros_competencia",
    "formaciones_miembro",
    "miembros_habilidades",
    "franjas_disponibilidad",
]


def upgrade() -> None:
    for tabla in _TABLAS:
        # 1) Nueva columna nullable + FK a voluntarios.
        op.add_column(tabla, sa.Column("voluntario_id", sa.Uuid(), nullable=True))
        op.create_index(f"ix_{tabla}_voluntario_id", tabla, ["voluntario_id"])
        op.create_foreign_key(
            f"fk_{tabla}_voluntario", tabla, "voluntarios",
            ["voluntario_id"], ["id"], ondelete="CASCADE",
        )

        # 2) Backfill: miembro_id (=contacto) -> voluntario de su vinculación VOLUNTARIO.
        op.execute(sa.text(f"""
            UPDATE {tabla} t
            SET voluntario_id = vo.id
            FROM voluntarios vo
            JOIN vinculaciones vi ON vi.id = vo.vinculacion_id
            WHERE vi.contacto_id = t.miembro_id
        """))

        # 3) Filas sin voluntario (dato huérfano del modelo viejo): se eliminan.
        op.execute(sa.text(f"DELETE FROM {tabla} WHERE voluntario_id IS NULL"))

        # 4) La unique de habilidad pasa de (miembro_id,…) a (voluntario_id,…) ANTES de
        #    dropear miembro_id (la constraint vieja lo referencia).
        if tabla == "miembros_habilidades":
            op.drop_constraint("uq_miembro_habilidad", tabla, type_="unique")
            op.create_unique_constraint(
                "uq_miembro_habilidad", tabla, ["voluntario_id", "habilidad_id"]
            )

        # 5) Ya poblada: voluntario_id pasa a NOT NULL y se retira miembro_id.
        op.alter_column(tabla, "voluntario_id", nullable=False)
        op.drop_column(tabla, "miembro_id")


def downgrade() -> None:
    op.drop_constraint("uq_miembro_habilidad", "miembros_habilidades", type_="unique")
    op.create_unique_constraint(
        "uq_miembro_habilidad", "miembros_habilidades", ["miembro_id", "habilidad_id"]
    )
    for tabla in _TABLAS:
        op.add_column(tabla, sa.Column("miembro_id", sa.Uuid(), nullable=True))
        op.execute(sa.text(f"""
            UPDATE {tabla} t
            SET miembro_id = vi.contacto_id
            FROM voluntarios vo
            JOIN vinculaciones vi ON vi.id = vo.vinculacion_id
            WHERE vo.id = t.voluntario_id
        """))
        op.alter_column(tabla, "miembro_id", nullable=False)
        op.drop_constraint(f"fk_{tabla}_voluntario", tabla, type_="foreignkey")
        op.drop_index(f"ix_{tabla}_voluntario_id", tabla)
        op.drop_column(tabla, "voluntario_id")
