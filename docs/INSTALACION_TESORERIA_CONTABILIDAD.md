# Guía de Instalación: Módulos de Tesorería y Contabilidad

## Requisitos Previos

- Python 3.10+
- SQLAlchemy 2.0+
- FastAPI
- Strawberry GraphQL
- Base de datos PostgreSQL (recomendado)

## Instalación

### 1. Actualizar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Crear Migraciones de Base de Datos

Los modelos ya están definidos en:

- `app/domains/financiero/models/tesoreria.py`
- `app/domains/financiero/models/contabilidad.py`

Si usas Alembic para migraciones:

```bash
alembic revision --autogenerate -m "Add tesoreria and contabilidad models"
alembic upgrade head
```

Si usas SQLAlchemy directamente:

```python
from app.core.database import engine
from app.domains.financiero.models import (
    CuentaBancaria,
    MovimientoTesoreria,
    ConciliacionBancaria,
    CuentaContable,
    AsientoContable,
    ApunteContable,
    BalanceContable,
)
from sqlalchemy import text

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

### 3. Cargar Plan de Cuentas Inicial

```python
from app.scripts.seeding.plan_cuentas_esfl import cargar_plan_cuentas_esfl
from app.core.database import get_session

async def seed_data():
    async with get_session() as session:
        await cargar_plan_cuentas_esfl(session)
```

## Configuración

### Variables de Entorno

Agregar al archivo `.env`:

```env
# Tesorería
TESORERIA_ENCRIPTAR_IBAN=true
TESORERIA_ENCRIPTACION_KEY=tu_clave_secreta_aqui

# Contabilidad
CONTABILIDAD_EJERCICIO_DEFECTO=2026
CONTABILIDAD_VALIDAR_PARTIDA_DOBLE=true
```

### Configuración de la Base de Datos

En `app/core/database.py`:

```python
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/siga"
```

## Uso en la Aplicación

### Inyección de Dependencias

```python
from fastapi import Depends
from app.core.database import get_session
from app.domains.financiero.services import TesoreriaService, ContabilidadService

async def get_tesoreria_service(session = Depends(get_session)) -> TesoreriaService:
    return TesoreriaService(session)

async def get_contabilidad_service(session = Depends(get_session)) -> ContabilidadService:
    return ContabilidadService(session)
```

### Crear Endpoint FastAPI

```python
from fastapi import APIRouter, Depends
from datetime import date
from decimal import Decimal

router = APIRouter(prefix="/api/tesoreria", tags=["tesoreria"])

@router.post("/cuentas")
async def crear_cuenta(
    nombre: str,
    iban: str,
    banco_nombre: str,
    tesoreria: TesoreriaService = Depends(get_tesoreria_service),
):
    return await tesoreria.crear_cuenta_bancaria(
        nombre=nombre,
        iban=iban,
        banco_nombre=banco_nombre,
    )
```

## Integración con GraphQL

### Definir Tipos Strawberry

```python
from strawberry import type, field
from uuid import UUID
from datetime import date
from decimal import Decimal

@type
class CuentaBancariaType:
    id: UUID
    nombre: str
    iban: str
    banco_nombre: str
    saldo_actual: Decimal
    activa: bool

@type
class MovimientoTesoreriaType:
    id: UUID
    cuenta_id: UUID
    fecha: date
    importe: Decimal
    tipo: str
    concepto: str
    conciliado: bool
```

### Crear Queries y Mutations

```python
import strawberry
from typing import List

@strawberry.type
class Query:
    @strawberry.field
    async def cuentas_bancarias(
        self,
        tesoreria: TesoreriaService = strawberry.dependency(get_tesoreria_service),
    ) -> List[CuentaBancariaType]:
        cuentas = await tesoreria.listar_cuentas_bancarias()
        return [
            CuentaBancariaType(
                id=c.id,
                nombre=c.nombre,
                iban=c.iban,
                banco_nombre=c.banco_nombre,
                saldo_actual=c.saldo_actual,
                activa=c.activa,
            )
            for c in cuentas
        ]

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def crear_cuenta_bancaria(
        self,
        nombre: str,
        iban: str,
        banco_nombre: str,
        tesoreria: TesoreriaService = strawberry.dependency(get_tesoreria_service),
    ) -> CuentaBancariaType:
        cuenta = await tesoreria.crear_cuenta_bancaria(
            nombre=nombre,
            iban=iban,
            banco_nombre=banco_nombre,
        )
        return CuentaBancariaType(
            id=cuenta.id,
            nombre=cuenta.nombre,
            iban=cuenta.iban,
            banco_nombre=cuenta.banco_nombre,
            saldo_actual=cuenta.saldo_actual,
            activa=cuenta.activa,
        )
```

## Testing

### Crear Tests Unitarios

```python
import pytest
from datetime import date
from decimal import Decimal
from app.domains.financiero.services import TesoreriaService
from app.domains.financiero.models import TipoMovimientoTesoreria

@pytest.mark.asyncio
async def test_crear_cuenta_bancaria(session):
    tesoreria = TesoreriaService(session)
    
    cuenta = await tesoreria.crear_cuenta_bancaria(
        nombre="Test Cuenta",
        iban="ES9121000418450200051332",
        banco_nombre="Banco Test",
    )
    
    assert cuenta.nombre == "Test Cuenta"
    assert cuenta.saldo_actual == Decimal("0.00")
    assert cuenta.activa == True

@pytest.mark.asyncio
async def test_registrar_movimiento(session):
    tesoreria = TesoreriaService(session)
    
    cuenta = await tesoreria.crear_cuenta_bancaria(
        nombre="Test Cuenta",
        iban="ES9121000418450200051332",
        banco_nombre="Banco Test",
    )
    
    movimiento = await tesoreria.registrar_movimiento(
        cuenta_id=cuenta.id,
        fecha=date.today(),
        importe=Decimal("100.00"),
        tipo=TipoMovimientoTesoreria.INGRESO,
        concepto="Test ingreso",
    )
    
    assert movimiento.importe == Decimal("100.00")
    assert movimiento.tipo == TipoMovimientoTesoreria.INGRESO
    
    # Verificar que el saldo se actualizó
    cuenta_actualizada = await tesoreria.obtener_cuenta_bancaria(cuenta.id)
    assert cuenta_actualizada.saldo_actual == Decimal("100.00")
```

## Troubleshooting

### Error: "Cuenta bancaria no encontrada"

Verificar que la `cuenta_id` existe en la base de datos:

```python
cuenta = await tesoreria.obtener_cuenta_bancaria(cuenta_id)
if not cuenta:
    print(f"Cuenta {cuenta_id} no encontrada")
```

### Error: "El asiento no está cuadrado"

Verificar que debe = haber:

```python
asiento = await contabilidad.obtener_asiento(asiento_id)
print(f"Debe: {asiento.total_debe}, Haber: {asiento.total_haber}")
```

### Error: "La conciliación no está equilibrada"

Verificar la diferencia:

```python
conciliacion = await tesoreria.obtener_conciliacion(conciliacion_id)
print(f"Diferencia: {conciliacion.diferencia}")
print(f"Saldo extracto: {conciliacion.saldo_final_extracto}")
print(f"Saldo sistema: {conciliacion.saldo_final_sistema}")
```

## Documentación Adicional

- [Guía de Uso](./GUIA_TESORERIA_CONTABILIDAD.md)
- [Diseño Técnico](./DISEÑO_TESORERIA_CONTABILIDAD.md)
- [PCESFL 2013](https://www.icac.hacienda.gob.es/)
- [Guía AEF](https://abc.fundaciones.org/)

---

**Versión**: 1.0  
**Última actualización**: 2 de mayo de 2026
