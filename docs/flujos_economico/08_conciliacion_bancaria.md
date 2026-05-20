# Flujo 8 — Conciliación bancaria

## 1. Propósito

Verificar mensualmente que el **saldo de cada cuenta bancaria** en SIGA coincide con el saldo real que tiene el banco. Cada `ApunteCaja` del sistema debe corresponder con una línea del extracto bancario (y viceversa). Cualquier descuadre se detecta y resuelve en este flujo.

Sin conciliación periódica, el balance contable pierde la imagen fiel; con ella, el ejercicio puede cerrarse con seguridad (D8.4).

---

## 2. Entidades implicadas

| Entidad | Rol |
|---|---|
| `CuentaBancaria` | La cuenta operativa cuyo extracto se concilia |
| `ApunteCaja` | Movimiento registrado en SIGA — debe casarse con una línea del extracto |
| `ExtractoBancario` | Cada línea individual del extracto descargado del banco |
| `Conciliacion` (1:1) | Vincula un `ApunteCaja` con un `ExtractoBancario` |
| `ConciliacionBancaria` (período) | Documento de cierre mensual: saldo inicial/final, totales debe/haber, fecha cierre |

Estados de `ApunteCaja.conciliado` y `ExtractoBancario.conciliado`: `false` por defecto; `true` al emparejarse. La fecha del emparejamiento queda en `fecha_conciliacion`.

---

## 3. Estados y transiciones

```
   (CuentaBancaria con movimientos)
              │
              │ A1 importar_extracto (CSV o Norma 43)
              ▼
   ExtractoBancario.conciliado=false      ApunteCaja.conciliado=false
              │                                       │
              └─────────────┬─────────────────────────┘
                            │ A2 conciliar_apunte_con_extracto
                            ▼
              ambos.conciliado=true; Conciliacion creada
                            │
                            │ A3 crear_conciliacion_periodo(mes)
                            ▼
              ConciliacionBancaria período = ABIERTA
                            │
                            │ A4 confirmar_conciliacion_periodo
                            ▼
              ConciliacionBancaria período = CERRADA (firmada)
```

---

## 4. Acciones

| # | Acción | Quién | Pre-estado | Post-estado | Efecto |
|---|---|---|---|---|---|
| A1 | **Importar extracto** (CSV o Norma 43) | Tesorero | — | N × `ExtractoBancario` sin conciliar | El extracto se sube como CSV o Q43; el sistema lo parsea |
| A2 | **Conciliar apunte con extracto** | Tesorero | apunte y extracto sin conciliar | ambos `conciliado=true`; `Conciliacion` creada | Manual (D8.2); valida que importes coinciden |
| A3 | **Crear conciliación de período** | Tesorero | hay un mes con apuntes y extracto importado | `ConciliacionBancaria` ABIERTA | Calcula saldo sistema vs saldo extracto |
| A4 | **Confirmar conciliación de período** | Tesorero | saldos cuadran | período CERRADO (firmado) | No se pueden añadir/borrar apuntes en ese período sin reabrir |
| A5 | **Romper emparejamiento** | Tesorero | apunte y extracto conciliados | ambos `conciliado=false`; `Conciliacion` eliminada | Solo si el período no está CERRADO |

---

## 5. Pantallas UI

### 5.1 Conciliación de la cuenta — `Conciliacion.vue` (NUEVA)

Ruta: `/economico/conciliacion`.

```
┌─ Cuenta: [ Cuenta principal — ES12… ▼ ]   Mes: [ 2026-05 ▼ ]              [ Importar extracto ] ┐
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ APUNTES DEL SISTEMA (8 pendientes)         │  LÍNEAS DEL EXTRACTO (12 pendientes)        │
│ ─────────────────────────────────────────┼────────────────────────────────────────────  │
│ ☐ 03/05 -125,00 Recibo REC-…             │  03/05 -125,00 ALQUILER PROY                │
│ ☐ 05/05  +50,00 Cuota García López       │  05/05  +50,00 SEPA García L                │
│ ☐ …                                      │  04/05    -3,50 COMISIÓN MTO                │
│                                          │  …                                            │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ Saldo sistema mes: 24 480,00 €   Saldo extracto: 24 480,00 €   Diferencia: 0,00 € ✓     │
│                                                              [ Confirmar conciliación ] │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

Selector de cuenta + selector de mes. Dos columnas: apuntes del sistema pendientes vs líneas del extracto pendientes (filtradas por la cuenta y el mes). El tesorero selecciona un apunte y una línea y pulsa "Emparejar" (o doble-clic). El sistema valida que los importes coinciden y los marca como conciliados.

Footer: subtotales y diferencia. Si la diferencia es 0, se habilita el botón "Confirmar conciliación" del período.

### 5.2 Histórico de conciliaciones de período

Ruta: `/economico/conciliacion-historico` (o sub-vista).

Lista de `ConciliacionBancaria` confirmadas, agrupadas por cuenta y por mes. Cada entrada muestra el saldo final, la fecha de cierre y el usuario que firmó.

---

## 6. Permisos / roles

| Código | Acción |
|---|---|
| `CON_IMPORTAR_EXTRACTO` | A1 — Importar CSV o Q43 |
| `CON_CONCILIAR_APUNTE` | A2, A5 — Emparejar/desemparejar |
| `CON_CONFIRMAR_PERIODO` | A3, A4 — Cerrar/firmar conciliación mensual |
| `CON_LIST` | Ver listado e histórico |

Asignación inicial: todos al rol `TESORERO`. `AUDITOR` con `CON_LIST` de solo lectura.

---

## 7. Norma legal aplicable

- **PCESFL 2013, norma 9ª de elaboración** (imagen fiel): la cuenta `572 Bancos` debe reflejar exactamente lo que diga el extracto bancario. Sin conciliación periódica es imposible garantizarlo.
- **Ley General Tributaria art. 29**: los registros contables deben coincidir con la realidad documental. La conciliación bancaria es la prueba.
- **Auditoría externa** (cuando aplique): la conciliación bancaria es el **primer documento que se pide**; sin ella no se acepta el cierre.

---

## 8. Estado de implementación actual

| Pieza | Estado |
|---|---|
| Modelos `ExtractoBancario`, `Conciliacion`, `ConciliacionBancaria` | ✓ |
| `TesoreriaService.importar_extracto(cuenta_id, lineas)` | ✓ (recibe lista parseada) |
| `TesoreriaService.listar_extractos` | ✓ |
| `TesoreriaService.apuntes_pendientes_conciliacion` | ✓ |
| `TesoreriaService.conciliar_apunte_con_extracto` | ✓ |
| `TesoreriaService.crear_conciliacion_periodo` | ✓ |
| `TesoreriaService.confirmar_conciliacion_periodo` | ✓ |
| `TesoreriaService.listar_conciliaciones_periodo` | ✓ |
| Mutations GraphQL: `marcar_apunte_conciliado`, `conciliar_apunte_con_extracto`, `confirmar_conciliacion_periodo` | ✓ sin guards |
| **Parser CSV en frontend** | ✗ falta |
| **Parser Norma 43 en backend** (D8.1) | ✗ falta |
| **Mutation `importar_extracto_csv`/`importar_extracto_norma43`** | ✗ falta (existe `importar_extracto` que recibe lista) |
| **Mutation `romper_conciliacion(conciliacion_id)`** | ✗ falta |
| **Vista `Conciliacion.vue`** con UI lado-a-lado | ✗ falta |
| **4 permisos `CON_*`** en `transacciones.json` + matriz | ✗ falta |
| **Validación bloqueante en cierre** (D8.4) | ✗ falta (gancho en `CierreEjercicioService.generar_asiento_cierre`) |
| **Sección de ayuda** | ✗ falta |

---

## 9. Plan de implementación

**Lote A — Permisos**

1. Añadir 4 transacciones a `transacciones.json`: `CON_IMPORTAR_EXTRACTO`, `CON_CONCILIAR_APUNTE`, `CON_CONFIRMAR_PERIODO`, `CON_LIST`.
2. Bootstrap + seed `seed_permisos_conciliacion.py` (asigna a TESORERO).
3. Decorar mutations existentes con guards.

**Lote B — Importadores**

4. Parser Norma 43 en backend (`tesoreria_service.parse_norma43(archivo_bytes) -> list[dict]`). Las líneas resultantes alimentan `importar_extracto`.
5. Mutation `importar_extracto_norma43(cuenta_id, archivo_b64) -> int` (devuelve nº líneas importadas).
6. Mutation `importar_extracto_csv(cuenta_id, lineas: [LineaExtractoInput!]!)` para el cliente que parsea CSV.

**Lote C — Servicio nuevo**

7. `TesoreriaService.romper_conciliacion(conciliacion_id)`: deshace el emparejamiento si el período no está CERRADO.
8. Mutation `romper_conciliacion` con guard `CON_CONCILIAR_APUNTE`.

**Lote D — Cierre bloqueante (D8.4)**

9. En `CierreEjercicioService.generar_asiento_cierre(ejercicio)`, antes de generar el asiento, buscar `ApunteCaja.conciliado = false` con `fecha en ese ejercicio`; si hay alguno, lanzar `ValueError` con el listado.

**Lote E — Frontend**

10. Vista `Conciliacion.vue` con selector cuenta+mes, paneles dobles, drag/doble-click, totales, importación, cierre de período.
11. Ruta `/economico/conciliacion` con guard `CON_LIST`.

**Lote F — Ayuda**

12. Acordeón "Flujo · Conciliación bancaria" en `Ayuda.vue`.

---

## 10. Decisiones tomadas (referencia rápida)

- **D8.1** — Soportar CSV genérico + Norma 43 AEB.
- **D8.2** — Emparejamiento siempre manual; sin auto-matching.
- **D8.3** — Cadencia mensual de conciliación de período.
- **D8.4** — Cierre de ejercicio bloqueado si hay apuntes sin conciliar.

---

## 11. Mejora futura: integración con Enable Banking (PSD2)

Como funcionalidad **opcional** y futura, se desarrollará una integración con [Enable Banking](https://enablebanking.com) (servicio PSD2 / open banking) que automatice la descarga del extracto bancario. En vez de exportar manualmente el CSV/Norma 43 del portal del banco y subirlo a SIGA, el sistema obtendrá los movimientos vía API tras una autorización OAuth de 90 días renovable.

Implicaciones:
- Sigue conviviendo con el flujo manual de D8.1 como fallback.
- Activable por organización en Parámetros Generales (sección "Conciliación automática").
- Mutation `sincronizar_extracto_enable_banking(cuenta_id)` que poblará `ExtractoBancario` igual que el importador manual.
- El emparejamiento sigue siendo manual (D8.2) — Enable Banking solo automatiza el *input*, no la conciliación.

Apuntado como pendiente en `pendientes_extemporaneos.md`.
