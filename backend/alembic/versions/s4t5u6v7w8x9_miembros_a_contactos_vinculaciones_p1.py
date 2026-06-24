"""Reestructuración miembros → contactos + vinculaciones + satélites (PASO 1: esquema).

Crea las nuevas tablas sin tocar datos aún:
  - tipos_vinculacion (ampliado con codigo, ambito, area_responsable, requiere_satelite)
  - vinculaciones (el lazo typado y vigente persona↔org)
  - socios (satélite de socio, con datos económicos)
  - voluntarios (satélite de voluntario)
  - Modifica FIRMA_CAMPANIA: firmante_id → contacto_id (pero aún cuelga de miembros)

Revision ID: s4t5u6v7w8x9
Revises: q2r3s4t5u6v7
Create Date: 2026-06-24 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 's4t5u6v7w8x9'
down_revision = 'q2r3s4t5u6v7'
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

    # ========== PASO 5: Modificar FIRMA_CAMPANIA: cambiar firmante_id → contacto_id ==========
    # (Aún apuntará a miembros, lo rediremos después a contactos)
    if not op.get_bind().dialect.has_column('firmas_campania', 'contacto_id'):
        op.add_column('firmas_campania', sa.Column('contacto_id', sa.Uuid(), nullable=True))
        op.execute("UPDATE firmas_campania SET contacto_id = firmante_id")
        op.create_foreign_key(
            'fk_firmas_campania_contacto',
            'firmas_campania', 'miembros',
            ['contacto_id'], ['id']
        )
        op.create_index('ix_firmas_campania_contacto_id', 'firmas_campania', ['contacto_id'])
        # firmante_id se eliminará en el paso 2


def downgrade() -> None:
    # Reversión en orden inverso
    op.drop_table('voluntarios', if_exists=True)
    op.drop_table('socios', if_exists=True)
    op.drop_table('vinculaciones', if_exists=True)
    op.drop_table('tipos_vinculacion', if_exists=True)
    
    # Revertir cambios en firmas_campania
    if op.get_bind().dialect.has_column('firmas_campania', 'contacto_id'):
        op.drop_index('ix_firmas_campania_contacto_id', 'firmas_campania', if_exists=True)
        op.drop_constraint('fk_firmas_campania_contacto', 'firmas_campania', type_='foreignkey')
        op.drop_column('firmas_campania', 'contacto_id')
