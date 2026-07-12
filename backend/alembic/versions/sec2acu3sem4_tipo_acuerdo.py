"""Semántica del acuerdo: qué ES y qué efecto produce.

Fase 3 del plan de secretaría. Un acuerdo era solo texto libre: nadie podía saber
que «se nombra Tesorera a Ana» ES un nombramiento que debe generar un mandato.

- `sec_tipos_acuerdo`: catálogo (NOMBRAMIENTO, CESE, APROBACION_CUENTAS…), con
  `produce_efecto` para distinguir los ejecutables de los meramente declarativos.
- `sec_acuerdos.tipo_acuerdo_id` → FK al catálogo.
- `sec_acuerdos_nombramiento`: payload estructurado (a quién, qué cargo, qué
  agrupación, fechas) + `nombramiento_id`, que se rellena al ejecutarlo y cierra
  el círculo de trazabilidad.

Revision ID: sec2acu3sem4
Revises: sec1org2unif3
Create Date: 2026-07-12 00:00:00.000000
"""

import uuid

from alembic import op
import sqlalchemy as sa

revision: str = 'sec2acu3sem4'
down_revision: str = 'sec1org2unif3'
branch_labels = None
depends_on = None

NEW_TABLES = ['sec_tipos_acuerdo', 'sec_acuerdos_nombramiento']

# Catálogo por defecto. `produce_efecto=True` ⇒ la máquina puede ejecutarlo.
TIPOS_ACUERDO = [
    ('NOMBRAMIENTO',       'Nombramiento de cargo',      True,
     'Designa a una persona para un cargo. Al ejecutarse produce el mandato.', 1),
    ('CESE',               'Cese de cargo',              True,
     'Pone fin al mandato de una persona en un cargo.', 2),
    ('APROBACION_CUENTAS', 'Aprobación de cuentas',      False,
     'Aprueba las cuentas anuales del ejercicio.', 3),
    ('APROBACION_PRESUPUESTO', 'Aprobación de presupuesto', False,
     'Aprueba el presupuesto de un ejercicio o de una campaña.', 4),
    ('ADMISION_SOCIO',     'Admisión de socio',          False,
     'Resuelve una solicitud de alta.', 5),
    ('DECLARATIVO',        'Acuerdo declarativo',        False,
     'Acuerdo sin efecto automático (posicionamientos, informes…).', 6),
]


def upgrade() -> None:
    from app.core.database import Base
    import app.models  # noqa: F401  (registra todos los modelos en Base.metadata)

    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 1) Tablas nuevas.
    Base.metadata.create_all(bind=bind, checkfirst=True, tables=[
        Base.metadata.tables[t] for t in NEW_TABLES if t in Base.metadata.tables
    ])

    # 2) Sembrar el catálogo (idempotente por código).
    for codigo, nombre, produce_efecto, descripcion, orden in TIPOS_ACUERDO:
        ya = bind.execute(
            sa.text("SELECT 1 FROM sec_tipos_acuerdo WHERE codigo = :c"), {'c': codigo}
        ).first()
        if not ya:
            bind.execute(sa.text("""
                INSERT INTO sec_tipos_acuerdo
                    (id, codigo, nombre, descripcion, produce_efecto, activo, orden, eliminado)
                VALUES (:id, :codigo, :nombre, :descripcion, :produce_efecto, true, :orden, false)
            """), {
                'id': uuid.uuid4(), 'codigo': codigo, 'nombre': nombre,
                'descripcion': descripcion, 'produce_efecto': produce_efecto, 'orden': orden,
            })

    # 3) sec_acuerdos.tipo_acuerdo_id
    cols = {c['name'] for c in insp.get_columns('sec_acuerdos')}
    if 'tipo_acuerdo_id' not in cols:
        op.add_column('sec_acuerdos', sa.Column('tipo_acuerdo_id', sa.Uuid(), nullable=True))
        op.create_index('ix_sec_acuerdos_tipo_acuerdo_id', 'sec_acuerdos', ['tipo_acuerdo_id'])
        op.create_foreign_key(
            'fk_sec_acuerdos_tipo_acuerdo', 'sec_acuerdos', 'sec_tipos_acuerdo',
            ['tipo_acuerdo_id'], ['id'], ondelete='RESTRICT',
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    cols = {c['name'] for c in insp.get_columns('sec_acuerdos')}
    if 'tipo_acuerdo_id' in cols:
        op.drop_column('sec_acuerdos', 'tipo_acuerdo_id')

    for t in reversed(NEW_TABLES):
        if insp.has_table(t):
            op.drop_table(t)
