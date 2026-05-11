"""Añade TipoUnidadOrganizativa y reestructura AgrupacionTerritorial

Revision ID: m014
Revises: m013
Create Date: 2026-05-06
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'm014'
down_revision: Union[str, None] = 'm013'
branch_labels = None
depends_on = None


def _audit():
    return [
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('creado_por_id', sa.Uuid(), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
    ]


def upgrade() -> None:
    # 1. Crear enums PostgreSQL
    op.execute("CREATE TYPE naturalezaunidad AS ENUM ('TERRITORIAL','FUNCIONAL','PROGRAMATICA','ADMINISTRATIVA')")
    op.execute("CREATE TYPE vinculounidad AS ENUM ('INTERNA','FILIAL','FEDERADA')")

    # 2. Crear tabla de catálogo
    op.create_table(
        'tipos_unidades_organizativas',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('naturaleza', sa.Enum('TERRITORIAL', 'FUNCIONAL', 'PROGRAMATICA', 'ADMINISTRATIVA',
                                        name='naturalezaunidad', create_type=False), nullable=False),
        sa.Column('vinculo', sa.Enum('INTERNA', 'FILIAL', 'FEDERADA',
                                     name='vinculounidad', create_type=False), nullable=False),
        sa.Column('nivel', sa.Integer(), nullable=True),
        sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
        *_audit(),
    )
    op.create_index('ix_tipos_unidades_org_naturaleza', 'tipos_unidades_organizativas', ['naturaleza'])
    op.create_index('ix_tipos_unidades_org_vinculo',    'tipos_unidades_organizativas', ['vinculo'])
    op.create_index('ix_tipos_unidades_org_eliminado',  'tipos_unidades_organizativas', ['eliminado'])
    op.create_foreign_key(None, 'tipos_unidades_organizativas', 'usuarios', ['creado_por_id'],    ['id'])
    op.create_foreign_key(None, 'tipos_unidades_organizativas', 'usuarios', ['modificado_por_id'], ['id'])

    # 3. Insertar tipos por defecto
    op.execute("""
        INSERT INTO tipos_unidades_organizativas (id, nombre, naturaleza, vinculo, nivel, activo, fecha_creacion, eliminado)
        VALUES
          (gen_random_uuid(), 'Sede / Federación nacional', 'TERRITORIAL', 'INTERNA', 1, true, now(), false),
          (gen_random_uuid(), 'Delegación regional',        'TERRITORIAL', 'INTERNA', 2, true, now(), false),
          (gen_random_uuid(), 'Grupo local',                'TERRITORIAL', 'INTERNA', 3, true, now(), false),
          (gen_random_uuid(), 'Sección funcional',          'FUNCIONAL',   'INTERNA', NULL, true, now(), false),
          (gen_random_uuid(), 'Área programática',          'PROGRAMATICA','INTERNA', NULL, true, now(), false),
          (gen_random_uuid(), 'Entidad filial',             'TERRITORIAL', 'FILIAL',  NULL, true, now(), false),
          (gen_random_uuid(), 'Entidad federada',           'TERRITORIAL', 'FEDERADA',NULL, true, now(), false)
    """)

    # 4. Añadir nuevas columnas a agrupaciones_territoriales
    op.add_column('agrupaciones_territoriales', sa.Column('tipo_id', sa.Uuid(), nullable=True))
    op.add_column('agrupaciones_territoriales', sa.Column('nif', sa.String(20), nullable=True))
    op.add_column('agrupaciones_territoriales', sa.Column('fecha_constitucion', sa.Date(), nullable=True))
    op.add_column('agrupaciones_territoriales', sa.Column('registro_oficial', sa.String(200), nullable=True))
    op.create_index('ix_agrup_territ_tipo_id', 'agrupaciones_territoriales', ['tipo_id'])
    op.create_foreign_key(None, 'agrupaciones_territoriales', 'tipos_unidades_organizativas',
                          ['tipo_id'], ['id'], ondelete='SET NULL')

    # 5. Migrar datos históricos
    op.execute("""
        UPDATE agrupaciones_territoriales a
        SET tipo_id = t.id
        FROM tipos_unidades_organizativas t
        WHERE t.nivel = 1 AND UPPER(a.tipo) IN ('NACIONAL','ESTATAL','INTERNACIONAL','FEDERAL')
    """)
    op.execute("""
        UPDATE agrupaciones_territoriales a
        SET tipo_id = t.id
        FROM tipos_unidades_organizativas t
        WHERE t.nivel = 2 AND UPPER(a.tipo) IN ('AUTONOMICO','AUTONOMICA','REGIONAL','PROVINCIAL')
    """)
    op.execute("""
        UPDATE agrupaciones_territoriales a
        SET tipo_id = t.id
        FROM tipos_unidades_organizativas t
        WHERE t.nivel = 3 AND UPPER(a.tipo) IN ('LOCAL','MUNICIPAL','COMARCAL')
    """)

    # 6. Eliminar columnas obsoletas
    op.drop_index('ix_agrupaciones_territoriales_tipo', table_name='agrupaciones_territoriales')
    op.drop_column('agrupaciones_territoriales', 'tipo')
    op.drop_column('agrupaciones_territoriales', 'nivel')


def downgrade() -> None:
    op.add_column('agrupaciones_territoriales', sa.Column('nivel', sa.Integer(), nullable=True))
    op.add_column('agrupaciones_territoriales', sa.Column('tipo', sa.String(50), nullable=True))
    op.drop_column('agrupaciones_territoriales', 'registro_oficial')
    op.drop_column('agrupaciones_territoriales', 'fecha_constitucion')
    op.drop_column('agrupaciones_territoriales', 'nif')
    op.drop_index('ix_agrup_territ_tipo_id', table_name='agrupaciones_territoriales')
    op.drop_column('agrupaciones_territoriales', 'tipo_id')
    op.drop_table('tipos_unidades_organizativas')
    op.execute("DROP TYPE IF EXISTS vinculounidad")
    op.execute("DROP TYPE IF EXISTS naturalezaunidad")
