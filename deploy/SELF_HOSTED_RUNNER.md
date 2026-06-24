# Runner self-hosted para el deploy de SIGA

## Por qué

El runner self-hosted corre **dentro del propio VPS**: despliega **en local**,
junto a Docker, y solo abre conexiones **salientes** a GitHub (long-poll HTTPS).
Con ello el deploy **no depende de SSH/scp entrante** hacia el VPS ni de estar en
la VPN, y no expone ningún puerto entrante nuevo.

**Motivo (verificado):** el deploy anterior usaba `appleboy/scp-action`/`ssh-action`
desde un runner GitHub-hosted. Funcionó hasta el 30-may (run #147); desde el
hardening de los servidores (24-jun, runs #148+) falla con `ssh: handshake failed:
EOF`. Se comprobó relanzando el deploy forzando dos puertos distintos (22 y 35004):
**ambos dan el mismo EOF**, es decir, el TCP conecta pero el servidor corta el
handshake SSH **independientemente del puerto**. Conclusión: tras securizar los
VPS, el SSH entrante desde IPs externas (las de GitHub) está bloqueado **a
propósito**; no es un fallo del workflow ni se arregla cambiando puerto/clave.

Por eso el runner self-hosted es la vía correcta: corre **dentro del VPS**,
despliega **en local** y solo abre conexiones **salientes** a GitHub, sin depender
de SSH entrante.

El workflow (`.github/workflows/deploy.yml`) selecciona el runner por **labels**:

| Entorno      | VPS  | Labels                          |
|--------------|------|---------------------------------|
| STAGING      | VPS2 | `self-hosted`, `siga-staging`   |
| PRODUCCIÓN   | VPS1 | `self-hosted`, `siga-production`|

`build-and-push` sigue corriendo en GitHub (ubuntu-latest); solo el job de
**deploy** corre en el VPS.

## Requisitos previos en el VPS

El runner corre bajo el usuario **`deployer`** (el mismo que ya despliega la app).
No hace falta crear un usuario nuevo.

1. **Docker** y **docker compose** funcionando.
2. `deployer` en el grupo `docker` (para ejecutar `docker compose`):
   ```bash
   sudo usermod -aG docker deployer
   ```
3. `deployer` con escritura sobre el directorio de deploy
   (`/opt/docker/apps/SIGA`). Como ya despliega hoy, normalmente ya la tiene.

   Comprobar ambos:
   ```bash
   groups deployer              # debe aparecer "docker"
   ls -ld /opt/docker/apps/SIGA # deployer debe poder escribir ahí
   ```

## Instalar y registrar el runner (STAGING / VPS2)

1. En GitHub: **repo → Settings → Actions → Runners → New self-hosted runner →
   Linux**. Te dará un bloque con la URL de descarga y un **token de registro**
   (caduca en ~1 h). Cópialo.

2. En el VPS, como el usuario `deployer`:
   ```bash
   sudo -iu deployer
   mkdir -p ~/actions-runner && cd ~/actions-runner
   # (usa la URL/versión que muestre GitHub en ese momento)
   curl -o actions-runner-linux-x64.tar.gz -L \
     https://github.com/actions/runner/releases/download/vX.Y.Z/actions-runner-linux-x64-X.Y.Z.tar.gz
   tar xzf actions-runner-linux-x64.tar.gz

   ./config.sh \
     --url https://github.com/pepeluimoreno/siga \
     --token <TOKEN_DE_REGISTRO> \
     --name siga-staging-vps2 \
     --labels siga-staging \
     --unattended --replace
   ```
   > `config.sh` añade automáticamente el label base `self-hosted`; con
   > `--labels siga-staging` el runner queda con **`self-hosted, siga-staging`**,
   > que es lo que pide el workflow.

3. Instalar como servicio (arranca solo y sobrevive a reinicios):
   ```bash
   sudo ./svc.sh install deployer
   sudo ./svc.sh start
   sudo ./svc.sh status
   ```

## Producción (VPS1)

Igual que arriba, pero en VPS1 y con:
```
--name siga-prod-vps1 --labels siga-production
```

## Comprobar

- En GitHub: **Settings → Actions → Runners** debe mostrar el runner **Idle**
  con sus labels.
- Lanza el deploy (push a `master` para staging) y verifica que el job
  `deploy-staging` cae en el runner del VPS.

## Secretos que usa el deploy

- `ENV_STAGING` / `ENV_PRODUCTION`: contenido completo de `.env.production`
  (se materializa en el VPS antes de desplegar).
- `GHCR_PAT`: PAT con `read:packages` para `docker login ghcr.io` (pull de
  imágenes privadas).

> Los antiguos secretos de SSH (`DEPLOY_HOST*`, `DEPLOY_USER`, `DEPLOY_KEY`,
> `DEPLOY_PORT`) **ya no se usan** y pueden borrarse.

## Verificación post-deploy

Desde el VPS (o por la VPN):
```bash
cd /opt/docker/apps/SIGA
docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml exec -T backend alembic current
# debe mostrar el head:  v7w8x9y0z1a2 (head)
docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python -m app.scripts.smoke_test
```
