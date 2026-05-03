# Plan de Reestructuración de Módulos — SIGA

> Documento de planificación. Fuente de verdad para la migración de la estructura anterior
> de dominios hacia la nueva arquitectura alineada con los módulos funcionales del sidebar.

---

## 1. Motivación

La estructura anterior era el resultado de varias sesiones de desarrollo con enfoques
distintos. Había dominios duplicados (`actividad` / `actividades`), dominios huérfanos sin conectar
al `__init__.py` (`eventos`, `organizaciones`), archivos legacy coexistiendo con subcarpetas nuevas
dentro del mismo directorio (`financiero`), y una separación de responsabilidades que no se
correspondía con la navegación real de la aplicación.

El objetivo es una estructura donde **cada módulo de primer nivel se corresponda exactamente
con una entrada del menú lateral de la UI**, y donde la responsabilidad de cada módulo sea
clara y no se solape con otros.

---

## 2. Estructura objetivo (implementada)

```
backend/app/modules/
│
├── acceso/                          ← MENÚ: Control de Acceso
│   ├── __init__.py
│   ├── docs/
│   ├── models/
│   │   ├── transaccion.py           # Transaccion (catálogo de operaciones RBAC)
│   │   ├── rol.py                   # Rol, TipoRol
│   │   ├── rol_transaccion.py       # RolTransaccion (M2M rol↔transaccion)
│   │   ├── auditoria.py             # LogAuditoria, TipoAccion
│   │   ├── usuario.py               # Usuario, UsuarioRol
│   │   └── seguridad.py             # Sesion, HistorialSeguridad, IPBloqueada, IntentoAcceso
│   └── services/
│
├── membresia/                       ← MENÚ: Membresía
│   ├── __init__.py
│   ├── docs/
│   ├── models/
│   │   ├── miembro.py               # Miembro, TipoMiembro
│   │   ├── estado_miembro.py        # EstadoMiembro
│   │   ├── motivo_baja.py           # MotivoBaja
│   │   ├── tipo_cargo.py            # TipoCargo
│   │   ├── skill.py                 # Skill, MiembroSkill
│   │   ├── disponibilidad.py        # FranjaDisponibilidad
│   │   ├── historial_agrupacion.py  # HistorialAgrupacion
│   │   ├── traslados/               # SolicitudTraslado, EstadoTraslado
│   │   └── voluntariado.py          # Competencias, formación, documentos
│   └── services/
│
├── actividades/                     ← MENÚ: Actividades
│   ├── __init__.py
│   ├── docs/
│   ├── models/
│   │   ├── catalogos.py             # TipoActividad, EstadoPropuesta, TipoRecurso, TipoKPI
│   │   ├── actividad.py             # Actividad, propuestas, tareas, KPIs
│   │   ├── campana.py               # Campania, TipoCampania, participantes, firmantes
│   │   ├── grupo.py                 # GrupoTrabajo, roles, reuniones
│   │   └── evento.py                # Evento, TipoEvento, EstadoEvento, participantes
│   └── services/
│
├── economico/                       ← MENÚ: Económico
│   ├── __init__.py
│   ├── docs/
│   │   ├── economico.md
│   │   ├── cobro.md
│   │   └── paypal.md
│   ├── core/
│   │   └── feature_flags.py         # SIMPLE / COMPLETA
│   ├── models/
│   │   ├── tesoreria.py             # CuentaBancaria, MovimientoTesoreria, ConciliacionBancaria
│   │   ├── contabilidad.py          # CuentaContable, AsientoContable, ApunteContable
│   │   ├── cuotas.py                # CuotaAnual, ImporteCuotaAnio, ModoIngreso
│   │   ├── donaciones.py            # Donacion, DonacionConcepto
│   │   ├── remesas.py               # Remesa, OrdenCobro
│   │   ├── presupuesto.py           # PlanificacionAnual, PartidaPresupuestaria
│   │   ├── cobro/                   # ProveedorPago, Pago, Suscripcion
│   │   └── reclamaciones/           # Reclamacion, AccionReclamacion
│   └── services/
│       ├── tesoreria_service.py
│       └── contabilidad_service.py
│
├── configuracion/                   ← MENÚ: Configuración
│   ├── __init__.py
│   ├── docs/
│   └── models/
│       ├── configuracion.py         # Configuracion, ReglaValidacionConfig, HistorialConfiguracion
│       ├── estados.py               # EstadoBase + todos los estados por dominio
│       ├── colaboraciones.py        # TipoAsociacion, Asociacion, EstadoConvenio, Convenio
│       └── organizacion.py          # TipoOrganizacion, Organizacion
│
└── core/                            ← TRANSVERSAL (sin entrada de menú)
    ├── __init__.py
    ├── models/                      # Shim de compatibilidad (re-exporta)
    ├── geografico/                  # Pais, Provincia, Municipio, Direccion, AgrupacionTerritorial
    └── comunicacion/                # TipoNotificacion, Notificacion, PreferenciaNotificacion
```

---

## 3. Mapa de migración (completado)

### 3.1 Módulos migrados

| Módulo origen | Destino | Estado |
|---|---|---|
| `administracion/` | `acceso/models/` (rol, transaccion, auditoria) | ✅ Migrado |
| `usuarios/` | `acceso/models/usuario.py` | ✅ Migrado |
| `core/models/seguridad.py` | `acceso/models/seguridad.py` | ✅ Migrado |
| `miembros/` | `membresia/models/` | ✅ Migrado |
| `voluntariado/` | `membresia/models/voluntariado.py` | ✅ Migrado |
| `campanas/` | `actividades/models/campana.py` | ✅ Migrado |
| `grupos/` | `actividades/models/grupo.py` | ✅ Migrado |
| `eventos/` | `actividades/models/evento.py` | ✅ Migrado |
| `actividad/` (legacy) | `actividades/models/` (catalogos + actividad) | ✅ Absorbido |
| `financiero_nuevo/` | `economico/` | ✅ Renombrado |
| `financiero/` | `economico/models/` (cuotas, donaciones, remesas, presupuesto, cobro, reclamaciones) | ✅ Migrado |
| `colaboraciones/` | `configuracion/models/colaboraciones.py` | ✅ Migrado |
| `organizaciones/` | `configuracion/models/organizacion.py` | ✅ Migrado |
| `core/models/configuracion.py` | `configuracion/models/configuracion.py` | ✅ Migrado |
| `core/models/estados.py` | `configuracion/models/estados.py` | ✅ Migrado |
| `geografico/` | `core/geografico/` | ✅ Migrado |
| `notificaciones/` | `core/comunicacion/` | ✅ Migrado |
| `cobro/` (legacy) | Absorbido por `economico/models/cobro/` | ✅ Eliminado |
| `analitico/` | Solo docs sin código útil | ✅ Eliminado |

---

## 4. Convenciones de la nueva estructura

- Cada módulo de primer nivel tiene: `__init__.py`, `docs/`, `models/`, `services/`
- Los modelos dentro de `models/` son archivos planos (no subcarpetas), salvo que el volumen lo justifique
- Todos los modelos heredan de `BaseModel` en `infrastructure/base_model.py`
- Los estados van a `configuracion/models/estados.py` como tablas, no como enums en columna
- Los enums Python solo para valores con lógica fija en el código (`TipoMovimientoTesoreria`, etc.)
- El `modules/__init__.py` importa exclusivamente desde los cinco módulos funcionales y `core`
- `core/models/__init__.py` actúa como shim de compatibilidad re-exportando desde los módulos reales

---

## 5. Estado de las fases

| Fase | Estado |
|---|---|
| Fase 1 — Estructura vacía de destino | ✅ Completada |
| Fase 2 — Migrar `economico` | ✅ Completada |
| Fase 3 — Migrar `acceso` | ✅ Completada |
| Fase 4 — Migrar `membresia` | ✅ Completada |
| Fase 5 — Migrar `actividades` | ✅ Completada |
| Fase 6 — Migrar `configuracion` | ✅ Completada |
| Fase 7 — Limpiar `core` | ✅ Completada |
| Fase 8 — Init principal | ✅ Completada |
| Fase 9 — Eliminar módulos legacy | ✅ Completada |
| Fase 10 — Corregir imports en graphql/scripts/models | ✅ Completada |
| Fase 11 — CI verde y deploy | ⬜ Pendiente |

---

## 6. Pendientes para próximas sesiones

- **CI**: ejecutar tests de importación y verificar que el backend arranca sin errores
- **Graphql types/inputs**: revisar si los types de strawchemy siguen siendo válidos con los nuevos paths
- **Geografico en core**: debate abierto — podría moverse a `membresia` si se considera más cohesivo con `AgrupacionTerritorial`
- **Scripts legacy**: `backend/scripts/seeding/*.py` y `backend/add_missing_agrupacion.py` aún usan `app.domains.*` — actualizar cuando se ejecuten de nuevo
- **Servicios**: crear servicios para `acceso`, `membresia`, `actividades`, `configuracion`
