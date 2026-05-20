# Flujo 3 — Generación y envío de remesa SEPA

## 1. Propósito

Crear un **lote de cobros SEPA** (`Remesa`) a partir de las cuotas pendientes del ejercicio, generar el **XML SEPA** (formato `pain.008.001.02`), descargarlo para subirlo al portal del banco, y registrar que el archivo fue enviado.

Este flujo **NO mueve dinero**: solo prepara el documento que se envía al banco. El movimiento real (cobros + fallidos) llega después en el [flujo 4](./04_liquidacion_remesa.md).

Sus salidas son:
- Una `Remesa` con `n` `OrdenCobro` (una por cuota incluida).
- Un fichero XML SEPA pain.008.
- Cada cuota incluida queda **comprometida** en una remesa (no se duplica en otra mientras esta no se anule).
- Los `Recibo` asociados a esas cuotas pueden estar ya emitidos (flujo 2) o emitirse en bloque ahora (decisión D3.1).

---

## 2. Entidades implicadas

### 2.1 `Remesa` (`remesas`) — ver detalle de campos en flujo 4

Para este flujo lo relevante:
- `tipo_remesa` ∈ {ORDINARIA, EXTRAORDINARIA, REENVIO}
- `seq_tipo` ∈ {FRST, RCUR, LAST, OOFF}
- `referencia` única (formato `SEPA_ISO20022CORE_YYYY-MM-DDTHH-MM-SS.xml`)
- `mensaje_id` (MsgId del XML SEPA)
- `fecha_cobro` (fecha en que el banco efectuará el cobro)
- `agrupacion_id` (tesorería delegada — opcional)

### 2.2 `OrdenCobro` (`ordenes_cobro`)

Una por cuota incluida en la remesa. Campos clave:
- `cuota_id` FK a la cuota cuyo cobro se intenta.
- `importe`, `referencia_mandato`, `iban` (snapshot del IBAN del socio en el momento de generar).
- `nseq` (correlativo dentro de la remesa, ver D4.1 — usado para construir el EndToEndId).

### 2.3 `CuotaAnual`

Selección:
- Cuotas con `estado = Pendiente` (no Cobradas, no Anuladas).
- Del `ejercicio` indicado.
- Opcionalmente filtradas por `agrupacion_id` (tesorería delegada).
- (Pre-generación) deben tener IBAN del socio asociado.

Tras generar la remesa, la cuota NO cambia de estado. Sigue `Pendiente` hasta el flujo 4.

### 2.4 `Miembro` / IBAN

El XML SEPA requiere por orden:
- `IBAN` del deudor.
- `Name` del deudor.
- Un `MandateIdentification` válido (`referencia_mandato`).

Si el socio no tiene IBAN → no se puede incluir en la remesa.

### 2.5 `Recibo` (entrelazado con flujo 2)

Dos modelos posibles según D3.1:
- **A**: emisión de recibos previa a la remesa (Recibo `EMITIDO` antes); la remesa enlaza la cuota → recibo vía `cuota_id`.
- **B**: emisión de recibos en el mismo acto de generación de remesa (un Recibo por cada OrdenCobro).

---

## 3. Estados y transiciones

### 3.1 Máquina de estados de `Remesa` (porción afectada por flujo 3)

```
            ┌────────────┐
            │  Borrador  │  ← generar_remesa() crea aquí
            └─────┬──────┘
                  │ generar_xml_sepa()
                  ▼
            ┌────────────┐
            │  Generada  │  ← XML creado y descargable
            └─────┬──────┘
                  │ marcar_enviada()
                  ▼
            ┌────────────┐
            │  Enviada   │  ← XML subido al banco, esperando respuesta
            └────────────┘
                  │
                  └──→ continúa en flujo 4 (liquidar_remesa)
```

Una `Remesa` `Borrador` que el tesorero descarta cambia a estado `Anulada` (FK) y las cuotas vuelven a estar disponibles para incluirse en otra remesa.

### 3.2 OrdenCobro

Permanece en `Pendiente` durante todo el flujo 3. Cambia en flujo 4.

### 3.3 CuotaAnual

Sin cambio durante flujo 3. Cuota permanece `Pendiente`.

---

## 4. Acciones

| # | Acción | Quién dispara | Pre-estado | Post-estado | Efecto colateral |
|---|---|---|---|---|---|
| A1 | **Previsualizar remesa** | Tesorero (UI) | — | — | Calcula nº cuotas, importe total, lista de socios sin IBAN (excluidos) |
| A2 | **Generar remesa ORDINARIA** | Tesorero (UI) | hay cuotas Pendientes | Remesa `Borrador`, n × OrdenCobro `Pendiente` | (si D3.1=B) emite Recibos `EMITIDO` |
| A3 | **Generar remesa EXTRAORDINARIA** | Tesorero (UI) | miembros seleccionados tienen IBAN | Remesa `Borrador` (tipo=EXTRAORDINARIA, seq=OOFF), OrdenCobro `Pendiente` | (si D3.1=B) emite Recibos `EMITIDO` |
| A4 | **Generar remesa de REENVÍO** | Tesorero (UI) | remesa origen con ≥1 OrdenCobro `Fallida` re-presentable | Remesa `Borrador` (tipo=REENVIO, seq=FRST, remesa_origen_id apunta a origen) | nuevas órdenes para las cuotas de los fallidos |
| A5 | **Generar XML SEPA** | Tesorero (UI) | Remesa `Borrador` | Remesa `Generada`, archivo descargable | Genera fichero `pain.008.001.02` |
| A6 | **Descargar XML** | Tesorero (UI) | Remesa `Generada` o `Enviada` | sin cambio | Devuelve el XML para subir al banco |
| A7 | **Marcar como enviada** | Tesorero (UI) | Remesa `Generada` | Remesa `Enviada` | Registra `fecha_envio` |
| A8 | **Anular remesa** | Tesorero (UI) | Remesa `Borrador` o `Generada` (NO Enviada) | Remesa `Anulada` | Las OrdenCobro asociadas se anulan; las cuotas vuelven a Pendientes |

**Restricción importante** (a clarificar en D3.4): una cuota no puede estar en dos remesas activas (no anuladas) a la vez. Si se intenta, A2/A3 debe excluirla y avisar al tesorero.

---

## 5. Pantallas UI

### 5.1 Lista de remesas (pantalla principal)

Columnas:
- Referencia
- Ejercicio (derivado del concepto o `fecha_cobro`)
- Tipo (Ordinaria / Extraordinaria / Reenvío) con badge color
- Fecha creación · Fecha cobro · Fecha envío
- Nº órdenes
- Importe total
- Estado (badge: Borrador, Generada, Enviada, Procesada, Parcial, Rechazada, Anulada)
- Acciones según estado

Filtros (FilterBar): ejercicio, tipo, estado, agrupación.

Botón principal: **+ Nueva remesa** (abre 5.2).

### 5.2 Asistente "Nueva remesa" (modal o vista dedicada)

**Paso 1 — Tipo**

```
Tipo de remesa:
  ◉ Ordinaria          — Cobro de cuotas pendientes del ejercicio
  ○ Extraordinaria     — Cargo único con concepto e importe libres (derrama, congresal…)
  ○ Reenvío de fallidos — Re-presenta órdenes fallidas de una remesa anterior
```

**Paso 2 — Parámetros** (según tipo)

ORDINARIA:
```
Ejercicio:        [2026 ▼]
Agrupación:       [Todas ▼] (tesorería delegada — solo aparece si el rol es central; un tesorero de agrupación ve la suya forzada)
Fecha de cobro:   [__/__/____]  (mínimo +14 días naturales si seq=FRST, +2 días si seq=RCUR)
Seq SEPA:         [RCUR ▼] (FRST si es la primera vez para muchos socios)
Concepto:         "Cuota ordinaria ejercicio 2026"  (editable)

Previsualización (al rellenar):
  - 412 cuotas pendientes
  - 408 con IBAN ✓ — se incluirán
  - 4 sin IBAN ⚠ — se excluyen (lista desplegable: ver socios)
  - Importe total: 24 480,00 €
```

EXTRAORDINARIA:
```
Ejercicio:           [2026 ▼]
Fecha de cobro:      [__/__/____]
Concepto:            [_________________________________]  (obligatorio, e.g. "Derrama techo solar 2026")
Importe por socio:   [___,__] €
Seq SEPA:            OOFF (fijo, cargos únicos)

Destinatarios:
  ◉ Todos los socios activos de la agrupación
  ○ Selección manual                    [Elegir socios…]

Previsualización:
  - 156 socios seleccionados
  - 152 con IBAN ✓
  - 4 sin IBAN ⚠
  - Importe total: 7 600,00 €
```

REENVÍO:
```
Remesa origen:    [REM-2025-005 — 18/05/2025 — 13 fallidos ▼]
                   (solo aparecen remesas con OrdenCobro Fallida no representada)
Fecha de cobro:   [__/__/____]
Seq SEPA:         FRST (fijo en reenvíos)

Códigos a incluir:
  ☑ AM04 — Fondos insuficientes (7)
  ☑ AC04 — Cuenta cerrada (3)
  ☐ MD01 — Sin mandato (no representable)
  ☐ MS02 — Rechazo del deudor (requiere acción manual)

Previsualización:
  - 10 órdenes a reenviar
  - 10 con IBAN actualizado ✓
  - Importe total: 500,00 €
```

**Paso 3 — Confirmar**

Resumen de lo seleccionado + botón "Generar remesa" → A2/A3/A4. Resultado: Remesa `Borrador`.

### 5.3 Detalle de remesa (Borrador / Generada)

Cabecera con datos de la remesa + lista de órdenes (orden | socio | IBAN | importe | mandato).

Acciones según estado:
- `Borrador` → **Generar XML SEPA** (A5) · **Anular remesa** (A8)
- `Generada` → **Descargar XML** (A6) · **Marcar como enviada** (A7) · **Anular remesa** (A8)
- `Enviada` → enlaza a flujo 4 (Liquidar) y deja descargar XML (A6)

### 5.4 (Solo central) Resumen de tesorerías delegadas

Pantalla agregada que muestra, por agrupación, sus remesas pendientes / enviadas / procesadas. Útil para auditoría central. Pendiente diseño detallado en un flujo posterior.

---

## 6. Permisos / roles

| Transacción | Acciones que habilita |
|---|---|
| `ECO_REMESA_CREAR` | A1, A2, A3, A4 — crear remesas |
| `ECO_REMESA_GENERAR_XML` | A5, A6 — generar y descargar XML |
| `ECO_REMESA_MARCAR_ENVIADA` | A7 — marcar como enviada |
| `ECO_REMESA_ANULAR` | A8 — anular remesa antes de enviarla |

Asignación inicial:
- `TESORERO_CENTRAL`: todas.
- `TESORERO_AGRUPACION`: todas pero filtradas por su `agrupacion_id` (forzado, no editable).
- `AUDITOR`: ninguna (solo lectura).

---

## 7. Norma legal aplicable

- **EPC131-08 SEPA Core Direct Debit Rulebook** — define el formato `pain.008.001.02`, el `MandateIdentification`, el `EndToEndIdentification`, los plazos (`FRST` mínimo 14 días naturales antes del cobro, `RCUR` 2 días).
- **Reglamento (UE) 260/2012** — establece los requisitos técnicos para los adeudos SEPA.
- **PCESFL 2013 norma 1ª** — al emitirse el cobro, ya hay un derecho sobre el socio (cta `430 Deudores`) que debe reflejarse contablemente cuando se reconozca el ingreso. La remesa por sí sola no genera asiento — el asiento se genera al cobrar en flujo 4.
- **LO 8/2007 art. 14** (partidos políticos): la generación de remesas y su trazabilidad debe quedar en el sistema; sirve para auditoría del Tribunal de Cuentas.

---

## 8. Estado de implementación actual

| Pieza | Estado |
|---|---|
| Modelos `Remesa`, `OrdenCobro` con todos los campos SEPA | ✓ |
| `RemesaService.generar_remesa(ejercicio, fecha_cobro, agrupacion_id, tipo_remesa, concepto, seq_tipo)` | ✓ |
| `RemesaService.generar_remesa_extraordinaria(...)` | ✓ |
| `RemesaService.generar_remesa_fallidos(remesa_origen_id)` | ✓ |
| `RemesaService.generar_xml_sepa(remesa_id, creditor_*)` → bytes | ✓ |
| `RemesaService.marcar_enviada(remesa_id, archivo?)` | ✓ |
| Mutations GraphQL para A2/A3/A4/A5/A7 | parcial — falta exponer todas con permisos |
| Vista `Remesas.vue` con form básico y lista | ✓ pero limitada |
| Selector tipo (Ordinaria/Extraordinaria/Reenvío) en UI | ✗ falta |
| Asistente 3 pasos (5.2) | ✗ falta |
| Detalle de remesa (5.3) | ✗ falta |
| Anular remesa (A8) | ✗ falta backend + UI |
| `OrdenCobro.nseq` para EndToEndId legible (D4.1) | ✗ falta — requiere ALTER + backfill |
| Validación "una cuota en una remesa activa" (D3.4) | ✗ falta |
| Permisos `ECO_REMESA_*` en la matriz | ✗ falta |

---

## 9. Plan de implementación (después de las decisiones)

**Lote A — Backend**

1. ALTER `OrdenCobro.nseq` + backfill (acumular en `SQL_PENDIENTE.md`).
2. Modificar `generar_remesa` y `generar_remesa_extraordinaria` para:
   - Asignar `nseq` correlativo.
   - Excluir cuotas sin IBAN (devolver lista de excluidos en una previsualización).
   - Validar que las cuotas no estén ya en otra remesa activa.
3. Nuevo método `previsualizar_remesa(...)` que devuelve sin persistir: nº órdenes, total, lista excluidos.
4. Nuevo método `anular_remesa(remesa_id)` con desbloqueo de cuotas.
5. Validación de `fecha_cobro` ≥ hoy + N días según `seq_tipo`.

**Lote B — GraphQL**

6. Mutations con permisos: `previsualizarRemesa`, `crearRemesaOrdinaria`, `crearRemesaExtraordinaria`, `crearRemesaReenvio`, `generarXmlSepa`, `marcarRemesaEnviada`, `anularRemesa`.

**Lote C — Frontend**

7. `Remesas.vue` rediseñado:
   - Listado con FilterBar (ejercicio, tipo, estado, agrupación).
   - Botón **+ Nueva remesa** → modal con asistente 5.2.
   - Click en una remesa → detalle (vista dedicada) con acciones según estado.
8. Retirar el panel de contadores superior (recurrente en módulo, [pendientes_extemporaneos.md](./pendientes_extemporaneos.md)).

**Lote D — Permisos y seed**

9. Alta de `ECO_REMESA_*` en la matriz.
10. Seed: crear plantilla de email para aviso de remesa generada al tesorero (opcional).

---

## 10. Decisiones tomadas (mayo 2026)

Resumen breve; detalle en [decisiones.md](./decisiones.md).

- **D3.1** — Emisión híbrida: SEPA emite recibos en bloque al generar remesa; manual emite explícitamente desde Recibos.
- **D3.2** — Una sola remesa ORDINARIA por ejercicio; EXTRAORDINARIAS y REENVÍOS no cuentan.
- **D3.3** — Cuotas sin IBAN se excluyen y se muestra la lista al tesorero antes de generar.
- **D3.4** — Una cuota no puede estar en dos remesas activas; las fallidas vuelven a estar disponibles.
- **D3.5** — Datos del acreedor SEPA en `ParametrosGenerales`, sección dedicada "SEPA". Un único acreedor.
