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
