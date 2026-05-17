# Entorno y patrón de despliegue

## Resumen ejecutivo

El desarrollo activo ocurre en el **Optiplex-790** (máquina física en la red local, accedida por SSH o VSCode Remote SSH). El código vive en `/opt/docker/apps/SIGA` directamente en esa máquina. Los cambios se prueban ahí y, cuando son estables, se hace push a `master`, lo que dispara un pipeline de GitHub Actions que despliega automáticamente en staging (`vps2.europalaica.org`).

---

## Entorno de desarrollo — Optiplex-790

### Arranque

```bash
# SIEMPRE usar el compose dev:
docker compose --env-file .env.dev -f docker-compose.dev.yml up -d

# Primera vez o cuando cambien dependencias Python/npm (requiere build):
docker compose --env-file .env.dev -f docker-compose.dev.yml up -d --build
```

> **CRÍTICO**: usar `docker compose --env-file .env.dev` SIN `-f docker-compose.dev.yml` levanta el compose base, que **no tiene bind mounts**. Los cambios en el código no se reflejan en el contenedor y hay que hacer rebuild. Siempre especificar el archivo dev.

### Contenedores dev

| Contenedor | Nombre | Notas |
|---|---|---|
| Backend | `siga_dev_backend` | Python / FastAPI / uvicorn --reload |
| Frontend | `siga_dev_frontend` | node:22-alpine con Vite dev server (HMR) |
| Base de datos | `siga_dev_db` | postgres:17-alpine, volumen `pgdata_dev` |

### Bind mounts activos

Los siguientes paths del host se montan directamente en el contenedor backend:

| Host | Contenedor | Efecto |
|---|---|---|
| `./backend/app` | `/app/app` | Hot-reload del código Python |
| `./backend/main.py` | `/app/main.py` | Hot-reload del punto de entrada |
| `./backend/alembic` | `/app/alembic` | Cambios en migraciones reflejados sin rebuild |
| `./frontend` | `/app` | HMR de Vue/Vite (node_modules en volumen separado) |

### Secuencia de arranque del backend

El contenedor backend ejecuta en orden:

1. `python -m app.scripts.wait_for_db` — espera a que Postgres responda
2. `alembic upgrade head` — aplica migraciones pendientes **automáticamente**
3. `python -m app.scripts.bootstrap` — siembra datos iniciales (admin, catálogos)
4. `uvicorn main:app --reload` — arranca la API con hot-reload

> Las migraciones **no son manuales** en desarrollo. Se aplican solas al arrancar el backend. Para forzar una migración en caliente: `docker exec siga_dev_backend alembic upgrade head`.

### Hot-reload

| Capa | Mecanismo | Tiempo |
|---|---|---|
| Frontend `.vue`, `.js`, `.css` | Vite HMR vía WebSocket (clientPort 443 → Traefik → :3000) | < 1 s |
| Backend `.py` (app/) | uvicorn `--reload` con watchfiles | 1-3 s |
| Migraciones Alembic | Automático al reiniciar el backend | — |

### Acceso web

Traefik ya corre en el Optiplex con dnsmasq. El frontend es accesible en:
- `http://siga.optiplex-790`
- `https://siga.optiplex-790` (certificado mkcert local)

El backend **no está expuesto directamente**: Vite proxea `/graphql → http://backend:8000` dentro de la red Docker interna.

### Variables de entorno dev

El archivo `.env.dev` (ignorado por git) contiene los valores locales. Partir de `.env.staging.example` y ajustar:

```
POSTGRES_USER=siga
POSTGRES_PASSWORD=...
POSTGRES_DB=siga
JWT_SECRET=...
APP_PREFIX=siga
APP_DEV_DOMAIN=siga.optiplex-790
INITIAL_ADMIN_EMAIL=...
INITIAL_ADMIN_PASSWORD=...
```

### El dump MySQL

El archivo `./01_europa_laica_com-2026_02_17.sql` (dump de la BD antigua en MySQL) está montado como `/tmp/dump.sql:ro` en el contenedor **base** (`docker-compose.yml`). En el compose dev no está montado por defecto; si se necesita para scripts de seeding, añadir temporalmente el volumen o copiar el archivo dentro del contenedor.

---

## Particularidades de Alembic con asyncpg

### El problema de `target_metadata` y los tipos Enum

En `alembic/env.py`, la función `do_run_migrations` **no debe** pasar `target_metadata` a `context.configure()`:

```python
def do_run_migrations(connection):
    context.configure(
        connection=connection,
        # target_metadata=target_metadata,  ← NO incluir aquí
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()
```

**Por qué**: cuando `target_metadata` está presente, el sistema de eventos DDL de SQLAlchemy registra listeners `before_create` para todos los tipos Enum de los modelos. Cuando una migración llama a `op.create_table(...)` con una columna Enum, esos listeners emiten `CREATE TYPE nombre_enum` automáticamente — aunque la migración ya lo haya creado con `op.execute("CREATE TYPE ...")` momentos antes. El resultado es `DuplicateObjectError: type "X" already exists`.

`target_metadata` solo es necesario para `alembic revision --autogenerate`. Para ejecutar migraciones (`alembic upgrade head`) no se necesita.

### Migraciones con enums explícitos

Las migraciones que crean tipos Enum propios siguen este patrón:

```python
def upgrade() -> None:
    op.execute("CREATE TYPE mi_enum AS ENUM ('A', 'B', 'C')")
    op.create_table(
        'mi_tabla',
        sa.Column('campo', sa.Enum('A', 'B', 'C', name='mi_enum', create_type=False), ...),
        ...
    )

def downgrade() -> None:
    op.drop_table('mi_tabla')
    op.execute("DROP TYPE IF EXISTS mi_enum")
```

La clave: `create_type=False` en `sa.Enum` dentro de `op.create_table`, porque el tipo ya se creó en el `op.execute` anterior.

### Módulo económico (pendiente)

La migración `m012` (tablas de contabilidad y tesorería) está **eliminada** temporalmente. El módulo económico se implementará como unidad completa más adelante. Los modelos Python del módulo (`app/modules/economico/`) existen y están importados (necesarios para resolver relaciones SQLAlchemy como `FormaPago` en `Miembro`), pero las tablas correspondientes aún no están en la BD. Las consultas GraphQL a esos endpoints fallarán en la BD hasta que se añada la migración.

La cadena de migraciones salta de `m011` a `m013` (el `down_revision` de m013 apunta a m011).

---

## Compose base (`docker-compose.yml`)

Sirve como base compartida entre desarrollo y staging. Características:

- No tiene bind mounts de código (el código se hornea en la imagen al hacer `build`).
- `restart: always` (en staging se quiere auto-recuperación; en dev usar `unless-stopped`).
- No expone puertos Traefik (staging los añade via `docker-compose.staging.yml`).
- Contenedores se llaman `${APP_PREFIX}_backend`, etc. (con `.env.dev` → `siga_backend`, `siga_frontend`, `siga_db`).

> Si se arranca con solo `docker compose --env-file .env.dev up`, se levantan los contenedores del compose base (`siga_backend`, `siga_frontend`) sin bind mounts. Cualquier cambio en el código requiere `docker compose ... build backend` y luego `up -d`. Es el modo "producción local" y no es lo que queremos en desarrollo.

---

## Entorno de staging — vps2.europalaica.org

El push a `master` dispara el pipeline de GitHub Actions:

1. **Job `build`**: construye imágenes backend y frontend, las publica en GHCR con tags `latest` y `${{ github.sha }}`.
2. **Job `deploy`** (SSH a vps2 via `appleboy/ssh-action`):
   - `git pull` para actualizar compose files.
   - Login GHCR con `secrets.GITHUB_TOKEN`.
   - Escribe `.env.staging` desde el secret `SIGA_ENV_STAGING`.
   - `docker compose -f docker-compose.yml -f docker-compose.staging.yml pull && up -d --remove-orphans`.

### Topología staging

- **Backend**: imagen GHCR, detrás de Traefik existente en vps2 (network `traefik_public`).
- **Frontend**: imagen `nginx:alpine` con bundle estático, detrás de Traefik.
- **Postgres**: red interna, no expuesto.
- URL pública: `siga.staging.europalaica.org`.

### Secrets de GitHub requeridos

| Secret | Contenido |
|---|---|
| `DEPLOY_HOST` | `vps2.europalaica.org` |
| `DEPLOY_USER` | usuario SSH (`elaicatec`) |
| `DEPLOY_KEY` | clave SSH privada |
| `SIGA_ENV_STAGING` | contenido completo del `.env.staging` |

### Imágenes y nombres en staging

- Imágenes: `ghcr.io/pepeluimoreno/siga-backend` y `ghcr.io/pepeluimoreno/siga-frontend`.
- Contenedores: `${APP_PREFIX}_backend`, `${APP_PREFIX}_frontend`, `${APP_PREFIX}_db` (APP_PREFIX=siga en staging).

---

## Política de borrado: soft-delete por defecto + papelera + hard-delete restringido

Regla general: **ningún borrado destruye datos por defecto**. Todo modelo que herede `BaseModel` ya incluye `eliminado`/`fecha_eliminacion`/`fecha_modificacion` y se elimina marcando `eliminado=True` (soft-delete).

### Papelera de reciclaje (Trash)

- Cada módulo expone una vista de "Papelera" donde se listan los registros con `eliminado=True`.
- Desde la papelera se puede **restaurar** (`eliminado=False`) o **borrar permanentemente** (hard-delete).
- Los registros en papelera **no aparecen** en las consultas habituales: las queries por defecto filtran `eliminado=False`.

### Modal de confirmación de borrado (soft-delete)

Toda acción de borrado en la UI abre un modal que cumple:

1. **Advertencia explícita de cascada**: lista clara y completa de qué entidades relacionadas quedarán afectadas.
2. **Checkbox "Borrado permanente"** que activa hard-delete en lugar de soft-delete.
3. El checkbox de **borrado permanente solo es visible/funcional para usuarios con rol de superadministrador**.
4. Botón de confirmación destructivo (rojo) y botón de cancelar prominente.

### Hard-delete

- Elimina físicamente el registro de la BD.
- **Solo disponible para `SUPERADMIN`**.
- Auditoría: cada hard-delete genera entrada en `logs_auditoria` con `accion=ELIMINAR` y copia del registro en `datos_anteriores`.

---

## Configuración SMTP — patrón híbrido (.env + BD)

El servicio de email (`app/core/email_service.py`) usa un patrón híbrido con la siguiente prioridad:

1. **Variables de entorno / secreto del orquestador** (`SMTP_HOST` presente → usa .env)
2. **Tabla `configuracion` en BD** (fallback cuando no hay variables de entorno)

### Variables de entorno reconocidas

```
SMTP_HOST=panel.europalaica.com
SMTP_PORT=587
SMTP_USERNAME=laicismo.org
SMTP_PASSWORD=...
SMTP_FROM=                    # opcional; si vacío usa SMTP_USERNAME
SMTP_ENCRYPTION=tls           # tls | ssl | none
```

Añadir al `.env.staging` (secret `SIGA_ENV_STAGING` en GitHub) y al `.env.dev` local si se quiere usar SMTP en desarrollo.

### Por qué este patrón

- En **producción/staging**: las credenciales van en el secreto del orquestador (Docker secret, GitHub secret), nunca en BD ni en código. El cambio de credenciales requiere actualizar el secret y reiniciar el contenedor.
- En **desarrollo**: si no hay variables de entorno, el backend cae a la configuración guardada en BD, editable desde la UI en *Parámetros Generales → Autenticación y Email*. Útil para pruebas sin tocar el servidor.

### Validación en envío

`EmailService.enviar()` comprueba que `host`, `usuario` y `password` estén rellenos antes de intentar la conexión. Si faltan, lanza `ValueError` con el detalle de qué campos faltan. El error llega al frontend como mensaje GraphQL legible.

---

## DNS y certificados TLS locales (Optiplex-790)

El Optiplex corre **dnsmasq** con wildcard `address=/optiplex-790/192.168.1.141`. Cualquier subdominio `*.optiplex-790` resuelve a la IP del Optiplex sin configuración adicional.

Para acceder desde otros equipos de la red local: apuntar DNS primario a `192.168.1.141`.

Los certificados TLS están generados con **mkcert** (CA local instalada en el Optiplex):

```bash
# Certificados en:
/opt/docker/apps/traefik/certs/local.crt
/opt/docker/apps/traefik/certs/local.key
# Generados para: *.optiplex-790
# Expiran en 3 años desde la generación
```

Traefik monta esa carpeta como `/certs:ro` y la usa como certificado por defecto en el entrypoint `websecure`.
