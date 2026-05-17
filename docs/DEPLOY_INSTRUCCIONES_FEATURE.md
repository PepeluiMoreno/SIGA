# Instrucciones de despliegue — Módulo Financiero SIGA

## 1. Subir el commit a GitHub

```bash
cd /ruta/al/proyecto/SIGA
git remote set-url origin https://github.com/PepeluiMoreno/SIGA.git
git push origin feature/tesoreria-contabilidad
```

O aplicar el patch adjunto:
```bash
git am financiero_produccion.patch
git push origin feature/tesoreria-contabilidad
```

## 2. Migración de base de datos (una sola vez)

```bash
cd backend
alembic upgrade a9f1b2c3d4e5
```

Esto crea las 9 tablas nuevas:
- cuentas_bancarias
- apuntes_caja
- extractos_bancarios
- conciliaciones
- conciliaciones_bancarias
- cuentas_contables
- asientos_contables
- apuntes_contables
- balances_contables

## 3. Seed del plan de cuentas PCESFL 2013

Ejecutar una sola vez tras la migración. Añadir al script de inicialización
o ejecutar directamente:

```python
# En una sesión async de Python / FastAPI startup:
from app.scripts.seeding.plan_cuentas_esfl import cargar_plan_cuentas_esfl
from app.core.database import AsyncSessionLocal

async with AsyncSessionLocal() as session:
    await cargar_plan_cuentas_esfl(session)
```

O añadir la llamada al `app/scripts/inicializar_sistema.py`:
```python
from app.scripts.seeding.plan_cuentas_esfl import cargar_plan_cuentas_esfl
await cargar_plan_cuentas_esfl(session)
```

## 4. Ejecutar los tests

```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/financiero/ -v
```

## 5. Rutas disponibles en el frontend

- `/tesoreria` — Gestión de cuentas bancarias, movimientos y conciliaciones
- `/contabilidad` — Plan de cuentas PCESFL 2013, asientos y balances

## 6. Queries GraphQL nuevas

### Tesorería
- `cuentasBancarias` — lista con filtros
- `apuntesCaja` — movimientos con filtros
- `extractosBancarios` — líneas de extracto
- `conciliacionesBancarias` — cierres de período

### Contabilidad
- `cuentasContables` — plan de cuentas
- `asientosContables` — libro diario
- `apuntesContables` — libro mayor
- `balancesContables` — balances generados

### Mutations de negocio
- `registrarApunteCaja` — registra movimiento + genera asiento automático
- `marcarApunteConciliado`
- `conciliarApunteConExtracto`
- `confirmarConciliacionPeriodo`
- `confirmarAsientoContable`
- `anularAsientoContable`
- `generarBalanceContable`

## 7. Flujo automático (versión COMPLETA)

Al registrar un apunte de caja vía `registrarApunteCaja`:
1. Se actualiza el saldo de la cuenta bancaria
2. RegistroContable mapea el origen/tipo a cuentas PCESFL:
   - Cuota cobrada → DEBE 572 (Bancos) / HABER 721 (Cuotas socios)
   - Donación → DEBE 572 / HABER 730 (Donaciones)
   - Remesa → DEBE 572 / HABER 430
   - Gasto manual → DEBE 629 / HABER 572
3. Se crea y confirma el asiento automáticamente
4. El apunte queda vinculado al asiento via `asiento_id`

## Archivos clave modificados

| Archivo | Cambio |
|---------|--------|
| `alembic/versions/a9f1b2c3d4e5_...py` | Nueva — migración completa |
| `domains/financiero/core/feature_flags.py` | version=COMPLETA, contabilidad=True |
| `domains/financiero/models/tesoreria/` | Modelos canónicos + alias |
| `domains/financiero/models/contabilidad/` | + BalanceContable |
| `domains/financiero/services/tesoreria_service.py` | Reescrito completo |
| `domains/financiero/services/contabilidad_service.py` | Bug double-join corregido |
| `domains/financiero/services/registro_contable.py` | Nuevo — asientos automáticos |
| `graphql/financiero_mutations.py` | Reescrito con resolvers reales |
| `graphql/mutations.py` | + FinancieroMutation + CRUD strawchemy |
| `graphql/schema_simple.py` | + 8 queries tesorería/contabilidad |
| `graphql/types_auto.py` | + 9 tipos GraphQL |
| `graphql/inputs_auto.py` | + Create/Update/Filter inputs |
| `app/domains/cobro/__init__.py` | Fix typo (coma → punto) |
| `frontend/src/views/financiero/Tesoreria.vue` | Completo con modales |
| `frontend/src/views/financiero/Contabilidad.vue` | Completo con modales |
| `frontend/src/composables/useTesoreria.js` | Actualizado |
| `frontend/src/composables/useContabilidad.js` | Actualizado |
| `tests/financiero/test_tesoreria_service.py` | 8 tests unitarios |
| `tests/financiero/test_contabilidad_service.py` | 9 tests unitarios |
