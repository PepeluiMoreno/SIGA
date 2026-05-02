# Guía de Implementación: Módulos de Tesorería y Contabilidad

## Índice

1. [Introducción](#introducción)
2. [Módulo de Tesorería](#módulo-de-tesorería)
3. [Módulo de Contabilidad](#módulo-de-contabilidad)
4. [Integración](#integración)
5. [Ejemplos de Uso](#ejemplos-de-uso)
6. [Requisitos Normativos](#requisitos-normativos)

---

## Introducción

Los módulos de **Tesorería** y **Contabilidad** han sido implementados siguiendo:

- **Arquitectura**: Domain-Driven Design (DDD) con SQLAlchemy 2.0 Async
- **Normativa**: Plan de Contabilidad de Entidades Sin Fines Lucrativos (PCESFL 2013)
- **Requisitos AEF**: Guía de Obligaciones Contables para Fundaciones 2022

Estos módulos permiten:

- Gestionar cuentas bancarias y movimientos de efectivo
- Registrar asientos contables con partida doble
- Conciliar extractos bancarios
- Generar balances y reportes financieros
- Cumplir con requisitos de auditoría y presentación de cuentas

---

## Módulo de Tesorería

### Descripción

El módulo de tesorería gestiona la liquidez de la organización, controlando cuentas bancarias, movimientos de efectivo y conciliaciones bancarias.

### Modelos

#### `CuentaBancaria`

Representa una cuenta bancaria de la organización.

**Campos principales:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `nombre` | String | Nombre descriptivo (ej: "Cuenta Operativa Santander") |
| `iban` | String | IBAN encriptado |
| `banco_nombre` | String | Nombre del banco |
| `saldo_actual` | Decimal | Saldo actual de la cuenta |
| `agrupacion_id` | UUID | Agrupación territorial (para tesorería descentralizada) |
| `activa` | Boolean | Estado de la cuenta |

**Métodos:**

```python
@property
def saldo_disponible(self) -> Decimal:
    """Retorna el saldo disponible."""
```

#### `MovimientoTesoreria`

Representa un movimiento de efectivo (ingreso, gasto o traspaso).

**Campos principales:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `cuenta_id` | UUID | Cuenta bancaria asociada |
| `fecha` | Date | Fecha del movimiento |
| `importe` | Decimal | Importe del movimiento |
| `tipo` | Enum | INGRESO, GASTO o TRASPASO |
| `concepto` | String | Descripción del movimiento |
| `referencia_externa` | String | Referencia bancaria (ej: número de transacción) |
| `entidad_origen_tipo` | String | Tipo de entidad origen ('cuota', 'donacion', etc.) |
| `entidad_origen_id` | UUID | ID de la entidad origen |
| `conciliado` | Boolean | Estado de conciliación |
| `asiento_id` | UUID | Asiento contable asociado |

**Métodos:**

```python
@property
def es_ingreso(self) -> bool:
    """Verifica si el movimiento es un ingreso."""

@property
def es_gasto(self) -> bool:
    """Verifica si el movimiento es un gasto."""
```

#### `ConciliacionBancaria`

Registro de conciliación entre extracto bancario y movimientos registrados.

**Campos principales:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `cuenta_id` | UUID | Cuenta bancaria |
| `fecha_inicio` | Date | Inicio del período |
| `fecha_fin` | Date | Fin del período |
| `saldo_inicial_extracto` | Decimal | Saldo inicial del extracto |
| `saldo_final_extracto` | Decimal | Saldo final del extracto |
| `saldo_inicial_sistema` | Decimal | Saldo inicial del sistema |
| `saldo_final_sistema` | Decimal | Saldo final del sistema |
| `diferencia` | Decimal | Diferencia entre extracto y sistema |
| `conciliado` | Boolean | Estado de conciliación |

### Servicio: `TesoreriaService`

Proporciona la lógica de negocio para tesorería.

**Métodos principales:**

```python
async def crear_cuenta_bancaria(
    nombre: str,
    iban: str,
    banco_nombre: str,
    bic_swift: Optional[str] = None,
    agrupacion_id: Optional[UUID] = None,
) -> CuentaBancaria
```

Crea una nueva cuenta bancaria.

```python
async def registrar_movimiento(
    cuenta_id: UUID,
    fecha: date,
    importe: Decimal,
    tipo: TipoMovimientoTesoreria,
    concepto: str,
    referencia_externa: Optional[str] = None,
    entidad_origen_tipo: Optional[str] = None,
    entidad_origen_id: Optional[UUID] = None,
) -> MovimientoTesoreria
```

Registra un movimiento y actualiza automáticamente el saldo de la cuenta.

```python
async def crear_conciliacion_bancaria(
    cuenta_id: UUID,
    fecha_inicio: date,
    fecha_fin: date,
    saldo_inicial_extracto: Decimal,
    saldo_final_extracto: Decimal,
) -> ConciliacionBancaria
```

Crea un registro de conciliación bancaria.

```python
async def confirmar_conciliacion(
    conciliacion_id: UUID
) -> ConciliacionBancaria
```

Confirma una conciliación si está equilibrada.

---

## Módulo de Contabilidad

### Descripción

El módulo de contabilidad gestiona el plan de cuentas, asientos contables y la generación de balances según el PCESFL 2013.

### Modelos

#### `CuentaContable`

Representa una cuenta en el plan de cuentas.

**Campos principales:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `codigo` | String | Código contable (ej: "57200001") |
| `nombre` | String | Nombre de la cuenta |
| `tipo` | Enum | ACTIVO, PASIVO, PATRIMONIO, INGRESO, GASTO |
| `nivel` | Integer | 1=grupo, 2=subgrupo, 3=cuenta |
| `padre_id` | UUID | Cuenta padre (para jerarquía) |
| `permite_asiento` | Boolean | Solo cuentas de nivel 3 |
| `es_dotacion` | Boolean | Elementos de dotación fundacional |
| `activa` | Boolean | Estado de la cuenta |

**Métodos:**

```python
@property
def es_cuenta_hoja(self) -> bool:
    """Verifica si es una cuenta de último nivel."""
```

#### `AsientoContable`

Representa un asiento contable (conjunto de apuntes).

**Campos principales:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `ejercicio` | Integer | Año fiscal |
| `numero_asiento` | Integer | Número secuencial |
| `fecha` | Date | Fecha del asiento |
| `glosa` | String | Descripción |
| `tipo_asiento` | Enum | APERTURA, GESTION, REGULARIZACION, CIERRE |
| `estado` | Enum | BORRADOR, CONFIRMADO, ANULADO |

**Métodos:**

```python
@property
def total_debe(self) -> Decimal:
    """Calcula el total del debe."""

@property
def total_haber(self) -> Decimal:
    """Calcula el total del haber."""

@property
def esta_cuadrado(self) -> bool:
    """Verifica si debe = haber."""

async def confirmar(self) -> None:
    """Confirma el asiento si está cuadrado."""

async def anular(self) -> None:
    """Anula el asiento."""
```

#### `ApunteContable`

Representa una línea de un asiento (partida doble).

**Campos principales:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `asiento_id` | UUID | Asiento padre |
| `cuenta_id` | UUID | Cuenta contable |
| `debe` | Decimal | Importe en el debe |
| `haber` | Decimal | Importe en el haber |
| `concepto` | String | Descripción |
| `actividad_id` | UUID | Actividad asociada (para seguimiento de fines propios) |

#### `BalanceContable`

Registro de balance de sumas y saldos.

**Campos principales:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `ejercicio` | Integer | Año fiscal |
| `fecha_generacion` | DateTime | Cuándo se generó |
| `total_debe` | Decimal | Total del debe |
| `total_haber` | Decimal | Total del haber |

### Servicio: `ContabilidadService`

Proporciona la lógica de negocio para contabilidad.

**Métodos principales:**

```python
async def crear_cuenta_contable(
    codigo: str,
    nombre: str,
    tipo: TipoCuentaContable,
    nivel: int,
    padre_id: Optional[UUID] = None,
    es_dotacion: bool = False,
) -> CuentaContable
```

Crea una nueva cuenta contable.

```python
async def crear_asiento(
    ejercicio: int,
    numero_asiento: int,
    fecha: date,
    glosa: str,
    tipo_asiento: TipoAsientoContable = TipoAsientoContable.GESTION,
) -> AsientoContable
```

Crea un nuevo asiento contable en estado BORRADOR.

```python
async def crear_apunte(
    asiento_id: UUID,
    cuenta_id: UUID,
    debe: Decimal = Decimal("0.00"),
    haber: Decimal = Decimal("0.00"),
    concepto: str = "",
    actividad_id: Optional[UUID] = None,
) -> ApunteContable
```

Crea un apunte dentro de un asiento.

```python
async def confirmar_asiento(asiento_id: UUID) -> AsientoContable
```

Confirma un asiento si está cuadrado (debe = haber).

```python
async def calcular_saldo_cuenta(
    cuenta_id: UUID,
    fecha_fin: Optional[date] = None,
    ejercicio: Optional[int] = None,
) -> Decimal
```

Calcula el saldo de una cuenta en una fecha determinada.

```python
async def generar_balance(
    ejercicio: int,
    fecha_fin: date,
) -> BalanceContable
```

Genera un balance de sumas y saldos.

---

## Integración

### Automatización: Cuota → Movimiento → Asiento

Cuando se marca una `CuotaAnual` como **COBRADA**, se debe:

1. **Crear MovimientoTesoreria**: Registrar ingreso en la cuenta bancaria
2. **Crear AsientoContable**: Registrar partida doble:
   - **DEBE**: Cuenta 101 (Bancos c/c)
   - **HABER**: Cuenta 400 (Cuotas de miembros)

### Automatización: Donación → Movimiento → Asiento

Similar a cuotas, pero con cuentas diferentes:

- **DEBE**: Cuenta 101 (Bancos c/c)
- **HABER**: Cuenta 410 (Donaciones)

### Conciliación Bancaria

Flujo recomendado:

1. Descargar extracto bancario
2. Crear `ConciliacionBancaria` con datos del extracto
3. Marcar movimientos como conciliados
4. Confirmar conciliación (debe estar equilibrada)

---

## Ejemplos de Uso

### Ejemplo 1: Crear Cuenta Bancaria

```python
from app.domains.financiero.services import TesoreriaService

tesoreria = TesoreriaService(session)

cuenta = await tesoreria.crear_cuenta_bancaria(
    nombre="Cuenta Operativa Santander",
    iban="ES9121000418450200051332",  # Encriptado en BD
    banco_nombre="Banco Santander",
    bic_swift="BSESESMM",
)
```

### Ejemplo 2: Registrar Ingreso por Cuota

```python
from datetime import date
from decimal import Decimal
from app.domains.financiero.models import TipoMovimientoTesoreria

movimiento = await tesoreria.registrar_movimiento(
    cuenta_id=cuenta.id,
    fecha=date.today(),
    importe=Decimal("50.00"),
    tipo=TipoMovimientoTesoreria.INGRESO,
    concepto="Cuota anual miembro",
    referencia_externa="SEPA-2026-001",
    entidad_origen_tipo="cuota",
    entidad_origen_id=cuota_id,
)
```

### Ejemplo 3: Crear Asiento Contable

```python
from app.domains.financiero.services import ContabilidadService
from app.domains.financiero.models import TipoAsientoContable
from decimal import Decimal

contabilidad = ContabilidadService(session)

# Crear asiento
asiento = await contabilidad.crear_asiento(
    ejercicio=2026,
    numero_asiento=1,
    fecha=date.today(),
    glosa="Ingreso cuota anual miembro",
    tipo_asiento=TipoAsientoContable.GESTION,
)

# Crear apuntes (partida doble)
await contabilidad.crear_apunte(
    asiento_id=asiento.id,
    cuenta_id=cuenta_101_id,  # Bancos c/c
    debe=Decimal("50.00"),
    concepto="Ingreso cuota",
)

await contabilidad.crear_apunte(
    asiento_id=asiento.id,
    cuenta_id=cuenta_400_id,  # Cuotas de miembros
    haber=Decimal("50.00"),
    concepto="Cuota anual",
)

# Confirmar asiento
await contabilidad.confirmar_asiento(asiento.id)
```

### Ejemplo 4: Conciliación Bancaria

```python
from datetime import date
from decimal import Decimal

# Crear conciliación
conciliacion = await tesoreria.crear_conciliacion_bancaria(
    cuenta_id=cuenta.id,
    fecha_inicio=date(2026, 5, 1),
    fecha_fin=date(2026, 5, 31),
    saldo_inicial_extracto=Decimal("1000.00"),
    saldo_final_extracto=Decimal("1500.00"),
)

# Verificar si está equilibrada
if conciliacion.esta_equilibrada:
    await tesoreria.confirmar_conciliacion(conciliacion.id)
else:
    print(f"Diferencia: {conciliacion.diferencia}")
```

---

## Requisitos Normativos

### Cumplimiento AEF (Guía de Obligaciones Contables)

✅ **Libro Diario**: Los asientos contables actúan como libro diario.

✅ **Libro Mayor**: Generado mediante consultas de apuntes por cuenta.

✅ **Balance de Sumas y Saldos**: Método `generar_balance()`.

✅ **Destino de Rentas**: Campo `actividad_id` en apuntes para seguimiento de fines propios vs administración.

✅ **Inventario**: Los modelos de inmovilizado pueden extenderse para generar inventario.

✅ **Plan de Actuación**: Integración con módulo de presupuestos para comparar ejecución.

### Cumplimiento PCESFL 2013

✅ **Plan de Cuentas**: Incluye estructura simplificada del PCESFL 2013.

✅ **Partida Doble**: Validación automática de debe = haber.

✅ **Tipos de Asientos**: APERTURA, GESTION, REGULARIZACION, CIERRE.

✅ **Estados de Asientos**: BORRADOR, CONFIRMADO, ANULADO.

✅ **Cuentas de Dotación**: Campo `es_dotacion` para identificar elementos de dotación fundacional.

---

## Próximos Pasos

1. **Generar tipos GraphQL**: Ejecutar `strawchemy` para generar tipos automáticos.
2. **Crear mutaciones GraphQL**: Exponer servicios a través de API GraphQL.
3. **Desarrollar interfaz frontend**: Crear vistas Vue 3 para tesorería y contabilidad.
4. **Implementar reportes**: Balance, PyG, Libro Diario, Libro Mayor.
5. **Integración de importación**: Soporte para importar extractos bancarios (Norma 43, SWIFT, Excel).
6. **Auditoría y trazabilidad**: Completar campos de auditoría (creado_por, modificado_por, etc.).

---

**Versión**: 1.0  
**Última actualización**: 2 de mayo de 2026  
**Autor**: Manus AI Agent
