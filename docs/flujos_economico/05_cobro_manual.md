# Flujo 5 — Cobro manual de cuotas

## 1. Propósito

Registrar el cobro de una cuota cuando el dinero llega **fuera del circuito SEPA**: transferencia bancaria, ingreso en efectivo, pago con tarjeta o cualquier otro modo no automático. Cierra el ciclo Cuota → Recibo → Cobro para los modos que no pasan por remesa (los SEPA se cierran con el flujo 4 Liquidación).

Por D5.1, la **puerta única** de cobro manual es el propio recibo: marcar cobrado un recibo desencadena la cadena completa (estado del recibo + estado de la cuota + apunte de caja + asiento contable).

---

## 2. Entidades implicadas

| Entidad | Rol en el flujo |
|---|---|
| `Recibo` | Entrada del cobro. Pasa de `EMITIDO` (o `FALLIDO` recuperado manualmente) a `COBRADO`. |
| `CuotaAnual` | Su `importe_pagado` se incrementa; estado pasa a `Cobrada` si el total queda cubierto. |
| `CuentaBancaria` | Destino del ingreso. Se elige al marcar cobrado. |
| `ApunteCaja` | Movimiento de tesorería tipo `INGRESO`, origen `CUOTA`, vinculado a la cuenta bancaria. |
| `AsientoContable` | Generado automáticamente vía `RegistroContable` (regla CUOTA/INGRESO → Debe `572` / Haber `721`). |

---

## 3. Estados y transiciones

```
   Recibo EMITIDO          Cuota Pendiente              (sin apunte aún)
        │                       │
        │ marcar_cobrado        │
        │ (cuenta, modo, fecha)
        ▼                       ▼                              ▼
   Recibo COBRADO          Cuota Cobrada              ApunteCaja INGRESO
                           (si pagado=importe)        + AsientoContable
                                                       (Debe 572 / Haber 721)
```

Si el cobro es parcial (`importe_pagado < importe`), la cuota se mantiene en `Pendiente` y el recibo, en `EMITIDO`. El segundo cobro vuelve a aplicar la cadena con el resto.

---

## 4. Acciones

| # | Acción | Quién dispara | Pre-estado | Post-estado | Efecto |
|---|---|---|---|---|---|
| A1 | **Marcar recibo como cobrado manualmente** | Tesorero (UI desde detalle del recibo) | Recibo `EMITIDO` o `FALLIDO` (no `COBRADO` ni `ANULADO`) | Recibo `COBRADO`, cuota actualizada, `ApunteCaja` creado, asiento confirmado | Pide cuenta bancaria, modo, fecha, referencia opcional |
| A2 | **Emitir + cobrar en un acto** (caso excepcional) | Tesorero (UI) | — | Recibo individual extraordinario emitido y cobrado en la misma transacción | Combina A2 del flujo 2 con A1 de este flujo; para cobros sin cuota previa |

---

## 5. Pantallas UI

No hay pantalla nueva. El flujo se ejecuta enteramente desde el **modal de detalle de recibo** de `Recibos.vue` (flujo 2 — pantalla 5.3).

El modal "Marcar cobrado" añade los campos requeridos:

```
┌─ Marcar como cobrado ───────────────────────────────────┐
│ Cuenta bancaria *  [ Cuenta principal — ES01… ▼ ]       │
│ Modo cobro *       [ Transferencia ▼ ]                  │
│ Fecha cobro *      [ __/__/____ ]                       │
│ Referencia         [ "TRANSFERENCIA INTERNA #1234" ]    │
│ Observaciones      [                              ]     │
│                                                         │
│ [Cancelar]                       [Confirmar cobro]      │
└─────────────────────────────────────────────────────────┘
```

Al confirmar:
- El recibo pasa a `COBRADO` (o `EMITIDO` si fue parcial).
- La cuota se actualiza.
- Se crea el `ApunteCaja` y se genera el asiento.
- Se cierra el modal y se recarga el listado.

---

## 6. Permisos / roles

- `RCB_MARCAR_COBRADO` (ya existe, flujo 2): habilita la acción A1. Asignada a `TESORERO`.
- `RCB_EMIT_LOTE` (ya existe, flujo 2): habilita la emisión previa para A2.

No se crean transacciones nuevas. El flujo 5 no añade permisos.

---

## 7. Norma legal aplicable

- **Código de Comercio art. 25.1**: cada cobro queda reflejado en el Libro Diario el día en que se produce. La fecha que se indica al marcar cobrado debe ser la fecha real del ingreso bancario, no la del registro en el sistema.
- **PCESFL 2013, norma 1ª** (imagen fiel): el saldo de `430 Usuarios deudores` baja exactamente con el importe cobrado y el de `572 Bancos` sube en el mismo importe.
- **Ley 49/2002 art. 24** (régimen fiscal del mecenazgo): para que un cobro pueda ser deducible (donación), la entidad debe poder demostrar fecha exacta del ingreso; este flujo deja constancia con `fecha_cobro`.

---

## 8. Estado de implementación actual

| Pieza | Estado |
|---|---|
| `Recibo.modo_cobro` admite TRANSFERENCIA, EFECTIVO, TARJETA, MANUAL | ✓ |
| `TesoreriaService.registrar_pago_cuota_manual` (cuota + apunte + asiento) | ✓ |
| `ReciboService.marcar_cobrado` (solo cambia estado del recibo, sin apunte ni asiento) | ⚠ necesita reescritura para orquestar todo |
| Mutation `marcar_recibo_cobrado` con guard `RCB_MARCAR_COBRADO` | ✓ |
| Modal "Marcar cobrado" en `Recibos.vue` con modo + fecha | ✓ |
| **Selector de `cuenta_bancaria_id` en el modal "Marcar cobrado"** | ✗ falta |
| **Cadena recibo + cuota + apunte + asiento en una transacción** | ✗ falta (D5.1) |
| Mutation `registrar_pago_cuota_manual` directa (deprecada por D5.1) | ⚠ conservar pero no usar |

---

## 9. Plan de implementación

**Lote A — Backend**

1. Reescribir `ReciboService.marcar_cobrado(recibo_id, cuenta_bancaria_id, modo_cobro, fecha_cobro, importe_cobrado=None, referencia=None, observaciones=None)`:
   - Cambia estado del recibo y rellena `fecha_cobro`.
   - Si tiene `cuota_id`, llama internamente a `TesoreriaService.registrar_pago_cuota_manual` para actualizar la cuota + crear ApunteCaja + generar asiento.
   - Una sola transacción.
2. Ampliar la mutation `marcar_recibo_cobrado` con el parámetro `cuenta_bancaria_id: UUID!`.
3. Marcar `registrar_pago_cuota_manual` en `financiero_mutations.py` como deprecada (comentario; no eliminar para no romper compatibilidad).

**Lote B — Frontend**

4. Modal "Marcar cobrado" de `Recibos.vue`:
   - Cargar lista de `CuentaBancaria` activas al abrir.
   - Añadir selector `cuenta_bancaria_id` como obligatorio.
   - Añadir campo opcional `referencia` (núm. transferencia, ticket).
   - Validar antes de invocar la mutation.

**Lote C — Ayuda**

5. Acordeón "Flujo · Cobro manual de cuotas" en `Ayuda.vue` con los pasos.

---

## 10. Decisiones tomadas (referencia rápida)

- **D5.1** — Punto único de entrada: marcar cobrado el recibo. La acción dispara la cadena completa (recibo + cuota + apunte + asiento). Sin entradas laterales.

---

## 11. Implicaciones para otros flujos

- **Flujo 2 (Emisión)**: el flujo 5 amplía la acción A3 del flujo 2 (marcar cobrado manualmente). El modal "Marcar cobrado" pasa a pedir cuenta bancaria.
- **Flujo 6 (Donaciones)**: las donaciones puntuales NO entran por aquí. Tienen su propio modelo `Donacion` y su flujo dedicado.
- **Módulo Tesorería**: la pantalla de Tesorería puede listar los `ApunteCaja` generados pero NO ofrece "Registrar cobro" directo — eso se hace siempre desde Recibos.
