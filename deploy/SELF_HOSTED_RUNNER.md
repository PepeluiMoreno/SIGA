# Runner self-hosted para el deploy de SIGA

## Por qué

El VPS **solo admite SSH por la VPN** (`10.9.0.x`): no es accesible por SSH desde
Internet (el `22` está filtrado upstream y el `35004` público no llega al sshd).
Por eso un runner GitHub-hosted no puede entrar por `scp`/`ssh`.

La solución operativa **sin perder seguridad** es un **runner self-hosted** en el
propio VPS:

- Solo abre conexiones **salientes** a GitHub (long-poll HTTPS). **No expone
  ningún puerto entrante** → cero superficie de ataque nueva.
- Ejecuta el despliegue **localmente**, junto a Docker. Ya no hay scp/ssh/VPN.

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
2. `deployer` debe poder hablar con Docker. Ver **"Acceso a Docker y seguridad"**
   más abajo para elegir entre grupo `docker` (simple, root-equivalente) o
   **Docker rootless** (recomendado, mínimo privilegio).
3. `deployer` debe tener escritura sobre el directorio de deploy
   (`/opt/docker/apps/SIGA`). Como ya despliega hoy, normalmente ya la tiene.
   Comprobar:
   ```bash
   groups deployer              # ver si está en "docker" (solo si vas por grupo docker)
   ls -ld /opt/docker/apps/SIGA # deployer debe poder escribir ahí
   ```

## Acceso a Docker y seguridad

> **Importante:** pertenecer al grupo `docker` equivale a ser **root** en el host
> (`docker run -v /:/host ... chroot /host` da control total). Además el runner
> **ejecuta el contenido de los workflows**. Elige el modelo de acceso conscientemente.

**Opción recomendada — Docker rootless** (el daemon corre como `deployer`, sin root;
un escape de contenedor te deja como usuario sin privilegios, no como root):
```bash
sudo -iu deployer
dockerd-rootless-setuptool.sh install
# exportar el socket del usuario (añadir también al entorno del runner, ver abajo)
echo 'export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock' >> ~/.bashrc
# permitir que el daemon siga vivo sin sesión interactiva
sudo loginctl enable-linger deployer
```
Notas: puertos <1024 necesitan ajuste; `--privileged` no aplica. Para un compose
de app + db suele funcionar sin cambios.

**Opción simple — grupo `docker`** (root-equivalente; acéptalo solo con candados:
usuario dedicado, *GitHub Environment* con aprobación requerida y branch protection):
```bash
sudo usermod -aG docker deployer
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
   > **Con Docker rootless**, el servicio necesita ver el socket del usuario.
   > Asegúrate de que `DOCKER_HOST=unix:///run/user/<uid>/docker.sock` esté en
   > el entorno del runner: añádelo a `~/actions-runner/.env` (lo lee el runner)
   > o exporta `DOCKER_HOST` en el `.bashrc` de `deployer` antes de instalar el
   > servicio. Verifica con un job de prueba que `docker ps` responde.

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
