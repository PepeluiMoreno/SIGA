"""m039: alinear columnas de auditoría en tablas del módulo Acción con BaseModel

Las tablas creadas en m037 usaban created_at/updated_at en lugar de los
campos estándar de BaseModel (fecha_creacion, fecha_modificacion, eliminado, etc.)

Revision ID: m039
Revises: m038
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa

revision = 'm039'
down_revision = 'm038'
branch_labels = None
depends_on = None

TABLES = [
    'tipos_accion',
    'estados_accion',
    'acciones',
    'tareas',
    'participaciones',
    'grupo_iniciativa',
]


def upgrade() -> None:
    for table in TABLES:
        op.execute(f'ALTER TABLE {table} RENAME COLUMN created_at TO fecha_creacion')
        op.execute(f'ALTER TABLE {table} RENAME COLUMN updated_at TO fecha_modificacion')
        op.execute(f'ALTER TABLE {table} ALTER COLUMN fecha_modificacion DROP NOT NULL')

        op.add_column(table, sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True))
        op.add_column(table, sa.Column(
            'eliminado', sa.Boolean(), nullable=False,
            server_default='false',
        ))
        op.add_column(table, sa.Column('creado_por_id', sa.Uuid(), nullable=True))
        op.add_column(table, sa.Column('modificado_por_id', sa.Uuid(), nullable=True))

        op.create_foreign_key(
            f'fk_{table}_creado_por_id',
            table, 'usuarios',
            ['creado_por_id'], ['id'],
        )
        op.create_foreign_key(
            f'fk_{table}_modificado_por_id',
            table, 'usuarios',
            ['modificado_por_id'], ['id'],
        )
        op.create_index(f'ix_{table}_eliminado', table, ['eliminado'])


def downgrade() -> None:
    for table in TABLES:
        op.drop_index(f'ix_{table}_eliminado', table)
        op.drop_constraint(f'fk_{table}_modificado_por_id', table, type_='foreignkey')
        op.drop_constraint(f'fk_{table}_creado_por_id', table, type_='foreignkey')
        op.drop_column(table, 'modificado_por_id')
        op.drop_column(table, 'creado_por_id')
        op.drop_column(table, 'eliminado')
        op.drop_column(table, 'fecha_eliminacion')
        op.execute(f'ALTER TABLE {table} ALTER COLUMN fecha_modificacion SET NOT NULL')
        op.execute(f'ALTER TABLE {table} RENAME COLUMN fecha_modificacion TO updated_at')
        op.execute(f'ALTER TABLE {table} RENAME COLUMN fecha_creacion TO created_at')
