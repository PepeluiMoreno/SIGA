"""Add módulo financiero: tesorería y contabilidad completa

Revision ID: a9f1b2c3d4e5
Revises: f7cbe6981805
Create Date: 2026-05-16 10:00:00.000000

Crea las siguientes tablas:
  - cuentas_bancarias
  - apuntes_caja
  - extractos_bancarios
  - conciliaciones
  - conciliaciones_bancarias
  - cuentas_contables
  - asientos_contables
  - apuntes_contables
  - balances_contables
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect as sa_inspect

revision: str = 'a9f1b2c3d4e5'
down_revision: Union[str, None] = 'f7cbe6981805'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AUDIT_COLS = [
    sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
    sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('creado_por_id', sa.Uuid(), nullable=True),
    sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
]

AUDIT_FKS = [
    sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id']),
    sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id']),
]


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa_inspect(conn)
    existing = set(inspector.get_table_names())

    # ── cuentas_bancarias ──────────────────────────────────────────────────────
    if 'cuentas_bancarias' not in existing:
        op.create_table(
            'cuentas_bancarias',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('nombre', sa.String(200), nullable=False),
            sa.Column('iban', sa.String(500), nullable=False),
            sa.Column('bic_swift', sa.String(20), nullable=True),
            sa.Column('banco_nombre', sa.String(200), nullable=True),
            sa.Column('titular', sa.String(200), nullable=True),
            sa.Column('descripcion', sa.Text(), nullable=True),
            sa.Column('saldo_actual', sa.Numeric(14, 2), server_default='0.00', nullable=False),
            sa.Column('saldo_conciliado', sa.Numeric(14, 2), server_default='0.00', nullable=False),
            sa.Column('agrupacion_id', sa.Uuid(), nullable=True),
            sa.Column('activa', sa.Boolean(), server_default='true', nullable=False),
            *AUDIT_COLS,
            sa.ForeignKeyConstraint(['agrupacion_id'], ['unidades_organizativas.id']),
            *AUDIT_FKS,
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_cuentas_bancarias_iban', 'cuentas_bancarias', ['iban'], unique=True)
        op.create_index('ix_cuentas_bancarias_activa', 'cuentas_bancarias', ['activa'])
        op.create_index('ix_cuentas_bancarias_eliminado', 'cuentas_bancarias', ['eliminado'])

    # ── cuentas_contables ─────────────────────────────────────────────────────
    if 'cuentas_contables' not in existing:
        op.create_table(
            'cuentas_contables',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('codigo', sa.String(20), nullable=False),
            sa.Column('nombre', sa.String(200), nullable=False),
            sa.Column('descripcion', sa.Text(), nullable=True),
            sa.Column('tipo', sa.Enum(
                'ACTIVO', 'PASIVO', 'PATRIMONIO', 'INGRESO', 'GASTO',
                name='tipocuentacontable'
            ), nullable=False),
            sa.Column('nivel', sa.Integer(), nullable=False),
            sa.Column('padre_id', sa.Uuid(), nullable=True),
            sa.Column('permite_asiento', sa.Boolean(), server_default='false', nullable=False),
            sa.Column('es_dotacion', sa.Boolean(), server_default='false', nullable=False),
            sa.Column('activa', sa.Boolean(), server_default='true', nullable=False),
            *AUDIT_COLS,
            sa.ForeignKeyConstraint(['padre_id'], ['cuentas_contables.id']),
            *AUDIT_FKS,
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_cuentas_contables_codigo', 'cuentas_contables', ['codigo'], unique=True)
        op.create_index('ix_cuentas_contables_tipo', 'cuentas_contables', ['tipo'])
        op.create_index('ix_cuentas_contables_nivel', 'cuentas_contables', ['nivel'])
        op.create_index('ix_cuentas_contables_activa', 'cuentas_contables', ['activa'])
        op.create_index('ix_cuentas_contables_eliminado', 'cuentas_contables', ['eliminado'])

    # ── asientos_contables ────────────────────────────────────────────────────
    if 'asientos_contables' not in existing:
        op.create_table(
            'asientos_contables',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('ejercicio', sa.Integer(), nullable=False),
            sa.Column('numero_asiento', sa.Integer(), nullable=False),
            sa.Column('fecha', sa.Date(), nullable=False),
            sa.Column('glosa', sa.String(500), nullable=False),
            sa.Column('tipo_asiento', sa.Enum(
                'APERTURA', 'GESTION', 'REGULARIZACION', 'CIERRE',
                name='tipoasientocontable'
            ), nullable=False),
            sa.Column('estado', sa.Enum(
                'BORRADOR', 'CONFIRMADO', 'ANULADO',
                name='estadoasientocontable'
            ), server_default='BORRADOR', nullable=False),
            sa.Column('observaciones', sa.Text(), nullable=True),
            *AUDIT_COLS,
            *AUDIT_FKS,
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_asientos_contables_ejercicio', 'asientos_contables', ['ejercicio'])
        op.create_index('ix_asientos_contables_fecha', 'asientos_contables', ['fecha'])
        op.create_index('ix_asientos_contables_estado', 'asientos_contables', ['estado'])
        op.create_index('ix_asientos_contables_eliminado', 'asientos_contables', ['eliminado'])

    # ── apuntes_caja ──────────────────────────────────────────────────────────
    if 'apuntes_caja' not in existing:
        op.create_table(
            'apuntes_caja',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('cuenta_bancaria_id', sa.Uuid(), nullable=False),
            sa.Column('tipo', sa.Enum(
                'INGRESO', 'GASTO', 'TRANSFERENCIA',
                name='tipoapunte'
            ), nullable=False),
            sa.Column('origen', sa.Enum(
                'CUOTA', 'DONACION', 'REMESA', 'PAGO', 'MANUAL',
                name='origenapunte'
            ), nullable=True),
            sa.Column('entidad_origen_tipo', sa.String(50), nullable=True),
            sa.Column('entidad_origen_id', sa.Uuid(), nullable=True),
            sa.Column('importe', sa.Numeric(14, 2), nullable=False),
            sa.Column('fecha', sa.Date(), nullable=False),
            sa.Column('concepto', sa.String(500), nullable=False),
            sa.Column('referencia_externa', sa.String(200), nullable=True),
            sa.Column('conciliado', sa.Boolean(), server_default='false', nullable=False),
            sa.Column('fecha_conciliacion', sa.Date(), nullable=True),
            sa.Column('asiento_id', sa.Uuid(), nullable=True),
            sa.Column('observaciones', sa.Text(), nullable=True),
            *AUDIT_COLS,
            sa.ForeignKeyConstraint(['cuenta_bancaria_id'], ['cuentas_bancarias.id']),
            sa.ForeignKeyConstraint(['asiento_id'], ['asientos_contables.id']),
            *AUDIT_FKS,
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_apuntes_caja_cuenta_bancaria_id', 'apuntes_caja', ['cuenta_bancaria_id'])
        op.create_index('ix_apuntes_caja_fecha', 'apuntes_caja', ['fecha'])
        op.create_index('ix_apuntes_caja_tipo', 'apuntes_caja', ['tipo'])
        op.create_index('ix_apuntes_caja_conciliado', 'apuntes_caja', ['conciliado'])
        op.create_index('ix_apuntes_caja_eliminado', 'apuntes_caja', ['eliminado'])

    # ── extractos_bancarios ───────────────────────────────────────────────────
    if 'extractos_bancarios' not in existing:
        op.create_table(
            'extractos_bancarios',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('cuenta_bancaria_id', sa.Uuid(), nullable=False),
            sa.Column('fecha', sa.Date(), nullable=False),
            sa.Column('importe', sa.Numeric(14, 2), nullable=False),
            sa.Column('concepto', sa.String(500), nullable=True),
            sa.Column('referencia', sa.String(200), nullable=True),
            sa.Column('conciliado', sa.Boolean(), server_default='false', nullable=False),
            *AUDIT_COLS,
            sa.ForeignKeyConstraint(['cuenta_bancaria_id'], ['cuentas_bancarias.id']),
            *AUDIT_FKS,
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_extractos_bancarios_cuenta_bancaria_id', 'extractos_bancarios', ['cuenta_bancaria_id'])
        op.create_index('ix_extractos_bancarios_fecha', 'extractos_bancarios', ['fecha'])
        op.create_index('ix_extractos_bancarios_conciliado', 'extractos_bancarios', ['conciliado'])
        op.create_index('ix_extractos_bancarios_eliminado', 'extractos_bancarios', ['eliminado'])

    # ── conciliaciones (apunte ↔ extracto, línea a línea) ────────────────────
    if 'conciliaciones' not in existing:
        op.create_table(
            'conciliaciones',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('apunte_id', sa.Uuid(), nullable=False),
            sa.Column('extracto_id', sa.Uuid(), nullable=False),
            sa.Column('metodo', sa.Enum(
                'AUTOMATICO', 'MANUAL',
                name='metodoconciliacion'
            ), nullable=False),
            sa.Column('usuario_id', sa.Uuid(), nullable=True),
            *AUDIT_COLS,
            sa.ForeignKeyConstraint(['apunte_id'], ['apuntes_caja.id']),
            sa.ForeignKeyConstraint(['extracto_id'], ['extractos_bancarios.id']),
            sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id']),
            *AUDIT_FKS,
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_conciliaciones_apunte_id', 'conciliaciones', ['apunte_id'])
        op.create_index('ix_conciliaciones_extracto_id', 'conciliaciones', ['extracto_id'])
        op.create_index('ix_conciliaciones_eliminado', 'conciliaciones', ['eliminado'])

    # ── conciliaciones_bancarias (cierre de período) ──────────────────────────
    if 'conciliaciones_bancarias' not in existing:
        op.create_table(
            'conciliaciones_bancarias',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('cuenta_bancaria_id', sa.Uuid(), nullable=False),
            sa.Column('fecha_inicio', sa.Date(), nullable=False),
            sa.Column('fecha_fin', sa.Date(), nullable=False),
            sa.Column('saldo_inicial_extracto', sa.Numeric(14, 2), nullable=False),
            sa.Column('saldo_final_extracto', sa.Numeric(14, 2), nullable=False),
            sa.Column('saldo_inicial_sistema', sa.Numeric(14, 2), nullable=False),
            sa.Column('saldo_final_sistema', sa.Numeric(14, 2), nullable=False),
            sa.Column('diferencia', sa.Numeric(14, 2), server_default='0.00', nullable=False),
            sa.Column('conciliado', sa.Boolean(), server_default='false', nullable=False),
            sa.Column('fecha_conciliacion', sa.Date(), nullable=True),
            sa.Column('observaciones', sa.Text(), nullable=True),
            *AUDIT_COLS,
            sa.ForeignKeyConstraint(['cuenta_bancaria_id'], ['cuentas_bancarias.id']),
            *AUDIT_FKS,
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_conciliaciones_bancarias_cuenta_bancaria_id', 'conciliaciones_bancarias', ['cuenta_bancaria_id'])
        op.create_index('ix_conciliaciones_bancarias_conciliado', 'conciliaciones_bancarias', ['conciliado'])
        op.create_index('ix_conciliaciones_bancarias_eliminado', 'conciliaciones_bancarias', ['eliminado'])

    # ── apuntes_contables ─────────────────────────────────────────────────────
    if 'apuntes_contables' not in existing:
        op.create_table(
            'apuntes_contables',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('asiento_id', sa.Uuid(), nullable=False),
            sa.Column('cuenta_id', sa.Uuid(), nullable=False),
            sa.Column('debe', sa.Numeric(14, 2), server_default='0.00', nullable=False),
            sa.Column('haber', sa.Numeric(14, 2), server_default='0.00', nullable=False),
            sa.Column('concepto', sa.String(500), nullable=False),
            sa.Column('actividad_id', sa.Uuid(), nullable=True),
            sa.Column('observaciones', sa.Text(), nullable=True),
            *AUDIT_COLS,
            sa.ForeignKeyConstraint(['asiento_id'], ['asientos_contables.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['cuenta_id'], ['cuentas_contables.id']),
            sa.ForeignKeyConstraint(['actividad_id'], ['actividades.id']),
            *AUDIT_FKS,
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_apuntes_contables_asiento_id', 'apuntes_contables', ['asiento_id'])
        op.create_index('ix_apuntes_contables_cuenta_id', 'apuntes_contables', ['cuenta_id'])
        op.create_index('ix_apuntes_contables_eliminado', 'apuntes_contables', ['eliminado'])

    # ── balances_contables ────────────────────────────────────────────────────
    if 'balances_contables' not in existing:
        op.create_table(
            'balances_contables',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('ejercicio', sa.Integer(), nullable=False),
            sa.Column('fecha_generacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('total_debe', sa.Numeric(14, 2), server_default='0.00', nullable=False),
            sa.Column('total_haber', sa.Numeric(14, 2), server_default='0.00', nullable=False),
            sa.Column('observaciones', sa.Text(), nullable=True),
            *AUDIT_COLS,
            *AUDIT_FKS,
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_balances_contables_ejercicio', 'balances_contables', ['ejercicio'])
        op.create_index('ix_balances_contables_eliminado', 'balances_contables', ['eliminado'])


def downgrade() -> None:
    op.drop_table('balances_contables')
    op.drop_table('apuntes_contables')
    op.drop_table('conciliaciones_bancarias')
    op.drop_table('conciliaciones')
    op.drop_table('extractos_bancarios')
    op.drop_table('apuntes_caja')
    op.drop_table('asientos_contables')
    op.drop_table('cuentas_contables')
    op.drop_table('cuentas_bancarias')
    op.execute("DROP TYPE IF EXISTS tipoapunte")
    op.execute("DROP TYPE IF EXISTS origenapunte")
    op.execute("DROP TYPE IF EXISTS tipocuentacontable")
    op.execute("DROP TYPE IF EXISTS tipoasientocontable")
    op.execute("DROP TYPE IF EXISTS estadoasientocontable")
    op.execute("DROP TYPE IF EXISTS metodoconciliacion")
