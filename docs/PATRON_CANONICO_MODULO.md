# Patrón canónico de módulo en SIGA

> Objetivo: que **todos los módulos hagan las cosas del mismo modo** (uniformidad)
> y que la lógica viva en **un solo sitio** (DRY). Este documento extrae la
> convención de los módulos ya maduros (`economico`, `acceso`, `secretaria`) y la
> fija como estándar al que el resto debe converger, módulo a módulo.
>
> **Alcance: capa INTRA-módulo.** Este documento cubre *cómo se estructura por
> dentro* un módulo (capas, servicios, eventos, RBAC). Es complementario —y
> subordinado— al plan de **arquitectura de plugins activables** descrito en
> `docs/chat modularizacion y rbac.md`, que define la capa de ENSAMBLADO: cómo un
> módulo se enchufa/desenchufa del sistema mediante un manifiesto (`PluginRegistry`),
> una tabla `modulo_config`, y un `schema_builder` que monta el schema GraphQL,
> el RBAC, el router y el menú dinámicamente según los módulos activos.
>
> **Nota de transición importante:** hoy `schema_simple.py` y `mutations.py`
> ensamblan `Query`/`Mutation` por **herencia de mixins fijos** (incluido el de
> comunicación añadido recientemente). Eso es el monolito que el Sprint 2 del plan
> de plugins desmontará. Por tanto, los mixins fijos son **transitorios**: cuando
> exista el `schema_builder`, cada módulo —comunicación incluido— deberá exponer
> sus campos vía `get_schema_fields()` en su manifiesto, no por herencia. No
> añadir más acoplamiento al monolito del que sea imprescindible.

## 1. Estado actual (por qué hace falta este documento)

Inventario real del backend (mayo 2026):

| Módulo | Capa de servicios | Lógica de negocio |
|---|---|---|
| economico | 18 servicios | en servicios ✅ |
| acceso | 6 servicios | en servicios ✅ |
| secretaria | 4 servicios | en servicios ✅ |
| core, configuracion, organizaciones, membresia, actividades | 0 servicios | en resolvers o CRUD autogeneradas ❌ |

Conviven 265 mutations autogeneradas por strawchemy con 15 resolvers/mutations
custom, sin una regla clara de cuándo usar cada vía. La consecuencia no es solo
estética: en `membresia`, nombramientos y traslados no pueden emitir avisos de
flujo porque no existe un método de servicio donde hacerlo.

## 2. Las tres capas y su responsabilidad única

```
GraphQL resolver  →  Service  →  Modelos / repos
   (frontera)         (negocio)     (datos)
```

1. **Resolver (`app/graphql/<modulo>_resolvers.py`)**: traduce GraphQL ↔ dominio.
   Comprueba permisos (`RequireTransaction`), lee `info.context` (session, user),
   llama a UN método de servicio y formatea la respuesta. **Sin lógica de negocio.**
2. **Service (`app/modules/<modulo>/services/<entidad>_service.py`)**: toda la
   lógica. Recibe `session` por constructor. Hace el `commit`. Publica eventos de
   dominio tras el commit. Es reutilizable desde resolvers, otros servicios,
   scripts y handlers.
3. **Modelos**: datos y reglas locales de la entidad (propiedades calculadas,
   validaciones de invariante). Sin acceso a sesión ni a otros agregados.

## 3. Convenciones obligatorias (extraídas del código que ya funciona)

### 3.1 Servicios
- Un servicio por agregado/entidad principal: `RemesaService`, `ActaService`, …
- **Constructor recibe la sesión**: `def __init__(self, session: AsyncSession)`.
  (17/18 servicios económicos ya lo hacen — es el patrón dominante.)
- Métodos `async`. El servicio **es dueño de su `commit`**; el resolver no comitea.
- Validaciones de negocio lanzan `ValueError` con mensaje claro; el resolver las
  traduce a error GraphQL.

### 3.2 Mutations: cuándo custom y cuándo autogenerada
- **CRUD puro sin reglas** (catálogos, tablas de apoyo) → mutation autogenerada
  por strawchemy. Aceptable y DRY: no se duplica código trivial.
- **Cualquier operación con reglas, side-effects o transición de estado**
  (aprobar, convocar, trasladar, generar remesa, imputar gasto…) → método de
  servicio + resolver custom. **Nunca** meter esa lógica en el resolver ni
  esperar que una CRUD autogenerada la cubra.
- Regla práctica: si la operación debería poder **emitir un evento de dominio**,
  necesita un servicio.

### 3.3 Eventos de dominio (comunicación entre módulos)
- Definición única en `app/core/events.py` (un `@dataclass(frozen=True)` por evento).
- Se **publican desde el servicio, siempre tras el `commit`**, envueltos en
  `try/except` (un fallo de aviso no revierte la operación):
  ```python
  await self.session.commit()
  await self.session.refresh(obj)
  try:
      from app.core.events import event_bus, MiEvento
      await event_bus.publish(MiEvento(...))
  except Exception:
      pass
  ```
- Los **handlers** que reaccionan viven en el módulo consumidor (p. ej.
  `core/comunicacion/handlers.py`) y se suscriben una vez en el lifespan con un
  `wire_<algo>(async_session)`. El emisor no conoce al consumidor.

### 3.4 Resolución de audiencia / permisos (DRY)
- Para "quién tiene rol/cargo/permiso" se usa **siempre** el `DestinatarioResolver`
  y la `PermissionMatrix`. No se reescriben consultas RBAC ad-hoc en cada módulo
  (era el caso del bug de presupuestos, que solo miraba `RolTransaccion`).

### 3.5 RBAC y catálogo
- Cada módulo declara su `catalog.py` (transacciones + funcionalidades) y se
  registra por side-effect en el lifespan. Los permisos se comprueban con
  `RequireTransaction("CODIGO")` en el resolver.

### 3.6 Seeds y migraciones
- Seeds **idempotentes** por código (crear-o-actualizar), en `scripts/seeding/`.
- Cambios de esquema **siempre** vía migración Alembic encadenada al head; nada
  de SQL aplicado a mano (la vista `v_nombramientos_vigentes` era deuda de esto).

## 4. Plantilla mínima de un módulo conforme

```
app/modules/<modulo>/
  models/            # entidades SQLAlchemy
  services/          # <entidad>_service.py  (lógica + commit + eventos)
  catalog.py         # transacciones y funcionalidades RBAC
app/graphql/<modulo>_resolvers.py   # Query/Mutation mixins, sin lógica
app/scripts/seeding/seed_<modulo>.py # idempotente (si hay datos base)
```

## 5. Cómo converger (sin reescribir todo de golpe)

Orden recomendado, **una rama por módulo**, sin mezclar con features:

1. `membresia` primero (lo necesita ya para emitir nombramientos/traslados):
   extraer `NombramientoService` y `TrasladoService` desde las CRUD actuales,
   con sus métodos de aprobación, y publicar los eventos ya definidos.
   - **Diagnóstico hecho:** existe `models/traslados/servicios.py::ServicioTraslados`,
     que es **código muerto** y anti-patrón a eliminar en esa rama: está mal
     ubicado (un servicio dentro de `models/`), nadie lo importa, usa `int` en vez
     de UUID, y referencia módulos inexistentes (`app.modulos.*`, nomenclatura
     antigua) con imports comentados. El modelo bueno es
     `models/traslados/modelos.py` (`SolicitudTraslado`, estados `EstadoTraslado`,
     doble aprobación origen/destino). El nuevo `TrasladoService` debe vivir en
     `services/`, recibir `session`, y al resolver una solicitud publicar
     `TrasladoResuelto`; al crearla, `TrasladoSolicitado`.
2. `actividades`, `organizaciones`, `configuracion`, `core`: extraer servicios
   donde haya lógica hoy en resolvers.
3. Revisar las 265 mutations autogeneradas: las que tengan reglas, migrarlas a
   servicio; las CRUD puras se quedan.

Criterio de "hecho" por módulo: lógica solo en servicios, resolvers finos,
eventos publicados desde servicios tras commit, sin consultas RBAC ad-hoc.

## 6. Lo ya conforme (referencia)

- `economico` (servicios + resolver custom + `avisar_desviacion` publica/emite).
- `secretaria` (`ReunionService`/`ActaService` publican los 3 eventos tras commit).
- `core/comunicacion` (`NotificacionService`/`DestinatarioResolver` reciben session;
  handlers desacoplados vía event bus). Es la referencia más reciente y completa.
