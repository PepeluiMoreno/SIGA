"""Enlace directo CuotaAnual → ApunteCaja.

Añade cuota_id a apuntes_caja para trazar pagos directos/manuales de cuota
sin pasar por la referencia polimórfica genérica.
Los pagos via remesa siguen vinculados por OrdenCobro → Remesa → ApunteCaja.

Revision ID: s4t5u6v7w8x9
Revises: r3s4t5u6v7w8
Create Date: 2026-06-16 06:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 's4t5u6v7w8x9'
down_revision = 'r3s4t5u6v7w8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'apuntes_caja',
        sa.Column('cuota_id', sa.Uuid(), nullable=True),
    )
    op.create_index('ix_apuntes_caja_cuota_id', 'apuntes_caja', ['cuota_id'])
    op.create_foreign_key(
        'fk_apuntes_caja_cuota_id',
        'apuntes_caja', 'cuotas_anuales',
        ['cuota_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_apuntes_caja_cuota_id', 'apuntes_caja', type_='foreignkey')
    op.drop_index('ix_apuntes_caja_cuota_id', table_name='apuntes_caja')
    op.drop_column('apuntes_caja', 'cuota_id')
