# Flujo 2 — Emisión de recibos

## 1. Propósito

Emitir los **recibos numerados** que justifican el cobro de cada cuota anual del socio. El recibo es el documento formal entre la entidad y el socio: lleva número correlativo (`REC-{AGR}-{YYYY}-{NNNNN}`), concepto, importe, fechas y estado de cobro. Es el justificante que el socio puede pedir y la pieza que el módulo de Comunicación Interna adjunta al email de aviso.

Sin emisión previa no hay remesa SEPA posible (flujo 3) ni cobro manual trazable (flujo 5). Este flujo cierra el triángulo: **Cuota anual (flujo 1) → Recibo emitido (flujo 2) → Cobro (flujos 3/4/5)**.

---

## 2. Entidades implicadas

### 2.1 `Recibo` (existente, modelo `recibos`)

Campos relevantes:
- `id`, `numero_recibo` (UNIQUE), `ejercicio`
- `tipo` ∈ {CUOTA_ORDINARIA, EXTRAORDINARIA, REENVIO}
- `concepto` (libre, ej. "Cuota ordinaria 2025")
- `miembro_id` FK → `miembros.id`
- `cuota_id` FK → `cuotas_anuales.id` (nullable: extraordinarias)
- `orden_cobro_id` FK → `ordenes_cobro.id` (nullable hasta liquidación)
- `importe`, `importe_pagado`
- `estado` ∈ {EMITIDO, COBRADO, FALLIDO, ANULADO}
- `modo_cobro` ∈ {SEPA, TRANSFERENCIA, MANUAL, EFECTIVO, TARJETA}
- `fecha_emision`, `fecha_vencimiento`, `fecha_cobro`
- `fecha_aviso_fallido`, `plantilla_email_aviso_id` (flujo 4)

Faltará añadir:
- `agrupacion_id` UUID FK → `unidades_organizativas.id` (D2.3 — numeración por agrupación)

### 2.2 `CuotaAnual` (referida)

- Su `id` se referencia desde `Recibo.cuota_id`.
- Su estado pasa a `Cobrada` cuando el recibo asociado pasa a `COBRADO`.

### 2.3 `UnidadOrganizativa` (referida)

- `nombre_corto` se usa como prefijo en el número de recibo (D2.3).

---

## 3. Estados y transiciones

```
   ┌─────────┐  emitir_lote/individual    ┌─────────┐
   │ (nuevo) │ ──────────────────────────> │ EMITIDO │
   └─────────┘                             └────┬────┘
                                                │
        ┌───────────────────────────────────────┼─────────────────────────┐
        │ marcar_cobrado_manual                 │ liquidar_remesa         │ anular
        ▼                                       ▼                         ▼
   ┌─────────┐                            ┌─────────┐              ┌─────────┐
   │ COBRADO │                            │ COBRADO │              │ ANULADO │
   └─────────┘                            └─────────┘              └─────────┘
   (modo MANUAL/                          (modo SEPA con           (cuota vuelve
    TRANSF/EFE/TAR)                        orden_cobro_id)         a Pendiente)
                                                │
                                                │ marcar_fallido
                                                ▼
                                          ┌─────────┐
                                          │ FALLIDO │
                                          └────┬────┘
                                               │ generar_remesa_fallidos
                                               ▼
                                          (nuevo Recibo
                                           tipo REENVIO)
```

---

## 4. Acciones

| # | Acción | Quién dispara | Pre-estado | Post-estado | Efecto |
|---|---|---|---|---|---|
| A1 | **Emitir lote ordinario** | Tesorero (UI) | sin recibos para esas cuotas | N recibos `EMITIDO` con número correlativo por agrupación | Selecciona ejercicio + agrupación (opcional) + filtra miembros |
| A2 | **Emitir recibo individual extraordinario** | Tesorero (UI) | — | 1 recibo `EMITIDO` tipo EXTRAORDINARIA | Para derramas, formación, donación |
| A3 | **Marcar cobrado manualmente** | Tesorero (UI desde detalle de recibo) | `EMITIDO` o `FALLIDO` | `COBRADO` con `modo_cobro` y `fecha_cobro` | Crea `ApunteCaja` + asiento contable (regla MANUAL/INGRESO) |
| A4 | **Anular recibo** | Tesorero (UI desde detalle) | `EMITIDO` o `FALLIDO` (no `COBRADO`) | `ANULADO` con observación motivo | Cuota vuelve a `Pendiente` (si tipo CUOTA_ORDINARIA) |
| A5 | **Descargar PDF (A5 resguardo)** | Tesorero / Socio | cualquier estado | sin cambios | Genera PDF con plantilla configurable (ver pendiente A5 en backlog) |
| A6 | **Enviar PDF al socio por email** | Tesorero (UI desde detalle o lote) | cualquier estado | sin cambios + log de envío | Usa plantilla de email del módulo Comunicación Interna |

---

## 5. Pantallas UI

### 5.1 Listado de recibos

Ubicación: módulo Tesorería → acordeón "Cuentas a cobrar" → botón "Ver listado" del bloque Recibos.

Ruta dedicada: `/economico/recibos`.

```
┌─ Recibos ──────────────────────────────────────────────────────────┐
│ Ejercicio [2025 ▼]  Estado [Todos ▼]  Agrupación [Todas ▼]         │
│ Miembro [buscar…]                            [+ Emitir lote]       │
├────────────────────────────────────────────────────────────────────┤
│ Nº recibo            │ Socio          │ Importe │ Estado  │ Cobro │
│ REC-MAD-2025-00042   │ García López   │ 50,00 € │ COBRADO │ 15/06 │
│ REC-MAD-2025-00043   │ Pérez Martín   │ 50,00 € │ FALLIDO │   —   │
│ REC-BCN-2025-00012   │ Ruiz Sanz      │ 50,00 € │ EMITIDO │   —   │
│ …                                                                  │
├────────────────────────────────────────────────────────────────────┤
│ 3 462 recibos · 3 128 cobrados · 334 fallidos                      │
└────────────────────────────────────────────────────────────────────┘
```

Acciones por fila: ver detalle (modal), descargar PDF, enviar email.

### 5.2 Emitir lote

Modal accesible desde botón "Emitir lote":

```
┌─ Emitir lote de recibos ──────────────────────────────────────────┐
│ Ejercicio: [ 2025 ▼ ]                                              │
│ Tipo:      ● Cuota ordinaria  ○ Cuota extraordinaria               │
│ Agrupación: [ Toda la organización ▼ ]                             │
│ Concepto: [ "Cuota ordinaria ejercicio 2025" ]                     │
│ Fecha emisión: [ 15/01/2025 ]                                      │
│                                                                    │
│ Previsualización:                                                  │
│   1 247 socios con cuota pendiente sin recibo emitido             │
│   Total a emitir: 62 350,00 €                                      │
│                                                                    │
│ [Cancelar]                          [Emitir 1 247 recibos]         │
└────────────────────────────────────────────────────────────────────┘
```

### 5.3 Detalle de recibo (modal)

```
┌─ Recibo REC-MAD-2025-00042 ───────────────────────────────────────┐
│ Estado: COBRADO                                                    │
│ Socio: María García López (socia nº 4218)                          │
│ Concepto: Cuota ordinaria ejercicio 2025                           │
│ Importe: 50,00 €  (pagado: 50,00 €)                                │
│ Modo cobro: SEPA   Fecha emisión: 15/01/25   Fecha cobro: 15/06/25 │
│ Orden de cobro: REM-2025-005-042 (remesa SEPA)                     │
│                                                                    │
│ [Descargar PDF] [Enviar al socio] [Anular] (deshabilitado COBRADO) │
└────────────────────────────────────────────────────────────────────┘
```

---

## 6. Permisos / roles

Transacciones a registrar en el catálogo:

| Código | Acción | Activa |
|---|---|---|
| `RCB_EMIT_LOTE` | Emitir lote ordinario/extraordinario | A1, A2 |
| `RCB_MARCAR_COBRADO` | Marcar cobrado manualmente | A3 |
| `RCB_ANULAR` | Anular recibo emitido o fallido | A4 |
| `RCB_DESCARGAR_PDF` | Descargar PDF del recibo | A5 |
| `RCB_ENVIAR_EMAIL` | Enviar PDF al socio por email | A6 |
| `RCB_LIST` | Ver listado de recibos (ya existe) | listado/detalle |

Roles previstos:
- `TESORERO_CENTRAL`: todas, sin filtro de agrupación.
- `TESORERO_AGRUPACION`: todas pero solo sobre recibos de su `agrupacion_id`.
- `SOCIO`: solo `RCB_LIST` + `RCB_DESCARGAR_PDF` sobre sus propios recibos (futuro, vista "Mis recibos").

---

## 7. Norma legal aplicable

- **Código de Comercio art. 25** — todo movimiento debe documentarse y guardarse 10 años. El recibo numerado es la prueba del cobro frente a auditoría y socio.
- **PCESFL 2013, norma 1ª de elaboración** (imagen fiel) — la cuenta `430 Usuarios deudores` debe reflejar exactamente los recibos emitidos no cobrados; sin recibo formal no hay cómo conciliar.
- **Ley Orgánica 8/2007 art. 14** (partidos políticos) — cada cuota debe ser atribuible a un afiliado identificado con NIF; el recibo es el justificante de esa atribución.
- **AEAT Modelo 182** — para que el socio pueda deducir su donación o cuota en IRPF (Ley 49/2002), la entidad debe poder demostrar cobro con número de recibo y fecha. El recibo es la base.

---

## 8. Estado de implementación actual

| Pieza | Estado |
|---|---|
| Modelo `Recibo` con campos completos | ✓ |
| `ReciboService.siguiente_numero(ejercicio)` (numeración global) | ✓ (necesita refactor a por-agrupación) |
| `ReciboService.emitir_lote(...)` | ✓ |
| `ReciboService.emitir_recibo_individual(...)` | ✓ |
| `ReciboService.marcar_cobrado(...)` | ✓ |
| `ReciboService.marcar_fallido(...)` | ✓ |
| `ReciboService.anular_recibo(...)` | ✓ |
| GraphQL mutation `emitir_recibos_lote` | ✓ |
| **Columna `recibos.agrupacion_id`** | ✗ falta |
| **Numeración por agrupación (D2.3)** | ✗ falta |
| **Vista `Recibos.vue`** (listado + filtros) | ✗ falta |
| **Modal `EmitirLoteRecibosModal.vue`** | ✗ falta |
| **Modal `DetalleReciboModal.vue`** | ✗ falta |
| **PDF resguardo bancario A5** | ✗ falta (en backlog) |
| **Envío de PDF por email** | ✗ falta (depende de plantilla A5) |
| **5 permisos nuevos** (RCB_EMIT_LOTE, RCB_MARCAR_COBRADO, RCB_ANULAR, RCB_DESCARGAR_PDF, RCB_ENVIAR_EMAIL) | ✗ falta |

---

## 9. Implementación propuesta

**Lote A — Backend**

1. SQL: `ALTER TABLE recibos ADD COLUMN agrupacion_id UUID REFERENCES unidades_organizativas(id) ON DELETE SET NULL;` + índice. Backfill: NULL para recibos históricos (no se renumeran).
2. Modelo `Recibo`: añadir `agrupacion_id` y relationship `agrupacion`.
3. `ReciboService.siguiente_numero(ejercicio, agrupacion_id) → str`:
   - Si `agrupacion_id` y la agrupación tiene `nombre_corto`: formato `REC-{NOMBRE_CORTO}-{ejercicio}-{NNNNN}`.
   - Si no: formato legacy `REC-{ejercicio}-{NNNNN}` (para retrocompatibilidad).
   - Contador correlativo dentro de (ejercicio, agrupacion_id).
4. `ReciboService.emitir_lote(...)`: pasar `agrupacion_id` y aplicar el nuevo formato.
5. Nuevas mutations GraphQL:
   - `marcar_recibo_cobrado_manual(recibo_id, modo_cobro, fecha_cobro, cuenta_bancaria_id?, observaciones?)` con permission `RCB_MARCAR_COBRADO`. Crea `ApunteCaja` + asiento si tipo CUOTA y cuenta bancaria informada.
   - `anular_recibo(recibo_id, motivo?)` con permission `RCB_ANULAR`. Revierte cuota a Pendiente.
   - `enviar_recibo_email(recibo_id, plantilla_email_id)` con permission `RCB_ENVIAR_EMAIL` (envío queda como TODO de integración real con Comunicación Interna; por ahora solo registra fecha).
6. Mutation GraphQL `descargar_recibo_pdf(recibo_id) -> String` que devuelve el PDF en base64. Usa plantilla configurable (ver plantilla PDF A5 en backlog) — si no hay plantilla aún, generar uno básico con `reportlab`. El frontend hace `atob()` y descarga como blob. (REST descartado — el proyecto usa GraphQL para todo).
7. Registrar 5 nuevas transacciones en `diccionario_transacciones.py` y `transacciones.json`.

**Lote B — Frontend**

8. Nueva ruta `/economico/recibos` → vista `Recibos.vue`:
   - Filtros: ejercicio, estado, agrupación, búsqueda por miembro.
   - Tabla con columnas Nº recibo, socio, importe, estado, fecha cobro.
   - Acciones por fila: detalle (modal), descargar PDF, enviar email.
   - Botón "+ Emitir lote".
9. Componente `EmitirLoteRecibosModal.vue` con previsualización antes de confirmar.
10. Componente `DetalleReciboModal.vue` con acciones según estado.
11. Acceso desde el Hub Tesorería: el bloque "Recibos" de Cuentas a cobrar pasa de `Bloque` con acción "Emitir lote desde Remesas" a `Bloque` con acción "Abrir Recibos" → `/economico/recibos`.

**Lote C — PDF (deferred al backlog)**

- Plantilla A5 estilo resguardo bancario gestionada desde Parámetros Generales. Mientras no exista, generación mínima con `reportlab` (datos esenciales sin estética).

---

## 10. Decisiones tomadas (mayo 2026)

### D2.1 · Emisión manual por el tesorero, no automática al generar remesa

**Decisión**: el tesorero pulsa "Emitir lote" cuando lo decide. Sin acoplamiento automático con remesa.

**Alternativas descartadas**:
- Emisión automática al crear remesa — descartada porque rompe la separación de fases (emisión es un acto formal independiente del cobro) y dificulta emitir recibos para cobros manuales fuera de remesa.
- Híbrido manual + automático al detectar pendientes en remesa — descartado por complejidad y porque oculta al tesorero qué se está emitiendo.

**Para el manual**:
- *Tesorero*: emite el lote cuando esté listo. Después puede incluir esos recibos en una remesa SEPA, registrar cobros manuales o exportar PDFs.

### D2.2 · Acciones por recibo individual: 4

**Decisión**: el tesorero puede sobre un recibo individual: marcar cobrado manualmente, anular, descargar PDF, enviar PDF por email al socio. Las 4 disponibles según permisos del rol.

**Para el manual**:
- *Tesorero*: desde el detalle del recibo, dispone de las 4 acciones. Anular solo es posible si no está COBRADO. Marcar cobrado pide la cuenta bancaria de destino para generar el apunte de caja.

### D2.3 · Numeración correlativa por agrupación territorial

**Decisión**: el número de recibo es `REC-{NOMBRE_CORTO_AGRUPACION}-{YYYY}-{NNNNN}` (ej. `REC-MAD-2025-00042`). El correlativo se reinicia cada ejercicio dentro de cada agrupación. Si no hay agrupación, formato legacy `REC-{YYYY}-{NNNNN}`.

**Alternativas descartadas**:
- Numeración global por entidad — descartada porque rompe el principio de descentralización: cada tesorero territorial debe tener su serie autocontenida.

**Consecuencias técnicas**:
- Nueva columna `recibos.agrupacion_id`.
- Refactor de `ReciboService.siguiente_numero` para aceptar `agrupacion_id`.
- Los 3 462 recibos históricos mantienen formato legacy (no se renumeran).
- En el listado UI hay que mostrar agrupación como columna o filtro.

**Para el manual**:
- *Tesorero central*: ve todas las series por agrupación.
- *Tesorero de agrupación*: solo su serie (con prefijo único).
- *Socio*: en su recibo verá el prefijo de la agrupación a la que pertenece.

---

## 11. Implicaciones para otros módulos / flujos

- **Flujo 3 (Remesas)**: la generación de remesa debe respetar el `agrupacion_id` del recibo (ya implementado parcialmente vía `agrupacion_id` en `Remesa`).
- **Flujo 4 (Liquidación)**: al marcar cobrado un recibo desde liquidación, debe actualizar también el `agrupacion_id` si proviene de remesa (ya lo hace por la cuota).
- **Comunicación Interna**: nueva plantilla email tipo `RECIBO_EMITIDO` para el envío A6.
- **Backlog**: la plantilla PDF A5 estilo resguardo bancario (anotada hace un par de días) entra como dependencia de A5/A6.
