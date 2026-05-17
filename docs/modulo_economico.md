# Módulo Económico — estado y cambios pendientes

> **Workflow**: NO aplicar `alembic upgrade head` ni reiniciar backend por cada cambio.
> Acumular SQL y cambios de modelo aquí; ejecutar de una vez al cerrar el lote.

---

## Estado actual del modelo (2026-05-15)

### Tablas principales

| Tabla | Clase Python | Archivo |
|---|---|---|
| `cuentas_bancarias` | `CuentaBancaria` | `tesoreria.py` |
| `movimientos_tesoreria` | `MovimientoTesoreria` | `tesoreria.py` |
| `conciliaciones_bancarias` | `ConciliacionBancaria` | `tesoreria.py` |
| `cuotas` | `Cuota` | `cuotas.py` |
| `cobros` | `Cobro` | `cobro/` |
| `donaciones` | `Donacion` | `donaciones.py` |
| `remesas` | `Remesa` | `remesas.py` |
| `reclamaciones` | `Reclamacion` | `reclamaciones/` |
| `categorias_partida` | `CategoriaPartida` | `presupuesto.py` |
| `partidas_presupuestarias` | `PartidaPresupuestaria` | `presupuesto.py` |
| `compromisos_presupuestarios` | `CompromisoPresupuestario` | `presupuesto.py` |
| `planificaciones_anuales` | `PlanificacionAnual` | `presupuesto.py` |
| `asientos_contables` | `AsientoContable` | `contabilidad.py` |

### Normativa aplicada
- PCESFL 2013 (Plan de Contabilidad para Entidades Sin Fines Lucrativos)
- Guía AEF 2022

---

## Documentación de referencia

Los documentos de diseño del módulo están en `backend/app/modules/economico/docs/`:

- [financiero.md](../backend/app/modules/economico/docs/financiero.md) — Tesorería y contabilidad (spec completa)
- [cobro.md](../backend/app/modules/economico/docs/cobro.md) — Adaptador de cobros
- [paypal.md](../backend/app/modules/economico/docs/paypal.md) — Integración PayPal

---

## Pendientes de diseño

### 1. `tipos_ingreso` como catálogo de tabla (pendiente)

El frontend usa un enum hardcoded `getTipoClass()` para colorear el tipo de ingreso.
Reemplazar por tabla `tipos_ingreso` con campo `color` para que sea configurable desde UI.
Ver memory: `project_tipo_ingreso_catalogo.md`

### 2. `campania_id` en pagos y donaciones (pendiente)

Para campañas de recogida de fondos (fundraising), añadir FK opcional `campania_id` a
`Cobro` / `Donacion`. Ver memory: `project_pagos_campanas_fondos.md`

### 3. Plan Anual de Actividades / Memoria Anual (pendiente)

Ejercicio presupuestario anual: las campañas se vinculan por fechas al plan, no por FK directa.
Ver memory: `project_plan_anual_actividades.md`

### 4. Migración m012 — verificar estado

La migración `m012` del módulo económico puede estar incompleta o no aplicada.
Verificar con `alembic history` y `alembic current` antes del siguiente lote.

---

## Cambios pendientes de migrar

### Lote: rediseño módulo campañas (2026-05-16)

#### Nuevas tablas

```sql
-- Desglose de presupuesto a nivel de actividad
CREATE TABLE partidas_presupuesto_actividad (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actividad_id UUID NOT NULL REFERENCES actividades(id) ON DELETE CASCADE,
  concepto VARCHAR(200) NOT NULL,
  importe_estimado NUMERIC(12,2) NOT NULL DEFAULT 0,
  importe_real NUMERIC(12,2),
  tipo_partida VARCHAR(10) NOT NULL DEFAULT 'gasto',  -- 'gasto' | 'ingreso'
  orden INTEGER NOT NULL DEFAULT 0,
  creado_en TIMESTAMPTZ DEFAULT now(),
  modificado_en TIMESTAMPTZ DEFAULT now()
);

-- Partes de trabajo (horas por actividad y miembro)
CREATE TABLE registros_trabajo_actividad (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actividad_id UUID NOT NULL REFERENCES actividades(id) ON DELETE CASCADE,
  miembro_id UUID NOT NULL REFERENCES miembros(id),
  fecha DATE NOT NULL,
  horas NUMERIC(5,2) NOT NULL,
  descripcion TEXT,
  tipo VARCHAR(20) NOT NULL DEFAULT 'presencia',  -- presencia|teletrabajo|coordinacion|otro
  creado_en TIMESTAMPTZ DEFAULT now()
);

-- Documentos adjuntos a actividades (actas, informes, fotos, material)
CREATE TABLE documentos_actividad (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actividad_id UUID NOT NULL REFERENCES actividades(id) ON DELETE CASCADE,
  nombre VARCHAR(200) NOT NULL,
  nombre_archivo VARCHAR(300) NOT NULL,
  ruta VARCHAR(500) NOT NULL,
  tipo_mime VARCHAR(100),
  tamanyo BIGINT,
  tipo_doc VARCHAR(20) NOT NULL DEFAULT 'otro',  -- acta|informe|foto|material|otro
  subido_por_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  creado_en TIMESTAMPTZ DEFAULT now()
);

-- Justificantes contables adjuntos a partidas de presupuesto
CREATE TABLE documentos_partida (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  partida_actividad_id UUID REFERENCES partidas_presupuesto_actividad(id) ON DELETE CASCADE,
  partida_campania_id UUID REFERENCES partidas_presupuesto_campania(id) ON DELETE CASCADE,
  nombre VARCHAR(200) NOT NULL,
  nombre_archivo VARCHAR(300) NOT NULL,
  ruta VARCHAR(500) NOT NULL,
  tipo_mime VARCHAR(100),
  tamanyo BIGINT,
  tipo_doc VARCHAR(20) NOT NULL DEFAULT 'otro',  -- factura|ticket|presupuesto|otro
  subido_por_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  creado_en TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT chk_partida_xor CHECK (
    (partida_actividad_id IS NOT NULL)::int + (partida_campania_id IS NOT NULL)::int = 1
  )
);
```

#### Modelos Python añadidos
- `PartidaPresupuestoActividad` — en `actividad.py`
- `RegistroTrabajoActividad` — en `actividad.py`
- `DocumentoActividad` — en `actividad.py`
- `DocumentoPartida` — en `actividad.py`

#### Infraestructura de uploads
- Nuevo router REST: `backend/app/routers/uploads.py`
- Volumen Docker: `/app/uploads/` → persistencia de ficheros subidos
- Pendiente: añadir volumen en `docker-compose.dev.yml`

---

## Pasos para aplicar el lote

```bash
docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend alembic upgrade head
docker compose -f docker-compose.dev.yml --env-file .env.dev restart backend
```
