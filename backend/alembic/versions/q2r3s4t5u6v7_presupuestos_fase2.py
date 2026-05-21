"""Presupuestos Fase 2: modificaciones, inicial vs vigente, control de disponibilidad.

Revision ID: q2r3s4t5u6v7
Revises: p1q2r3s4t5u6
Create Date: 2026-05-22 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'q2r3s4t5u6v7'
down_revision = 'p1q2r3s4t5u6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Presupuesto inicial vs vigente
    op.add_column('partidas_presupuestarias', sa.Column(
        'importe_inicial', sa.Numeric(12, 2), nullable=False, server_default='0.00'
    ))
    # Inicializar el inicial con el vigente actual para presupuestos ya existentes
    op.execute("UPDATE partidas_presupuestarias SET importe_inicial = importe_presupuestado")

    # Control de disponibilidad opcional
    op.add_column('planificaciones_anuales', sa.Column(
        'control_disponibilidad', sa.Boolean(), nullable=False, server_default='false'
    ))

    # Tabla de modificaciones presupuestarias
    op.create_table(
        'modificaciones_presupuestarias',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('planificacion_id', sa.Uuid(), nullable=False),
        sa.Column('tipo', sa.Enum('TRANSFERENCIA', 'AMPLIACION', 'SUPLEMENTO',
                                  name='tipomodificacionpresupuestaria'), nullable=False),
        sa.Column('partida_destino_id', sa.Uuid(), nullable=False),
        sa.Column('partida_origen_id', sa.Uuid(), nullable=True),
        sa.Column('importe', sa.Numeric(12, 2), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('motivo', sa.Text(), nullable=False),
        sa.Column('registrada_por_id', sa.Uuid(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('creado_por_id', sa.Uuid(), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
        sa.Column('es_inmutable', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['planificacion_id'], ['planificaciones_anuales.id']),
        sa.ForeignKeyConstraint(['partida_destino_id'], ['partidas_presupuestarias.id']),
        sa.ForeignKeyConstraint(['partida_origen_id'], ['partidas_presupuestarias.id']),
        sa.ForeignKeyConstraint(['registrada_por_id'], ['usuarios.id']),
    )
    op.create_index('ix_modif_presup_planificacion', 'modificaciones_presupuestarias', ['planificacion_id'])
    op.create_index('ix_modif_presup_destino', 'modificaciones_presupuestarias', ['partida_destino_id'])


def downgrade() -> None:
    op.drop_index('ix_modif_presup_destino', 'modificaciones_presupuestarias')
    op.drop_index('ix_modif_presup_planificacion', 'modificaciones_presupuestarias')
    op.drop_table('modificaciones_presupuestarias')
    sa.Enum(name='tipomodificacionpresupuestaria').drop(op.get_bind(), checkfirst=True)
    op.drop_column('planificaciones_anuales', 'control_disponibilidad')
    op.drop_column('partidas_presupuestarias', 'importe_inicial')
