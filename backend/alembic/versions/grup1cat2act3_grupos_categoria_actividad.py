"""Generalización de Grupos (alcance seguro): TipoGrupo.categoria + GrupoTrabajo.actividad_id.

- Añade `tipos_grupo.categoria` (clasificador del concepto Grupo:
  TERRITORIAL | ORGANICO | EFIMERO_CAMPANIA | EFIMERO_ACTIVIDAD).
- Añade `grupos_trabajo.actividad_id` (FK actividades, nullable) para el grupo
  efímero formado con ocasión de una actividad (simétrico a campania_id).

Aditiva: no toca UnidadOrganizativa ni las FKs territoriales. No borra datos.

Revision ID: grup1cat2act3
Revises: firm1act2meta3
"""
from alembic import op
import sqlalchemy as sa


revision = "grup1cat2act3"
down_revision = "firm1act2meta3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tipos_grupo",
        sa.Column("categoria", sa.String(length=30), server_default="ORGANICO", nullable=False),
    )
    op.create_index("ix_tipos_grupo_categoria", "tipos_grupo", ["categoria"])
    # Los tipos marcados permanentes se asumen orgánicos; el resto quedan como
    # ORGANICO por defecto (afinable por seed). TERRITORIAL se reserva y no se
    # asigna aquí (la territorial la implementa UnidadOrganizativa).

    op.add_column("grupos_trabajo", sa.Column("actividad_id", sa.Uuid(), nullable=True))
    op.create_index("ix_grupos_trabajo_actividad_id", "grupos_trabajo", ["actividad_id"])
    op.create_foreign_key(
        "fk_grupos_trabajo_actividad", "grupos_trabajo", "actividades",
        ["actividad_id"], ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_grupos_trabajo_actividad", "grupos_trabajo", type_="foreignkey")
    op.drop_index("ix_grupos_trabajo_actividad_id", "grupos_trabajo")
    op.drop_column("grupos_trabajo", "actividad_id")

    op.drop_index("ix_tipos_grupo_categoria", "tipos_grupo")
    op.drop_column("tipos_grupo", "categoria")
