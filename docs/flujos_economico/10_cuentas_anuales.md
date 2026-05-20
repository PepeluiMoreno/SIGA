# Flujo 10 — Cuentas Anuales

## 1. Propósito

Preparar, aprobar y depositar las **Cuentas Anuales** del ejercicio cerrado ante el organismo competente (Protectorado para fundaciones, Registro de Asociaciones para asociaciones, Tribunal de Cuentas para partidos políticos). El paquete consta de tres documentos:

1. **Balance** (estructurado según PCESFL 2013).
2. **Cuenta de Resultados** (formato Excedente PCESFL).
3. **Memoria económica** (12 apartados según RD 1491/2011).

Los dos primeros se calculan automáticamente desde la contabilidad cerrada (flujo 9). La Memoria la redacta el tesorero apartado a apartado. El conjunto se aprueba por la junta directiva y se deposita firmado.

---

## 2. Entidades implicadas

### 2.1 `CuentasAnuales` (NUEVA tabla `cuentas_anuales`)

Una fila por ejercicio. Campos:
- `id`, `ejercicio` (único)
- `estado` ∈ {BORRADOR, APROBADAS, DEPOSITADAS}
- `balance_pcesfl: JSON` — snapshot del balance al momento de creación
- `cuenta_resultados: JSON` — snapshot de la cuenta de resultados
- `memoria: JSON` — 12 claves (`apartado_1`..`apartado_12`), cada una con texto libre
- `excedente: NUMERIC(14,2)` — copia para indexación
- `fecha_aprobacion`, `aprobado_por_id` (presidente), `acta_referencia` (str)
- `fecha_deposito`, `archivo_acuse_recibo` (path/URL al PDF del registro)
- Auditoría estándar

### 2.2 `CierreEjercicioService` (reutilizado)

`calcular_balance_pcesfl(ejercicio)` y `calcular_cuenta_resultados(ejercicio)` producen los snapshots iniciales.

---

## 3. Estados y transiciones

```
   (no existe)
        │ A1 generar_cuentas_anuales(ejercicio)
        ▼  (pre: ejercicio CERRADO, flujo 9 completo)
   ┌──────────┐
   │ BORRADOR │  ← tesorero rellena la Memoria
   └────┬─────┘
        │ A2 aprobar_cuentas_anuales(ccaa_id, presidente_id, acta_ref)
        ▼
   ┌──────────┐
   │ APROBADAS│  ← junta directiva firma; textos inmutables
   └────┬─────┘
        │ A3 marcar_depositadas(ccaa_id, fecha, acuse)
        ▼
   ┌────────────┐
   │ DEPOSITADAS│  ← Protectorado / Registro firma; documento legalmente cerrado
   └────────────┘
```

---

## 4. Acciones

| # | Acción | Quién | Pre-estado | Post-estado |
|---|---|---|---|---|
| A1 | **Generar CCAA del ejercicio** | Tesorero | ejercicio CERRADO; no hay CCAA aún | `BORRADOR` con snapshots calculados |
| A2 | **Editar Memoria** | Tesorero | estado BORRADOR | `BORRADOR` (texto actualizado) |
| A3 | **Aprobar CCAA** | Presidente/Junta | BORRADOR | APROBADAS con `fecha_aprobacion` + `acta_referencia` |
| A4 | **Marcar depositadas** | Tesorero/Secretario | APROBADAS | DEPOSITADAS con `fecha_deposito` + acuse |
| A5 | **Descargar PDF** | Tesorero/Auditor | cualquier estado | sin cambio |
| A6 | **Reabrir CCAA** | Solo tesorero matriz (excepción) | APROBADAS o DEPOSITADAS (no recomendable) | BORRADOR con motivo y traza |

---

## 5. Pantallas UI

### 5.1 `CuentasAnuales.vue` (NUEVA) — ruta `/economico/cuentas-anuales`

Listado:

```
Ejercicio │ Estado      │ Excedente   │ F. aprobación │ F. depósito
──────────┼─────────────┼─────────────┼───────────────┼─────────────
2024      │ DEPOSITADAS │ +12 350,00 €│ 28/06/2025    │ 12/07/2025
2025      │ APROBADAS   │  +8 220,18 €│ 30/06/2026    │ —
2026      │ BORRADOR    │  +5 100,00 €│ —             │ —
```

Botón **+ Generar CCAA del ejercicio cerrado** (habilitado si hay un ejercicio cerrado sin CCAA).

### 5.2 Detalle / Edición — `DetalleCCAA.vue`

Pestañas o acordeones:
1. **Resumen** — fechas, estado, excedente, acciones (aprobar, depositar, exportar PDF).
2. **Balance PCESFL** — visualización tabular del snapshot.
3. **Cuenta de Resultados** — visualización tabular del snapshot.
4. **Memoria** — acordeón con las 12 secciones; texto editable solo en BORRADOR.

Cada sección de la Memoria muestra (a) instrucciones del PCESFL sobre qué contar, (b) editor de texto, (c) opcionalmente tablas pre-calculadas (e.g. el apartado 5 Inmovilizado tiene tabla con altas/bajas/amortizaciones).

---

## 6. Permisos / roles

| Código | Acción | Asignación |
|---|---|---|
| `CCAA_GENERAR` | A1, A2, A6 — preparar/editar Memoria | TESORERO |
| `CCAA_APROBAR` | A3 — aprobar en junta | PRESIDENTE + VICEPRESIDENTE |
| `CCAA_DEPOSITAR` | A4 — marcar depositadas | TESORERO + SECRETARIO |
| `CCAA_LIST` | A5, listar | TESORERO + JUNTA + AUDITOR |

---

## 7. Norma legal aplicable

- **Ley 50/2002 art. 25** (Fundaciones): el patronato aprueba las CCAA en los 6 meses siguientes al cierre y las deposita en el Protectorado.
- **LO 1/2002 art. 14** (Asociaciones): las CCAA se aprueban según los estatutos (junta directiva o asamblea) y se depositan en el Registro de Asociaciones competente.
- **LO 8/2007 art. 14** (Partidos políticos): las CCAA se depositan ante el Tribunal de Cuentas con desglose más exigente (subvenciones, financiación electoral).
- **RD 1491/2011 norma 4ª de elaboración**: estructura obligatoria de la Memoria económica con sus 12 apartados.
- **PCESFL 2013** (Resolución ICAC): formato del Balance y la Cuenta de Resultados (Excedente).

---

## 8. Estado de implementación actual

| Pieza | Estado |
|---|---|
| Tabla `cuentas_anuales` | ✗ FALTA crear |
| Modelo `CuentasAnuales` con relación a Miembro/Usuario aprobador | ✗ FALTA |
| `CuentasAnualesService` con `generar`, `aprobar`, `marcar_depositadas`, `actualizar_memoria` | ✗ FALTA |
| Mutations/Queries GraphQL | ✗ FALTA |
| Vista `CuentasAnuales.vue` (listado) y detalle `DetalleCCAA.vue` | ✗ FALTA |
| 4 permisos `CCAA_*` + asignación a roles | ✗ FALTA |
| PDF de exportación con reportlab | ✗ FALTA (depende del backlog de reportlab) |
| Sección de ayuda | ✗ FALTA |

---

## 9. Plan de implementación

**Lote A — Schema, modelo y servicio**

1. SQL `CREATE TABLE cuentas_anuales (...)` con columnas + índices.
2. Modelo `CuentasAnuales` en `economico/models/cuentas_anuales.py`.
3. `CuentasAnualesService` con:
   - `generar(ejercicio)` — valida que el ejercicio está cerrado (flujo 9), calcula balance + cuenta resultados y crea fila BORRADOR.
   - `actualizar_memoria(ccaa_id, apartado, texto)` — solo en BORRADOR.
   - `aprobar(ccaa_id, aprobado_por_id, acta_referencia)` — BORRADOR → APROBADAS.
   - `marcar_depositadas(ccaa_id, fecha, archivo)` — APROBADAS → DEPOSITADAS.
   - `reabrir(ccaa_id, motivo)` — devuelve a BORRADOR con traza.

**Lote B — GraphQL**

4. Type `CuentasAnualesType`, mutations + queries con guards.

**Lote C — Permisos**

5. 4 transacciones `CCAA_*` + seed.

**Lote D — Frontend**

6. Vista `CuentasAnuales.vue` con listado.
7. Detalle `DetalleCCAA.vue` con 4 pestañas (Resumen, Balance, Cuenta de Resultados, Memoria 12 secciones).
8. Ruta + integración con `Cierre.vue` (botón "Generar CCAA" tras cerrar).

**Lote E — Exportación**

9. Generación HTML imprimible (sin dependencias) — fallback.
10. PDF con reportlab cuando esté instalado (en backlog).

**Lote F — Ayuda**

11. Acordeón "Flujo · Cuentas Anuales" en `Ayuda.vue`.

---

## 10. Decisiones tomadas (referencia rápida)

- **D10.1** — Snapshot completo en `cuentas_anuales` (balance, cuenta de resultados, memoria, excedente).
- **D10.2** — Memoria con plantilla guiada de 12 apartados PCESFL.
- **D10.3** — Workflow Borrador → Aprobadas (junta) → Depositadas.
- **D10.4** — Exportación PDF (reportlab); HTML imprimible mientras tanto.

---

## 11. Implicaciones para otros flujos

- **Flujo 9 (Cierre)**: precondición. Sin cierre confirmado, no se pueden generar CCAA.
- **Flujo 6 (Donaciones)** y **Flujo 11 (Modelo 182)**: el apartado 11 de la Memoria (Subvenciones, donaciones y legados) extrae datos de estos flujos.
- **Módulo Actas / Junta Directiva**: si existe, la `acta_referencia` debería enlazar al acta donde se aprobaron.
