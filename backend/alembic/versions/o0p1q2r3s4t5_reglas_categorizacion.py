"""Reglas de categorización automática de apuntes por concepto.

Revision ID: o0p1q2r3s4t5
Revises: n9o0p1q2r3s4
Create Date: 2026-05-21 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'o0p1q2r3s4t5'
down_revision = 'n9o0p1q2r3s4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'reglas_categorizacion',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('patron', sa.String(200), nullable=False),
        sa.Column('tipo_coincidencia',
                  sa.Enum('CONTIENE', 'EMPIEZA_POR', 'EXACTO', 'REGEX', name='tipocoincidencia'),
                  nullable=False, server_default='CONTIENE'),
        sa.Column('tipo_apunte', sa.String(20), nullable=True),
        sa.Column('categoria_fiscal_id', sa.Uuid(), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('activa', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('creado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('es_inmutable', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['categoria_fiscal_id'], ['categorias_fiscales.id']),
    )
    op.create_index('ix_reglas_categorizacion_categoria', 'reglas_categorizacion', ['categoria_fiscal_id'])
    op.create_index('ix_reglas_categorizacion_tipo_apunte', 'reglas_categorizacion', ['tipo_apunte'])
    op.create_index('ix_reglas_categorizacion_activa', 'reglas_categorizacion', ['activa'])


def downgrade() -> None:
    op.drop_index('ix_reglas_categorizacion_activa', 'reglas_categorizacion')
    op.drop_index('ix_reglas_categorizacion_tipo_apunte', 'reglas_categorizacion')
    op.drop_index('ix_reglas_categorizacion_categoria', 'reglas_categorizacion')
    op.drop_table('reglas_categorizacion')
    sa.Enum(name='tipocoincidencia').drop(op.get_bind(), checkfirst=True)
