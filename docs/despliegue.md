# Despliegue — SIGA

Conforme al **Estándar de Ingeniería · CI/CD, Secretos y Despliegue** (v1.0).
La rama implementa el estándar **completo** (dev + staging + producción). De
momento solo se pondrá en marcha el **entorno de desarrollo (optiplex-790)**;
staging y producción quedan listos para cuando se activen.

## Entornos

| Entorno     | Dónde         | Imagen      | Disparo                                            |
|-------------|---------------|-------------|----------------------------------------------------|
| Desarrollo  | optiplex-790  | build local | manual (`scripts/dev-up.sh`)                       |
| Staging     | VPS2          | GHCR        | push a `master`                                    |
| Producción  | VPS1          | GHCR        | tag `v*` o `workflow_dispatch` (deploy_production)  |

Regla base/override: `docker-compose.yml` es desarrollo (build local).
Staging/producción superponen `docker-compose.prod.yml` (imagen GHCR +
`pull_policy: always` + Docker secrets), con `-f docker-compose.yml -f docker-compose.prod.yml`.

## Desarrollo (optiplex-790)

```bash
cp .env.example .env          # rellena los marcadores
./scripts/dev-up.sh           # up -d --build (base + override dev)
./scripts/dev-up.sh logs
./scripts/dev-up.sh down
```
Acceso: `https://siga.optiplex-790`. En desarrollo las credenciales van por
`.env` (env var); no se usan Docker secrets.

## Staging / Producción

Automático vía `.github/workflows/deploy.yml`:

1. **build-and-push** publica `ghcr.io/pepeluimoreno/siga-{backend,frontend}` con
   `latest`, el SHA y, en releases, la versión semántica.
2. **deploy-staging** (push a `master`) y **deploy-production** (tag `v*` o
   dispatch) copian compose+scripts por scp y ejecutan `scripts/deploy-remote-pull.sh`.
3. El `.env.production` se vuelca en el servidor desde el GitHub Secret
   `ENV_STAGING` / `ENV_PRODUCTION` (umask 077).

`scripts/deploy-remote-pull.sh` hace: materializar secretos (env → Docker
secret + `unset`), backup de BD, registrar imagen previa, `pull` → `up -d`,
migraciones idempotentes (entrypoint), healthcheck contra `HEALTHCHECK_URL` y
**rollback** a la imagen previa si falla.

## Secretos (§4.5)

El código lee toda credencial con `<VAR>_FILE` (Docker secret) y cae a `<VAR>`
(env) por compatibilidad. Lógica en `backend/app/core/secrets.py`:

- `Settings` (pydantic) aplica `<CAMPO>_FILE` con prioridad sobre env (validador
  previo): `db_password`, `jwt_secret`, `smtp_password`…
- Fuera de `Settings`: PayPal, cifrado y bootstrap usan `read_secret_env`.

Secretos materializados (de env var a `/run/secrets`): `db_password`,
`jwt_secret`, `smtp_password`, `encryption_key`, `paypal_client_secret`,
`initial_admin_password`.

## Catálogo de GitHub Secrets (§6)

| Secret                  | Uso                                            | Sensible |
|-------------------------|------------------------------------------------|----------|
| `DEPLOY_HOST`           | host SSH de producción (VPS1)                  | —        |
| `DEPLOY_HOST_STAGING`   | host SSH de staging (VPS2)                      | —        |
| `DEPLOY_USER`           | usuario SSH de despliegue                       | —        |
| `DEPLOY_KEY`            | clave SSH privada de despliegue                 | sí       |
| `DEPLOY_PORT`           | puerto SSH (si no es 22)                         | —        |
| `GHCR_PAT`              | PAT para `docker login ghcr.io` (registro privado) | sí   |
| `ENV_STAGING`           | bloque `.env` de staging (incluye credenciales) | sí       |
| `ENV_PRODUCTION`        | bloque `.env` de producción (incluye credenciales) | sí    |
| `PORTAINER_WEBHOOK_URL` | webhook opcional de redeploy en Portainer        | —        |

`GITHUB_TOKEN` lo provee Actions; basta `permissions: packages: write`.

## Estructura conforme

- `docker-compose.yml` — base, build local (`image: …-local:dev`, `restart: unless-stopped`).
- `docker-compose.dev.yml` — override de desarrollo (hot-reload + Traefik).
- `docker-compose.prod.yml` — override GHCR + `pull_policy` + Docker secrets.
- `scripts/dev-up.sh` — arranque en desarrollo.
- `scripts/deploy-remote-pull.sh` — despliegue server-side (backup, secretos, healthcheck, rollback).
- `.github/workflows/deploy.yml` — build→GHCR + deploy staging/producción.
- `.gitignore` — lista blanca de `.env*` y `secrets/*` (solo `.gitkeep`).
- `.env.example` (dev) y `.env.production.example` (staging/prod) — solo marcadores.
- `secrets/.gitkeep` — carpeta de Docker secrets versionada vacía.

## Checklist — release a producción (§10)

- [ ] Validado en staging (push a `master` verde).
- [ ] `.env.production` (ENV_PRODUCTION) con credenciales rotadas y vigentes.
- [ ] `HEALTHCHECK_URL` responde 200.
- [ ] El scp del workflow copia todos los compose que el script referencia.
- [ ] Tag `vAAAA.MM.DD-descripcion` creado y empujado.
- [ ] Tras el deploy: healthcheck verde y verificación funcional (p.ej. envío real de correo).

## Notas / cleanup pendiente (fuera del estándar)

- El `docker-compose.yml` base monta un dump SQL de desarrollo
  (`./01_…sql:/tmp/dump.sql:ro`). En staging/prod ese fichero no existe; conviene
  moverlo al override de desarrollo para no crear un montaje vacío en el servidor.
