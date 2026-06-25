# Despliegue — SIGA

Conforme al **Estándar de Ingeniería · CI/CD, Secretos y Despliegue** (v1.0).
La rama implementa el estándar **completo** (dev + staging + producción).
**Staging (VPS2)** ya está activo vía **runner self-hosted** (push a `master`);
producción (VPS1) queda lista para cuando se defina su destino y se registre su
runner.

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

1. **build-and-push** (runner GitHub-hosted) publica
   `ghcr.io/pepeluimoreno/siga-{backend,frontend}` con `latest`, el SHA y, en
   releases, la versión semántica.
2. **deploy-staging** (push a `master`) y **deploy-production** (tag `v*` o
   dispatch) corren en un **runner self-hosted instalado en el propio VPS**
   (selección por labels), copian compose+scripts **en local** (`cp`) y ejecutan
   `scripts/deploy-remote-pull.sh`.
3. El `.env.production` se vuelca en el servidor desde el GitHub Secret
   `SIGA_ENV_STAGING` / `ENV_PRODUCTION` (umask 077).

> **Por qué self-hosted y no SSH:** desde el hardening de los VPS (jun-2026) el
> SSH entrante está cerrado al público (solo VPN WireGuard‑sobre‑wstunnel; ver
> el doc *Seguridad de la infraestructura — Europa Laica*). Un runner
> GitHub-hosted no puede entrar por scp/ssh. El runner self-hosted corre dentro
> del VPS, sale **solo hacia** GitHub y despliega en local sin abrir puertos.
> Instalación y registro: **`deploy/SELF_HOSTED_RUNNER.md`**.

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
| `GHCR_PAT`              | PAT (`read:packages`) para `docker login ghcr.io` (registro privado) | sí   |
| `SIGA_ENV_STAGING`      | bloque `.env` de staging (incluye credenciales) | sí       |
| `ENV_PRODUCTION`        | bloque `.env` de producción (incluye credenciales) | sí    |
| `PORTAINER_WEBHOOK_URL` | webhook opcional de redeploy en Portainer        | —        |

`GITHUB_TOKEN` lo provee Actions; basta `permissions: packages: write`.

> Los secretos de SSH (`DEPLOY_HOST`, `DEPLOY_HOST_STAGING`, `DEPLOY_USER`,
> `DEPLOY_KEY`, `DEPLOY_PORT`) **ya no se usan** con el runner self-hosted y
> pueden borrarse del repo.

## Runner self-hosted — registro de instalación

Guía completa de instalación/registro: **`deploy/SELF_HOSTED_RUNNER.md`**.
Selección por labels en el workflow:

| Entorno    | VPS  | Labels                           |
|------------|------|----------------------------------|
| Staging    | VPS2 | `self-hosted`, `siga-staging`    |
| Producción | VPS1 | `self-hosted`, `siga-production` |

### As-built — STAGING (VPS2), 25-jun-2026

| Dato | Valor |
|---|---|
| Host | VPS2 (`staging`, `10.9.0.1` por VPN) — Ubuntu 24.04 |
| Usuario del runner | `deployer` (usuario de despliegue común del VPS; grupo `docker`) |
| Versión del runner | `2.335.1` (linux-x64) |
| Directorio | `/opt/actions-runner` |
| Nombre del runner | `siga-staging-vps2` |
| Labels | `self-hosted`, `siga-staging` |
| Servicio systemd | `actions.runner.pepeluimoreno-siga.siga-staging-vps2.service` (`enabled`, corre como `deployer`) |
| Dir de deploy | `/opt/docker/apps/SIGA` (propiedad de `deployer`) |

Operación del servicio:
```bash
cd /opt/actions-runner
sudo ./svc.sh status      # estado
sudo ./svc.sh stop|start  # parar/arrancar
# desregistrar (si se retira el runner):
sudo ./svc.sh uninstall && sudo -u deployer ./config.sh remove --token <TOKEN>
```

### Producción (VPS1) — pendiente

El runner de producción se instalará en VPS1 con `--labels siga-production`
**cuando se defina el destino de producción** (ver nota: el doc de seguridad
describe VPS1 como hub de VPN/cortafuegos; confirmar si SIGA‑prod vivirá allí).

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
- [ ] `HEALTHCHECK_URL` (o `APP_DOMAIN`) responde 200 (ojo si hay basic-auth delante).
- [ ] El runner self-hosted del entorno está **Idle** en GitHub (Settings → Actions → Runners).
- [ ] El workflow copia (`cp`) todos los compose que el script referencia.
- [ ] Tag `vAAAA.MM.DD-descripcion` creado y empujado.
- [ ] Tras el deploy: healthcheck verde y verificación funcional (p.ej. envío real de correo).

## Notas / cleanup pendiente (fuera del estándar)

- El `docker-compose.yml` base monta un dump SQL de desarrollo
  (`./01_…sql:/tmp/dump.sql:ro`). En staging/prod ese fichero no existe; conviene
  moverlo al override de desarrollo para no crear un montaje vacío en el servidor.
