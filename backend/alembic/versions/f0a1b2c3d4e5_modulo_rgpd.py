"""Módulo transversal de Protección de Datos (RGPD / LOPDGDD).

Crea las 8 tablas del módulo:
- rgpd_encargados_tratamiento (art. 28)
- rgpd_actividades_tratamiento (RAT, art. 30)
- rgpd_actividades_encargados (N:M)
- rgpd_clausulas_informativas (art. 13/14)
- rgpd_consentimientos (art. 7)
- rgpd_solicitudes_derechos (ARSULIPO, art. 15-22)
- rgpd_brechas_seguridad (art. 33/34)
- rgpd_auditoria_accesos (art. 5.2, append-only)

Y siembra las claves rgpd.* en configuraciones.

Idempotente (IF NOT EXISTS / ON CONFLICT): seguro de aplicar en entornos
donde el SQL del lote 10 ya se aplicó manualmente (dev).

Importante: asyncpg no permite múltiples sentencias por `op.execute()`,
así que cada CREATE / INSERT va en su propia llamada.

Revision ID: f0a1b2c3d4e5
Revises: e1f2a3b4c5d6
Create Date: 2026-05-27 18:30:00.000000
"""
from alembic import op


revision = 'f0a1b2c3d4e5'
down_revision = 'e1f2a3b4c5d6'
branch_labels = None
depends_on = None


def _run(*statements: str) -> None:
    for s in statements:
        op.execute(s)


def upgrade() -> None:
    # ── Encargados del tratamiento (art. 28) ─────────────────────────────
    _run(
        """
        CREATE TABLE IF NOT EXISTS rgpd_encargados_tratamiento (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          nombre VARCHAR(200) NOT NULL,
          nif VARCHAR(30),
          servicio VARCHAR(300) NOT NULL,
          contacto_email VARCHAR(200),
          contacto_telefono VARCHAR(50),
          pais_alojamiento VARCHAR(100),
          transferencia_internacional BOOLEAN NOT NULL DEFAULT FALSE,
          contrato_firmado BOOLEAN NOT NULL DEFAULT FALSE,
          contrato_fecha DATE,
          contrato_documento_url VARCHAR(500),
          clausulas_tipo_aepd BOOLEAN NOT NULL DEFAULT FALSE,
          notas TEXT,
          activo BOOLEAN NOT NULL DEFAULT TRUE,
          fecha_creacion TIMESTAMP NOT NULL DEFAULT now(),
          fecha_modificacion TIMESTAMP,
          fecha_eliminacion TIMESTAMP,
          eliminado BOOLEAN NOT NULL DEFAULT FALSE,
          creado_por_id UUID REFERENCES usuarios(id),
          modificado_por_id UUID REFERENCES usuarios(id)
        )
        """,
        "CREATE INDEX IF NOT EXISTS ix_rgpd_encargados_nombre    ON rgpd_encargados_tratamiento(nombre)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_encargados_activo    ON rgpd_encargados_tratamiento(activo)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_encargados_eliminado ON rgpd_encargados_tratamiento(eliminado)",
    )

    # ── RAT (art. 30) ────────────────────────────────────────────────────
    _run(
        """
        CREATE TABLE IF NOT EXISTS rgpd_actividades_tratamiento (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          nombre VARCHAR(200) NOT NULL,
          descripcion TEXT,
          finalidad TEXT NOT NULL,
          base_juridica VARCHAR(40) NOT NULL,
          base_juridica_detalle TEXT,
          categorias_interesados TEXT,
          categorias_datos TEXT,
          datos_sensibles BOOLEAN NOT NULL DEFAULT FALSE,
          datos_sensibles_detalle TEXT,
          destinatarios_cesion TEXT,
          transferencias_internacionales BOOLEAN NOT NULL DEFAULT FALSE,
          transferencias_paises VARCHAR(300),
          transferencias_garantias TEXT,
          plazo_conservacion TEXT,
          medidas_seguridad TEXT,
          activa BOOLEAN NOT NULL DEFAULT TRUE,
          fecha_alta_actividad DATE,
          fecha_revision DATE,
          fecha_creacion TIMESTAMP NOT NULL DEFAULT now(),
          fecha_modificacion TIMESTAMP,
          fecha_eliminacion TIMESTAMP,
          eliminado BOOLEAN NOT NULL DEFAULT FALSE,
          creado_por_id UUID REFERENCES usuarios(id),
          modificado_por_id UUID REFERENCES usuarios(id)
        )
        """,
        "CREATE INDEX IF NOT EXISTS ix_rgpd_rat_nombre        ON rgpd_actividades_tratamiento(nombre)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_rat_base_juridica ON rgpd_actividades_tratamiento(base_juridica)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_rat_activa        ON rgpd_actividades_tratamiento(activa)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_rat_sensibles     ON rgpd_actividades_tratamiento(datos_sensibles)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_rat_eliminado     ON rgpd_actividades_tratamiento(eliminado)",
    )

    # ── Relación N:M actividades ↔ encargados ────────────────────────────
    _run(
        """
        CREATE TABLE IF NOT EXISTS rgpd_actividades_encargados (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          actividad_id UUID NOT NULL REFERENCES rgpd_actividades_tratamiento(id) ON DELETE CASCADE,
          encargado_id UUID NOT NULL REFERENCES rgpd_encargados_tratamiento(id) ON DELETE CASCADE,
          fecha_creacion TIMESTAMP NOT NULL DEFAULT now(),
          fecha_modificacion TIMESTAMP,
          fecha_eliminacion TIMESTAMP,
          eliminado BOOLEAN NOT NULL DEFAULT FALSE,
          creado_por_id UUID REFERENCES usuarios(id),
          modificado_por_id UUID REFERENCES usuarios(id),
          UNIQUE (actividad_id, encargado_id)
        )
        """,
        "CREATE INDEX IF NOT EXISTS ix_rgpd_actenc_actividad ON rgpd_actividades_encargados(actividad_id)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_actenc_encargado ON rgpd_actividades_encargados(encargado_id)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_actenc_eliminado ON rgpd_actividades_encargados(eliminado)",
    )

    # ── Cláusulas informativas (art. 13/14) ──────────────────────────────
    _run(
        """
        CREATE TABLE IF NOT EXISTS rgpd_clausulas_informativas (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          codigo VARCHAR(60) NOT NULL,
          version INTEGER NOT NULL DEFAULT 1,
          vigente BOOLEAN NOT NULL DEFAULT FALSE,
          fecha_vigencia_desde DATE,
          fecha_vigencia_hasta DATE,
          finalidad_corta VARCHAR(300) NOT NULL,
          texto TEXT NOT NULL,
          fecha_creacion TIMESTAMP NOT NULL DEFAULT now(),
          fecha_modificacion TIMESTAMP,
          fecha_eliminacion TIMESTAMP,
          eliminado BOOLEAN NOT NULL DEFAULT FALSE,
          creado_por_id UUID REFERENCES usuarios(id),
          modificado_por_id UUID REFERENCES usuarios(id),
          CONSTRAINT uq_clausulas_codigo_version UNIQUE (codigo, version)
        )
        """,
        "CREATE INDEX IF NOT EXISTS ix_rgpd_clausulas_codigo    ON rgpd_clausulas_informativas(codigo)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_clausulas_vigente   ON rgpd_clausulas_informativas(vigente)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_clausulas_eliminado ON rgpd_clausulas_informativas(eliminado)",
    )

    # ── Consentimientos (art. 7) ─────────────────────────────────────────
    _run(
        """
        CREATE TABLE IF NOT EXISTS rgpd_consentimientos (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          miembro_id UUID REFERENCES miembros(id) ON DELETE SET NULL,
          usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
          email_externo VARCHAR(200),
          nombre_externo VARCHAR(200),
          clausula_id UUID NOT NULL REFERENCES rgpd_clausulas_informativas(id),
          estado VARCHAR(20) NOT NULL DEFAULT 'OTORGADO',
          fecha_otorgamiento TIMESTAMP NOT NULL,
          fecha_retirada TIMESTAMP,
          canal VARCHAR(20) NOT NULL DEFAULT 'WEB',
          prueba TEXT,
          fecha_creacion TIMESTAMP NOT NULL DEFAULT now(),
          fecha_modificacion TIMESTAMP,
          fecha_eliminacion TIMESTAMP,
          eliminado BOOLEAN NOT NULL DEFAULT FALSE,
          creado_por_id UUID REFERENCES usuarios(id),
          modificado_por_id UUID REFERENCES usuarios(id)
        )
        """,
        "CREATE INDEX IF NOT EXISTS ix_rgpd_cons_miembro   ON rgpd_consentimientos(miembro_id)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_cons_usuario   ON rgpd_consentimientos(usuario_id)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_cons_email     ON rgpd_consentimientos(email_externo)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_cons_clausula  ON rgpd_consentimientos(clausula_id)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_cons_estado    ON rgpd_consentimientos(estado)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_cons_eliminado ON rgpd_consentimientos(eliminado)",
    )

    # ── Solicitudes de derechos ARSULIPO (art. 15-22) ────────────────────
    _run(
        """
        CREATE TABLE IF NOT EXISTS rgpd_solicitudes_derechos (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          codigo_interno VARCHAR(40) NOT NULL UNIQUE,
          tipo VARCHAR(40) NOT NULL,
          estado VARCHAR(20) NOT NULL DEFAULT 'PRESENTADA',
          miembro_id UUID REFERENCES miembros(id) ON DELETE SET NULL,
          usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
          nombre_solicitante VARCHAR(200) NOT NULL,
          documento_solicitante VARCHAR(40),
          email_solicitante VARCHAR(200),
          telefono_solicitante VARCHAR(50),
          canal_presentacion VARCHAR(30) NOT NULL DEFAULT 'EMAIL',
          fecha_presentacion DATE NOT NULL,
          fecha_limite_respuesta DATE NOT NULL,
          prorrogada BOOLEAN NOT NULL DEFAULT FALSE,
          fecha_limite_prorroga DATE,
          motivo_prorroga TEXT,
          descripcion_solicitud TEXT,
          fecha_resolucion TIMESTAMP,
          resolucion TEXT,
          documento_resolucion_url VARCHAR(500),
          tramitada_por_id UUID REFERENCES usuarios(id),
          fecha_creacion TIMESTAMP NOT NULL DEFAULT now(),
          fecha_modificacion TIMESTAMP,
          fecha_eliminacion TIMESTAMP,
          eliminado BOOLEAN NOT NULL DEFAULT FALSE,
          creado_por_id UUID REFERENCES usuarios(id),
          modificado_por_id UUID REFERENCES usuarios(id)
        )
        """,
        "CREATE INDEX IF NOT EXISTS ix_rgpd_sol_codigo    ON rgpd_solicitudes_derechos(codigo_interno)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_sol_tipo      ON rgpd_solicitudes_derechos(tipo)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_sol_estado    ON rgpd_solicitudes_derechos(estado)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_sol_miembro   ON rgpd_solicitudes_derechos(miembro_id)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_sol_usuario   ON rgpd_solicitudes_derechos(usuario_id)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_sol_eliminado ON rgpd_solicitudes_derechos(eliminado)",
    )

    # ── Brechas de seguridad (art. 33/34) ────────────────────────────────
    _run(
        """
        CREATE TABLE IF NOT EXISTS rgpd_brechas_seguridad (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          codigo_interno VARCHAR(40) NOT NULL UNIQUE,
          fecha_deteccion TIMESTAMP NOT NULL,
          fecha_ocurrencia DATE,
          descripcion TEXT NOT NULL,
          origen VARCHAR(40) NOT NULL,
          severidad VARCHAR(20) NOT NULL DEFAULT 'MEDIA',
          datos_afectados TEXT,
          personas_afectadas_num INTEGER,
          datos_sensibles_afectados BOOLEAN NOT NULL DEFAULT FALSE,
          medidas_inmediatas TEXT,
          medidas_correctivas TEXT,
          notificada_aepd BOOLEAN NOT NULL DEFAULT FALSE,
          fecha_notificacion_aepd TIMESTAMP,
          referencia_aepd VARCHAR(100),
          notificacion_aepd_documento_url VARCHAR(500),
          motivo_no_notificacion TEXT,
          comunicada_interesados BOOLEAN NOT NULL DEFAULT FALSE,
          fecha_comunicacion_interesados TIMESTAMP,
          medio_comunicacion_interesados VARCHAR(200),
          cerrada BOOLEAN NOT NULL DEFAULT FALSE,
          fecha_cierre TIMESTAMP,
          detectada_por_id UUID REFERENCES usuarios(id),
          responsable_gestion_id UUID REFERENCES usuarios(id),
          fecha_creacion TIMESTAMP NOT NULL DEFAULT now(),
          fecha_modificacion TIMESTAMP,
          fecha_eliminacion TIMESTAMP,
          eliminado BOOLEAN NOT NULL DEFAULT FALSE,
          creado_por_id UUID REFERENCES usuarios(id),
          modificado_por_id UUID REFERENCES usuarios(id)
        )
        """,
        "CREATE INDEX IF NOT EXISTS ix_rgpd_bre_codigo     ON rgpd_brechas_seguridad(codigo_interno)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_bre_origen     ON rgpd_brechas_seguridad(origen)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_bre_severidad  ON rgpd_brechas_seguridad(severidad)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_bre_notif_aepd ON rgpd_brechas_seguridad(notificada_aepd)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_bre_cerrada    ON rgpd_brechas_seguridad(cerrada)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_bre_eliminado  ON rgpd_brechas_seguridad(eliminado)",
    )

    # ── Auditoría de accesos (art. 5.2, append-only) ─────────────────────
    _run(
        """
        CREATE TABLE IF NOT EXISTS rgpd_auditoria_accesos (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          fecha_acceso TIMESTAMP NOT NULL DEFAULT now(),
          usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
          usuario_email_snapshot VARCHAR(200),
          entidad VARCHAR(60) NOT NULL,
          entidad_id UUID,
          tipo_acceso VARCHAR(20) NOT NULL DEFAULT 'LECTURA',
          campos_accedidos TEXT,
          motivo VARCHAR(300),
          ip VARCHAR(45),
          user_agent VARCHAR(500),
          immutable_marker BOOLEAN NOT NULL DEFAULT TRUE
        )
        """,
        "CREATE INDEX IF NOT EXISTS ix_rgpd_audit_fecha      ON rgpd_auditoria_accesos(fecha_acceso)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_audit_usuario    ON rgpd_auditoria_accesos(usuario_id)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_audit_entidad    ON rgpd_auditoria_accesos(entidad)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_audit_entidad_id ON rgpd_auditoria_accesos(entidad_id)",
        "CREATE INDEX IF NOT EXISTS ix_rgpd_audit_tipo       ON rgpd_auditoria_accesos(tipo_acceso)",
    )

    # ── Claves de configuración rgpd.* (idempotente por clave única) ─────
    op.execute("""
        INSERT INTO configuraciones (id, clave, valor, tipo_dato, descripcion, modificable, grupo, orden) VALUES
          (gen_random_uuid(), 'rgpd.dpd_nombre',           '',     'string', 'Nombre del Delegado de Protección de Datos',                          TRUE, 'organizacion', 90),
          (gen_random_uuid(), 'rgpd.dpd_email',            '',     'string', 'Email del DPD',                                                       TRUE, 'organizacion', 91),
          (gen_random_uuid(), 'rgpd.dpd_telefono',         '',     'string', 'Teléfono del DPD',                                                    TRUE, 'organizacion', 92),
          (gen_random_uuid(), 'rgpd.dpd_externo',          'false','bool',   '¿El DPD es externo (proveedor)?',                                      TRUE, 'organizacion', 93),
          (gen_random_uuid(), 'rgpd.anios_retencion_baja', '6',    'int',    'Años a conservar datos tras baja antes de purga (LOPDGDD art. 32)',   TRUE, 'organizacion', 94)
        ON CONFLICT (clave) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM configuraciones WHERE clave IN (
          'rgpd.dpd_nombre', 'rgpd.dpd_email', 'rgpd.dpd_telefono',
          'rgpd.dpd_externo', 'rgpd.anios_retencion_baja'
        )
    """)
    for table in (
        'rgpd_auditoria_accesos',
        'rgpd_brechas_seguridad',
        'rgpd_solicitudes_derechos',
        'rgpd_consentimientos',
        'rgpd_clausulas_informativas',
        'rgpd_actividades_encargados',
        'rgpd_actividades_tratamiento',
        'rgpd_encargados_tratamiento',
    ):
        op.execute(f"DROP TABLE IF EXISTS {table}")
