"""Catálogo de plataformas telemáticas para reuniones.

- Tabla sec_plataformas_telematicas con `campos_esquema` (JSON) por
  plataforma: cada producto define qué datos pide al usuario.
- Columnas en sec_reuniones: plataforma_telematica_id (FK) y
  datos_conexion_telematica (JSON con los valores).
- Seed inicial: Jitsi, Zoom, Google Meet, Microsoft Teams, Indico, Otra.

Idempotente. Cada sentencia en su propio op.execute() porque asyncpg no
acepta múltiples comandos por prepared statement. Para el seed, los
strings JSON contienen `:` que SQLAlchemy interpretaría como bindparams;
usamos op.get_bind().exec_driver_sql() para saltar el bind processing.

Revision ID: f2c3d4e5f6a7
Revises: f1b2c3d4e5f6
Create Date: 2026-05-27 18:32:00.000000
"""
from alembic import op


revision = 'f2c3d4e5f6a7'
down_revision = 'f1b2c3d4e5f6'
branch_labels = None
depends_on = None


def _q(value):
    """Serializa un string Python a literal SQL escapado; None → NULL."""
    if value is None:
        return "NULL"
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


_SEED = [
    ('JITSI', 'Jitsi Meet',
     'Servidor de videoconferencia abierto y autoalojable.',
     '📹', 10, 'https://meet.jit.si/',
     '[{"key":"sala","label":"Nombre de la sala","tipo":"text","requerido":true,"placeholder":"asamblea-2026"},'
     '{"key":"url","label":"URL completa","tipo":"url","requerido":false,"placeholder":"https://meet.jit.si/asamblea-2026"},'
     '{"key":"password","label":"Contraseña","tipo":"text","requerido":false}]',
     True),
    ('ZOOM', 'Zoom',
     'Plataforma comercial de videoconferencia.',
     '🟦', 20, 'https://zoom.us/j/',
     '[{"key":"url","label":"URL de la reunión","tipo":"url","requerido":true},'
     '{"key":"id_reunion","label":"ID de reunión","tipo":"text","requerido":false},'
     '{"key":"password","label":"Contraseña","tipo":"text","requerido":false}]',
     True),
    ('MEET', 'Google Meet',
     'Videoconferencia de Google Workspace.',
     '🟢', 30, 'https://meet.google.com/',
     '[{"key":"url","label":"URL de la reunión","tipo":"url","requerido":true,"placeholder":"https://meet.google.com/xxx-xxxx-xxx"}]',
     True),
    ('TEAMS', 'Microsoft Teams',
     'Videoconferencia de Microsoft 365.',
     '🟪', 40, 'https://teams.microsoft.com/',
     '[{"key":"url","label":"URL de la reunión","tipo":"url","requerido":true},'
     '{"key":"id_reunion","label":"ID de reunión","tipo":"text","requerido":false},'
     '{"key":"password","label":"Contraseña","tipo":"text","requerido":false}]',
     True),
    ('INDICO', 'Indico',
     'Plataforma de eventos académicos / activismo (CERN).',
     '🎯', 50, None,
     '[{"key":"url","label":"URL del evento Indico","tipo":"url","requerido":true},'
     '{"key":"sala","label":"ID del evento","tipo":"text","requerido":false}]',
     True),
    ('OTRA', 'Otra plataforma',
     'Plataforma personalizada — usa URL y notas libres.',
     '🔗', 99, None,
     '[{"key":"url","label":"URL de la reunión","tipo":"url","requerido":true},'
     '{"key":"nombre_plataforma","label":"Nombre de la plataforma","tipo":"text","requerido":false},'
     '{"key":"notas","label":"Notas de conexión","tipo":"text","requerido":false}]',
     False),
]


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS sec_plataformas_telematicas (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          codigo VARCHAR(40) UNIQUE NOT NULL,
          nombre VARCHAR(100) NOT NULL,
          descripcion TEXT,
          icono VARCHAR(100),
          activa BOOLEAN NOT NULL DEFAULT TRUE,
          orden INTEGER NOT NULL DEFAULT 0,
          url_base VARCHAR(300),
          campos_esquema TEXT,
          es_inmutable BOOLEAN NOT NULL DEFAULT FALSE,
          fecha_creacion TIMESTAMP NOT NULL DEFAULT now(),
          fecha_modificacion TIMESTAMP,
          fecha_eliminacion TIMESTAMP,
          eliminado BOOLEAN NOT NULL DEFAULT FALSE,
          creado_por_id UUID REFERENCES usuarios(id),
          modificado_por_id UUID REFERENCES usuarios(id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_sec_plat_telem_codigo ON sec_plataformas_telematicas(codigo)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_sec_plat_telem_activa ON sec_plataformas_telematicas(activa)")
    op.execute(
        "ALTER TABLE sec_reuniones "
        "ADD COLUMN IF NOT EXISTS plataforma_telematica_id UUID "
        "REFERENCES sec_plataformas_telematicas(id) ON DELETE SET NULL"
    )
    op.execute("ALTER TABLE sec_reuniones ADD COLUMN IF NOT EXISTS datos_conexion_telematica TEXT")
    op.execute("CREATE INDEX IF NOT EXISTS ix_sec_reuniones_plat_telem ON sec_reuniones(plataforma_telematica_id)")

    # Seed fila a fila. Usamos exec_driver_sql para saltar el bind processing
    # de SQLAlchemy — los strings JSON contienen `:` que sería confundido
    # con bindparams (p.ej. `"requerido":true`).
    bind = op.get_bind()
    for (codigo, nombre, descripcion, icono, orden, url_base,
         campos_esquema, es_inmutable) in _SEED:
        sql = (
            "INSERT INTO sec_plataformas_telematicas "
            "(id, codigo, nombre, descripcion, icono, orden, url_base, "
            " campos_esquema, es_inmutable) VALUES "
            f"(gen_random_uuid(), {_q(codigo)}, {_q(nombre)}, "
            f" {_q(descripcion)}, {_q(icono)}, {orden}, {_q(url_base)}, "
            f" {_q(campos_esquema)}, "
            f" {'TRUE' if es_inmutable else 'FALSE'}) "
            "ON CONFLICT (codigo) DO NOTHING"
        )
        bind.exec_driver_sql(sql)


def downgrade() -> None:
    op.execute("ALTER TABLE sec_reuniones DROP COLUMN IF EXISTS datos_conexion_telematica")
    op.execute("ALTER TABLE sec_reuniones DROP COLUMN IF EXISTS plataforma_telematica_id")
    op.execute("DROP TABLE IF EXISTS sec_plataformas_telematicas")
