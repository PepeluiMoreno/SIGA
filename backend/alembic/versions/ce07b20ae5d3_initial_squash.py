"""Schema inicial completo generado desde los modelos actuales.

Revision ID: ce07b20ae5d3
Revises:
Create Date: 2026-05-13

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'ce07b20ae5d3'
down_revision: Union[str, None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    from app.core.database import Base
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    from app.core.database import Base
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
