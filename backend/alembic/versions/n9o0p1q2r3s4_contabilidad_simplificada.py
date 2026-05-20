"""Contabilidad simplificada: categorías fiscales.

Crea la tabla categorias_fiscales (estructura de clasificación del modo
simplificado, equivalente al plan de cuentas del modo completo) y añade
categoria_fiscal_id a apuntes_caja.

Revision ID: n9o0p1q2r3s4
Revises: d36a6ce11db3
Create Date: 2026-05-21 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'n9o0p1q2r3s4'
down_revision = 'd36a6ce11db3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'categorias_fiscales',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('codigo', sa.String(30), nullable=False),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('tipo', sa.Enum('INGRESO', 'GASTO', name='tipocategoriafiscal'), nullable=False),
        sa.Column('computa_modelo_182', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('computa_modelo_347', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('casilla_modelo', sa.String(20), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('activa', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('creado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('es_inmutable', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo'),
    )
    op.create_index('ix_categorias_fiscales_codigo', 'categorias_fiscales', ['codigo'])
    op.create_index('ix_categorias_fiscales_tipo', 'categorias_fiscales', ['tipo'])
    op.create_index('ix_categorias_fiscales_activa', 'categorias_fiscales', ['activa'])

    op.add_column('apuntes_caja', sa.Column('categoria_fiscal_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_apuntes_caja_categoria_fiscal', 'apuntes_caja',
        'categorias_fiscales', ['categoria_fiscal_id'], ['id']
    )
    op.create_index('ix_apuntes_caja_categoria_fiscal_id', 'apuntes_caja', ['categoria_fiscal_id'])


def downgrade() -> None:
    op.drop_index('ix_apuntes_caja_categoria_fiscal_id', 'apuntes_caja')
    op.drop_constraint('fk_apuntes_caja_categoria_fiscal', 'apuntes_caja', type_='foreignkey')
    op.drop_column('apuntes_caja', 'categoria_fiscal_id')

    op.drop_index('ix_categorias_fiscales_activa', 'categorias_fiscales')
    op.drop_index('ix_categorias_fiscales_tipo', 'categorias_fiscales')
    op.drop_index('ix_categorias_fiscales_codigo', 'categorias_fiscales')
    op.drop_table('categorias_fiscales')
    sa.Enum(name='tipocategoriafiscal').drop(op.get_bind(), checkfirst=True)
