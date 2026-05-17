# Módulo Actividades (incl. Campañas) — estado y cambios pendientes

> **Workflow**: NO aplicar `alembic upgrade head` ni reiniciar backend por cada cambio.
> Acumular SQL y cambios de modelo aquí; ejecutar de una vez al cerrar el lote.

---

## Estado actual del modelo (2026-05-16)

### Actividades

| Tabla | Clase Python | Archivo | Descripción |
|---|---|---|---|
| `actividades` | `Actividad` | `actividad.py` | Unidad operativa (reemplaza `acciones`) |
| `tipos_accion` | `TipoActividad` / `TipoAccion` | `actividad.py` | Catálogo de tipos (alias de compatibilidad) |
| `estados_accion` | `EstadoAccion` | `catalogos.py` | Estados del ciclo de vida |
| `participaciones` | `Participacion` | `actividad.py` | Participantes en una actividad (miembro o externo) |
| `tareas` | `Tarea` | `tarea.py` | Tareas dentro de una actividad |
| `partidas_presupuesto_actividad` | `PartidaPresupuestoActividad` | `actividad.py` | Desglose de presupuesto por actividad (**nuevo**) |
| `registros_trabajo_actividad` | `RegistroTrabajoActividad` | `actividad.py` | Partes de trabajo/horas por actividad (**nuevo**) |
| `documentos_actividad` | `DocumentoActividad` | `actividad.py` | Adjuntos de actividad (actas, fotos, informes) (**nuevo**) |
| `documentos_partida` | `DocumentoPartida` | `actividad.py` | Justificantes contables de partidas (**nuevo**) |

> `accion.py` es un shim de compatibilidad que re-exporta `Actividad as Accion`. No borrar hasta migrar todos los resolvers.

**Actividad interna vs. de campaña**: `campania_id = null` → actividad interna; `campania_id = <uuid>` → acción de campaña.

### Grupos de trabajo

| Tabla | Clase Python | Archivo |
|---|---|---|
| `grupos_trabajo` | `GrupoTrabajo` | `grupo.py` |
| `requisitos_recurso` | `RequisitoRecurso` | `grupo.py` |
| `aportaciones_horas` | `AportacionHoras` | `grupo.py` |

### Campañas

| Tabla | Clase Python | Archivo |
|---|---|---|
| `campanias` | `Campania` | `campana.py` |
| `tipos_campania` | `TipoCampania` | `campana.py` |
| `tipos_meta` | `TipoMeta` | `campana.py` |
| `tipos_canal_difusion` | `TipoCanalDifusion` | `campana.py` |
| `metas_campania` | `MetaCampania` | `campana.py` |
| `canales_difusion_campania` | `CanalDifusionCampania` | `campana.py` |
| `partidas_presupuesto_campania` | `PartidaPresupuestoCampania` | `campana.py` |
| `plantillas_campania` | `PlantillaCampania` | `campana.py` |
| `plantillas_meta` | `PlantillaMeta` | `campana.py` |
| `plantillas_partida` | `PlantillaPartida` | `campana.py` |
| `plantillas_actividad` | `PlantillaActividad` | `campana.py` |
| `plantillas_tarea` | `PlantillaTarea` | `campana.py` |
| `roles_participante` | `RolParticipante` | `campana.py` |
| `participantes_campania` | `ParticipanteCampania` | `campana.py` |
| `firmantes` | `Firmante` | `campana.py` |
| `firmas_campania` | `FirmaCampania` | `campana.py` |

**Árbol de campañas**: `Campania.padre_id` FK opcional a sí misma. Permite sub-campañas (ej. campaña estatal → instancias locales). La UI de árbol está pendiente (Fase 6).

---

## Arquitectura de UI (2026-05-16) — rediseño completo

### Principio: Detalle = Edición

Las vistas `DetalleCampania.vue` y `CampaniaForm.vue` deben ser **visualmente idénticas**: mismas secciones, misma estructura de acordeones, mismos grids. La única diferencia es que en detalle los valores son `div` con fondo `bg-slate-50` y en edición son `input`/`select`/`textarea`.

### Estructura general

```
WorkflowBar  (estado + botones de transición)

─── Barra KPI (siempre visible, no accordion) ──────────────────
 [Nº actividades] [Presupuesto total] [Metas X/Y] [Fechas] [Estado]

─── AccordionGroup (exclusivo) ─────────────────────────────────
 1. DATOS GENERALES          (violet, default-open)
 2. DISEÑO Y PLANIFICACIÓN   (indigo, default-closed)
 3. COMUNICACIÓN Y METAS     (sky, default-closed)
 4. VALORACIÓN Y CIERRE      (emerald, default-closed)
```

### Acordeón 1 · Datos generales (violet)

Nombre, Estado, Tipo, Ámbito, Lema, URL, Descripción corta, Descripción completa, Objetivo principal, Responsable.

### Acordeón 2 · Diseño y Planificación (indigo)

Sub-sección A — Plantilla y tipo (solo edición/borrador):
- Radiogroup: En blanco / Preconfigurado con plantilla
- Si preconfigurado: select de plantilla + chips informativos

Sub-sección B — Calendario de actividades:
- Controles: [ + Nueva actividad ] [ Vista: Lista | Timeline ]
- **Timeline visual CSS** (sin librerías): chips coloreados por tipo, posicionados por fecha
- **Lista de actividades**: acordeón interno por actividad con secciones:
  - Detalles (descripción, fechas, lugar, online)
  - Presupuesto (tabla de partidas: concepto, tipo, estimado, real)
  - Recursos humanos (responsable, participaciones, horas)
  - Tareas (estado, título, prioridad, horas, asignado)
  - Partes de trabajo (fecha, miembro, horas, tipo, descripción, adjunto)
  - Documentación (documentos de actividad + justificantes contables)

### Acordeón 3 · Comunicación y Metas (sky)

- Canales de difusión (chips multi-select)
- Metas: tabla con tipo, unidad, planificado, real, % progreso
- Botón de notificación (solo en ejecución)

### Acordeón 4 · Valoración y Cierre (emerald)

- Visible siempre (no solo cuando cerrada)
- Presupuesto ejecutado global
- Objetivos cumplidos (toggle)
- Valoración (textarea/div)
- Resumen financiero: partidas de campaña no imputadas a actividades
- Botón "Cerrar campaña" (condicional al estado)

### Timeline visual (CSS puro)

```
left%  = (fechaInicio - inicioRango) / rangoTotal * 100
width% = duracion / rangoTotal * 100
```

Color por tipo de actividad. Click en chip → expande la actividad en la lista.

### Árbol de campañas (`/campanias/arbol`)

Vista separada con renderizado CSS recursivo (`<ul><li>` + `border-left`). Cada nodo muestra nombre, estado, fechas y permite: crear subcampaña, clonar, abrir. Panel lateral al hacer click: resumen + presupuesto consolidado (rollup hijas).

### Clonación de campañas

Modal con: nombre del clon, desplazamiento de fechas (±N días/semanas), checkboxes de qué incluir (metas, partidas, actividades+tareas, subcampañas). No se clonan: participaciones, documentos, registros trabajo.

### Infraestructura de uploads

- Endpoint REST: `POST /api/uploads/actividades/{id}/documentos` (multipart/form-data)
- Almacenamiento: `/app/uploads/campanias/` (volumen Docker)
- Tablas: `documentos_actividad` y `documentos_partida`
- **No** integrado con el módulo de documentación (deferred)

---

## Ciclo de vida de campaña

Estados: **Borrador → Programada → En curso → Pausada → Finalizada / Cancelada**

Gestionado con `WorkflowBar` con botones de transición. **No se usan pestañas por fase** (decisión de 2026-05-16: diseño unificado con acordeones).

---

## Cambios pendientes de migrar

### Lote: rediseño módulo campañas (2026-05-16)

Los modelos Python ya están creados en `actividad.py`. Falta ejecutar las migraciones.
SQL completo en [`docs/modulo_economico.md`](modulo_economico.md) — sección "Lote: rediseño módulo campañas".

Tablas nuevas:
- `partidas_presupuesto_actividad`
- `registros_trabajo_actividad`
- `documentos_actividad`
- `documentos_partida` (con CHECK constraint XOR entre las dos FKs)

### Catálogo `periodicidades` para campañas y actividades

**SQL pendiente**:
```sql
CREATE TABLE periodicidades (
    id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo    VARCHAR(30) NOT NULL UNIQUE,
    nombre    VARCHAR(100) NOT NULL,
    recurrente BOOLEAN NOT NULL DEFAULT false,
    activo    BOOLEAN NOT NULL DEFAULT true
);
CREATE INDEX ix_periodicidades_codigo ON periodicidades (codigo);

INSERT INTO periodicidades (codigo, nombre, recurrente) VALUES
  ('anual',      'Anual',      true),
  ('permanente', 'Permanente', false),
  ('puntual',    'Puntual',    false),
  ('semestral',  'Semestral',  true);
```

> **Estado actual**: El campo `periodicidad String(20)` sigue siendo texto libre. Migración pendiente.

### Campos `rol_emisor` y `contexto` en `PlantillaEmail`

```sql
ALTER TABLE plantillas_email ADD COLUMN rol_emisor VARCHAR(50);
ALTER TABLE plantillas_email ADD COLUMN contexto TEXT;
CREATE INDEX ix_plantillas_email_rol_emisor ON plantillas_email (rol_emisor);
```

### Campo `notificacion_enviada` en `Campania` — ✅ APLICADO

Migración aplicada el 2026-05-15. Flag one-shot: una vez `true`, no vuelve a `false`.

---

## Pendientes de backend

### Fase 1 — modelos base (✅ parcial)

- ✅ Modelos `PartidaPresupuestoActividad`, `RegistroTrabajoActividad`, `DocumentoActividad`, `DocumentoPartida` en `actividad.py`
- ✅ Exports en `__init__.py`
- ❌ Tipos Strawberry (`types_auto.py`): `PartidaPresupuestoActividadType`, `RegistroTrabajoActividadType`, `DocumentoActividadType`
- ❌ Inputs Strawberry (`inputs_auto.py`): Create/Update para partidas y registros
- ❌ Mutations: `crear_partida_actividad`, `guardar_partidas_actividad`, `crear_registro_trabajo`
- ❌ Mutation `clonar_campania(campania_id, nombre, offset_dias, incluir_actividades, incluir_subcampanias)`
- ❌ Mutation `propagar_a_subcampanias(campania_id, campos: [str])`

### Fase 2 — router de uploads

- ❌ Crear `backend/app/routers/uploads.py`
  - `POST /api/uploads/actividades/{id}/documentos`
  - `POST /api/uploads/partidas-actividad/{id}/documentos`
  - `POST /api/uploads/partidas-campania/{id}/documentos`
  - `GET /api/uploads/{ruta}`
  - `DELETE /api/uploads/documentos/{doc_id}`
- ❌ Montar en `main.py`
- ❌ Añadir volumen `/app/uploads` en `docker-compose.dev.yml`

---

## Pendientes de frontend

### Fase 3 — queries y mutations

- ❌ Extender `GET_CAMPANIA` con `partidas`, `registros_trabajo`, `documentos` por actividad
- ❌ Mutations: `GUARDAR_PARTIDAS_ACTIVIDAD`, `CREAR_REGISTRO_TRABAJO`, `CLONAR_CAMPANIA`, `PROPAGAR_A_SUBCAMPANIAS`

### Fase 4 — componentes compartidos

- ❌ `frontend/src/modules/comunicaciones/components/CampaniaKpiBar.vue` — barra KPI fija
- ❌ `frontend/src/modules/comunicaciones/components/ActividadTimeline.vue` — timeline CSS puro
- ❌ `frontend/src/modules/comunicaciones/components/ActividadCard.vue` — tarjeta expandible (prop `readonly`)

### Fase 5 — vistas principales

- ❌ Reescribir `DetalleCampania.vue` con 4 acordeones + KPI bar + timeline
- ❌ Reescribir `CampaniaForm.vue` con misma estructura (inputs en lugar de divs)

### Fase 6 — árbol y clonación

- ❌ Crear `ArbolCampanias.vue` (`/campanias/arbol`)
- ❌ Modal de clonación en `DetalleCampania.vue`
- ❌ Modal "Propagar a subcampañas"

### Fase 7 — dashboard

- ❌ Rediseñar `ListaCampanias.vue` como dashboard con KPIs globales + tarjetas

---

## Pasos para aplicar el lote

```bash
docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend alembic upgrade head
docker compose -f docker-compose.dev.yml --env-file .env.dev restart backend
```
