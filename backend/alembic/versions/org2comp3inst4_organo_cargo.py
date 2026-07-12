"""Composición por instancia de órgano: tabla organos_cargos.

La composición de un órgano concreto (la Junta de Madrid) se inicializa copiando
la plantilla de su tipo (`tipos_organo_cargos`), pero cada agrupación puede
ajustarla. Ver docs/arquitectura/GOBERNANZA.md.

Revision ID: org2comp3inst4
Revises: org1gob2ana3
Create Date: 2026-07-12 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision: str = 'org2comp3inst4'
down_revision: str = 'org1gob2ana3'
branch_labels = None
depends_on = None

NEW_TABLES = ['organos_cargos']


def upgrade() -> None:
    from app.core.database import Base
    import app.models  # noqa: F401  (registra todos los modelos en Base.metadata)

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True, tables=[
        Base.metadata.tables[t] for t in NEW_TABLES if t in Base.metadata.tables
    ])


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    for t in reversed(NEW_TABLES):
        if insp.has_table(t):
            op.drop_table(t)
