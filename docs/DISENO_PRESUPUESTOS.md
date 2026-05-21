# Diseño — Módulo de Presupuestos

**Rama:** `feature/presupuestos`
**Estado:** en desarrollo (Fase 1)

Documento de trabajo. Recoge el alcance acordado y el plan por fases para una
gestión presupuestaria profesional de entidad no lucrativa.

---

## Punto de partida

El modelo de datos ya existe parcialmente en `presupuesto.py` (no era un stub el
modelo, sí la vista). Disponible:

- `PlanificacionAnual` — presupuesto de un ejercicio, con estado, aprobación y
  propiedades calculadas (ingresos, gastos, saldo, % ejecución)
- `CategoriaPartida` — categorías para agrupar partidas
- `PartidaPresupuestaria` — partida con importe presupuestado / comprometido / ejecutado
- `CompromisoPresupuestario` — compromiso de una partida sobre campaña o actividad
- `EstadoPlanificacion` — catálogo de estados

Falta: servicios, resolvers, vista real (hoy es un stub de 14 líneas), imputación
automática de la ejecución, seeds de estados, y los métodos de transición (están como
`TODO`).

---

## Requerimientos funcionales (visión completa)

1. **Estructura** — presupuesto por ejercicio, partidas agrupadas en categorías,
   separadas en ingresos y gastos. Debe cuadrar (equilibrio o déficit/superávit explícito).
2. **Vinculación a la actividad real** — partidas asociables a tipo de actividad o
   campaña (presupuesto por programas, exigido por subvenciones).
3. **Ciclo de vida** — borrador → propuesto → aprobado → en ejecución → cerrado.
   La aprobación es acto de gobierno (conecta con Secretaría: acuerdo de reunión).
4. **Modificaciones presupuestarias** — transferencias entre partidas, ampliaciones,
   suplementos. Trazadas. No se edita el aprobado a mano.
5. **Ejecución y seguimiento** — imputación de apuntes reales a partidas; tres niveles
   (presupuestado / comprometido / ejecutado); disponible por partida.
6. **Control y alertas** — partida agotada, sobreejecutada, desviación significativa;
   opción de control de disponibilidad.
7. **Análisis de desviaciones** — previsto vs ejecutado por partida, en importe y %,
   a fecha y proyectado a cierre.
8. **Comparativa y prórroga** — clonar del año anterior, comparar ejercicios, prórroga.
9. **Integración con cuentas anuales** — liquidación del presupuesto en la Memoria.

---

## Plan por fases

### Fase 1 — Núcleo (EN CURSO)
Lo mínimo para que el presupuesto sea usable de punta a punta.
- Completar transiciones de estado de `PlanificacionAnual` (resolver estado real, no TODO)
- Vinculación de partida a actividad/campaña a nivel de partida
- Servicio `PresupuestoService`: CRUD de planificación y partidas, transiciones,
  validación de equilibrio
- Resolvers GraphQL (queries y mutations)
- Seeds de `EstadoPlanificacion` (BORRADOR, PROPUESTO, APROBADO, EN_EJECUCION, CERRADO)
- Imputación de ejecución: cuando un `ApunteCaja` se imputa a una actividad/campaña con
  partida asociada, actualizar `importe_ejecutado`
- Vista real: estructura del presupuesto, alta de partidas, estado de ejecución
- Informe de desviaciones (previsto vs ejecutado)
- RBAC: transacciones del módulo
- Ayuda y DEPLOY

### Fase 2 — Modificaciones y control
- Modelo `ModificacionPresupuestaria` (transferencia / ampliación / suplemento)
- Presupuesto inicial vs vigente
- Alertas de partida agotada / sobreejecutada
- Control de disponibilidad opcional al imputar

### Fase 3 — Avanzado
- Clonar presupuesto del ejercicio anterior
- Comparativa interanual
- Prórroga presupuestaria
- Volcado a la Memoria de cuentas anuales
- Dashboard económico (incorpora ya el presupuesto)

---

## Decisiones de diseño

- **No romper lo existente.** Se amplía `presupuesto.py`, no se reescribe. Los campos
  y propiedades ya presentes se conservan.
- **Estados al catálogo**, como en Secretaría: `EstadoPlanificacion` ya es tabla; las
  transiciones resolverán el estado por código.
- **Imputación apoyada en la taxonomía existente.** La ejecución se alimenta de
  `ApunteCaja.actividad_id` / `campania_id`, que ya existen, vía el compromiso/partida.
- **Aprobación enlazable con Secretaría** en Fase 1 solo se registra fecha; el vínculo
  formal con acuerdo de reunión se valora en fase posterior.

## Patrón de UI (vista de presupuesto)

**No se usan pestañas.** El proyecto usa paneles en acordeón (`AccordionPanel` +
`AccordionGroup`), con anidamiento de **dos niveles jerárquicos como máximo**, igual que
Tesoreria.vue y DetalleAccion.vue.

Estructura prevista de `Presupuesto.vue`:

- **Nivel 1 — paneles de acordeón:**
  - *Cabecera del presupuesto* — ejercicio, estado, totales (ingresos/gastos/saldo),
    botones de transición de estado según el ciclo de vida
  - *Ingresos* — partidas de ingreso (count = nº partidas)
  - *Gastos* — partidas de gasto (count = nº partidas)
  - *Seguimiento de ejecución* — informe de desviaciones previsto vs ejecutado
- **Nivel 2 — subacordeón dentro de Ingresos y Gastos:** agrupación por
  `CategoriaPartida`; cada categoría es un subpanel que contiene la tabla de sus partidas.

Componentes reutilizables disponibles: `AccordionPanel` (props `title`, `count`,
`defaultOpen`, slot `title`), `AccordionGroup` (abre uno a la vez).
