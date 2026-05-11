"""Add plan_actividades JTI base table.

Crea la tabla raíz plan_actividades para Joined Table Inheritance.
Añade plan_id (FK única) a campanias y eventos.

Revision ID: m020
Revises: m019_add_temas_ui
Create Date: 2026-05-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'm020'
down_revision = 'm019'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Tabla base JTI ────────────────────────────────────────────────────────
    op.create_table(
        'plan_actividades',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo', sa.String(20), nullable=False),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('modalidad', sa.String(20), nullable=True),
        sa.Column('estado_plan', sa.String(20), nullable=False, server_default='planificado'),
        sa.Column('fecha_inicio', sa.Date(), nullable=True),
        sa.Column('fecha_fin', sa.Date(), nullable=True),
        sa.Column('responsable_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('agrupacion_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('presupuesto_asignado', sa.Numeric(12, 2), nullable=False, server_default='0.00'),
        # Auditoría
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('creado_por_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('modificado_por_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['responsable_id'], ['miembros.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['agrupacion_id'], ['agrupaciones_territoriales.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_id'], ['plan_actividades.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['usuarios.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_plan_actividades_tipo', 'plan_actividades', ['tipo'])
    op.create_index('ix_plan_actividades_nombre', 'plan_actividades', ['nombre'])
    op.create_index('ix_plan_actividades_fecha_inicio', 'plan_actividades', ['fecha_inicio'])
    op.create_index('ix_plan_actividades_fecha_fin', 'plan_actividades', ['fecha_fin'])
    op.create_index('ix_plan_actividades_eliminado', 'plan_actividades', ['eliminado'])
    op.create_index('ix_plan_actividades_responsable_id', 'plan_actividades', ['responsable_id'])
    op.create_index('ix_plan_actividades_agrupacion_id', 'plan_actividades', ['agrupacion_id'])
    op.create_index('ix_plan_actividades_parent_id', 'plan_actividades', ['parent_id'])

    # ── plan_id en campanias ──────────────────────────────────────────────────
    op.add_column('campanias',
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_unique_constraint('uq_campanias_plan_id', 'campanias', ['plan_id'])
    op.create_index('ix_campanias_plan_id', 'campanias', ['plan_id'])
    op.create_foreign_key(
        'fk_campanias_plan_id', 'campanias', 'plan_actividades',
        ['plan_id'], ['id'], ondelete='SET NULL',
    )

    # ── plan_id en eventos ────────────────────────────────────────────────────
    op.add_column('eventos',
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_unique_constraint('uq_eventos_plan_id', 'eventos', ['plan_id'])
    op.create_index('ix_eventos_plan_id', 'eventos', ['plan_id'])
    op.create_foreign_key(
        'fk_eventos_plan_id', 'eventos', 'plan_actividades',
        ['plan_id'], ['id'], ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_eventos_plan_id', 'eventos', type_='foreignkey')
    op.drop_index('ix_eventos_plan_id', table_name='eventos')
    op.drop_constraint('uq_eventos_plan_id', 'eventos', type_='unique')
    op.drop_column('eventos', 'plan_id')

    op.drop_constraint('fk_campanias_plan_id', 'campanias', type_='foreignkey')
    op.drop_index('ix_campanias_plan_id', table_name='campanias')
    op.drop_constraint('uq_campanias_plan_id', 'campanias', type_='unique')
    op.drop_column('campanias', 'plan_id')

    op.drop_index('ix_plan_actividades_parent_id', table_name='plan_actividades')
    op.drop_index('ix_plan_actividades_agrupacion_id', table_name='plan_actividades')
    op.drop_index('ix_plan_actividades_responsable_id', table_name='plan_actividades')
    op.drop_index('ix_plan_actividades_eliminado', table_name='plan_actividades')
    op.drop_index('ix_plan_actividades_fecha_fin', table_name='plan_actividades')
    op.drop_index('ix_plan_actividades_fecha_inicio', table_name='plan_actividades')
    op.drop_index('ix_plan_actividades_nombre', table_name='plan_actividades')
    op.drop_index('ix_plan_actividades_tipo', table_name='plan_actividades')
    op.drop_table('plan_actividades')
