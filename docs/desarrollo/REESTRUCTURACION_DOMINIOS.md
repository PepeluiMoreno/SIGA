# Plan de Reestructuración de Dominios — SIGA

> Documento de planificación. Fuente de verdad para la migración de la estructura actual
> de dominios hacia la nueva arquitectura alineada con los módulos funcionales del sidebar.

---

## 1. Motivación

La estructura actual de dominios es el resultado de varias sesiones de desarrollo con enfoques
distintos. Hay dominios duplicados (`actividad` / `actividades`), dominios huérfanos sin conectar
al `__init__.py` (`eventos`, `organizaciones`), archivos legacy coexistiendo con subcarpetas nuevas
dentro del mismo directorio (`financiero`), y una separación de responsabilidades que no se
corresponde con la navegación real de la aplicación.

El objetivo es una estructura donde **cada dominio de primer nivel se corresponda exactamente
con una entrada del menú lateral de la UI**, y donde la responsabilidad de cada módulo sea
clara y no se solape con otros.

---

## 2. Estructura objetivo

```
backend/app/domains/
│
├── acceso/                          ← MENÚ: Control de Acceso
│   ├── __init__.py
│   ├── docs/
│   ├── models/
│   │   ├── usuario.py               # Usuario, sesiones, historial seguridad
│   │   ├── rol.py                   # Rol, TipoRol, RolTransaccion
│   │   ├── transaccion.py           # Transaccion, permisos
│   │   └── auditoria.py             # LogAuditoria, TipoAccion
│   └── services/
│
├── membresia/                       ← MENÚ: Membresía
│   ├── __init__.py
│   ├── docs/
│   ├── models/
│   │   ├── miembro.py               # Miembro, TipoMiembro, EstadoMiembro, MotivoBaja
│   │   ├── agrupacion.py            # AgrupacionTerritorial
│   │   ├── traslado.py              # HistorialAgrupacion, traslados
│   │   ├── voluntariado.py          # Competencias, formacion, documentos
│   │   └── skill.py                 # Skill, NivelSkill
│   └── services/
│
├── actividades/                     ← MENÚ: Actividades
│   ├── __init__.py
│   ├── docs/
│   ├── models/
│   │   ├── campana.py               # Campania, TipoCampania, ParticipanteCampania
│   │   ├── evento.py                # Evento, TipoEvento, EstadoEvento, inscripciones
│   │   ├── actividad.py             # Actividad permanente, propuestas, tareas
│   │   ├── grupo.py                 # GrupoTrabajo, MiembroGrupo, reuniones
│   │   └── kpi.py                   # KPI, KPIActividad, MedicionKPI (transversal)
│   └── services/
│
├── economico/                       ← MENÚ: Económico
│   ├── __init__.py
│   ├── docs/
│   ├── core/
│   │   └── feature_flags.py         # SIMPLE / COMPLETA
│   ├── models/
│   │   ├── tesoreria.py             # CuentaBancaria, MovimientoTesoreria, ConciliacionBancaria
│   │   ├── cuotas.py                # CuotaAnual, ImporteCuotaAnio
│   │   ├── donaciones.py            # Donacion, DonacionConcepto
│   │   ├── remesas.py               # Remesa, OrdenCobro
│   │   ├── cobro.py                 # ProveedorPago, Pago, Suscripcion
│   │   ├── presupuesto.py           # PlanificacionAnual, PartidaPresupuestaria
│   │   ├── reclamaciones.py         # Reclamacion, AccionReclamacion
│   │   └── contabilidad.py          # AsientoContable, ApunteContable, CuentaContable (COMPLETA)
│   └── services/
│       ├── tesoreria_service.py
│       └── contabilidad_service.py
│
├── configuracion/                   ← MENÚ: Configuración
│   ├── __init__.py
│   ├── docs/
│   └── models/
│       ├── catalogos.py             # Todos los catálogos y tablas de estados
│       ├── feature_flags.py         # Activación global de módulos
│       └── organizacion.py          # Datos de la organización, colaboraciones, convenios
│
└── core/                            ← TRANSVERSAL (sin entrada de menú)
    ├── comunicacion/                # Notificaciones, mensajería interna
    ├── geografico/                  # Pais, Provincia, Municipio, Direccion
    └── infraestructura/             # BaseModel, database, config, seguridad
```

---

## 3. Mapa de migración

### 3.1 Dominios activos a renombrar o mover

| Dominio actual | Destino | Acción |
|---|---|---|
| `administracion/` | `acceso/` | Renombrar. Mover Rol, Usuario, Transaccion, LogAuditoria |
| `usuarios/` | `acceso/models/usuario.py` | Fusionar en `acceso` |
| `miembros/` | `membresia/models/miembro.py` | Mover |
| `geografico/` | `core/geografico/` | Mover (transversal) |
| `voluntariado/` | `membresia/models/voluntariado.py` | Mover |
| `notificaciones/` | `core/comunicacion/` | Mover (transversal) |
| `campanas/` | `actividades/models/campana.py` | Mover |
| `grupos/` | `actividades/models/grupo.py` | Mover |
| `colaboraciones/` | `configuracion/models/organizacion.py` | Mover |
| `financiero/` | `economico/` | Renombrar + limpiar legacy |
| `financiero_nuevo/` | `economico/` | Es la versión correcta — renombrar y usar esta |
| `core/` | `core/` + `configuracion/` | Separar: estados/config → `configuracion`, infraestructura → `core` |

### 3.2 Dominios huérfanos a conectar o eliminar

| Dominio huérfano | Contenido | Acción |
|---|---|---|
| `actividad/` | Versión anterior de actividades (19KB) | 🔴 Eliminar — `actividades/` ya lo cubre |
| `cobro/` | Models legacy + typo en `__init__,py` | 🔴 Eliminar — absorbido por `economico/cobro.py` |
| `eventos/` | `evento.py` completo (12KB), sin conectar | 🟡 Mover a `actividades/models/evento.py` |
| `organizaciones/` | `organizacion.py` completo (10KB), sin conectar | 🟡 Mover a `configuracion/models/organizacion.py` |
| `analitico/` | Solo docs de KPIs, sin código | 🟡 Mover docs a `actividades/docs/` |
| `financiero_nuevo/` | Versión nueva correcta | 🎯 Renombrar a `economico/` |

---

## 4. Entradas de menú y permisos por módulo

| Módulo | Entrada menú | Prefijos de transacción | Roles típicos |
|---|---|---|---|
| `acceso` | Control de Acceso | `USR_*`, `ROL_*`, `AUD_*`, `PERM_*` | Administrador |
| `membresia` | Membresía | `MBR_*`, `AGR_*`, `TRAS_*`, `SKILL_*`, `VOL_*` | Secretaría, Territorial |
| `actividades` | Actividades | `CAMP_*`, `EVT_*`, `ACT_*`, `GRP_*`, `KPI_*` | Coordinadores, Voluntarios |
| `economico` | Económico | `TES_*`, `CUOT_*`, `DON_*`, `REM_*`, `CONT_*` | Tesorero, Contable |
| `configuracion` | Configuración | `CFG_*`, `CAT_*`, `ORG_*` | Administrador |
| `core` | *(sin menú)* | `MSG_*`, `NOT_*` | Sistema |

---

## 5. Convenciones de la nueva estructura

- Cada dominio de primer nivel tiene: `__init__.py`, `docs/`, `models/`, `services/`
- Los modelos dentro de `models/` son archivos planos (no subcarpetas), salvo que el volumen lo justifique
- Todos los modelos heredan de `BaseModel` en `core/infraestructura/`
- Los estados van a `configuracion/models/catalogos.py` como tablas, no como enums en columna
- Los enums Python solo para valores con lógica fija en el código (`TipoMovimientoTesoreria`, etc.)
- El `domains/__init__.py` importa exclusivamente desde los cinco dominios funcionales y `core`
- Cada dominio tiene su propio `docs/` con un `README.md` que describe sus entidades y servicios

---

## 6. Plan de ejecución por fases

### Fase 1 — Crear estructura vacía de destino
Crear los cinco dominios nuevos (`acceso`, `membresia`, `actividades`, `economico`, `configuracion`)
con su estructura de carpetas y `__init__.py` vacíos. Sin mover código todavía.

### Fase 2 — Migrar `economico`
Es el más trabajado y el que tiene la nueva arquitectura más madura (`financiero_nuevo`).
Renombrar `financiero_nuevo` → `economico`, actualizar imports, eliminar `financiero` legacy y `cobro` legacy.

### Fase 3 — Migrar `acceso`
Fusionar `administracion` + `usuarios` en `acceso`. Actualizar `domains/__init__.py`.

### Fase 4 — Migrar `membresia`
Mover `miembros`, `voluntariado`, `geografico` (agrupaciones). Conectar traslados.

### Fase 5 — Migrar `actividades`
Mover `campanas`, `grupos`, `eventos` (huérfano). Absorber `actividad` (vestigio). Conectar KPIs.

### Fase 6 — Migrar `configuracion`
Extraer catálogos y estados de `core`. Mover `colaboraciones` y `organizaciones`.

### Fase 7 — Limpiar `core`
Dejar solo lo verdaderamente transversal: infraestructura, comunicación, geográfico base.

### Fase 8 — Actualizar `domains/__init__.py`
Reescribir el init principal con los nuevos imports. Verificar que el backend arranca.

### Fase 9 — CI verde y deploy
Verificar CI, corregir imports rotos, desplegar a staging.

---

## 7. Criterio de "done" por fase

- El backend arranca sin errores de import
- El CI pasa (sintaxis + lint + build frontend)
- No quedan referencias a los dominios antiguos en `domains/__init__.py`
- Los dominios origen han sido eliminados del repo

---

## 8. Estado actual

| Fase | Estado |
|---|---|
| Fase 1 — Estructura vacía | ⬜ Pendiente |
| Fase 2 — Económico | ⬜ Pendiente |
| Fase 3 — Acceso | ⬜ Pendiente |
| Fase 4 — Membresía | ⬜ Pendiente |
| Fase 5 — Actividades | ⬜ Pendiente |
| Fase 6 — Configuración | ⬜ Pendiente |
| Fase 7 — Limpiar core | ⬜ Pendiente |
| Fase 8 — Init principal | ⬜ Pendiente |
| Fase 9 — CI y deploy | ⬜ Pendiente |
