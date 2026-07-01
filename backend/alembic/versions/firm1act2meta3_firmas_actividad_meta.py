"""Ancla la recogida de firmas a la Actividad: MetaActividad + FirmaCampania.actividad_id.

- Crea la tabla `metas_actividad` (espejo de `metas_campania`; la meta en firmas
  de una actividad de recogida vive aquí).
- Añade `firmas_campania.actividad_id` (FK actividades, nullable) para anclar la
  firma a la actividad online.
- Hace `firmas_campania.campania_id` NULL-able (queda como contexto denormalizado).

Aditiva: no borra datos. Las firmas existentes conservan su `campania_id`.

Revision ID: firm1act2meta3
Revises: vol1ext2anc3
"""
from alembic import op
import sqlalchemy as sa


revision = "firm1act2meta3"
down_revision = "vol1ext2anc3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "metas_actividad",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("actividad_id", sa.Uuid(), nullable=False),
        sa.Column("tipo_meta_id", sa.Uuid(), nullable=False),
        sa.Column("valor_planificado", sa.Numeric(14, 2), nullable=True),
        sa.Column("valor_real", sa.Numeric(14, 2), nullable=True),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column("orden", sa.Integer(), server_default="0", nullable=False),
        # Auditoría (BaseModel)
        sa.Column("fecha_creacion", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("fecha_modificacion", sa.DateTime(), nullable=True),
        sa.Column("fecha_eliminacion", sa.DateTime(), nullable=True),
        sa.Column("eliminado", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("creado_por_id", sa.Uuid(), nullable=True),
        sa.Column("modificado_por_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["actividad_id"], ["actividades.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tipo_meta_id"], ["tipos_meta_campania.id"]),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["modificado_por_id"], ["usuarios.id"]),
    )
    op.create_index("ix_metas_actividad_actividad_id", "metas_actividad", ["actividad_id"])
    op.create_index("ix_metas_actividad_tipo_meta_id", "metas_actividad", ["tipo_meta_id"])
    op.create_index("ix_metas_actividad_eliminado", "metas_actividad", ["eliminado"])

    # firmas_campania: se ancla a la actividad y la campaña pasa a nullable.
    op.add_column("firmas_campania", sa.Column("actividad_id", sa.Uuid(), nullable=True))
    op.create_index("ix_firmas_campania_actividad_id", "firmas_campania", ["actividad_id"])
    op.create_foreign_key(
        "fk_firmas_campania_actividad", "firmas_campania", "actividades",
        ["actividad_id"], ["id"],
    )
    op.alter_column("firmas_campania", "campania_id", existing_type=sa.Uuid(), nullable=True)


def downgrade() -> None:
    # Restaurar campania_id NOT NULL: rellenar desde la actividad y purgar huérfanas.
    op.execute(sa.text("""
        UPDATE firmas_campania f
        SET campania_id = a.campania_id
        FROM actividades a
        WHERE f.campania_id IS NULL AND f.actividad_id = a.id
    """))
    op.execute(sa.text("DELETE FROM firmas_campania WHERE campania_id IS NULL"))
    op.alter_column("firmas_campania", "campania_id", existing_type=sa.Uuid(), nullable=False)

    op.drop_constraint("fk_firmas_campania_actividad", "firmas_campania", type_="foreignkey")
    op.drop_index("ix_firmas_campania_actividad_id", "firmas_campania")
    op.drop_column("firmas_campania", "actividad_id")

    op.drop_index("ix_metas_actividad_eliminado", "metas_actividad")
    op.drop_index("ix_metas_actividad_tipo_meta_id", "metas_actividad")
    op.drop_index("ix_metas_actividad_actividad_id", "metas_actividad")
    op.drop_table("metas_actividad")
