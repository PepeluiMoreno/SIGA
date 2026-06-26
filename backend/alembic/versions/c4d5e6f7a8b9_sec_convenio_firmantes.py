"""sec_convenio_firmantes: firmantes de cada parte de un convenio (nombre/NIF/cargo).

Tabla hija de sec_convenios. Guarda, por convenio y por parte (ASOCIACION /
CONTRAPARTE), los firmantes con su nombre, NIF y cargo como instantánea del
momento de la firma (un convenio es un documento legal).

DDL idempotente (IF NOT EXISTS) por seguridad ante el estado concurrente del
historial de migraciones.

Revision ID: c4d5e6f7a8b9
Revises: a2b3c4d5e6f7
Create Date: 2026-06-26 00:00:00.000000
"""
from alembic import op

revision = 'c4d5e6f7a8b9'
down_revision = 'a2b3c4d5e6f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS sec_convenio_firmantes (
            id UUID PRIMARY KEY,
            convenio_id UUID NOT NULL REFERENCES sec_convenios(id) ON DELETE CASCADE,
            parte VARCHAR(20) NOT NULL,
            nombre VARCHAR(200) NOT NULL,
            nif VARCHAR(20),
            cargo VARCHAR(150),
            orden INTEGER NOT NULL DEFAULT 0,
            fecha_creacion TIMESTAMP NOT NULL DEFAULT now(),
            fecha_modificacion TIMESTAMP,
            fecha_eliminacion TIMESTAMP,
            eliminado BOOLEAN NOT NULL DEFAULT false,
            creado_por_id UUID REFERENCES usuarios(id),
            modificado_por_id UUID REFERENCES usuarios(id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_sec_convenio_firmantes_convenio_id ON sec_convenio_firmantes (convenio_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_sec_convenio_firmantes_eliminado ON sec_convenio_firmantes (eliminado)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS sec_convenio_firmantes")
