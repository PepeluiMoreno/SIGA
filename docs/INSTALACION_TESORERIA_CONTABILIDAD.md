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

Los modelos están definidos en:

- `app/domains/financiero/models/tesoreria/` (cuenta_bancaria, apunte, conciliacion)
- `app/domains/financiero/models/contabilidad/` (plan_cuentas, asiento)

Generar y aplicar migraciones con Alembic:

```bash
alembic revision --autogenerate -m "Add tesoreria and contabilidad models"
alembic upgrade head
```

### 3. Cargar Plan de Cuentas Inicial

```python
from app.scripts.seeding.plan_cuentas_esfl import cargar_plan_cuentas_esfl
from app.core.database import get_session

async def seed_data():
    async with get_session() as session:
        await cargar_plan_cuentas_esfl(session)
```

El plan de cuentas sigue el **PCESFL 2013** (Plan de Contabilidad de Entidades Sin Fines Lucrativos).

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
from app.domains.financiero.services.tesoreria_service import TesoreriaService
from app.domains.financiero.services.contabilidad_service import ContabilidadService

async def get_tesoreria_service(session = Depends(get_session)) -> TesoreriaService:
    return TesoreriaService(session)

async def get_contabilidad_service(session = Depends(get_session)) -> ContabilidadService:
    return ContabilidadService(session)
```

### Integración con GraphQL (strawchemy)

SIGA usa **strawchemy** para generación automática de tipos GraphQL desde los modelos SQLAlchemy.
No es necesario definir manualmente los tipos `@strawberry.type` para las entidades — strawchemy
los genera a partir del modelo. Solo se definen queries y mutations en los resolvers.

Ejemplo de query:

```python
import strawberry
from app.domains.financiero.services.tesoreria_service import TesoreriaService

@strawberry.type
class Query:
    @strawberry.field
    async def cuentas_bancarias(
        self,
        info: strawberry.types.Info,
    ) -> list:
        service = TesoreriaService(info.context["session"])
        return await service.listar_cuentas()
```

## Nomenclatura de modelos

| Concepto | Clase Python | Tabla BD |
|---|---|---|
| Cuenta bancaria | `CuentaBancaria` | `cuentas_bancarias` |
| Apunte de caja | `ApunteCaja` | `apuntes_caja` |
| Extracto bancario | `ExtractoBancario` | `extractos_bancarios` |
| Conciliación | `Conciliacion` | `conciliaciones` |
| Cuenta contable | `CuentaContable` | `cuentas_contables` |
| Asiento contable | `AsientoContable` | `asientos_contables` |
| Línea de asiento | `ApunteContable` | `apuntes_contables` |

> **Nota:** Los nombres `MovimientoTesoreria`, `ConciliacionBancaria`, `AsientoContable` y
> `ApunteContable` que aparecen en documentación anterior han sido unificados con los nombres
> de clase definitivos listados arriba. Ver `DISEÑO_TESORERIA_CONTABILIDAD.md` para el diseño completo.

## Testing

### Tests Unitarios

```python
import pytest
from datetime import date
from decimal import Decimal
from app.domains.financiero.services.tesoreria_service import TesoreriaService
from app.domains.financiero.models.tesoreria.apunte import TipoApunte

@pytest.mark.asyncio
async def test_crear_cuenta_bancaria(session):
    tesoreria = TesoreriaService(session)

    cuenta = await tesoreria.crear_cuenta_bancaria(
        nombre="Test Cuenta",
        iban="ES9121000418450200051332",
        banco="Banco Test",
    )

    assert cuenta.nombre == "Test Cuenta"
    assert cuenta.saldo_actual == Decimal("0.00")
    assert cuenta.activo == True

@pytest.mark.asyncio
async def test_registrar_apunte(session, estado_apunte_id):
    tesoreria = TesoreriaService(session)

    cuenta = await tesoreria.crear_cuenta_bancaria(
        nombre="Test Cuenta",
        iban="ES9121000418450200051332",
        banco="Banco Test",
    )

    apunte = await tesoreria.registrar_apunte(
        cuenta_id=cuenta.id,
        tipo=TipoApunte.INGRESO,
        importe=Decimal("100.00"),
        fecha=date.today(),
        concepto="Test ingreso",
        estado_id=estado_apunte_id,
    )

    assert apunte.importe == Decimal("100.00")
    assert apunte.tipo == TipoApunte.INGRESO

    cuenta_actualizada = await tesoreria.obtener_cuenta(cuenta.id)
    assert cuenta_actualizada.saldo_actual == Decimal("100.00")
```

## Troubleshooting

### Error: "Cuenta bancaria no encontrada"

```python
cuenta = await tesoreria.obtener_cuenta(cuenta_id)
if not cuenta:
    print(f"Cuenta {cuenta_id} no encontrada")
```

### Error: "El asiento no cuadra"

Verificar que `sum(debe) == sum(haber)` en las líneas antes de llamar a `crear_asiento()`.

### Error: versión COMPLETA requerida

`ContabilidadService` lanza `NotImplementedError` si `FINANCIERO_CONFIG["version"]` no es `"COMPLETA"`.
Activar en `core/feature_flags.py`:

```python
FINANCIERO_CONFIG = {
    "version": "COMPLETA",
    ...
}
```

## Documentación Adicional

- [Diseño Técnico](./DISEÑO_TESORERIA_CONTABILIDAD.md)
- [Plan de desarrollo](./PLAN_DESARROLLO.md)
- [PCESFL 2013](https://www.icac.hacienda.gob.es/)
- [Guía AEF](https://abc.fundaciones.org/)

---

**Versión**: 1.1  
**Última actualización**: 2 de mayo de 2026
