# HANDOFF — estado de la sesión (traslados / membresía / RBAC)

> Handoff de una sesión de Claude Code en la web (contenedor cloud aislado, sin
> acceso al stack) hacia una sesión en **VSCode sobre z4dev** (acceso al Docker/BD
> vivos). Lee esto entero antes de tocar nada.

## Dónde estamos

- **Rama de trabajo**: `claude/traslados-mejora` (parte de `master`). El checkout de
  z4dev (`/opt/docker/apps/SIGA`) está en esta rama y el stack dev corre sobre ella.
- **En master ya** (PR #11 mergeado): todo el MVP de paridad GSH→SIGA + su UI +
  limpieza optiplex→z4dev. Ver `docs/desarrollo/MVP_GSH_SIGA.md`.
- **Solo en esta rama** (no en master): backend + UI del **rediseño de traslados**
  y un **estilo global de fondo de formulario**.

## Entorno (z4dev)

- Dev host = **z4dev** (WSL sobre el Windows de VSCode). Repo en `/opt/docker/apps/SIGA`.
- Stack: `docker compose -f docker-compose.yml -f docker-compose.dev.yml`. Contenedores
  `siga_dev_backend` (uvicorn --reload + `alembic upgrade head` al arrancar),
  `siga_dev_frontend` (Vite HMR, bind-mount), `siga_dev_db` (postgres).
- Login break-glass: usuario **`superadmin`**, pass **`admin_dev_2026`** (viene de
  `SUPERADMIN_PASSWORD` en el `.env`; el bootstrap la resincroniza al reiniciar).
- **SMTP sin configurar** → auto-alta y avisos hacen todo menos enviar el email.
- **PayPal**: necesita `PAYPAL_CLIENT_ID/SECRET` sandbox para probar el pago de cuota.
- Versiones (uv.lock): Python 3.13, strawchemy 0.21.0, strawberry 0.315.3.
- **Gotcha de git**: el `origin` de z4dev tiene un refspec estrecho
  (`+refs/heads/master:refs/remotes/origin/master`) → `git fetch origin` **solo trae
  master**. Para traer otras ramas: `git fetch origin <rama>`. Arréglalo de raíz con:
  `git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*' && git fetch origin`.

## Convenciones del proyecto (respétalas)

- **RBAC en 3 capas por el MISMO permiso** (menú `v-if` = ruta `meta.requiredPermission`
  = resolver `RequireTransaction`). Ver `docs/modulo_acceso.md`. Router es default-deny.
- El catálogo RBAC (transacciones/funcionalidades/roles) se declara en
  `app/modules/<mod>/catalog.py` y se materializa en BD por `CatalogSyncService.sync()`
  en el `lifespan` de `main.py` (que además enlaza SUPERADMIN a todo). Fuente única.
- **DRY**: reutilizar componentes comunes (AppLayout, ResponsiveTable, FilterBar,
  EstadoBadge, AppButton, SelectorMiembro/Agrupacion, useGraphQL, useConfirm/usePrompt,
  usePermisos). `useConfirm`/`usePrompt` usan claves ES: `titulo`, `mensaje`, `variante`
  ('aviso'|'peligro'), `etiquetaConfirmar`; prompt: `label`, `requerido`.
- Catálogos editables: patrón `CatalogoGenerico.vue` + entrada en `CatalogosIndex.vue`
  + ruta + queries en `graphql/queries/catalogos.js`.
- Migraciones alembic: patrón `Base.metadata.create_all(bind, checkfirst=True,
  tables=[...])` + seeds idempotentes con `op.execute` (ver `trasl1cat2est3` y
  `g2h3i4j5k6l7`). Head único actual: `trasl1cat2est3`.
- **master es rama de despliegue**: nada de commits directos ni force-push. Trabajo en
  rama + PR. (Ahora mismo trabajas solo, sin colega.)

---

## PENDIENTE — prioridad

### 1. RBAC sin datos + superadmin sin permisos (DIAGNOSTICAR YA)
El usuario ve el **módulo de control de acceso vacío** y a **superadmin le faltan
permisos**. El arranque SÍ sincroniza el catálogo (`main.py` lifespan). Hay que ver si
es tablas vacías (sync fallando) o datos-ok-pero-frontend-no-lista. Diagnóstico:
```bash
docker logs siga_dev_backend 2>&1 | grep -iE "Catálogos sincronizados|PermissionMatrix|Traceback|error" | tail -15
docker exec siga_dev_db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select (select count(*) from transacciones) t,(select count(*) from roles) r,(select count(*) from funcionalidades) f;"'
docker exec siga_dev_db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select count(*) from roles_transacciones rt join roles r on r.id=rt.rol_id where r.codigo = \$\$SUPERADMIN\$\$;"'
docker exec siga_dev_db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select u.username, r.codigo from usuarios u join usuarios_roles ur on ur.usuario_id=u.id join roles r on r.id=ur.rol_id where u.username = \$\$superadmin\$\$;"'
```
Tablas: `transacciones`, `roles`, `funcionalidades`, `roles_transacciones`,
`usuarios_roles`. Si (2) da 0 o (1) tiene Traceback → sync roto (arréglalo). Si hay
datos → es frontend (pantallas Catálogo RBAC / Roles no listan).

### 2. Rework de TRASLADOS — ¡REEMPLAZAR lo que hay en la rama!
La rama trae una versión **SOBRE-INGENIERIZADA** (doble aprobación origen/destino +
"ejecutar" + catálogo `motivos_traslado`). **El usuario la rechazó.** El modelo REAL
(decisiones tomadas) es:
- Un traslado es una **NOTIFICACIÓN**. Lo registra el **propio socio** o el
  **secretario de su agrupación** (ámbito territorial).
- El **secretario de DESTINO se da por enterado**, y **ese acto aplica el cambio** de
  agrupación (mueve `agrupacion_id` + rellena `HistorialAgrupacion`).
- **Fuera el catálogo `motivos_traslado`** y su página en Config. Solo una **nota libre
  opcional** (`SolicitudTraslado.motivo` como texto).
- Estados reducidos a **Notificado → Enterado (+ Anulado)**. Fuera
  PENDIENTE/APROBADO_ORIGEN/APROBADO_DESTINO/APROBADO/EJECUTADO.
- El catálogo `estados_traslado` (con color) puede quedarse, **re-sembrado** con los 3
  estados nuevos.
- Hay que **migración de limpieza**: quitar `motivo_traslado_id` + tabla
  `motivos_traslado`, y re-sembrar `estados_traslado`.
- **Ubicación (pendiente de confirmar con el usuario)**: autoservicio del socio +
  bandeja del secretario **filtrada a su agrupación** (entrantes a acusar). Preguntar.

Ficheros afectados: `app/modules/membresia/models/traslados/modelos.py`,
`app/graphql/vinculaciones_resolvers.py` (mutations solicitar/aprobar*/rechazar/
cancelar/ejecutar → sustituir por `notificar_traslado` + `darse_por_enterado_traslado`
+ `anular`), `frontend/src/modules/membresia/views/BandejaTraslados.vue`,
`frontend/src/graphql/queries/socioGestion.js`, y quitar
`frontend/.../catalogos/MotivosTraslado.vue` + su ruta + tarjeta en `CatalogosIndex.vue`.

### 3. Catálogo de flujos de membresía (documentar)
Producir `docs/flujos_membresia/` (patrón de `docs/flujos_economico/`: propósito,
entidades, estados, acciones/agentes, pantallas, permisos, norma). Agentes:
socio (PROPIO), secretario de agrupación (territorial), coordinador territorial,
tesorero (económico), presidente/vicepresidente, junta directiva (colegiado),
coordinador de campaña. Flujos: alta/auto-alta ✅, admisión ✅, baja ✅, traslado
(rework), reducción de cuota ✅, **sanciones disciplinarias ✗ (falta entero)**,
**histórico integral del socio ◑**.

### 4. Dos huecos de fondo
- **Sanciones disciplinarias**: no existe modelo (solo `EXPULSION` como MotivoBaja).
  Flujo **estatutario** (expediente: incoación → instrucción → alegaciones → resolución
  Junta/Asamblea → apercibimiento / suspensión temporal de derechos / expulsión).
  **Diseñar con el usuario según los estatutos de Europa Laica; NO inventar.**
- **Histórico integral del socio**: piezas existen (cuotas ordinarias/extraordinarias,
  donaciones, participaciones en actividades/voluntariado/firmas) pero **sin ensamblar**
  en una ficha "vida del socio". Base: `historial_contacto` (membresia_resolvers, cubre
  FIRMA/ASISTENCIA/DONACION) — falta unir cuotas.

### 5. Bug preexistente en master (aparte)
`TypeError: Cannot return null for non-nullable field GrupoTrabajoType.agrupacion` —
un grupo de trabajo sin agrupación y el campo GraphQL es no-nulable. Igual que se
arregló `SolicitudTrasladoType.motivoTraslado` (declarar `Optional` en el tipo
strawchemy en `types_auto.py`).

### 6. Estilo (bajo, cosmético)
Se añadió fondo global a `<form>` en `frontend/src/style.css` (var `--t-form-bg` →
`--t-50`). El usuario pidió aparcarlo; puede querer subir el tono (`--t-100`).

## Regla de oro con el usuario
Trabaja **paso a paso**: pregunta lo que no sepas del dominio (estatutos, roles reales),
no sobre-ingenierices (lección de traslados), y confirma el modelo antes de codificar.
