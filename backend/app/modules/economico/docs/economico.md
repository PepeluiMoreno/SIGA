# Módulo Financiero — Tesorería y Contabilidad

Normativa aplicada: **PCESFL 2013** y **Guía AEF 2022**.

---

## 1. Tesorería

Gestiona la liquidez de la organización: cuentas bancarias, movimientos de caja y conciliaciones.

### Modelos

**`CuentaBancaria`** — cuenta bancaria real de la organización.

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | String | Nombre descriptivo |
| `iban` | String | IBAN (encriptado en BD) |
| `bic_swift` | String | BIC/SWIFT |
| `banco_nombre` | String | Nombre del banco |
| `saldo_actual` | Decimal | Saldo actualizado en cada movimiento |
| `agrupacion_id` | UUID | Agrupación territorial (tesorería descentralizada) |
| `activa` | Boolean | Estado de la cuenta |

**`MovimientoTesoreria`** — cada euro que entra o sale.

| Campo | Tipo | Descripción |
|---|---|---|
| `cuenta_id` | UUID | Cuenta bancaria |
| `fecha` | Date | Fecha del movimiento |
| `importe` | Decimal | Importe |
| `tipo` | Enum | `INGRESO`, `GASTO`, `TRASPASO` |
| `concepto` | String | Descripción |
| `referencia_externa` | String | Referencia bancaria |
| `entidad_origen_tipo` | String | `cuota`, `donacion`, `actividad`... |
| `entidad_origen_id` | UUID | ID del evento de negocio origen |
| `conciliado` | Boolean | Estado de conciliación |
| `asiento_id` | UUID | Asiento contable generado (versión COMPLETA) |

**`ConciliacionBancaria`** — cierre de conciliación por período.

| Campo | Tipo | Descripción |
|---|---|---|
| `cuenta_id` | UUID | Cuenta bancaria |
| `fecha_inicio` / `fecha_fin` | Date | Período |
| `saldo_inicial/final_extracto` | Decimal | Datos del banco |
| `saldo_inicial/final_sistema` | Decimal | Datos del sistema |
| `diferencia` | Decimal | Debe ser 0 para confirmar |
| `conciliado` | Boolean | Estado |

### Servicio: `TesoreriaService`

```python
await tesoreria.crear_cuenta_bancaria(nombre, iban, banco_nombre, bic_swift, agrupacion_id)
await tesoreria.registrar_movimiento(cuenta_id, fecha, importe, tipo, concepto, ...)
await tesoreria.obtener_movimientos_por_cuenta(cuenta_id, fecha_inicio, fecha_fin)
await tesoreria.marcar_movimiento_conciliado(movimiento_id, extracto_id)
await tesoreria.crear_conciliacion_bancaria(cuenta_id, fecha_inicio, fecha_fin, ...)
await tesoreria.confirmar_conciliacion(conciliacion_id)
await tesoreria.obtener_saldo_cuenta(cuenta_id)
```

---

## 2. Contabilidad *(solo versión COMPLETA)*

Partida doble según PCESFL 2013. Solo activo cuando `FINANCIERO_CONFIG["version"] == "COMPLETA"`.

### Modelos

**`CuentaContable`** — nodo del árbol del Plan General Contable.

| Campo | Tipo | Descripción |
|---|---|---|
| `codigo` | String | Código contable (ej: `"101"`) |
| `nombre` | String | Nombre |
| `tipo` | Enum | `ACTIVO`, `PASIVO`, `PATRIMONIO`, `INGRESO`, `GASTO` |
| `nivel` | Integer | 1=grupo, 2=subgrupo, 3=cuenta |
| `padre_id` | UUID | Cuenta padre (jerarquía) |
| `permite_asiento` | Boolean | Solo cuentas de nivel 3 |
| `es_dotacion` | Boolean | Dotación fundacional (requisito AEF) |

**`AsientoContable`** — cabecera del asiento.

| Campo | Tipo | Descripción |
|---|---|---|
| `ejercicio` | Integer | Año fiscal |
| `numero_asiento` | Integer | Número secuencial por ejercicio |
| `fecha` | Date | Fecha |
| `glosa` | String | Descripción |
| `tipo_asiento` | Enum | `APERTURA`, `GESTION`, `REGULARIZACION`, `CIERRE` |
| `estado` | Enum | `BORRADOR`, `CONFIRMADO`, `ANULADO` |

**`ApunteContable`** — línea debe/haber del asiento.

| Campo | Tipo | Descripción |
|---|---|---|
| `asiento_id` | UUID | Asiento padre |
| `cuenta_id` | UUID | Cuenta contable |
| `debe` | Decimal | Importe al debe |
| `haber` | Decimal | Importe al haber |
| `concepto` | String | Descripción |
| `actividad_id` | UUID | Actividad (trazabilidad fines propios — AEF) |

**`BalanceContable`** — balance de sumas y saldos generado.

### Servicio: `ContabilidadService`

```python
await contabilidad.crear_cuenta_contable(codigo, nombre, tipo, nivel, padre_id, es_dotacion)
await contabilidad.importar_plan_cuentas(lista_dict)   # desde JSON
await contabilidad.crear_asiento(ejercicio, fecha, glosa, lineas, tipo_asiento)
await contabilidad.anular_asiento(asiento_id)
await contabilidad.calcular_saldo_cuenta(cuenta_id, ejercicio, fecha_fin)
await contabilidad.balance_comprobacion(ejercicio, fecha_fin)
```

El servicio valida automáticamente que `sum(debe) == sum(haber)` antes de persistir.

---

## 3. Plan de cuentas PCESFL 2013

Script de carga inicial: `backend/app/scripts/seeding/plan_cuentas_esfl.py`

Estructura simplificada incluida:

| Grupo | Nombre |
|---|---|
| 1 | ACTIVO (Caja, Bancos, Deudores) |
| 2 | PASIVO (Acreedores) |
| 3 | PATRIMONIO (Dotación fundacional, Reservas) |
| 4 | INGRESOS (Cuotas, Donaciones, Subvenciones, Financieros) |
| 5 | GASTOS (Actividades propias, Personal, Administración, Amortizaciones) |

---

## 4. Integración entre subdominios

### Cuota cobrada
1. `CuotaAnual` pasa a estado `COBRADA`
2. `TesoreriaService.registrar_movimiento()` → `MovimientoTesoreria` (INGRESO, origen=cuota)
3. En versión COMPLETA: `ContabilidadService.crear_asiento()` → DEBE cuenta 101 / HABER cuenta 400

### Donación recibida
1. `Donacion` pasa a estado `RECIBIDA`
2. `MovimientoTesoreria` (INGRESO, origen=donacion)
3. En versión COMPLETA: DEBE cuenta 101 / HABER cuenta 410

---

## 5. Instalación

```bash
# Migraciones
alembic revision --autogenerate -m "Add tesoreria and contabilidad models"
alembic upgrade head

# Cargar plan de cuentas (solo versión COMPLETA)
uv run python -c "
import asyncio
from app.scripts.seeding.plan_cuentas_esfl import cargar_plan_cuentas_esfl
from app.core.database import get_session
async def main():
    async with get_session() as s:
        await cargar_plan_cuentas_esfl(s)
asyncio.run(main())
"
```

## 6. Variables de entorno

```env
TESORERIA_ENCRIPTAR_IBAN=true
TESORERIA_ENCRIPTACION_KEY=clave_secreta
CONTABILIDAD_EJERCICIO_DEFECTO=2026
CONTABILIDAD_VALIDAR_PARTIDA_DOBLE=true
```

## 7. Cumplimiento normativo

| Requisito | Estado |
|---|---|
| Plan de cuentas PCESFL 2013 | ✅ Incluido y cargable desde JSON |
| Partida doble con validación | ✅ `esta_cuadrado` antes de confirmar |
| Tipos de asiento (Apertura, Gestión, Regularización, Cierre) | ✅ |
| Dotación fundacional identificada | ✅ Campo `es_dotacion` |
| Destino de rentas (fines propios vs administración) | ✅ `actividad_id` en `ApunteContable` |
| Libro Diario | ✅ `listar_asientos()` ordenado por fecha/número |
| Balance de comprobación | ✅ `balance_comprobacion()` |
