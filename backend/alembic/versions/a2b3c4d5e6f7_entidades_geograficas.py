"""entidades_geograficas: jerarquía territorial única y recursiva.

Una sola tabla recursiva (padre_id) para toda la división territorial; el tipo
del nodo es un AmbitoGeografico (País/CCAA/Provincia/Municipio…). Se puebla desde
el recurso consolidado «Geografía jerárquica (INE)» de OpenDataManager.

Revision ID: a2b3c4d5e6f7
Revises: z1a2b3c4d5e6
Create Date: 2026-06-26 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a2b3c4d5e6f7'
down_revision = 'z1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'entidades_geograficas',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('codigo', sa.String(length=20), nullable=False),
        sa.Column('codigo_ine', sa.String(length=20), nullable=True),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.Column('ruta', sa.String(length=400), nullable=True),
        sa.Column('nivel', sa.Integer(), nullable=True),
        sa.Column('padre_id', sa.Uuid(), nullable=True),
        sa.Column('ambito_geografico_id', sa.Uuid(), nullable=True),
        sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
        # columnas de BaseModel/AuditoriaMixin (auditoría / soft-delete)
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('creado_por_id', sa.Uuid(), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['padre_id'], ['entidades_geograficas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ambito_geografico_id'], ['ambitos_geograficos.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('codigo', name='uq_entidad_geografica_codigo'),
    )
    op.create_index('ix_entidades_geograficas_codigo', 'entidades_geograficas', ['codigo'])
    op.create_index('ix_entidades_geograficas_codigo_ine', 'entidades_geograficas', ['codigo_ine'])
    op.create_index('ix_entidades_geograficas_nombre', 'entidades_geograficas', ['nombre'])
    op.create_index('ix_entidades_geograficas_padre_id', 'entidades_geograficas', ['padre_id'])
    op.create_index('ix_entidades_geograficas_ambito', 'entidades_geograficas', ['ambito_geografico_id'])
    op.create_index('ix_entidades_geograficas_eliminado', 'entidades_geograficas', ['eliminado'])


def downgrade() -> None:
    op.drop_table('entidades_geograficas')
