"""Catálogos de metas/canales, instancias por campaña, y sistema de plantillas.

Revision ID: g2h3i4j5k6l7
Revises: a7f3c9d8b2e4
Create Date: 2026-05-16 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision: str = 'g2h3i4j5k6l7'
down_revision: str = 'a7f3c9d8b2e4'
branch_labels = None
depends_on = None

NEW_TABLES = [
    'tipos_meta_campania',
    'tipos_canal_difusion',
    'metas_campania',
    'canales_difusion_campania',
    'partidas_presupuesto_campania',
    'plantillas_campania',
    'plantilla_metas',
    'plantilla_partidas',
    'plantilla_actividades',
    'plantilla_tareas',
]


def upgrade() -> None:
    from app.core.database import Base
    # Ensure all models are registered before create_all
    import app.models  # noqa: F401

    bind = op.get_bind()
    # Create only the new tables (checkfirst=True skips existing ones)
    Base.metadata.create_all(bind=bind, checkfirst=True, tables=[
        Base.metadata.tables[t] for t in NEW_TABLES
        if t in Base.metadata.tables
    ])

    # Seeds: tipos_meta_campania
    op.execute("""
        INSERT INTO tipos_meta_campania (id, nombre, descripcion, unidad_medida, activo, eliminado, fecha_creacion)
        SELECT
          gen_random_uuid(), nombre, descripcion, unidad_medida, true, false, NOW()
        FROM (VALUES
          ('Recaudación de fondos', 'Importe total recaudado', '€'),
          ('Participantes', 'Número de personas que participan', 'personas'),
          ('Firmas recogidas', 'Número de firmas o adhesiones', 'firmas'),
          ('Visitas web', 'Número de visitas a la página de la campaña', 'visitas'),
          ('Impacto en medios', 'Menciones o apariciones en medios de comunicación', 'menciones')
        ) AS t(nombre, descripcion, unidad_medida)
        WHERE NOT EXISTS (SELECT 1 FROM tipos_meta_campania LIMIT 1)
    """)

    # Seeds: tipos_canal_difusion
    op.execute("""
        INSERT INTO tipos_canal_difusion (id, nombre, descripcion, activo, eliminado, fecha_creacion)
        SELECT
          gen_random_uuid(), nombre, descripcion, true, false, NOW()
        FROM (VALUES
          ('Email membresía', 'Correo electrónico a socios y simpatizantes'),
          ('Web / Blog', 'Publicación en la web o blog de la organización'),
          ('Redes sociales', 'Difusión en redes sociales'),
          ('Prensa', 'Notas de prensa o apariciones en medios'),
          ('Eventos y actos', 'Presentación en eventos presenciales'),
          ('Publicidad exterior', 'Carteles, lonas, flyers…')
        ) AS t(nombre, descripcion)
        WHERE NOT EXISTS (SELECT 1 FROM tipos_canal_difusion LIMIT 1)
    """)


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table('plantilla_tareas')
    op.drop_table('plantilla_actividades')
    op.drop_table('plantilla_partidas')
    op.drop_table('plantilla_metas')
    op.drop_table('plantillas_campania')
    op.drop_table('partidas_presupuesto_campania')
    op.drop_table('canales_difusion_campania')
    op.drop_table('metas_campania')
    op.drop_table('tipos_canal_difusion')
    op.drop_table('tipos_meta_campania')
