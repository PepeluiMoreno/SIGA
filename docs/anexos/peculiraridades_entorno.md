# Entorno y patrón de despliegue

Trabajamos directamente con el servidor de staging en `vps2.europalaica.org` mediante un flujo de CI/CD con imágenes en GHCR.

La aplicación se dockeriza y se sirve detrás del Traefik **ya existente** en `vps2`, dentro de la network `traefik_public`. Se ofrece al usuario en `siga.staging.europalaica.org`.

Es principio general **no hardcodear** información. Todo lo sensible o variable (passwords, JWT, dominio, prefijo de app, resolver de certificados) vive en variables de entorno; los valores de producción llegan al servidor desde un único GitHub secret.

## Patrón canónico (compartido con `opendatamanager` y demás apps de `vps2`)

### Topología

- **Backend Python** detrás directamente de Traefik (sin nginx delante).
- **Frontend Vue3** servido por una imagen `nginx:alpine` con el bundle estático.
- **Postgres** en red interna, no expuesto.
- **Reverse proxy**: Traefik existente en `vps2`. Cert resolver `letsencrypt`.

### Estructura de archivos en el repo

- `docker-compose.yml` — base con `build:` (sirve para desarrollo local).
- `docker-compose.staging.yml` — override con `image: ghcr.io/...` y labels Traefik (sirve para staging).
- `.env.staging.example` — documenta qué variables hacen falta, sin valores reales.
- `.github/workflows/deploy.yml` — workflow único: job `build` (build + push GHCR) y job `deploy` (SSH al servidor).
- `backend/Dockerfile` y `frontend/Dockerfile` con sus respectivos `.dockerignore`.

### Variables de entorno

`.env.staging.example` documenta todas las variables. En el servidor de staging, el `.env.staging` se genera en cada deploy a partir del secret `SIGA_ENV_STAGING` (un único string multilínea con todo el contenido del `.env`). No hay un secret por variable; todo va en uno.

Variables canónicas:
- `APP_PREFIX` — prefijo para contenedores y routers Traefik (`siga`).
- `APP_DOMAIN` — host expuesto (`siga.staging.europalaica.org`).
- `TRAEFIK_CERTRESOLVER` — `letsencrypt`.
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.
- `JWT_SECRET`.

### Flujo de despliegue

1. Push a `master` dispara el workflow.
2. Job `build`: construye imágenes backend y frontend, las publica en GHCR con tags `latest` y `${{ github.sha }}`. Cache via `type=registry,ref=...:latest` + `type=inline`.
3. Job `deploy` (vía `appleboy/ssh-action`):
   - SSH a `vps2` con el secret `DEPLOY_KEY`.
   - `cd /opt/docker/apps/SIGA && git pull` para actualizar compose y archivos.
   - Login en GHCR con `secrets.GITHUB_TOKEN`.
   - Escribe `.env.staging` con permisos `077` desde el secret `SIGA_ENV_STAGING`.
   - `docker compose --env-file .env.staging -f docker-compose.yml -f docker-compose.staging.yml pull` y `up -d --remove-orphans`.
   - `docker image prune -f` al final.

### Secrets de GitHub requeridos

| Secret | Contenido |
|---|---|
| `DEPLOY_HOST` | `vps2.europalaica.org` |
| `DEPLOY_USER` | usuario SSH (`elaicatec`) |
| `DEPLOY_KEY` | clave SSH privada cuya pública está en `~/.ssh/authorized_keys` del servidor |
| `SIGA_ENV_STAGING` | contenido completo del `.env.staging` (multilínea) |

### Convenciones de nombres

- Imágenes: `ghcr.io/pepeluimoreno/siga-backend` y `ghcr.io/pepeluimoreno/siga-frontend`.
- Contenedores: `${APP_PREFIX}_backend`, `${APP_PREFIX}_frontend`, `${APP_PREFIX}_db`.
- Routers Traefik: `${APP_PREFIX}-api` (con `PathPrefix(/api)` y `stripprefix`), `${APP_PREFIX}-web` (host raíz).

## Entorno de desarrollo local — Optiplex-790

El desarrollo activo se realiza sobre un ordenador físico llamado `optiplex-790` en la misma red local, aunque se accede igual que a un servidor remoto: por SSH (VSCode Remote SSH o terminal). **El código fuente vive directamente en el Optiplex**, en `/opt/docker/apps/SIGA`. No hay paso de sincronización de archivos; se edita in-situ.

### Topología del entorno de desarrollo

- Sin Traefik. Los puertos se exponen directamente al host.
- **Frontend**: Vite dev server (HMR) en `http://optiplex-790:3000`.
- **Backend**: `uvicorn --reload` en `http://optiplex-790:8000`.
- **DB**: Postgres en red interna Docker; volumen `pgdata_dev` separado del staging.
- El proxy de Vite (`/graphql → http://backend:8000`) resuelve el backend por nombre de contenedor dentro de la red Docker interna.

### Arranque

```bash
# Primera vez o cuando cambien dependencias Python/npm:
docker compose -f docker-compose.dev.yml up --build

# Resto de veces:
docker compose -f docker-compose.dev.yml up
```

### Cómo funciona el hot-reload

| Capa | Mecanismo | Tiempo de recarga |
|---|---|---|
| Frontend `.vue`, `.js`, `.css` | Vite HMR vía WebSocket en `:3000` | < 1 s |
| Backend `.py` (app/) | uvicorn `--reload` con watchfiles | 1-3 s |
| Migraciones Alembic | Manual: `docker exec siga_dev_backend alembic upgrade head` | — |

Los bind mounts activos:
- `./backend/app` → `/app/app`
- `./backend/main.py` → `/app/main.py`
- `./backend/alembic` → `/app/alembic`
- `./frontend` → `/app` (completo; `node_modules` en volumen anónimo separado)

### Relación con staging

El push a `master` sigue disparando el pipeline de GitHub Actions que despliega en `vps2.europalaica.org`. El Optiplex y staging son entornos completamente independientes con volúmenes de DB distintos. El flujo normal es: **desarrollar en Optiplex → probar → push a master → staging se actualiza automáticamente**.

---

## Política de borrado: soft-delete por defecto + papelera + hard-delete restringido

Regla general: **ningún borrado destruye datos por defecto**. Todo modelo que herede `BaseModel` ya incluye `eliminado`/`fecha_eliminacion`/`fecha_modificacion` y se elimina marcando `eliminado=True` (soft-delete).

### Papelera de reciclaje (Trash)

- Cada módulo expone una vista de "Papelera" donde se listan los registros con `eliminado=True`.
- Desde la papelera se puede **restaurar** (`eliminado=False`) o **borrar permanentemente** (hard-delete).
- Los registros en papelera **no aparecen** en las consultas habituales: las queries por defecto filtran `eliminado=False`.

### Modal de confirmación de borrado (soft-delete)

Toda acción de borrado en la UI abre un modal que cumple:

1. **Advertencia explícita de cascada**: lista clara y completa de qué entidades relacionadas quedarán afectadas (p. ej. "Se eliminarán también: 12 cuotas asociadas, 3 inscripciones a campañas, 1 vinculación con un grupo de trabajo").
2. **Checkbox "Borrado permanente"** que activa hard-delete en lugar de soft-delete.
3. El checkbox de **borrado permanente solo es visible/funcional para usuarios con rol de superadministrador**. Para el resto, no aparece o aparece deshabilitado con tooltip explicativo.
4. Botón de confirmación destructivo (rojo) y botón de cancelar prominente.

### Hard-delete

- Elimina físicamente el registro de la BD.
- **Solo disponible para `SUPERADMIN`** (transacción asociada al borrado permanente).
- Auditoría: cada hard-delete genera entrada en `logs_auditoria` con `accion=ELIMINAR`, descripción detallada y, si es posible, copia del registro en `datos_anteriores`.
