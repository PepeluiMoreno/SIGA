# Procedimiento de despliegue de aplicaciones Python (ecosistema Europa Laica)

Procedimiento de referencia para **desarrollar y desplegar** aplicaciones Python
(FastAPI + Postgres + Docker) en la infraestructura de Europa Laica. Recoge la
**sistemática de despliegue vigente** tras el hardening de jun-2026.

Complementa, y en la parte de despliegue **actualiza**, el *Estándar de
Ingeniería · CI/CD, Secretos y Despliegue* (cuyo §5.2 describía el deploy por
SSH, hoy inviable). Documentos relacionados:

- `deploy/SELF_HOSTED_RUNNER.md` — instalación del runner paso a paso.
- `docs/despliegue.md` — despliegue concreto de SIGA.
- *Seguridad de la infraestructura — Europa Laica* — VPN WireGuard/wstunnel y firewall.

---

## 1. Principio rector

> El **CI construye** en GitHub-hosted y publica la imagen en GHCR; el **deploy
> se ejecuta dentro del propio servidor** mediante un **runner self-hosted**, que
> sale hacia GitHub (no se entra al servidor).

Motivo: tras el hardening, el **SSH entrante está cerrado al público**. El acceso
solo existe **dentro de la VPN WireGuard** (encapsulada en WebSocket con
`wstunnel`, porque el proveedor filtra el UDP de WireGuard). Un runner
GitHub-hosted **no puede** entrar por scp/ssh (`ssh: handshake failed: EOF`). El
runner self-hosted esquiva el problema sin abrir ningún puerto ni tocar el
hardening.

---

## 2. Arquitectura del pipeline

```
push a master / tag v*
        │
        ▼
┌──────────────────────────┐     ┌───────────────────────────────────────┐
│ build-and-push           │     │ deploy-staging / deploy-production      │
│ runner: ubuntu-latest    │ ──► │ runner: self-hosted (labels)            │
│ (GitHub-hosted)          │     │ corre DENTRO del VPS, como `deployer`   │
│ build + push a GHCR      │     │ ./scripts/deploy-remote-pull.sh         │
└──────────────────────────┘     └───────────────────────────────────────┘
```

Selección del runner por **labels** en `.github/workflows/deploy.yml`:

| Entorno    | VPS  | Labels                           | Disparo                        |
|------------|------|----------------------------------|--------------------------------|
| Staging    | VPS2 | `self-hosted`, `siga-staging`    | push a `master`                |
| Producción | VPS1 | `self-hosted`, `siga-production` | tag `v*` o `workflow_dispatch` |

`build-and-push` corre en GitHub-hosted; **solo el job de deploy** corre en el VPS.

---

## 3. Estructura de repositorio (mínima conforme)

```
<app>/
├── Dockerfile                       # imagen; la app corre como usuario NO-root (USER)
├── docker-compose.yml               # BASE (desarrollo, build local)
├── docker-compose.prod.yml          # OVERRIDE staging/prod (imagen GHCR + Docker secrets)
├── docker-compose.dev.yml           # OPCIONAL: overrides de desarrollo
├── .env.example / .env.production.example   # solo marcadores
├── secrets/.gitkeep                 # carpeta versionada vacía (700 en el servidor)
├── scripts/
│   ├── dev-up.sh                    # arranque en desarrollo
│   └── deploy-remote-pull.sh        # deploy server-side (lo ejecuta el runner)
└── .github/workflows/deploy.yml     # build→GHCR + deploy en runner self-hosted
```

Regla base/override: el `docker-compose.yml` base es desarrollo (build local);
staging/prod superponen `docker-compose.prod.yml` (`-f docker-compose.yml -f
docker-compose.prod.yml`).

---

## 4. El workflow `deploy.yml` (esqueleto vigente)

```yaml
on:
  push: { branches: [master], tags: ['v*'] }
  workflow_dispatch:
    inputs: { deploy_production: { type: boolean, default: false } }
concurrency: { group: deploy-<app>, cancel-in-progress: false }

jobs:
  build-and-push:
    runs-on: ubuntu-latest          # GitHub-hosted: construye y publica en GHCR
    permissions: { contents: read, packages: write }
    # ... checkout, login ghcr (GITHUB_TOKEN), build-push-action ...

  deploy-staging:
    needs: build-and-push
    if: github.ref == 'refs/heads/master' && !(...deploy_production)
    runs-on: [self-hosted, siga-staging]    # ← runner DEL VPS
    env: { DEPLOY_DIR: /opt/docker/apps/<app> }
    steps:
      - uses: actions/checkout@v4
      - name: Desplegar (local en el VPS)
        env:
          DEPLOY_IMAGE_TAG: ${{ github.sha }}
          ENV_STAGING: ${{ secrets.<APP>_ENV_STAGING }}
          GHCR_PAT: ${{ secrets.GHCR_PAT }}        # solo si las imágenes son privadas
        run: |
          set -euo pipefail
          mkdir -p "$DEPLOY_DIR/scripts"
          cp -f docker-compose.yml docker-compose.prod.yml "$DEPLOY_DIR"/
          cp -f scripts/*.sh "$DEPLOY_DIR/scripts"/
          cd "$DEPLOY_DIR"
          umask 077
          printf '%s\n' "$ENV_STAGING" > .env.production
          export DEPLOY_IMAGE_TAG GHCR_PAT
          ./scripts/deploy-remote-pull.sh
```

> **Diferencia clave con el modelo SSH antiguo:** no hay `appleboy/scp-action` ni
> `ssh-action`. El runner ya está dentro del VPS: copia los compose **en local**
> (`cp`) y ejecuta el script directamente.

---

## 5. Script de despliegue server-side (`deploy-remote-pull.sh`)

Responsabilidades obligatorias (en orden):

1. Cargar `.env.production` (existe en el servidor; lo vuelca el job desde el secret).
2. Permitir override de `IMAGE_TAG` vía `DEPLOY_IMAGE_TAG` (lo pasa el CI con el SHA).
3. Usar `-f docker-compose.yml -f docker-compose.prod.yml`.
4. **Materializar credenciales como Docker secret** (env → fichero `secrets/*.txt`) y `unset`.
5. `docker login ghcr.io` **solo si `GHCR_PAT` está definido** (registro privado).
6. **Backup de la BD** antes de migrar.
7. Registrar la imagen previa para **rollback**.
8. `pull` → `up -d`; las migraciones idempotentes las aplica el entrypoint del backend.
9. **Healthcheck** con reintentos; si falla, **rollback** a la imagen previa.

---

## 6. Gestión de secretos (dos capas)

- **Origen:** GitHub Secret por entorno (`<APP>_ENV_STAGING` / `ENV_PRODUCTION`),
  que contiene el bloque `.env` completo incluidas credenciales.
- **Entrega:** en runtime, **Docker secret** (fichero en `/run/secrets/<x>`), nunca
  variable de entorno plana.
- **Código:** lee toda credencial con el patrón `<VAR>_FILE` (Docker secret),
  cayendo a `<VAR>` solo por compatibilidad de desarrollo.

### Reglas de oro y gotchas verificados

- **El contenedor corre como usuario NO-root** (USER en el Dockerfile). Por tanto
  los ficheros de secret materializados **deben ser legibles por ese usuario**:
  se escriben con **`chmod 644`** (no 600), dentro de una carpeta `secrets/` con
  permisos **700** (protege en el host). Con 600 el contenedor da
  `PermissionError: /run/secrets/<x>`.
- **Postgres y `_FILE` son excluyentes:** si llegan a la vez `POSTGRES_PASSWORD`
  (heredado del base) y `POSTGRES_PASSWORD_FILE` (override de prod), el entrypoint
  aborta (`both POSTGRES_PASSWORD and POSTGRES_PASSWORD_FILE are set`). En el
  override de prod **fijar `POSTGRES_PASSWORD: ""`** para que use solo el `_FILE`.
- Una credencial que haya tocado git se considera **quemada**: rotarla (no basta
  borrarla del repo).

---

## 7. Convenciones de Docker Compose

- **Volúmenes de datos** (BD, uploads): `external: true` con nombre fijo; **nunca**
  se recrean en un deploy.
- **Red de Traefik** (`traefik_public`): `external: true`; red interna propia.
- `restart: unless-stopped`; healthchecks en servicios con `depends_on:
  condition: service_healthy`.
- Build local en el compose base; imagen GHCR solo en el override de prod.
- Un override de runtime que cambia `image:` **debe** neutralizar el `build:`
  heredado (`build: !reset null`).

---

## 8. Seeding de datos: **una sola forma**

> El seeding de datos de referencia/catálogo en el arranque lo hace
> **EXCLUSIVAMENTE `app/scripts/bootstrap.py`** (idempotente), invocado por el
> `CMD` del backend tras `alembic upgrade head`.

Reglas:

1. **`bootstrap.py` es el dueño único** de los catálogos. Cada catálogo, un dueño.
   Las funciones `ensure_*` son **idempotentes**: comprueban existencia antes de
   insertar. Si la tabla tiene **varios constraints únicos** (p. ej.
   `tipos_vinculacion` con UNIQUE en `codigo` y en `nombre`), la comprobación debe
   cubrir **todos** (buscar por `codigo` **O** `nombre`) para evitar choques ante
   drift de datos.
2. **Las migraciones Alembic son solo esquema** (y, como mucho, transformación
   puntual de datos existentes durante ese cambio). **No** siembran catálogos de
   forma continua. Los seeds históricos en migraciones se dejan **idempotentes**
   (`ON CONFLICT DO NOTHING` sin columna), pero la fuente viva es bootstrap.
3. **Datos demo/mock** (`seed_demo_*`, `seed_mock_*`) son **categoría aparte,
   manual**; nunca corren en el arranque.

El `CMD` del backend:
```
wait_for_db  →  alembic upgrade head  →  python -m app.scripts.bootstrap  →  uvicorn
```

---

## 9. Catálogo de GitHub Secrets

| Secret                  | Uso                                                  | Sensible |
|-------------------------|------------------------------------------------------|----------|
| `<APP>_ENV_STAGING`     | bloque `.env` de staging (incluye credenciales)      | sí       |
| `ENV_PRODUCTION`        | bloque `.env` de producción (incluye credenciales)   | sí       |
| `GHCR_PAT`              | PAT `read:packages` para `docker login ghcr.io` (solo si las imágenes son privadas) | sí |
| `PORTAINER_WEBHOOK_URL` | webhook opcional de redeploy en Portainer            | —        |

`GITHUB_TOKEN` lo provee Actions (basta `permissions: packages: write`).

> Con runner self-hosted **ya no se usan** los secretos de SSH (`DEPLOY_HOST*`,
> `DEPLOY_USER`, `DEPLOY_KEY`, `DEPLOY_PORT`): pueden borrarse.
> Si los paquetes de GHCR se hacen **públicos**, `GHCR_PAT` tampoco hace falta.

---

## 10. Alta de una máquina en la cadena de despliegue

Resumen (detalle completo en `deploy/SELF_HOSTED_RUNNER.md`):

1. Usuario de despliegue (`deployer`) en grupo `docker` + escritura en
   `/opt/docker/apps/<app>`.
2. Descargar y registrar el runner (`config.sh --labels <app>-staging`,
   **como `deployer`**, nunca root).
3. Instalar como servicio systemd (`svc.sh install deployer`).
4. Verificar **Idle** en GitHub → Settings → Actions → Runners.

---

## 11. Checklist — aplicación Python nueva conforme

- ☐ `Dockerfile` con `USER` no-root.
- ☐ `docker-compose.yml` (build local) + `docker-compose.prod.yml` (GHCR + secrets).
- ☐ Patrón `<VAR>_FILE` en el código para toda credencial.
- ☐ `secrets/.gitkeep`; `.gitignore`/`.dockerignore` con lista blanca de `.env*` y `secrets/`.
- ☐ `scripts/deploy-remote-pull.sh` (materializa secrets a **644**, backup, pull, up, healthcheck, rollback).
- ☐ `docker-compose.prod.yml` con `POSTGRES_PASSWORD: ""` en `db`.
- ☐ Volúmenes de datos `external: true`.
- ☐ Seeding **solo** en `bootstrap.py` (idempotente, multi-constraint); migraciones = esquema.
- ☐ `.github/workflows/deploy.yml`: `build-and-push` en `ubuntu-latest`, deploy en `[self-hosted, <app>-staging/production]`.
- ☐ GitHub Secrets del catálogo creados.
- ☐ Runner self-hosted registrado en el VPS y en **Idle**.
- ☐ `.env.production` colocado en el VPS con `APP_DOMAIN`/`HEALTHCHECK_URL` que devuelva 200.

---

## 12. Lecciones registradas (problemas reales y su causa)

| Síntoma | Causa | Solución |
|---|---|---|
| `ssh: handshake failed: EOF` en el deploy | hardening cierra SSH público (VPN-only) | runner self-hosted |
| `cd: Permission denied` en el dir de deploy | `chown` deja el dir `750 deployer` | inspeccionar con `sudo`; no afecta al deploy |
| `both POSTGRES_PASSWORD and POSTGRES_PASSWORD_FILE are set` | base + override aportan ambas | `POSTGRES_PASSWORD: ""` en prod |
| `PermissionError: /run/secrets/<x>` | secret `600` y contenedor no-root con otro uid | materializar a `644` (dir `700`) |
| `duplicate key … _nombre_key` en seed | seed solo cubría un constraint único | `ensure_*` por todos los uniques / `ON CONFLICT DO NOTHING` |
| Múltiples mecanismos de seeding en conflicto | migraciones + bootstrap + scripts sembraban lo mismo | **una sola forma: `bootstrap.py`** |
