# Runner self-hosted para el deploy de SIGA

## Por qué

El runner self-hosted corre **dentro del propio VPS**: despliega **en local**,
junto a Docker, y solo abre conexiones **salientes** a GitHub (long-poll HTTPS).
Con ello el deploy **no depende de SSH/scp entrante** hacia el VPS ni de estar en
la VPN, y no expone ningún puerto entrante nuevo.

**Motivo (verificado):** el deploy anterior usaba `appleboy/scp-action`/`ssh-action`
desde un runner GitHub-hosted. Funcionó hasta el 30-may (run #147); desde el
hardening de los VPS (24-jun, runs #148+) falla con `ssh: handshake failed: EOF`.

Causa real, comprobada en VPS2:
- El SSH entrante desde Internet está **cerrado a propósito**. El acceso solo es
  posible **dentro de la VPN WireGuard**, que a su vez viaja **envuelta en
  WebSocket** (`wstunnel server --restrict-to localhost:51820 ws://0.0.0.0:8443`)
  para sortear el bloqueo del proveedor.
- nftables **desvía el puerto SSH público** (`tcp dport 35004 redirect to :8443`)
  hacia wstunnel y **descarta** 22/6543. Por eso un cliente SSH externo (GitHub, o
  tú sin VPN) conecta el TCP pero el handshake muere: habla SSH contra wstunnel,
  que espera WebSocket. Se reprodujo idéntico forzando puertos 22 y 35004.
- `wstunnel` está `--restrict-to localhost:51820` (solo WireGuard), así que **no**
  se puede tunelizar SSH por ahí: la única entrada externa es **unirse a la VPN**.

Conclusión: con SSH entrante cerrado por diseño, el runner self-hosted es la vía
correcta. Corre **dentro del VPS**, despliega **en local** y solo abre conexiones
**salientes** a GitHub; respeta el hardening sin abrir ni un puerto.

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
