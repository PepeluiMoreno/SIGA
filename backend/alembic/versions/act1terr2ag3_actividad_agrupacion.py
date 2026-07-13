"""Actividad.agrupacion_id: ancla territorial de la actividad

El motor territorial necesita saber a qué agrupación pertenece una actividad para
poder decidir si cae en el ámbito del usuario. Hasta ahora el territorio solo se
deducía por caminos ambiguos y opcionales (la campaña o el grupo de trabajo), y una
actividad interna sin campaña ni grupo no tenía territorio alguno: era inacotable.

Relleno: se hereda de la campaña, y si no la hay, del grupo. Lo que quede a NULL es
actividad de la organización central (solo la alcanza un ámbito global).

Revision ID: act1terr2ag3
Revises: sec2acu3sem4
"""
from alembic import op
import sqlalchemy as sa


revision = "act1terr2ag3"
down_revision = "sec2acu3sem4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "actividades",
        sa.Column("agrupacion_id", sa.Uuid(), nullable=True),
    )
    op.create_index(
        "ix_actividades_agrupacion_id", "actividades", ["agrupacion_id"]
    )
    op.create_foreign_key(
        "actividades_agrupacion_id_fkey",
        "actividades", "unidades_organizativas",
        ["agrupacion_id"], ["id"],
    )

    # Heredar el territorio de la campaña; si no hay campaña, del grupo de trabajo.
    op.execute("""
        UPDATE actividades a
           SET agrupacion_id = c.agrupacion_id
          FROM campanias c
         WHERE a.campania_id = c.id
           AND c.agrupacion_id IS NOT NULL
    """)
    op.execute("""
        UPDATE actividades a
           SET agrupacion_id = g.agrupacion_id
          FROM grupos_trabajo g
         WHERE a.agrupacion_id IS NULL
           AND a.grupo_id = g.id
           AND g.agrupacion_id IS NOT NULL
    """)


def downgrade() -> None:
    op.drop_constraint(
        "actividades_agrupacion_id_fkey", "actividades", type_="foreignkey"
    )
    op.drop_index("ix_actividades_agrupacion_id", table_name="actividades")
    op.drop_column("actividades", "agrupacion_id")
