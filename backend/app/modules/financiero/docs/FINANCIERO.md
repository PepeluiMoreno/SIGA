# Módulo Financiero — SIGA

> Documento de diseño arquitectural. Fuente de verdad para el desarrollo del dominio `financiero`.

---

## 1. Visión general

El módulo financiero de SIGA es un **dominio plugable** activado mediante feature flags. Soporta dos versiones:

| Versión | Para | Contabilidad |
|---|---|---|
| `SIMPLE` | Asociaciones | Apuntes de caja (ingresos/gastos) |
| `COMPLETA` | Fundaciones | Partida doble + Plan de cuentas PGC |

Ambas versiones comparten los subdominios de cuotas, donaciones, remesas, cobro, reclamaciones, presupuesto y tesorería. La versión `COMPLETA` añade el subdominio de **contabilidad**.

---

## 2. Estructura de carpetas

```
backend/app/domains/financiero/
│
├── FINANCIERO.md
│
├── core/
│   └── feature_flags.py
│
├── models/
│   ├── cuotas/
│   │   ├── __init__.py
│   │   ├── importe_cuota.py        # ImporteCuotaAnio, ModoIngreso
│   │   └── cuota_anual.py          # CuotaAnual
│   │
│   ├── donaciones/
│   │   ├── __init__.py
│   │   ├── concepto.py             # DonacionConcepto
│   │   └── donacion.py             # Donacion
│   │
│   ├── remesas/
│   │   ├── __init__.py
│   │   ├── remesa.py               # Remesa
│   │   └── orden_cobro.py          # OrdenCobro
│   │
│   ├── cobro/
│   │   ├── __init__.py
│   │   ├── proveedor.py            # ProveedorPago
│   │   ├── pago.py                 # Pago
│   │   └── suscripcion.py          # Suscripcion
│   │
│   ├── reclamaciones/
│   │   ├── __init__.py
│   │   ├── reclamacion.py          # Reclamacion
│   │   └── accion_reclamacion.py   # AccionReclamacion
│   │
│   ├── presupuesto/
│   │   ├── __init__.py
│   │   ├── planificacion.py        # PlanificacionAnual, EstadoPlanificacion
│   │   ├── partida.py              # PartidaPresupuestaria
│   │   └── categoria_partida.py    # CategoriaPartida
│   │
│   ├── tesoreria/
│   │   ├── __init__.py
│   │   ├── cuenta_bancaria.py      # CuentaBancaria
│   │   ├── apunte.py               # ApunteCaja
│   │   └── conciliacion.py         # ExtractoBancario, Conciliacion
│   │
│   └── contabilidad/               # solo versión COMPLETA
│       ├── __init__.py
│       ├── plan_cuentas.py         # CuentaContable (árbol PGC)
│       └── asiento.py              # Asiento, LineaAsiento
│
└── services/
    ├── __init__.py
    ├── base_service.py
    ├── cuotas_service.py
    ├── donaciones_service.py
    ├── remesas_service.py
    ├── cobro_service.py
    ├── reclamaciones_service.py
    ├── presupuesto_service.py
    ├── tesoreria_service.py
    └── contabilidad_service.py     # solo versión COMPLETA
```

---

## 3. Subdominios

### 3.1 Cuotas

**Responsabilidad:** modelar la obligación de pago periódica de un socio.

- `ImporteCuotaAnio` — tarifa oficial por tipo de miembro y ejercicio fiscal.
- `CuotaAnual` — obligación concreta de un socio para un ejercicio.

**Regla clave:** `CuotaAnual` es la deuda, no el pago. El ingreso real se registra en `ApunteCaja` con `origen_tipo=CUOTA`.

---

### 3.2 Donaciones

**Responsabilidad:** registrar aportaciones voluntarias de miembros o externos.

- `DonacionConcepto` — catálogo de conceptos.
- `Donacion` — la donación. Puede ser anónima o nominativa. Si tiene NIF, es deducible. En versión `COMPLETA` genera certificado IRPF.

**Regla clave:** genera un `ApunteCaja` con `origen_tipo=DONACION` al confirmarse su recepción.

---

### 3.3 Remesas

**Responsabilidad:** cobros bancarios SEPA en lote.

- `Remesa` — lote de órdenes. Genera el XML SEPA.
- `OrdenCobro` — cobro individual dentro de la remesa, vinculado a `CuotaAnual`.

**Regla clave:** cuando una `OrdenCobro` pasa a `PROCESADA`, se genera automáticamente el `ApunteCaja` en tesorería.

---

### 3.4 Cobro

**Responsabilidad:** integración con pasarelas de pago externas (PayPal, Bizum, Stripe...).

- `ProveedorPago` — catálogo de pasarelas.
- `Pago` — transacción registrada en la pasarela (ID externo, webhook, estado).
- `Suscripcion` — pago recurrente activo en una pasarela.

**Regla clave:** adaptador de entrada de dinero digital. Cuando un `Pago` pasa a `COMPLETADO`, genera un `ApunteCaja`. No gestiona lógica de negocio de cuotas o donaciones.

---

### 3.5 Reclamaciones

**Responsabilidad:** gestionar el proceso de reclamación de impagos.

- `Reclamacion` — proceso abierto sobre una `CuotaAnual` impagada. Tiene nivel (1ª, 2ª, 3ª) y estado.
- `AccionReclamacion` — cada acción del proceso: notificación, llamada, carta certificada, gestoría.

**Regla clave:** se abre automáticamente cuando una `CuotaAnual` supera X días de impago. Las acciones quedan auditadas.

---

### 3.6 Presupuesto

**Responsabilidad:** planificación económica anual.

- `PlanificacionAnual` — el presupuesto del ejercicio.
- `PartidaPresupuestaria` — línea de ingreso o gasto (presupuestado, comprometido, ejecutado).
- `CategoriaPartida` — clasificación de partidas.

**Regla clave:** `PartidaPresupuestaria` no contiene dinero real. La ejecución se calcula cruzando partidas con `ApunteCaja` del mismo ejercicio y categoría.

---

### 3.7 Tesorería

**Responsabilidad:** registro de los movimientos reales de dinero.

- `CuentaBancaria` — cuenta real (corriente, ahorro, caja). IBAN, banco, saldo actual y saldo conciliado.
- `ApunteCaja` — el registro contable fundamental:
  - `tipo`: `INGRESO` | `GASTO`
  - `importe`, `fecha`, `concepto`
  - `cuenta_bancaria_id`
  - `origen_tipo` + `origen_id` — referencia polimórfica al evento origen (`CUOTA`, `DONACION`, `REMESA`, `PAGO`, `MANUAL`)
  - En versión `COMPLETA`: `asiento_id` → referencia al asiento generado
- `ExtractoBancario` — línea importada del CSV/MT940 del banco.
- `Conciliacion` — vincula `ApunteCaja` con `ExtractoBancario`. Registra fecha, método y usuario.

**Regla clave:** `ApunteCaja` es el registro de caja, no el evento de negocio. Una cuota impagada no genera apunte. Una cuota cobrada sí.

---

### 3.8 Contabilidad *(solo versión COMPLETA)*

**Responsabilidad:** partida doble, plan de cuentas PGC y estados financieros.

- `CuentaContable` — nodo del árbol PGC. Importable/exportable JSON. Estructura jerárquica: grupo → subgrupo → cuenta → subcuenta.
- `Asiento` — cabecera del asiento contable (fecha, número, descripción, ejercicio).
- `LineaAsiento` — cada línea debe/haber, referencia a `CuentaContable`.

**Regla clave:** cada `ApunteCaja` en versión `COMPLETA` dispara la generación del `Asiento` correspondiente mediante el `RegistroContable` (registry pattern), que mapea `(origen_tipo, concepto) → (cuenta_debe, cuenta_haber)`.

---

## 4. Cadena de vida de un euro

```
[Socio debe cuota]
        │
        ▼
  CuotaAnual (obligación)
        │
        ├──── vía SEPA ────► OrdenCobro → Remesa → XML banco
        │                         │ PROCESADA
        │                         ▼
        ├──── vía online ──► Pago (cobro/pasarela)
        │                         │ COMPLETADO
        │                         ▼
        └──── vía manual ─────────┤
                                  │
                                  ▼
                            ApunteCaja  ◄──── también: Donacion, Gasto manual
                                  │
                     [versión SIMPLE] → fin
                     [versión COMPLETA]
                                  │
                                  ▼
                       Asiento (debe/haber)
                        └── LineaAsiento × N
```

---

## 5. Feature flags

```python
FINANCIERO_CONFIG = {
    "version": "SIMPLE",  # "SIMPLE" | "COMPLETA"
    "subdominios_activos": {
        "cuotas":          True,
        "donaciones":      True,
        "remesas":         True,
        "cobro":           True,
        "reclamaciones":   True,
        "presupuesto":     True,
        "tesoreria":       True,
        "contabilidad":    False,  # solo COMPLETA
    }
}
```

---

## 6. Convenciones de código

- **ORM:** SQLAlchemy async con `Mapped` / `mapped_column`. Sin `Column()` legacy.
- **PKs:** `uuid.UUID` en todos los modelos.
- **Importes:** `Decimal` (nunca `float`).
- **Fechas:** `date` para negocio, `datetime` para auditoría.
- **Herencia:** todos los modelos heredan de `BaseModel` (`AuditoriaMixin` incluido).
- **Estados:** FK a tablas de estado en `domains/core/models/estados.py`.
- **GraphQL:** strawchemy para generación automática de tipos desde modelos SQLAlchemy.
- **Paginación:** todos los métodos de listado aceptan `limit` y `offset`.
- **Servicios:** heredan de `BaseService`. Async/await en todos los métodos.

---

## 7. Estados por subdominio

| Subdominio | Clase de estado | Códigos |
|---|---|---|
| Cuotas | `EstadoCuota` | `PENDIENTE`, `COBRADA`, `IMPAGADA`, `ANULADA`, `EXENTA` |
| Donaciones | `EstadoDonacion` | `PENDIENTE`, `RECIBIDA`, `CERTIFICADA`, `ANULADA` |
| Remesas | `EstadoRemesa` | `BORRADOR`, `GENERADA`, `ENVIADA`, `PROCESADA`, `RECHAZADA`, `PARCIAL` |
| Órdenes cobro | `EstadoOrdenCobro` | `PENDIENTE`, `PROCESADA`, `FALLIDA`, `ANULADA` |
| Cobro/Pago | `EstadoPago` *(nuevo)* | `CREADO`, `COMPLETADO`, `FALLIDO`, `REEMBOLSADO`, `CANCELADO` |
| Reclamaciones | `EstadoReclamacion` *(nuevo)* | `ABIERTA`, `EN_PROCESO`, `RESUELTA`, `JUDICIAL`, `CERRADA` |
| Apunte de caja | `EstadoApunte` *(nuevo)* | `PENDIENTE`, `CONFIRMADO`, `CONCILIADO`, `ANULADO` |
| Presupuesto | `EstadoPlanificacion` | `BORRADOR`, `APROBADO`, `EN_EJECUCION`, `CERRADO` |

---

## 8. Archivos a eliminar tras migración

| Archivo actual | Reemplazado por |
|---|---|
| `models/tesoreria.py` | `models/tesoreria/apunte.py` |
| `models/tesoreria_conciliacion.py` | `models/tesoreria/conciliacion.py` |
| `models/cuotas.py` | `models/cuotas/` |
| `models/donaciones.py` | `models/donaciones/` |
| `models/remesas.py` | `models/remesas/` |
| `models/presupuesto.py` | `models/presupuesto/` |
| `domains/cobro/` (raíz) | `models/cobro/` |

---

## 9. Orden de implementación

1. `core/feature_flags.py` — ampliar con todos los subdominios
2. `models/tesoreria/` — `cuenta_bancaria`, `apunte`, `conciliacion`
3. `models/cobro/` — migrar desde `domains/cobro/`
4. `models/reclamaciones/` — nuevo
5. Refactor cuotas, donaciones, remesas, presupuesto a subcarpetas
6. `services/base_service.py` + todos los servicios
7. `models/contabilidad/` — solo COMPLETA
8. `services/contabilidad_service.py` — solo COMPLETA
