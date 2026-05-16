"""rename_tipos_agrupacion_to_niveles_unidades

Revision ID: 031b5617936a
Revises: 705751a664c9
Create Date: 2026-05-15 07:37:40.927013
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '031b5617936a'
down_revision: Union[str, None] = '705751a664c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename tables (data preserved)
    op.rename_table('tipos_unidades_organizativas', 'niveles_organizativos')
    op.rename_table('agrupaciones_territoriales', 'unidades_organizativas')

    # Rename indices on niveles_organizativos
    op.execute("ALTER INDEX IF EXISTS ix_tipos_unidades_organizativas_eliminado RENAME TO ix_niveles_organizativos_eliminado")
    op.execute("ALTER INDEX IF EXISTS ix_tipos_unidades_organizativas_naturaleza RENAME TO ix_niveles_organizativos_naturaleza")
    op.execute("ALTER INDEX IF EXISTS ix_tipos_unidades_organizativas_padre_tipo_id RENAME TO ix_niveles_organizativos_padre_tipo_id")
    op.execute("ALTER INDEX IF EXISTS ix_tipos_unidades_organizativas_vinculo RENAME TO ix_niveles_organizativos_vinculo")

    # Rename indices on unidades_organizativas
    op.execute("ALTER INDEX IF EXISTS ix_agrupaciones_territoriales_activo RENAME TO ix_unidades_organizativas_activo")
    op.execute("ALTER INDEX IF EXISTS ix_agrupaciones_territoriales_agrupacion_padre_id RENAME TO ix_unidades_organizativas_agrupacion_padre_id")
    op.execute("ALTER INDEX IF EXISTS ix_agrupaciones_territoriales_eliminado RENAME TO ix_unidades_organizativas_eliminado")
    op.execute("ALTER INDEX IF EXISTS ix_agrupaciones_territoriales_municipio_id RENAME TO ix_unidades_organizativas_municipio_id")
    op.execute("ALTER INDEX IF EXISTS ix_agrupaciones_territoriales_nombre RENAME TO ix_unidades_organizativas_nombre")
    op.execute("ALTER INDEX IF EXISTS ix_agrupaciones_territoriales_pais_id RENAME TO ix_unidades_organizativas_pais_id")
    op.execute("ALTER INDEX IF EXISTS ix_agrupaciones_territoriales_provincia_id RENAME TO ix_unidades_organizativas_provincia_id")
    op.execute("ALTER INDEX IF EXISTS ix_agrupaciones_territoriales_tipo_id RENAME TO ix_unidades_organizativas_tipo_id")

    # Create materialized view with new name (was not created before)
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS vista_unidades_organizativas AS
        SELECT
            o.id,
            o.nombre,
            o.nombre_corto,
            CASE
                WHEN LOWER(t.nombre) LIKE '%estatal%' THEN 'ESTATAL'
                WHEN LOWER(t.nombre) LIKE '%internacional%' THEN 'INTERNACIONAL'
                WHEN LOWER(t.nombre) LIKE '%autonóm%' OR LOWER(t.nombre) LIKE '%autonom%' THEN 'AUTONOMICA'
                WHEN LOWER(t.nombre) LIKE '%provincial%' THEN 'PROVINCIAL'
                WHEN LOWER(t.nombre) LIKE '%local%' THEN 'LOCAL'
                ELSE o.ambito
            END as tipo,
            o.organizacion_padre_id as agrupacion_padre_id,
            o.nivel,
            o.pais_id,
            o.provincia_id,
            o.municipio_id,
            o.direccion_id,
            o.email,
            COALESCE(o.telefono_movil, o.telefono_fijo) as telefono,
            o.web,
            o.descripcion,
            o.activo
        FROM organizaciones o
        INNER JOIN tipos_organizacion t ON o.tipo_id = t.id
        WHERE t.categoria = 'INTERNA'
          AND o.eliminado = FALSE
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_vista_unid_id ON vista_unidades_organizativas(id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_vista_unid_tipo ON vista_unidades_organizativas(tipo)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_vista_unid_padre ON vista_unidades_organizativas(agrupacion_padre_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_vista_unid_provincia ON vista_unidades_organizativas(provincia_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_vista_unid_activo ON vista_unidades_organizativas(activo)")


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS vista_unidades_organizativas CASCADE")

    op.execute("ALTER INDEX IF EXISTS ix_unidades_organizativas_tipo_id RENAME TO ix_agrupaciones_territoriales_tipo_id")
    op.execute("ALTER INDEX IF EXISTS ix_unidades_organizativas_provincia_id RENAME TO ix_agrupaciones_territoriales_provincia_id")
    op.execute("ALTER INDEX IF EXISTS ix_unidades_organizativas_pais_id RENAME TO ix_agrupaciones_territoriales_pais_id")
    op.execute("ALTER INDEX IF EXISTS ix_unidades_organizativas_nombre RENAME TO ix_agrupaciones_territoriales_nombre")
    op.execute("ALTER INDEX IF EXISTS ix_unidades_organizativas_municipio_id RENAME TO ix_agrupaciones_territoriales_municipio_id")
    op.execute("ALTER INDEX IF EXISTS ix_unidades_organizativas_eliminado RENAME TO ix_agrupaciones_territoriales_eliminado")
    op.execute("ALTER INDEX IF EXISTS ix_unidades_organizativas_agrupacion_padre_id RENAME TO ix_agrupaciones_territoriales_agrupacion_padre_id")
    op.execute("ALTER INDEX IF EXISTS ix_unidades_organizativas_activo RENAME TO ix_agrupaciones_territoriales_activo")

    op.execute("ALTER INDEX IF EXISTS ix_niveles_organizativos_vinculo RENAME TO ix_tipos_unidades_organizativas_vinculo")
    op.execute("ALTER INDEX IF EXISTS ix_niveles_organizativos_padre_tipo_id RENAME TO ix_tipos_unidades_organizativas_padre_tipo_id")
    op.execute("ALTER INDEX IF EXISTS ix_niveles_organizativos_naturaleza RENAME TO ix_tipos_unidades_organizativas_naturaleza")
    op.execute("ALTER INDEX IF EXISTS ix_niveles_organizativos_eliminado RENAME TO ix_tipos_unidades_organizativas_eliminado")

    op.rename_table('unidades_organizativas', 'agrupaciones_territoriales')
    op.rename_table('niveles_organizativos', 'tipos_unidades_organizativas')
