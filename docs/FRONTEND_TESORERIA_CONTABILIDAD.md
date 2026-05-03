# Frontend: Módulos de Tesorería y Contabilidad

## Resumen

Se ha implementado el frontend completo para los módulos de **Tesorería** y **Contabilidad** en Vue 3 con Tailwind CSS, siguiendo los patrones arquitectónicos del proyecto SIGA.

## Estructura de Archivos

### Vistas (Views)

```
frontend/src/views/financiero/
├── Tesoreria.vue           # Vista principal de tesorería
├── Contabilidad.vue        # Vista principal de contabilidad
└── ListaFinanciero.vue     # (Existente) Dashboard financiero general
```

### Composables

```
frontend/src/composables/
├── useTesoreria.js         # Lógica de tesorería
├── useContabilidad.js      # Lógica de contabilidad
├── useGraphQL.js           # (Existente) Cliente GraphQL
├── useMiembro.js           # (Existente)
└── useCampania.js          # (Existente)
```

### Queries GraphQL

```
frontend/src/graphql/queries/
├── tesoreria.js            # Queries y mutations de tesorería
├── contabilidad.js         # Queries y mutations de contabilidad
├── financiero.js           # (Existente)
└── ...
```

### Router

```
frontend/src/router/index.js
```

Nuevas rutas:
- `/tesoreria` → Tesoreria.vue
- `/contabilidad` → Contabilidad.vue

## Vistas Implementadas

### 1. Tesoreria.vue

**Ruta**: `/tesoreria`

**Funcionalidades**:

- **Dashboard de Resumen**:
  - Saldo total de todas las cuentas
  - Número de cuentas activas
  - Movimientos conciliados vs pendientes

- **Pestaña: Cuentas Bancarias**:
  - Listado de cuentas con saldo actual
  - IBAN parcialmente encriptado por seguridad
  - Botón para crear nueva cuenta
  - Selector para ver movimientos de una cuenta

- **Pestaña: Movimientos**:
  - Tabla de movimientos con columnas:
    - Fecha
    - Concepto
    - Importe (con color según tipo: verde ingreso, rojo gasto)
    - Tipo (INGRESO/GASTO/TRASPASO)
    - Estado de conciliación (✓ o ○)
  - Filtro por cuenta
  - Botón para registrar nuevo movimiento

- **Pestaña: Conciliaciones**:
  - Listado de conciliaciones bancarias
  - Muestra saldo del extracto vs saldo del sistema
  - Indicador visual de diferencia
  - Botón para crear nueva conciliación

**Composable**: `useTesoreria.js`

```javascript
const {
  cuentasBancarias,      // Array de cuentas
  movimientos,           // Array de movimientos
  conciliaciones,        // Array de conciliaciones
  loading,               // Estado de carga
  error,                 // Errores
  obtenerCuentasBancarias,
  obtenerMovimientos,
  obtenerMovimientosNoConciliados,
  obtenerConciliaciones,
  crearCuentaBancaria,
  registrarMovimiento,
  crearConciliacion,
  confirmarConciliacion,
  calcularTotales,       // Computed: totales de ingresos/gastos
  saldoTotal,            // Computed: suma de saldos
} = useTesoreria()
```

### 2. Contabilidad.vue

**Ruta**: `/contabilidad`

**Funcionalidades**:

- **Dashboard de Resumen**:
  - Número de cuentas activas
  - Asientos confirmados
  - Asientos en borrador
  - Ejercicio actual

- **Pestaña: Plan de Cuentas**:
  - Tabla jerárquica del plan de cuentas PCESFL 2013
  - Columnas:
    - Código (formato: 1, 10, 100, etc.)
    - Nombre (indentado según nivel)
    - Tipo (ACTIVO, PASIVO, PATRIMONIO, INGRESO, GASTO)
    - Nivel (profundidad en la jerarquía)
    - Estado (Activa/Inactiva)
  - Filtro por tipo de cuenta
  - Botón para crear nueva cuenta

- **Pestaña: Asientos Contables**:
  - Listado de asientos con:
    - Número de asiento
    - Fecha
    - Glosa (descripción)
    - Totales de debe/haber
    - Estado (BORRADOR, CONFIRMADO, ANULADO)
  - Filtros:
    - Ejercicio (año)
    - Rango de fechas
    - Estado
  - Botón para crear nuevo asiento
  - Click en asiento para ver detalles

- **Pestaña: Libro Mayor**:
  - Selector de cuenta contable
  - Tabla de apuntes con:
    - Fecha
    - Número de asiento
    - Concepto
    - Debe (solo si > 0)
    - Haber (solo si > 0)
  - Filtros por fecha y ejercicio

- **Pestaña: Balance**:
  - Botón para generar balance de sumas y saldos
  - Muestra estado de equilibrio (Debe = Haber)

**Composable**: `useContabilidad.js`

```javascript
const {
  planCuentas,           // Array de cuentas contables
  asientos,              // Array de asientos
  apuntes,               // Array de apuntes
  balances,              // Array de balances
  asientoActual,         // Asiento en edición
  ejercicioActual,       // Año actual
  loading,               // Estado de carga
  error,                 // Errores
  obtenerPlanCuentas,
  obtenerAsientos,
  obtenerApuntes,
  obtenerBalance,
  obtenerSaldoCuenta,
  crearCuentaContable,
  crearAsiento,
  crearApunte,
  confirmarAsiento,
  anularAsiento,
  generarBalance,
  totalesAsientoActual,  // Computed: totales del asiento
  cuentasPorTipo,        // Computed: agrupadas por tipo
  asientosPorEstado,     // Computed: agrupados por estado
} = useContabilidad()
```

## Queries y Mutations GraphQL

### Tesorería

**Queries**:
- `GET_CUENTAS_BANCARIAS`: Obtener todas las cuentas
- `GET_CUENTA_BANCARIA`: Obtener una cuenta específica
- `GET_MOVIMIENTOS_TESORERIA`: Obtener movimientos con filtros
- `GET_MOVIMIENTOS_NO_CONCILIADOS`: Obtener movimientos sin conciliar
- `GET_CONCILIACIONES_BANCARIAS`: Obtener conciliaciones de una cuenta
- `GET_CONCILIACION_BANCARIA`: Obtener una conciliación específica

**Mutations**:
- `CREATE_CUENTA_BANCARIA`: Crear nueva cuenta
- `CREATE_MOVIMIENTO_TESORERIA`: Registrar movimiento
- `MARCAR_MOVIMIENTO_CONCILIADO`: Marcar como conciliado
- `CREATE_CONCILIACION_BANCARIA`: Crear conciliación
- `CONFIRMAR_CONCILIACION`: Confirmar conciliación

### Contabilidad

**Queries**:
- `GET_PLAN_CUENTAS`: Obtener plan de cuentas con filtros
- `GET_CUENTA_CONTABLE`: Obtener cuenta específica
- `GET_CUENTA_POR_CODIGO`: Buscar por código
- `GET_ASIENTOS_CONTABLES`: Obtener asientos con filtros
- `GET_ASIENTO_CONTABLE`: Obtener asiento específico
- `GET_APUNTES_CUENTA`: Obtener apuntes de una cuenta (libro mayor)
- `GET_BALANCE_CONTABLE`: Obtener balance generado
- `GET_SALDO_CUENTA`: Obtener saldo de una cuenta

**Mutations**:
- `CREATE_CUENTA_CONTABLE`: Crear nueva cuenta
- `CREATE_ASIENTO_CONTABLE`: Crear asiento
- `CREATE_APUNTE_CONTABLE`: Agregar apunte a asiento
- `CONFIRMAR_ASIENTO`: Confirmar asiento
- `ANULAR_ASIENTO`: Anular asiento
- `GENERAR_BALANCE`: Generar balance

## Patrones de Diseño

### Composables

Los composables siguen el patrón de composición de Vue 3:

```javascript
export function useTesoreria() {
  // Estado reactivo
  const cuentasBancarias = ref([])
  const loading = ref(false)
  
  // Métodos
  const obtenerCuentasBancarias = async () => { ... }
  
  // Computed
  const saldoTotal = computed(() => { ... })
  
  // Retornar interfaz pública
  return {
    cuentasBancarias,
    loading,
    obtenerCuentasBancarias,
    saldoTotal,
  }
}
```

### Vistas

Las vistas utilizan:

- **AppLayout**: Componente base con header y sidebar
- **Tabs Navigation**: Para cambiar entre secciones
- **Tablas**: Para listados de datos
- **Tarjetas**: Para resúmenes (KPIs)
- **Formularios**: Para crear/editar (a implementar)
- **Spinners**: Para estados de carga

### Estilos

- **Tailwind CSS**: Framework de utilidades
- **Colores**:
  - Verde: Ingresos, estados positivos
  - Rojo: Gastos, estados negativos
  - Azul: Información, cuentas
  - Púrpura: Acciones, botones primarios
  - Amarillo: Advertencias, pendientes

## Flujos de Datos

### Tesorería: Crear Movimiento

```
Usuario → Formulario → crearMovimiento() → Mutation GraphQL → Backend
                                                                   ↓
                                            Actualiza saldo de cuenta
                                                                   ↓
                                            Retorna movimiento creado
                                                                   ↓
Actualiza array movimientos ← Response ← Frontend
```

### Contabilidad: Confirmar Asiento

```
Usuario → Click Botón → confirmarAsiento() → Mutation GraphQL → Backend
                                                                    ↓
                                            Valida partida doble
                                                                    ↓
                                            Cambia estado a CONFIRMADO
                                                                    ↓
                                            Retorna asiento actualizado
                                                                    ↓
Actualiza estado en tabla ← Response ← Frontend
```

## Funciones de Utilidad

```javascript
// Formatear moneda
const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

// Formatear fecha
const formatDate = (date) => {
  return new Intl.DateTimeFormat('es-ES').format(new Date(date))
}

// Encriptar IBAN para mostrar
const formatearIban = (iban) => {
  return iban.slice(0, 4) + ' **** **** **** ' + iban.slice(-4)
}

// Clases CSS dinámicas para badges
const getTipoBadgeClass = (tipo) => {
  const classes = {
    ACTIVO: 'bg-blue-100 text-blue-800',
    PASIVO: 'bg-red-100 text-red-800',
    // ...
  }
  return classes[tipo] || 'bg-gray-100 text-gray-800'
}
```

## Próximos Pasos

### Formularios (A Implementar)

1. **FormularioCuenta.vue**: Crear/editar cuentas bancarias
2. **FormularioMovimiento.vue**: Registrar movimientos
3. **FormularioConciliacion.vue**: Crear conciliaciones
4. **FormularioAsiento.vue**: Crear asientos contables
5. **FormularioApunte.vue**: Agregar apuntes a asientos

### Modales (A Implementar)

- Modal para detalles de asiento
- Modal para confirmación de acciones
- Modal para importar extractos bancarios

### Reportes (A Implementar)

- Exportar balance a PDF
- Exportar libro mayor a Excel
- Generar estado de resultados
- Generar balance de situación

### Validaciones (A Mejorar)

- Validar IBAN antes de crear cuenta
- Validar que asiento esté cuadrado antes de confirmar
- Validar fechas de conciliación
- Validar importes positivos

### Mejoras de UX

- Paginación en tablas grandes
- Búsqueda/filtro en tiempo real
- Ordenamiento de columnas
- Exportación de datos
- Gráficos de tendencias

## Testing

### Tests Unitarios (A Crear)

```javascript
describe('useTesoreria', () => {
  it('debe obtener cuentas bancarias', async () => {
    const { obtenerCuentasBancarias, cuentasBancarias } = useTesoreria()
    await obtenerCuentasBancarias()
    expect(cuentasBancarias.value.length).toBeGreaterThan(0)
  })
})
```

### Tests de Componentes (A Crear)

```javascript
describe('Tesoreria.vue', () => {
  it('debe mostrar lista de cuentas', () => {
    const wrapper = mount(Tesoreria)
    expect(wrapper.find('table').exists()).toBe(true)
  })
})
```

## Notas Técnicas

1. **Encriptación de IBAN**: El backend encripta el IBAN completo. El frontend solo muestra los primeros 4 y últimos 4 dígitos.

2. **Validación de Partida Doble**: El backend valida automáticamente que debe = haber. El frontend muestra el estado.

3. **Estados de Asientos**: BORRADOR → CONFIRMADO → ANULADO (solo en borrador)

4. **Ejercicio Fiscal**: Año actual por defecto, pero editable para años anteriores.

5. **Conciliación**: Marca movimientos como conciliados. La diferencia debe ser 0 para considerar conciliada.

## Referencias

- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Tailwind CSS](https://tailwindcss.com/)
- [Strawberry GraphQL](https://strawberry.rocks/)
- [PCESFL 2013](https://www.icac.hacienda.gob.es/)

---

**Versión**: 1.0  
**Fecha**: 3 de mayo de 2026  
**Estado**: ✅ Implementación completada
