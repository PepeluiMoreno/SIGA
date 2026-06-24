"""Reestructuración miembros → contactos + vinculaciones + satélites (PASO 1: esquema).

Crea las nuevas tablas sin tocar datos aún:
  - tipos_vinculacion (ampliado con codigo, ambito, area_responsable, requiere_satelite)
  - vinculaciones (el lazo typado y vigente persona↔org)
  - socios (satélite de socio, con datos económicos)
  - voluntarios (satélite de voluntario)
  - Modifica FIRMA_CAMPANIA: firmante_id → contacto_id (pero aún cuelga de miembros)

Revision ID: s4t5u6v7w8x9
Revises: f3d4e5f6a7b8
Create Date: 2026-06-24 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 's4t5u6v7w8x9'
# Rebasado sobre el head real de la línea principal (antes colgaba de
# q2r3s4t5u6v7/fase2, lo que dejaba dos heads). El refactor CRM debe aplicarse
# el último, tras secretaría/convenios/plataformas.
down_revision = 'f3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========== PASO 1: Extender tipos_vinculacion con campos de gobierno ==========
    # Si la tabla ya existe, añadir columnas. Si no, crearla.
    op.execute("""
        CREATE TABLE IF NOT EXISTS tipos_vinculacion (
            id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            nombre VARCHAR(150) NOT NULL UNIQUE,
            codigo VARCHAR(50) UNIQUE,
            ambito VARCHAR(20) DEFAULT 'central',
            area_responsable VARCHAR(200),
            requiere_satelite BOOLEAN DEFAULT FALSE,
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
            fecha_modificacion TIMESTAMP,
            fecha_eliminacion TIMESTAMP,
            eliminado BOOLEAN DEFAULT FALSE
        )
    """)
    # Si la tabla ya existía (catálogo `tipos_vinculacion` del módulo acceso, con
    # solo nombre/requiere_entidad/activo), añadir las columnas de gobierno nuevas
    # de forma idempotente para que el catálogo CRM las tenga.
    op.execute("ALTER TABLE tipos_vinculacion ADD COLUMN IF NOT EXISTS codigo VARCHAR(50)")
    op.execute("ALTER TABLE tipos_vinculacion ADD COLUMN IF NOT EXISTS ambito VARCHAR(20) DEFAULT 'central'")
    op.execute("ALTER TABLE tipos_vinculacion ADD COLUMN IF NOT EXISTS area_responsable VARCHAR(200)")
    op.execute("ALTER TABLE tipos_vinculacion ADD COLUMN IF NOT EXISTS requiere_satelite BOOLEAN DEFAULT FALSE")
    # La tabla preexistente del módulo acceso traía `requiere_entidad NOT NULL`
    # sin default; el catálogo CRM no lo usa. Se retira para no bloquear inserts.
    op.execute("ALTER TABLE tipos_vinculacion DROP COLUMN IF EXISTS requiere_entidad")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_tipos_vinculacion_codigo ON tipos_vinculacion(codigo)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tipos_vinculacion_codigo ON tipos_vinculacion(codigo)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tipos_vinculacion_ambito ON tipos_vinculacion(ambito)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tipos_vinculacion_activo ON tipos_vinculacion(activo)")

    # ========== PASO 2: Crear tabla vinculaciones ==========
    op.execute("""
        CREATE TABLE IF NOT EXISTS vinculaciones (
            id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            miembro_id UUID,
            tipo_vinculacion_id UUID NOT NULL REFERENCES tipos_vinculacion(id),
            fecha_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
            fecha_fin DATE,
            estado VARCHAR(50) DEFAULT 'activa',
            agrupacion_id UUID,
            fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
            fecha_modificacion TIMESTAMP,
            fecha_eliminacion TIMESTAMP,
            eliminado BOOLEAN DEFAULT FALSE,
            creado_por_id UUID,
            modificado_por_id UUID
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_vinculaciones_miembro_id ON vinculaciones(miembro_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vinculaciones_tipo ON vinculaciones(tipo_vinculacion_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vinculaciones_fecha_fin ON vinculaciones(fecha_fin)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vinculaciones_estado ON vinculaciones(estado)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_vinculacion_miembro_tipo ON vinculaciones(miembro_id, tipo_vinculacion_id) WHERE fecha_fin IS NULL AND eliminado = FALSE")

    # ========== PASO 3: Crear satélite socios ==========
    op.execute("""
        CREATE TABLE IF NOT EXISTS socios (
            id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            vinculacion_id UUID NOT NULL UNIQUE REFERENCES vinculaciones(id) ON DELETE CASCADE,
            numero_socio VARCHAR(50),
            cuota_mensual NUMERIC(12, 2),
            incremento_cuota NUMERIC(12, 2) DEFAULT 0,
            incremento_cuota_obs TEXT,
            iban VARCHAR(500),
            swift_bic VARCHAR(11),
            referencia_pago VARCHAR(200),
            forma_pago_id UUID,
            estado_socio VARCHAR(50) DEFAULT 'activo',
            es_honor BOOLEAN DEFAULT FALSE,
            motivo_reduccion_id UUID,
            motivo_baja_id UUID,
            motivo_baja_texto VARCHAR(500),
            fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
            fecha_modificacion TIMESTAMP,
            fecha_eliminacion TIMESTAMP,
            eliminado BOOLEAN DEFAULT FALSE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_socios_vinculacion_id ON socios(vinculacion_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_socios_numero ON socios(numero_socio)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_socios_estado ON socios(estado_socio)")

    # ========== PASO 4: Crear satélite voluntarios ==========
    op.execute("""
        CREATE TABLE IF NOT EXISTS voluntarios (
            id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            vinculacion_id UUID NOT NULL UNIQUE REFERENCES vinculaciones(id) ON DELETE CASCADE,
            disponibilidad VARCHAR(50),
            horas_disponibles_semana INTEGER,
            profesion VARCHAR(255),
            nivel_estudios_id UUID,
            experiencia_voluntariado VARCHAR(1000),
            intereses VARCHAR(1000),
            observaciones_voluntariado VARCHAR(1000),
            puede_conducir BOOLEAN DEFAULT FALSE,
            vehiculo_propio BOOLEAN DEFAULT FALSE,
            disponibilidad_viajar BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
            fecha_modificacion TIMESTAMP,
            fecha_eliminacion TIMESTAMP,
            eliminado BOOLEAN DEFAULT FALSE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_voluntarios_vinculacion_id ON voluntarios(vinculacion_id)")

    # ========== PASO 5: FIRMA_CAMPANIA: añadir contacto_id (copia de firmante_id) ==========
    # Sin FK todavía: `contactos` se crea en p2, que también re-apunta la FK.
    # firmante_id se eliminará en p2.
    op.execute("ALTER TABLE firmas_campania ADD COLUMN IF NOT EXISTS contacto_id UUID")
    op.execute("UPDATE firmas_campania SET contacto_id = firmante_id WHERE contacto_id IS NULL")
    op.execute("CREATE INDEX IF NOT EXISTS ix_firmas_campania_contacto_id ON firmas_campania(contacto_id)")


def downgrade() -> None:
    # Reversión en orden inverso
    op.drop_table('voluntarios', if_exists=True)
    op.drop_table('socios', if_exists=True)
    op.drop_table('vinculaciones', if_exists=True)
    op.drop_table('tipos_vinculacion', if_exists=True)

    # Revertir cambios en firmas_campania (idempotente)
    op.execute("DROP INDEX IF EXISTS ix_firmas_campania_contacto_id")
    op.execute("ALTER TABLE firmas_campania DROP COLUMN IF EXISTS contacto_id")
