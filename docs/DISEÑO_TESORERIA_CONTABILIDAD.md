# Diseño de Módulos: Tesorería y Contabilidad (Actualizado)

Este diseño incorpora los requisitos de la **Guía AEF 2022** y el **Plan de Contabilidad de Entidades Sin Fines Lucrativos (PCESFL 2013)**.

## 1. Módulo de Tesorería

### Modelos de Datos

#### `CuentaBancaria`
- `id`: UUID (PK)
- `nombre`: String
- `iban`: String (Encriptado)
- `bic_swift`: String
- `banco_nombre`: String
- `saldo_actual`: Numeric(14, 2)
- `agrupacion_id`: UUID (FK a agrupaciones)
- `activa`: Boolean

#### `MovimientoTesoreria`
- `id`: UUID (PK)
- `cuenta_id`: UUID (FK a CuentaBancaria)
- `fecha`: Date
- `importe`: Numeric(14, 2)
- `tipo`: Enum (INGRESO, GASTO, TRASPASO)
- `concepto`: String
- `referencia_externa`: String
- `entidad_origen_tipo`: String ('cuota', 'donacion', 'actividad')
- `entidad_origen_id`: UUID
- `conciliado`: Boolean
- `asiento_id`: UUID (FK a AsientoContable)

## 2. Módulo de Contabilidad (PCESFL 2013)

### Modelos de Datos

#### `CuentaContable`
- `id`: UUID (PK)
- `codigo`: String (ej: "57200001")
- `nombre`: String
- `nivel`: Integer
- `padre_id`: UUID (FK a CuentaContable)
- `tipo`: Enum (ACTIVO, PASIVO, PATRIMONIO, INGRESO, GASTO)
- `permite_asiento`: Boolean
- `es_dotacion`: Boolean (Para identificar elementos de la dotación fundacional)

#### `AsientoContable`
- `id`: UUID (PK)
- `ejercicio`: Integer
- `numero_asiento`: Integer
- `fecha`: Date
- `glosa`: String
- `estado`: Enum (BORRADOR, CONFIRMADO, ANULADO)
- `tipo_asiento`: Enum (APERTURA, GESTION, REGULARIZACION, CIERRE)

#### `ApunteContable`
- `id`: UUID (PK)
- `asiento_id`: UUID (FK a AsientoContable)
- `cuenta_id`: UUID (FK a CuentaContable)
- `debe`: Numeric(14, 2)
- `haber`: Numeric(14, 2)
- `concepto`: String
- `actividad_id`: UUID (FK a Actividad, para seguimiento de fines propios)

## 3. Requisitos Específicos ESFL (Guía AEF)

1. **Destino de Rentas**: Los asientos deben permitir identificar gastos destinados a fines propios vs gastos de administración.
2. **Inventario**: El sistema debe generar el inventario detallado (Descripción, Fecha Adquisición, Valor, Amortización).
3. **Plan de Actuación**: Integración con el módulo de presupuestos para comparar ejecución real vs planificada.
4. **Memoria**: Generación de datos para los puntos 1, 2, 3 y 4 de la memoria (Actividades, Destino de Rentas, Plan de Actuación, Inventario).

## 4. Implementación

- **Backend**: SQLAlchemy 2.0 Async, Strawberry GraphQL.
- **Frontend**: Vue 3, Tailwind CSS.
- **Servicios**: `TesoreriaService` y `ContabilidadService` para lógica de negocio (partida doble, validación de saldos).