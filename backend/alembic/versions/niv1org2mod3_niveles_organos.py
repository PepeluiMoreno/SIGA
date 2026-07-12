"""El modelo organizativo se configura por NIVEL, no por tipo de órgano.

La misma «Junta Directiva» se compone distinto en una Delegación que en un Grupo
Local, así que la plantilla de composición se muda del TIPO al NIVEL territorial:

- crea `niveles_organos`        (qué órganos tiene cada nivel)
- crea `niveles_organos_cargos` (composición de ese órgano en ese nivel)
- elimina `tipos_organo_cargos` (la plantilla global ya no tiene sentido)

Configuración = modelo por nivel. Poblamiento = `organos`/`organos_cargos` de cada
agrupación. Ver docs/arquitectura/GOBERNANZA.md.

Revision ID: niv1org2mod3
Revises: org2comp3inst4
Create Date: 2026-07-12 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision: str = 'niv1org2mod3'
down_revision: str = 'org2comp3inst4'
branch_labels = None
depends_on = None

NEW_TABLES = ['niveles_organos', 'niveles_organos_cargos']


def upgrade() -> None:
    from app.core.database import Base
    import app.models  # noqa: F401  (registra todos los modelos en Base.metadata)

    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 1) Tablas del modelo por nivel.
    Base.metadata.create_all(bind=bind, checkfirst=True, tables=[
        Base.metadata.tables[t] for t in NEW_TABLES if t in Base.metadata.tables
    ])

    # 2) La plantilla global por tipo desaparece (la composición es del nivel).
    #    No se migran datos: en dev solo había el tipo «Junta Directiva» sin cargos.
    if insp.has_table('tipos_organo_cargos'):
        op.drop_table('tipos_organo_cargos')


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table('tipos_organo_cargos'):
        op.create_table(
            'tipos_organo_cargos',
            sa.Column('id', sa.Uuid(), primary_key=True),
            sa.Column('tipo_organo_id', sa.Uuid(),
                      sa.ForeignKey('tipos_organo.id', ondelete='CASCADE'), nullable=False),
            sa.Column('cargo_id', sa.Uuid(),
                      sa.ForeignKey('cargos.id', ondelete='CASCADE'), nullable=False),
            sa.Column('orden_protocolario', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
            sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
            sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
            sa.Column('eliminado', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('creado_por_id', sa.Uuid(), nullable=True),
            sa.Column('modificado_por_id', sa.Uuid(), nullable=True),
        )

    for t in reversed(NEW_TABLES):
        if insp.has_table(t):
            op.drop_table(t)
