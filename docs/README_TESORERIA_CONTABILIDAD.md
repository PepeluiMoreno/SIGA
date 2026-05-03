# Módulos de Tesorería y Contabilidad - SIGA

## Resumen Ejecutivo

Se han implementado dos módulos completos para la gestión financiera de organizaciones sin fines de lucro, cumpliendo con la normativa española (PCESFL 2013 y Guía AEF 2022).

### ✅ Módulo de Tesorería

**Objetivo**: Gestionar la liquidez de la organización mediante cuentas bancarias, movimientos de efectivo y conciliaciones.

**Características principales:**

- Gestión de múltiples cuentas bancarias con IBAN encriptado
- Registro de movimientos (ingresos, gastos, traspasos)
- Conciliación automática de extractos bancarios
- Vinculación de movimientos a entidades origen (cuotas, donaciones, etc.)
- Seguimiento de saldos en tiempo real

**Modelos:**

- `CuentaBancaria`: Cuentas bancarias de la organización
- `MovimientoTesoreria`: Movimientos de efectivo
- `ConciliacionBancaria`: Registros de conciliación

**Servicio:**

- `TesoreriaService`: Lógica de negocio para tesorería

### ✅ Módulo de Contabilidad

**Objetivo**: Gestionar la contabilidad de la organización según el PCESFL 2013, con soporte para partida doble y generación de reportes.

**Características principales:**

- Plan de cuentas completo según PCESFL 2013
- Asientos contables con validación automática de partida doble
- Seguimiento de fines propios vs gastos de administración
- Generación de balances de sumas y saldos
- Identificación de elementos de dotación fundacional

**Modelos:**

- `CuentaContable`: Plan de cuentas (jerarquía de cuentas)
- `AsientoContable`: Asientos contables
- `ApunteContable`: Líneas de asientos (partida doble)
- `BalanceContable`: Balances generados

**Servicio:**

- `ContabilidadService`: Lógica de negocio para contabilidad

### 📊 Estructura de Archivos

```
backend/app/domains/financiero/
├── models/
│   ├── __init__.py
│   ├── tesoreria.py              # Modelos de tesorería
│   ├── contabilidad.py           # Modelos de contabilidad
│   ├── cuotas.py                 # (Existente)
│   ├── donaciones.py             # (Existente)
│   ├── remesas.py                # (Existente)
│   └── presupuesto.py            # (Existente)
├── services/
│   ├── __init__.py
│   ├── tesoreria_service.py      # Servicio de tesorería
│   └── contabilidad_service.py   # Servicio de contabilidad
└── ...

backend/app/scripts/seeding/
└── plan_cuentas_esfl.py          # Datos iniciales del plan de cuentas

docs/
├── DISEÑO_TESORERIA_CONTABILIDAD.md      # Diseño técnico
├── GUIA_TESORERIA_CONTABILIDAD.md        # Guía de uso completa
├── INSTALACION_TESORERIA_CONTABILIDAD.md # Guía de instalación
└── README_TESORERIA_CONTABILIDAD.md      # Este archivo
```

## 🚀 Inicio Rápido

### 1. Crear una Cuenta Bancaria

```python
from app.domains.financiero.services import TesoreriaService

tesoreria = TesoreriaService(session)

cuenta = await tesoreria.crear_cuenta_bancaria(
    nombre="Cuenta Operativa",
    iban="ES9121000418450200051332",
    banco_nombre="Banco Santander",
)
```

### 2. Registrar un Movimiento

```python
from datetime import date
from decimal import Decimal
from app.domains.financiero.models import TipoMovimientoTesoreria

movimiento = await tesoreria.registrar_movimiento(
    cuenta_id=cuenta.id,
    fecha=date.today(),
    importe=Decimal("100.00"),
    tipo=TipoMovimientoTesoreria.INGRESO,
    concepto="Cuota anual miembro",
)
```

### 3. Crear un Asiento Contable

```python
from app.domains.financiero.services import ContabilidadService
from app.domains.financiero.models import TipoAsientoContable
from decimal import Decimal

contabilidad = ContabilidadService(session)

asiento = await contabilidad.crear_asiento(
    ejercicio=2026,
    numero_asiento=1,
    fecha=date.today(),
    glosa="Ingreso cuota anual",
    tipo_asiento=TipoAsientoContable.GESTION,
)

# Crear apuntes (partida doble)
await contabilidad.crear_apunte(
    asiento_id=asiento.id,
    cuenta_id=cuenta_101_id,  # Bancos c/c
    debe=Decimal("100.00"),
)

await contabilidad.crear_apunte(
    asiento_id=asiento.id,
    cuenta_id=cuenta_400_id,  # Cuotas de miembros
    haber=Decimal("100.00"),
)

# Confirmar
await contabilidad.confirmar_asiento(asiento.id)
```

## 📋 Requisitos Normativos

### Cumplimiento PCESFL 2013

✅ Plan de cuentas adaptado a entidades sin fines de lucro  
✅ Partida doble con validación automática  
✅ Tipos de asientos (Apertura, Gestión, Regularización, Cierre)  
✅ Estados de asientos (Borrador, Confirmado, Anulado)  
✅ Identificación de elementos de dotación fundacional  

### Cumplimiento Guía AEF 2022

✅ Libro Diario (asientos contables)  
✅ Libro Mayor (apuntes por cuenta)  
✅ Balance de Sumas y Saldos  
✅ Destino de Rentas (seguimiento de fines propios vs administración)  
✅ Inventario (extensible a través de modelos de inmovilizado)  
✅ Plan de Actuación (integración con presupuestos)  

## 🔗 Integración con Otros Módulos

### Automatización: Cuota → Tesorería → Contabilidad

Cuando se marca una cuota como **COBRADA**:

1. Se crea automáticamente un `MovimientoTesoreria` (INGRESO)
2. Se crea un `AsientoContable` con partida doble:
   - DEBE: Cuenta 101 (Bancos c/c)
   - HABER: Cuenta 400 (Cuotas de miembros)

### Automatización: Donación → Tesorería → Contabilidad

Similar a cuotas, pero con:

- DEBE: Cuenta 101 (Bancos c/c)
- HABER: Cuenta 410 (Donaciones)

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [GUIA_TESORERIA_CONTABILIDAD.md](./GUIA_TESORERIA_CONTABILIDAD.md) | Guía completa de uso con ejemplos |
| [INSTALACION_TESORERIA_CONTABILIDAD.md](./INSTALACION_TESORERIA_CONTABILIDAD.md) | Guía de instalación y configuración |
| [DISEÑO_TESORERIA_CONTABILIDAD.md](./DISEÑO_TESORERIA_CONTABILIDAD.md) | Diseño técnico y arquitectura |

## 🛠️ Próximos Pasos

1. **GraphQL API**: Generar tipos y mutaciones para exponer servicios
2. **Frontend**: Crear vistas Vue 3 para tesorería y contabilidad
3. **Reportes**: Implementar generación de:
   - Balance de Situación
   - Cuenta de Pérdidas y Ganancias (PyG)
   - Libro Diario
   - Libro Mayor
4. **Importación**: Soporte para importar extractos bancarios (Norma 43, SWIFT, Excel)
5. **Auditoría**: Completar campos de trazabilidad (creado_por, modificado_por, etc.)
6. **Validaciones**: Agregar más reglas de negocio según necesidades

## 📞 Soporte

Para preguntas o problemas:

1. Consultar la [Guía de Uso](./GUIA_TESORERIA_CONTABILIDAD.md)
2. Revisar [Troubleshooting](./INSTALACION_TESORERIA_CONTABILIDAD.md#troubleshooting)
3. Crear un issue en el repositorio

## 📄 Licencia

Este código forma parte del proyecto SIGA y sigue la licencia del proyecto.

---

**Versión**: 1.0  
**Fecha**: 2 de mayo de 2026  
**Autor**: Manus AI Agent  
**Estado**: ✅ Implementación completada
