# PENDIENTE — Sesión dedicada: coherencia estructural de los módulos

> Esta tarea NO se ha abordado aún. Requiere una sesión dedicada solo a esto,
> trabajando **una rama por módulo**, sin mezclar con features.
> Estándar de referencia: `docs/PATRON_CANONICO_MODULO.md`.

## Objetivo

Que todos los módulos tengan **las cosas en los mismos sitios** y se hagan **de
la misma forma**. En concreto:

1. **Las reglas de negocio van en SERVICIOS, no en GraphQL.** Los resolvers son
   capa fina: comprueban permiso, leen el contexto, llaman a UN método de
   servicio y devuelven. Nada de lógica ni `commit` en el resolver.
2. **Ubicación uniforme de cada cosa:**
   - `app/modules/<modulo>/models/` → solo entidades SQLAlchemy.
   - `app/modules/<modulo>/services/` → toda la lógica (un servicio por entidad,
     recibe `session` por constructor, es dueño de su `commit`).
   - `app/graphql/<modulo>_resolvers.py` → Query/Mutation finos.
   - `app/scripts/seeding/seed_<modulo>.py` → datos base idempotentes.
   - Nada fuera de sitio (ni servicios dentro de `models/`, ni SQL aplicado a mano).

## Punto de partida (diagnóstico ya hecho)

| Módulo | Servicios | Acción |
|---|---|---|
| economico, acceso, secretaria | sí | referencia; revisar que el resolver no tenga lógica |
| core, configuracion, organizaciones, membresia, actividades | NO | extraer servicios desde los resolvers/CRUD |

- `membresia` primero: extraer `NombramientoService` y `TrasladoService` desde las
  mutations CRUD autogeneradas; ya se eliminó el código muerto
  `models/traslados/servicios.py`.
- Criterio de "hecho" por módulo: lógica solo en `services/`, resolvers finos,
  nada fuera de sitio, eventos (si los hay) publicados desde el servicio tras commit.

## Fuera de alcance (decidido)

- NO modularización ni sistema de plugins activables (el doc
  `chat modularizacion y rbac.md` queda solo como referencia, no se implementa).
- NO sustituir strawchemy de forma generalizada en esta tarea.
