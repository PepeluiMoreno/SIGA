"""m040: índices únicos parciales para evitar participaciones duplicadas

- (accion_id, miembro_id) único cuando miembro_id IS NOT NULL
- (accion_id, email_externo) único cuando email_externo IS NOT NULL

Revision ID: m040
Revises: m039
Create Date: 2026-05-13
"""

from alembic import op

revision = 'm040'
down_revision = 'm039'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Limpieza: si ya hubiera duplicados en la BD (datos de prueba), conservar
    # la fila más antigua de cada combinación y borrar las demás.
    op.execute("""
        DELETE FROM participaciones p
        USING participaciones q
        WHERE p.accion_id = q.accion_id
          AND p.miembro_id = q.miembro_id
          AND p.miembro_id IS NOT NULL
          AND p.fecha_creacion > q.fecha_creacion
    """)
    op.execute("""
        DELETE FROM participaciones p
        USING participaciones q
        WHERE p.accion_id = q.accion_id
          AND p.email_externo = q.email_externo
          AND p.email_externo IS NOT NULL
          AND p.fecha_creacion > q.fecha_creacion
    """)

    op.execute("""
        CREATE UNIQUE INDEX uq_participacion_accion_miembro
        ON participaciones (accion_id, miembro_id)
        WHERE miembro_id IS NOT NULL
    """)
    op.execute("""
        CREATE UNIQUE INDEX uq_participacion_accion_email_externo
        ON participaciones (accion_id, email_externo)
        WHERE email_externo IS NOT NULL
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_participacion_accion_email_externo")
    op.execute("DROP INDEX IF EXISTS uq_participacion_accion_miembro")
