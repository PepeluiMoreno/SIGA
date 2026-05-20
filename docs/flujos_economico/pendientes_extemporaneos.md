# Backlog de comentarios extemporáneos

Anotaciones del usuario sobre fallos de UI, disconformidades, ideas o detalles observados **durante el desarrollo de otra funcionalidad**, que no son el foco del ciclo en marcha y que se atenderán al cierre del mismo.

**Regla**: cuando se cierra el ciclo de desarrollo actual (flujo o lote), se repasa este backlog y se decide qué entra en el siguiente ciclo. Lo que entre se mueve a su flujo correspondiente o se promueve a un mini-ciclo propio.

**Cómo se anota cada entrada**:
- Fecha y contexto (qué ciclo estaba en marcha cuando se observó).
- Descripción concreta del problema o idea.
- Pantalla / componente afectado.
- Severidad orientativa: 🔴 bloqueante · 🟡 mejora visible · 🟢 nice-to-have.

---

## Pendientes abiertos

### 2026-05-20 — roadmap de Tesorería (placeholders retirados de la UI)

Al limpiar `Tesoreria.vue` se retiraron los tiles "placeholder" de funcionalidades aún no implementadas (la vista quedaba dominada por tiles inertes y algunos engañaban — la feature ya existía en otra vista). Se registran aquí para no perderlos; cuando toque, cada uno se promueve a su propio mini-ciclo. Severidad 🟢 salvo que se decida otra cosa.

**Caja y bancos** — 🟢 CRUD de cuentas bancarias propias · 🟢 Mandatos SEPA (vigentes de socios) · 🟢 Caja chica · 🟢 Flujo de caja proyectado (30/60/90/180 días) · 🟢 Indicadores PMC/PMP · 🟢 Simulación de escenarios · 🟢 Soporte multidivisa.

**Cuentas a cobrar** — 🟢 Subvenciones (oficiales y privadas) · 🟢 Patrocinios y mecenazgo · 🟢 Ingresos por actividades propias (cursos, eventos, publicaciones) · 🟢 Ingresos financieros · 🟢 Instrumentos: efectos a cobrar (letras, pagarés, cheques).

**Cuentas a pagar** — 🟡 XML SEPA Credit Transfer (pain.001, transferencias salientes — el código de remesas SEPA es reutilizable) · 🟡 Facturas de proveedores · 🟢 Nóminas y Seguridad Social · 🟢 Suministros recurrentes · 🟡 Pagos a profesionales con retención IRPF (base del Modelo 111) · 🟢 Impuestos y tributos · 🟢 Instrumentos: efectos a pagar.

**Configuración** — 🟢 Plantillas de email (encaja en Comunicación Interna) · 🟢 Catálogo de conceptos de subvención · 🟢 Catálogo de proveedores recurrentes.

**Cumplimientos legales / fiscales** — 🟡 Modelo 111 (retenciones IRPF, trimestral) · 🟡 Modelo 190 (resumen anual) · 🟢 Modelo 347 (operaciones >3.005 €) · 🟢 Modelo 200 (Impuesto de Sociedades, si hay actividad económica sujeta) · 🟢 Calendario fiscal del ejercicio · 🟢 Informes y auditoría externa.

### 2026-05-20 — durante backlog (exportación Excel de socios)

- 🟡 **El histórico económico del socio no debe ocultarse aunque deje de pagar cuota** — cuando un socio cambia a un tipo de socio que no paga cuota (`requiereCuota = false`), los sub-acordeones de cuotas en "Datos económicos" de `MiembroDetail.vue` se ocultan (hoy gateados por `requiereCuota`). Pero su **histórico** debe seguir siendo visible: historial de cuotas pasadas, historial de solicitudes de reducción/modificación de cuota, incrementos voluntarios, etc. — aunque su cuota actual sea cero. *Solución prevista*: separar el gating — "Procedimiento de pago de cuotas" y "Cuota aplicada" (configuración de cuota futura) sí dependen de `requiereCuota`; pero "Historial de cuotas" y el historial de solicitudes deben mostrarse siempre que existan registros, con independencia del tipo actual. *Pantalla*: `MiembroDetail.vue` → acordeón "Datos económicos".

### 2026-05-19 — durante refactor flujo 7 (Justificantes — modo delegación)

- 🟢 **Justificantes: ampliar lista de personas elegibles a no-socios** — hoy "Registro de justificantes de gastos" (modo delegación del tesorero) sólo admite **socios** como personas que incurrieron en el gasto. En el futuro se ampliará a:
  - **Voluntarios de una campaña** que no son socios.
  - **Personas externas vinculadas a la organización** (colaboradores ocasionales, ponentes, técnicos contratados puntualmente para un evento).
  Implica: modelo de "personas vinculadas" o reutilizar `Miembro` con un flag `es_vinculo_externo`, datos fiscales mínimos para emitir el pago, y revisar la regla de "miembros elegibles por grupo de la actividad". *Decisión actual*: solo socios; cuando aparezca el caso, abrir su propio ciclo.

### 2026-05-19 — durante refactor de taxonomía de actividades

- 🟡 **Refactor masivo `confirm()` / `alert()` / `prompt()` → modales bonitos** — hoy hay ~8 archivos con `confirm()`, ~13 con `alert()` y ~4 con `prompt()` (frontend `*.vue`). El primero ya se está sustituyendo por `ConfirmActionModal` (creado en `components/common/`); el alert se sustituirá por un futuro `InfoModal` (o un sistema de toasts si así lo decidimos). El prompt es minoritario y suele ser para "introduce un motivo" — se cubre con un modal de input. **Criterio**: no toda advertencia merece modal — un éxito breve es mejor toast (no bloqueante); un fallo crítico va en modal. Hacer en su propio mini-ciclo de UX, revisando uso por uso. *Pantallas afectadas*: `Donaciones.vue`, `Recibos.vue`, `Conciliacion.vue`, `Justificantes.vue`, `Remesas.vue`, `Contabilidad.vue`, `CuentasAnuales.vue`, `CuotasEjercicio.vue`, `CampaniaForm.vue`, `CatalogoGenerico.vue`, etc.

- 🟡 **CRUD completo de apuntes de caja (bitácora + edición/anulación)** — pendiente: (a) terminar la pestaña "Bitácora de movimientos" iniciada en `Contabilidad.vue` (filtros tipo/origen/ejercicio/búsqueda ya implementados, falta integración con la query `GET_BITACORA_MOVIMIENTOS`); (b) decidir y construir UI de **edición/anulación** de apuntes — los apuntes son inmutables por diseño contable, pero podemos ofrecer "Anular apunte" (genera contraapunte) y "Editar metadatos no contables" (concepto, observaciones, imputación a actividad). Ciclo dedicado para no precipitar el diseño contable.

### 2026-05-19 — durante flujo 6 (Donaciones)

- 🟢 **Manuales filtrados por rol en `/ayuda`** — al completar los 11 flujos del módulo económico (todos con acordeón en `Ayuda.vue`), procede ahora derivar **manuales por rol** consolidando solo las pantallas/acciones que cada rol puede ejecutar: `manual_tesorero_central.md`, `manual_tesorero_agrupacion.md`, `manual_junta.md`, `manual_socio.md`, `manual_auditor.md` (estructura prevista en `flujos_economico/README.md`). *Encaja con*: módulo de ayuda. *Coste*: medio, requiere mapear cada `transacciones.json` con el flujo correspondiente.

- 🟡 **Módulo Secretaría — leer `docs/chat_secretaria.md` antes de empezar** — material de partida del usuario para guiar el desarrollo del módulo de secretaría (alcance funcional, libros oficiales, actas, certificados, registro de entidades, comunicaciones formales, etc.). *Cuándo*: cuando se abra el ciclo de secretaría tras cerrar el módulo económico. *Encaja con*: módulo Secretaría (próximo módulo). *Cómo*: revisar el documento, extraer entidades / flujos / pantallas / permisos y aplicar el mismo workflow (discutir → diseñar → documentar → aprobar → codear) que hemos seguido en económico.

- 🟢 **v2: Donaciones recurrentes con mandato SEPA** — extensión del flujo 6. Cuando una donación tiene `caracter = RECURRENTE`, el sistema debe gestionar:
  - **Mandato SEPA** del donante (referencia única, fecha de firma, IBAN, BIC).
  - **Generación periódica** (mensual/trimestral/anual) de cargos como nuevas filas `Donacion` con fecha del cobro real.
  - **Inclusión en remesa SEPA**: nueva variante en flujo 3 que también empaqueta donaciones recurrentes (no solo cuotas). Considerar añadir `tipo_destino` a `Remesa` o usar `tipo_remesa=DONACION`.
  - **Fallidos**: si un cargo rebota, marcar la donación como ANULADA, notificar al tesorero y opcionalmente al donante. No emitir certificado por esa donación.
  - **Vista de mandatos vigentes** en `Donaciones.vue` (sección "Recurrentes activas") con resumen de próximos cargos.
  En v1 los campos `caracter` y `mandato_id` ya quedan modelados pero la lógica no se activa.

- ✅ **Flujo 11 Modelo 182: ampliar a claves A/B (dineraria/especie)** — RESUELTO 2026-05-19 (D11.4): `Modelo182Service.generar_agregado` agrupa ahora por `(NIF, clave)`. Un donante con donaciones DINERARIA + ESPECIE genera dos líneas. ESPECIE usa la `valoracion` (no `importe`). Fichero AEAT emite la clave correcta (A/B). PDF resumen añade columna "Clave". Type GraphQL `Modelo182DonanteType` expone `clave`. `Modelo182.vue` muestra columna Clave con badge color (verde A, azul B).
  - Pendiente futuro: añadir clave **C** (cuotas de asociados con derecho a deducción — Ley 49/2002 art. 19.1.a) cuando se decida si las cuotas SIGA son deducibles; añadir "indicador de recurrencia" (deducción reforzada Ley 49/2002 art. 19.3 si el donante lleva ≥3 años con donaciones iguales o crecientes).

### 2026-05-19 — durante flujo 10 (Cuentas Anuales)

- ✅ **Agrupaciones — eliminar tarjeta de color sobre la raíz y unificar expand/collapse** — RESUELTO 2026-05-19: `NodoArbol.vue` rediseñado al mismo patrón visual que `CuentaNode.vue` (fila uniforme con caret ▶/▼, indentación por profundidad). Eliminada la tarjeta destacada `bg-indigo-700` del nodo raíz. `DetalleAgrupacionesTerritoriales.vue` provee `expandedMap` reactivo y `toggleNodo` vía `provide`/`inject`, con botón único "Expandir todo / Colapsar todo" arriba del listado y contador de unidades visibles. Sustituidos los `purple-*` (regla del proyecto) por `indigo-*`/`slate-*`.

- 🟢 **Componente común `<TreeView>` para datos jerárquicos** — extraer un componente Vue reutilizable que abstraiga la presentación de árbol expandible/colapsable (caret, sangría por nivel, búsqueda, filtros, expandir/colapsar todo, acciones por nodo). Particularizar después para: (a) Estructura organizativa (`NodoArbol.vue` en membresía), (b) Plan de cuentas (`CuentaNode.vue` en económico), (c) cualquier otro árbol futuro (categorías de actividad, partidas presupuestarias jerárquicas, etc.). Slots para personalizar la fila (icono, nombre, badges, columnas extra, acciones). Lo ideal: `components/common/TreeView.vue` aceptando `:nodes`, `:expanded-map`, `:get-children`, `:render-node` y emitiendo `@toggle`, `@select`. Eliminará duplicación entre las dos vistas actuales. *Encaja con*: refactor de UI común, sin urgencia.

- ✅ **Datos económicos del nuevo socio: tipo de cuota aplicable + motivo de reducción** — RESUELTO 2026-05-19 (D1.7):
  - `Miembro.motivo_reduccion_id` FK opcional añadido (modelo + SQL aplicado).
  - `CuotaService` (generar + recalcular) aplica jerarquía: override individual → motivo del TipoMiembro → cuota base.
  - Sección "Cuota aplicable" en acordeón "Datos económicos" de `MiembroDetail.vue` con resumen del Tipo y selector de motivo individual + advertencia "no afecta a cuotas ya emitidas (D1.5)".
  - Query `GET_MIEMBRO_BY_ID` extendida con `motivoReduccionId` + relación `motivoReduccion`.
  - `useMiembro.loadCatalogos` añade `catalogos.motivosReduccion`.
  - `saveMiembro` (create + update) propaga `motivoReduccionId`.

### 2026-05-19 — durante flujo 8 (conciliación bancaria)

- 🟢 **Integración opcional con Enable Banking (PSD2 open banking)** — desarrollar una funcionalidad opcional de conciliación bancaria automática vía API de Enable Banking (`enablebanking.com`). En lugar de descargar manualmente el CSV/Norma 43 del banco y subirlo a SIGA, el sistema descarga los movimientos vía API PSD2 con autorización OAuth del tesorero. Implica:
  - Registro como TPP (Third Party Provider) en Enable Banking o uso de su modelo SaaS.
  - Flujo OAuth para que el tesorero autorice el acceso a la cuenta (renovable cada 90 días por PSD2).
  - Backend: nueva mutation `sincronizar_extracto_enable_banking(cuenta_id)` que pull los movimientos del periodo y los carga como `ExtractoBancario`.
  - Activable por organización en Parámetros Generales (sección "Conciliación automática").
  - Ventajas: cero descargas manuales, conciliación casi en tiempo real, menos errores de transcripción.
  - Coste: Enable Banking factura por cuenta conectada. Decisión coste/beneficio por organización.
  - Coexiste con el flujo manual (D8.1) como fallback.

### 2026-05-19 — durante flujo 7 (justificantes de gasto)

- 🟡 **Notificaciones internas para cambios de estado del justificante** — integrar con el módulo de Comunicación Interna para que, al cambiar de estado un `JustificanteGasto`, se notifique a la persona correspondiente:
  - PRESENTADO → notificar al `Actividad.responsable_id` ("tienes un justificante pendiente de aceptar").
  - ACEPTADO → notificar al tesorero del ámbito ("tienes un justificante pendiente de aprobar").
  - APROBADO → notificar al presentador ("tu justificante ha sido aprobado, pendiente de pago").
  - PAGADO → notificar al presentador ("se ha registrado el pago de tu justificante").
  - RECHAZADO → notificar al presentador con el motivo.
  Implica: (a) crear plantillas de notificación interna por tipo de transición, (b) event hooks en el `JustificanteGastoService` que disparan eventos, (c) consumir esos eventos desde Comunicación Interna. Encaja con el módulo de notificaciones internas (aviso dentro de la app, no email).


- ✅ **`ApunteCaja.actividad_id` y `campania_id`** — RESUELTO 2026-05-19: añadidos FK opcionales a `actividades`/`campanias` en `apuntes_caja` (modelo + SQL aplicado + mutation `registrarApunteCaja` actualizada). UI de Tesorería: modal "Registrar movimiento manual" accesible desde acordeones A · Caja+bancos ("+ Registrar ingreso/gasto") y C · Cuentas a pagar ("+ Registrar gasto" en Pagos manuales). Permite imputar el apunte a una actividad o campaña para la Memoria anual del flujo 10.

### 2026-05-19 — durante flujo 5 (cobro manual)

- ✅ **Bug al crear grupo de trabajo: falta `tipo_grupo_id` (NOT NULL)** — RESUELTO 2026-05-19: sustituida la mutation strawchemy `crearGrupoTrabajo` (que enviaba `tipo_grupo_id` como UNSET y disparaba `IntegrityError`) por un resolver manual `crearGrupoTrabajoSeguro` en `actividad_resolvers.py` con permiso `TEAM_CREATE`. Comportamiento:
  - Valida `nombre` no vacío.
  - Si `tipo_grupo_id` no se envía, usa el primer `TipoGrupo` activo del catálogo como default (en su defecto, error claro con mensaje).
  - Si se envía, verifica que existe.
  - Si no hay ningún `TipoGrupo` activo, error explicativo en vez de IntegrityError críptico.
  - `NuevoGrupo.vue` migrado a la nueva mutation.

- 🟢 **Exportación a Excel de la lista de socios (módulo Membresía)** — en la ruta `/miembros`, añadir botón "Exportar a Excel" que genere un XLSX con los socios visibles con los filtros aplicados. **Transacción nueva** restringida a roles de **presidencia a nivel territorial o superior** (no a coordinadores). Implica: (a) crear permiso `MBR_EXPORT_XLSX` en `transacciones.json`, (b) endpoint o mutation que devuelva el fichero base64, (c) usar `openpyxl` (pendiente de instalar como `reportlab`), (d) botón en `ListaMiembros.vue`.

- 🟡 **RGPD — auditoría y medidas de cumplimiento** — PARCIALMENTE RESUELTO 2026-05-20: panel "RGPD y privacidad" rediseñado en la ficha de socio (solicitud de supresión por el propio socio, límite de retención calculado, anonimización real vía `anonimizar_miembro`), y **plan completo del módulo transversal** en `docs/modulo_rgpd.md` (responsables, RAT, derechos ARSULIPO, bloqueo de datos + purga diferida, consentimientos, brechas, auditoría). El desarrollo del módulo completo se aborda según las fases de ese documento. Detalle original:
  - **Registro de actividades de tratamiento** (art. 30 RGPD): inventariar qué datos personales se tratan y con qué finalidad.
  - **Derecho de acceso, rectificación, supresión, oposición, portabilidad** (arts. 15–22 RGPD): pantallas para que el socio ejerza sus derechos sin pedirlos por email.
  - **Borrado lógico vs físico de datos personales**: hoy SIGA usa borrado lógico (campo `eliminado`); cumplir el derecho al olvido puede requerir borrado real o seudonimización al cabo de cierto tiempo.
  - **Logs de acceso a datos sensibles** (NIF, dirección, datos económicos): registrar quién consulta qué.
  - **Consentimiento explícito** del socio para comunicaciones no esenciales (emails de marketing/eventos vs avisos obligatorios de la entidad).
  - **Encargado/Responsable del tratamiento**: cláusula informativa al alta y al editar datos.
  - **Cifrado de datos en reposo** (IBAN, NIF) y en tránsito (HTTPS).
  - **DPD (Delegado de Protección de Datos)**: si la entidad supera 250 personas o trata datos especialmente sensibles, es obligatorio.
  - **Plan de incidencias**: protocolo de notificación de brechas en 72 h a la AEPD.
  - Discutir con el usuario qué nivel de profundidad se necesita y qué módulos de SIGA deben adaptarse (probablemente Membresía + Económico + Acceso/auditoría).

### 2026-05-19 — durante flujo 2 (emisión de recibos)

- ✅ **Instalar `reportlab` para generar PDFs** — RESUELTO mayo 2026: `reportlab>=4.0.0` añadido a `pyproject.toml`, `uv.lock` regenerado, imagen reconstruida. `descargarReciboPdf` ya estaba implementado con fallback; `exportarCcaaPdf` (flujo 10) ahora genera PDF profesional A4 con portada, balance, cuenta de resultados y los 12 apartados de la Memoria. Pendiente: usar reportlab para Libro Diario (hoy CSV) y certificado Modelo 182 (flujo 11).

- 🟡 **Plantilla PDF resguardo bancario A5 configurable** — la plantilla del recibo debe ser editable desde Parámetros Generales (logo, dirección de la entidad, texto legal, formato A5 plegable estilo recibo bancario). Hoy, cuando reportlab esté disponible, se generará una versión mínima sin diseño. Mejorar después.

- 🟡 **Plantilla email "RECIBO_EMITIDO" en Comunicación Interna** — para que el tesorero pueda enviar el recibo al socio (flujo 2 — A6), hace falta una plantilla con `modulo='economico'` y variables como `{nombre_socio}`, `{numero_recibo}`, `{importe}`, `{fecha_emision}`. Crear seed mínimo cuando se aborde el envío.

### 2026-05-19 — durante Lote A del flujo 1 (cuotas)

- ✅ **Renombrar `financiero_mutations.py` → `economico_mutations.py`** — RESUELTO 2026-05-19: archivo renombrado vía `git mv`, clase `FinancieroMutation` → `EconomicoFlujosMutation`, import único en `mutations.py` actualizado, comentario residual en `mutations.py` línea 299 corregido. Backend recarga limpio, schema sin pérdidas.

### 2026-05-19 — durante documentación del flujo 1 (cuotas)

- ✅ **Mantenimiento del plan de cuentas — restringido al tesorero matriz** — RESUELTO 2026-05-19:
  - Bug arreglado: `crear_cuenta_contable` (manual) usaba `ECO_ASIENTO_CREAR`; ahora exige `ECO_CUENTA_CREAR`.
  - Mutations strawchemy `crearCuentaContable` / `actualizarCuentaContable` / `eliminarCuentasContables` (sin permission_classes) eliminadas de `mutations.py`. Sustituidas por resolvers manuales en `economico_resolvers.py` con permiso `ECO_CUENTA_CREAR`: `crear_cuenta_contable`, `actualizar_cuenta_contable`, `desactivar_cuenta_contable` (las cuentas nunca se borran físicamente — integridad con asientos históricos).
  - Permisos `ECO_CUENTA_CREAR` + `ECO_CUENTA_LISTAR` asignados a TESORERO (seed reproducible `seed_permisos_plan_cuentas.py`).
  - Pendiente para el futuro: cuando exista la jerarquía `TESORERO_CENTRAL` / `TESORERO_AGRUPACION`, restringir `ECO_CUENTA_CREAR` solo al primero.

### 2026-05-19 — durante Lote D del flujo 3 (permisos + ParametrosGenerales)

- 🟢 **Tesorería delegada — IBAN de acreedor SEPA por agrupación** — hoy D3.5 deja los 4 datos del acreedor (nombre, IBAN, BIC, Identificador SEPA) en Parámetros Generales: un único acreedor central. Cuando cada agrupación tenga su propia cuenta operativa, los 4 campos deben migrar a `CuentaBancaria` (extender el modelo con `titular`, `bic_swift` ya existen; añadir `id_acreedor_sepa`). El `RemesaService._cargar_acreedor_sepa` pasaría a leer la cuenta bancaria asociada a la remesa (vía `remesa.agrupacion_id → cuenta.agrupacion_id`). *Encaja con*: tesorería delegada, flujo a documentar más adelante.

- 🟡 **Tesorería tarda en cargarse al volver a ella** — perf: investigar si las queries iniciales pueden cachearse o reducirse en `Tesoreria.vue` (probablemente exceso de queries al `onMounted`). *Pantalla*: `Tesoreria.vue`.

### 2026-05-18 — durante rediseño UI Tesorería

- 🟢 **Promover subnivel del sidebar si un acordeón se vuelve denso** — el usuario indicó que si alguno de los 4 acordeones de Tesorería (A · Caja y bancos, B · Cuentas a cobrar, C · Cuentas a pagar, D · Configuración) acaba siendo muy denso, podemos extraer su navegación a un segundo nivel del sidebar (sub-entradas debajo de "Tesorería"). Aplicar cuando un acordeón concreto pase de 8-10 sub-bloques o reciba quejas de usuarios.

### 2026-05-18 — durante codificación del flujo 4

- 🟢 **Árbol de cuentas: tooltip con descripción al hacer hover sobre el nombre** — las 184 cuentas tienen ya descripción en lenguaje llano (orientada a tesorero no profesional); mostrarla en un bubble tip al pasar el ratón sobre el nombre de la cuenta. *Pantalla*: `Contabilidad.vue` → pestaña Plan de cuentas → componente `CuentaNode.vue`.

- 🟡 **Plantilla de impresión del recibo (PDF A5 estilo resguardo bancario)** — diseñar un modelo de recibo en tamaño A5 con el logo de la organización y estética de resguardo bancario. La plantilla (HTML/CSS o Jinja) se gestiona desde Parámetros Generales, y la función de descarga del recibo la toma y rellena al vuelo los datos variables (número de recibo, miembro, importe, concepto, fechas…). *Encaja con*: Flujo 2 (Emisión de recibos) cuando se documente. *Backend ya parcial*: `app/modules/economico/services/pdf/recibo_service.py`.

- 🟢 **Refactor: dividir `tesoreria_service.py` por funcionalidad** — el archivo se ha hecho monstruoso. Proponer trocearlo en módulos pequeños bajo `app/modules/economico/services/tesoreria/`: `apuntes.py`, `cuentas.py`, `conciliacion.py`, `pagos_manuales.py`, `liquidacion_legacy.py` (la antigua liquidar_remesa que sustituye RemesaService.liquidar_remesa). Aplicar el mismo criterio a `remesa_service.py` si crece tras el flujo 4. *Norma del proyecto que respeta*: reutilización + módulos cohesivos.

- 🟢 **Remesas: retirar los contadores de colores del panel superior** — mismo criterio que se aplicó a Contabilidad y a Tesorería. Estos KPIs no aportan contexto aislados; guardarlos para el dashboard del tesorero. *Pantalla*: `Remesas.vue`.

### 2026-05-18 — durante diseño del flujo 1 (cuotas)

- 🟡 **Histórico de traslados de socio entre agrupaciones territoriales** — cambiar `Miembro.agrupacion_id` directamente pierde la traza. Modelar `TrasladoSocio` (miembro_id, agrupacion_origen_id, agrupacion_destino_id, fecha_traslado, motivo, autorizado_por) o `MiembroAgrupacionHistorico` (miembro_id, agrupacion_id, fecha_alta_en_agrupacion, fecha_baja_en_agrupacion). Esto permite saber dónde ha estado y colaborado cada socio. *Ya existe parcialmente*: `TRANSACCIONES_TRASLADOS` en `diccionario_transacciones.py` sugiere que algo se preveía; revisar antes de implementar. *Encaja con*: módulo Membresía, no Económico.

### 2026-05-18 — durante ciclo de seed cobros históricos + rediseño Balance

- 🟡 **Pestaña Asientos: mostrar evento de negocio, no asiento técnico** — la tabla actual muestra "TipoAsientoContable.GESTION" y similar (cosmético arreglado), pero la idea de fondo del usuario sigue pendiente: reemplazar la vista raw de asientos por una **bitácora de movimientos** con columnas `Fecha | Origen (recibo X cobrado / justificante Y pagado / ...) | Importe | Tipo | Asiento # | Estado`, y la vista de asientos pasa a modo experto / drill-down. *Pantalla*: `Contabilidad.vue` pestaña Asientos. *Detalles en*: `docs/modulo_economico.md`.

- 🟡 **Dashboard del tesorero** — los KPIs aislados de cabecera no aportaban contexto y se retiraron. Pendiente diseñar un dashboard del tesorero con: saldos cuentas bancarias + caja con evolución mensual, cuotas pendientes ejercicio en curso vs anterior, recibos fallidos pendientes de re-presentar, próximos vencimientos (remesas / declaraciones / asiento de cierre), estado del ejercicio (% asientos confirmados, balance cuadra, alertas), accesos directos a acciones. *Pantalla*: nueva pantalla de inicio del módulo Económico. *Detalles en*: `docs/modulo_economico.md`.

---

## Pendientes cerrados

### Cerrados 2026-05-19 al repasar backlog tras flujo 6

- ✅ **Cuotas del ejercicio en curso** — implementado en flujo 1: vista `CuotasEjercicio.vue` para fijar cuota ordinaria + reducidas del ejercicio activo.
- ✅ **Motivos de reducción de cuota** — implementado en flujo 1: tabla `motivos_reduccion_cuota`, CRUD en `MotivosReduccionCuota.vue`, `porcentaje_reduccion` congelado si ya hay recibos emitidos (D1.5).
- ✅ **Reglas contables editables desde el UI** — `ReglasContables.vue` operativo en módulo Contabilidad. Catálogo completo editable.
- ✅ **Tesorería: cuenta bancaria en el FilterBar superior** — superado por el rediseño UI Tesorería con 4 acordeones (A·Caja+bancos, B·Cuentas a cobrar, C·Cuentas a pagar, D·Configuración). Cada acordeón muestra sus KPI con contexto, no aislados.
- ✅ **Tesorería: retirar contadores de colores del panel superior** — eliminada cabecera con KPIs aislados. Los KPIs viven dentro de cada acordeón con su contexto.
- ✅ **Remesas: retirar contadores de colores del panel superior** — Remesas.vue rediseñada con FilterBar limpio en Lote C del flujo 3.
- ✅ **Centro de ayuda — guías por flujo** — añadidos acordeones para los 11 flujos del módulo económico (1–11). Sigue pendiente: derivar manuales filtrados por rol (TESORERO, AUDITOR, SOCIO, JUNTA).
- ✅ **Instalar `reportlab` para PDFs** — `reportlab>=4.0.0` en dependencias. Usado en certificado donación, libro diario, CCAA PDF, certificado Modelo 182.

### Cerrados antes

- 🟢 **Tesorería: retirar los contadores de colores del panel superior** — atendido también en `Remesas.vue` durante el Lote C del flujo 3 (KPIs retirados, sustituidos por FilterBar + listado limpio). Pendiente aplicar lo mismo en `Tesoreria.vue` cuando le toque su flujo.
