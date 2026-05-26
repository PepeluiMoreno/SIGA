# SQL acumulado — pendiente de alembic upgrade

Aplicar cuando termine el lote. Instrucciones:
```
docker exec -it siga_dev_backend alembic upgrade head
docker restart siga_dev_backend
```

---

## Lote 1: APLICADO directamente — 2026-05-17

```sql
-- tareas — nuevas columnas
ALTER TABLE tareas
  ADD COLUMN IF NOT EXISTS habilidad_id UUID REFERENCES habilidades(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS nivel_habilidad_id UUID REFERENCES niveles_habilidad(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_tareas_habilidad_id ON tareas(habilidad_id);
CREATE INDEX IF NOT EXISTS ix_tareas_nivel_habilidad_id ON tareas(nivel_habilidad_id);

-- actividades — nuevas columnas
ALTER TABLE actividades
  ADD COLUMN IF NOT EXISTS duracion_horas NUMERIC(6,2),
  ADD COLUMN IF NOT EXISTS duracion_dias INTEGER,
  ADD COLUMN IF NOT EXISTS localidad VARCHAR(150),
  ADD COLUMN IF NOT EXISTS provincia VARCHAR(100);
```

> Aplicado directamente con docker exec siga_dev_db psql. Pendiente de reflejar
> en una migración Alembic formal para producción.

---

## Lote 2: Ámbito Geográfico — pendiente de aplicar

```sql
-- Catálogo de ámbitos geográficos (Nacional, CCAA, Provincia, Comarca, Municipio…)
CREATE TABLE IF NOT EXISTS ambitos_geograficos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(100) NOT NULL UNIQUE,
  descripcion TEXT,
  granularidad INTEGER NOT NULL DEFAULT 50,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en TIMESTAMPTZ DEFAULT now(),
  modificado_en TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_ambitos_geograficos_granularidad ON ambitos_geograficos(granularidad);
CREATE INDEX IF NOT EXISTS ix_ambitos_geograficos_activo ON ambitos_geograficos(activo);

-- Datos iniciales: ámbitos estándar para España
INSERT INTO ambitos_geograficos (nombre, descripcion, granularidad) VALUES
  ('Supranacional', 'Ámbito por encima del Estado (UE, internacional)', 5),
  ('Nacional',      'Ámbito estatal completo',                          10),
  ('CCAA',          'Comunidad Autónoma',                               20),
  ('Provincia',     'Provincia o territorio equivalente',               30),
  ('Comarca',       'Agrupación de municipios / comarca',               40),
  ('Municipio',     'Municipio o ciudad',                               50),
  ('Local',         'Barrio, distrito o entidad subnunicipal',          60)
ON CONFLICT (nombre) DO NOTHING;

-- FK en niveles_organizativos → ambitos_geograficos
ALTER TABLE niveles_organizativos
  ADD COLUMN IF NOT EXISTS ambito_geografico_id UUID
    REFERENCES ambitos_geograficos(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_niveles_organizativos_ambito_geografico_id
  ON niveles_organizativos(ambito_geografico_id);

-- Asignación inicial según los niveles ya existentes
-- (ajustar al nombre real de cada nivel si difiere)
UPDATE niveles_organizativos SET ambito_geografico_id = (
  SELECT id FROM ambitos_geograficos WHERE nombre = 'Nacional'
) WHERE nombre ILIKE '%sede central%' OR nivel = 1;

UPDATE niveles_organizativos SET ambito_geografico_id = (
  SELECT id FROM ambitos_geograficos WHERE nombre = 'CCAA'
) WHERE nombre ILIKE '%agrupaci%territorial%' OR nivel = 2;

UPDATE niveles_organizativos SET ambito_geografico_id = (
  SELECT id FROM ambitos_geograficos WHERE nombre = 'Provincia'
) WHERE nombre ILIKE '%grupo local%' OR nivel = 3;
```

> **Instrucciones**: ejecutar con `docker exec -it siga_dev_db psql -U siga -d siga`
> y después `docker restart siga_dev_backend`.

---

## Lote pendiente: Tesorería delegada por agrupación

```sql
-- Remesa vinculada a agrupación territorial (tesorería delegada)
ALTER TABLE remesas
  ADD COLUMN IF NOT EXISTS agrupacion_id UUID REFERENCES unidades_organizativas(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_remesas_agrupacion_id ON remesas(agrupacion_id);

-- OrigenApunte: añadir REMESA al enum PostgreSQL
-- (ya aplicado directamente via ALTER TYPE en 2026-05-18)
-- ALTER TYPE origenapunte ADD VALUE IF NOT EXISTS 'REMESA';
```

**Modelo Python a actualizar** cuando se migre:
- `Remesa`: añadir `agrupacion_id` FK + relationship `agrupacion`
- `RemesaCreateInput`: añadir campo `agrupacion_id`

**Lógica de tesorería delegada** (fase UI posterior):
- Al crear remesa, filtrar `CuotaAnual` por `agrupacion_id` de la cuenta bancaria seleccionada
- Permisos: rol `TESORERO_AGRUPACION` solo ve cuentas/remesas de su agrupacion_id
- Consolidado central: query remesas sin filtro de agrupacion (solo para SUPERADMIN / TESORERO_CENTRAL)

---

## Lote 3: Ciclo de cobro + Cierre contable PCESFL (2026-05-18) — PENDIENTE

```sql
-- ===== Recibos: nueva tabla =====
CREATE TABLE IF NOT EXISTS recibos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  numero_recibo VARCHAR(30) NOT NULL UNIQUE,
  ejercicio INTEGER NOT NULL,
  tipo VARCHAR(30) NOT NULL DEFAULT 'CUOTA_ORDINARIA',
  concepto VARCHAR(300) NOT NULL,
  miembro_id UUID NOT NULL REFERENCES miembros(id),
  cuota_id UUID REFERENCES cuotas_anuales(id) ON DELETE SET NULL,
  orden_cobro_id UUID REFERENCES ordenes_cobro(id) ON DELETE SET NULL,
  importe NUMERIC(10,2) NOT NULL,
  importe_pagado NUMERIC(10,2) NOT NULL DEFAULT 0,
  estado VARCHAR(20) NOT NULL DEFAULT 'EMITIDO',
  modo_cobro VARCHAR(20),
  fecha_emision DATE NOT NULL,
  fecha_vencimiento DATE,
  fecha_cobro DATE,
  observaciones TEXT,
  fecha_creacion TIMESTAMP DEFAULT now(),
  fecha_modificacion TIMESTAMP,
  fecha_eliminacion TIMESTAMP,
  eliminado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID REFERENCES usuarios(id),
  modificado_por_id UUID REFERENCES usuarios(id)
);
CREATE INDEX IF NOT EXISTS ix_recibos_ejercicio ON recibos(ejercicio);
CREATE INDEX IF NOT EXISTS ix_recibos_miembro_id ON recibos(miembro_id);
CREATE INDEX IF NOT EXISTS ix_recibos_estado ON recibos(estado);
CREATE INDEX IF NOT EXISTS ix_recibos_cuota_id ON recibos(cuota_id);
CREATE INDEX IF NOT EXISTS ix_recibos_eliminado ON recibos(eliminado);

-- ===== Remesa: nuevos campos SEPA =====
ALTER TABLE remesas
  ADD COLUMN IF NOT EXISTS tipo_remesa VARCHAR(20) NOT NULL DEFAULT 'ORDINARIA',
  ADD COLUMN IF NOT EXISTS concepto VARCHAR(300),
  ADD COLUMN IF NOT EXISTS seq_tipo VARCHAR(4) NOT NULL DEFAULT 'RCUR',
  ADD COLUMN IF NOT EXISTS remesa_origen_id UUID REFERENCES remesas(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_remesas_tipo_remesa ON remesas(tipo_remesa);
CREATE INDEX IF NOT EXISTS ix_remesas_remesa_origen_id ON remesas(remesa_origen_id);

-- ===== OrdenCobro: fecha_rechazo =====
ALTER TABLE ordenes_cobro
  ADD COLUMN IF NOT EXISTS fecha_rechazo DATE;

-- ===== Justificante de Gasto: nueva tabla =====
CREATE TABLE IF NOT EXISTS justificantes_gasto (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  numero_justificante VARCHAR(30) NOT NULL UNIQUE,
  ejercicio INTEGER NOT NULL,
  miembro_id UUID NOT NULL REFERENCES miembros(id),
  actividad_id UUID NOT NULL REFERENCES actividades(id),
  partida_actividad_id UUID REFERENCES partidas_presupuesto_actividad(id) ON DELETE SET NULL,
  agrupacion_id UUID REFERENCES unidades_organizativas(id),
  concepto VARCHAR(300) NOT NULL,
  importe NUMERIC(10,2) NOT NULL,
  fecha_gasto DATE NOT NULL,
  fecha_presentacion DATE NOT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'PRESENTADO',
  aprobado_por_id UUID REFERENCES miembros(id),
  fecha_aprobacion DATE,
  motivo_rechazo TEXT,
  apunte_caja_id UUID REFERENCES apuntes_caja(id) ON DELETE SET NULL,
  cuenta_bancaria_id UUID REFERENCES cuentas_bancarias(id),
  modo_pago VARCHAR(20),
  fecha_pago DATE,
  observaciones TEXT,
  fecha_creacion TIMESTAMP DEFAULT now(),
  fecha_modificacion TIMESTAMP,
  fecha_eliminacion TIMESTAMP,
  eliminado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID REFERENCES usuarios(id),
  modificado_por_id UUID REFERENCES usuarios(id)
);
CREATE INDEX IF NOT EXISTS ix_justificantes_gasto_ejercicio ON justificantes_gasto(ejercicio);
CREATE INDEX IF NOT EXISTS ix_justificantes_gasto_miembro_id ON justificantes_gasto(miembro_id);
CREATE INDEX IF NOT EXISTS ix_justificantes_gasto_actividad_id ON justificantes_gasto(actividad_id);
CREATE INDEX IF NOT EXISTS ix_justificantes_gasto_estado ON justificantes_gasto(estado);
CREATE INDEX IF NOT EXISTS ix_justificantes_gasto_eliminado ON justificantes_gasto(eliminado);

-- ===== OrigenApunte: añadir JUSTIFICANTE_GASTO al enum =====
ALTER TYPE origenapunte ADD VALUE IF NOT EXISTS 'JUSTIFICANTE_GASTO';
```

**Instrucciones para aplicar**:
```bash
docker exec -i siga_dev_db psql -U siga -d siga < <(echo "$SQL")
docker restart siga_dev_backend
```

-- ===== Eliminación de balances_contables (mayo 2026) =====
-- El balance de sumas y saldos no se persiste: se calcula al vuelo desde apuntes.
-- Lo que se archivará a futuro son las Cuentas Anuales (Balance PCESFL + Cuenta
-- de Resultados + Memoria) tras el asiento de CIERRE confirmado.
DROP TABLE IF EXISTS balances_contables CASCADE;

-- ===== Lote 5 (Flujo 4 — Liquidación de remesa) =====
-- D4.1: end_to_end_id legible {referencia_remesa}-{nseq:03d}
ALTER TABLE ordenes_cobro ADD COLUMN IF NOT EXISTS nseq INTEGER NOT NULL DEFAULT 0;
WITH numeradas AS (
  SELECT id, ROW_NUMBER() OVER (PARTITION BY remesa_id ORDER BY fecha_creacion, id) AS rn
  FROM ordenes_cobro
)
UPDATE ordenes_cobro o SET nseq = n.rn FROM numeradas n WHERE n.id = o.id AND o.nseq = 0;

-- D4.3: trazabilidad del aviso al socio fallido + plantilla usada
ALTER TABLE recibos
  ADD COLUMN IF NOT EXISTS fecha_aviso_fallido DATE,
  ADD COLUMN IF NOT EXISTS plantilla_email_aviso_id UUID REFERENCES plantillas_email(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_recibos_fecha_aviso_fallido ON recibos(fecha_aviso_fallido);

-- ===== Lote 6 (Flujo 1 — Establecimiento de cuotas) =====
-- D1.1: cat�logo de motivos de reducci�n con % aplicado a la cuota base
CREATE TABLE IF NOT EXISTS motivos_reduccion_cuota (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo VARCHAR(30) UNIQUE NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  porcentaje_reduccion NUMERIC(5,2) NOT NULL CHECK (porcentaje_reduccion BETWEEN 0 AND 100),
  orden INTEGER NOT NULL DEFAULT 0,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  fecha_creacion TIMESTAMP DEFAULT now(),
  fecha_modificacion TIMESTAMP,
  fecha_eliminacion TIMESTAMP,
  eliminado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID REFERENCES usuarios(id),
  modificado_por_id UUID REFERENCES usuarios(id)
);
CREATE INDEX IF NOT EXISTS ix_motivos_reduccion_cuota_codigo ON motivos_reduccion_cuota(codigo);
CREATE INDEX IF NOT EXISTS ix_motivos_reduccion_cuota_activo ON motivos_reduccion_cuota(activo);

-- D1.2: cada TipoMiembro puede tener motivo de reducci�n por defecto
ALTER TABLE tipos_miembro
  ADD COLUMN IF NOT EXISTS motivo_reduccion_id UUID
    REFERENCES motivos_reduccion_cuota(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_tipos_miembro_motivo_reduccion_id ON tipos_miembro(motivo_reduccion_id);

-- snapshot del motivo aplicado en cada CuotaAnual (trazabilidad)
ALTER TABLE cuotas_anuales
  ADD COLUMN IF NOT EXISTS motivo_reduccion_id UUID
    REFERENCES motivos_reduccion_cuota(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_cuotas_anuales_motivo_reduccion_id ON cuotas_anuales(motivo_reduccion_id);

-- ===== Lote 7 (Flujo 2 — Emisión de recibos) =====
-- D2.3: recibo asociado a agrupación territorial (prefijo en número)
ALTER TABLE recibos
  ADD COLUMN IF NOT EXISTS agrupacion_id UUID REFERENCES unidades_organizativas(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_recibos_agrupacion_id ON recibos(agrupacion_id);
-- numero_recibo se mantiene UNIQUE global: el prefijo {AGR}- evita colisiones entre agrupaciones

-- ===== Flujo 3 (D3.5): Datos del acreedor SEPA en `configuraciones` =====
INSERT INTO configuraciones (clave, valor, tipo_dato, descripcion, modificable, grupo, orden)
VALUES
  ('sepa_creditor_name',  '',  'string',  'Nombre del acreedor SEPA (titular de la cuenta operativa)',  TRUE, 'SEPA',  1),
  ('sepa_creditor_iban',  '',  'string',  'IBAN del acreedor SEPA',                                       TRUE, 'SEPA',  2),
  ('sepa_creditor_bic',   '',  'string',  'BIC/SWIFT del acreedor SEPA',                                  TRUE, 'SEPA',  3),
  ('sepa_creditor_id',    '',  'string',  'Identificador SEPA del acreedor (AT-02, formato ES-XX-NNN…)',  TRUE, 'SEPA',  4)
ON CONFLICT (clave) DO NOTHING;

-- ===== Flujo 7 (D7.5 + D7.2): aceptación intermedia + adjunto opcional =====
ALTER TABLE justificantes_gasto
  ADD COLUMN IF NOT EXISTS aceptado_por_id UUID REFERENCES miembros(id),
  ADD COLUMN IF NOT EXISTS fecha_aceptacion DATE,
  ADD COLUMN IF NOT EXISTS archivo_factura VARCHAR(500);
CREATE INDEX IF NOT EXISTS ix_justificantes_gasto_aceptado_por_id ON justificantes_gasto(aceptado_por_id);

-- ===== Flujo 7 (D7.6 + D7.7): atajo tesorero + categoría de gasto =====
ALTER TABLE justificantes_gasto
  ADD COLUMN IF NOT EXISTS cuenta_contable_id UUID REFERENCES cuentas_contables(id),
  ADD COLUMN IF NOT EXISTS presentado_en_nombre_de_id UUID REFERENCES miembros(id);
CREATE INDEX IF NOT EXISTS ix_justificantes_gasto_cuenta_contable_id ON justificantes_gasto(cuenta_contable_id);

-- ===== Flujo 10: Cuentas Anuales =====
CREATE TABLE IF NOT EXISTS cuentas_anuales (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ejercicio INTEGER NOT NULL UNIQUE,
  estado VARCHAR(20) NOT NULL DEFAULT 'BORRADOR',
  balance_pcesfl JSONB,
  cuenta_resultados JSONB,
  memoria JSONB,
  excedente NUMERIC(14,2),
  fecha_aprobacion DATE,
  aprobado_por_id UUID REFERENCES miembros(id),
  acta_referencia VARCHAR(200),
  fecha_deposito DATE,
  archivo_acuse_recibo VARCHAR(500),
  observaciones TEXT,
  fecha_creacion TIMESTAMP DEFAULT now(),
  fecha_modificacion TIMESTAMP,
  fecha_eliminacion TIMESTAMP,
  eliminado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID REFERENCES usuarios(id),
  modificado_por_id UUID REFERENCES usuarios(id)
);
CREATE INDEX IF NOT EXISTS ix_cuentas_anuales_ejercicio ON cuentas_anuales(ejercicio);
CREATE INDEX IF NOT EXISTS ix_cuentas_anuales_estado ON cuentas_anuales(estado);

-- ===== Flujo 11: Modelo 182 (declaración fiscal de donaciones) =====
CREATE TABLE IF NOT EXISTS presentaciones_modelo_182 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ejercicio INTEGER NOT NULL UNIQUE,
  fecha_envio DATE NOT NULL,
  codigo_aeat VARCHAR(100),
  n_donantes INTEGER NOT NULL DEFAULT 0,
  importe_total NUMERIC(14,2) NOT NULL DEFAULT 0,
  archivo_acuse VARCHAR(500),
  observaciones TEXT,
  fecha_creacion TIMESTAMP DEFAULT now(),
  fecha_modificacion TIMESTAMP,
  fecha_eliminacion TIMESTAMP,
  eliminado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID REFERENCES usuarios(id),
  modificado_por_id UUID REFERENCES usuarios(id)
);
CREATE INDEX IF NOT EXISTS ix_presentaciones_modelo_182_ejercicio ON presentaciones_modelo_182(ejercicio);

-- ===== Flujo 6: Donaciones (ampliación del modelo) ===== [APLICADO 2026-05-21]
-- Las columnas se aplicaron directamente (faltaban en BD y rompían Modelo 182).
ALTER TABLE donaciones
  ADD COLUMN IF NOT EXISTS tipo VARCHAR(15) NOT NULL DEFAULT 'DINERARIA',
  ADD COLUMN IF NOT EXISTS caracter VARCHAR(15) NOT NULL DEFAULT 'PUNTUAL',
  ADD COLUMN IF NOT EXISTS descripcion_especie TEXT,
  ADD COLUMN IF NOT EXISTS valoracion NUMERIC(10,2),
  ADD COLUMN IF NOT EXISTS documento_valoracion VARCHAR(500),
  ADD COLUMN IF NOT EXISTS cuenta_bancaria_id UUID REFERENCES cuentas_bancarias(id),
  ADD COLUMN IF NOT EXISTS apunte_caja_id UUID REFERENCES apuntes_caja(id),
  ADD COLUMN IF NOT EXISTS asiento_id UUID REFERENCES asientos_contables(id),
  ADD COLUMN IF NOT EXISTS agrupacion_id UUID REFERENCES unidades_organizativas(id),
  ADD COLUMN IF NOT EXISTS numero_certificado VARCHAR(30) UNIQUE;
CREATE INDEX IF NOT EXISTS ix_donaciones_tipo ON donaciones(tipo);
CREATE INDEX IF NOT EXISTS ix_donaciones_agrupacion_id ON donaciones(agrupacion_id);

-- Estados de donación: limpiar y sembrar los 3 finales (D6.1)
DELETE FROM estados_donacion WHERE nombre IN ('Pendiente','Recibida','Certificada','Anulada');
INSERT INTO estados_donacion (id, nombre, descripcion, orden, es_inicial, es_final, activo, fecha_creacion, es_inmutable, eliminado)
SELECT gen_random_uuid(), 'REGISTRADA', 'Donación registrada, pendiente de cobro', 1, true, false, true, now(), false, false
WHERE NOT EXISTS (SELECT 1 FROM estados_donacion WHERE nombre='REGISTRADA');
INSERT INTO estados_donacion (id, nombre, descripcion, orden, es_inicial, es_final, activo, fecha_creacion, es_inmutable, eliminado)
SELECT gen_random_uuid(), 'COBRADA', 'Donación recibida y contabilizada', 2, false, false, true, now(), false, false
WHERE NOT EXISTS (SELECT 1 FROM estados_donacion WHERE nombre='COBRADA');
INSERT INTO estados_donacion (id, nombre, descripcion, orden, es_inicial, es_final, activo, fecha_creacion, es_inmutable, eliminado)
SELECT gen_random_uuid(), 'ANULADA', 'Donación anulada o devuelta', 99, false, true, true, now(), false, false
WHERE NOT EXISTS (SELECT 1 FROM estados_donacion WHERE nombre='ANULADA');

-- ===== Bloqueante #1 (post-flujo 6): imputación de apuntes de caja a actividad/campaña =====
-- Permite calcular el balance económico por actividad/campaña que se reporta en la
-- Memoria económica (flujo 10). Sin esto, los gastos directos (alquileres, software,
-- salarios) no pueden imputarse a la actividad o campaña que los origina.
ALTER TABLE apuntes_caja
  ADD COLUMN IF NOT EXISTS actividad_id UUID REFERENCES actividades(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS campania_id UUID REFERENCES campanias(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_apuntes_caja_actividad_id ON apuntes_caja(actividad_id);
CREATE INDEX IF NOT EXISTS ix_apuntes_caja_campania_id ON apuntes_caja(campania_id);

-- ===== Datos económicos del socio: motivo de reducción individual =====
-- Override del motivo de reducción del TipoMiembro a nivel de socio individual.
-- Prevalece sobre `tipo_miembro.motivo_reduccion_id` al calcular la cuota.
-- D1.5: el porcentaje queda congelado si ya hay recibos emitidos para esa cuota.
ALTER TABLE miembros
  ADD COLUMN IF NOT EXISTS motivo_reduccion_id UUID REFERENCES motivos_reduccion_cuota(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_miembros_motivo_reduccion_id ON miembros(motivo_reduccion_id);

-- ===== Lote A-pre: Catálogo de estados de campaña con `codigo` estable + estado CERRADA =====
ALTER TABLE estados_campania
  ADD COLUMN IF NOT EXISTS codigo VARCHAR(50);

-- Rellenar por NOMBRE (los UUIDs pueden variar entre entornos)
UPDATE estados_campania SET codigo='BORRADOR'   WHERE nombre='Borrador'   AND codigo IS NULL;
UPDATE estados_campania SET codigo='PROGRAMADA' WHERE nombre='Programada' AND codigo IS NULL;
UPDATE estados_campania SET codigo='EN_CURSO'   WHERE nombre='En curso'   AND codigo IS NULL;
UPDATE estados_campania SET codigo='PAUSADA'    WHERE nombre='Pausada'    AND codigo IS NULL;
UPDATE estados_campania SET codigo='FINALIZADA' WHERE nombre='Finalizada' AND codigo IS NULL;
UPDATE estados_campania SET codigo='CANCELADA'  WHERE nombre='Cancelada'  AND codigo IS NULL;

ALTER TABLE estados_campania
  ALTER COLUMN codigo SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ux_estados_campania_codigo ON estados_campania(codigo);

INSERT INTO estados_campania (
  id, codigo, nombre, descripcion, orden, es_inicial, es_final,
  color, activo, fecha_creacion, eliminado
)
SELECT gen_random_uuid(),
       'CERRADA', 'Cerrada',
       'Campaña cerrada económicamente; no admite nuevos gastos',
       7, false, true,
       '#1F2937', true, now(), false
 WHERE NOT EXISTS (SELECT 1 FROM estados_campania WHERE codigo='CERRADA');

UPDATE estados_campania
   SET descripcion = 'Actividades terminadas; todavía pueden imputarse gastos rezagados'
 WHERE codigo = 'FINALIZADA';

-- ===== Lote A: Actividad.caracter (PUNTUAL / RECURRENTE / PERMANENTE) =====
ALTER TABLE actividades
  ADD COLUMN IF NOT EXISTS caracter VARCHAR(15) NOT NULL DEFAULT 'PUNTUAL';
CREATE INDEX IF NOT EXISTS ix_actividades_caracter ON actividades(caracter);

-- Migración: actividades sin campaña y sin recurrencia → PERMANENTE.
UPDATE actividades
   SET caracter = 'PERMANENTE'
 WHERE campania_id IS NULL AND es_recurrente = false AND padre_id IS NULL;

-- Actividades recurrentes (plantillas o instancias) → RECURRENTE.
UPDATE actividades
   SET caracter = 'RECURRENTE'
 WHERE es_recurrente = true OR padre_id IS NOT NULL;

-- ===== Refactor Flujo 7 Justificantes (multi-línea + documentos + cuenta por tipo de actividad) =====
ALTER TABLE tipos_accion
  ADD COLUMN IF NOT EXISTS cuenta_contable_default_id UUID
    REFERENCES cuentas_contables(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_tipos_accion_cuenta_contable_default_id
  ON tipos_accion(cuenta_contable_default_id);

CREATE TABLE IF NOT EXISTS justificantes_gasto_linea (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  justificante_id UUID NOT NULL REFERENCES justificantes_gasto(id) ON DELETE CASCADE,
  concepto VARCHAR(300) NOT NULL,
  importe NUMERIC(10,2) NOT NULL,
  fecha_gasto DATE NOT NULL,
  observaciones TEXT,
  fecha_creacion TIMESTAMP DEFAULT now(),
  fecha_modificacion TIMESTAMP,
  fecha_eliminacion TIMESTAMP,
  eliminado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID REFERENCES usuarios(id),
  modificado_por_id UUID REFERENCES usuarios(id)
);
CREATE INDEX IF NOT EXISTS ix_justificantes_gasto_linea_justificante_id
  ON justificantes_gasto_linea(justificante_id);

CREATE TABLE IF NOT EXISTS justificantes_gasto_documento (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  justificante_id UUID NOT NULL REFERENCES justificantes_gasto(id) ON DELETE CASCADE,
  nombre_archivo VARCHAR(255) NOT NULL,
  url VARCHAR(500) NOT NULL,
  mime_type VARCHAR(80),
  tamano_bytes INTEGER,
  ocr_texto TEXT,
  ocr_datos_json TEXT,
  fecha_creacion TIMESTAMP DEFAULT now(),
  fecha_modificacion TIMESTAMP,
  fecha_eliminacion TIMESTAMP,
  eliminado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID REFERENCES usuarios(id),
  modificado_por_id UUID REFERENCES usuarios(id)
);
CREATE INDEX IF NOT EXISTS ix_justificantes_gasto_documento_justificante_id
  ON justificantes_gasto_documento(justificante_id);

-- Migración: por cada JustificanteGasto existente, crear una línea-espejo
INSERT INTO justificantes_gasto_linea (id, justificante_id, concepto, importe, fecha_gasto, fecha_creacion, eliminado)
SELECT gen_random_uuid(), j.id, j.concepto, j.importe, j.fecha_gasto, now(), false
  FROM justificantes_gasto j
 WHERE j.eliminado = false
   AND NOT EXISTS (SELECT 1 FROM justificantes_gasto_linea l WHERE l.justificante_id = j.id);

-- ─────────────────────────────────────────────────────────────────────────
-- Solicitud de reducción de cuota (Flujo: el socio solicita, el tesorero
-- aprueba/rechaza). Estados: PRESENTADA | APROBADA | RECHAZADA | ANULADA.
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS solicitudes_reduccion_cuota (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  miembro_id UUID NOT NULL REFERENCES miembros(id),
  motivo_reduccion_id UUID NOT NULL REFERENCES motivos_reduccion_cuota(id),
  ejercicio INTEGER NOT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'PRESENTADA',
  texto_solicitud TEXT,
  fecha_presentacion DATE NOT NULL,
  resuelto_por_id UUID REFERENCES miembros(id),
  fecha_resolucion DATE,
  motivo_rechazo TEXT,
  fecha_creacion TIMESTAMP DEFAULT now(),
  fecha_modificacion TIMESTAMP,
  fecha_eliminacion TIMESTAMP,
  eliminado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID REFERENCES usuarios(id),
  modificado_por_id UUID REFERENCES usuarios(id)
);
CREATE INDEX IF NOT EXISTS ix_solicitudes_reduccion_cuota_miembro_id
  ON solicitudes_reduccion_cuota(miembro_id);
CREATE INDEX IF NOT EXISTS ix_solicitudes_reduccion_cuota_estado
  ON solicitudes_reduccion_cuota(estado);
CREATE INDEX IF NOT EXISTS ix_solicitudes_reduccion_cuota_ejercicio
  ON solicitudes_reduccion_cuota(ejercicio);
CREATE INDEX IF NOT EXISTS ix_solicitudes_reduccion_cuota_motivo
  ON solicitudes_reduccion_cuota(motivo_reduccion_id);

CREATE TABLE IF NOT EXISTS solicitudes_reduccion_cuota_documento (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  solicitud_id UUID NOT NULL REFERENCES solicitudes_reduccion_cuota(id) ON DELETE CASCADE,
  nombre_archivo VARCHAR(255) NOT NULL,
  url VARCHAR(500) NOT NULL,
  mime_type VARCHAR(80),
  tamano_bytes INTEGER,
  fecha_creacion TIMESTAMP DEFAULT now(),
  fecha_modificacion TIMESTAMP,
  fecha_eliminacion TIMESTAMP,
  eliminado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID REFERENCES usuarios(id),
  modificado_por_id UUID REFERENCES usuarios(id)
);
CREATE INDEX IF NOT EXISTS ix_solicitudes_reduccion_cuota_documento_solicitud_id
  ON solicitudes_reduccion_cuota_documento(solicitud_id);

-- ─────────────────────────────────────────────────────────────────────────
-- Vista de nombramientos orgánicos vigentes (estado ACTIVO, sin fecha de fin).
-- Fuente única: historial_nombramientos. Una VISTA (no materializada) → siempre
-- al día, sin mantenimiento. Permite detectar fácilmente al tesorero/cargo
-- vigente de cada agrupación. Mapeada en el ORM como modelo de solo lectura
-- NombramientoVigente.
-- ─────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_nombramientos_vigentes AS
SELECT id, miembro_id, cargo_id, agrupacion_id, fecha_inicio
FROM historial_nombramientos
WHERE estado = 'ACTIVO' AND fecha_fin IS NULL AND eliminado = false;

-- ─────────────────────────────────────────────────────────────────────────
-- Incremento voluntario de cuota (APLICADO directamente — 2026-05-20).
-- El socio puede decidir pagar de más sobre su cuota base; cantidad fija en €
-- que se suma al generar las cuotas. No requiere aprobación, solo se graba.
-- ─────────────────────────────────────────────────────────────────────────
ALTER TABLE miembros
  ADD COLUMN IF NOT EXISTS incremento_cuota NUMERIC(10,2) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS incremento_cuota_obs TEXT;

-- Formas de pago PayPal y Bizum (APLICADO directamente — 2026-05-20).
INSERT INTO formas_pago (id, codigo, nombre, descripcion, activo, fecha_creacion, eliminado, es_inmutable) VALUES
  (gen_random_uuid(), 'PAYPAL', 'PayPal', 'Cobro a una cuenta PayPal', true, now(), false, false),
  (gen_random_uuid(), 'BIZUM',  'Bizum',  'Cobro mediante Bizum al teléfono', true, now(), false, false)
ON CONFLICT (codigo) DO NOTHING;

-- Reclasificación de unidades organizativas (APLICADO directamente — 2026-05-20).
-- Las 43 unidades tipificadas como "Grupo local" eran en realidad provincias
-- (su nombre coincide con una provincia). Se reclasifican a "Agrupaciones
-- provinciales" para que la jerarquía sea Nacional → CCAA → Provincia.
UPDATE unidades_organizativas
SET tipo_id = (SELECT id FROM niveles_organizativos WHERE nombre='Agrupaciones provinciales')
WHERE tipo_id = (SELECT id FROM niveles_organizativos WHERE nombre='Grupo local');

-- Corrección de nombre del nivel supranacional (APLICADO directamente — 2026-05-20).
UPDATE niveles_organizativos SET nombre='Europa Laica Internacional' WHERE nombre='Europa Internacional';

-- ─────────────────────────────────────────────────────────────────────────
-- Lote 9: Donaciones ligadas a campañas de recogida de fondos (2026-05-26)
-- La columna `donaciones.campania_id` ya existe (UUID indexada) pero no
-- tiene FK a `campanias`. Añadirla. La relación SQLAlchemy ya se ha
-- destapado en `donaciones.py:campania`.
-- ─────────────────────────────────────────────────────────────────────────
ALTER TABLE donaciones
  ADD CONSTRAINT fk_donaciones_campania_id
  FOREIGN KEY (campania_id) REFERENCES campanias(id)
  ON DELETE SET NULL
  NOT VALID;
-- NOT VALID + VALIDATE: evita full-scan bloqueante en producción.
ALTER TABLE donaciones VALIDATE CONSTRAINT fk_donaciones_campania_id;

-- ─────────────────────────────────────────────────────────────────────────
-- Lote 8: Catálogo `tipos_ingreso` (preparado 2026-05-26) — PENDIENTE
-- Reemplaza el getTipoClass hardcoded de ListaEconomico.vue y unifica el
-- discriminador {CUOTA, DONACION, SUBVENCION, GASTO, …} con un catálogo
-- que lleve `color` (badge dinámico, patrón estándar del proyecto).
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tipos_ingreso (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo VARCHAR(40) UNIQUE NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  color VARCHAR(20),
  signo VARCHAR(10) NOT NULL DEFAULT 'INGRESO',  -- INGRESO | GASTO
  orden INTEGER NOT NULL DEFAULT 0,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  fecha_creacion TIMESTAMP DEFAULT now(),
  fecha_modificacion TIMESTAMP,
  fecha_eliminacion TIMESTAMP,
  eliminado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID REFERENCES usuarios(id),
  modificado_por_id UUID REFERENCES usuarios(id)
);
CREATE INDEX IF NOT EXISTS ix_tipos_ingreso_codigo ON tipos_ingreso(codigo);
CREATE INDEX IF NOT EXISTS ix_tipos_ingreso_signo ON tipos_ingreso(signo);
CREATE INDEX IF NOT EXISTS ix_tipos_ingreso_activo ON tipos_ingreso(activo);

INSERT INTO tipos_ingreso (codigo, nombre, descripcion, color, signo, orden) VALUES
  ('CUOTA',              'Cuota',                       'Cuota ordinaria de socio',                       '#7C3AED', 'INGRESO',  1),
  ('DONACION',           'Donación',                    'Donación recibida',                              '#2563EB', 'INGRESO',  2),
  ('SUBVENCION_PUBLICA', 'Subvención pública',          'Subvención de administración pública',           '#059669', 'INGRESO',  3),
  ('SUBVENCION_PRIVADA', 'Subvención privada',          'Subvención de entidad privada',                  '#10B981', 'INGRESO',  4),
  ('VENTA',              'Venta',                       'Venta de bienes o servicios',                    '#0891B2', 'INGRESO',  5),
  ('OTROS_INGRESOS',     'Otros ingresos',              'Ingresos no clasificados',                       '#64748B', 'INGRESO', 99),
  ('GASTO',              'Gasto',                       'Gasto general',                                  '#DC2626', 'GASTO',   10),
  ('GASTO_PERSONAL',     'Gastos de personal',          'Salarios, retenciones, seguros sociales',        '#B91C1C', 'GASTO',   11),
  ('GASTO_ACTIVIDAD',    'Gastos de actividad',         'Materiales, alquileres, ponentes',               '#EF4444', 'GASTO',   12),
  ('GASTO_ESTRUCTURA',   'Gastos de estructura',        'Mantenimiento de sede, software, gestoría',      '#F97316', 'GASTO',   13),
  ('TRASPASO',           'Traspaso entre cuentas',      'Movimiento entre cuentas propias (neutro)',      '#94A3B8', 'INGRESO', 90)
ON CONFLICT (codigo) DO NOTHING;

-- FK opcional en cuotas_anuales y donaciones (snapshot del tipo en cada movimiento)
ALTER TABLE cuotas_anuales
  ADD COLUMN IF NOT EXISTS tipo_ingreso_id UUID REFERENCES tipos_ingreso(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_cuotas_anuales_tipo_ingreso_id ON cuotas_anuales(tipo_ingreso_id);

ALTER TABLE donaciones
  ADD COLUMN IF NOT EXISTS tipo_ingreso_id UUID REFERENCES tipos_ingreso(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_donaciones_tipo_ingreso_id ON donaciones(tipo_ingreso_id);

-- Backfill: marcar las cuotas como CUOTA y las donaciones como DONACION
UPDATE cuotas_anuales SET tipo_ingreso_id = (SELECT id FROM tipos_ingreso WHERE codigo='CUOTA')
  WHERE tipo_ingreso_id IS NULL;
UPDATE donaciones     SET tipo_ingreso_id = (SELECT id FROM tipos_ingreso WHERE codigo='DONACION')
  WHERE tipo_ingreso_id IS NULL;

-- Tras este lote, en código backend:
--   * añadir relación `tipo_ingreso` en modelos CuotaAnual y Donacion
--   * exponer `tipoIngreso { codigo nombre color }` en GraphQL
--   * deprecar TipoMovimientoTesoreria a favor del catálogo (o conservarlo solo
--     para distinguir TRASPASO ↔ flujo neto, ortogonal a este catálogo)
-- En frontend (ListaEconomico.vue):
--   * eliminar getTipoClass, usar badgeStyle(fila.tipoIngresoColor)
--   * exponer color desde la query GraphQL de cuotas y donaciones
