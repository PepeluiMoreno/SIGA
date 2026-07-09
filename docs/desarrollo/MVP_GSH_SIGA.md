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

### Bucket A — en curso
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
- ⏳ Pendiente en A: pago de cuota online por el socio; estadísticas altas/bajas;
  cambio simpatizante→socio.

### Bucket C — parcialmente hecho
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
- ⏳ **Pendiente (lado lectura)**: los `ECO_*_LISTAR` no se aplican porque los
  listados los sirve `strawchemy.field` en `schema_simple.py` sin control. La versión
  moderna de strawchemy acepta `permission_classes=` en `field()`, pero **antes de
  aplicarlo hay que confirmar la versión de strawchemy desplegada** (un skew rompería
  el arranque). Severidad menor: /graphql va tras Authelia/VPN; el hueco es horizontal
  (cualquier usuario autenticado lista datos económicos aunque no tenga rol económico).

### Bucket B — parcialmente hecho
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

### Bucket D — parcialmente hecho
- ✅ **Estadísticas de altas/bajas** (`MembresiaQuery.estadisticas_altas_bajas`,
  `MEMBRESIA_MIEMBRO_LISTAR`): altas (inicio de vinculación SOCIO) y bajas (cierre)
  por año y agrupación en un rango, con nombre de agrupación y neto. Cubre el hueco
  de informes de altas/bajas que GSH tenía (por agrupación/provincia/CCAA) y SIGA no.
  Tipo `EstadisticaAltasBajasType`.
- ⏳ Pendiente en D: avisos de próximo cobro / cuota no cobrada; limpieza de legacy
  (requiere migraciones — se deja para el flujo de migración por lotes del equipo,
  no se ejecuta ad-hoc; ver `docs/modulo_membresia.md`).

### Bucket A — pendiente restante
- ⏳ **Pago de cuota online por el socio** (PayPal/transferencia): existe
  `paypal_service` y `api/paypal.py` (create/capture/webhook), pero falta el endpoint
  público "pagar mi cuota/recibo" ligado a `Recibo`/`CuotaAnual`. Requiere credenciales
  PayPal y verificación en sandbox (no ejecutable en esta sesión).
