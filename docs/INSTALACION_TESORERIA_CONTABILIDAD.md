# Guía de Instalación: Módulos de Tesorería y Contabilidad

## Requisitos Previos

- Python 3.10+
- SQLAlchemy 2.0+
- FastAPI
- Strawberry GraphQL
- PostgreSQL

## Migraciones

```bash
alembic revision --autogenerate -m "Add tesoreria and contabilidad models"
alembic upgrade head
```

## Cargar Plan de Cuentas Inicial

```python
from app.scripts.seeding.plan_cuentas_esfl import cargar_plan_cuentas_esfl
from app.core.database import get_session

async def seed_data():
    async with get_session() as session:
        await cargar_plan_cuentas_esfl(session)
```

## Nomenclatura de modelos

| Concepto | Clase Python | Tabla BD |
|---|---|---|
| Cuenta bancaria | `CuentaBancaria` | `cuentas_bancarias` |
| Movimiento de caja | `MovimientoTesoreria` | `movimientos_tesoreria` |
| Conciliación por período | `ConciliacionBancaria` | `conciliaciones_bancarias` |
| Cuenta contable | `CuentaContable` | `cuentas_contables` |
| Asiento contable | `AsientoContable` | `asientos_contables` |
| Línea de asiento | `ApunteContable` | `apuntes_contables` |
| Balance generado | `BalanceContable` | `balances_contables` |

## Variables de Entorno

```env
TESORERIA_ENCRIPTAR_IBAN=true
TESORERIA_ENCRIPTACION_KEY=tu_clave_secreta
CONTABILIDAD_EJERCICIO_DEFECTO=2026
CONTABILIDAD_VALIDAR_PARTIDA_DOBLE=true
```

## Troubleshooting

**Error: El asiento no cuadra** — verificar que `sum(debe) == sum(haber)` en las líneas.

**Error: versión COMPLETA requerida** — activar en `core/feature_flags.py`: `"version": "COMPLETA"`
