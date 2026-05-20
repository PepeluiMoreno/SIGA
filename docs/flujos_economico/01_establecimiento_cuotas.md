# Flujo 1 — Establecimiento de cuotas del ejercicio

## 1. Propósito

Definir las cuotas que la asociación cobrará a sus miembros durante un ejercicio: **una cuota base** común y un **catálogo de motivos de reducción** que la rebajan en un porcentaje según la situación del socio (estudiante, desempleado, pensionista, de honor, etc.). Después, **generar las cuotas individuales** (`CuotaAnual`) de cada miembro activo aplicando automáticamente el motivo asociado a su tipo de miembro.

Este flujo es el **punto de partida del ciclo económico anual**: sin cuotas individuales generadas no se pueden emitir recibos (Flujo 2), ni generar remesas (Flujo 3), ni cobrar (Flujo 4).

---

## 2. Entidades implicadas

### 2.1 `MotivoReduccion`  (NUEVA tabla `motivos_reduccion_cuota`)

Catálogo de razones por las que una cuota se rebaja respecto a la base.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | PK |
| `codigo` | VARCHAR(30) | Único: `JOVEN`, `PARADO`, `JUBILADO`, `HONOR`, `BECA`… |
| `nombre` | VARCHAR(100) | "Estudiante / Joven", "Desempleado", "Cuota honorífica"… |
| `descripcion` | TEXT | Documentación interna del motivo |
| `porcentaje_reduccion` | NUMERIC(5,2) | 0–100. Ejemplo `90.00` = paga el 10% de la base |
| `orden` | INTEGER | Para ordenar en UI |
| `activo` | BOOLEAN | Para retirar motivos sin borrarlos |
| auditoría | … | `fecha_creacion`, etc. (BaseModel) |

Ejemplo:
```
codigo   | nombre                   | %_reduccion   | efecto
JOVEN    | Estudiante / Joven       | 90.00         | paga 10%
PARADO   | Desempleado              | 90.00         | paga 10%
JUBILADO | Pensionista              | 50.00         | paga 50%
HONOR    | Cuota honorífica         | 100.00        | EXCLUIDO (no se genera CuotaAnual — D1.4)
BECA     | Beca / situación social  | 100.00        | EXCLUIDO (no se genera CuotaAnual — D1.4)
```

> **Regla del sistema (D1.4)**: cualquier motivo con `porcentaje_reduccion >= 100` significa "no se genera cuota". El miembro queda fuera del proceso de emisión, no aparece en listados de cuotas pendientes ni se le emite recibo. Para tarifa real "0€" pero con cuota generada, no usar este modelo (se descartó por ruido en reportes).

### 2.2 `TipoMiembro`  (existente, AMPLIAR)

Tabla `tipos_miembro` (3 registros: De honor, Ordinario, Simpatizante).

Ampliar con:
- `motivo_reduccion_id` UUID FK nullable → `motivos_reduccion_cuota.id`. Si NULL, el tipo paga cuota base íntegra.

Mapeo previsto:
| TipoMiembro | motivo_reduccion | Efecto |
|---|---|---|
| Ordinario | (NULL) | paga cuota base |
| De honor | HONOR (100%) | **excluido del proceso** (D1.4) |
| Simpatizante | (NULL o configurable) | paga cuota base salvo asignación |

### 2.3 `CuotaEjercicio`  (NUEVO modelo o REUSAR `ImporteCuotaAnio`)

Configuración de un ejercicio completo:
- `ejercicio` (UNIQUE)
- `importe_base` NUMERIC(10,2) — la cuota plena
- `fecha_vencimiento_default` DATE — fecha límite recomendada para el cobro
- `cerrado` BOOLEAN — true cuando ya no se pueden modificar importes (porque ya hay cobros)
- `observaciones` TEXT

**Decisión técnica**: aprovechar la tabla existente `importes_cuota_anio` quitándole el campo `codigo_cuota` y `tipo_miembro_id` (o ignorándolos en este flujo). El registro con `codigo_cuota='BASE'` por ejercicio actúa como cuota base. Migración: marcar las filas actuales como obsoletas, crear una sola fila `BASE` por ejercicio.

### 2.4 `CuotaAnual` (existente, AMPLIAR)

- `motivo_reduccion_id` UUID FK nullable → `motivos_reduccion_cuota.id` (snapshot del motivo aplicado al generarla; permite auditar qué reducción tenía cada cuota aunque después cambie el catálogo).
- El campo `importe` ya existe: se rellena con el importe efectivo calculado al generarla.

---

## 3. Estados y transiciones

### 3.1 `CuotaEjercicio` (configuración del año)

```
   ┌─────────────────┐
   │   Abierto       │  ← creado, importes editables
   └────────┬────────┘
            │ generar_cuotas_individuales()
            ▼
   ┌─────────────────┐
   │ Con cuotas      │  ← hay ≥1 CuotaAnual del ejercicio
   │ generadas       │     importes ya no se cambian alegremente
   └────────┬────────┘
            │ marcar_ejercicio_cerrado()
            ▼
   ┌─────────────────┐
   │   Cerrado       │  ← cuotas ya emitidas y cobradas; no se pueden modificar
   └─────────────────┘
```

### 3.2 `CuotaAnual` (cuota de un miembro)

Ya existe la máquina (`Pendiente`, `Cobrada`, `Impagada`, `Anulada`, `Exenta`). Este flujo solo dispara la **creación** en estado `Pendiente` (o `Exenta` si el motivo es 100% reducción).

---

## 4. Acciones

| # | Acción | Quién dispara | Pre-estado | Post-estado | Efecto |
|---|---|---|---|---|---|
| A1 | **Crear configuración del ejercicio** (clonar del anterior) | Tesorero (UI) | sin `CuotaEjercicio` para ese año | nuevo `CuotaEjercicio` (Abierto) con `importe_base` clonado | Pantalla 5.1 — paso 1 |
| A2 | **Editar importe base** | Tesorero (UI) | `CuotaEjercicio.Abierto` o `Con cuotas generadas` (con aviso) | Importe modificado | Si ya hay cuotas generadas, NO recalcula las existentes (el tesorero decide regenerarlas explícitamente) |
| A3 | **Gestionar motivos de reducción** (CRUD) | Tesorero (UI) | — | Cambios en `motivos_reduccion_cuota` | Pantalla 5.2 (parametrización) |
| A4 | **Asociar motivo a tipo de miembro** | Tesorero (UI) | — | `TipoMiembro.motivo_reduccion_id` actualizado | Pantalla 5.3 (parametrización) |
| A5 | **Previsualizar generación de cuotas** | Tesorero (UI) | `CuotaEjercicio.Abierto` | sin cambios | Calcula y muestra: nº miembros activos por tipo × importe efectivo, total esperado |
| A6 | **Generar cuotas individuales** | Tesorero (UI) | `CuotaEjercicio.Abierto` | `CuotaEjercicio.Con cuotas generadas`; nuevas `CuotaAnual` con estado `Pendiente` (o `Exenta` si reducción = 100%) | Idempotente: skip si ya existe `CuotaAnual` para ese (miembro, ejercicio) |
| A7 | **Regenerar cuota de un miembro** | Tesorero (UI, detalle) | `CuotaAnual` existente en estado `Pendiente` | Recalcula importe con la configuración actual | Útil tras cambiar el motivo del miembro o el importe base |

---

## 5. Pantallas UI

### 5.1 Configuración del ejercicio

Ubicación: módulo Económico → Cuotas → "Configurar ejercicio".

```
┌─ Cuotas del ejercicio ──────────────────────────────────────────┐
│ Ejercicio: [ 2026 ▼ ]   [+ Crear / clonar de 2025]               │
│ ─────────────────────────────────────────────────────────────────│
│ Importe base:           [ 50,00 € ]   por miembro                │
│ Vencimiento sugerido:   [ 31/03/2026 ]                           │
│ Estado:                 ⚪ Abierto                               │
│                                                                  │
│ Motivos de reducción aplicables (cat. global):                   │
│   JOVEN     Estudiante / Joven      -90% →  paga  5,00 €         │
│   PARADO    Desempleado             -90% →  paga  5,00 €         │
│   JUBILADO  Pensionista             -50% →  paga 25,00 €         │
│   HONOR     Cuota honorífica       -100% →  excluido del proceso │
│   [+ Editar catálogo de motivos]                                 │
│                                                                  │
│ [Previsualizar generación]   [Guardar configuración]             │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 Catálogo de motivos de reducción

Ubicación: Parametrización → Catálogos → "Motivos de reducción de cuota".

Tabla CRUD estándar (lista + modal alta/edición):

```
| Código     | Nombre                | % Reducción | Activo |
| JOVEN      | Estudiante / Joven    | 90,00%      |   ✓    |
| PARADO     | Desempleado           | 90,00%      |   ✓    |
| JUBILADO   | Pensionista           | 50,00%      |   ✓    |
| HONOR      | Cuota honorífica      | 100,00%     |   ✓    |
| BECA       | Beca / social         | 100,00%     |   ✓    |
[+ Nuevo motivo]
```

### 5.3 Asociar motivo a tipo de miembro

Ubicación: Membresía → Parametrización → Tipos de miembro (existente).

Añadir columna "Motivo reducción por defecto":

```
| Tipo         | Motivo reducción default | Cuota efectiva 2026 |
| Ordinario    | (ninguno)                | 50,00 €             |
| De honor     | HONOR (-100%)            |  0,00 €             |
| Simpatizante | JOVEN (-90%) ▼           |  5,00 €             |
```

### 5.4 Generación de cuotas individuales

Pantalla con previsualización antes de confirmar:

```
┌─ Generar cuotas ejercicio 2026 ─────────────────────────────────┐
│ Configuración aplicada: cuota base 50,00 €                       │
│                                                                  │
│ Miembros activos a procesar:                                     │
│   Ordinario:     843 × 50,00 €        =   42 150,00 €            │
│   De honor:       12 × HONOR (-100%) →   excluidos (no cuota)    │
│   Simpatizante:  343 × JOVEN (-90%)   =    1 715,00 €            │
│   ─────────────────────────────────────────────                  │
│   TOTAL ESPERADO:                         43 865,00 € (1 186 cuotas)│
│                                                                  │
│ Ya existen 1 198 cuotas para 2026 (idempotente: se omitirán).    │
│                                                                  │
│ [Cancelar]      [Generar cuotas individuales]                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 6. Permisos / roles

Transacciones nuevas a registrar en el catálogo (`diccionario_transacciones.py`):

| Código | Acción | Acciones que habilita |
|---|---|---|
| `CUOT_EJERCICIO_CONFIG` | Configurar ejercicio (importe base + clonado) | A1, A2 |
| `CUOT_MOTIVO_REDUC_MGMT` | CRUD del catálogo `MotivoReduccion` | A3 |
| `TM_MOTIVO_DEFAULT` | Asociar motivo a TipoMiembro | A4 |
| `CUOT_GENERATE` | Generar cuotas individuales del ejercicio | A5, A6, A7 (ya existe) |

Roles previstos:
- `TESORERO_CENTRAL`: todas.
- `TESORERO_AGRUPACION`: ninguna (la configuración de cuotas es central).
- `ADMINISTRADOR`: CRUD de motivos (parametrización).

---

## 7. Norma legal aplicable

- **Ley Orgánica 1/2002 reguladora del Derecho de Asociación, art. 7.f**: los estatutos deben recoger el patrimonio inicial y los recursos económicos previstos. La cuota es el principal y ha de poder fijarse y modificarse por el órgano competente.
- **Ley 50/2002 de Fundaciones (si aplica) y PCESFL 2013, norma 4ª de elaboración** (principio de uniformidad): la política de cuotas debe ser consistente y trazable de un ejercicio al siguiente.
- **LO 8/2007 de financiación de partidos políticos** (si aplica): las cuotas de afiliados son la principal fuente de ingresos privada admitida; deben quedar perfectamente registradas y atribuibles a un miembro identificado (sin anonimato ni cuotas globales).
- **AEAT, Modelo 182** (cuando el socio puede deducirse parte): la cuota debe quedar identificada con el NIF del aportante para poder declararla.

---

## 8. Estado de implementación actual (revisado mayo 2026)

| Pieza | Estado |
|---|---|
| Tabla `tipos_miembro` con `motivo_reduccion_id` | ✓ |
| Tabla `importes_cuota_anio` (4 filas para 2026, reutilizada para la cuota base) | ✓ |
| Tabla `cuotas_anuales` con `motivo_reduccion_id` | ✓ |
| Tabla `motivos_reduccion_cuota` (5 registros seed) | ✓ |
| `MotivoReduccionCuota.excluye_cuota` (property: `%≥100`) — D1.4 | ✓ |
| `MotivoReduccionCuota.aplicar_a(importe_base)` | ✓ |
| `CuotaService.configurar_ejercicio(ejercicio, importe_base, clonar_de=None)` — A3 | ✓ |
| `CuotaService.previsualizar_generacion(ejercicio)` — A4 | ✓ |
| `CuotaService.generar_cuotas_individuales(ejercicio)` — A5 (idempotente) | ✓ |
| `CuotaService.recalcular_cuota(cuota_id)` — A6 | ✓ |
| `CuotaService.listar_motivos()` | ✓ |
| Mutations GraphQL: `configurarCuotaEjercicio`, `previsualizarGeneracionCuotas`, `generarCuotasIndividuales` | ✓ |
| Mutations GraphQL: CRUD de motivos (`crearMotivoReduccion`, `actualizarMotivoReduccion`) | ✓ |
| Vista `MotivosReduccionCuota.vue` (catálogo) | ✓ |
| Vista `CuotasEjercicio.vue` (configurar + generar, dos pasos D1.3) | ✓ |
| Vista `Cuotas.vue` (listado) | ✓ |
| Selector de `motivo_reduccion_id` en `TiposMiembro.vue` (catálogo Membresía) — D1.2 | ✓ |
| **`CuotaService.recalcular_lote(ejercicio)`** — A7 | ✗ falta |
| **Permisos `CUO_*` en `transacciones.json` + matriz** | ✗ falta (mutations actualmente sin guard) |
| **Guards `@RequireTransaction("CUO_*")` en las mutations** | ✗ falta |
| **Sección flujo 1 en `Ayuda.vue`** | ✗ falta |

El flujo 1 está casi terminado. **Los gaps son cosméticos** (recalcular_lote + ayuda) y **uno crítico** (permisos: hoy cualquier usuario autenticado puede generar cuotas en bloque).

---

## 9. Implementación propuesta (gaps reales, mayo 2026)

**Lote A — Permisos (crítico)**

1. Añadir 3 transacciones nuevas a `transacciones.json` (las otras 2 ya existían con prefijo `CUOT_`):
   - `CUOT_MOTIVO_LIST`, `CUOT_GENERAR`, `CUOT_LIST` (nuevas).
   - `CUOT_EJERCICIO_CONFIG`, `CUOT_MOTIVO_REDUC_MGMT` (ya existían).
   - (Se descarta `CUOT_RECALCULAR` porque D1.5 elimina el recálculo en bloque.)
2. Seed reproducible `seed_permisos_cuotas.py` con:
   - `CUOT_MOTIVO_REDUC_MGMT`, `CUOT_EJERCICIO_CONFIG`, `CUOT_GENERAR` → solo TESORERO (matriz, D1.6).
   - `CUOT_MOTIVO_LIST`, `CUOT_LIST` → TESORERO + AUDITOR.
3. Decorar mutations con `@RequireTransaction("CUOT_*")` correspondiente:
   - `crearMotivoReduccion`, `actualizarMotivoReduccion` → `CUOT_MOTIVO_REDUC_MGMT`.
   - `configurarCuotaEjercicio` → `CUOT_EJERCICIO_CONFIG`.
   - `previsualizarGeneracionCuotas`, `generarCuotasIndividuales` → `CUOT_GENERAR`.
   - `recalcularCuota` (individual) → `CUOT_GENERAR` (es excepción puntual, no abre flujo).

**Lote B — Backend: inmutabilidad del porcentaje (D1.5)**

4. `CuotaService.motivo_tiene_recibos(motivo_id) -> bool` que devuelve true si hay ≥1 `Recibo` (cualquier estado) vinculado a cuotas que usan ese motivo.
5. Query GraphQL `motivoTieneRecibos(motivoId: UUID!) -> Boolean` (consulta para que la UI pre-deshabilite el input).
6. En `actualizarMotivoReduccion`: si `motivo_tiene_recibos` y el `porcentaje_reduccion` del input difiere del actual, lanzar `ValueError` con mensaje claro.

**Lote C — Frontend (pequeño)**

7. En `MotivosReduccionCuota.vue`, al abrir el modal de edición de un motivo:
   - Llamar a `motivoTieneRecibos` para saber si el % está bloqueado.
   - Si lo está, deshabilitar el input del % y mostrar un aviso ("El porcentaje no se puede modificar porque ya hay recibos emitidos con este motivo. Anula las cuotas afectadas para liberar el motivo.").
8. Verificar que la edición de `TipoMiembro` permite quitar el motivo (poner a null) y guarda correctamente.

**Lote D — Ayuda**

9. Acordeón "Flujo · Cuotas del ejercicio" en `Ayuda.vue` (sección Económico), reflejando D1.1–D1.6.

---

## 10. Decisiones tomadas (mayo 2026)

### D1.1 · Cuota base + porcentaje de reducción por motivo

**Decisión**: una sola cuota base por ejercicio (NUMERIC(10,2)). Cualquier reducción se modela como un `MotivoReduccion` con `porcentaje_reduccion` (0–100). El importe efectivo = `importe_base × (1 − %/100)`, redondeado a 2 decimales.

**Alternativas descartadas**:
- Una fila por tarifa (`General`, `Joven`, `Parado`…) — descartado por rigidez: cualquier cambio en la base obliga a editar N filas.
- Importe fijo de reducción — descartado porque al cambiar la base no se actualizan automáticamente las cuotas reducidas.

**Para el manual**:
- *Tesorero*: configura una sola cuota base; los motivos se gestionan en su catálogo y se aplican automáticamente.

### D1.2 · Asignación automática por tipo de miembro

**Decisión**: cada `TipoMiembro` lleva un `motivo_reduccion_id` opcional. Al generar cuotas individuales, se aplica automáticamente el motivo del tipo de cada miembro. Si NULL, paga cuota base completa.

**Alternativas descartadas**:
- Campo `motivo_reduccion_id` en `Miembro` (override individual) — pospuesto a v2. La regla "automática por tipo" es suficiente para la mayoría.
- Combinación con override manual — sin caso de uso claro ahora; se añade si los tesoreros lo piden.

**Para el manual**:
- *Tesorero*: si un miembro debe pagar cuota distinta, debe cambiar su `tipo_miembro` (existente).
- *Administrador*: mantiene la asociación tipo ↔ motivo en parametrización.

### D1.3 · Dos pasos separados (configurar / generar)

**Decisión**: la pantalla 5.1 configura importes (revisable a discreción del tesorero). La pantalla 5.4 genera las `CuotaAnual` solo cuando el tesorero lo aprueba. Antes muestra previsualización con total esperado y desglose.

**Alternativas descartadas**:
- 1 paso (configurar y generar a la vez) — descartado porque revisar miles de cuotas creadas por error es costoso de revertir.
- Generación diferida por miembro (al alta o aniversario) — descartado: las cuotas siguen un ejercicio común, no un ciclo personal.

**Para el manual**:
- *Tesorero*: primero configura los importes del ejercicio; cuando esté seguro, pulsa "Generar cuotas". Es idempotente — si ya hay cuotas del ejercicio, no las duplica.

### D1.4 · Tipos sin cuota (Honorario) → excluidos del proceso

**Decisión**: si el `TipoMiembro` apunta a un `MotivoReduccion` con `porcentaje_reduccion = 100` **o** está marcado como exclusivo, los miembros de ese tipo **NO** generan `CuotaAnual`. No se les emite recibo ni se incluyen en remesas. Simplifica: en BD no aparecen, las consultas de "cuotas pendientes" no los muestran, no se filtra nada en lógica posterior.

Implementación: en `CuotaService.generar_cuotas_individuales(ejercicio)`, antes de crear cada cuota, comprobar:
```python
motivo = tipo_miembro.motivo_reduccion
if motivo and motivo.porcentaje_reduccion >= 100:
    continue  # excluido del proceso
```

**Alternativas descartadas**:
- Generar `CuotaAnual` con importe 0 y estado `Exenta` — descartado por ruido en listados y reportes.
- Bandera `excluye_de_emision` en MotivoReduccion — descartado por redundancia con el porcentaje ≥100%; la regla "100% reducción ⇒ no se genera" es suficiente y más sencilla.

**Para el manual**:
- *Tesorero*: si quieres que un grupo de socios no pague cuota (honoríficos, beca total), asóciales un tipo de miembro con motivo `HONOR` (100% reducción). El sistema los excluye automáticamente.
- *Administrador*: los motivos al 100% son "no genera cuota". Para los que pagan menos pero sí pagan, usar % < 100.

---

## 11. Implicaciones para otros módulos

- **Membresía / TipoMiembro**: se amplía la pantalla de edición de TipoMiembro con un selector de motivo por defecto.
- **Catálogos (Parametrización)**: nueva entrada "Motivos de reducción de cuota".
- **Flujo 2 (Emisión de recibos)**: depende de este flujo — el recibo toma el `importe` ya calculado de `CuotaAnual`.
- **Modelo 182 (Flujo 11)**: el importe declarable es el `importe` efectivo, no el de la base — el modelo ya lo cubre.
