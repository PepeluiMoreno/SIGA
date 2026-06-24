"""CRM paso 3: split de actividades.participaciones, base Participacion,
membresias y tipos_entidad_juridica; backfill de Membresia por socio.

Tras p1 (esquema) y p2 (datos miembros→contactos), faltan las tablas que en
greenfield crea `create_all` pero que en una BD migrada en sitio no existen.
Complicación: la tabla `participaciones` YA existe como la antigua tabla de
asistencias a actividades; hay que reconducirla a `asistencias_actividad` y crear
la nueva `participaciones` base. Además, por decisión funcional la cuota se calcula
por `TipoMiembro`, así que cada socio recibe una `Membresia` con su `tipo_miembro_id`.

Revision ID: u6v7w8x9y0z1
Revises: t5u6v7w8x9y0
Create Date: 2026-06-24 14:00:00.000000
"""
from alembic import op

revision = 'u6v7w8x9y0z1'
down_revision = 't5u6v7w8x9y0'
branch_labels = None
depends_on = None


_AUDIT = """
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_modificacion TIMESTAMP,
    fecha_eliminacion TIMESTAMP,
    eliminado BOOLEAN NOT NULL DEFAULT FALSE,
    creado_por_id UUID REFERENCES usuarios(id),
    modificado_por_id UUID REFERENCES usuarios(id)
"""


def upgrade() -> None:
    # ========== 1. tipos_entidad_juridica ==========
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS tipos_entidad_juridica (
            id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            nombre VARCHAR(150) NOT NULL UNIQUE,
            codigo VARCHAR(50) UNIQUE,
            descripcion TEXT,
            permite_convenios BOOLEAN NOT NULL DEFAULT TRUE,
            permite_jerarquia BOOLEAN NOT NULL DEFAULT FALSE,
            orden INTEGER NOT NULL DEFAULT 0,
            activo BOOLEAN NOT NULL DEFAULT TRUE,
            {_AUDIT}
        )
    """)

    # ========== 2. Split de la antigua `participaciones` (asistencias a actividad) ==========
    # 2a. La antigua tabla de asistencias se llamaba `participaciones`; pasa a
    #     `asistencias_actividad` para liberar el nombre para la base nueva.
    op.execute("ALTER TABLE participaciones RENAME TO asistencias_actividad")

    # 2b. Crear la base `participaciones` nueva.
    op.execute(f"""
        CREATE TABLE participaciones (
            id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            contacto_id UUID NOT NULL REFERENCES contactos(id) ON DELETE RESTRICT,
            tipo VARCHAR(50) NOT NULL,
            fecha TIMESTAMP NOT NULL DEFAULT NOW(),
            estado VARCHAR(50) NOT NULL DEFAULT 'registrada',
            {_AUDIT}
        )
    """)
    op.execute("CREATE INDEX ix_participaciones_contacto_id ON participaciones(contacto_id)")
    op.execute("CREATE INDEX ix_participaciones_tipo ON participaciones(tipo)")

    # 2c. Cada asistencia necesita un Contacto: socio (miembro_id) o externo
    #     (nombre_externo/email_externo → Contacto creado al vuelo).
    op.execute("ALTER TABLE asistencias_actividad ADD COLUMN _contacto_tmp UUID")
    op.execute("UPDATE asistencias_actividad SET _contacto_tmp = miembro_id WHERE miembro_id IS NOT NULL")
    op.execute("""
        DO $$
        DECLARE r record; cid uuid;
        BEGIN
            FOR r IN SELECT id, nombre_externo, email_externo
                     FROM asistencias_actividad WHERE miembro_id IS NULL LOOP
                cid := gen_random_uuid();
                INSERT INTO contactos (id, tipo, nombre, email, activo, eliminado,
                                       solicita_supresion_datos, datos_anonimizados, fecha_creacion)
                VALUES (cid, 'PERSONA_FISICA', COALESCE(NULLIF(r.nombre_externo, ''), 'Externo'),
                        r.email_externo, TRUE, FALSE, FALSE, FALSE, NOW());
                UPDATE asistencias_actividad SET _contacto_tmp = cid WHERE id = r.id;
            END LOOP;
        END $$;
    """)

    # 2d. Crear la Participacion (tipo ASISTENCIA) por cada asistencia y enlazarla.
    op.execute("ALTER TABLE asistencias_actividad ADD COLUMN participacion_id UUID")
    op.execute("""
        DO $$
        DECLARE r record; pid uuid;
        BEGIN
            FOR r IN SELECT id, _contacto_tmp, fecha_creacion FROM asistencias_actividad LOOP
                pid := gen_random_uuid();
                INSERT INTO participaciones (id, contacto_id, tipo, fecha, estado, eliminado, fecha_creacion)
                VALUES (pid, r._contacto_tmp, 'ASISTENCIA', COALESCE(r.fecha_creacion, NOW()),
                        'registrada', FALSE, COALESCE(r.fecha_creacion, NOW()));
                UPDATE asistencias_actividad SET participacion_id = pid WHERE id = r.id;
            END LOOP;
        END $$;
    """)

    # 2e. Finalizar asistencias_actividad: FK + unique + NOT NULL; soltar lo viejo.
    op.execute("ALTER TABLE asistencias_actividad ALTER COLUMN participacion_id SET NOT NULL")
    op.execute("CREATE UNIQUE INDEX ux_asistencias_actividad_participacion ON asistencias_actividad(participacion_id)")
    op.execute("""
        ALTER TABLE asistencias_actividad
        ADD CONSTRAINT fk_asistencias_actividad_participacion
        FOREIGN KEY (participacion_id) REFERENCES participaciones(id) ON DELETE CASCADE
    """)
    op.execute("ALTER TABLE asistencias_actividad DROP COLUMN _contacto_tmp")
    op.execute("ALTER TABLE asistencias_actividad DROP COLUMN IF EXISTS miembro_id")
    op.execute("ALTER TABLE asistencias_actividad DROP COLUMN IF EXISTS nombre_externo")
    op.execute("ALTER TABLE asistencias_actividad DROP COLUMN IF EXISTS email_externo")

    # ========== 3. membresias (satélite) + backfill por socio ==========
    op.execute(f"""
        CREATE TABLE membresias (
            id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            participacion_id UUID NOT NULL UNIQUE REFERENCES participaciones(id) ON DELETE CASCADE,
            tipo_miembro_id UUID REFERENCES tipos_miembro(id),
            numero_socio VARCHAR(50) UNIQUE,
            {_AUDIT}
        )
    """)
    # Acto de alta (Participacion tipo MEMBRESIA) por cada vinculación SOCIO.
    op.execute("""
        INSERT INTO participaciones (id, contacto_id, tipo, fecha, estado, eliminado, fecha_creacion)
        SELECT gen_random_uuid(), v.contacto_id, 'MEMBRESIA',
               COALESCE(v.fecha_creacion, NOW()), 'registrada', FALSE, COALESCE(v.fecha_creacion, NOW())
        FROM vinculaciones v
        JOIN tipos_vinculacion tv ON v.tipo_vinculacion_id = tv.id AND tv.codigo = 'SOCIO'
    """)
    # tipo_miembro tomado de miembros_legacy (contacto.id == miembro.id).
    op.execute("""
        INSERT INTO membresias (id, participacion_id, tipo_miembro_id, eliminado, fecha_creacion)
        SELECT gen_random_uuid(), p.id, ml.tipo_miembro_id, FALSE, NOW()
        FROM participaciones p
        JOIN miembros_legacy ml ON ml.id = p.contacto_id
        WHERE p.tipo = 'MEMBRESIA'
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS membresias")
    op.execute("DELETE FROM participaciones WHERE tipo IN ('MEMBRESIA', 'ASISTENCIA')")
    # Revertir el split de asistencias (best-effort).
    op.execute("ALTER TABLE asistencias_actividad DROP CONSTRAINT IF EXISTS fk_asistencias_actividad_participacion")
    op.execute("ALTER TABLE asistencias_actividad DROP COLUMN IF EXISTS participacion_id")
    op.execute("DROP TABLE IF EXISTS participaciones")
    op.execute("ALTER TABLE asistencias_actividad RENAME TO participaciones")
    op.execute("DROP TABLE IF EXISTS tipos_entidad_juridica")
