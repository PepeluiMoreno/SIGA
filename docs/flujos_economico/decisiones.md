# Decisiones tomadas — módulo Económico

Registro maestro de decisiones de diseño tomadas durante la documentación e implementación de los flujos económicos. Origen y consecuencias quedan trazados para que se reflejen luego en los manuales de usuario por rol.

Formato: `D{flujo}.{n}` (e.g. `D4.1` = primera decisión del flujo 4).

---

## Flujo 4 — Liquidación de remesa SEPA

### D4.1 · EndToEndId SEPA legible (mayo 2026)

**Decisión**: el identificador `EndToEndIdentification` en el XML SEPA es **`{referencia_remesa}-{nseq:03d}`** (ejemplo: `REM-2025-005-042`).

**Alternativas descartadas**:
- UUID de `OrdenCobro.id` — descartado por ilegibilidad en el extracto del socio.
- Referencia del recibo (`REC-2025-00042`) — descartado porque no funciona en remesas de reenvío (1 cuota puede tener varios recibos).

**Consecuencias técnicas**:
- Nueva columna `OrdenCobro.nseq INTEGER NOT NULL DEFAULT 0` (correlativo dentro de la remesa).
- Backfill SQL para órdenes existentes.
- El generador XML usa `f"{remesa.referencia}-{orden.nseq:03d}"`.
- El parser de pain.002/camt.054 recupera la `OrdenCobro` por descomposición de la cadena.

**Para el manual**:
- *Tesorero*: explicar que en el extracto bancario y en la respuesta del banco verán códigos como `REM-2025-005-042` que identifican unívocamente cada orden.

---

### D4.2 · Fallidos no representables → acción manual (mayo 2026)

**Decisión**: cuando el banco devuelve códigos SEPA no re-presentables (`MD01` sin mandato, `MS02` rechazo del deudor, `AC13` cuenta no autorizada, etc.), el sistema **no** anula automáticamente la orden ni la cuota. La orden queda en `Fallida` con el código registrado; el tesorero decide caso por caso.

**Alternativas descartadas**:
- Anulación automática — descartado porque casos como `MS02` (deudor revierte por error) son recuperables hablando con el socio.
- Diferenciar por código — descartado por complejidad de mantener la tabla de "qué hacer ante cada código".

**Consecuencias técnicas**:
- `RemesaService.liquidar_remesa` deja todas las fallidas con estado `Fallida`, sin tocar la cuota.
- La cuota se mantiene `Pendiente` (o lo que fuera antes); el tesorero la anula manualmente si procede.

**Para el manual**:
- *Tesorero*: tras una liquidación con fallidos, debe revisar la pantalla 5.4 y decidir comunicar al socio, anular la cuota o reenviar en una nueva remesa.

---

### D4.3 · Aviso al socio por fallido = pantalla con multi-envío + plantilla (mayo 2026)

**Decisión**: no hay envío automático en la liquidación. Tras procesarla, el tesorero accede a una pantalla nueva (5.4 "Comunicación a socios con recibo fallido") con:

- Lista filtrable de recibos `FALLIDO` (por código SEPA, ejercicio, agrupación, fecha, "solo sin notificar").
- Multiselección sobre la lista.
- Selector de **plantilla de email** del módulo Comunicación Interna (`plantillas_email` filtrada por `modulo='economico'`).
- Botón "Enviar" → encola un email por socio seleccionado sustituyendo variables (`{nombre_socio}`, `{numero_recibo}`, `{importe}`, `{codigo_sepa}`, `{motivo}`, `{fecha_devolucion}`, `{iban_socio}`).

**Alternativas descartadas**:
- Email automático siempre — descartado, da poco margen al tesorero.
- Email automático solo para representables — descartado por la misma razón.

**Consecuencias técnicas**:
- Nuevas columnas en `recibos`:
  - `fecha_aviso_fallido DATE NULL`
  - `plantilla_email_aviso_id UUID NULL` FK a `plantillas_email`
- Permiso nuevo `ECO_RECIBO_COMUNICAR_FALLIDO`.
- Seed inicial de plantillas en módulo Comunicación Interna (`RECIBO_FALLIDO_AM04`, `RECIBO_FALLIDO_GENERICO`).

**Para el manual**:
- *Tesorero*: tras liquidación con fallidos, debe ir a "Comunicación a fallidos", filtrar/seleccionar, elegir plantilla y enviar. Las plantillas se gestionan en Comunicación Interna (no en Económico).
- *Administrador*: gestiona las plantillas en Comunicación Interna con `modulo='economico'`.

---

---

## Flujo 1 — Establecimiento de cuotas del ejercicio

### D1.1 · Cuota base + porcentaje de reducción por motivo (mayo 2026)

**Decisión**: una sola **cuota base** por ejercicio (NUMERIC). Cualquier rebaja se modela como `MotivoReduccion` con `porcentaje_reduccion` (0–100). El importe efectivo = `importe_base × (1 − %/100)`, redondeado a 2 decimales.

**Alternativas descartadas**:
- Una fila por tarifa (`General`, `Joven`, `Parado`…) — descartado por rigidez: cualquier cambio en la base obliga a editar N filas.
- Importe fijo de reducción — descartado: al cambiar la base, las cuotas reducidas no se actualizan automáticamente.

**Para el manual**:
- *Tesorero*: configura una sola cuota base por ejercicio; los motivos se gestionan en su catálogo y se aplican automáticamente.

---

### D1.2 · Asignación automática por TipoMiembro (mayo 2026)

**Decisión**: cada `TipoMiembro` lleva un `motivo_reduccion_id` opcional. Al generar `CuotaAnual` se aplica el motivo del tipo del miembro. Si NULL, paga cuota base completa. No hay override individual por miembro en v1.

**Alternativas descartadas**:
- Campo `motivo_reduccion_id` en `Miembro` (override individual) — pospuesto a v2.
- Combinación tipo por defecto + override miembro — sin caso de uso claro ahora.

**Para el manual**:
- *Tesorero*: si un socio debe pagar distinto, cambiar su `tipo_miembro`.
- *Administrador*: mantiene la asociación tipo ↔ motivo en parametrización.

---

### D1.3 · Dos pasos separados: configurar / generar (mayo 2026)

**Decisión**: pantalla 5.1 configura importes (editable libremente). Pantalla 5.4 genera `CuotaAnual` solo cuando el tesorero lo aprueba, con previsualización del total esperado y desglose por tipo. Idempotente: si ya hay cuotas del ejercicio, no las duplica.

**Alternativas descartadas**:
- 1 paso (configurar y generar a la vez) — revertir miles de cuotas creadas por error es costoso.
- Generación diferida por miembro (al alta o aniversario) — las cuotas siguen un ejercicio común, no un ciclo personal.

**Para el manual**:
- *Tesorero*: primero configura los importes; cuando esté seguro, pulsa "Generar cuotas".

---

### D1.6 · Gestión del catálogo de motivos = TESORERO_CENTRAL (mayo 2026)

**Decisión**: la transacción `CUO_MOTIVO_MANAGE` (crear/editar motivo de reducción) se asigna **exclusivamente** al rol TESORERO de la organización matriz. Aunque haya tesorería delegada en el futuro, los tesoreros de agrupación no pueden alterar este catálogo.

**Por qué**: el catálogo de motivos es un activo único de la asociación; permitir cambios desde cada agrupación generaría inconsistencias entre series de recibos.

**Para el manual**:
- *Tesorero central*: mantiene el catálogo. Las altas y ediciones son de su responsabilidad.
- *Tesorero de agrupación*: solo lo consulta (`CUO_MOTIVO_LIST`).

---

### D1.5 · Porcentaje del motivo es inmutable si hay recibos emitidos (mayo 2026)

**Decisión**: cuando un `MotivoReduccionCuota` ya tiene cuotas asociadas que han generado al menos un `Recibo` (emitido, cobrado, fallido o anulado), el campo `porcentaje_reduccion` queda **bloqueado en la UI y validado en el backend**. Los demás campos (nombre, descripción, orden, activo) siguen editables.

**Alternativas descartadas**:
- Recálculo automático — modificar retroactivamente los importes emitidos rompe la trazabilidad y confunde al socio (lo que pagó no coincide con lo que dice el motivo).
- Recálculo manual con confirmación — el problema persiste; además depende del criterio puntual del tesorero.

**Procedimiento para cambiar la rebaja de un socio cuando el motivo ya está "congelado"**:
1. Anular la cuota del socio y su recibo asociado.
2. Asignarle otro motivo (cambiando su TipoMiembro o, a futuro v2, vía override individual).
3. Re-emitir el recibo manualmente o incluirlo en una remesa extraordinaria.

**Consecuencias técnicas**:
- En `CuotaService` (o un nuevo helper): `motivo_tiene_recibos(motivo_id) -> bool`.
- En la mutation `actualizarMotivoReduccion`: si `motivo_tiene_recibos` es true y el `porcentaje_reduccion` cambia, rechazar con mensaje claro.
- En la UI (`MotivosReduccionCuota.vue`): deshabilitar el input del % al editar si la mutation devuelve "motivo congelado" (o pre-consultar via query).

**Para el manual**:
- *Tesorero*: si quieres cambiar el porcentaje de un motivo, antes asegúrate de que ninguna cuota con ese motivo tenga ya recibo emitido. Si lo tiene, el sistema te lo impedirá; el camino es anular la cuota del socio afectado, cambiarle el motivo y re-emitir.

---

### D1.4 · Tipos sin cuota (Honorario) → excluidos del proceso (mayo 2026)

**Decisión**: si el `TipoMiembro` apunta a un `MotivoReduccion` con `porcentaje_reduccion >= 100`, los miembros de ese tipo **no generan `CuotaAnual`**. No aparecen en listados de cuotas, no se les emite recibo, no se incluyen en remesas.

**Alternativas descartadas**:
- Crear `CuotaAnual` con importe 0 y estado `Exenta` — descartado por ruido en listados/reportes.
- Bandera `excluye_de_emision` en MotivoReduccion — descartado por redundancia con el `%≥100`.

**Para el manual**:
- *Tesorero*: para que un grupo no pague cuota (honoríficos, beca total), asóciales un tipo con motivo `HONOR` (100%). El sistema los excluye automáticamente.
- *Administrador*: el límite "100% = no genera cuota" es regla del sistema, no configurable.

### D1.7 · Override individual del motivo de reducción (mayo 2026)

**Decisión**: el socio puede tener un `motivo_reduccion_id` propio que prevalece sobre el del `TipoMiembro`. La regla de resolución al calcular su cuota es:

1. Si `miembro.motivo_reduccion_id` está informado → ese motivo.
2. Si no → `miembro.tipo_miembro.motivo_reduccion_id` (D1.2).
3. Si no → no hay reducción, paga la cuota base.

Cubre casos en los que un socio concreto debe pagar reducida (o nada) aunque su tipo general no lo contemple — por ejemplo: socio ordinario con situación de desempleo prolongada al que se le aplica reducción individual sin cambiar su tipo.

**Alternativas descartadas**:
- Crear un `TipoMiembro` específico para cada caso particular — explosión de tipos y ruido en el catálogo.
- Tabla intermedia `miembro_motivo` con vigencia temporal — sobreingeniería para un caso poco frecuente; se puede revisitar si emerge la necesidad.

**Consecuencias técnicas**:
- `Miembro.motivo_reduccion_id` FK opcional a `motivos_reduccion_cuota`.
- `CuotaService.generar_cuotas_individuales` y `recalcular_cuota` aplican la jerarquía.
- En la ficha del socio (acordeón "Datos económicos") aparece el selector "Motivo de reducción individual (opcional)" con la advertencia "no afecta a cuotas ya emitidas" (D1.5 sigue vigente).
- La previsualización por tipo no contempla overrides individuales (se calcula sobre el agregado por tipo); el cómputo real al generar sí los respeta.

**Para el manual**:
- *Tesorero*: si necesitas aplicar una reducción a un socio concreto sin cambiar su tipo, edita su ficha y elige el motivo en "Motivo de reducción individual". El cambio afecta solo a cuotas futuras (D1.5).
- *Tesorero*: si quieres devolver al socio a la regla general de su tipo, deja el campo en blanco.

---

## Flujo 2 — Emisión de recibos

### D2.1 · Emisión manual por el tesorero (mayo 2026)

**Decisión**: el tesorero pulsa "Emitir lote" cuando lo decide. No hay emisión automática al generar remesa.

**Alternativas descartadas**:
- Automática al crear remesa — rompe la separación de fases (emisión es independiente del cobro).
- Híbrido — añade complejidad sin ganancia clara.

**Para el manual**:
- *Tesorero*: emite cuando esté listo; los recibos quedan disponibles para incluir en remesa, cobrar manualmente o exportar.

---

### D2.2 · Acciones por recibo individual: marcar cobrado, anular, PDF, email (mayo 2026)

**Decisión**: sobre un recibo individual el tesorero puede: marcar cobrado manualmente (con cuenta bancaria + modo + fecha), anular (si no COBRADO), descargar PDF (A5 resguardo), enviar PDF por email al socio (con plantilla del módulo Comunicación Interna).

**Para el manual**:
- *Tesorero*: 4 acciones contextuales según estado y permisos.

---

### D2.3 · Numeración correlativa por agrupación territorial (mayo 2026)

**Decisión**: formato `REC-{NOMBRE_CORTO_AGRUPACION}-{YYYY}-{NNNNN}` (ej. `REC-MAD-2025-00042`). Correlativo reiniciado cada ejercicio dentro de cada agrupación. Si no hay agrupación: formato legacy `REC-{YYYY}-{NNNNN}`. Los 3 462 recibos históricos mantienen su numeración (no se renumeran).

**Alternativas descartadas**:
- Numeración global por entidad — rompe el principio de descentralización (cada tesorero territorial debe tener su serie autocontenida).

**Consecuencias técnicas**:
- Nueva columna `recibos.agrupacion_id`.
- `ReciboService.siguiente_numero(ejercicio, agrupacion_id)` con lookup a `UnidadOrganizativa.nombre_corto`.

**Para el manual**:
- *Tesorero central*: ve todas las series.
- *Tesorero de agrupación*: solo su serie con su prefijo.
- *Socio*: en su recibo aparece el prefijo de su agrupación.

---

## Flujo 7 — Justificantes de gasto

### D7.1 · Flujo de tres firmas: presenta → acepta responsable → aprueba tesorero (mayo 2026)

**Decisión**: el justificante recorre **tres firmas** antes del pago:

1. **PRESENTADO** — un miembro (voluntario, colaborador, cargo) presenta el gasto. Cualquier miembro activo puede hacerlo (ver D7.3).
2. **ACEPTADO** — el **responsable de la actividad** (`Actividad.responsable_id`) acepta el gasto. Confirma que el gasto es legítimo y corresponde a la actividad.
3. **APROBADO** — el **tesorero** revisa la documentación y aprueba el pago:
   - Si la tesorería es central: el tesorero central aprueba todo.
   - Si la tesorería está descentralizada: el tesorero del ámbito de la actividad (o de una agrupación ancestro) aprueba.
4. **PAGADO** — el tesorero registra el pago una vez aprobado: indica cuenta bancaria, modo y fecha. Se crea ApunteCaja + asiento contable.

Salidas alternativas:
- **RECHAZADO** (con motivo obligatorio): puede dispararlo el responsable en `PRESENTADO` o el tesorero en `ACEPTADO`.
- **ANULADO**: el presentador lo retira mientras está `PRESENTADO`.

**Implementación**:
- `JustificanteGasto.aceptado_por_id` + `fecha_aceptacion` (campos nuevos).
- Estado nuevo `ACEPTADO`.
- `JustificanteGastoService.aceptar(justificante_id, responsable_id)` valida que `responsable_id == actividad.responsable_id`.
- `JustificanteGastoService.aprobar(...)` exige estado previo `ACEPTADO` (no `PRESENTADO`).

**Para el manual**:
- *Voluntario*: presenta el justificante. Verás su estado evolucionar en "Mis justificantes".
- *Responsable de actividad*: en "Justificantes pendientes de mi visto bueno" aceptas o rechazas los gastos imputados a tus actividades.
- *Tesorero (central o de ámbito)*: en "Justificantes pendientes de aprobación" das el visto bueno final tras revisar el documento, y registras el pago cuando se efectúa.

---

### D7.5 · Aceptación intermedia por responsable de actividad (mayo 2026)

**Decisión**: ver D7.1. La aceptación del responsable de la actividad es un paso obligatorio entre `PRESENTADO` y `APROBADO`. No es un mero trámite: el responsable es quien mejor sabe si el gasto corresponde a su actividad.

**Permiso requerido**: `JUST_ACEPTAR` — asignado a cualquier miembro que sea responsable de al menos una actividad. La validación de "responsable de esta actividad concreta" se hace en código (no se modela como rol territorial).

**Para el manual**:
- *Responsable de actividad*: cuando un miembro presenta un gasto contra tu actividad, recibes una notificación o lo ves en tu listado. Tu papel es confirmar que ese gasto se hizo realmente para esa actividad y autorizar al tesorero a evaluarlo. No estás aprobando el pago — solo confirmando la imputación.

---

### D7.2 · Adjunto opcional (factura/ticket) (mayo 2026)

**Decisión**: el adjunto (PDF/imagen de la factura o ticket) es **opcional al presentar**. Se puede añadir más tarde. El aprobador puede rechazar el justificante con motivo "Falta factura" si lo considera necesario.

**Consecuencias técnicas**:
- Añadir columna `JustificanteGasto.archivo_factura` (path o URL) — para v1 guardamos solo el path; el almacenamiento en disco / S3 se decide al implementar el módulo Documentación general.
- En la UI, campo de subida opcional al presentar y botón "Adjuntar factura" en el detalle si está PRESENTADO sin adjunto.

**Para el manual**:
- *Miembro*: puede presentar el gasto sin adjuntar la factura, pero la mayoría de tesoreros la pedirán antes de aprobar. Se recomienda adjuntarla siempre.
- *Tesorero*: si falta la factura, rechazar con motivo "Falta justificante documental" para que el miembro lo añada y vuelva a presentar.

---

### D7.3 · Presentador = cualquier miembro activo (mayo 2026)

**Decisión**: cualquier miembro con estado activo en SIGA puede presentar un justificante de gasto. No se requiere ningún rol específico; basta con el permiso genérico `JUST_PRESENTAR` asignado a todos los miembros.

**Por qué**: gastos en nombre de la organización pueden hacerlos voluntarios, colaboradores ocasionales, ponentes, etc., no solo cargos. Restringir a roles dificulta la operativa real.

**Validación implícita**: el tesorero de la agrupación correspondiente sigue siendo el filtro de admisión — si el gasto no corresponde, lo rechaza con motivo.

**Para el manual**:
- *Miembro*: cualquier miembro activo puede presentar un gasto. Lo verá en su zona "Mis justificantes". El tesorero de su agrupación se lo aprobará o rechazará.

---

### D7.4 · Numeración por ámbito de la actividad asociada (mayo 2026)

**Decisión**: el número de justificante depende de la **agrupación a la que pertenece la actividad** que origina el gasto:
- Si la actividad está vinculada a un **grupo de trabajo** con `agrupacion_id`, el número lleva el prefijo de esa agrupación: `JUST-{NOMBRE_CORTO}-{YYYY}-{NNNNN}`.
- Si la actividad **no tiene grupo** o el grupo no tiene agrupación (actividad global, campaña central), el número va sin prefijo: `JUST-{YYYY}-{NNNNN}`.

Cada serie es independiente y correlativa por (ejercicio, agrupación), reiniciada cada año.

**Consecuencias técnicas**:
- `JustificanteGastoService.presentar` debe derivar `agrupacion_id` de la actividad → grupo → agrupación.
- `JustificanteGastoService.siguiente_numero(ejercicio, agrupacion_nombre_corto)` análogo a `ReciboService.siguiente_numero` (D2.3).
- Apilar como pendiente: dar a la `Actividad` un `agrupacion_id` directo (hoy se infiere por `grupo_id`). Sin ello, una campaña sin grupo queda en la serie sin prefijo aunque pudiera corresponder a una agrupación.

**Para el manual**:
- *Tesorero de agrupación*: ve los justificantes de su serie territorial con su prefijo.
- *Tesorero central*: ve todas las series, incluida la serie sin prefijo (gastos de actividades globales).
- *Miembro*: en su justificante aparece el prefijo de la agrupación de la actividad si la tiene.

---

### D7.6 · Atajo del tesorero: presentar en nombre del socio → auto-aceptación (mayo 2026)

**Decisión**: cuando un **tesorero** presenta el justificante "a petición del socio que incurrió en el gasto" (porque el socio no tiene acceso a la app, no quiere usarla, o se presenta en mostrador con la factura), el flujo se acorta:

1. La mutation `presentar_justificante_gasto` admite un campo opcional `presentado_en_nombre_de_id` (el miembro real que incurrió en el gasto).
2. Si el usuario logueado tiene `JUST_APROBAR` (es tesorero) Y se rellena ese campo, el justificante nace **directamente en estado `ACEPTADO`** con:
   - `miembro_id = presentado_en_nombre_de_id` (el que pagó el gasto)
   - `aceptado_por_id = usuario actual` (el tesorero que lo presentó)
   - `fecha_aceptacion = hoy`
3. El tesorero sigue teniendo que **aprobarlo** (`aprobar_justificante_gasto`) como paso separado para preservar la trazabilidad de las dos firmas finales (aceptación administrativa + aprobación de pago).

**Por qué la segregación final se conserva**: aunque el tesorero acelere el inicio del proceso, la aprobación formal (con luz verde al pago) debe quedar registrada como acto independiente. Esto cumple el principio de control interno PCESFL norma 1ª.

**Para el manual**:
- *Tesorero*: si un socio te trae una factura física que tienes que dar de alta, usa "Presentar gasto en nombre de socio" desde Justificantes. Se acepta automáticamente; tú lo apruebas y pagas en pasos posteriores.

---

### D7.7 · Vinculación obligatoria a categoría de gasto (cuenta contable) y partida presupuestaria (mayo 2026)

**Decisión**: al presentar el justificante hay que indicar:
1. **Categoría de gasto** (`cuenta_contable_id`): la cuenta del **grupo 6** del plan contable (PCESFL) a la que se imputa el gasto (e.g. `621` Arrendamientos, `624` Transportes, `626` Servicios bancarios, `629` Otros servicios, `640` Sueldos, etc.). **Obligatorio**.
2. **Partida presupuestaria** (`partida_actividad_id`): la partida concreta del presupuesto de la actividad. **Opcional** si la actividad no tiene presupuesto detallado; obligatoria si la tiene.

Si el usuario presenta un gasto y la actividad tiene partidas presupuestarias definidas, la UI exige seleccionar una. Si no las tiene, ese campo queda en blanco y el gasto se imputa "directo a la actividad" sin desglose por partida.

**Consecuencias técnicas**:
- Añadir `JustificanteGasto.cuenta_contable_id UUID FK -> cuentas_contables.id` (obligatorio NOT NULL para nuevos; los históricos quedan NULL).
- El servicio `pagar()` ya usa una `cuenta_de_gasto` derivada de reglas contables; ahora la toma directamente de `justificante.cuenta_contable_id`. Si por compatibilidad queda NULL, sigue cayendo en la regla `JUSTIFICANTE_GASTO/GASTO` genérica como fallback.
- En la UI, el selector de "Categoría de gasto" carga las cuentas contables `tipo=GASTO` `permite_asiento=true` `activa=true`.
- El selector de "Partida presupuestaria" carga las partidas de la actividad seleccionada (si las tiene).

**Para el manual**:
- *Presentador*: al presentar el gasto, indica la **categoría contable** (qué tipo de gasto es). Si la actividad tiene presupuesto, también la **partida** dentro de ese presupuesto.
- *Tesorero*: si una categoría falta o está mal puesta, rechaza el justificante con motivo y pide al socio que la corrija.

---

## Flujo 8 — Conciliación bancaria

### D8.1 · Formatos de extracto soportados: CSV + Norma 43 (mayo 2026)

**Decisión**: el importador admite dos formatos:
- **CSV genérico** con columnas `fecha`, `importe`, `concepto`, `referencia` (separador `;` o `,`; decimal con `,` o `.`).
- **Norma 43 AEB** (fichero `.Q43`), el formato estándar de los bancos españoles para extractos.

Otros formatos (camt.053, MT940) quedan fuera del alcance inicial.

**Consecuencias técnicas**:
- `TesoreriaService.importar_extracto(cuenta_id, lineas)` ya existe pero solo recibe la lista de líneas parseada. Hay que añadir parsers en frontend (CSV) o backend (Norma 43).
- Para Norma 43, lo más limpio es parsearlo en backend: nueva mutation `importar_extracto_norma43(cuenta_id, archivo_b64)` que descodifica y llama internamente al servicio existente.
- Validar que cada línea no se duplica (mismo importe + fecha + referencia en la misma cuenta y rango cercano).

**Para el manual**:
- *Tesorero*: descarga el extracto del banco en formato Norma 43 (todos los bancos españoles lo ofrecen) o en CSV, y súbelo desde la pantalla de Conciliación.

---

### D8.2 · Emparejamiento manual (sin auto-matching) (mayo 2026)

**Decisión**: el tesorero empareja manualmente cada apunte de caja del sistema con la línea del extracto correspondiente. El sistema no propone matchings automáticos por importe/fecha.

**Por qué**: aunque el auto-matching es cómodo, los falsos positivos (dos apuntes del mismo importe en fechas cercanas, comisiones que se solapan) erosionan la fiabilidad. La conciliación es un control de imagen fiel; preferimos lentitud a falsedad.

**UI prevista**: dos paneles lado a lado (apuntes del sistema pendientes ↔ líneas del extracto pendientes), con drag-and-drop o doble-clic para emparejar. La vista muestra subtotales y la diferencia a cuadrar.

**Para el manual**:
- *Tesorero*: la conciliación es manual. Examina cada apunte del sistema y elige su línea correspondiente del extracto. El sistema verifica que los importes coinciden y los marca como conciliados.

---

### D8.3 · Cadencia mensual de conciliación de período (mayo 2026)

**Decisión**: la conciliación de período (`ConciliacionBancaria`, el documento firmado de cierre) se hace **mensual** como buena práctica. El sistema no fuerza la cadencia, pero la UI organiza la conciliación por meses naturales y muestra rojo los meses pendientes.

**Para el manual**:
- *Tesorero*: cada mes, importa el extracto, empareja los apuntes pendientes con sus líneas, comprueba que el saldo cuadra y firma la conciliación del mes (`confirmar_conciliacion_periodo`).

---

### D8.4 · Conciliación completa bloqueante antes del cierre de ejercicio (mayo 2026)

**Decisión**: no se puede ejecutar el asiento de cierre de un ejercicio si hay apuntes de caja sin conciliar de ese ejercicio. La validación es **bloqueante**: el sistema rechaza el cierre con la lista de apuntes pendientes.

**Por qué**: PCESFL norma 9ª de elaboración (imagen fiel) y norma de control interno. Un ejercicio con apuntes sin conciliar tiene saldo no verificado contra el banco; cerrar sería falsear las cuentas anuales.

**Consecuencias técnicas**:
- `CierreEjercicioService.generar_asiento_cierre(ejercicio)` añade una pre-validación: si hay `ApunteCaja.conciliado = false` con `fecha en ese ejercicio`, lanza `ValueError` con el listado.
- La UI del cierre (flujo 9, pendiente) muestra esa lista en rojo y enlaza directamente a la pantalla de conciliación.

**Para el manual**:
- *Tesorero*: antes de iniciar el cierre de ejercicio, completa la conciliación bancaria de todos los meses del año. Si quedan apuntes sin conciliar, el sistema te listará cuáles son y no permitirá generar el asiento de cierre hasta que estén todos resueltos.

---

## Flujo 9 — Cierre de ejercicio

### D9.1 · Permiso único `CIERRE_EJECUTAR` (mayo 2026)

**Decisión**: las tres acciones del cierre (regularización, cierre, apertura) comparten un permiso único `CIERRE_EJECUTAR`. Los tres son actos del mismo tesorero matriz en la misma sesión de cierre anual; no tiene sentido granularizar más.

Las queries asociadas (`balance_pcesfl`, `cuenta_resultados`, `estado_cierre`, `libro_diario_csv`) requieren `CIERRE_CONSULTAR` (sólo lectura), que se asigna también al rol AUDITOR.

**Consecuencias técnicas**:
- Reemplazar `RequireTransaction("ECO_ASIENTO_APROBAR")` por `RequireTransaction("CIERRE_EJECUTAR")` en `generar_asiento_regularizacion`, `generar_asiento_cierre`, `generar_asiento_apertura`.
- Añadir `RequireTransaction("CIERRE_CONSULTAR")` a las 4 queries de consulta.

---

### D9.2 · Cierre solo por TESORERO de la matriz (mayo 2026)

**Decisión**: `CIERRE_EJECUTAR` se asigna **únicamente al rol TESORERO** (matriz). Aunque haya tesorería delegada en agrupaciones, el cierre del ejercicio es un acto único organizacional — afecta a las cuentas anuales del conjunto, que solo se depositan una vez ante el Protectorado / Tribunal de Cuentas.

`CIERRE_CONSULTAR` se asigna a TESORERO + AUDITOR.

**Coherente con**: D1.6 (plan de cuentas), D7.1 (aprobación final de justificantes), D8.4 (bloqueo de cierre por conciliación).

---

### D9.3 · Pre-requisitos bloqueantes: todos los asientos CONFIRMADOS (mayo 2026)

**Decisión**: antes de ejecutar el asiento de **regularización** (primer paso del cierre), el sistema verifica que **todos los asientos del ejercicio están en estado `CONFIRMADO`** (ninguno en `BORRADOR`). Si quedan borradores, se aborta con la lista.

Antes de **cierre** propiamente dicho, además se aplica D8.4 (conciliación bancaria completa).

Antes de **apertura del ejercicio siguiente**, debe existir un asiento de CIERRE confirmado del ejercicio cerrado.

**Consecuencias técnicas**:
- En `generar_asiento_regularizacion`: query `count(AsientoContable.estado=BORRADOR, ejercicio=X) == 0`.
- La pre-validación de conciliación (D8.4) ya está en `generar_asiento_cierre`.
- En `generar_asiento_apertura`: query del asiento CIERRE confirmado.

**Para el manual**:
- *Tesorero*: antes de cerrar, asegúrate de que no quedan asientos en estado Borrador. Confírmalos uno a uno desde Contabilidad → Asientos.

---

### D9.4 · UI: vista dedicada `/economico/cierre-ejercicio` + acceso desde Contabilidad (mayo 2026)

**Decisión**: el flujo de cierre se expone en una **vista dedicada** (`/economico/cierre-ejercicio`) con todas las piezas del cierre en una sola pantalla:
- Checklist del estado (asientos confirmados ✓/✗, balance cuadra ✓/✗, conciliación completa ✓/✗, regularización hecha ✓/✗, cierre hecho ✓/✗, apertura siguiente hecha ✓/✗).
- Botones para ejecutar las 3 acciones (regularización, cierre, apertura) habilitados secuencialmente.
- Visualización inline del Balance PCESFL y la Cuenta de Resultados.
- Descarga del Libro Diario (CSV).

Desde `Contabilidad.vue` (pestaña existente) hay un acceso destacado **"Ir al cierre del ejercicio"** que enlaza a esta vista.

---

## Flujo 10 — Cuentas Anuales

### D10.1 · Snapshot completo persistido por ejercicio (mayo 2026)

**Decisión**: una nueva tabla `cuentas_anuales` con **una fila por ejercicio** que persiste un snapshot inmutable de:
- `balance_pcesfl` (JSON con la estructura completa).
- `cuenta_resultados` (JSON con la estructura completa).
- `memoria` (JSON con las 12 secciones — ver D10.2).
- `excedente` (Decimal, copia para indexación/búsqueda).
- `fecha_aprobacion`, `aprobado_por_id`, `acta_referencia`.
- `fecha_deposito`, `archivo_acuse_recibo` (PDF del registro).
- `estado` ∈ {BORRADOR, APROBADAS, DEPOSITADAS}.

**Por qué snapshot**: las cuentas anuales depositadas son un documento legal inmutable. Aunque el ejercicio se "reabriera" (caso excepcional), las CCAA depositadas deben conservar lo que se firmó, no recalcular.

**Para el manual**:
- *Tesorero*: cuando generas las CCAA, el sistema toma una foto del balance y la cuenta de resultados del ejercicio cerrado. Esa foto no cambia aunque alguien modifique algo después.

---

### D10.2 · Memoria con plantilla guiada de 12 apartados PCESFL (mayo 2026)

**Decisión**: la Memoria económica se redacta con una plantilla guiada según RD 1491/2011, con los 12 apartados obligatorios:
1. Actividad de la entidad.
2. Bases de presentación de las cuentas anuales.
3. Excedente del ejercicio.
4. Normas de registro y valoración.
5. Inmovilizado material, intangible e inversiones inmobiliarias.
6. Usuarios y otros deudores de la actividad propia.
7. Beneficiarios-acreedores.
8. Activos y pasivos financieros.
9. Fondos propios.
10. Situación fiscal.
11. Subvenciones, donaciones y legados.
12. Aplicación de elementos patrimoniales a fines propios.

Cada apartado tiene un texto libre + opcionalmente tablas auto-rellenadas con datos del ejercicio (saldos, importes, comparativos con el año anterior).

**Consecuencias técnicas**:
- `memoria` se persiste como JSON con claves `apartado_1`, `apartado_2`, ..., `apartado_12`.
- En la UI hay un acordeón por apartado con instrucciones del PCESFL y un editor de texto.

**Para el manual**:
- *Tesorero*: redactar la Memoria es la tarea más larga del cierre. Hazlo en pestañas, una por apartado. El sistema rellena algunos datos numéricos automáticamente.

---

### D10.3 · Workflow de 3 estados con aprobación de junta (mayo 2026)

**Decisión**: las Cuentas Anuales recorren tres estados:
1. **BORRADOR** — el tesorero las prepara: rellena Memoria, revisa Balance y Cuenta de Resultados auto-generados.
2. **APROBADAS** — la junta directiva las aprueba en acta. Se registra `fecha_aprobacion`, `aprobado_por_id` (presidente) y `acta_referencia`. A partir de aquí, los textos quedan inmutables.
3. **DEPOSITADAS** — el tesorero/secretario las deposita ante el Protectorado / Tribunal de Cuentas / Registro de Asociaciones. Se registra `fecha_deposito` y el `archivo_acuse_recibo` (PDF del sellado del registro).

**Norma legal**: Ley 50/2002 art. 25.2 (fundaciones) y LO 1/2002 art. 14 (asociaciones). Las cuentas se aprueban por el órgano de gobierno (junta o asamblea) según los estatutos.

**Para el manual**:
- *Tesorero*: prepara las CCAA (estado Borrador).
- *Presidente / Junta*: aprueba en acta y marca el estado APROBADAS con la referencia del acta.
- *Tesorero / Secretario*: deposita ante el registro competente y sube el acuse de recibo.

---

### D10.4 · Exportación PDF con reportlab / weasyprint (mayo 2026)

**Decisión**: el documento final de las CCAA se exporta en **PDF**. Backend genera el PDF con `reportlab` (ya pendiente de instalar para Libro Diario y certificado Modelo 182).

Mientras `reportlab` no esté instalado en el contenedor, se ofrece una vista HTML imprimible como fallback (el tesorero usa "Imprimir → Guardar como PDF" del navegador).

**Implicación**: el tag `🟡 Instalar reportlab` ya está en el backlog desde el flujo 2. La instalación es prerrequisito para v1 completo de los flujos 2, 9, 10 y 11.

---

## Flujo 11 — Modelo 182 (declaración fiscal de donaciones)

### D11.1 · Solo donaciones con NIF identificable (mayo 2026)

**Decisión**: el fichero del Modelo 182 incluye **solo** donaciones del ejercicio para las que se puede identificar fiscalmente al donante:
- Donaciones con `donante_dni` rellenado, o
- Donaciones de miembros (`miembro_id`) cuyo socio tiene NIF registrado, y `anonima = false`.

Las donaciones anónimas o sin NIF no se incluyen — el donante no podría deducirlas y la AEAT rechaza registros sin NIF.

**Consecuencias técnicas**:
- El servicio filtra por `(donante_dni IS NOT NULL OR miembro.nif IS NOT NULL) AND anonima = false`.
- La UI muestra cuántas donaciones quedan excluidas y por qué motivo (anónima, sin NIF), para que el tesorero pueda completar datos si procede.

**Para el manual**:
- *Tesorero*: si una donación importante queda excluida, revísala: completa el NIF del donante externo o pide al socio que actualice su NIF en la ficha de miembro.

---

### D11.2 · Tipo de donante inferido del NIF (mayo 2026)

**Decisión**: no se añade un campo nuevo `tipo_donante`. El servicio infiere si es Persona Física (PF) o Persona Jurídica (PJ) a partir del **patrón del NIF**:
- Empieza por dígito o por K/L/M/X/Y/Z → PF (DNI, NIE, residente extranjero).
- Empieza por A/B/C/D/E/F/G/H/J/N/P/Q/R/S/U/V/W → PJ (CIF español).

Los códigos del Modelo 182 son: `1`=Persona Física, `2`=Persona Jurídica.

**Consecuencias técnicas**:
- Helper `_inferir_tipo_donante(nif: str) -> int` en `Modelo182Service`.
- Validación previa: si el NIF no encaja en ninguno de los patrones, se marca como excluido y se muestra al tesorero.

**Para el manual**:
- *Tesorero*: el sistema deduce automáticamente si el donante es persona física o jurídica del NIF. Si la inferencia es incorrecta para algún caso particular, corrige el NIF.

---

### D11.3 · Genera fichero AEAT (TXT) + PDF resumen (mayo 2026)

**Decisión**: el flujo produce dos documentos:
1. **Fichero AEAT 182** — texto plano posicional, codificación ISO-8859-1, registros de 250 caracteres con `\r\n`. Se sube directamente a la sede electrónica de la AEAT.
2. **PDF resumen** — listado por donante (NIF, nombre, total, tipo) + totales globales. Para archivo interno y revisión por la junta.

**Consecuencias técnicas**:
- `Modelo182Service.generar_fichero_aeat(ejercicio) -> bytes` (TXT).
- `Modelo182Service.generar_pdf_resumen(ejercicio) -> bytes` (PDF con reportlab).
- Mutations GraphQL devuelven ambos en base64.

---

### D11.4 · Tabla `presentaciones_modelo_182` para trazabilidad (mayo 2026)

**Decisión**: una tabla nueva registra cada presentación a la AEAT:
- `ejercicio` (único)
- `fecha_envio` — cuándo se subió el TXT a la AEAT.
- `codigo_aeat` — código de presentación que devuelve la AEAT al recibir el fichero.
- `archivo_acuse` — URL/path al PDF del acuse de recibo (justificante de presentación).
- `n_donantes`, `importe_total` (copia del momento del envío).
- `observaciones`.

Permite:
- Detectar duplicidades (no enviar dos veces el mismo año por error).
- Histórico para auditoría: qué se envió y cuándo se acusó recibo.
- Mostrar en la UI los ejercicios ya presentados vs pendientes.

**Para el manual**:
- *Tesorero*: tras subir el TXT a la AEAT y recibir el acuse, ven a SIGA → Modelo 182 y registra la presentación con la fecha, el código AEAT y sube el PDF del acuse.

### D11.5 · Claves AEAT A / B por tipo de donación (mayo 2026)

**Decisión**: el agregado del Modelo 182 separa por (NIF, clave AEAT), no solo por NIF.

La AEAT distingue claves en el Modelo 182:
- **A** — Donativo dinerario.
- **B** — Donativo en especie (bienes).
- **C** — Cuotas de asociados con derecho a deducción (no aplica hoy en SIGA: las cuotas no se declaran como donativo).

Tras el flujo 6, una `Donacion` lleva `tipo ∈ {DINERARIA, ESPECIE}`. El servicio mapea:
- `DINERARIA` → clave **A**, importe = `Donacion.importe`.
- `ESPECIE` → clave **B**, importe = `Donacion.valoracion` (la valoración de tasación, no `importe`).

Un donante que aporta dinero Y especie en el mismo ejercicio genera **dos líneas** en el TXT AEAT y dos filas en la tabla del agregado.

**Alternativa descartada**: una sola línea con el sumatorio y una clave única. No cumple la norma — los datos resultan inválidos para la AEAT.

**Consecuencias técnicas**:
- `Modelo182Service.generar_agregado()` cambia su clave de agrupación de `nif` a `(nif, clave)`.
- `Modelo182DonanteType` expone el campo `clave: str`.
- `Modelo182.vue` añade columna "Clave" con badge color (A verde, B azul).
- Casos sin valoración en ESPECIE pasan a "excluidos" con motivo "Donación en especie sin valoración".

**Pendiente futuro (en backlog)**:
- Clave **C** (cuotas): decidir si las cuotas SIGA son deducibles y cómo declararlas separadas de las donaciones.
- "Indicador de recurrencia" (Ley 49/2002 art. 19.3 — deducción reforzada si el donante lleva ≥3 años con donaciones iguales o crecientes): añadir bandera en la línea AEAT.

**Para el manual**:
- *Tesorero*: cuando registres una donación, elige el tipo correcto (dineraria vs en especie). El sistema asignará la clave A o B automáticamente al generar el Modelo 182.
- *Tesorero*: si una persona dona dinero y bienes en el mismo año, **emite dos certificados anuales** (uno A y otro B). Eso es lo que la Ley 49/2002 exige.

---

## Flujo 6 — Donaciones

(Decisiones tomadas tras consultar [chat_donaciones.md](../chat_donaciones.md) — especificación funcional del módulo).

### D6.1 · Workflow extendido REGISTRADA → COBRADA → ANULADA (mayo 2026)

**Decisión**: una donación recorre los estados:
1. **REGISTRADA** — recibida la información pero no se ha confirmado el cobro (ej. compromiso de transferencia futura).
2. **COBRADA** — el dinero está en la cuenta de la entidad o el bien físico ha sido recibido. Solo en este estado se genera el asiento contable y se permite emitir certificado.
3. **ANULADA** — registro erróneo o devuelto. Sin asiento contable; si ya lo había, se anula.

**Estado adicional implícito**: `certificado_emitido` (bool) es ortogonal al estado — una donación COBRADA puede o no tener certificado.

---

### D6.2 · Asiento contable automático al cobrar (mayo 2026)

**Decisión**: al pasar a COBRADA, el sistema genera automáticamente:
- `ApunteCaja` en la `cuenta_bancaria_id` indicada (si es dineraria) — tipo INGRESO, origen DONACION.
- Asiento contable Debe `572` (Bancos) / Haber `730` (Donaciones y legados imputados a resultados) vía `RegistroContable` con regla `DONACION/INGRESO`.
- Para donaciones **en especie**: no hay `ApunteCaja` (no entra dinero) pero sí asiento Debe `xxx` (cuenta del bien — material/inmovilizado según corresponda) / Haber `730` con el importe de valoración.

**Coherente con**: flujo 5 (cobro manual de cuotas) — misma cadena recibo+apunte+asiento.

---

### D6.3 · Certificado anual agrupado por donante (mayo 2026)

**Decisión**: el certificado fiscal (Ley 49/2002 art. 24) se emite **una vez al año por donante**, agrupando todas las donaciones COBRADAS del ejercicio. PDF con reportlab que incluye los datos obligatorios:
- NIF + denominación de la entidad.
- NIF + nombre del donante.
- Total agregado del ejercicio.
- Detalle por donación (fecha, forma de pago, importe).
- Literal "La entidad está acogida al régimen especial de la Ley 49/2002".
- Literal "La donación es irrevocable, pura y simple".
- Número de certificado correlativo (formato `CERT-{YYYY}-{NNNNN}`).
- Firma/sello de la entidad (placeholder gráfico en v1).

---

### D6.4 · Permiso de registro: TESORERO (matriz y agrupación) (mayo 2026)

**Decisión**: las transacciones existentes (`DON_LIST`, `DON_CREATE`, `DON_CERT`) se asignan a TESORERO. La donación lleva `agrupacion_id` derivada del tesorero que la registra.

---

### D6.5 · v1: tipo dineraria/especie + carácter; recurrentes SEPA a v2 (mayo 2026)

**Decisión**: en v1 se implementan los campos `tipo` (DINERARIA / ESPECIE) y `caracter` (PUNTUAL / RECURRENTE), pero el comportamiento recurrente (generación automática de cargos vía mandato SEPA, gestión de fallidos) queda **aplazado al v2**.

En v1, una donación recurrente se trata como puntual a efectos prácticos — el campo se conserva para futura activación. Las donaciones en especie sí se implementan completamente: se piden descripción, valoración y documento de tasación adjunto.

**Aplazado a v2** (anotado en `pendientes_extemporaneos.md`):
- Mandato SEPA donaciones recurrentes.
- Generación periódica automática de cargos.
- Reenvío de fallidos como remesa específica.

---

### D6.6 · Certificado separado por tipo (dineraria A vs especie B) (mayo 2026)

**Decisión**: un donante que en el mismo año recibe **dinerarias y en especie** obtiene **dos certificados separados**:
- Certificado A — total dineraria del ejercicio (clave A en Modelo 182).
- Certificado B — total en especie del ejercicio con desglose de bienes y valoraciones (clave B).

Razón: el Modelo 182 (flujo 11) lleva una clave única por línea, y la deducción puede tener trato distinto.

**Coherencia con flujo 11**: la D11.x debe ampliarse para emitir una línea por (donante, clave). Anoto el ajuste en el backlog.

---

## Flujo 5 — Cobro manual de cuotas

### D5.1 · Punto único de entrada: marcar cobrado el recibo (mayo 2026)

**Decisión**: cualquier cobro manual de una cuota (transferencia, efectivo, tarjeta) se registra desde el **recibo**. La acción "Marcar cobrado" de `Recibos.vue` (mutation `marcar_recibo_cobrado`) se amplía para:

1. Pedir `cuenta_bancaria_id` (destino del ingreso).
2. Marcar el recibo `COBRADO` con `modo_cobro`, `fecha_cobro`, `importe_pagado`.
3. Actualizar la `CuotaAnual` asociada: `importe_pagado` += importe, estado → `Cobrada` si total cubierto.
4. Crear `ApunteCaja` en la cuenta bancaria con tipo INGRESO, origen CUOTA.
5. Generar `AsientoContable` (Debe 572 / Haber 721) vía `RegistroContable`.

Todo en una transacción atómica.

Si el cobro es por un concepto sin cuota (derrama, formación), primero se emite un recibo individual extraordinario (flujo 2 — A2) y luego se marca cobrado.

**Alternativas descartadas**:
- Dos entradas (desde recibo y desde tesorería) — rompe la trazabilidad recibo → cobro y duplica código.
- Ingresos genéricos sin recibo — para subvenciones/ventas hay que crear su flujo propio (módulo Tesorería puro), no mezclarlo con cobro de cuotas.

**Consecuencias técnicas**:
- `TesoreriaService.registrar_pago_cuota_manual` queda como helper interno invocado desde `marcar_recibo_cobrado`. NO se expone directamente como mutation principal (la actual `registrar_pago_cuota_manual` se mantiene por compatibilidad pero se marca como deprecada en el doc).
- `ReciboService.marcar_cobrado` se reescribe para orquestar todo (recibo + cuota + apunte + asiento) en una transacción.
- El modal "Marcar cobrado" del Recibos.vue añade selector de cuenta bancaria.

**Para el manual**:
- *Tesorero*: para registrar un pago manual, ve a Recibos → busca el recibo del socio → "Marcar cobrado" → indica cuenta bancaria, modo (transferencia/efectivo/tarjeta) y fecha. Una sola pantalla, todo registrado.
- Si quieres cobrar algo que no es cuota (derrama, formación), primero emite un recibo individual extraordinario desde Recibos → "+ Emitir recibo" → luego márcalo cobrado.

---

## Flujo 3 — Generación y envío de remesa SEPA

### D3.1 · Emisión de recibo según tipo de cobro (mayo 2026)

**Decisión**: el flujo de emisión depende del modo de cobro:
- **SEPA** → al generar la remesa se emiten en bloque los recibos (uno por orden) automáticamente.
- **Manual** (transferencia, efectivo, tarjeta) → el tesorero emite el recibo explícitamente desde la pantalla de Recibos (flujo 2).

**Alternativas descartadas**:
- Solo "antes de remesa" — rompe ergonomía SEPA: obliga a dos pulsaciones cuando una basta.
- Solo "al generar remesa" — bloquea cobros no SEPA: el recibo no existiría hasta que se hace la remesa.

**Consecuencias técnicas**:
- `RemesaService.generar_remesa(...)` invoca `ReciboService.emitir_lote(...)` al final, con `modo_cobro="SEPA"` y enlazando `Recibo.orden_cobro_id`.
- `RemesaService.generar_remesa_extraordinaria(...)` y `generar_remesa_fallidos(...)` hacen lo mismo (con su tipo y concepto).
- Los recibos manuales se generan vía la pantalla de Recibos sin pasar por remesa.

**Para el manual**:
- *Tesorero*: si cobra por SEPA, no necesita "emitir recibos" antes; la remesa lo hace. Para cobros manuales, emite primero desde la pantalla de Recibos.

---

### D3.2 · Una remesa ordinaria por ejercicio (mayo 2026)

**Decisión**: una sola remesa ORDINARIA por ejercicio para toda la organización. Las EXTRAORDINARIAS (derramas, congresales) y los REENVÍOS no cuentan en este límite.

**Alternativas descartadas**:
- Varias al año (mensual/trimestral) — la organización tiene cuota anual; cobrarla por partes complica conciliación y mandatos SEPA.
- Una por agrupación al año — la tesorería actual es centralizada en una sola cuenta corriente.

**Consecuencias técnicas**:
- `generar_remesa(ejercicio, ...)` valida que no exista ya una remesa ORDINARIA no anulada para ese ejercicio; aborta si existe.
- En el UI, el botón "+ Nueva remesa ordinaria" se deshabilita si ya hay una activa del ejercicio.

**Para el manual**:
- *Tesorero*: lanza una remesa por año. Si necesita re-presentar fallidos, usa "Remesa de reenvío" (no cuenta como ordinaria).

---

### D3.3 · Excluir cuotas sin IBAN y mostrar la lista al tesorero (mayo 2026)

**Decisión**: si un socio no tiene IBAN registrado, su cuota no se incluye en la remesa. En la pre-visualización (pantalla 5.2 paso 2) se muestra la lista de excluidos con nombre + cuota, antes de generar. El tesorero confirma o cancela.

**Alternativas descartadas**:
- Excluir silenciosamente — el tesorero descubre la merma a posteriori, mala UX y riesgo de descuadres.
- Abortar — penaliza al tesorero por un dato que puede no controlar (IBAN del socio); bloquea cobros recuperables del resto.

**Consecuencias técnicas**:
- `RemesaService.previsualizar_remesa(ejercicio)` devuelve `{cuotas_incluidas: int, cuotas_excluidas: list, importe_total: Decimal}`.
- `generar_remesa(...)` ignora cuotas sin IBAN y registra en `observaciones` el número de excluidos.

**Para el manual**:
- *Tesorero*: si en la previsualización ve socios sin IBAN, puede (a) cancelar y completar IBANes desde Membresía, o (b) generar la remesa sin ellos y cobrarles después manualmente.

---

### D3.4 · Una cuota no puede estar en dos remesas activas (mayo 2026)

**Decisión**: si una cuota ya está en una `OrdenCobro` cuya remesa está en estado `Borrador`, `Generada`, `Enviada`, `Procesada` o `Parcial` (no anulada ni totalmente fallida), no se incluye en una nueva remesa. Evita doble cobro.

**Excepción**: si la `OrdenCobro` previa está en estado `Fallida`, la cuota está disponible para la remesa de reenvío (flujo 4 A4).

**Alternativas descartadas**:
- Sin restricción — riesgo real de doble cobro bancario, devoluciones del banco, mala imagen.

**Consecuencias técnicas**:
- `generar_remesa(...)` excluye cuotas con `OrdenCobro` activa.
- En la previsualización aparecen como "ya incluidas en remesa REM-XXX-XXX" si las hay.

**Para el manual**:
- *Tesorero*: si una cuota desaparece de la previsualización, está ya en otra remesa.

---

### D3.7 · Revisión de D3.1 — emitir / revisar / remesar como pasos separados (mayo 2026)

**Decisión**: revertimos D3.1. El flujo correcto es:
1. **Emitir lote de recibos** (flujo 2 — A1). El tesorero pulsa "Emitir lote" para el ejercicio; se crean recibos `EMITIDO` con `modo_cobro=SEPA` (los que paguen por domiciliación; el modo lo determina la `CuotaAnual` o el `TipoMiembro`).
2. **Revisar/corregir** (flujo 2 — A3/A4/A5/A6). Durante el periodo que decida el tesorero: anular recibos erróneos, marcar como cobrado manualmente alguno que ya haya pagado por transferencia, descargar PDFs para revisar, etc.
3. **Generar remesa** (flujo 3 — A2). Toma los recibos `EMITIDO + modo_cobro=SEPA + tipo=CUOTA_ORDINARIA` cuyas cuotas siguen `Pendiente` y no están ya en otra orden activa.

**Alternativas descartadas**:
- D3.1 original (auto-emisión al remesar): contradice D2.1 y no permite revisión humana antes de la presentación bancaria.
- Modelo configurable por organización: añade complejidad para una decisión que el usuario quiere coherente en todas las instalaciones.

**Consecuencias técnicas**:
- `RemesaService.generar_remesa` **deja de invocar** `_emitir_recibos_para_remesa`. En su lugar, el filtro `_cuotas_elegibles` se sustituye por `_recibos_sepa_emitidos_para_remesa(ejercicio, agrupacion_id)` que devuelve recibos EMITIDO+SEPA+CUOTA_ORDINARIA cuyas cuotas Pendientes no están ya en orden activa.
- Cada `OrdenCobro` enlaza con el recibo preexistente (`Recibo.orden_cobro_id = orden.id`).
- Si no hay recibos emitidos, la generación de remesa **falla con mensaje claro** ("No hay recibos SEPA emitidos pendientes. Emite primero el lote desde Recibos.").
- La pre-visualización del flujo 3 muestra "recibos emitidos a incluir" en lugar de "cuotas pendientes".

**Para el manual**:
- *Tesorero*: el procedimiento típico anual es: en enero, emitir el lote → durante febrero, revisar y corregir → en febrero/marzo, generar la remesa SEPA. No se pueden meter cuotas en la remesa sin que su recibo esté ya emitido y validado.

---

### D3.6 · Prefijo de agrupación en referencia de remesa — pospuesto a tesorería delegada (mayo 2026)

**Decisión**: hoy las referencias de remesa son `REM-{YYYY}-{NNN}` (sin agrupación territorial). Cuando se implemente la tesorería delegada (cada agrupación con su acreedor SEPA propio), pasarán a `REM-{PREFIJO}-{YYYY}-{NNN}` y el `EndToEndIdentification` SEPA derivado quedará `REM-{PREFIJO}-{YYYY}-{NNN}-{nseq:03d}`.

**Por qué ahora no**: D3.2 (una sola remesa ordinaria por ejercicio) + D3.5 (un único acreedor SEPA central) hacen innecesario el prefijo. Solo aporta valor cuando hay varias agrupaciones emitiendo remesas con identificadores SEPA distintos.

**Coherencia con otros códigos**:
- El **número de recibo** sí lleva agrupación hoy (D2.3): `REC-{NOMBRE_CORTO}-{YYYY}-{NNNNN}` cuando aplica.
- El **EndToEndId SEPA** (D4.1) deriva de la referencia de remesa, así que automáticamente la heredará cuando se aplique D3.6.

**Para el manual**:
- *Tesorero*: hoy en el extracto bancario del socio aparece la referencia `REM-2025-005-042`; en su recibo aparece `REC-MAD-2025-00042` (con prefijo de su agrupación, si la organización es descentralizada). Dos códigos distintos para usos distintos.

---

### D3.5 · Datos del acreedor SEPA en Parámetros Generales (mayo 2026)

**Decisión**: los 4 datos del acreedor SEPA (`creditor_name`, `creditor_iban`, `creditor_bic`, `creditor_id`) se guardan en `ParametrosGenerales` con sección "SEPA" dedicada en la UI. Un único acreedor para toda la organización.

**Alternativas descartadas**:
- Extender `CuentaBancaria` — exceso para una organización con tesorería centralizada (descartado conjuntamente con D3.2).
- Configuraciones planas (`sepa.creditor_*`) — sin UI, dificulta mantenimiento.

**Consecuencias técnicas**:
- Añadir sección "SEPA" en `ParametrosGenerales.vue` con 4 campos.
- Tabla `parametros_generales` con claves `sepa_creditor_name`, `sepa_creditor_iban`, `sepa_creditor_bic`, `sepa_creditor_id`.
- `RemesaService.generar_xml_sepa(remesa_id)` los lee internamente; ya no requiere parámetros.
- Validación: la remesa no puede generar XML si falta alguno de los 4 datos del acreedor.

**Para el manual**:
- *Administrador*: rellena la sección "SEPA" de Parámetros Generales una sola vez (al instalar el sistema) y la mantiene si la cuenta del acreedor cambia.
- *Tesorero*: si al intentar generar XML sale "faltan datos del acreedor", avisa al administrador.

---

## (Plantilla para próximas decisiones)

### D{x}.{n} · Título de la decisión (fecha)

**Decisión**: …

**Alternativas descartadas**: …

**Consecuencias técnicas**: …

**Para el manual**:
- *Rol X*: …
- *Rol Y*: …
