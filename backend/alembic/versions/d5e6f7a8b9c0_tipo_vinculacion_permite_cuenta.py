"""tipos_vinculacion: permite_cuenta (qué vínculos pueden recibir cuenta de usuario).

Distingue qué tipos de vinculación con la organización habilitan a un contacto
para ser dotado de cuenta de usuario de la aplicación. Por defecto FALSE; se marca
TRUE en los vínculos que implican operar el sistema (socio, voluntario, contratado).

Revision ID: d5e6f7a8b9c0
Revises: a2b3c4d5e6f7
Create Date: 2026-06-26 00:00:00.000000
"""
from alembic import op

revision = 'd5e6f7a8b9c0'
# Reapuntado a la cabeza real existente: el down_revision original
# 'c4d5e6f7a8b9' referenciaba una migración inexistente en este árbol (cadena
# rota por trabajo concurrente). El esquema ya estaba aplicado (BD en d5e6f7a8b9c0).
down_revision = 'a2b3c4d5e6f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE tipos_vinculacion "
        "ADD COLUMN IF NOT EXISTS permite_cuenta BOOLEAN NOT NULL DEFAULT FALSE"
    )
    # Defaults de gobernanza: los vínculos que implican operar la aplicación
    # pueden recibir cuenta de usuario.
    op.execute(
        "UPDATE tipos_vinculacion SET permite_cuenta = TRUE "
        "WHERE codigo IN ('SOCIO', 'VOLUNTARIO', 'EMPLEADO')"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE tipos_vinculacion DROP COLUMN IF EXISTS permite_cuenta")
