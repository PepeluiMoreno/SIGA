# Coherencia estructural de los módulos en SIGA

> Objetivo: que **todos los módulos tengan las cosas en los mismos sitios y se
> hagan de la misma forma**. Cuando abras cualquier módulo, debes encontrar lo
> mismo en el mismo lugar. No es modularización ni sistema de plugins: es
> coherencia. Este documento describe el estándar extraído de los módulos que ya
> lo hacen bien (`economico`, `acceso`, `secretaria`) para que el resto converja.

## 1. Estado actual (por qué hace falta)

Los módulos no están organizados igual. Inventario real (mayo 2026):

| Módulo | Capa de servicios |
|---|---|
| economico | 18 servicios |
| acceso | 6 servicios |
| secretaria | 4 servicios |
| core, configuracion, organizaciones, membresia, actividades | 0 servicios |

Donde no hay servicios, la lógica vive metida en los resolvers o se delega a
operaciones CRUD genéricas, y aparecen cosas fuera de sitio (p. ej. un servicio
viejo dentro de `membresia/models/traslados/servicios.py`, que es código muerto).
El resultado: cada módulo se lee distinto y cuesta saber dónde tocar.

## 2. Dónde va cada cosa (estructura de carpetas)

Todo módulo se organiza igual:

```
app/modules/<modulo>/
  models/                     # entidades SQLAlchemy (y solo eso)
  services/                   # lógica de negocio: <entidad>_service.py
  catalog.py                  # transacciones y funcionalidades RBAC del módulo
app/graphql/<modulo>_resolvers.py   # Query/Mutation del módulo (capa fina)
app/scripts/seeding/seed_<modulo>.py # datos base idempotentes (si los hay)
```

Reglas de ubicación:
- Un modelo es solo datos y reglas locales de su entidad. **Nunca** un servicio
  ni lógica de proceso dentro de `models/`.
- Toda la lógica de negocio vive en `services/`, un fichero por entidad principal.
- El resolver vive en `app/graphql/`, no dentro del módulo.
- Los seeds en `app/scripts/seeding/`, nunca SQL suelto aplicado a mano.

## 3. Cómo se hace cada cosa (las tres capas)

```
Resolver (frontera GraphQL)  →  Service (negocio)  →  Modelos (datos)
```

1. **Resolver**: comprueba permiso con `RequireTransaction("CODIGO")`, lee
   `info.context` (session, user), llama a UN método de servicio y devuelve el
   resultado. Sin lógica de negocio, sin `commit`.
2. **Service**: recibe `session` por constructor (`def __init__(self, session)`).
   Contiene toda la lógica. Es dueño de su `commit`. Las validaciones lanzan
   `ValueError` con mensaje claro. Reutilizable desde resolvers, otros servicios,
   scripts y handlers de eventos.
3. **Modelo**: campos, relaciones y propiedades calculadas de la entidad.

## 4. Convenciones uniformes

- **Servicios reciben la sesión por constructor** (17/18 servicios de economico ya
  lo hacen — es el patrón dominante; se generaliza).
- **El servicio comitea, el resolver no.**
- **Operación con reglas o cambio de estado → método de servicio.** CRUD trivial
  de un catálogo puede quedarse autogenerado; cualquier cosa con lógica, no.
- **Permisos** siempre con `RequireTransaction` en el resolver; nunca consultas
  RBAC ad-hoc por el código (usar la `PermissionMatrix` / `DestinatarioResolver`).
- **Eventos de dominio** (si el módulo avisa a otros): se publican desde el
  servicio, **tras el commit**, envueltos en try/except:
  ```python
  await self.session.commit()
  await self.session.refresh(obj)
  try:
      from app.core.events import event_bus, MiEvento
      await event_bus.publish(MiEvento(...))
  except Exception:
      pass
  ```
- **Seeds idempotentes** por código (crear-o-actualizar).
- **Cambios de esquema** siempre vía migración Alembic encadenada al head.

## 5. Cómo converger (sin prisa, sin reescribir todo de golpe)

Una rama por módulo, criterio de "hecho" por módulo:
- La lógica está en `services/`, no en los resolvers.
- Los resolvers son finos.
- No hay nada fuera de sitio (ni servicios en `models/`, ni SQL suelto).
- Si el módulo emite avisos, lo hace desde el servicio tras commit.

Orden sugerido (por necesidad, no por ambición):
1. `membresia`: extraer servicios de nombramiento y traslado desde las CRUD
   actuales; eliminar el código muerto `models/traslados/servicios.py`.
2. `actividades`, `organizaciones`, `configuracion`, `core`: extraer a `services/`
   la lógica que hoy esté en resolvers.

## 6. Referencia (módulos ya coherentes)

- `economico`, `acceso`, `secretaria`: servicios con session, lógica fuera de los
  resolvers.
- `core/comunicacion`: `NotificacionService` / `DestinatarioResolver` reciben
  session; eventos publicados desde los servicios tras commit. Referencia reciente.
