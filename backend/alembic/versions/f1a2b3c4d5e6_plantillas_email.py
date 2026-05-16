"""Añade tabla plantillas_email para catálogo de plantillas de correo.

Revision ID: f1a2b3c4d5e6
Revises: e7e5bec87533
Create Date: 2026-05-15 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision = 'f1a2b3c4d5e6'
down_revision = 'e7e5bec87533'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'plantillas_email',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('codigo', sa.String(50), unique=True, nullable=False),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('descripcion', sa.Text, nullable=True),
        sa.Column('modulo', sa.String(50), nullable=False),
        sa.Column('asunto', sa.String(300), nullable=False),
        sa.Column('cuerpo_html', sa.Text, nullable=False),
        sa.Column('variables_disponibles', JSON, nullable=True),
        sa.Column('activo', sa.Boolean, nullable=False, server_default='true'),
        # Campos de auditoría de BaseModel
        sa.Column('fecha_creacion', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('fecha_modificacion', sa.DateTime, nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime, nullable=True),
        sa.Column('eliminado', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('creado_por_id', UUID(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id', UUID(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=True),
    )
    op.create_index('ix_plantillas_email_codigo', 'plantillas_email', ['codigo'])
    op.create_index('ix_plantillas_email_modulo', 'plantillas_email', ['modulo'])
    op.create_index('ix_plantillas_email_activo', 'plantillas_email', ['activo'])
    op.create_index('ix_plantillas_email_eliminado', 'plantillas_email', ['eliminado'])


def downgrade() -> None:
    op.drop_index('ix_plantillas_email_eliminado', 'plantillas_email')
    op.drop_index('ix_plantillas_email_activo', 'plantillas_email')
    op.drop_index('ix_plantillas_email_modulo', 'plantillas_email')
    op.drop_index('ix_plantillas_email_codigo', 'plantillas_email')
    op.drop_table('plantillas_email')
