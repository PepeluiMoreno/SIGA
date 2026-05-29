# Módulo Actividades (incl. Campañas) — estado y cambios pendientes

> **Workflow**: NO aplicar `alembic upgrade head` ni reiniciar backend por cada cambio.
> Acumular SQL y cambios de modelo aquí; ejecutar de una vez al cerrar el lote.

---

## Reglas de negocio (fuente para el manual de usuario)

> Redactadas en lenguaje de usuario. Esta sección es la fuente del manual; el detalle
> técnico (modelo de datos, fases) está más abajo. Última revisión: 2026-05-29.

### 1. Ciclo de vida de una actividad
Una actividad recorre estos estados:

`Propuesta → Aprobada → En preparación → Preparada → En curso → Finalizada`
(y, como salida alternativa desde cualquier estado no final, `Cancelada`).

- **Distinción**: una actividad puede pertenecer a una campaña (*actividad de campaña*) o ser
  independiente (*actividad fuera de campaña*). Las reglas de preparación y autorización aplican
  a ambas; cambian solo los actores que autorizan.

### 2. Preparación obligatoria
- **Ninguna actividad, por insignificante que sea, puede iniciarse (pasar a "En curso") sin
  preparación.** Como mínimo debe existir una **planificación de tareas** (al menos una tarea).
- Cada **tipo de actividad** define qué requisitos de preparación son obligatorios; cada actividad
  concreta puede ajustar (override) esos requisitos. Los requisitos posibles son:
  - **Anuncio de inicio**: al menos un documento que anuncie el comienzo de la actividad.
  - **Convocatoria de participantes**: los participantes deben ser citados.
  - **Grupo de trabajo**: si la actividad lo requiere, debe formarse durante la preparación.
- **No se sale de "En preparación" hasta cumplir todos los requisitos aplicables.** Cuando el
  checklist está completo (y, en su caso, los grupos están formados con todo el personal
  comprometido y las autorizaciones concedidas), la actividad pasa a **"Preparada"**.

### 3. Asignación de recursos
La preparación consiste en cubrir los **recursos** que la actividad necesita, de seis familias:
- **Humanos**: formación del grupo de trabajo (ver regla 4).
- **Económicos**: compromiso de fondos de partidas presupuestarias (ver regla 5).
- **Espacio físico** (si es presencial): lugar/local durante un intervalo de tiempo.
- **Sala virtual** (si es online): plataforma de videoconferencia.
- **Material/equipo**: equipo audiovisual, mobiliario, etc., con control de **existencias** (stock).
- **Transporte**: vehículos privados de los voluntarios que tengan vehículo propio.

Todo recurso con coste compromete automáticamente una partida de gasto de la actividad.

### 4. Grupo de trabajo y consentimiento del voluntario
- Formar el grupo implica **consultar la disponibilidad** de los voluntarios y sus **habilidades**
  para acometer las tareas definidas en la actividad.
- Para incorporar a un voluntario hace falta **su consentimiento**: el **coordinador de campaña**
  (que no tiene por qué ser un coordinador territorial) le envía una **notificación que el
  voluntario debe aceptar**. Solo cuenta como comprometido cuando acepta.
- El transporte en vehículo propio sigue el mismo flujo de consentimiento.

### 5. Autorización de la parte económica
La asignación de dinero de partidas presupuestarias para los gastos de la actividad pasa por un
circuito de autorización:
1. El **diseñador de la campaña** somete la planificación económica a autorización.
2. El **Interventor** (control presupuestario — rol `INTERVENTOR`) emite un **informe**:
   - **Desfavorable** → la planificación económica **vuelve al diseñador de la campaña** (con
     los motivos) para que la revise y la vuelva a someter.
   - **Favorable** → pasa al Presidente.
3. El **Presidente** da el **visto bueno definitivo** → la parte económica queda **aceptada**.

### 6. Autorización de recursos humanos y materiales
- **Campañas territoriales** → aprueba el **Coordinador Territorial** de la agrupación.
- **Campañas generales** → aprueba el **Presidente**.

### 7. Iniciar, cerrar y cancelar
- **Iniciar** ("En curso"): requiere actividad "Preparada" (regla 2) — y nunca sin tareas.
- **Cierre y valoración**: **no pueden hacerse antes de la fecha de celebración** de la actividad.
- **Cancelación**: una actividad **sí puede cancelarse en cualquier momento** (incluso antes de la
  fecha), pero **expresando obligatoriamente los motivos**.
- *(El cierre y valoración de campañas y de actividades fuera de campaña se detallará al final.)*

### 8. Planificación anual (precede a todo el ciclo)
- Cada año, la **junta directiva** aprueba un **calendario de actividades para el año siguiente**.
  Esas actividades pueden estar **encuadradas o no en campañas**.
- A cada campaña se le **nombra un coordinador de campaña**.
- Esto ocurre **de forma recursiva en todas las agrupaciones territoriales**: cada agrupación
  aprueba su propio calendario anual (su junta directiva), no solo la organización general.
- **Dependencia dura: sin planificación de campañas no puede haber presupuestos.** El presupuesto
  (partidas y compromisos) de un ejercicio se construye sobre las campañas/actividades planificadas
  y aprobadas; no se pueden asignar fondos a lo que no está en el plan aprobado.

> Orden del cliclo completo: **Plan anual (junta, por agrupación) → campañas (con coordinador) →
> actividades → preparación/recursos → presupuesto/autorización → ejecución → cierre.**

### 10. Objetivos (KPIs) y valoración
- **El submódulo de objetivos/KPIs es opcional, controlado por una *feature flag*** en
  **Parámetros Generales › Funcionalidades** ("Medición de objetivos / KPIs"). Una organización que
  no quiera usarlo diseña campañas y actividades **sin objetivos** y nada lo exige.
- **Con el flag activado** aplican estas reglas:
  - **No puede haber valoración sin objetivos**: cerrar/valorar exige ≥1 objetivo formulado.
  - **Obligatorios desde el principio**: no se aprueba ni prepara una campaña/actividad sin al menos
    un objetivo definido (con su valor objetivo). Planificar es planificar *con metas*.
- **Con el flag desactivado** (por defecto): los objetivos no se piden en ningún momento; la
  valoración, si se hace, es solo cualitativa (texto libre).
- Los objetivos pueden formularse **a dos niveles**: **campaña** y **actividad**.
- Los objetivos son en realidad **KPIs**: cada uno tiene una unidad de medida, un **valor objetivo**
  (fijado al planificar) y un **valor real** (rellenado al cierre).
- **Valoración = cumplido / no cumplido por KPI**: cada objetivo es binario (se alcanzó o no, según
  su valor real frente al objetivo). La valoración global se expresa como **"X de N objetivos
  cumplidos"**; el texto de valoración complementa, no sustituye, ese dato. (Sin pesos ni notas
  ponderadas, por decisión del 2026-05-29.)
- El **KPI de Asistencia/Penetración** es un caso aparte: se muestra **siempre**, esté o no activo
  este submódulo (ver regla 11).

### 11. Control de asistencia (independiente del submódulo de objetivos)
- Toda actividad presenta **siempre en la UI** un **KPI fijo de Asistencia / Penetración**, esté o no
  activado el submódulo de objetivos. Es un indicador "fijo" que **se puede rellenar o no**, según se
  haya hecho control de asistencia.
- Mide el alcance distinguiendo dos públicos:
  - **Penetración interna** (en la organización): personas de la organización que asisten/participan.
  - **Penetración externa** (público general): personas ajenas a la organización alcanzadas.
- Se **autocalcula** desde los participantes (interno = participaciones con miembro; externo =
  participaciones externas) y/o se completa manualmente si el control fue presencial. Sustituye al
  antiguo campo `asistencia_real`.
- **Que el control de asistencia sea obligatorio es un *feature flag del tipo de actividad***
  (`TipoActividad.control_asistencia_obligatorio`): así la organización se obliga a llevar control de
  asistencia **según el tipo de actividad**. Si el tipo lo exige, no se puede cerrar la actividad sin
  registrar la asistencia; si no, queda opcional.

### 13. Modo de inicio: programado vs disparo manual
Como las actividades están programadas (tienen fecha), el inicio puede ser automático:
- **`modo_inicio = PROGRAMADO`** (por defecto): al llegar la `fecha_inicio` (y `hora_inicio` si la
  hay), la actividad pasa **automáticamente** de "Preparada" a "En curso". Sigue exigiendo estar
  "Preparada" (regla 2): si no se preparó a tiempo, **no arranca** y queda señalada como pendiente.
  No hace falta el botón "Iniciar actividad"; se ofrece a lo sumo un "iniciar ahora" para adelantar.
- **`modo_inicio = MANUAL`** (disparo manual): no arranca sola; **requiere** que alguien pulse
  "Iniciar actividad". Es el comportamiento para actividades sin fecha fija o que dependen de un
  detonante externo.
- El modo se define por actividad (con valor por defecto heredable del tipo de actividad).
- Técnico: un job periódico (`backend/app/scripts/jobs/`) promueve `Preparada → En curso` para las
  PROGRAMADO cuya fecha/hora ha llegado. El botón "Iniciar actividad" del WorkflowBar solo se muestra
  en MANUAL (o como "adelantar" en PROGRAMADO). Campo nuevo `actividades.modo_inicio` +
  `tipos_accion.modo_inicio_default` (se acumulan en F1).

### 12. Reuniones: gobierno (Secretaría) vs operativas (Actividades)
Las reuniones se reparten **por su naturaleza**, no por dónde se listan:
- **Reuniones de órgano de gobierno** (Asamblea General, Junta Directiva, Comisión): viven en
  **Secretaría**, que es su **fuente de verdad**. Tienen peso legal (Ley Orgánica 1/2002):
  convocatoria con antelación, quórum, orden del día, acuerdos, votaciones, acta y libro de actas.
- Al convocarse, **se proyectan automáticamente como una Actividad interna** (espejo) para entrar en
  calendario y presupuesto. **Esa actividad es de solo lectura como reunión**: se gestiona desde
  Secretaría. En la UI de actividades se marca con un distintivo "Gobierno · gestionar en Secretaría"
  que enlaza a la reunión original.
- **Reuniones operativas / de grupo de trabajo** (coordinación, seguimiento): son **un tipo de
  actividad** ("Reunión") y/o `ReunionGrupo`. Ligeras, sin aparato legal; viven en Actividades.
- Regla práctica para el usuario: *si la reunión genera acuerdos vinculantes o exige quórum →
  Secretaría; si es coordinación de trabajo → Actividad.*

### 9. Organizaciones sin despliegue territorial (regla transversal)
La aplicación **debe funcionar igual para una organización pequeña de implantación local**, sin
estructura territorial (una sola unidad organizativa, sin agrupaciones hijas). En ese caso,
**todo lo que lleva el apelativo de "territorial" queda en nada, porque el territorio es uno**:
- La **recursión por agrupaciones se degrada a un único nodo**: hay un solo plan anual, una sola
  junta directiva, un solo ámbito.
- **No existe el nivel de coordinador territorial**: toda autorización que correspondería a un
  coordinador territorial recae en el **Presidente** (es decir, todo se comporta como "general").
- El despliegue territorial (agrupaciones, juntas por agrupación, coordinadores territoriales,
  reparto de presupuesto por agrupación) es **opcional** y solo se activa en organizaciones que lo
  tengan. Ninguna regla de negocio puede *exigir* estructura territorial para operar.

Esto ajusta el punto a confirmar (b): "territorial vs general" se decide por si la campaña cuelga
de una agrupación territorial con coordinador propio; **a falta de despliegue territorial, siempre
es "general"** (aprueba el Presidente).

> **Puntos a confirmar** (afectan al modelo, ver más abajo): (a) si la autorización económica es por
> actividad o agregada por campaña; (b) criterio exacto territorial vs general (nivel de la
> agrupación de la campaña); (c) confirmar que "controller" = rol `INTERVENTOR`;
> (d) `PlanificacionAnual` hoy es **global** (`ejercicio` único) — hay que hacerla **por agrupación**
> (`agrupacion_id` + unique `(ejercicio, agrupacion_id)`) y vincular la aprobación a la junta de cada una.

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

---

## EPIC: Puerta de preparación de actividades (depuración 2026-05-29)

Origen: revisión de transacciones en staging. Reglas de negocio acordadas con el usuario.

### Decisiones de diseño tomadas
1. **Dónde se declara qué preparación requiere cada actividad** → en el **tipo de actividad** con override por actividad.
2. **Consentimiento del voluntario** → el **coordinador de campaña** (no necesariamente territorial) envía una **notificación que el voluntario debe aceptar**. Cuando todos los grupos quedan formados con el personal comprometido, la actividad pasa a **Preparada**.

### Nuevo ciclo de estados de actividad
`Propuesta → Aprobada → En preparación → Preparada → En curso → Finalizada / Cancelada`

- Se inserta **"Preparada"** (orden 4) entre "En preparación" (3) y "En curso" (que pasa a orden 5; "Finalizada" 6, "Cancelada" 7). Renumerar `estados_accion`.
- **En preparación → Preparada**: solo cuando se cumplen TODOS los requisitos aplicables (ver gate).
- **Preparada → En curso**: arranque efectivo (ya guardado: exige ≥1 tarea; la planificación es parte de la preparación).

### Cambios de modelo (DDL acumulado — NO aplicar aún)

```sql
-- Flags de requisitos por tipo de actividad (defaults)
ALTER TABLE tipos_accion ADD COLUMN requiere_anuncio       boolean NOT NULL DEFAULT false;
ALTER TABLE tipos_accion ADD COLUMN requiere_convocatoria  boolean NOT NULL DEFAULT false;
ALTER TABLE tipos_accion ADD COLUMN requiere_grupo         boolean NOT NULL DEFAULT false;
ALTER TABLE tipos_accion ADD COLUMN control_asistencia_obligatorio boolean NOT NULL DEFAULT false;  -- regla 11

-- Override por actividad (NULL = heredar del tipo)
ALTER TABLE actividades ADD COLUMN requiere_anuncio_override      boolean;
ALTER TABLE actividades ADD COLUMN requiere_convocatoria_override boolean;
ALTER TABLE actividades ADD COLUMN requiere_grupo_override        boolean;

-- Estado del compromiso del voluntario (consentimiento por notificación)
ALTER TABLE aportaciones_horas ADD COLUMN estado_consentimiento varchar(15)
    NOT NULL DEFAULT 'PENDIENTE';  -- PENDIENTE | ACEPTADO | RECHAZADO
ALTER TABLE aportaciones_horas ADD COLUMN notificacion_id uuid
    REFERENCES notificaciones(id) ON DELETE SET NULL;
ALTER TABLE aportaciones_horas ADD COLUMN fecha_respuesta timestamptz;
-- (el flag `confirmado` existente queda como espejo de estado_consentimiento='ACEPTADO')
```

Seed: añadir estado `Preparada` a `estados_accion` y renumerar; nuevo `TipoNotificacion`
código `CONVOCATORIA_GRUPO` (prioridad ALTA, permite_email) para el aviso al voluntario.

### Gate de preparación (En preparación → Preparada)
Para cada requisito **aplicable** (override de la actividad, si no NULL; si no, el del tipo):
- `requiere_anuncio`   → existe ≥1 `DocumentoActividad` con `tipo_doc='anuncio'`.
- `requiere_convocatoria` → todos los `Participacion` de la actividad están citados (notificados).
- `requiere_grupo`     → existe grupo y **todos** sus `RequisitoRecurso` tienen las horas
  cubiertas por `AportacionHoras` con `estado_consentimiento='ACEPTADO'` (`horas_pendientes==0`).
- Siempre → ≥1 tarea de planificación (ya implementado en `_validar_transicion`).

El backend valida en `transicionar_estado`; la UI muestra un **checklist de preparación**
con cada requisito y su estado (cumplido/pendiente) y deshabilita el botón "Marcar preparada"
hasta que todos estén verdes.

### Flujo de consentimiento del voluntario
1. Coordinador de campaña propone voluntario para cubrir un `RequisitoRecurso`
   → crea `AportacionHoras(estado_consentimiento='PENDIENTE')`.
2. Se emite notificación `CONVOCATORIA_GRUPO` al voluntario (reutiliza `NotificacionService.emitir`).
3. El voluntario **acepta/rechaza** desde su bandeja → `estado_consentimiento` + `fecha_respuesta`;
   `confirmado=True` si acepta.
4. Cuando todos los requisitos de todos los grupos están cubiertos por aceptaciones →
   la actividad puede pasar a **Preparada**.

### Plan de implementación (fases)
- **F1 — Modelo/estado** (base): DDL arriba + seed estado "Preparada" + `TipoNotificacion` + modelos.
- **F2 — Gate backend**: cálculo de requisitos efectivos + validación en `transicionar_estado`
  (En preparación → Preparada) + helper `requisitos_preparacion(actividad)`.
- **F3 — UI checklist**: panel de preparación en `DetalleAccion.vue` con estado por requisito.
- **F4 — Documento de anuncio**: subir/registrar `DocumentoActividad` tipo `anuncio` desde la UI.
- **F5 — Convocatoria de participantes**: acción "Citar participantes".
- **F6 — Formación de grupo**: UI de consulta de disponibilidad+habilidades y propuesta de voluntarios.
- **F7 — Consentimiento**: emisión de notificación + bandeja del voluntario (aceptar/rechazar).

> Estado: F1–F7 ❌ pendientes. nº1 (tareas antes de "En curso") y nº3 (cierre tras fecha /
> cancelación con motivos) ✅ ya implementados sin migración (solo lógica).

---

## Asignación de recursos ampliada (decisiones 2026-05-29)

La "formación del grupo de trabajo" de la nº2 se generaliza: una actividad necesita
**recursos** de varias familias y la preparación consiste en cubrirlos todos.

### Decisiones tomadas
1. **Modelo unificado**: un único `RequisitoRecurso` + `AsignacionRecurso` para todas las
   familias (se migra el `AportacionHoras`/`RequisitoRecurso` de horas actual). Un solo motor
   de checklist, disponibilidad y consentimiento.
2. **Existencias = stock + reservas (MVP)**: campo `existencias` por recurso; disponibilidad =
   stock − reservas solapadas. Sin tabla de movimientos por ahora (ampliable).
3. **Espacios físicos = texto libre (como ahora)**: NO se crea catálogo `espacios` reservable.
   El requisito ESPACIO se satisface con el campo `lugar`/`direccion` relleno (sin control de
   solapamiento). El modelo deja la puerta abierta a añadir catálogo de espacios después.

### Familias de recurso
HUMANO · ECONOMICO · ESPACIO(texto libre) · VIRTUAL(`PlataformaTelematica`) · MATERIAL(stock) · TRANSPORTE(vehículos de voluntarios).

### Columna vertebral genérica (sustituye a RequisitoRecurso/AportacionHoras de horas)
```sql
-- RequisitoRecurso v2: qué necesita la actividad/grupo
ALTER TABLE requisitos_recurso ADD COLUMN familia varchar(15) NOT NULL DEFAULT 'HUMANO';
ALTER TABLE requisitos_recurso ADD COLUMN cantidad numeric(10,2);   -- horas|plazas|unidades|importe
ALTER TABLE requisitos_recurso ADD COLUMN obligatorio boolean NOT NULL DEFAULT true;
ALTER TABLE requisitos_recurso ALTER COLUMN especialidad_id DROP NOT NULL;  -- solo HUMANO
ALTER TABLE requisitos_recurso ALTER COLUMN nivel_id DROP NOT NULL;
ALTER TABLE requisitos_recurso ADD COLUMN actividad_id uuid REFERENCES actividades(id);  -- requisito directo de actividad

-- AsignacionRecurso (renombra/extiende aportaciones_horas): qué lo cubre
ALTER TABLE aportaciones_horas ADD COLUMN espacio_texto text;            -- ESPACIO (libre)
ALTER TABLE aportaciones_horas ADD COLUMN recurso_material_id uuid;       -- MATERIAL
ALTER TABLE aportaciones_horas ADD COLUMN plataforma_id uuid REFERENCES sec_plataformas_telematicas(id); -- VIRTUAL
ALTER TABLE aportaciones_horas ADD COLUMN vehiculo_id uuid;               -- TRANSPORTE
-- (estado_consentimiento y notificacion_id ya previstos en el bloque DDL de la nº2)

-- Catálogo de material con stock (MVP)
CREATE TABLE categorias_recurso (id uuid PK, nombre varchar(100), activo bool);
CREATE TABLE recursos_material (
  id uuid PK, nombre varchar(200), categoria_id uuid REFERENCES categorias_recurso,
  gestion_stock varchar(12) NOT NULL DEFAULT 'INVENTARIABLE',  -- INVENTARIABLE|FUNGIBLE|EXTERNO
  existencias int NOT NULL DEFAULT 0, retornable bool NOT NULL DEFAULT true,
  coste_unitario numeric(12,2), cuenta_contable_id uuid, agrupacion_id uuid, activo bool DEFAULT true);

-- Vehículos de voluntarios (sobre Miembro.vehiculo_propio)
CREATE TABLE vehiculos (
  id uuid PK, miembro_id uuid REFERENCES miembros(id) ON DELETE CASCADE,
  descripcion varchar(200), plazas int NOT NULL DEFAULT 4, activo bool DEFAULT true);

-- Plataforma telemática: capacidad de sesiones concurrentes (licencias)
ALTER TABLE sec_plataformas_telematicas ADD COLUMN sesiones_concurrentes int;
```

### Motor de disponibilidad (una función)
`disponible(recurso, intervalo) = capacidad − Σ(asignaciones CONFIRMADAS solapadas)`;
FUNGIBLE descuenta del stock sin devolución. Solape = intersección de
`[fecha_inicio·hora_inicio .. fecha_fin·hora_fin]`.

### Integración económica
Todo recurso con coste (MATERIAL externo/fungible, VIRTUAL de pago, TRANSPORTE km×tarifa)
crea/actualiza una `PartidaPresupuestoActividad` (gasto) ⇒ compromiso de fondos automático.

### Plan revisado (sustituye fases F6/F7 de la nº2 por estas, recurso-genéricas)
- **F1 — Modelo/estado**: estado "Preparada" + flags tipo/actividad + DDL columna vertebral + catálogos material/vehículos.
- **F2 — Motor genérico**: `requisitos_preparacion(actividad)` (familias aplicables) + disponibilidad + validación del gate.
- **F3 — Checklist UI** en `DetalleAccion.vue`: una fila por familia/requisito con estado.
- **F4 — Documento de anuncio** (DocumentoActividad tipo `anuncio`).
- **F5 — Convocatoria de participantes**.
- **F6 — Asignación de recursos UI**: humano (disponibilidad+habilidades), material (stock), virtual, espacio (texto), transporte (vehículos).
- **F7 — Consentimiento**: notificación `CONVOCATORIA_GRUPO`/`OFERTA_TRANSPORTE` + bandeja del voluntario (aceptar/rechazar).
- **F8 — Autorizaciones de preparación** (reglas de negocio 5 y 6).

### Circuito de autorización (técnico — F8)
Dos pistas independientes que deben quedar ACEPTADAS para alcanzar "Preparada":

**Pista económica** (sub-máquina de estados sobre la planificación económica de la actividad):
```
ECON_BORRADOR → (diseñador somete) → ECON_INFORME_INTERVENTOR
   desfavorable → ECON_DEVUELTA (al diseñador, con motivos) → re-somete → ECON_INFORME_INTERVENTOR
   favorable    → ECON_VOBO_PRESIDENTE → (presidente aprueba) → ECON_ACEPTADA
```
**Pista recursos (humanos+materiales)**:
```
REC_BORRADOR → (somete) → REC_EN_APROBACION → aprobado → REC_ACEPTADA / devuelto → REC_BORRADOR
   aprobador = COORDINADOR (territorial) de la agrupación   [campaña territorial]
             = PRESIDENTE                                    [campaña general]
```
- Actores resueltos vía `UsuarioRol` + `Rol` ORGANIZACION en la agrupación de la campaña:
  `INTERVENTOR` (= controller), `PRESIDENTE`, `COORDINADOR`.
- Modelo sugerido: campos de estado por pista en la actividad (`econ_estado`, `recursos_estado`)
  + log genérico `DictamenPreparacion(actividad_id, pista, paso, resultado, por_usuario_id, fecha, motivos)`
  para trazabilidad (sirve también al manual/auditoría).

> **Pendiente de confirmar antes de fijar DDL de F8**:
> (a) ¿autorización económica **por actividad** o **agregada por campaña**?
> (b) criterio **territorial vs general** (¿por nivel/tipo de la `agrupacion_id` de la campaña?);
> (c) confirmar **controller = `INTERVENTOR`**.

- **F9 — Objetivos/KPIs y valoración** (regla de negocio 10).

### Submódulo de objetivos/KPIs (técnico — F9)
Decisiones: **opt-in por feature flag** · **unificado** · **binario (cumplido/no)** · **obligatorio
desde aprobación/preparación (solo si el flag está activo)**.

**Feature flag**: fila en `configuraciones` con `clave='actividades.medicion_objetivos'` (bool,
default false), expuesta en Parámetros Generales › Funcionalidades. Se lee con un helper cacheado
(patrón `economico/core/feature_flags.py`), p. ej. `medicion_objetivos_activa(session)`, e invalidación
de caché al guardar. **Todos los gates de abajo se aplican solo si el flag está activo.**

```sql
-- Catálogo: evoluciona tipos_meta_campania
ALTER TABLE tipos_meta_campania ADD COLUMN direccion varchar(15) NOT NULL DEFAULT 'MAYOR_MEJOR';
    -- MAYOR_MEJOR | MENOR_MEJOR | OBJETIVO_EXACTO
ALTER TABLE tipos_meta_campania ADD COLUMN formato varchar(12) NOT NULL DEFAULT 'entero';
ALTER TABLE tipos_meta_campania ADD COLUMN es_obligatorio_sistema boolean NOT NULL DEFAULT false;
    -- KPI de sistema no eludible (Asistencia/Penetración). Auto-adjunto a toda actividad.
ALTER TABLE tipos_meta_campania ADD COLUMN auto_calculo varchar(20);  -- p.ej. 'PARTICIPACION'
-- (alias conceptual: TipoKPI; se mantiene el tablename por compatibilidad)

-- Objetivo unificado: generaliza metas_campania a campaña O actividad
ALTER TABLE metas_campania RENAME TO objetivos;          -- o crear `objetivos` y migrar
ALTER TABLE objetivos ALTER COLUMN campania_id DROP NOT NULL;
ALTER TABLE objetivos ADD COLUMN actividad_id uuid REFERENCES actividades(id) ON DELETE CASCADE;
ALTER TABLE objetivos ADD COLUMN umbral_cumplido numeric(6,2) DEFAULT 100;  -- % para contar como cumplido
ALTER TABLE objetivos ADD CONSTRAINT ck_objetivo_un_nivel
    CHECK ((campania_id IS NOT NULL) <> (actividad_id IS NOT NULL));
-- valor_planificado → valor_objetivo (rename), valor_real ya existe.
-- `asistencia_real` de actividad deja de ser campo especial: pasa a ser un KPI "asistentes".
```

Reglas mecanizadas:
- **Gate de aprobación/preparación**: bloquear si la campaña/actividad no tiene ≥1 objetivo con
  `valor_objetivo`. Se integra en el gate de "Preparada" (regla 2) y en la aprobación.
- **Gate de cierre**: bloquear cierre/valoración si no hay objetivos o falta algún `valor_real`.
  Encaja con la nº3 (cierre solo tras fecha de celebración).
- **Cumplimiento** (función única, ambos niveles):
  `cumplido = grado(valor_real, valor_objetivo, direccion) ≥ umbral_cumplido`;
  `objetivos_cumplidos` (bool ya existente) se **deriva** = todos los obligatorios cumplidos.
- **Valoración** = "X de N cumplidos" + texto cualitativo. Alimenta la valoración automática de la
  Memoria Anual (ver memoria de proyecto del Plan Anual).
- **Asistencia/Penetración (independiente del flag de objetivos)**: se siembra como `TipoKPI` con
  `es_obligatorio_sistema=true` y `auto_calculo='PARTICIPACION'`. Se muestra **siempre** en la UI de
  toda actividad —aunque `actividades.medicion_objetivos` esté OFF— como KPI fijo rellenable, y **no
  se puede eliminar**. Su `valor_real`:
  - interna = nº de participaciones con `miembro_id`; externa = nº con `nombre_externo` (o manual).
  - (Penetración como % —p.ej. internos/total de la agrupación— queda como refinamiento a confirmar.)
  A nivel campaña, agrega los de sus actividades.
- **Obligatoriedad de asistencia por tipo**: `TipoActividad.control_asistencia_obligatorio` (bool,
  nuevo flag del tipo, junto a `requiere_anuncio/convocatoria/grupo` de F1). Si está activo, **gate de
  cierre**: no se cierra una actividad de ese tipo sin asistencia registrada. Este gate es
  **independiente** del flag de objetivos (los demás gates de KPIs sí dependen de él).
- **Plantillas**: extender `PlantillaMeta` a KPIs sugeridos por tipo de actividad.

> Cierre y valoración de campañas / actividades fuera de campaña: **pendiente, se trata al final** (a petición del usuario).
