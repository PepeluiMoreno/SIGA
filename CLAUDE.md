# SIGA — instrucciones para trabajar en este repo

## Entorno (z4dev)

Stack dev en Docker con hot reload:
`docker compose -f docker-compose.yml -f docker-compose.dev.yml`
Contenedores: `siga_dev_backend` (uvicorn --reload + `alembic upgrade head`),
`siga_dev_frontend` (Vite HMR), `siga_dev_db` (postgres).

- **Ningún puerto está publicado al host.** `curl localhost:8000` cuelga. Para
  hablar con la API: `docker exec siga_dev_backend python -c '...urllib...'`
  (no hay `curl` dentro del contenedor).
- Login break-glass: usuario `superadmin`, contraseña `admin_dev_2026`.
  En la mutación `login` el campo se llama `email` pero acepta el username.
- Verificar el frontend: `docker exec siga_dev_frontend npx vite build --mode development`.
  Ojo: el build reescribe `frontend/dist/`, que está versionado.
- **Gotcha de git**: `origin` tiene un refspec estrecho, así que `git fetch origin`
  solo trae `master`. Para otras ramas: `git fetch origin <rama>`.

## Reglas innegociables

- **`master` es rama de despliegue.** Nada de commits directos ni force-push.
  Se trabaja en rama y se abre PR.
- **Trabaja paso a paso.** Pregunta lo que no sepas del dominio (estatutos, roles
  reales) en vez de suponerlo, y **confirma el modelo antes de codificar**.
- **No sobre-ingenierices.** Un flujo de negocio suele ser más simple de lo que
  parece: pregunta cuál es antes de construir máquinas de estados.
- **DRY.** Antes de escribir un componente, mira si ya existe en
  `components/common/` o `composables/`.

## Frontend

**Lee `docs/ui_convenciones.md` antes de tocar una vista.** Resumen de lo que más
se incumple:

- **Vista de lista** = `AppLayout` con **`fluid`** → `FilterRail` (con
  `FilterBar vertical`) + `ResponsiveTable`. Sin `fluid`, `AppLayout` centra el
  contenido y deja medio ancho vacío. Nada de `<table>` a mano.
  Referencia viva: `modules/membresia/views/ListaContactos.vue`.
- **Las vistas de lista están en `<keep-alive>`** (ver `App.vue`). Por tanto:
  - declara `defineOptions({ name: 'ListaLoQueSea' })` — sin `name`, `keep-alive`
    no la reconoce y no la cachea;
  - carga los datos en **`onActivated`, nunca en `onMounted`** — un componente
    cacheado se monta una sola vez, y al volver de un formulario verías la lista
    obsoleta.
- Una lista **carga al entrar**; los filtros refinan lo ya mostrado. No hay
  listas que esperen a que el usuario pulse «Buscar».
- El filtrado es **en cliente**: las queries de strawchemy no aceptan
  `limit`/`offset`.

## Backend

**Lee `docs/PATRON_CANONICO_MODULO.md`** (dónde va cada cosa dentro de un módulo)
y **`docs/modulo_acceso.md`** (el modelo de permisos).

- **RBAC en 3 capas por el MISMO permiso**: el `v-if` del menú, el
  `meta.requiredPermission` de la ruta y el `RequireTransaction` del resolver
  comprueban la misma transacción. El router es **default-deny**.
- El catálogo RBAC se **declara en código**, en `app/modules/<mod>/catalog.py`, y
  lo materializa `CatalogSyncService.sync()` en el `lifespan` de `main.py`.
  Toda transacción debe pertenecer al menos a una funcionalidad: si no, es
  inasignable (los roles se componen de funcionalidades) y el arranque falla en
  dev.
- **El borrado lógico precede siempre al físico**: un borrado `hard` exige que el
  registro ya esté en la papelera.

## Documentación

- `docs/ui_convenciones.md` — sistema de diseño del frontend.
- `docs/PATRON_CANONICO_MODULO.md` — estructura de un módulo backend.
- `docs/modulo_*.md` — un documento por módulo de dominio.
- `docs/flujos_economico/` — catálogo de flujos de negocio (patrón a replicar).
- `HANDOFF.md` — estado de la sesión en curso y trabajo pendiente priorizado.
