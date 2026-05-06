"""add forma_pago and miembro forma_pago_id

Revision ID: c78cdbdbfc93
Revises: 9096dc619f8c
Create Date: 2026-05-06 11:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c78cdbdbfc93'
down_revision: Union[str, None] = '9096dc619f8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('formas_pago',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('codigo', sa.String(length=30), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('descripcion', sa.String(length=500), nullable=True),
    sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
    sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('creado_por_id', sa.Uuid(), nullable=True),
    sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_formas_pago_activo'), 'formas_pago', ['activo'], unique=False)
    op.create_index(op.f('ix_formas_pago_codigo'), 'formas_pago', ['codigo'], unique=True)
    op.add_column('miembros', sa.Column('forma_pago_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'miembros', 'formas_pago', ['forma_pago_id'], ['id'])
    op.create_index(op.f('ix_miembros_forma_pago_id'), 'miembros', ['forma_pago_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_miembros_forma_pago_id'), table_name='miembros')
    op.drop_constraint(None, 'miembros', type_='foreignkey')
    op.drop_column('miembros', 'forma_pago_id')
    op.drop_index(op.f('ix_formas_pago_codigo'), table_name='formas_pago')
    op.drop_index(op.f('ix_formas_pago_activo'), table_name='formas_pago')
    op.drop_table('formas_pago')
