# Módulos de Tesorería y Contabilidad - SIGA

## Resumen Ejecutivo

Dos módulos para la gestión financiera de organizaciones sin fines de lucro, cumpliendo con la normativa española (PCESFL 2013 y Guía AEF 2022).

### ✅ Módulo de Tesorería

**Objetivo**: Gestionar la liquidez de la organización mediante cuentas bancarias, apuntes de caja y conciliaciones.

**Características principales:**

- Gestión de múltiples cuentas bancarias con IBAN encriptado
- Registro de apuntes de caja (ingresos, gastos, transferencias)
- Conciliación de extractos bancarios (automática y manual)
- Vinculación de apuntes a eventos de negocio origen (cuotas, donaciones, remesas, pagos)
- Seguimiento de saldos en tiempo real

**Modelos:**

- `CuentaBancaria` — cuentas bancarias de la organización
- `ApunteCaja` — movimientos reales de dinero en cuenta
- `ExtractoBancario` — líneas importadas de CSV/MT940
- `Conciliacion` — vinculación apunte ↔ extracto

**Servicio:** `TesoreriaService`

---

### ✅ Módulo de Contabilidad *(solo versión COMPLETA)*

**Objetivo**: Contabilidad de partida doble según el PCESFL 2013.

**Características principales:**

- Plan de cuentas completo según PCESFL 2013 (importable/exportable JSON)
- Asientos contables con validación automática de cuadre
- Seguimiento de fines propios vs gastos de administración
- Balance de comprobación por ejercicio
- Identificación de elementos de dotación fundacional

**Modelos:**

- `CuentaContable` — árbol jerárquico del plan de cuentas (grupo → subgrupo → cuenta → subcuenta)
- `AsientoContable` — cabecera del asiento (número, ejercicio, fecha, glosa)
- `ApunteContable` — líneas debe/haber del asiento

**Servicio:** `ContabilidadService`

---

## 📂 Estructura de Archivos

```
backend/app/domains/financiero/
├── FINANCIERO.md                          # Diseño arquitectural del dominio
├── core/
│   └── feature_flags.py                   # Versión SIMPLE / COMPLETA
├── models/
│   ├── cuotas/                            # Obligaciones de pago de socios
│   ├── donaciones/                        # Donaciones nominativas y anónimas
│   ├── remesas/                           # Cobros SEPA en lote
│   ├── cobro/                             # Pasarelas de pago externas
│   ├── reclamaciones/                     # Gestión de impagos
│   ├── presupuesto/                       # Planificación económica anual
│   ├── tesoreria/                         # Caja y movimientos reales
│   │   ├── cuenta_bancaria.py
│   │   ├── apunte.py                      # ApunteCaja, TipoApunte, OrigenApunte
│   │   └── conciliacion.py                # ExtractoBancario, Conciliacion
│   └── contabilidad/                      # Solo versión COMPLETA
│       ├── plan_cuentas.py                # CuentaContable
│       └── asiento.py                     # AsientoContable, ApunteContable
└── services/
    ├── base_service.py
    ├── tesoreria_service.py
    └── contabilidad_service.py            # Solo versión COMPLETA
```

---

## 🚀 Inicio Rápido

### 1. Crear una Cuenta Bancaria

```python
from app.domains.financiero.services.tesoreria_service import TesoreriaService

tesoreria = TesoreriaService(session)

cuenta = await tesoreria.crear_cuenta_bancaria(
    nombre="Cuenta Operativa",
    iban="ES9121000418450200051332",
    banco="Banco Santander",
)
```

### 2. Registrar un Apunte de Caja

```python
from datetime import date
from decimal import Decimal
from app.domains.financiero.models.tesoreria.apunte import TipoApunte, OrigenApunte

apunte = await tesoreria.registrar_apunte(
    cuenta_id=cuenta.id,
    tipo=TipoApunte.INGRESO,
    importe=Decimal("100.00"),
    fecha=date.today(),
    concepto="Cuota anual miembro",
    estado_id=estado_confirmado_id,
    origen=OrigenApunte.CUOTA,
    origen_id=cuota.id,
)
```

### 3. Crear un Asiento Contable *(versión COMPLETA)*

```python
from app.domains.financiero.services.contabilidad_service import ContabilidadService
from decimal import Decimal

contabilidad = ContabilidadService(session)

asiento = await contabilidad.crear_asiento(
    ejercicio=2026,
    fecha=date.today(),
    descripcion="Ingreso cuota anual",
    lineas=[
        {
            "cuenta_id": cuenta_57_id,    # Bancos c/c
            "importe_debe": Decimal("100.00"),
            "concepto": "Cobro cuota",
        },
        {
            "cuenta_id": cuenta_400_id,   # Cuotas de miembros
            "importe_haber": Decimal("100.00"),
            "concepto": "Cobro cuota",
        },
    ],
)
```

El servicio valida automáticamente que `sum(debe) == sum(haber)` antes de persistir.

---

## 📋 Requisitos Normativos

### Cumplimiento PCESFL 2013

✅ Plan de cuentas adaptado a entidades sin fines de lucro  
✅ Partida doble con validación automática de cuadre  
✅ Numeración automática de asientos por ejercicio  
✅ Identificación de elementos de dotación fundacional (`es_dotacion`)  
✅ Plan de cuentas importable/exportable en JSON  

### Cumplimiento Guía AEF 2022

✅ Libro Diario (asientos ordenados por fecha/número)  
✅ Libro Mayor (apuntes por cuenta)  
✅ Balance de comprobación (`balance_comprobacion()`)  
✅ Destino de Rentas (campo `actividad_id` en `ApunteContable`)  
✅ Plan de Actuación (integración con subdominio `presupuesto`)  

---

## 🔗 Integración con Otros Subdominios

### Cadena: Cuota → Tesorería → Contabilidad

Cuando se confirma el cobro de una `CuotaAnual`:

1. `TesoreriaService.registrar_apunte()` crea un `ApunteCaja` con `origen=OrigenApunte.CUOTA`
2. En versión COMPLETA, `ContabilidadService.crear_asiento()` genera el asiento:
   - DEBE: cuenta 57x (Bancos c/c)
   - HABER: cuenta 400 (Cuotas de miembros)

### Cadena: Donación → Tesorería → Contabilidad

Igual que cuotas, con `origen=OrigenApunte.DONACION`:

- DEBE: cuenta 57x (Bancos c/c)
- HABER: cuenta 410 (Donaciones)

### Conciliación Bancaria

```
ExtractoBancario (CSV/MT940)
        │
        ▼
  Conciliacion ↔ ApunteCaja
  metodo: AUTOMATICO | MANUAL
```

---

## 🛠️ Próximos Pasos

1. **Resolvers GraphQL** — exponer `TesoreriaService` y `ContabilidadService` vía strawchemy
2. **Frontend Vue 3** — vistas de cuentas, apuntes y asientos
3. **Reportes** — Balance de Situación, PyG, Libro Diario, Libro Mayor
4. **Importación extractos** — soporte Norma 43, SWIFT MT940, Excel
5. **Seeding** — script `plan_cuentas_esfl.py` con el plan completo PCESFL 2013
6. **Tests** — cobertura de servicios críticos

---

## 📚 Documentación

| Documento | Descripción |
|---|---|
| [FINANCIERO.md](../FINANCIERO.md) | Diseño arquitectural completo del dominio |
| [DISEÑO_TESORERIA_CONTABILIDAD.md](../../../../docs/DISEÑO_TESORERIA_CONTABILIDAD.md) | Diseño técnico y modelos |
| [INSTALACION_TESORERIA_CONTABILIDAD.md](../../../../docs/INSTALACION_TESORERIA_CONTABILIDAD.md) | Instalación y configuración |

---

## 📄 Licencia

Este código forma parte del proyecto SIGA y sigue la licencia del proyecto.
