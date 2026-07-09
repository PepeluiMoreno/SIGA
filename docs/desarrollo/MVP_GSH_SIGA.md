# MVP SIGA — Análisis GSH ↔ SIGA y plan de cierre de huecos

> Comparativa funcional entre **GSH** (app PHP de Gestión de Socios de Europa Laica,
> seudo-MVC por roles) y **SIGA** (FastAPI + Strawberry GraphQL, modelo CRM
> Party-Role). Objetivo: cerrar los huecos que impiden que SIGA sustituya a GSH.

## Arquitecturas

- **GSH**: agrupa por rol (`cPresidente`, `cCoordinador`, `cTesorero`, `controladorSocios`,
  `cAdmin`). Tablas planas `MIEMBRO`/`SOCIO`/`CUOTAANIOSOCIO`. Tesorería, remesas,
  donaciones y PayPal cuelgan de "socios".
- **SIGA**: por módulos (`membresia`, `economico`, `comunicacion`, `acceso`,
  `organizaciones`). Modelo `Contacto` → `Vinculacion` tipada → satélites
  `Socio`/`Voluntario`. La lógica vive en resolvers GraphQL (el service de membresía
  estaba vacío).

## Resumen del contraste

- **Membresía**: GSH tiene piezas que a SIGA le faltan (auto-alta pública, estadísticas,
  cambio simpatizante→socio…). SIGA tiene un CRM más rico (habilidades, voluntariado,
  RGPD, traslados modelados).
- **Económico**: **SIGA va muy por delante** (SEPA pain.008/pain.002/camt.054,
  conciliación Norma 43, contabilidad PCESFL, cuentas anuales, Modelo 182, presupuestos,
  justificantes de gasto, reducciones de cuota). Aquí los "huecos" son sobre todo
  **piezas no cableadas y agujeros de seguridad dentro de SIGA**, no funciones que GSH
  tenga y SIGA no.

## Buckets del MVP (alcance confirmado: los 4)

### Bucket A — Alta y cobro del socio
1. **Auto-alta pública** del socio (web + API) + **confirmación doble opt-in**.
   Hoy SIGA no crea `SOCIO_ASPIRANTE`; el flujo estaba hecho solo por el lado de
   aprobar/rechazar.
2. **Pago de cuota online por el socio** (PayPal/transferencia). SIGA tiene
   `paypal_service` pero sin endpoint público "pagar mi recibo".
3. **Estadísticas de altas/bajas** (agrupación/provincia/CCAA).
4. **Cambio simpatizante → socio**.
5. **Validación de IBAN (mod-97)** — ausente en toda SIGA.

### Bucket B — Cablear piezas medio hechas (membresía)
- **Traslados** (`SolicitudTraslado`): máquina de estados y RBAC modelados, **sin
  resolvers**. `HistorialAgrupacion` no se rellena solo.
- Mutations dedicadas **suspender / baja / reactivar** (transacciones declaradas sin resolver).

### Bucket C — Cerrar RBAC económico (bloqueante de producción)
- Mutations sin `permission_classes`: `registrar_pago_cuota_manual`,
  `importar_fallidos_banco`, `marcar_recibo_fallido`, `registrar_apunte_caja`,
  `anular_apunte_caja`, `confirmar/anular_asiento_contable`, etc.
- `ECO_*_LISTAR` declarados pero no aplicados (listados por strawchemy sin control).

### Bucket D — Reporting + limpieza
- Estadísticas altas/bajas; avisos de próximo cobro / cuota no cobrada.
- Limpieza legacy: `MiembroSegmentacion`/`EstadoMiembro` sobre la tabla huérfana
  `miembros`; `models/contabilidad.py` duplica el paquete `contabilidad/`;
  `services/membresia_service.py` vacío.

### Fuera del MVP
Cuaderno 19/CSB (GSH lo tiene desactivado), OCR de justificantes, dashboard financiero
agregado, reversión contable de devoluciones PayPal, pain.001 de transferencias,
reclamaciones de impago (4 modelos muertos; GSH tampoco lo tiene).

---

## Progreso de implementación

> **Estado global (2026-07-09): los 4 buckets implementados.** Todo pusheado en la
> rama `claude/gsh-siga-membership-analysis-11otv9` y abierto como PR #11 (draft)
> contra `master`. Verificación **estática** completa (compila, importa, el esquema
> GraphQL construye con las versiones exactas de `uv.lock` — Python 3.13, strawchemy
> 0.21.0, strawberry 0.315.3; el frontend builda). **Falta verificación en ejecución**
> contra un backend vivo: ver "Checklist antes de merge" al final.

### Bucket A — ✅ completo (pago online pendiente de sandbox)
- ✅ **Validación IBAN mod-97** (`app/core/documento.py`: `validar_iban`, `normalizar_iban`).
- ✅ **Auto-alta pública de socio con doble opt-in**:
  - `app/modules/membresia/services/solicitud_socio_publica_service.py` — crea
    `Contacto` + `Vinculacion(SOCIO_ASPIRANTE, estado="pendiente_verificacion")` +
    satélite `Socio` (conserva IBAN/forma de pago) y envía email con token JWT.
    Al confirmar, la vinculación pasa a `"activa"` y entra en la bandeja
    `solicitudes_socio_pendientes` (que ya existía) para aprobación de secretaría.
  - `app/api/publico/socios.py` — `POST /api/publico/socios`, `GET …/verificar`,
    `GET …/config`. Captcha + honeypot + rate-limit, calcado de `firmas.py`.
  - `aprobar_solicitud_socio` ajustado para conservar el satélite del aspirante y
    fijar `numero_socio`/`estado_socio` al aprobar.
  - Router montado en `main.py`; limiters en `app/core/ratelimit.py`.
- (El pago de cuota online y su página front se detallan más abajo, en "Bucket A —
  pago online". El cambio simpatizante→socio quedó en el Bucket B; las estadísticas
  en el Bucket D.)

### Bucket C — ✅ completo
- ✅ **RBAC del lado escritura** (bloqueante de producción): añadido `permission_classes`
  a todas las mutations económicas que estaban abiertas:
  - `registrar_apunte_caja`, `actualizar_metadatos_apunte_caja`, `anular_apunte_caja`
    → `ECO_MOVIMIENTO_REGISTRAR`.
  - `confirmar_asiento_contable`, `anular_asiento_contable` → `ECO_ASIENTO_APROBAR`.
  - `registrar_pago_cuota_manual` → `ECO_CUOTA_REGISTRAR_PAGO`.
  - `importar_fallidos_banco` → `ECO_REMESA_PROCESAR_RESPUESTA`.
  - `marcar_recibo_fallido` → `ECO_RECIBO_MARCAR_COBRADO`.
  - `presentar/anular_solicitud_reduccion_cuota`, `modificar_incremento_cuota`
    (autoservicio del socio) → `RequireAuthenticated` (con TODO de ámbito horizontal
    self/tesorería).
  - Verificado: ya no queda ninguna mutation pública económica sin RBAC.
- ✅ **Lado lectura**: confirmada la versión desplegada por `uv.lock`
  (strawchemy 0.21.0, soporta `permission_classes` en `field()`). Aplicado
  `RequireTransaction` a los 18 listados sensibles de `schema_simple.py`
  (tesorería→ECO_CONCILIACION_LISTAR, cuentas→ECO_CUENTA_LISTAR,
  contabilidad→ECO_ESTRUCTURA_CONTABLE_LISTAR, cuotas/reducciones→ECO_CUOTA_LISTAR,
  donaciones/remesas/recibos/justificantes→sus ECO_*_LISTAR,
  presupuesto→ECO_PRESUPUESTO_CONSULTAR). Los catálogos inocuos que usan los
  formularios (formasPago, importesCuotaAnio, motivosReduccionCuota,
  donacionConceptos, estadosPlanificacion, categoriasPartida) quedan solo con
  autenticación. **Esquema completo verificado** con python3.13 + versiones del
  lock: construye y todos los campos siguen en el SDL.

### Bucket B — ✅ completo
- ✅ **Mutations de ciclo de vida del socio** (`vinculaciones_resolvers.py`):
  - `suspender_socio` → `MEMBRESIA_MIEMBRO_SUSPENDER` (estado_socio='suspendido',
    vinculación 'inactiva').
  - `dar_de_baja_socio` → `MEMBRESIA_MIEMBRO_BAJA` (cierra vinculación + motivo de baja).
  - `reactivar_socio` → `MEMBRESIA_MIEMBRO_BAJA` (reabre la última vinculación SOCIO).
  - Todas con guard de ámbito territorial (`assert_miembro_en_ambito`).
- ✅ **Conversión simpatizante → socio** (`convertir_simpatizante_en_socio`,
  `MEMBRESIA_MIEMBRO_CREAR`): crea vinculación SOCIO + satélite y cierra la de
  SIMPATIZANTE; valida IBAN. Equivale a `cambioSimpSocio` de GSH.
- ✅ **Traslados entre agrupaciones** (máquina de estados de `SolicitudTraslado`):
  `solicitar_traslado` (SOLICITAR), `aprobar_traslado_origen`/`aprobar_traslado_destino`
  (APROBAR, con guard de ámbito sobre origen/destino), `rechazar_traslado` (RECHAZAR),
  `cancelar_traslado`, `ejecutar_traslado` (APROBAR). La ejecución mueve
  `agrupacion_id` del contacto y de su vinculación SOCIO, **cierra el tramo de
  `HistorialAgrupacion` vigente y abre uno nuevo** en destino. Estado derivado de la
  doble aprobación (`_recalcular_estado_traslado`).

### Bucket D — ✅ completo
- ✅ **Estadísticas de altas/bajas** (`MembresiaQuery.estadisticas_altas_bajas`,
  `MEMBRESIA_MIEMBRO_LISTAR`): altas (inicio de vinculación SOCIO) y bajas (cierre)
  por año y agrupación en un rango, con nombre de agrupación y neto. Cubre el hueco
  de informes de altas/bajas que GSH tenía (por agrupación/provincia/CCAA) y SIGA no.
  Tipo `EstadisticaAltasBajasType`.
- ✅ **Avisos de cobro** (`economico_mutations.py`):
  - `enviar_avisos_proximo_cobro(remesa_id)` → `ECO_REMESA_ENVIAR`: email a los
    domiciliados de la remesa con importe y fecha de cargo (el
    `emailAvisarDomiciliadosProximoCobro` de GSH).
  - `enviar_avisos_cuota_pendiente(ejercicio, solo_sin_domiciliacion)` →
    `ECO_RECIBO_NOTIFICAR_FALLIDOS`: email a socios con cuota pendiente
    **con enlace de pago tokenizado** (el `emailAvisarCuotaNoCobradaSinCC` de GSH).
- ✅ **Limpieza legacy** (solo lo seguro; SQL acumulado, no ejecutado):
  - `models/economico/contabilidad.py` **borrado**: era código muerto inalcanzable
    (el paquete `contabilidad/` lo eclipsaba en el import; verificado en runtime).
  - `models/membresia/miembro_segmentacion_view.py` **borrado**: cero referencias,
    construido sobre la tabla legacy `miembros`. SQL del `DROP MATERIALIZED VIEW`
    acumulado en `docs/modulo_membresia.md` (convención del repo: no ejecutar ad-hoc).
  - `services/membresia_service.py`: de placeholder vacío a punto de anclaje
    documentado que re-exporta `SolicitudSocioPublicaService`.
  - `EstadoMiembro` se conserva (CRUD auto en el esquema; quitarlo rompería types_auto).

### Bucket A — pago online ✅ (pendiente de sandbox)
- ✅ **Pago de cuota online por el socio** (paridad con `pagarCuotaSocio` /
  `pagarCuotaSocioSinCC` de GSH):
  - `economico/services/pago_cuota_publica_service.py`: enlace tokenizado (JWT
    purpose `pago_cuota`, 30 días) → info de la cuota → `crear_orden` (el importe
    lo deriva SIEMPRE el servidor del pendiente de la `CuotaAnual`) → `capturar`,
    que registra el `Pago` de pasarela **y liquida la cuota** (importe_pagado,
    modo PAYPAL, referencia=order_id, estado Cobrada al completarse) — la pieza
    que faltaba en `registrar_pago_capturado`. Si `org.paypal_cuenta_bancaria_id`
    está configurado, genera además ApunteCaja + asiento.
  - `api/publico/pago_cuota.py`: `GET /api/publico/pago-cuota`, `POST …/crear-orden`,
    `POST …/capturar`, con rate-limit por IP. Montado en `main.py`.
  - ⚠️ **Verificar en sandbox PayPal antes de producción** (requiere
    `PAYPAL_CLIENT_ID/SECRET`, no disponibles en esta sesión): crear orden,
    aprobar como buyer, capturar y comprobar que la cuota queda Cobrada.
  - ✅ **Página front `/pagar-cuota`** (`frontend/src/views/PagarCuota.vue`, ruta
    pública): lee el token de la URL, muestra la cuota (importes del servidor),
    monta los botones del SDK JS de PayPal contra los endpoints públicos y muestra
    los estados ya-pagada / completado / error. El `client-id` lo sirve el endpoint
    de info (es público por diseño del SDK). Build de Vite verificado.

---

## UI de back-office (para lo nuevo del backend)

El pago de socio (`/pagar-cuota`) ya tiene su página pública. Falta la UI **interna**
que consume las mutations/queries nuevas (se irá construyendo sobre la misma rama):

- **Bandeja de solicitudes de socio** (auto-altas verificadas): listar
  `solicitudes_socio_pendientes` y botones aprobar/rechazar.
- **Detalle del socio**: acciones de ciclo de vida (suspender / reactivar / dar de
  baja con motivo) y **convertir simpatizante→socio**.
- **Traslados**: bandeja de `SolicitudTraslado` con las transiciones (solicitar,
  aprobar origen/destino, rechazar, cancelar, ejecutar).
- **Estadísticas de altas/bajas**: vista con filtro por rango de años y agrupación.
- **Avisos de cobro**: acciones en tesorería (próximo cobro por remesa; cuota
  pendiente por ejercicio).

> Gate de rutas/botones por los permisos correspondientes
> (`MEMBRESIA_MIEMBRO_VALIDAR/_SUSPENDER/_BAJA/_CREAR`, `MEMBRESIA_TRASLADO_*`,
> `MEMBRESIA_MIEMBRO_LISTAR`, `ECO_REMESA_ENVIAR`, `ECO_RECIBO_NOTIFICAR_FALLIDOS`).

---

## Verificación en ejecución (2026-07-09) — hecha

La rama se verificó contra un backend vivo. Resultado y detalle técnico de los fixes
aplicados en **[VERIFICACION_MVP_RBAC_RGPD.md](VERIFICACION_MVP_RBAC_RGPD.md)**.
Resumen de lo que cambió respecto al MVP original:

- **Módulo económico encendido** (`modulos.py`: `economico` → `activo=True`). Estaba
  OFF, lo que dejaba inerte todo el RBAC económico nuevo (denegaba hasta a SUPERADMIN).
- **Permisos del tesorero completados** (`seed_permisos_tesorero.py`): +5 transacciones
  que la PR volvió obligatorias (cuentas, apuntes de caja, pago manual, asientos,
  presupuesto).
- **Default-deny en los 122 listados strawchemy** + **secretos de `Usuario`
  (`password_hash`/`reset_token*`) marcados `info=PRIVATE`**: cerró una fuga
  preexistente (104 listados públicos sin auth; token de reset filtrable).
- **Fix RGPD**: modelos `Consentimiento`/`SolicitudDerecho` alineados a la columna
  real `contacto_id` (la migración la había renombrado; el ORM se quedó en
  `miembro_id`). Sin esto, la auto-alta con consentimiento abortaba.

---

## Checklist antes de merge (PR #11)

1. Arrancar stack dev y confirmar backend `healthy`.
2. **Permisos (riesgo principal):** el rol TESORERO conserva los `ECO_*_LISTAR`
   (re-sembrar si la BD es anterior a esos seeds) y sigue viendo
   cuotas/remesas/recibos/donaciones; un usuario sin rol económico deja de verlos;
   los formularios de membresía (formasPago, importesCuotaAnio) siguen funcionando.
3. Auto-alta end-to-end (requiere SMTP): formulario → email → verificar → bandeja →
   aprobar; IBAN inválido → 422.
4. Ciclo de vida y traslado completo vía GraphQL (mueve `agrupacion_id` +
   `HistorialAgrupacion`).
5. Pago PayPal en sandbox (opcional; requiere `PAYPAL_CLIENT_ID/SECRET`).
6. Tests (`backend/tests/`) y linter.
7. Ejecutar el SQL de limpieza acumulado **solo** en el lote de migraciones del
   equipo (no ad-hoc); ver `docs/modulo_membresia.md`.
