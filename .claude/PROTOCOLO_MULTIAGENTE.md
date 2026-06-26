# Protocolo de trabajo multi-agente en paralelo — SIGA

> **Léeme al empezar cada sesión.** Esta es la fuente de verdad de cómo colaboran varios
> agentes (chats de Claude Code) sobre este repo sin pisarse. Si algo aquí contradice lo que
> creías, manda esto.

## 0. Lo primero que haces al arrancar

1. Averigua **quién eres**: lee `.claude/AGENTE.local.md` en tu worktree. Te dice tu `ROL`
   (`modulo` | `integrador` | `buzon`) y, si eres de módulo, tu `MODULO`.
2. Si eres agente de **módulo**: ejecuta `/inbox` para ver tu bandeja `.claude/inbox/<MODULO>.md`.
3. Si eres el **integrador**: ejecuta `/integrar` para ver ramas listas y cableados pendientes.
4. Si eres el **buzón**: espera notas del usuario y procésalas con `/triaje`.

Si no existe `.claude/AGENTE.local.md`, pregunta al usuario qué rol tienes antes de tocar nada.

---

## 1. Roles

| Rol | Dónde vive | Qué hace | Qué NO hace |
|---|---|---|---|
| **Agente de módulo** | worktree `../SIGA-wt/<modulo>`, rama `feature/<modulo>` | Trabaja SOLO en los ficheros de su módulo. Commitea en su rama. Pide cableado al integrador cuando necesita tocar una zona caliente. | No edita zonas calientes. No mergea a master. No corre `alembic upgrade head`. |
| **Integrador** | árbol principal `/opt/docker/apps/SIGA`, rama `master` | Único que edita zonas calientes, mergea ramas a master, aplica migraciones y gestiona el stack dev compartido. | No desarrolla features de módulo (las recibe ya hechas en ramas). |
| **Buzón** | cualquier worktree (no toca código) | Recibe las notas desordenadas del usuario, las clasifica por módulo y las encola en `.claude/inbox/`. Es un *reverse proxy* humano→agente. | No arregla nada él mismo. No edita código. |

**Regla de oro:** un fichero tiene **un solo dueño** en un momento dado. Los módulos poseen sus
carpetas; el integrador posee las zonas calientes. Nadie edita lo que no posee.

---

## 2. Mapa de propiedad (ownership)

Cada agente de módulo edita **libremente** lo suyo. Backend y frontend de SIGA usan el mismo
nombre de módulo (con dos extras solo-frontend: `comunicaciones`, `presidencia`).

| Módulo | Backend (posee) | Frontend (posee) | Resolver GraphQL (posee el fichero, pero el *registro* es zona caliente) |
|---|---|---|---|
| `acceso` | `backend/app/modules/acceso/**` (⚠ ver nota registry) | `frontend/src/modules/acceso/**` | `acceso_resolvers.py` |
| `actividades` | `backend/app/modules/actividades/**` | `frontend/src/modules/actividades/**`, `components/grupos/**`, `components/campanias/**` | `actividad_resolvers.py`, `accion_resolvers.py`, `campania_resolvers.py` |
| `economico` | `backend/app/modules/economico/**` | `frontend/src/modules/economico/**`, `components/economico/**`, `components/paypal/**` | `economico_resolvers.py`, `categoria_fiscal_resolvers.py`, `categorizacion_resolvers.py`, `presupuesto_resolvers.py` |
| `membresia` | `backend/app/modules/membresia/**` | `frontend/src/modules/membresia/**`, `components/miembros/**` | `membresia_resolvers.py`, `socios_resolvers.py`, `vinculaciones_resolvers.py` |
| `secretaria` | `backend/app/modules/secretaria/**` | `frontend/src/modules/secretaria/**` | `secretaria_resolvers.py` |
| `configuracion` | `backend/app/modules/configuracion/**` (⚠ NO `models/estados.py`) | `frontend/src/modules/configuracion/**`, `components/configuracion/**`, `components/parametrizacion/**` | `configuracion_resolvers.py` |
| `proteccion_datos` | `backend/app/modules/proteccion_datos/**` | `frontend/src/modules/proteccion_datos/**` | `proteccion_datos_resolvers.py` |
| `core` | `backend/app/modules/core/**` (geografía, comunicación, chat) | `frontend/src/modules/comunicaciones/**` | `comunicacion_resolvers.py`, `chat_resolvers.py`, `geografico_resolvers.py` |
| `organizaciones` | `backend/app/modules/organizaciones/**` | `frontend/src/modules/presidencia/**` | `presupuesto_resolvers.py` (si aplica) |
| `administracion` | `backend/app/modules/administracion/**` | — | — |

> **Nota acceso**: el agente `acceso` posee su módulo, PERO
> `backend/app/modules/acceso/services/registry.py` es zona caliente (lo usan TODOS los módulos
> para registrar permisos). No lo edites: si necesitas un cambio en el `ModuleCatalog`, pídelo
> al integrador. Tu `catalog.py` propio sí lo editas.

> **Nota estados compartidos**: `backend/app/modules/configuracion/models/estados.py` define
> estados que importan varios módulos (`EstadoCuota`, `EstadoCampania`, …). Es zona caliente
> aunque viva dentro de `configuracion`. Para añadir un estado nuevo, pídelo al integrador.

---

## 3. Zonas calientes (NINGÚN agente de módulo las edita — se piden al integrador)

Estos ficheros los toca **todo** módulo y son cableado manual: si dos agentes los editan a la
vez, conflicto de merge garantizado. **No los edites. Pide el cambio con `/pedir-cableado`.**

### Backend
- `backend/main.py` — imports de catalogs + lifespan
- `backend/app/graphql/schema_simple.py` — Query root (agrega todos los módulos)
- `backend/app/graphql/mutations.py` — Mutation root
- `backend/app/modules/acceso/services/registry.py` — `ModuleCatalog`
- `backend/alembic/versions/**` — migraciones (además, **solo el integrador aplica `upgrade head`**, ver §6)
- `backend/app/modules/configuracion/models/estados.py` — estados compartidos
- `backend/app/infrastructure/base_model.py` — BaseModel / mixins
- `backend/app/core/events.py` — event bus
- `backend/app/core/database.py` — sesión / Base

### Frontend
- `frontend/src/router/index.js` — rutas (imports de todas las vistas)
- `frontend/src/components/common/**` — componentes base compartidos (AppButton, AppInput, AppFormGrid, AppLayout, …)
- `frontend/src/stores/auth.js` — store de auth global
- `frontend/src/composables/usePermisos.js` — hook de permisos global

> **¿Y si la mejora es DENTRO de un componente común?** (p.ej. AppFormGrid necesita un prop
> nuevo). Eso lo pides al integrador igual: el componente común es de todos. No lo forkees en tu
> módulo "para no molestar" — eso rompe el principio de reutilización del proyecto.

---

## 4. Flujo de trabajo de un agente de módulo

1. `git status` para confirmar que estás en tu worktree y rama `feature/<modulo>`.
2. `/inbox` → coge una tarea `[ABIERTO]` de tu bandeja (o el usuario te da una directa).
3. Desarrolla **solo en tus ficheros** (§2). Commitea con `tipo(<modulo>): descripción` (§5).
4. ¿Necesitaste tocar una zona caliente? → **NO la edites**. Acaba lo tuyo, deja la vista/
   resolver/migración creada en tu rama, y ejecuta `/pedir-cableado` describiendo qué hace
   falta cablear. El integrador lo hará al mergear.
5. Marca la tarea `[HECHO]` en tu bandeja con el hash del commit.
6. Cuando tu rama esté lista para integrarse, avisa al integrador (o déjalo en `integrador.md`).

**Nunca** mergees a master tú. **Nunca** corras migraciones. **Nunca** edites otro módulo:
si un bug "tuyo" resulta vivir en otro módulo, no lo arregles — manda una nota al buzón (o
escribe directamente en la bandeja del módulo dueño) explicándolo.

---

## 5. Convención de commits (= mecanismo de atribución)

Se mantiene la convención del repo: `tipo(scope): descripción` en español.
- **tipos**: `feat`, `fix`, `refactor`, `revert`, `chore`, `docs`
- **scope = tu módulo** SIEMPRE. Un agente `economico` commitea `feat(economico): …`.
  Esto hace que el `git log` sea la traza de quién tocó qué. Si tu commit no es de tu scope,
  estás editando lo que no debes.
- Cierre de commit (igual que el resto del repo):
  ```
  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
  ```

---

## 6. Reglas duras (alembic, BD, stack dev)

- **Una sola BD Postgres compartida** (`docker-compose.dev.yml`, BD `siga`). Todos los
  worktrees apuntan a la misma. Por eso:
  - **Solo el integrador ejecuta `alembic upgrade head`.** Un agente de módulo SÍ puede *crear*
    una migración (`alembic revision`) en su rama, pero **no la aplica**: la deja para el
    integrador, que la encadena al head real y la aplica una sola vez contra la BD compartida.
  - Si dos módulos crean migraciones a la vez, divergen los heads. El integrador las reconcilia
    (`alembic merge`) al integrar. Por eso las migraciones son zona caliente.
- **Un solo stack dev** corriendo (backend `:8000`, frontend `:3000`), gestionado por el
  integrador desde master con `docker compose -f docker-compose.dev.yml up`. **No arranques tu
  propio backend/frontend en tu worktree** (colisión de puertos y de BD). Para ver tu cambio en
  vivo, pide al integrador que mergee tu rama y recargue (hot-reload lo recoge).

---

## 7. El buzón y las bandejas (`.claude/inbox/`)

- El usuario reporta fallos/mejoras de forma desordenada al **chat buzón**.
- El buzón ejecuta `/triaje`: clasifica la nota por módulo (usando el mapa §2) y escribe un
  bloque `[ABIERTO]` en `.claude/inbox/<modulo>.md`. Registra el reparto en `_triage_log.md`.
- Las **peticiones de cableado** de los agentes van a `.claude/inbox/integrador.md`.
- Formato de las entradas: ver `.claude/inbox/_README.md`.

---

## 8. Resumen de "qué puedo / qué no" por rol

**Soy agente de módulo `X`:**
- ✅ editar `app/modules/X/**`, `frontend/src/modules/X/**` y mis componentes (§2)
- ✅ crear migraciones, vistas, resolvers en mi rama
- ✅ `/pedir-cableado` cuando necesito tocar algo compartido
- ❌ editar otro módulo, zonas calientes (§3), mergear, `alembic upgrade head`, arrancar mi stack

**Soy el integrador:**
- ✅ todo lo compartido: zonas calientes, merges, migraciones, stack dev
- ✅ `/integrar` para procesar ramas listas y cableados pendientes
- ❌ desarrollar features de módulo (llegan ya hechas en ramas)

**Soy el buzón:**
- ✅ `/triaje`: clasificar y encolar notas del usuario
- ❌ tocar código
