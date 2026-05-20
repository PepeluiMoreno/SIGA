# Flujo 4 — Liquidación de remesa SEPA

## 1. Propósito

Procesar la **respuesta del banco** a una remesa SEPA enviada. El banco devuelve dos tipos de información:

- **Fichero `pain.002`** (Payment Status Report) o **`camt.054`** (Bank to Customer Debit/Credit Notification) → notifica las órdenes que el banco no ha podido cobrar, con un código de rechazo SEPA (AM04, MD01, AC04, AC13, MS02…) y la fecha de devolución.
- **Extracto bancario `camt.053` o CSV/MT940**, con el detalle del ingreso bruto recibido en la cuenta corriente del acreedor (la asociación) y los cargos individuales correspondientes a cada cobro exitoso.

El resultado de procesar ambos ficheros es:

1. Cada `OrdenCobro` queda marcada como `Procesada` o `Fallida` con su código SEPA.
2. La `Remesa` pasa a estado `Procesada` (si todas las órdenes están en estado terminal) o `Parcial` (si quedan en `Pendiente`).
3. Los recibos `EMITIDO` asociados a órdenes cobradas pasan a `COBRADO`; los asociados a fallidas pasan a `FALLIDO`.
4. Las cuotas correspondientes a los cobros exitosos quedan **pagadas** (`importe_pagado` actualizado, estado `Cobrada`).
5. Se crea un `ApunteCaja` de ingreso en la cuenta bancaria del acreedor por el neto del lote, y se genera el asiento contable Debe `572` / Haber `721` o `430` según la regla aplicable.

Este flujo es el **único momento en que el dinero realmente entra** en la cuenta de la asociación; lo previo (emisión de recibos, generación de remesa, envío al banco) son compromisos formales, no caja.

---

## 2. Entidades implicadas

### 2.1 `Remesa`  (`remesas`)

Campos relevantes:
- `id`, `referencia`, `fecha_creacion`, `fecha_envio`, `fecha_cobro`
- `importe_total`, `gastos`, `num_ordenes`
- `estado_id` → FK a `estados_remesa`
- `tipo_remesa` ∈ {ORDINARIA, EXTRAORDINARIA, REENVIO}
- `seq_tipo` ∈ {FRST, RCUR, LAST, OOFF} (norma EPC131-08)
- `archivo_sepa`, `mensaje_id`
- `agrupacion_id` (tesorería delegada)
- `remesa_origen_id` (si es REENVIO, apunta a la remesa origen)

### 2.2 `OrdenCobro`  (`ordenes_cobro`)

Cada deudor → una orden. Campos:
- `id`, `remesa_id`, `cuota_id`
- `importe`, `referencia_mandato`, `iban`
- `estado_id` → FK a `estados_orden_cobro`
- `fecha_procesamiento`, `codigo_rechazo`, `motivo_rechazo`, `fecha_rechazo`

### 2.3 `Recibo`  (`recibos`)

- `cuota_id` apunta a la cuota cuyo cobro se intenta vía esta orden.
- El recibo se emitió ANTES de la remesa (flujo 2). En este flujo cambia su `estado` y se rellena `fecha_cobro` o `observaciones` de fallido.

### 2.4 `CuotaAnual`  (`cuotas_anuales`)

- `importe_pagado` se incrementa con el importe cobrado.
- `estado_id` → de `Pendiente` a `Cobrada` cuando `importe_pagado ≥ importe`.

### 2.5 `ApunteCaja`  (`apuntes_caja`)

Por cada cobro exitoso se crea uno con:
- `cuenta_bancaria_id` = cuenta del acreedor
- `tipo = INGRESO`, `origen = REMESA`
- `entidad_origen_tipo = "remesa"`, `entidad_origen_id = remesa.id`
- `importe`, `fecha = fecha_cobro_real`
- `concepto = "Liquidación remesa {referencia}"`

### 2.6 `AsientoContable` (auto, vía `RegistroContable`)

Por cada `ApunteCaja` se genera Debe `572` (Bancos) / Haber `721` o `430`, según la regla `REMESA/INGRESO`.

---

## 3. Estados y transiciones

### 3.1 Máquina de estados de `Remesa`

```
            ┌────────────┐
            │  Borrador  │  ← se está rellenando, aún no se ha generado XML
            └─────┬──────┘
                  │ generar_xml_sepa()
                  ▼
            ┌────────────┐
            │  Generada  │  ← XML creado, sin enviar al banco
            └─────┬──────┘
                  │ marcar_enviada()
                  ▼
            ┌────────────┐
            │  Enviada   │  ← XML enviado al banco, esperando respuesta
            └─────┬──────┘
                  │ procesar_respuesta_banco()
        ┌─────────┼────────┐
        ▼         ▼        ▼
   ┌──────────┐ ┌────────┐ ┌──────────┐
   │Procesada │ │Parcial │ │Rechazada │
   └──────────┘ └────────┘ └──────────┘
   (todas OK)   (algunas    (banco
                 fallidas)   rechaza
                             lote
                             entero)
```

### 3.2 Máquina de estados de `OrdenCobro`

```
   ┌───────────┐
   │ Pendiente │  ← creada con la remesa
   └─────┬─────┘
         │ procesar_respuesta_banco
   ┌─────┴─────┐
   ▼           ▼
┌──────────┐ ┌─────────┐
│Procesada │ │ Fallida │
└──────────┘ └────┬────┘
                  │ generar_remesa_fallidos
                  ▼
            (nueva orden en
             remesa REENVIO,
             SeqTp=FRST)
```

Hay un estado `Anulada` para órdenes que se cancelan antes de procesar (cuota anulada manualmente, etc.).

### 3.3 Máquina de estados de `Recibo` (referida a este flujo)

```
   EMITIDO ──┬──> COBRADO   (orden Procesada)
             └──> FALLIDO   (orden Fallida)
```

Solo se transiciona en este flujo; los recibos `ANULADO` o ya `COBRADO` se ignoran.

---

## 4. Acciones

| # | Acción | Quién la dispara | Pre-estado | Post-estado | Lado de efecto |
|---|---|---|---|---|---|
| A1 | **Importar fichero pain.002 / camt.054** | Tesorero (UI) o sistema (webhook PSD2 futuro) | Remesa `Enviada` | sin cambio aún | Crea registro `RespuestaBanco` con líneas no procesadas |
| A2 | **Previsualizar resultado** | Tesorero (UI) | Remesa `Enviada` | sin cambio | Muestra emparejamiento orden ↔ código rechazo, lista de cobradas/fallidas |
| A3 | **Confirmar liquidación** | Tesorero (UI) | Remesa `Enviada` | Remesa → `Procesada` / `Parcial`; Órdenes → `Procesada` / `Fallida`; Recibos → `COBRADO` / `FALLIDO`; Cuotas → `Cobrada` para las exitosas; nuevo `ApunteCaja` ingreso bruto; asiento contable | DB transaccional |
| A4 | **Generar remesa de reenvío** | Tesorero (UI) | Remesa `Procesada/Parcial` con ≥1 fallida re-presentable | Nueva remesa `Borrador` `tipo=REENVIO`, `seq_tipo=FRST`, `remesa_origen_id = remesa.id` | Nuevas órdenes en `Pendiente` |
| A5 | **Anular orden no re-presentable** | Tesorero (UI) | Orden `Fallida` con código `MD01`, `MS02` u otros no representables | Orden → `Anulada`; recibo asociado se mantiene `FALLIDO`; cuota se mantiene pendiente (o anulada según política) | DB |

**Códigos SEPA gestionados** (subconjunto operativo más frecuente):
- Re-presentables (cobro automático posterior): `AM04` (fondos insuficientes), `AC04` (cuenta cerrada — solo con nuevo mandato), `MS03` (motivo no especificado).
- No re-presentables sin autorización: `MD01` (sin mandato), `MS02` (deudor solicita la devolución), `AC13` (deudor no autorizado).
- Códigos técnicos: `AC01` (formato cuenta), `AC06` (cuenta bloqueada).

---

## 5. Pantallas UI

Las dos pantallas viven en el módulo Económico, sección Tesorería → Remesas.

### 5.1 Detalle de una Remesa (estado `Enviada`)

Cabecera: referencia, fechas, total, num órdenes, estado actual.

Sección "Liquidar banco":

```
┌─ Cargar respuesta del banco ─────────────────────────────────────┐
│                                                                  │
│  Tipo:  ◉ pain.002 (Payment Status Report)                       │
│         ○ camt.054 (Bank to Customer Notification)               │
│         ○ Entrada manual (lista de fallidos)                     │
│                                                                  │
│  Fichero:  [ Seleccionar archivo… ]                              │
│  Fecha de liquidación:  [ __/__/____ ]                           │
│                                                                  │
│  [ Previsualizar ]                                               │
└──────────────────────────────────────────────────────────────────┘
```

Tras "Previsualizar" → tabla con dos paneles:

```
COBRADAS (487)                       │  FALLIDAS (13)
─────────────────────────────────────┼──────────────────────────────
Orden  Miembro             Importe   │  Orden  Miembro     Código  Motivo
─────────────────────────────────────┼──────────────────────────────
…                                    │  #032  García L.   AM04    Fondos insuf.
…                                    │  #058  Pérez M.    MD01    Sin mandato
                                     │  …

TOTAL COBRADO: 24 350,00 €           │  TOTAL FALLIDO: 650,00 €
```

Botones:
- `Confirmar liquidación` (verde, primario) → A3
- `Cancelar` (vuelve a "Cargar respuesta")

### 5.2 Detalle de una Remesa (estado `Procesada` o `Parcial`)

Igual que 5.1 pero:
- La sección "Liquidar banco" se sustituye por la lista final de órdenes con su estado y código.
- Aparece un botón `Generar remesa de reenvío` si hay ≥1 fallida re-presentable.

### 5.3 Listado de Remesas

Columnas: referencia, fecha cobro, tipo, importe, nº órdenes, **estado** (badge color), **% cobrado** (si Procesada/Parcial). Acciones según estado.

---

## 6. Permisos / roles

Nuevas transacciones a definir en la matriz de permisos:

| Transacción | Acción habilitada |
|---|---|
| `ECO_REMESA_LIQUIDAR` | A1, A2, A3 — procesar respuesta del banco |
| `ECO_REMESA_REENVIAR` | A4 — generar remesa de reenvío |
| `ECO_ORDEN_ANULAR` | A5 — anular orden no re-presentable |

Roles que deberían tenerlas:
- `TESORERO_CENTRAL`: todas, sin filtro de agrupación.
- `TESORERO_AGRUPACION`: solo sobre remesas con `agrupacion_id` = su agrupación.
- `AUDITOR`: lectura sobre estos datos, sin las transacciones.

---

## 7. Norma legal aplicable

- **EPC131-08** (SEPA Core Direct Debit Rulebook): define el formato de los ficheros `pain.002` / `camt.054`, los códigos de rechazo (R-Reasons) y el calendario de re-presentación (5 días hábiles para devolución no autorizada por motivos técnicos; 8 semanas si el deudor solicita devolución; 13 meses si el cobro no estaba autorizado).
- **PCESFL 2013, norma 1ª de elaboración** (imagen fiel): el balance debe reflejar la situación real de cobros pendientes (`430 Usuarios deudores`) y los fallidos no cobrados; sin registrar los rechazos se falsea la imagen fiel.
- **Código de Comercio art. 25.1**: todo cobro debe quedar reflejado día a día en el Libro Diario.
- **Reglamento (UE) 260/2012**: obliga a aceptar las devoluciones SEPA dentro del calendario y a poder identificar cada devolución con el código R asignado por el banco.

---

## 8. Estado de implementación actual

| Pieza | Estado |
|---|---|
| Modelo `Remesa` con `tipo_remesa`, `seq_tipo`, `remesa_origen_id` | ✓ |
| Modelo `OrdenCobro` con `codigo_rechazo`, `motivo_rechazo`, `fecha_rechazo` | ✓ |
| `RemesaService.importar_fallidos_banco(remesa_id, fallidos[])` | ✓ (input manual) |
| `RemesaService.generar_remesa_fallidos(remesa_origen_id)` | ✓ |
| **Parser de `pain.002`** | ✗ falta |
| **Parser de `camt.054`** | ✗ falta |
| `RemesaService.liquidar_remesa(remesa_id, fecha, cobradas, fallidas)` — atómico: cobradas → recibos COBRADOS, cuotas pagadas, ApunteCaja, asiento; fallidas → recibos FALLIDOS, OrdenCobro Fallida | ✗ falta (la lógica de cobradas se gestionaba con `TesoreriaService.liquidar_remesa` pero hay que rehacerlo para que también marque recibos) |
| Pantalla 5.1 (Liquidar banco) | ✗ falta |
| Botón "Generar remesa de reenvío" en 5.2 | ✗ falta |
| Transacciones `ECO_REMESA_LIQUIDAR`, `ECO_REMESA_REENVIAR`, `ECO_ORDEN_ANULAR` en la matriz | ✗ falta |
| `OrigenApunte.REMESA` y regla contable `REMESA/INGRESO` | ✓ |

---

## 9. Implementación propuesta (después de tu visto bueno)

**Lote A — Backend**

1. `app/modules/economico/services/sepa_parsers.py`:
   - `parse_pain002(xml_bytes) -> list[dict]` con `[{end_to_end_id, codigo, motivo, fecha}]`.
   - `parse_camt054(xml_bytes) -> dict` con `{fecha_liquidacion, importe_bruto, cargos: [{end_to_end_id, importe}]}`.
   - Emparejamiento por `end_to_end_id` = `OrdenCobro.id` o `OrdenCobro.referencia_mandato`.

2. `RemesaService.liquidar_remesa(remesa_id, fecha_liquidacion, cobradas: list[UUID], fallidas: list[dict])`:
   - Transaccional. Llama a `marcar_cobrado` en los recibos cobrados, `marcar_fallido` en los recibos fallidos, actualiza cuotas, marca `OrdenCobro.estado_id`, crea `ApunteCaja` por el bruto, dispara `RegistroContable`, calcula estado final de la remesa.

3. GraphQL mutations:
   - `previsualizar_liquidacion_remesa(remesa_id, archivo_b64, tipo) -> PreviewLiquidacion`
   - `liquidar_remesa(remesa_id, fecha, cobradas: [UUID!], fallidas: [FallidoInput!]) -> Remesa`

**Lote B — Frontend**

4. `Tesoreria.vue` → sección Remesas: clic en una remesa Enviada abre el detalle con la pantalla 5.1.
5. Componente `<LiquidacionRemesaForm>` con upload de fichero + previsualización + confirmación.
6. Botón "Generar remesa de reenvío" en pantalla 5.2.

**Lote C — Permisos**

7. Alta de las 3 transacciones en la matriz; asignar a roles.

---

## 10. Decisiones tomadas (mayo 2026)

### D1. EndToEndId SEPA = referencia legible

Formato: **`{referencia_remesa}-{nseq:03d}`**, ejemplo `REM-2025-005-042`.

- Máximo 35 caracteres (límite SEPA `End-to-End Identification`).
- Legible para el tesorero al revisar extractos y para el socio cuando lo vea en su movimiento bancario.
- Implementación: añadir columna `OrdenCobro.nseq INTEGER NOT NULL` (correlativo dentro de la remesa, asignado al generar el lote). El XML SEPA usa `f"{remesa.referencia}-{orden.nseq:03d}"`. El parser de pain.002/camt.054 recupera la `OrdenCobro` por descomposición de la cadena.

### D2. Órdenes con código no re-presentable → acción manual

Cuando el banco devuelve `MD01`, `MS02`, `AC13`, etc., el sistema **no** anula automáticamente la orden ni la cuota. La orden queda en estado `Fallida` con el código registrado y el tesorero decide caso por caso: contactar al socio, anular cuota, regenerar mandato, etc.

Esto evita que un fallido SEPA "simple" (por ejemplo `MS02` que el deudor revierte por error) deje la cuota irrecuperable.

### D3. Aviso al socio = gestión manual con asistente de comunicación

No hay correo automático en la liquidación. **Tras la liquidación**, el tesorero accede a una pantalla nueva (5.4) de "Comunicación a socios con recibo fallido":

- Lista filtrable de recibos `FALLIDO` (por código SEPA, ejercicio, agrupación, fecha de rechazo).
- Multiselección sobre la lista.
- Selector de **plantilla de email** procedente del módulo de Comunicación Interna (tabla `plantillas_email`).
- Botón "Enviar" → encola un email por socio seleccionado con variables sustituidas (nombre del socio, importe, código de rechazo, instrucciones de regularización).

Esto delega la comunicación al módulo existente (`comunicacion_interna`), reutiliza sus plantillas y su sistema de envío. Implicación: el módulo económico **no** define sus propias plantillas — usa las del catálogo de Comunicación Interna, etiquetadas con tipo `RECIBO_FALLIDO` o equivalente.

---

## 11. Pantalla adicional 5.4 — Comunicación a socios fallidos

Ubicación: módulo Tesorería → submenú "Comunicación a fallidos" (o accesible desde el detalle de una remesa procesada).

```
┌─ Comunicar fallidos ─────────────────────────────────────────────────┐
│                                                                      │
│ Filtros:  Ejercicio [2025 ▼]   Agrupación [Todas ▼]                  │
│           Código SEPA [Todos ▼]   Solo sin notificar [✓]             │
│                                                                      │
│ ┌────────────────────────────────────────────────────────────────┐   │
│ │ ☐ Sel. │ Socio          │ Recibo         │ Código │ Importe   │   │
│ ├────────┼────────────────┼────────────────┼────────┼───────────┤   │
│ │ ☑      │ García López   │ REC-2025-00042 │ AM04   │  50,00 €  │   │
│ │ ☑      │ Pérez Martín   │ REC-2025-00058 │ MD01   │  50,00 €  │   │
│ │ ☐      │ Ruiz Sanz      │ REC-2025-00103 │ AC04   │  50,00 €  │   │
│ │ …                                                                  │
│ └────────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ Plantilla de email: [ "Recibo devuelto - aviso al socio" ▼ ]          │
│                                                                      │
│ Variables que se sustituirán:                                        │
│   {nombre_socio}    {numero_recibo}    {importe}                     │
│   {codigo_sepa}     {motivo}           {fecha_devolucion}            │
│                                                                      │
│ [Previsualizar email]  [Enviar a 2 socios seleccionados]             │
└──────────────────────────────────────────────────────────────────────┘
```

Tras enviar:
- Cada `Recibo` queda marcado con un nuevo campo `fecha_aviso_fallido` (o similar) para que el filtro "Solo sin notificar" funcione.
- Se registra una entrada en `notificaciones_enviadas` (módulo Comunicación Interna).

**Permisos asociados**:
- `ECO_RECIBO_COMUNICAR_FALLIDO` para acceder y enviar.

---

## 12. Implicaciones para los demás flujos / módulos

### Módulo Comunicación Interna

Tabla existente `plantillas_email` con columnas:
- `codigo` (str único, e.g. `RECIBO_FALLIDO_AVISO`)
- `nombre` (str legible)
- `modulo` (str, filtraremos por `'economico'` o `'tesoreria'`)
- `asunto` (str)
- `cuerpo_html` (text)
- `variables_disponibles` (JSON con la lista de placeholders aceptados)
- `activo`, `eliminado` (control de vida)

Acciones a hacer en este módulo (fuera del flujo 4, **no codear aquí**):
- Crear una o varias plantillas seed con `modulo='economico'`, e.g.:
  - `RECIBO_FALLIDO_AM04` — Aviso fondos insuficientes (re-presentable).
  - `RECIBO_FALLIDO_GENERICO` — Aviso genérico de devolución.
- Las plantillas declaran sus `variables_disponibles` como JSON:
  ```json
  ["nombre_socio", "numero_recibo", "importe", "codigo_sepa", "motivo", "fecha_devolucion", "iban_socio"]
  ```

### Cambios de schema (SQL pendiente)

Acumular en `SQL_PENDIENTE.md` y aplicar antes de codear el flujo:

```sql
-- Flujo 4: end_to_end_id legible y trazabilidad de aviso al socio
ALTER TABLE ordenes_cobro
  ADD COLUMN IF NOT EXISTS nseq INTEGER NOT NULL DEFAULT 0;
-- Backfill: asignar correlativo por remesa
WITH numeradas AS (
  SELECT id, ROW_NUMBER() OVER (PARTITION BY remesa_id ORDER BY creado_en, id) AS rn
  FROM ordenes_cobro
)
UPDATE ordenes_cobro o SET nseq = n.rn FROM numeradas n WHERE n.id = o.id AND o.nseq = 0;

ALTER TABLE recibos
  ADD COLUMN IF NOT EXISTS fecha_aviso_fallido DATE,
  ADD COLUMN IF NOT EXISTS plantilla_email_aviso_id UUID
    REFERENCES plantillas_email(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_recibos_fecha_aviso_fallido ON recibos(fecha_aviso_fallido);
```

### Permisos nuevos

Añadir a la matriz de transacciones:
- `ECO_REMESA_LIQUIDAR` — A1, A2, A3 (procesar respuesta del banco).
- `ECO_REMESA_REENVIAR` — A4 (generar remesa de reenvío).
- `ECO_ORDEN_ANULAR` — A5 (anular orden no representable, opcional).
- `ECO_RECIBO_COMUNICAR_FALLIDO` — pantalla 5.4 (multi-envío a socios fallidos).
