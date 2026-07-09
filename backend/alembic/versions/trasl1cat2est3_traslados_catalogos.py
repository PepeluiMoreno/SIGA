"""Traslados: catálogos de motivos y estados (con color) + FK en solicitudes.

Crea las tablas de catálogo ``motivos_traslado`` y ``estados_traslado`` (esta
última de presentación, con color), añade ``motivo_traslado_id`` a
``solicitudes_traslado``, hace ``motivo`` nullable (pasa a detalle libre) y
siembra ambos catálogos de forma idempotente.

Revision ID: trasl1cat2est3
Revises: tag1etiq2civi3
Create Date: 2026-07-09 22:40:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision: str = 'trasl1cat2est3'
down_revision: str = 'tag1etiq2civi3'
branch_labels = None
depends_on = None

NEW_TABLES = ['motivos_traslado', 'estados_traslado']


def upgrade() -> None:
    from app.core.database import Base
    import app.models  # noqa: F401  (registra todos los modelos en Base.metadata)

    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 1) Tablas nuevas (checkfirst evita recrearlas si ya existen).
    Base.metadata.create_all(bind=bind, checkfirst=True, tables=[
        Base.metadata.tables[t] for t in NEW_TABLES if t in Base.metadata.tables
    ])

    # 2) Columna motivo_traslado_id en solicitudes_traslado + motivo nullable.
    cols = {c['name'] for c in insp.get_columns('solicitudes_traslado')}
    if 'motivo_traslado_id' not in cols:
        op.add_column('solicitudes_traslado',
                      sa.Column('motivo_traslado_id', sa.Uuid(), nullable=True))
        op.create_index('ix_solicitudes_traslado_motivo_traslado_id',
                        'solicitudes_traslado', ['motivo_traslado_id'])
        op.create_foreign_key('solicitudes_traslado_motivo_traslado_id_fkey',
                              'solicitudes_traslado', 'motivos_traslado',
                              ['motivo_traslado_id'], ['id'])
    # `motivo` deja de ser obligatorio (queda como detalle libre).
    op.alter_column('solicitudes_traslado', 'motivo',
                    existing_type=sa.Text(), nullable=True)

    # 3) Seed idempotente de motivos_traslado.
    op.execute("""
        INSERT INTO motivos_traslado (id, codigo, nombre, descripcion, orden, activo, es_inmutable, eliminado, fecha_creacion)
        SELECT gen_random_uuid(), codigo, nombre, descripcion, orden, true, true, false, NOW()
        FROM (VALUES
          ('CAMBIO_DOMICILIO', 'Cambio de domicilio', 'El socio ha cambiado de residencia', 1),
          ('REORGANIZACION',   'Reorganización territorial', 'Reajuste de agrupaciones de la asociación', 2),
          ('PREFERENCIA',      'Preferencia personal', 'El socio prefiere otra agrupación', 3),
          ('OTRO',             'Otro', 'Otro motivo (se detalla en el texto libre)', 9)
        ) AS t(codigo, nombre, descripcion, orden)
        WHERE NOT EXISTS (SELECT 1 FROM motivos_traslado WHERE motivos_traslado.codigo = t.codigo)
    """)

    # 4) Seed idempotente de estados_traslado (con color, es_inicial/es_final).
    op.execute("""
        INSERT INTO estados_traslado (id, codigo, nombre, descripcion, orden, es_inicial, es_final, activo, color, es_inmutable, eliminado, fecha_creacion)
        SELECT gen_random_uuid(), codigo, nombre, NULL, orden, es_inicial, es_final, true, color, true, false, NOW()
        FROM (VALUES
          ('PENDIENTE',         'Pendiente',          1, true,  false, '#f59e0b'),
          ('APROBADO_ORIGEN',   'Aprobado por origen', 2, false, false, '#3b82f6'),
          ('APROBADO_DESTINO',  'Aprobado por destino',3, false, false, '#3b82f6'),
          ('APROBADO',          'Aprobado',           4, false, false, '#10b981'),
          ('EJECUTADO',         'Ejecutado',          5, false, true,  '#059669'),
          ('RECHAZADO_ORIGEN',  'Rechazado por origen',6, false, true,  '#ef4444'),
          ('RECHAZADO_DESTINO', 'Rechazado por destino',7, false, true, '#ef4444'),
          ('CANCELADO',         'Cancelado',          8, false, true,  '#94a3b8')
        ) AS t(codigo, nombre, orden, es_inicial, es_final, color)
        WHERE NOT EXISTS (SELECT 1 FROM estados_traslado WHERE estados_traslado.codigo = t.codigo)
    """)


def downgrade() -> None:
    op.drop_constraint('solicitudes_traslado_motivo_traslado_id_fkey',
                       'solicitudes_traslado', type_='foreignkey')
    op.drop_index('ix_solicitudes_traslado_motivo_traslado_id',
                  table_name='solicitudes_traslado')
    op.drop_column('solicitudes_traslado', 'motivo_traslado_id')
    op.drop_table('estados_traslado')
    op.drop_table('motivos_traslado')
