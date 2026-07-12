"""Unifica el órgano: secretaría deja de usar strings y apunta al catálogo real.

Fase 1 del plan de secretaría (ver GOBERNANZA.md):

- `sec_tipos_reunion.organo` (string libre `ASAMBLEA_GENERAL|JUNTA_DIRECTIVA|COMISION`)
  → `tipo_organo_id` FK a `tipos_organo`. Siembra el tipo «Comisión», que no existía.
- `sec_reuniones.organo_id` → FK a `organos`: el órgano CONCRETO que se reúne y adopta
  los acuerdos.
- `flujos_aprobacion`: el aprobador deja de ser un ROL y pasa a ser POLIMÓRFICO —
  órgano colegiado (`tipo_organo_aprobador_id`) o cargo individual (`cargo_aprobador_id`),
  con XOR. Un rol es un haz de permisos, no un sujeto que decide.

Revision ID: sec1org2unif3
Revises: niv1org2mod3
Create Date: 2026-07-12 00:00:00.000000
"""

import uuid

from alembic import op
import sqlalchemy as sa

revision: str = 'sec1org2unif3'
down_revision: str = 'niv1org2mod3'
branch_labels = None
depends_on = None

# Tipo de órgano «Comisión»: el string COMISION de secretaría no tenía contrapartida.
TIPO_COMISION_ID = uuid.UUID('00000000-0000-0000-0000-0000000a0002')

# Mapeo del string legacy → nombre del tipo de órgano en `tipos_organo`.
MAPEO_ORGANO = {
    'ASAMBLEA_GENERAL': 'Asamblea general',
    'JUNTA_DIRECTIVA': 'Junta Directiva',
    'COMISION': 'Comisión',
}


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # ── 1) Tipo de órgano «Comisión» (idempotente) ──────────────────────────────
    ya = bind.execute(
        sa.text("SELECT 1 FROM tipos_organo WHERE nombre = 'Comisión'")
    ).first()
    if not ya:
        bind.execute(sa.text("""
            INSERT INTO tipos_organo
                (id, nombre, descripcion, denominacion_singular, denominacion_plural,
                 composicion, sistema, activo, eliminado)
            VALUES
                (:id, 'Comisión', 'Órgano de trabajo con composición por cargos.',
                 'comisión', 'comisiones',
                 CAST('CARGOS' AS composicion_organo), false, true, false)
        """), {'id': TIPO_COMISION_ID})

    # ── 2) sec_tipos_reunion.organo (string) → tipo_organo_id (FK) ──────────────
    cols_tr = {c['name'] for c in insp.get_columns('sec_tipos_reunion')}
    if 'tipo_organo_id' not in cols_tr:
        op.add_column('sec_tipos_reunion', sa.Column('tipo_organo_id', sa.Uuid(), nullable=True))

        # Traspasar el dato: cada string a su tipo de órgano.
        for legacy, nombre_tipo in MAPEO_ORGANO.items():
            bind.execute(sa.text("""
                UPDATE sec_tipos_reunion tr
                SET tipo_organo_id = (SELECT id FROM tipos_organo WHERE nombre = :nombre_tipo)
                WHERE tr.organo = :legacy
            """), {'legacy': legacy, 'nombre_tipo': nombre_tipo})

        # Cualquier fila sin mapear queda a la vista antes de imponer NOT NULL.
        huerfanas = bind.execute(sa.text(
            "SELECT count(*) FROM sec_tipos_reunion WHERE tipo_organo_id IS NULL"
        )).scalar()
        if huerfanas:
            raise RuntimeError(
                f"{huerfanas} tipos de reunión sin tipo de órgano mapeado; revisa MAPEO_ORGANO"
            )

        op.alter_column('sec_tipos_reunion', 'tipo_organo_id', nullable=False)
        op.create_index('ix_sec_tipos_reunion_tipo_organo_id', 'sec_tipos_reunion', ['tipo_organo_id'])
        op.create_foreign_key(
            'fk_sec_tipos_reunion_tipo_organo', 'sec_tipos_reunion', 'tipos_organo',
            ['tipo_organo_id'], ['id'], ondelete='RESTRICT',
        )

    if 'organo' in cols_tr:
        op.drop_column('sec_tipos_reunion', 'organo')

    # ── 3) sec_reuniones.organo_id → el órgano concreto que se reúne ────────────
    cols_r = {c['name'] for c in insp.get_columns('sec_reuniones')}
    if 'organo_id' not in cols_r:
        op.add_column('sec_reuniones', sa.Column('organo_id', sa.Uuid(), nullable=True))
        op.create_index('ix_sec_reuniones_organo_id', 'sec_reuniones', ['organo_id'])
        op.create_foreign_key(
            'fk_sec_reuniones_organo', 'sec_reuniones', 'organos',
            ['organo_id'], ['id'], ondelete='RESTRICT',
        )

    # ── 4) flujos_aprobacion: aprobador ROL → polimórfico (órgano | cargo) ──────
    cols_f = {c['name'] for c in insp.get_columns('flujos_aprobacion')}
    if 'tipo_organo_aprobador_id' not in cols_f:
        op.add_column('flujos_aprobacion', sa.Column('tipo_organo_aprobador_id', sa.Uuid(), nullable=True))
        op.create_index('ix_flujos_aprobacion_tipo_organo_aprobador_id', 'flujos_aprobacion', ['tipo_organo_aprobador_id'])
        op.create_foreign_key(
            'fk_flujos_aprobacion_tipo_organo', 'flujos_aprobacion', 'tipos_organo',
            ['tipo_organo_aprobador_id'], ['id'], ondelete='RESTRICT',
        )
    if 'cargo_aprobador_id' not in cols_f:
        op.add_column('flujos_aprobacion', sa.Column('cargo_aprobador_id', sa.Uuid(), nullable=True))
        op.create_index('ix_flujos_aprobacion_cargo_aprobador_id', 'flujos_aprobacion', ['cargo_aprobador_id'])
        op.create_foreign_key(
            'fk_flujos_aprobacion_cargo', 'flujos_aprobacion', 'cargos',
            ['cargo_aprobador_id'], ['id'], ondelete='RESTRICT',
        )

    # La tabla está vacía (0 filas): no hay dato de `rol_aprobador_id` que migrar.
    if 'rol_aprobador_id' in cols_f:
        op.drop_column('flujos_aprobacion', 'rol_aprobador_id')

    # XOR: exactamente un aprobador.
    existing_cks = {c['name'] for c in insp.get_check_constraints('flujos_aprobacion')}
    if 'ck_flujo_aprobador_organo_xor_cargo' not in existing_cks:
        op.create_check_constraint(
            'ck_flujo_aprobador_organo_xor_cargo', 'flujos_aprobacion',
            '(tipo_organo_aprobador_id IS NOT NULL) != (cargo_aprobador_id IS NOT NULL)',
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    cols_f = {c['name'] for c in insp.get_columns('flujos_aprobacion')}
    existing_cks = {c['name'] for c in insp.get_check_constraints('flujos_aprobacion')}
    if 'ck_flujo_aprobador_organo_xor_cargo' in existing_cks:
        op.drop_constraint('ck_flujo_aprobador_organo_xor_cargo', 'flujos_aprobacion', type_='check')
    if 'rol_aprobador_id' not in cols_f:
        op.add_column('flujos_aprobacion', sa.Column('rol_aprobador_id', sa.Uuid(), nullable=True))
    for col in ('tipo_organo_aprobador_id', 'cargo_aprobador_id'):
        if col in cols_f:
            op.drop_column('flujos_aprobacion', col)

    cols_r = {c['name'] for c in insp.get_columns('sec_reuniones')}
    if 'organo_id' in cols_r:
        op.drop_column('sec_reuniones', 'organo_id')

    cols_tr = {c['name'] for c in insp.get_columns('sec_tipos_reunion')}
    if 'organo' not in cols_tr:
        op.add_column('sec_tipos_reunion', sa.Column('organo', sa.String(50), nullable=True))
        inv = {v: k for k, v in MAPEO_ORGANO.items()}
        for nombre_tipo, legacy in inv.items():
            bind.execute(sa.text("""
                UPDATE sec_tipos_reunion tr SET organo = :legacy
                WHERE tr.tipo_organo_id = (SELECT id FROM tipos_organo WHERE nombre = :nombre_tipo)
            """), {'legacy': legacy, 'nombre_tipo': nombre_tipo})
    if 'tipo_organo_id' in cols_tr:
        op.drop_column('sec_tipos_reunion', 'tipo_organo_id')
