"""Integra reuniones de secretaría en la taxonomía de actividades.

Añade campos de clasificación y FK estructurales en TipoActividad y Reunion.
El mapeo a cuentas PCESFL se implementará en feature/reglas-contables-actividades.

Revision ID: m8n9o0p1q2r3
Revises: l7m8n9o0p1q2
Create Date: 2026-05-20 14:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'm8n9o0p1q2r3'
down_revision = 'l7m8n9o0p1q2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Campos de clasificación en tipos_accion ──────────────────────────────
    op.add_column('tipos_accion', sa.Column(
        'es_actividad_gobierno', sa.Boolean(),
        nullable=False, server_default='false',
        comment='True para actividades de secretaría y presidencia'
    ))
    op.add_column('tipos_accion', sa.Column(
        'tipo_reunion_secretaria_id', sa.Uuid(),
        sa.ForeignKey('sec_tipos_reunion.id'), nullable=True,
        comment='Vincula con el TipoReunion de secretaría que crea instancias de este tipo'
    ))
    op.create_index(
        'ix_tipos_accion_es_actividad_gobierno',
        'tipos_accion', ['es_actividad_gobierno']
    )

    # ── FK actividad_id en sec_reuniones ─────────────────────────────────────
    op.add_column('sec_reuniones', sa.Column(
        'actividad_id', sa.Uuid(),
        sa.ForeignKey('actividades.id'), nullable=True,
        comment='Actividad generada al convocar — para presupuesto y contabilidad'
    ))
    op.create_index('ix_sec_reuniones_actividad_id', 'sec_reuniones', ['actividad_id'])


def downgrade() -> None:
    op.drop_index('ix_sec_reuniones_actividad_id', 'sec_reuniones')
    op.drop_column('sec_reuniones', 'actividad_id')

    op.drop_index('ix_tipos_accion_es_actividad_gobierno', 'tipos_accion')
    op.drop_column('tipos_accion', 'tipo_reunion_secretaria_id')
    op.drop_column('tipos_accion', 'es_actividad_gobierno')
