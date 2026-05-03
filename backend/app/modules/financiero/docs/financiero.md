# Módulo Financiero — Diseño Arquitectural

Ver también: [`backend/app/domains/financiero/FINANCIERO.md`](../../backend/app/domains/financiero/FINANCIERO.md)

## Visión general

El módulo financiero es un **dominio plugable** con dos versiones activadas mediante feature flags:

| Versión | Para | Contabilidad |
|---|---|---|
| `SIMPLE` | Asociaciones | Movimientos de caja (ingresos/gastos) |
| `COMPLETA` | Fundaciones | Partida doble + Plan de cuentas PCESFL 2013 |

## Subdominios

| Subdominio | Responsabilidad | Versión |
|---|---|---|
| `cuotas` | Obligaciones de pago de socios | Ambas |
| `donaciones` | Aportaciones voluntarias | Ambas |
| `remesas` | Cobros SEPA en lote | Ambas |
| `cobro` | Integración con pasarelas externas | Ambas |
| `reclamaciones` | Gestión de impagos | Ambas |
| `presupuesto` | Planificación económica anual | Ambas |
| `tesoreria` | Cuentas bancarias y movimientos reales | Ambas |
| `contabilidad` | Partida doble, plan de cuentas PGC | Solo COMPLETA |

## Cadena de vida de un euro

```
CuotaAnual (obligación)
        │
        ├── vía SEPA ───► OrdenCobro → Remesa
        ├── vía pasarela ► Pago (cobro)
        └── vía manual ─────────────┤
                                  │
                          MovimientoTesoreria
                                  │
                  [SIMPLE] → fin
                  [COMPLETA] → AsientoContable (debe/haber)
```

## Feature flags

```python
# backend/app/domains/financiero/core/feature_flags.py
FINANCIERO_CONFIG = {
    "version": "SIMPLE",  # o "COMPLETA"
    "subdominios_activos": {
        "cuotas": True, "donaciones": True, "remesas": True,
        "cobro": True, "reclamaciones": True, "presupuesto": True,
        "tesoreria": True,
        "contabilidad": False,  # solo COMPLETA
    }
}
```

## Convenciones

- Importes: `Decimal` (nunca `float`)
- Fechas de negocio: `date`; auditoría: `datetime`
- Estados: FK a catálogo cuando el flujo depende de ellos
- Enums Python para valores con lógica fija (`TipoMovimientoTesoreria`, `TipoAsientoContable`...)
- GraphQL: strawchemy genera tipos automáticamente desde los modelos SQLAlchemy
