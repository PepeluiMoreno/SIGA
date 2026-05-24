"""Chat interno: tabla de vínculo canales_chat (SIGA ↔ sala XMPP).

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-05-24 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'e1f2a3b4c5d6'
down_revision = 'd0e1f2a3b4c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'canales_chat',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('origen', sa.String(length=30), nullable=False),
        sa.Column('origen_id', sa.Uuid(), nullable=False),
        sa.Column('sala_jid', sa.String(length=300), nullable=False),
        sa.Column('nombre', sa.String(length=200), nullable=True),
        sa.Column('estado_sync', sa.String(length=20), nullable=False, server_default='PENDIENTE'),
        sa.Column('ultimo_sync', sa.DateTime(), nullable=True),
        sa.Column('ultimo_error', sa.Text(), nullable=True),
        sa.Column('fecha_archivado', sa.DateTime(), nullable=True),
        # Campos de auditoría heredados de BaseModel
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('creado_por_id', sa.Uuid(), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('origen', 'origen_id', name='uq_canal_origen'),
        sa.UniqueConstraint('sala_jid', name='uq_canal_sala_jid'),
    )
    op.create_index('ix_canales_chat_origen', 'canales_chat', ['origen'])
    op.create_index('ix_canales_chat_origen_id', 'canales_chat', ['origen_id'])
    op.create_index('ix_canales_chat_estado_sync', 'canales_chat', ['estado_sync'])
    op.create_index('ix_canal_origen', 'canales_chat', ['origen', 'origen_id'])


def downgrade() -> None:
    op.drop_index('ix_canal_origen', table_name='canales_chat')
    op.drop_index('ix_canales_chat_estado_sync', table_name='canales_chat')
    op.drop_index('ix_canales_chat_origen_id', table_name='canales_chat')
    op.drop_index('ix_canales_chat_origen', table_name='canales_chat')
    op.drop_table('canales_chat')
