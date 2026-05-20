# Flujo 9 — Cierre de ejercicio

## 1. Propósito

Ejecutar el **cierre contable anual** según PCESFL 2013: regularizar las cuentas de gastos e ingresos contra el excedente, cerrar el balance del ejercicio y abrir el ejercicio siguiente con los saldos arrastrados. Es el acto contable más solemne del año: una vez ejecutado, los asientos del ejercicio quedan **inmutables**.

Salida: tres asientos contables formales (regularización, cierre, apertura), el Libro Diario completo, el Balance PCESFL y la Cuenta de Resultados (Excedente). Esos cuatro documentos son la base de las **Cuentas Anuales** que se depositan ante el Protectorado / Tribunal de Cuentas (flujo 10).

---

## 2. Entidades implicadas

| Entidad | Rol |
|---|---|
| `AsientoContable` | Se crean 3 nuevos con `tipo_asiento ∈ {REGULARIZACION, CIERRE, APERTURA}` |
| `ApunteContable` | Líneas debe/haber de los asientos del cierre |
| `CuentaContable` | Todas las cuentas con saldo quedan saldadas tras cierre |
| `Configuracion` | `org.contabilidad_compleja` debe estar activo |

---

## 3. Estados y transiciones

```
   Ejercicio N abierto, con asientos confirmados
              │
              │ A1 generar_asiento_regularizacion(N)
              ▼  (pre-validación: todos los asientos del ejercicio CONFIRMADOS, D9.3)
   Cuentas grupo 6 (gastos) y grupo 7 (ingresos) saldadas a la cuenta 129
              │
              │ A2 generar_asiento_cierre(N)
              ▼  (pre-validación: conciliación bancaria completa D8.4)
   Todas las cuentas saldadas; el ejercicio queda CERRADO (inmutable)
              │
              │ A3 generar_asiento_apertura(N+1)
              ▼  (pre-validación: asiento CIERRE confirmado del ejercicio N)
   Ejercicio N+1 abierto con los saldos de balance arrastrados
```

---

## 4. Acciones

| # | Acción | Quién | Pre-estado | Post-estado | Efecto |
|---|---|---|---|---|---|
| A0 | **Consultar checklist de cierre** | Tesorero / Auditor | — | sin cambio | Devuelve `estado_cierre` con los 6 flags |
| A1 | **Generar asiento de regularización** | Tesorero matriz | ejercicio con asientos CONFIRMADOS (D9.3) | `AsientoContable(REGULARIZACION, CONFIRMADO)`; cuentas 6/7 saldadas a 129 | Imputa el excedente del ejercicio |
| A2 | **Generar asiento de cierre** | Tesorero matriz | regularización hecha + conciliación completa (D8.4) | `AsientoContable(CIERRE, CONFIRMADO)`; balance saldado | Ejercicio inmutable |
| A3 | **Generar asiento de apertura** | Tesorero matriz | asiento CIERRE confirmado | `AsientoContable(APERTURA, CONFIRMADO)` en N+1 | Saldos del balance arrastrados al ejercicio siguiente |
| A4 | **Descargar Libro Diario** | Tesorero / Auditor | — | sin cambio | CSV con todos los asientos del ejercicio |
| A5 | **Ver Balance PCESFL** | Tesorero / Auditor | — | sin cambio | Estructura activo / pasivo / patrimonio neto según PCESFL 2013 |
| A6 | **Ver Cuenta de Resultados (Excedente)** | Tesorero / Auditor | — | sin cambio | Estructura PCESFL: ingresos − gastos = excedente |

---

## 5. Pantallas UI

### 5.1 `Cierre.vue` (NUEVA) — ruta `/economico/cierre-ejercicio`

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Cierre de ejercicio                          Ejercicio: [ 2025 ▼ ]            │
├──────────────────────────────────────────────────────────────────────────────┤
│ CHECKLIST                                                                     │
│  ✓ Asientos confirmados (146 / 146)                                           │
│  ✓ Balance cuadra (Σ debe = Σ haber = 138 432,18 €)                           │
│  ✗ Conciliación bancaria completa (12 apuntes pendientes — IR A CONCILIAR)    │
│  ✗ Regularización hecha                                                       │
│  ✗ Cierre hecho                                                               │
│  ✗ Apertura ejercicio siguiente hecha                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│ ACCIONES                                                                      │
│  [ 1. Generar regularización ]   ← habilitado solo si checklist verde         │
│  [ 2. Generar cierre ]           ← habilitado tras regularización             │
│  [ 3. Generar apertura 2026 ]    ← habilitado tras cierre                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ DOCUMENTOS                                                                    │
│  [ ↓ Libro Diario CSV ]      [ Ver Balance PCESFL ]   [ Ver Cuenta de Result. ]│
└──────────────────────────────────────────────────────────────────────────────┘
```

Cada paso ejecutado deshabilita el botón anterior y habilita el siguiente. Si una pre-validación falla, el sistema muestra el detalle (lista de asientos en borrador, lista de apuntes sin conciliar) y enlaces para resolverlos.

### 5.2 Acceso desde `Contabilidad.vue`

Botón destacado en la cabecera: **"Cierre del ejercicio →"** que enlaza a `/economico/cierre-ejercicio` con el ejercicio actual preseleccionado.

---

## 6. Permisos / roles

| Código | Acción | Asignación |
|---|---|---|
| `CIERRE_EJECUTAR` | A1, A2, A3 | TESORERO (matriz) |
| `CIERRE_CONSULTAR` | A0, A4, A5, A6 | TESORERO + AUDITOR |

---

## 7. Norma legal aplicable

- **Código de Comercio art. 25.1**: el balance debe abrirse y cerrarse al inicio y final de cada ejercicio. El Libro de Inventarios y Cuentas Anuales debe contener estos asientos.
- **PCESFL 2013 norma 18ª de elaboración**: la regularización antes del cierre es obligatoria. Las cuentas de los grupos 6 (gastos) y 7 (ingresos) se saldan contra la `129 Excedente del ejercicio`.
- **PCESFL 2013 modelo de Cuenta de Resultados**: el resultado del ejercicio en una ESFL se denomina "Excedente", no "Beneficio". Distinción legal relevante (las ESFL no pueden repartir el excedente).
- **Ley 50/2002 art. 34**: las Cuentas Anuales deben depositarse ante el Protectorado. El cierre del ejercicio es la condición previa al depósito.
- **LO 8/2007 art. 14** (partidos políticos): depósito ante el Tribunal de Cuentas con la misma exigencia de formalización.

---

## 8. Estado de implementación actual

| Pieza | Estado |
|---|---|
| `CierreEjercicioService.generar_asiento_regularizacion` | ✓ |
| `CierreEjercicioService.generar_asiento_cierre` | ✓ con bloqueo D8.4 |
| `CierreEjercicioService.generar_asiento_apertura` | ✓ |
| `CierreEjercicioService.verificar_estado_cierre` | ✓ |
| `CierreEjercicioService.calcular_balance_pcesfl` | ✓ |
| `CierreEjercicioService.calcular_cuenta_resultados` | ✓ |
| Mutations GraphQL `generar_asiento_*` | ✓ con guard `ECO_ASIENTO_APROBAR` |
| Queries `balance_pcesfl`, `cuenta_resultados`, `estado_cierre`, `libro_diario_csv` | ✓ sin guards |
| **Permiso `CIERRE_EJECUTAR`** (D9.1) | ✗ falta crear |
| **Permiso `CIERRE_CONSULTAR`** (D9.1) | ✗ falta crear |
| **Cambio de guards a `CIERRE_EJECUTAR` / `CIERRE_CONSULTAR`** | ✗ falta |
| **Pre-validación de asientos CONFIRMADOS en regularización** (D9.3) | ✗ falta |
| **Vista `Cierre.vue`** | ✗ falta |
| **Acceso destacado desde `Contabilidad.vue`** | ✗ falta |
| **Sección de ayuda** | ✗ falta |

---

## 9. Plan de implementación

**Lote A — Permisos**

1. Añadir 2 transacciones a `transacciones.json`: `CIERRE_EJECUTAR`, `CIERRE_CONSULTAR`.
2. Bootstrap + seed `seed_permisos_cierre.py` (TESORERO con ambos; AUDITOR con consulta).
3. Cambiar guards de las 3 mutations + las 4 queries.

**Lote B — Pre-validación de asientos confirmados (D9.3)**

4. En `CierreEjercicioService.generar_asiento_regularizacion`, antes de calcular saldos: query `count(AsientoContable.estado=BORRADOR, ejercicio=X) > 0` → `ValueError` con lista.

**Lote C — Frontend `Cierre.vue`**

5. Nueva vista `/economico/cierre-ejercicio`:
   - Selector de ejercicio.
   - Checklist visual del `estado_cierre`.
   - 3 botones de acciones secuenciales.
   - Visualizaciones inline de Balance PCESFL y Cuenta de Resultados.
   - Botón de descarga Libro Diario CSV.
6. Botón destacado **"Cierre del ejercicio →"** en `Contabilidad.vue`.

**Lote D — Ayuda**

7. Acordeón "Flujo · Cierre de ejercicio" en `Ayuda.vue`.

---

## 10. Decisiones tomadas (referencia rápida)

- **D9.1** — Permiso único `CIERRE_EJECUTAR` para las 3 acciones; `CIERRE_CONSULTAR` para las lecturas.
- **D9.2** — Solo TESORERO matriz puede cerrar (no agrupaciones).
- **D9.3** — Antes de regularizar, todos los asientos del ejercicio deben estar CONFIRMADOS.
- **D9.4** — Vista dedicada `/economico/cierre-ejercicio` + enlace destacado desde Contabilidad.

---

## 11. Implicaciones para otros flujos

- **Flujo 10 (Cuentas Anuales)**: el cierre del ejercicio es el **paso previo necesario**. Sin cierre confirmado, no hay cuentas anuales que depositar.
- **Bloqueo de asientos retroactivos**: una vez el ejercicio queda cerrado, `ContabilidadService.crear_asiento(ejercicio)` rechaza nuevos asientos (lo añadimos en su día).
- **Memoria Anual**: la Memoria depende del Excedente calculado en la Cuenta de Resultados de este flujo.
