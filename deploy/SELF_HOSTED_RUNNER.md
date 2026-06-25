# Runner self-hosted — instalación en una máquina de la cadena de despliegue

Manual paso a paso para incorporar una máquina (VPS) a la cadena de CI/CD de
SIGA como **runner self-hosted de GitHub Actions**. Incluye **todos los pasos**,
las **salidas esperadas** de cada comando y una sección de **problemas reales
encontrados y su solución** (registrados durante la puesta en marcha de VPS2 el
25-jun-2026).

> Guía operativa: la referencia normativa del despliegue está en
> `docs/despliegue.md` y en el *Estándar de Ingeniería · CI/CD, Secretos y
> Despliegue*. El diseño "SSH solo por la VPN" está en *Seguridad de la
> infraestructura — Europa Laica*.

---

## 1. Qué es y por qué (causa verificada)

Un **runner** es la máquina que ejecuta los pasos de un workflow de GitHub
Actions. Hay dos tipos:

- **GitHub-hosted** (`ubuntu-latest`): máquina en la nube de GitHub. Para
  desplegar en el VPS tendría que **entrar por SSH/scp** desde Internet.
- **Self-hosted**: una máquina **tuya** (el propio VPS) que abre una conexión
  **saliente** a GitHub (long-poll HTTPS) y recibe los trabajos por ahí. No
  expone ningún puerto entrante.

**Por qué SIGA usa self-hosted (verificado):** desde el hardening de los VPS
(jun-2026) el **SSH entrante está cerrado al público a propósito**. El acceso
solo es posible **dentro de la VPN WireGuard**, que viaja **encapsulada en
WebSocket** con `wstunnel` (Nodo50 filtra el UDP 51820 de WireGuard). En el
cortafuegos, nftables **desvía el puerto SSH público** (`tcp dport 35004 redirect
to :8443`, donde escucha `wstunnel --restrict-to localhost:51820`) y **descarta**
22/6543. Resultado: un runner GitHub-hosted **no puede** entrar por scp/ssh
(`ssh: handshake failed: EOF`). El runner self-hosted, al correr **dentro** del
VPS y salir **solo hacia** GitHub, esquiva todo eso **sin abrir ningún puerto**
ni tocar el hardening.

Selección del runner por **labels** en `.github/workflows/deploy.yml`:

| Entorno    | VPS  | Labels                           | Disparo                         |
|------------|------|----------------------------------|---------------------------------|
| Staging    | VPS2 | `self-hosted`, `siga-staging`    | push a `master`                 |
| Producción | VPS1 | `self-hosted`, `siga-production` | tag `v*` o `workflow_dispatch`  |

`build-and-push` sigue corriendo en GitHub-hosted (`ubuntu-latest`); **solo el
job de deploy** corre en el VPS.

---

## 2. Requisitos de la máquina

- **Linux x86_64** con **Docker** y **docker compose** operativos.
- Un **usuario de despliegue** en el grupo `docker` y con escritura sobre el
  directorio de deploy (`/opt/docker/apps/SIGA`). En el ecosistema de Europa
  Laica ese usuario es **`deployer`** (usuario de despliegue **común** de todas
  las apps del VPS).
- Salida HTTPS hacia `github.com` (la VPN/hardening no la bloquean: es saliente).

> **Seguridad — acoplamiento asumido:** el runner ejecuta el contenido de los
> workflows; al correr como `deployer`, comparte su identidad (clave SSH y acceso
> al resto de apps en `/opt/docker/apps`). Es el coste aceptado de usar un único
> usuario de despliegue. Si quieres aislamiento, crea un usuario dedicado (p. ej.
> `gh-runner`) con **solo** grupo `docker` + escritura en el dir de SIGA, y
> sustituye `deployer` por él en todos los pasos.

---

## 3. Paso 0 — Conocer el usuario de despliegue antes de tocarlo

No reutilices a ciegas una cuenta de función desconocida. Comprueba qué es y qué
hace:

```bash
getent passwd deployer                      # home y shell
id deployer                                  # grupos (¿docker? ¿sudo?)
ps -u deployer -o pid,etime,cmd 2>/dev/null || echo "sin procesos"
grep -rls 'User=deployer' /etc/systemd/system /lib/systemd/system 2>/dev/null || echo "ninguna unit systemd"
sudo crontab -l -u deployer 2>/dev/null || echo "sin crontab"
sudo grep -rh deployer /etc/sudoers /etc/sudoers.d/ 2>/dev/null || echo "no en sudoers"
sudo find /home /opt /srv /var /etc -xdev -user deployer 2>/dev/null | head -30
```

**Salida esperada / observada en VPS2:**

```
deployer:x:1002:1002::/home/deployer:/bin/bash
uid=1002(deployer) gid=1002(deployer) groups=1002(deployer),988(docker)
sin procesos de deployer
ninguna unit con User=deployer
sin crontab de deployer
deployer no esta en sudoers
/home/deployer/.ssh/id_ed25519
/opt/docker/apps/gsh/...            # deployer ya despliega GSH
```

Lectura: `deployer` ya está **en el grupo `docker`** (988), tiene **claves SSH**
propias y es el **usuario de despliegue de GSH** (y, por decisión, de todas las
apps). No está en `sudoers`. Conclusión: apto para reutilizar como runner de
SIGA.

---

## 4. Paso 1 — Preparar usuario y directorios

`deployer` ya existe y ya está en `docker`; solo hay que asegurar permisos y el
directorio del runner:

```bash
# (idempotente) grupo docker
sudo usermod -aG docker deployer

# dir de deploy de SIGA -> deployer
sudo chown -R deployer:deployer /opt/docker/apps/SIGA
ls -ld /opt/docker/apps/SIGA

# dir del runner
sudo mkdir -p /opt/actions-runner
sudo chown deployer:deployer /opt/actions-runner

# verificar Docker como deployer (proceso nuevo => toma el grupo)
sudo -u deployer bash -c 'docker ps >/dev/null 2>&1 && echo "docker OK" || echo "docker NO"'
uname -m
```

**Salida esperada:**

```
drwxr-x--- 10 deployer deployer 4096 may 27 18:28 /opt/docker/apps/SIGA
docker OK
x86_64
```

> ⚠️ El `chown -R` cambia la **propiedad** del árbol de deploy a `deployer`, y el
> directorio queda `750 deployer:deployer`. **Efecto colateral esperado:** otros
> usuarios (p. ej. `elaicatec`) ya **no entran** sin `sudo` (`cd: Permission
> denied`). El deploy no se ve afectado: corre como `deployer`. Para inspeccionar
> manualmente usa `sudo` o `sudo -u deployer …`.

---

## 5. Paso 2 — Obtener el token de registro (navegador)

En GitHub: repo **pepeluimoreno/siga → Settings → Actions → Runners → New
self-hosted runner → Linux**. Esa página muestra:

- el bloque **Download** (incluye la **versión** actual del runner, p. ej.
  `2.335.1`, en la URL del `curl`),
- el bloque **Configure** con un **token de registro** (`A...`, **caduca en
  ~1 h**).

---

## 6. Paso 3 — Descargar y registrar el runner

`deployer` puede ser cuenta no interactiva: se usa `sudo -u deployer <comando>`
(no `sudo -iu`) y un directorio dedicado. **Rellena `RUNNER_VERSION` y
`REG_TOKEN`** con lo de la página:

```bash
RUNNER_VERSION="2.335.1"     # del bloque Download
REG_TOKEN="AXXXXXXXXXXXXXXXXXXXXXXXXXXXX"   # del bloque Configure

# descarga + extracción
sudo -u deployer bash -c "cd /opt/actions-runner && \
  curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz && \
  tar xzf actions-runner.tar.gz && rm -f actions-runner.tar.gz"

# registro (config.sh DEBE correr como deployer, nunca root)
sudo -u deployer env HOME=/opt/actions-runner bash -c "cd /opt/actions-runner && \
  ./config.sh --url https://github.com/pepeluimoreno/siga \
    --token ${REG_TOKEN} \
    --name siga-staging-vps2 \
    --labels siga-staging \
    --unattended --replace"
```

`config.sh` añade automáticamente el label base `self-hosted`; con `--labels
siga-staging` el runner queda con **`self-hosted, siga-staging`** (lo que pide el
workflow).

**Salida esperada (`config.sh`):**

```
√ Connected to GitHub
# Runner Registration
√ Runner successfully added
√ Settings Saved.
```

---

## 7. Paso 4 — Dependencias del sistema (si hacen falta)

Si `config.sh` o el arranque se quejan de librerías (`libicu`, etc.):

```bash
sudo /opt/actions-runner/bin/installdependencies.sh
```

**Salida esperada (Ubuntu 24.04):** instala `liblttng-ust*` y **reutiliza
`libicu74`**, que es la correcta. Verás varios:

```
E: No se ha podido localizar el paquete libicu80   (… 79, 78, 77, 76, 75)
libicu74 ya está en su versión más reciente
-----------------------------
 Finish Install Dependencies
-----------------------------
```

> Esos `E: No se ha podido localizar libicu80…75` son **normales**: el script
> prueba versiones de la más nueva a la más vieja y se queda con `libicu74`. No
> son un error. Si aparece un aviso de **kernel pendiente** (`Pending kernel
> upgrade!`), no afecta al runner; planifica un reboot cuando puedas.

---

## 8. Paso 5 — Instalar como servicio systemd

El servicio se instala como root pero **corre como `deployer`**, y arranca solo
tras reinicios:

```bash
cd /opt/actions-runner
sudo ./svc.sh install deployer
sudo ./svc.sh start
sudo ./svc.sh status
```

**Salida esperada:**

```
Creating launch runner in /etc/systemd/system/actions.runner.pepeluimoreno-siga.siga-staging-vps2.service
Run as user: deployer
Run as uid: 1002
...
● actions.runner.pepeluimoreno-siga.siga-staging-vps2.service - GitHub Actions Runner (...)
     Loaded: loaded (...; enabled; preset: enabled)
     Active: active (running) since ...
   Main PID: ###### (runsvc.sh)
             └─###### ./externals/node20/bin/node ./bin/RunnerService.js
```

Lo clave: **`Active: active (running)`** y **`enabled`**.

---

## 9. Paso 6 — Verificar en GitHub

En **pepeluimoreno/siga → Settings → Actions → Runners** debe aparecer:

- **`siga-staging-vps2`** en estado **🟢 Idle**,
- labels **`self-hosted`, `siga-staging`**.

A partir de aquí, un **push a `master`** dispara `build-and-push` (en
GitHub-hosted) y luego `deploy-staging` **cae en este runner**.

---

## 10. Primer despliegue y verificación

Tras un merge a `master`, el runner ejecuta `scripts/deploy-remote-pull.sh`
(materializa secretos → backup BD → `pull` → `up -d` → migraciones idempotentes
→ healthcheck → rollback si falla). Comprueba el estado **con `sudo`** (el dir es
`750 deployer`):

```bash
sudo docker compose --env-file /opt/docker/apps/SIGA/.env.production \
  -f /opt/docker/apps/SIGA/docker-compose.yml \
  -f /opt/docker/apps/SIGA/docker-compose.prod.yml ps
```

**Estado sano esperado:** `siga_db` → `Up (healthy)`, `siga_backend` → `Up`,
`siga_frontend` → `Up`.

Verificación de migraciones / smoke test:

```bash
sudo docker compose --env-file /opt/docker/apps/SIGA/.env.production \
  -f /opt/docker/apps/SIGA/docker-compose.yml -f /opt/docker/apps/SIGA/docker-compose.prod.yml \
  exec -T backend alembic current     # debe mostrar el head
```

---

## 11. Problemas reales encontrados y su solución

Registro de lo que falló en la puesta en marcha de VPS2 y cómo se arregló (todos
los arreglos están en el repo):

### 11.1 `ssh: handshake failed: EOF` en el deploy por SSH (causa del cambio)
- **Síntoma:** el job `deploy-staging` (versión vieja con `appleboy/scp-action`)
  fallaba en el paso scp con `ssh: handshake failed: EOF`, idéntico en puertos 22
  y 35004.
- **Causa:** el hardening cierra el SSH público (ver §1). No es un bug del
  workflow.
- **Solución:** runner self-hosted (este manual). No se reabre SSH.

### 11.2 `cd: Permission denied` sobre `/opt/docker/apps/SIGA`
- **Causa:** tras `chown -R deployer`, el dir quedó `750 deployer:deployer`.
- **Solución:** es esperado; inspecciona con `sudo` o `sudo -u deployer`. No
  afecta al deploy.

### 11.3 Postgres `unhealthy` — `both POSTGRES_PASSWORD and POSTGRES_PASSWORD_FILE are set`
- **Síntoma:** `siga_db` en `Restarting (1)`; en `docker logs siga_db`:
  `error: both POSTGRES_PASSWORD and POSTGRES_PASSWORD_FILE are set (but are exclusive)`.
- **Causa:** el `docker-compose.yml` base define `POSTGRES_PASSWORD` (para dev) y
  el override de prod añade `POSTGRES_PASSWORD_FILE`; al combinarlos llegan las
  dos (el `unset` del script no basta porque compose reinterpola desde el
  `--env-file`).
- **Solución (repo):** en `docker-compose.prod.yml`, servicio `db`, fijar
  `POSTGRES_PASSWORD: ""` para neutralizar la var plana; postgres usa solo el
  `_FILE`.

### 11.4 Backend `PermissionError: /run/secrets/db_password`
- **Síntoma:** `siga_backend` en `Restarting (1)`; traceback con
  `PermissionError: [Errno 13] Permission denied: '/run/secrets/db_password'`.
- **Causa:** el script materializaba los secrets con `chmod 600` propiedad de
  `deployer` (uid 1002), pero el contenedor corre como usuario **no-root** con
  otro uid → no puede leer un fichero `600` ajeno.
- **Solución (repo):** materializar los secrets con `chmod 644`. El directorio
  `secrets/` sigue siendo `700` (protege en el host); el fichero `644` permite la
  lectura dentro del contenedor.
- **Recuperación inmediata sin redeploy:**
  `sudo chmod 644 /opt/docker/apps/SIGA/secrets/*.txt && sudo docker restart siga_backend`.

### 11.5 Seed no idempotente — `tipos_vinculacion_nombre_key` (pendiente, dev)
- **Síntoma:** backend revienta en el seed con
  `duplicate key value violates unique constraint "tipos_vinculacion_nombre_key"`
  (`ON CONFLICT (codigo) DO NOTHING` no cubre el conflicto por `nombre`).
- **Causa:** staging ya tiene una fila `Simpatizante` con otro `codigo`; el seed
  solo contempla conflicto por `codigo`.
- **Estado:** es un bug de aplicación (no de infra). Arreglo de una línea: usar
  `ON CONFLICT DO NOTHING` (sin columna) o comprobar también por `nombre`. Queda
  para desarrollo.

---

## 12. Operación y mantenimiento

```bash
cd /opt/actions-runner
sudo ./svc.sh status         # estado del servicio
sudo ./svc.sh stop           # parar
sudo ./svc.sh start          # arrancar
journalctl -u actions.runner.pepeluimoreno-siga.siga-staging-vps2.service -f   # logs

# desregistrar/retirar el runner (requiere un token de remove de GitHub)
sudo ./svc.sh uninstall
sudo -u deployer env HOME=/opt/actions-runner bash -c \
  'cd /opt/actions-runner && ./config.sh remove --token <REMOVE_TOKEN>'
```

Actualizar el runner: el propio runner se autoactualiza cuando GitHub lo
requiere; si se queda atrás, repetir §6-§8 con la versión nueva (`--replace`).

---

## 13. Producción (VPS1) — pendiente

Cuando se defina el destino de producción, repetir este manual **en VPS1** con:

```
--name siga-prod-vps1 --labels siga-production
```

> Nota: el doc de seguridad describe **VPS1 = infra** como hub de VPN/cortafuegos;
> confirmar si SIGA‑producción vivirá allí o en otra máquina antes de registrar
> su runner.

---

## 14. Registro as-built — STAGING (VPS2)

| Dato | Valor |
|---|---|
| Fecha | 25-jun-2026 |
| Host | VPS2 (`staging`, `10.9.0.1` por VPN) — Ubuntu 24.04 |
| Usuario del runner | `deployer` (uid 1002; grupo `docker` 988) |
| Versión del runner | `2.335.1` (linux-x64) |
| Directorio del runner | `/opt/actions-runner` |
| Nombre del runner | `siga-staging-vps2` |
| Labels | `self-hosted`, `siga-staging` |
| Servicio systemd | `actions.runner.pepeluimoreno-siga.siga-staging-vps2.service` (`enabled`, corre como `deployer`) |
| Dir de deploy | `/opt/docker/apps/SIGA` (propiedad de `deployer`, `750`) |

## 15. Secretos que usa el deploy

- `SIGA_ENV_STAGING` (staging) / `ENV_PRODUCTION` (producción): bloque `.env`
  completo (incluye credenciales); el script lo vuelca a `.env.production` con
  `umask 077` y materializa los secretos.
- `GHCR_PAT` (opcional): PAT con `read:packages` para `docker login ghcr.io` si
  las imágenes de GHCR son **privadas**. Si los paquetes son **públicos**, no se
  necesita.

> Los antiguos secretos de SSH (`DEPLOY_HOST*`, `DEPLOY_USER`, `DEPLOY_KEY`,
> `DEPLOY_PORT`) **ya no se usan** con el runner self-hosted y pueden borrarse.
