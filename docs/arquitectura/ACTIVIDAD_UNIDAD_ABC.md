# La Actividad como unidad universal de trabajo y de coste (ABC)

> Norte arquitectónico. Este documento fija un principio de diseño transversal
> del que parten decisiones concretas (p. ej. el rediseño de firmas, ver
> `docs/REDISENO_FIRMAS_ACTIVIDAD.md`). No describe una implementación cerrada,
> sino la dirección a la que converge el modelo.

## 1. Principio

**Todo lo que "se hace" en la organización es una `Actividad`.** No hay flujos
operativos de primera clase fuera de la Actividad: campañas, recogidas de
firmas, eventos, reuniones de gobierno, formación, y también procesos
económicos periódicos como la **recaudación de la cuota anual**.

La Actividad es, a la vez:

- la **unidad operativa** (qué se hace, quién lo coordina, cuándo, dónde), y
- el **objeto de coste** de la contabilidad analítica por actividades (**ABC**,
  *Activity-Based Costing*): el punto al que se imputan gastos e ingresos y
  desde el que se calcula coste y rentabilidad.

## 2. Taxonomía de actividades

Ya modelada en `Actividad.caracter` + `periodicidad`
(`app/modules/actividades/models/actividad.py`):

| Carácter | Qué es | Ejemplos |
|---|---|---|
| **PUNTUAL** | ocurre una vez con fecha | un acto público, una firma presencial |
| **RECURRENTE** | patrón con instancias (plantilla `padre_id=NULL` → instancias) | boletín mensual, **recaudación de cuota anual** |
| **PERMANENTE** | actividad continua agregadora (fuera de campaña) | mantenimiento del local, coordinación, redes sociales |

Ortogonalmente, una actividad puede ser **de campaña** (`campania_id` presente)
o **interna/estructural** (`campania_id` NULL).

### Casos que fija esta visión

- **Recogida de firmas**: `Actividad` **online** (`es_online=True`) de una
  campaña de recogida de firmas, con **meta en nº de firmas**. La firma se ancla
  a la Actividad. (Fase 1, ver spec de firmas.)
- **Recaudación de cuota anual**: `Actividad(caracter=RECURRENTE,
  periodicidad='anual')` cuyo **coordinador es el tesorero** (`responsable_id`).
  Sus costes (remesas, comisiones bancarias) y sus ingresos (cuotas cobradas)
  se imputan a esa actividad.

## 3. Qué YA existe (SIGA está cableado para ABC en gran parte)

El objeto de coste ya está enganchado en el módulo económico:

| Enganche | Dónde |
|---|---|
| Gasto justificado → actividad (**NOT NULL**) + partida | `economico/models/justificantes_gasto.py:43,46` |
| Apunte de tesorería → actividad | `economico/models/tesoreria/apunte.py:70` |
| Asiento contable → actividad | `economico/models/contabilidad/asiento.py:103` |
| Partida de presupuesto → actividad | `economico/models/presupuesto.py:82,174` (`PartidaPresupuestoActividad`) |
| Cuenta contable por defecto según **tipo** de actividad | `actividades/models/actividad.py:27` (`TipoActividad.cuenta_contable_default_id`) |
| Origen de un movimiento = `'actividad'` | `economico/models/tesoreria.py:80` (`entidad_origen_tipo`) |
| Presupuesto ejecutado/estimado en la propia actividad | `actividad.py` (`presupuesto_estimado/ejecutado`) |

Conclusión: **la Actividad ya es el objeto de coste**. Falta la capa de arriba.

## 4. Qué falta para ABC completo

1. **Universalización**: que todo flujo operativo **nazca** como Actividad
   (firmas, cuota anual, gobierno…), no solo que pueda referenciarla. Se aborda
   flujo a flujo, empezando por firmas.
2. **Cost drivers y reparto**: repartir el coste de las actividades
   **PERMANENTES/estructurales** (local, coordinación, comunicación) sobre las
   actividades/campañas finalistas mediante inductores (nº de firmas, nº de
   socios, horas de voluntariado, etc.). Es el núcleo de ABC y **hoy no está**.
3. **Lado ingreso**: imputar ingresos (cuotas, donaciones asociadas) a la
   actividad, igual que ya se hace con el gasto.
4. **Informe analítico**: coste e ingreso por actividad y por campaña →
   coste unitario (€/firma, €/socio captado, €/beneficiario) y rentabilidad.

## 5. Hoja de ruta incremental

- **Fase 1 — Firmas → Actividad** (`docs/REDISENO_FIRMAS_ACTIVIDAD.md`).
  Primer flujo que se reconduce a Actividad; sirve de patrón.
- **Fase 2 — Cuota anual como Actividad** recurrente (coordinador = tesorero);
  imputación de sus gastos e ingresos.
- **Fase 3 — Motor ABC**: catálogo de *cost drivers*, reparto de actividades
  permanentes sobre las finalistas, e informe de coste por actividad/campaña.

## 6. Implicaciones de modelo (a confirmar por fase)

- **Coordinador**: hoy `Actividad.responsable_id` (Contacto). Para gobierno de
  campaña puede requerir un rol explícito (coordinador vs responsable operativo).
- **Meta por actividad**: `MetaActividad` (reutilizando `TipoMeta`), para
  objetivos cuantitativos por actividad (firmas, socios, asistentes…), coherente
  con `MetaCampania`.
- **Estados operativos**: `EstadoAccion` carece de `codigo`/`es_final` fiables;
  conviene normalizarlos para saber cuándo una actividad está "abierta/activa".
- **Inductores de coste**: nuevo catálogo (Fase 3) que ligue una magnitud
  medible de la actividad con el reparto de costes indirectos.

## 7. Por qué importa

Con esto, la pregunta "¿cuánto nos cuesta —y cuánto rinde— cada cosa que
hacemos?" se responde con datos: coste por campaña, por recogida de firmas, por
euro recaudado de cuota. Es la base para priorizar, justificar subvenciones y
rendir cuentas con transparencia analítica, no solo con contabilidad financiera.
