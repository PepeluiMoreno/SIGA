# Flujo 7 — Justificantes de gasto

## 1. Propósito

Permitir a cualquier miembro presentar un **justificante de gasto** realizado en nombre de la organización (factura, ticket, dieta…), tramitar su validación en tres firmas (presentador → responsable de actividad → tesorero), y registrar el pago como `ApunteCaja` con su asiento contable.

Todo gasto se imputa **obligatoriamente a una actividad** (campaña, permanente o puntual). La actividad determina la imputación contable y la agrupación territorial (D7.4).

---

## 2. Entidades implicadas

### 2.1 `JustificanteGasto` (`justificantes_gasto`)

Campos relevantes:
- `numero_justificante` (correlativo, ver D7.4)
- `ejercicio`, `miembro_id` (presentador), `actividad_id` (obligatorio), `partida_actividad_id` (opcional)
- `agrupacion_id` (derivada de la actividad)
- `concepto`, `importe`, `fecha_gasto`, `fecha_presentacion`
- `estado` ∈ {PRESENTADO, ACEPTADO, APROBADO, RECHAZADO, PAGADO, ANULADO}
- `aceptado_por_id`, `fecha_aceptacion` — D7.5 (campos NUEVOS por añadir)
- `aprobado_por_id`, `fecha_aprobacion`, `motivo_rechazo`
- `apunte_caja_id`, `cuenta_bancaria_id`, `modo_pago`, `fecha_pago`
- `archivo_factura` — D7.2 (campo NUEVO por añadir)
- `observaciones`

### 2.2 `Actividad` (referida)

- `responsable_id` → quién acepta (D7.5).
- `grupo_id` → indirectamente da la agrupación territorial (D7.4). A futuro: añadir `agrupacion_id` directo.

### 2.3 `Miembro` (presentador y aprobadores)

### 2.4 `CuentaBancaria`, `ApunteCaja`, `AsientoContable`

Como en cualquier movimiento de salida de caja, el pago genera apunte y asiento (Debe cuenta de gasto / Haber `572 Bancos`) vía `RegistroContable`.

---

## 3. Estados y transiciones

```
                                       motivo
                              ┌────────────────────┐
                              ▼                    │
   ┌─────────────┐         ┌──────────┐         ┌──────────┐
   │  PRESENTADO │ ───────>│ ACEPTADO │ ───────>│ APROBADO │ ──────> ┌───────┐
   └─────┬───────┘ aceptar └─────┬────┘ aprobar └────┬─────┘ pagar  │PAGADO │
         │  responsable          │ tesorero          │              └───────┘
         │                       ▼                   │
         │                 ┌──────────┐              │
         │                 │RECHAZADO │<─────────────┘ (motivo)
         │                 └──────────┘
         │
         │  anular (el propio presentador)
         ▼
   ┌─────────────┐
   │  ANULADO    │
   └─────────────┘
```

---

## 4. Acciones

| # | Acción | Quién dispara | Pre-estado | Post-estado | Efecto |
|---|---|---|---|---|---|
| A1 | **Presentar justificante** | Miembro activo | — | `PRESENTADO` | Numeración correlativa según D7.4; opcionalmente adjunta factura (D7.2) |
| A2 | **Anular (retirar)** | Presentador | `PRESENTADO` | `ANULADO` | Solo el propio presentador antes de que se acepte |
| A3 | **Aceptar** | Responsable de la actividad (D7.5) | `PRESENTADO` | `ACEPTADO` | Confirma que el gasto corresponde a la actividad |
| A4 | **Rechazar (responsable)** | Responsable de la actividad | `PRESENTADO` | `RECHAZADO` | Motivo obligatorio |
| A5 | **Aprobar** | Tesorero central o de ámbito (D7.1) | `ACEPTADO` | `APROBADO` | Da luz verde al pago |
| A6 | **Rechazar (tesorero)** | Tesorero | `ACEPTADO` | `RECHAZADO` | Motivo obligatorio (ej. "falta factura") |
| A7 | **Pagar** | Tesorero | `APROBADO` | `PAGADO` | Pide cuenta bancaria + modo + fecha → crea ApunteCaja (GASTO) + asiento contable |
| A8 | **Adjuntar/Reemplazar factura** | Presentador o responsable | `PRESENTADO` o `ACEPTADO` | sin cambio | Actualiza `archivo_factura` (D7.2) |

---

## 5. Pantallas UI

### 5.1 Listado de justificantes — `Justificantes.vue` (NUEVA)

Ruta: `/economico/justificantes`. FilterBar: ejercicio, estado, agrupación, búsqueda por miembro o número.

```
Nº justificante           Actividad             Presentado por    Importe   Estado
JUST-MAD-2025-00012       Asamblea local mayo   J. García López   125,00 €  ACEPTADO
JUST-2025-00007           Congreso estatal      M. Ruiz Sanz      450,00 €  PAGADO
…
```

Acciones por fila según estado y rol. Acciones de presentación con botón "+ Presentar gasto".

### 5.2 Modal presentar justificante

```
Actividad *      [ Asamblea local mayo ▼ ]
Concepto *       [ "Alquiler proyector" ]
Importe *        [ 125,00 € ]
Fecha gasto *    [ 12/05/2026 ]
Partida          [ Logística ▼ ] (opcional)
Adjuntar factura [ Seleccionar fichero ] (opcional, D7.2)
Observaciones    [ ... ]
```

### 5.3 Modal detalle + acciones según estado

Acciones contextuales:
- **Presentador**: Anular (si `PRESENTADO`), Adjuntar factura (si sin adjunto).
- **Responsable de actividad**: Aceptar / Rechazar (si `PRESENTADO`).
- **Tesorero**: Aprobar / Rechazar (si `ACEPTADO`), Pagar (si `APROBADO`).

### 5.4 Mi zona — "Mis justificantes"

Listado filtrado a los presentados por el miembro logueado. Mismas acciones contextuales.

### 5.5 Pendientes de mi visto bueno

- **Responsable**: justificantes `PRESENTADO` de actividades cuyo `responsable_id = miembro_id_logueado`.
- **Tesorero**: justificantes `ACEPTADO` de su ámbito (matriz o agrupación según D7.1).

---

## 6. Permisos / roles

| Código | Acción | Asignación |
|---|---|---|
| `JUST_PRESENTAR` | A1, A2, A8 — presentar/retirar/adjuntar | Todos los miembros activos |
| `JUST_ACEPTAR` | A3, A4 — aceptar/rechazar como responsable | Miembros que sean responsable de ≥1 actividad |
| `JUST_APROBAR` | A5, A6 — aprobar/rechazar como tesorero | TESORERO (central + ámbitos) |
| `JUST_PAGAR` | A7 — registrar el pago | TESORERO |
| `JUST_LIST` | Ver listados | TESORERO, presidencia, AUDITOR (filtrado) |

---

## 7. Norma legal aplicable

- **Ley General Tributaria (Ley 58/2003) art. 106**: conservación de facturas y justificantes durante 4 años (10 si afectan a ejercicios prescritos).
- **Real Decreto 1619/2012**: requisitos formales de las facturas (nº, fecha, NIF emisor, descripción).
- **PCESFL 2013 norma 1ª** (control interno): segregación de funciones. La persona que presenta no es la que aprueba ni la que paga.
- **LO 8/2007 art. 14** (partidos): los gastos deben imputarse a una actividad concreta justificable ante el Tribunal de Cuentas.

---

## 8. Estado de implementación actual

| Pieza | Estado |
|---|---|
| Tabla `justificantes_gasto` con campos básicos | ✓ |
| Modelo `JustificanteGasto` | ✓ |
| Estado `ACEPTADO` y campos `aceptado_por_id`, `fecha_aceptacion` (D7.5) | ✗ FALTA |
| Campo `archivo_factura` (D7.2) | ✗ FALTA |
| `JustificanteGastoService.presentar` | ✓ pero no deriva `agrupacion_id` de la actividad (D7.4) |
| `JustificanteGastoService.aprobar` | ✓ pero no exige estado previo `ACEPTADO` |
| `JustificanteGastoService.aceptar` (D7.5) | ✗ FALTA |
| `JustificanteGastoService.rechazar`, `.pagar`, `.anular` | ✓ |
| `siguiente_numero(ejercicio, agrupacion_nombre_corto)` (D7.4) | ✗ FALTA (hoy es global) |
| Mutations GraphQL: `presentar_justificante_gasto`, `aprobar_*`, `rechazar_*`, `pagar_*`, `anular_*` | ✓ |
| Mutation `aceptar_justificante_gasto` (D7.5) | ✗ FALTA |
| Guards `@RequireTransaction("JUST_*")` en las mutations | ✗ FALTA |
| 5 permisos `JUST_*` en `transacciones.json` + seed | ✗ FALTA |
| Vista `Justificantes.vue` (listado + filtros) | ✗ FALTA |
| Modales (presentar / detalle / pagar) | ✗ FALTA |
| Sección de ayuda en `Ayuda.vue` | ✗ FALTA |

---

## 9. Plan de implementación

**Lote A — Schema y modelo**

1. SQL: añadir a `justificantes_gasto`:
   - `aceptado_por_id UUID REFERENCES miembros(id)` + índice.
   - `fecha_aceptacion DATE`.
   - `archivo_factura VARCHAR(500)` (path/URL, hasta tener módulo Documentación).
2. Modelo `JustificanteGasto`: añadir los 3 campos.

**Lote B — Servicio + permisos**

3. Permisos: 5 transacciones nuevas en `transacciones.json` + seed `seed_permisos_justificantes.py`.
4. `JustificanteGastoService`:
   - Reescribir `siguiente_numero(ejercicio, agrupacion_nombre_corto)` (D7.4).
   - Modificar `presentar` para derivar `agrupacion_id` desde `actividad → grupo → agrupacion`.
   - Nuevo método `aceptar(justificante_id, responsable_id)`: valida que `responsable_id == actividad.responsable_id` y que estado=`PRESENTADO`.
   - Modificar `aprobar` para exigir estado=`ACEPTADO` (no `PRESENTADO`).
   - Validar en `aprobar` que el aprobador tiene jerarquía territorial sobre la actividad (D7.1) — versión inicial: cualquier TESORERO; versión completa: jerarquía cuando se implemente tesorería delegada.
   - Nuevo método `adjuntar_factura(justificante_id, archivo_factura)`.

**Lote C — GraphQL**

5. Mutation nueva `aceptar_justificante_gasto(justificante_id, responsable_id?) -> bool` con guard `JUST_ACEPTAR`. Si `responsable_id` no se pasa, usar el del context (user actual).
6. Mutation nueva `adjuntar_factura_justificante(justificante_id, archivo_factura) -> bool`.
7. Guards en las mutations existentes: `presentar_*` → `JUST_PRESENTAR`, `aprobar_*` y `rechazar_*` → `JUST_APROBAR`, `pagar_*` → `JUST_PAGAR`, `anular_*` → `JUST_PRESENTAR` (solo el propio presentador).

**Lote D — Frontend**

8. Vista `Justificantes.vue` con FilterBar + listado + contadores por estado.
9. Modal "Presentar justificante" con selector de actividad + concepto + importe + fecha + adjunto opcional.
10. Modal "Detalle" con acciones contextuales según estado y permiso del usuario.
11. Modal "Pagar" con selector de cuenta bancaria + modo + fecha.
12. Vistas "Mis justificantes" y "Pendientes de mi visto bueno" (sub-rutas con filtros aplicados).
13. Ruta en `router/index.js` con permiso `JUST_LIST`.

**Lote E — Ayuda**

14. Acordeón "Flujo · Justificantes de gasto" en `Ayuda.vue` con los 3 papeles (presentador, responsable, tesorero).

---

## 10. Decisiones tomadas

Detalle en [decisiones.md](./decisiones.md).

- **D7.1** — Flujo de tres firmas: presenta → acepta responsable → aprueba tesorero (central o de ámbito).
- **D7.2** — Adjunto opcional al presentar; el tesorero puede rechazar si falta.
- **D7.3** — Cualquier miembro activo puede presentar.
- **D7.4** — Numeración con prefijo de agrupación cuando la actividad tiene grupo con `agrupacion_id`; sin prefijo si es global.
- **D7.5** — Aceptación intermedia del responsable de la actividad obligatoria antes de la aprobación del tesorero.

---

## 11. Implicaciones para otros módulos

- **Módulo Actividades**: el campo `Actividad.responsable_id` cobra protagonismo en este flujo. Verificar que toda actividad tiene responsable asignado.
- **Módulo Documentación** (pendiente): cuando exista, los `archivo_factura` deben migrarse al sistema de adjuntos común.
- **Módulo Notificaciones (Comunicación Interna)**: integración bidireccional con este flujo. Cuando se presenta un justificante, el sistema debe **disparar una notificación al responsable de la actividad** indicando que tiene un justificante pendiente de aceptar. Análogamente, cuando el responsable acepta, se notifica al tesorero responsable del ámbito. Y cuando el tesorero aprueba o paga, se notifica al presentador. Esto requiere:
  - Un evento por cada cambio de estado.
  - Plantillas de notificación interna (no email; aviso dentro de SIGA) por tipo de transición.
  - Que cada rol con `JUST_ACEPTAR` o `JUST_APROBAR` tenga acceso a una **vista dedicada "Pendientes de mi visto bueno"** (pantalla 5.5 del flujo) donde solo aparecen los suyos.

Apuntado como dependencia en `pendientes_extemporaneos.md`.

---

## 12. Relación con la Memoria Anual (flujo 10)

Los `JustificanteGasto` (pagados) son **una de las dos fuentes** para el balance económico de actividades y campañas que se publica en la Memoria Anual:

1. **Justificantes de gasto** (este flujo): gastos imputados por miembros vía ticket/factura, con `actividad_id` que los liga a una actividad concreta. Útiles para microgastos, dietas, suministros puntuales, viajes, materiales.
2. **Facturas directas de proveedores** (módulo Tesorería, pendiente de documentar): gastos institucionales recurrentes (alquileres, software, seguros, salarios) que la entidad paga directamente sin que un miembro lo "presente". Hoy se registran como `ApunteCaja` tipo `GASTO` desde Tesorería, pero **falta** el campo `actividad_id` o `campania_id` en `ApunteCaja` para imputarlos a una actividad. Esta carencia se debe resolver antes de implementar la Memoria Anual.

Al implementar el flujo 10 habrá que consolidar las dos fuentes (`JustificanteGasto.actividad_id` + `ApunteCaja.actividad_id` futuro) para obtener el gasto total por actividad, restarlo de los ingresos imputables (cuotas finalistas, subvenciones, donaciones afectadas) y producir el cuadro de balance por actividad/campaña.

Apuntado como dependencia en `pendientes_extemporaneos.md`.
