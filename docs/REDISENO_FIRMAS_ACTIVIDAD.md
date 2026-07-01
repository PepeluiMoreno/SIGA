# Rediseño: la recogida de firmas es una Actividad, no una Campaña

> Estado: **parcialmente implementado (interim)**. Ya hecho: el desplegable y el
> alta funcionan **por actividad** (`GET /api/publico/firmas/actividades`,
> `POST` acepta `actividad_id`), pero el satélite `FirmaCampania` sigue anclado
> a la campaña de esa actividad y la métrica de firmas se lee de `MetaCampania`
> (sin `MetaActividad` ni migración todavía). Pendiente: re-anclar la firma a la
> actividad y mover la meta a la actividad (requiere migración + merge de heads).
>
> **Frontend:** el detalle de campaña (`DetalleCampania.vue`) muestra ya un panel
> "Recogida de firmas" (firmas verificadas vs objetivo + actividades online),
> alimentado por el nuevo resolver `firmasVerificadasCampania`. El resto de la UI
> ya contemplaba lo necesario (`esOnline` editable, métricas con unidad "firmas").
> Marco: es la **Fase 1** del norte arquitectónico
> `docs/arquitectura/ACTIVIDAD_UNIDAD_ABC.md` (la Actividad como unidad
> universal de trabajo y de coste).
> Origen: la firma pública se ancló a `Campania`, pero el modelo correcto es:
> una **campaña de recogida de firmas** es una Campaña cuya **actividad
> principal** (si no la única) es una **recogida de firmas en la web** de la
> asociación; esa recogida es una **Actividad** con una **meta expresada en nº
> de firmas**. Por tanto **la firma debe colgar de la Actividad**.

## 1. Modelo objetivo

```
Campania ("Recogida de firmas por …")
   └── Actividad (recogida de firmas web)      ← es_online, meta en firmas
          └── FirmaCampania (satélite de Participacion)  ← se ancla AQUÍ
```

- La **Campaña** es el contenedor (comunicación, presupuesto, informe global).
- La **Actividad** es **online** (`es_online = True`) y es donde se recogen las
  firmas y donde vive la **meta en firmas**. Puede haber varias (web,
  presencial…), pero la web es la que alimenta este formulario.
- La **firma** es un `Contacto` (PF) con una `Participacion` tipo `FIRMA` y su
  satélite `FirmaCampania`, que pasa a apuntar a la **Actividad**.

### Se estandariza vía plantilla de campaña

En vez de montar la actividad a mano en cada campaña, la **plantilla de campaña
"Recogida de firmas"** (ya existe: `seed_plantillas_campania.py` reserva el UUID
`5ead1968-7c4a-466e-bb27-9df806200738`) se **puebla** con:

- una `PlantillaActividad` **online** "Recogida de firmas web", y
- una **meta en firmas** para esa actividad.

Así, al crear una campaña desde esa plantilla, nace ya con su actividad online de
firmas y su objetivo, sin trabajo manual.

### Cómo se identifica "una actividad de recogida de firmas"

Criterio propuesto (fiel a "una actividad que tenga meta expresada en número de
firmas"): **la Actividad tiene una `MetaActividad` cuyo `TipoMeta.unidad_medida
== "firmas"`**. No dependemos del nombre del tipo de actividad.

## 1b. Identidad del firmante (implementado)

- Un **firmante es un `Contacto` (PF) con la vinculación `FIRMANTE`**. El alta
  pública crea/asegura esa `Vinculacion` (tipo `FIRMANTE`, sin satélite) de forma
  idempotente.
- **Desduplicación por NIF (DNI/NIE)**, no por email: el `Contacto` se busca por
  `numero_documento` normalizado. Una misma persona no se duplica aunque firme con
  emails distintos, y si ya existe (p. ej. es socio) se reutiliza y se le añade la
  vinculación FIRMANTE.
- **NIF obligatorio y validado** (letra de control) en las tres capas: navegador,
  proxy PHP del plugin y endpoint SIGA. Solo DNI/NIE (no pasaporte).
- **Historial de firmas** por firmante = sus `FirmaCampania` (una por campaña/
  actividad firmada); ya disponible vía `contacto.firmas_campania`.

## 2. Estado actual (lo que hay que cambiar)

| Hoy | Objetivo |
|---|---|
| `FirmaCampania.campania_id` **NOT NULL** (ancla a campaña) | añadir `actividad_id` y anclar a la actividad; `campania_id` pasa a NULL-able (denormalizado desde `actividad.campania_id`) |
| Metas solo en `MetaCampania` (no hay meta de actividad) | nuevo `MetaActividad` (espejo de `MetaCampania`, reutiliza `TipoMeta`) |
| Endpoint `POST /api/publico/firmas` recibe `campania_id` | recibe `actividad_id` |
| `GET /api/publico/firmas/campanias` | `GET /api/publico/firmas/actividades` |
| `GET …/contador/{campania_id}` | `…/contador/{actividad_id}` |
| Plugin: desplegable de campañas | desplegable de actividades de firmas |

## 3. Cambios de esquema (aditivos, no destructivos)

1. **Nueva tabla `metas_actividad`** (espejo de `metas_campania`):
   `id, actividad_id → actividades(id) ON DELETE CASCADE, tipo_meta_id →
   tipos_meta_campania(id), valor_planificado, valor_real, notas, orden`.
2. **`firmas_campania`**: nueva columna `actividad_id` (NULL-able, FK
   `actividades(id)`, index); `campania_id` pasa a **NULL-able**.
3. **Sin borrados ni backfill forzoso.** Las `FirmaCampania` existentes
   conservan su `campania_id`; las nuevas usan `actividad_id`. (Backfill
   opcional posterior: `actividad_id` = la actividad de firmas web de esa
   campaña, si existe una sola.)

### Huecos en las plantillas (para "poblarla como plantilla")

Hoy `PlantillaActividad` **no tiene `es_online`** y las metas de plantilla
(`PlantillaMeta`) cuelgan de la **plantilla (campaña)**, no de una
`PlantillaActividad`. Para que la plantilla lleve "una actividad online con meta
en firmas" hacen falta:

4. `PlantillaActividad.es_online` (Boolean, default False) — para que la
   actividad instanciada nazca online.
5. Decidir dónde vive la meta de firmas de la plantilla:
   - **P1 (propuesta):** nueva `PlantillaMetaActividad` (meta por actividad de
     plantilla) → al instanciar crea `MetaActividad`. Coherente con "meta en la
     actividad".
   - **P2:** reutilizar `PlantillaMeta` (nivel campaña, unidad "firmas") → al
     instanciar crea `MetaCampania`. Cero esquema nuevo, pero la meta queda en la
     campaña, no en la actividad.
6. **Seed:** poblar la plantilla `5ead1968…` con la `PlantillaActividad` online
   "Recogida de firmas web" + su meta en firmas (idempotente).

## 4. Servicio (`FirmaPublicaService`)

- `registrar_firma(actividad_id, …)`: valida actividad abierta **y con meta de
  firmas**; upsert de `Contacto`; `FirmaCampania(actividad_id=…,
  campania_id=actividad.campania_id)`; email de doble opt-in citando la
  actividad. La verificación (`verificar_firma`) no cambia (usa `firma_id`).
- `listar_actividades_firmas_abiertas()`: actividades no eliminadas, **abiertas**
  y con `MetaActividad` de unidad "firmas".
- `contar_firmas_verificadas(actividad_id)`: cuenta por `actividad_id`.

## 5. Endpoint público

- `POST /api/publico/firmas` → campo `actividad_id` (UUID).
- `GET /api/publico/firmas/actividades` → `[{id, nombre, campania, meta_firmas,
  firmas_verificadas}]` de las recogidas web abiertas.
- `GET /api/publico/firmas/contador/{actividad_id}`.

## 6. Plugin WordPress

- Ajustes: el desplegable se llena desde `…/actividades` (no `…/campanias`).
- Se guarda `actividad_id`; el shortcode acepta `actividad="UUID"`.
- El proxy REST reenvía `actividad_id`.

## 7. ⚠️ Decisiones que necesito de ti antes de tocar datos

**(A) ¿Qué es una actividad "abierta" para firmar?** `EstadoAccion` **no tiene
`codigo`** (hereda de `EstadoBase`: `nombre, es_final, …`) y el seed de
`ESTADOS_ACCION` **no marca `es_final`**. Estados existentes: *Propuesta,
Aprobada, En preparación, En curso, Finalizada, Cancelada*. Opciones:
  - **A1 (propuesta):** abierta = estado ∈ {Aprobada, En preparación, En curso}
    (excluye Propuesta, Finalizada, Cancelada). Requiere fijarlo por `nombre` o,
    mejor, **añadir `es_final`/un flag al seed de estados** para no depender del
    nombre.
  - **A2:** abierta = estado.nombre ∉ {Finalizada, Cancelada} (más permisivo).

**(B) Forma de la meta.** `MetaActividad` reutilizando `TipoMeta` (unidad
"firmas") — coherente con `MetaCampania`, permite varias metas y encaja con la
plantilla P1 — **[propuesta]**; o un simple entero `meta_firmas` en `Actividad`
(más rápido, menos general).

**(C) Meta en la plantilla:** P1 (`PlantillaMetaActividad` → `MetaActividad`,
propuesta) vs P2 (`PlantillaMeta` → `MetaCampania`). Ver §3.

## 8. ⚠️ Alembic: 4 heads abiertos

Hay 4 revisiones cabeza sin mergear: `m8n9o0p1q2r3`, `a7f3c9d8b2e4`,
`vol1ext2anc3`, `c1a2b3d4e5f6`. La migración de este rediseño tendrá que fijar
`down_revision` y, seguramente, **mergear heads** primero. No lo hago sin tu OK
porque afecta al orden de despliegue en staging/prod.

## 9. Rollout y rollback

- Migración aditiva → desplegable sin downtime; las firmas viejas siguen
  contando por campaña hasta backfill.
- Rollback: `downgrade` elimina `metas_actividad` y la columna `actividad_id`, y
  revierte `campania_id` a NOT NULL (posible solo si no hay firmas con
  `campania_id` NULL; por eso el interim mantiene `campania_id` poblado).
