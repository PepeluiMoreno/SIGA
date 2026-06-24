"""Reestructuración miembros → contactos + vinculaciones + satélites (PASO 2: datos).

Migración de datos en cascada:
  1. Insertar tipos_vinculacion base
  2. Copiar miembros → tabla temporal contactos_temp (preservando UUID)
  3. Crear vinculaciones de tipo socio/voluntario/simpatizante según miembros
  4. Copiar satélites (socios, voluntarios)
  5. Renombrar miembros → miembros_legacy, contactos_temp → contactos
  6. Redirigir todas las FKs de `miembros_id` a `contacto_id`
  7. Redirigir FKs económicas a `vinculacion_socio_id`
  8. Actualizar usuario.miembro_id → usuario.contacto_id
  9. Limpiar miembros_legacy (crear backup si es necesario)

Revision ID: t5u6v7w8x9y0
Revises: s4t5u6v7w8x9
Create Date: 2026-06-24 13:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 't5u6v7w8x9y0'
down_revision = 's4t5u6v7w8x9'
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    """¿Existe `table.column`? (el dialecto asyncpg no expone `has_column`)."""
    insp = sa.inspect(op.get_bind())
    return column in {c["name"] for c in insp.get_columns(table)}


def _drop_fks_on_column(table: str, column: str) -> None:
    """Elimina cualquier FK que restrinja `table.column`, sea cual sea su nombre.

    Robusto frente a las dos formas de crear el esquema base: por migraciones
    (nombres tipo `fk_...`) o por `create_all` (nombres `{tabla}_{col}_fkey`).
    """
    op.execute(f"""
        DO $$
        DECLARE r record;
        BEGIN
            FOR r IN
                SELECT con.conname
                FROM pg_constraint con
                JOIN pg_attribute a
                  ON a.attrelid = con.conrelid AND a.attnum = ANY(con.conkey)
                WHERE con.contype = 'f'
                  AND con.conrelid = '{table}'::regclass
                  AND a.attname = '{column}'
            LOOP
                EXECUTE format('ALTER TABLE {table} DROP CONSTRAINT %I', r.conname);
            END LOOP;
        END $$;
    """)


def upgrade() -> None:
    # ========== 1. Insertar tipos_vinculacion base ==========
    # id explícito con gen_random_uuid(): la tabla preexistente (catálogo de
    # acceso) no tiene server-default en `id` (el modelo usa default de Python).
    op.execute("""
        INSERT INTO tipos_vinculacion (id, nombre, codigo, ambito, area_responsable, requiere_satelite, activo)
        VALUES
            (gen_random_uuid(), 'Firmante', 'FIRMANTE', 'central', 'COMUNICACION_FIRMAS', FALSE, TRUE),
            (gen_random_uuid(), 'Simpatizante', 'SIMPATIZANTE', 'central', 'COMUNICACION_SIMPATIZANTES', FALSE, TRUE),
            (gen_random_uuid(), 'Socio', 'SOCIO', 'territorial', 'MEMBRESIA_SOCIO_GESTIONAR', TRUE, TRUE),
            (gen_random_uuid(), 'Voluntario', 'VOLUNTARIO', 'territorial', 'MEMBRESIA_VOLUNTARIO_GESTIONAR', TRUE, TRUE),
            (gen_random_uuid(), 'Donante', 'DONANTE', 'central', 'TESORERIA_DONANTES', FALSE, TRUE),
            (gen_random_uuid(), 'Empleado', 'EMPLEADO', 'central', 'RECURSOS_HUMANOS', TRUE, TRUE)
        ON CONFLICT (codigo) DO NOTHING
    """)

    # ========== 2. Copiar miembros → contactos_temp ==========
    op.execute("""
        CREATE TABLE contactos_temp AS
        SELECT
            id, nombre, apellido1, apellido2, sexo, fecha_nacimiento, pais_nacimiento_id,
            tipo_documento, numero_documento, pais_documento_id, direccion, codigo_postal,
            localidad, provincia_id, pais_domicilio_id, telefono, telefono2, email, agrupacion_id,
            profesion, nivel_estudios_id, foto_url, solicita_supresion_datos, fecha_solicitud_supresion,
            fecha_limite_retencion, datos_anonimizados, fecha_anonimizacion, activo,
            fecha_creacion, fecha_modificacion, fecha_eliminacion, eliminado, creado_por_id, modificado_por_id
        FROM miembros
    """)
    op.execute("ALTER TABLE contactos_temp ADD PRIMARY KEY (id)")

    # contactos_temp se creó copiando columnas de `miembros`; faltan las columnas
    # propias del modelo Contacto (discriminador + datos de persona jurídica).
    # Todos los miembros migrados son personas físicas.
    op.execute("ALTER TABLE contactos_temp ADD COLUMN tipo VARCHAR(20) NOT NULL DEFAULT 'PERSONA_FISICA'")
    op.execute("ALTER TABLE contactos_temp ADD COLUMN razon_social VARCHAR(255)")
    op.execute("ALTER TABLE contactos_temp ADD COLUMN cif VARCHAR(20)")
    op.execute("ALTER TABLE contactos_temp ADD COLUMN tipo_entidad_juridica_id UUID")
    op.execute("ALTER TABLE contactos_temp ADD COLUMN actividad_principal VARCHAR(500)")
    op.execute("ALTER TABLE contactos_temp ADD COLUMN representante_legal_id UUID")

    # ========== 3. Crear vinculaciones (TODAS ANTES de renombrar miembros) ==========
    
    # 3a. Simpatizantes
    op.execute("""
        INSERT INTO vinculaciones (miembro_id, tipo_vinculacion_id, fecha_inicio, estado, agrupacion_id, fecha_creacion, creado_por_id)
        SELECT m.id, tv.id, COALESCE(m.fecha_alta, CURRENT_DATE),
               CASE WHEN m.fecha_baja IS NOT NULL THEN 'cerrada'
                    WHEN m.activo = FALSE THEN 'inactiva' ELSE 'activa' END,
               m.agrupacion_id, COALESCE(m.fecha_creacion, NOW()), m.creado_por_id
        FROM miembros m
        JOIN tipos_miembro tm ON m.tipo_miembro_id = tm.id AND tm.nombre = 'Simpatizante'
        JOIN tipos_vinculacion tv ON tv.codigo = 'SIMPATIZANTE'
    """)
    # NOTA: tipos_miembro y estados_miembro NO tienen columna `codigo`; se
    # identifican por `nombre`. Verificar que los nombres canónicos del despliegue
    # real coinciden ('Simpatizante', 'Alta', 'Suspendido') antes de aplicar.

    # 3b. Socios (NO simpatizantes)
    op.execute("""
        INSERT INTO vinculaciones (miembro_id, tipo_vinculacion_id, fecha_inicio, fecha_fin, estado, agrupacion_id, fecha_creacion, creado_por_id)
        SELECT m.id, tv.id, m.fecha_alta, m.fecha_baja,
               CASE WHEN m.fecha_baja IS NOT NULL THEN 'cerrada'
                    WHEN em.nombre = 'Alta' THEN 'activa'
                    WHEN em.nombre = 'Suspendido' THEN 'inactiva' ELSE 'cerrada' END,
               m.agrupacion_id, COALESCE(m.fecha_creacion, NOW()), m.creado_por_id
        FROM miembros m
        LEFT JOIN tipos_miembro tm ON m.tipo_miembro_id = tm.id
        LEFT JOIN estados_miembro em ON m.estado_id = em.id
        JOIN tipos_vinculacion tv ON tv.codigo = 'SOCIO'
        WHERE tm.nombre IS NULL OR tm.nombre != 'Simpatizante'
    """)

    # 3c. Voluntarios
    op.execute("""
        INSERT INTO vinculaciones (miembro_id, tipo_vinculacion_id, fecha_inicio, estado, agrupacion_id, fecha_creacion, creado_por_id)
        SELECT DISTINCT m.id, tv.id, COALESCE(m.fecha_creacion::DATE, CURRENT_DATE),
               CASE WHEN m.activo = FALSE THEN 'inactiva' ELSE 'activa' END,
               m.agrupacion_id, COALESCE(m.fecha_creacion, NOW()), m.creado_por_id
        FROM miembros m
        JOIN tipos_vinculacion tv ON tv.codigo = 'VOLUNTARIO'
        WHERE m.es_voluntario = TRUE
    """)

    # ========== 4. Copiar satélites (ANTES de renombrar) ==========
    
    # Socios
    op.execute("""
        INSERT INTO socios (vinculacion_id, numero_socio, cuota_mensual, incremento_cuota, incremento_cuota_obs,
                           iban, swift_bic, referencia_pago, forma_pago_id, estado_socio, es_honor,
                           motivo_reduccion_id, motivo_baja_id, motivo_baja_texto, fecha_creacion, fecha_modificacion)
        SELECT v.id, NULL, NULL, m.incremento_cuota, m.incremento_cuota_obs, m.iban, m.swift_bic, m.referencia_pago,
               m.forma_pago_id, CASE WHEN m.fecha_baja IS NOT NULL THEN 'baja'
                                     WHEN em.nombre = 'Alta' THEN 'activo'
                                     WHEN em.nombre = 'Suspendido' THEN 'suspendido' ELSE 'baja' END,
               m.es_socio_honor, m.motivo_reduccion_id, m.motivo_baja_id, m.motivo_baja_texto,
               COALESCE(m.fecha_creacion, NOW()), m.fecha_modificacion
        FROM miembros m
        JOIN vinculaciones v ON v.miembro_id = m.id
        JOIN tipos_vinculacion tv ON v.tipo_vinculacion_id = tv.id AND tv.codigo = 'SOCIO'
        LEFT JOIN estados_miembro em ON m.estado_id = em.id
    """)

    # Voluntarios
    op.execute("""
        INSERT INTO voluntarios (vinculacion_id, disponibilidad, horas_disponibles_semana, profesion,
                                nivel_estudios_id, experiencia_voluntariado, intereses, observaciones_voluntariado,
                                puede_conducir, vehiculo_propio, disponibilidad_viajar, fecha_creacion, fecha_modificacion)
        SELECT v.id, m.disponibilidad, m.horas_disponibles_semana, m.profesion, m.nivel_estudios_id,
               m.experiencia_voluntariado, m.intereses, m.observaciones_voluntariado,
               m.puede_conducir, m.vehiculo_propio, m.disponibilidad_viajar,
               COALESCE(m.fecha_creacion, NOW()), m.fecha_modificacion
        FROM miembros m
        JOIN vinculaciones v ON v.miembro_id = m.id
        JOIN tipos_vinculacion tv ON v.tipo_vinculacion_id = tv.id AND tv.codigo = 'VOLUNTARIO'
        WHERE m.es_voluntario = TRUE
    """)

    # ========== 5. Renombrar miembros → miembros_legacy y activar contactos ==========
    op.execute("ALTER TABLE miembros RENAME TO miembros_legacy")
    op.execute("ALTER TABLE contactos_temp RENAME TO contactos")

    # ========== 6. Redirigir vinculaciones: miembro_id → contacto_id ==========
    op.execute("ALTER TABLE vinculaciones RENAME COLUMN miembro_id TO contacto_id")
    op.execute("ALTER TABLE vinculaciones DROP CONSTRAINT IF EXISTS fk_vinculaciones_miembro")
    op.execute("""
        ALTER TABLE vinculaciones
        ADD CONSTRAINT fk_vinculaciones_contacto
        FOREIGN KEY (contacto_id) REFERENCES contactos(id) ON DELETE RESTRICT
    """)

    # ========== 7. Redirigir usuario.miembro_id → usuario.contacto_id ==========
    # Quitar primero la FK vieja (apunta a miembros, que pasará a miembros_legacy)
    # sea cual sea su nombre, luego renombrar la columna y enlazar a contactos.
    _drop_fks_on_column('usuarios', 'miembro_id')
    op.execute("ALTER TABLE usuarios RENAME COLUMN miembro_id TO contacto_id")
    op.execute("""
        ALTER TABLE usuarios
        ADD CONSTRAINT fk_usuarios_contacto
        FOREIGN KEY (contacto_id) REFERENCES contactos(id) ON DELETE SET NULL
    """)

    # ========== 8. Redirigir FKs económicas: miembro_id → vinculacion_socio_id ==========
    fk_economicas = ['cuotas_anuales', 'pagos', 'recibos', 'suscripciones']
    for tabla in fk_economicas:
        if _has_column(tabla, 'miembro_id'):
            op.add_column(tabla, sa.Column('vinculacion_socio_id', sa.Uuid(), nullable=True))
            op.execute(f"""
                UPDATE {tabla} t
                SET vinculacion_socio_id = v.id
                FROM vinculaciones v
                WHERE t.miembro_id = v.contacto_id
                  AND v.tipo_vinculacion_id = (SELECT id FROM tipos_vinculacion WHERE codigo = 'SOCIO')
            """)
            op.create_foreign_key(
                f'fk_{tabla}_vinculacion_socio',
                tabla, 'vinculaciones',
                ['vinculacion_socio_id'], ['id']
            )
            # Quitar la FK vieja sobre miembro_id (nombre variable) y la columna.
            _drop_fks_on_column(tabla, 'miembro_id')
            op.drop_column(tabla, 'miembro_id')

    # ========== 9. firmas_campania: fijar contacto_id, FK a contactos, soltar firmante_id ==========
    op.execute("UPDATE firmas_campania SET contacto_id = COALESCE(contacto_id, firmante_id)")
    # Soltar cualquier FK previa sobre firmante_id/contacto_id y la columna vieja.
    _drop_fks_on_column('firmas_campania', 'firmante_id')
    _drop_fks_on_column('firmas_campania', 'contacto_id')
    op.drop_column('firmas_campania', 'firmante_id')
    op.create_foreign_key(
        'fk_firmas_campania_contacto', 'firmas_campania', 'contactos',
        ['contacto_id'], ['id']
    )


def downgrade() -> None:
    # Reversión completa: restaurar todo
    op.execute("ALTER TABLE miembros_legacy RENAME TO miembros")
    op.execute("ALTER TABLE contactos RENAME TO contactos_temp")
    
    # Revertir cambios en usuarios
    op.execute("ALTER TABLE usuarios RENAME COLUMN contacto_id TO miembro_id")
    op.execute("""
        ALTER TABLE usuarios
        DROP CONSTRAINT IF EXISTS fk_usuarios_contacto,
        ADD CONSTRAINT fk_usuarios_miembro
        FOREIGN KEY (miembro_id) REFERENCES miembros(id) ON DELETE SET NULL
    """)
    
    # Revertir vinculaciones
    op.execute("ALTER TABLE vinculaciones RENAME COLUMN contacto_id TO miembro_id")
    op.execute("ALTER TABLE vinculaciones DROP CONSTRAINT IF EXISTS fk_vinculaciones_contacto")
    op.execute("""
        ALTER TABLE vinculaciones
        ADD CONSTRAINT fk_vinculaciones_miembro
        FOREIGN KEY (miembro_id) REFERENCES miembros(id)
    """)
    
    # Eliminar tablas
    op.drop_table('contactos_temp', if_exists=True)
    op.drop_table('socios', if_exists=True)
    op.drop_table('voluntarios', if_exists=True)
