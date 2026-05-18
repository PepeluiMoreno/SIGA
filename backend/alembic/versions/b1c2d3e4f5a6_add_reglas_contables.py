"""Add reglas_contables y tablas cobro PayPal

Revision ID: b1c2d3e4f5a6
Revises: a9f1b2c3d4e5
Create Date: 2026-05-16 12:00:00.000000

Crea:
  - reglas_contables: mapeo configurable origen/tipo → cuentas PCESFL
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect as sa_inspect

revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = 'a9f1b2c3d4e5'
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

    # ── reglas_contables ──────────────────────────────────────────────────────
    if 'reglas_contables' not in existing:
        op.create_table(
            'reglas_contables',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('origen', sa.String(50), nullable=True),
            sa.Column('tipo_apunte', sa.String(50), nullable=False),
            sa.Column('cuenta_debe_codigo', sa.String(20), nullable=False),
            sa.Column('cuenta_haber_codigo', sa.String(20), nullable=False),
            sa.Column('descripcion', sa.Text(), nullable=True),
            sa.Column('orden', sa.Integer(), server_default='10', nullable=False),
            sa.Column('activa', sa.Boolean(), server_default='true', nullable=False),
            *AUDIT_COLS,
            *AUDIT_FKS,
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_reglas_contables_origen', 'reglas_contables', ['origen'])
        op.create_index('ix_reglas_contables_tipo_apunte', 'reglas_contables', ['tipo_apunte'])
        op.create_index('ix_reglas_contables_activa', 'reglas_contables', ['activa'])
        op.create_index('ix_reglas_contables_eliminado', 'reglas_contables', ['eliminado'])


def downgrade() -> None:
    op.drop_table('reglas_contables')
