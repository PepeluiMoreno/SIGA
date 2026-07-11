"""Órganos de gobierno: TipoOrgano + composición + Organo; migra juntas_directivas.

Crea el catálogo de tipos de órgano (``tipos_organo``), su composición-plantilla
por cargos (``tipos_organo_cargos``) y las instancias (``organos``). Generaliza la
antigua ``juntas_directivas``: siembra un tipo «Junta Directiva», traspasa sus
filas a ``organos`` con ese tipo, y elimina la tabla vieja.

Ver docs/arquitectura/GOBERNANZA.md.

Revision ID: org1gob2ana3
Revises: trasl1cat2est3
Create Date: 2026-07-11 00:00:00.000000
"""

import uuid

from alembic import op
import sqlalchemy as sa

revision: str = 'org1gob2ana3'
down_revision: str = 'trasl1cat2est3'
branch_labels = None
depends_on = None

NEW_TABLES = ['tipos_organo', 'tipos_organo_cargos', 'organos']

# Id estable del tipo «Junta Directiva» sembrado (para migrar juntas + idempotencia).
TIPO_JUNTA_ID = uuid.UUID('00000000-0000-0000-0000-0000000a0001')


def upgrade() -> None:
    from app.core.database import Base
    import app.models  # noqa: F401  (registra todos los modelos en Base.metadata)

    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 1) Tablas nuevas (checkfirst evita recrearlas si ya existen).
    Base.metadata.create_all(bind=bind, checkfirst=True, tables=[
        Base.metadata.tables[t] for t in NEW_TABLES if t in Base.metadata.tables
    ])

    # 2) Sembrar el tipo «Junta Directiva» (idempotente). `composicion` es un enum
    #    PostgreSQL, hay que castear el literal explícitamente.
    ya = bind.execute(
        sa.text("SELECT 1 FROM tipos_organo WHERE id = :id"), {"id": TIPO_JUNTA_ID}
    ).first()
    if not ya:
        bind.execute(sa.text("""
            INSERT INTO tipos_organo
                (id, nombre, descripcion, denominacion_singular, denominacion_plural,
                 composicion, sistema, activo, eliminado)
            VALUES
                (:id, :nombre, :descripcion, :den_s, :den_p,
                 CAST(:composicion AS composicion_organo), true, true, false)
        """), {
            'id': TIPO_JUNTA_ID,
            'nombre': 'Junta Directiva',
            'descripcion': 'Órgano ejecutivo de gobierno, compuesto por cargos.',
            'den_s': 'junta directiva',
            'den_p': 'juntas directivas',
            'composicion': 'CARGOS',
        })

    # 3) Migrar juntas_directivas → organos (solo si la tabla vieja existe).
    #    Solo columnas presentes en AMBAS tablas (juntas_directivas.activa → organos.activo).
    if insp.has_table('juntas_directivas'):
        bind.execute(sa.text("""
            INSERT INTO organos
                (id, tipo_organo_id, agrupacion_id, nombre, fecha_constitucion,
                 fecha_disolucion, activo, observaciones,
                 fecha_creacion, fecha_modificacion, fecha_eliminacion, eliminado,
                 creado_por_id, modificado_por_id)
            SELECT
                j.id, :tipo_id, j.agrupacion_id, j.nombre, j.fecha_constitucion,
                j.fecha_disolucion, j.activa, j.observaciones,
                j.fecha_creacion, j.fecha_modificacion, j.fecha_eliminacion, j.eliminado,
                j.creado_por_id, j.modificado_por_id
            FROM juntas_directivas j
            WHERE NOT EXISTS (SELECT 1 FROM organos o WHERE o.id = j.id)
        """), {"tipo_id": TIPO_JUNTA_ID})

        op.drop_table('juntas_directivas')


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Recrear juntas_directivas y devolver las instancias de tipo «Junta Directiva».
    if not insp.has_table('juntas_directivas'):
        op.create_table(
            'juntas_directivas',
            sa.Column('id', sa.Uuid(), primary_key=True),
            sa.Column('agrupacion_id', sa.Uuid(),
                      sa.ForeignKey('unidades_organizativas.id', ondelete='RESTRICT'), nullable=False),
            sa.Column('nombre', sa.String(255), nullable=False),
            sa.Column('fecha_constitucion', sa.Date(), nullable=False),
            sa.Column('fecha_disolucion', sa.Date(), nullable=True),
            sa.Column('activa', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('observaciones', sa.Text(), nullable=True),
            sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
            sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
            sa.Column('eliminado', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('es_inmutable', sa.Boolean(), nullable=False, server_default=sa.false()),
        )
        if insp.has_table('organos'):
            bind.execute(sa.text("""
                INSERT INTO juntas_directivas
                    (id, agrupacion_id, nombre, fecha_constitucion, fecha_disolucion,
                     activa, observaciones, fecha_creacion, fecha_modificacion, eliminado, es_inmutable)
                SELECT id, agrupacion_id, nombre, fecha_constitucion, fecha_disolucion,
                     activo, observaciones, fecha_creacion, fecha_modificacion, eliminado, es_inmutable
                FROM organos WHERE tipo_organo_id = :tipo_id
            """), {"tipo_id": TIPO_JUNTA_ID})

    for t in reversed(NEW_TABLES):
        if insp.has_table(t):
            op.drop_table(t)
