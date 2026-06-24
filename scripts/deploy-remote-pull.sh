#!/usr/bin/env bash
# Despliegue server-side de SIGA en STAGING (VPS2) / PRODUCCIÓN (VPS1).
# Estándar de Ingeniería §5.3.
#
# Responsabilidades:
#   - cargar .env.production (debe existir en el servidor)
#   - permitir override de IMAGE_TAG vía DEPLOY_IMAGE_TAG (lo pasa el CI)
#   - usar  -f docker-compose.yml -f docker-compose.prod.yml (+ COMPOSE_EXTRA_FILE)
#   - materializar las credenciales sensibles como Docker secret (+ unset)
#   - backup de la BD antes de migrar
#   - registrar la imagen previa para rollback
#   - pull → up -d → migraciones idempotentes (las aplica el entrypoint del backend)
#   - healthcheck con reintentos; si falla, rollback a la imagen previa
set -euo pipefail

cd "$(dirname "$0")/.."

ENV_FILE="${ENV_FILE:-.env.production}"
[ -f "$ENV_FILE" ] || { echo "ERROR: falta $ENV_FILE en el servidor." >&2; exit 1; }
set -a; . "./$ENV_FILE"; set +a

export IMAGE_TAG="${DEPLOY_IMAGE_TAG:-${IMAGE_TAG:-latest}}"
APP_PREFIX="${APP_PREFIX:-siga}"
BACKEND_IMG="${IMAGE_NAME_BACKEND:-ghcr.io/pepeluimoreno/siga-backend}"
FRONTEND_IMG="${IMAGE_NAME_FRONTEND:-ghcr.io/pepeluimoreno/siga-frontend}"

COMPOSE=(docker compose --env-file "$ENV_FILE" -f docker-compose.yml -f docker-compose.prod.yml)
[ -n "${COMPOSE_EXTRA_FILE:-}" ] && COMPOSE+=(-f "$COMPOSE_EXTRA_FILE")

# ── Materialización de secretos: env var → Docker secret (fichero) ──────────────
# Se escribe siempre el fichero (vacío si la fuente está vacía) para que el
# compose encuentre todos los secrets declarados; tras escribir, se hace unset
# para que la variable plana no llegue al contenedor.
install -d -m 700 secrets
materialize_secret() {  # $1 = ENV_VAR  $2 = nombre_secret
  local var="$1" name="$2" val="${!1:-}"
  printf '%s' "$val" > "secrets/${name}.txt"
  chmod 600 "secrets/${name}.txt"
  unset "$var"
}
materialize_secret POSTGRES_PASSWORD       db_password
materialize_secret JWT_SECRET              jwt_secret
materialize_secret SMTP_PASSWORD           smtp_password
materialize_secret ENCRYPTION_KEY          encryption_key
materialize_secret PAYPAL_CLIENT_SECRET    paypal_client_secret
materialize_secret INITIAL_ADMIN_PASSWORD  initial_admin_password

# ── Login a GHCR (si el registro es privado) ───────────────────────────────────
if [ -n "${GHCR_PAT:-}" ]; then
  echo "$GHCR_PAT" | docker login ghcr.io -u "${GHCR_USER:-pepeluimoreno}" --password-stdin
fi

# ── Registrar imagen previa para rollback ──────────────────────────────────────
PREV_BACKEND="$(docker inspect --format '{{.Image}}' "${APP_PREFIX}_backend" 2>/dev/null || true)"
PREV_FRONTEND="$(docker inspect --format '{{.Image}}' "${APP_PREFIX}_frontend" 2>/dev/null || true)"

# ── Backup de la BD antes de migrar (si el servicio db está en marcha) ──────────
if "${COMPOSE[@]}" ps --status running db 2>/dev/null | grep -q db; then
  mkdir -p backups
  STAMP="$(date +%Y%m%d-%H%M%S)"
  echo "→ Backup de BD en backups/db-${STAMP}.sql.gz"
  "${COMPOSE[@]}" exec -T db sh -c \
    'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "backups/db-${STAMP}.sql.gz" || \
    echo "AVISO: backup falló (¿primer despliegue?), continúo."
fi

rollback() {
  echo "✗ Healthcheck fallido — revirtiendo a la imagen previa." >&2
  if [ -n "$PREV_BACKEND" ];  then docker tag "$PREV_BACKEND"  "${BACKEND_IMG}:rollback";  fi
  if [ -n "$PREV_FRONTEND" ]; then docker tag "$PREV_FRONTEND" "${FRONTEND_IMG}:rollback"; fi
  if [ -n "$PREV_BACKEND" ] && [ -n "$PREV_FRONTEND" ]; then
    IMAGE_TAG=rollback "${COMPOSE[@]}" up -d --remove-orphans
    echo "↩ Rollback aplicado." >&2
  else
    echo "No hay imagen previa para revertir (primer despliegue)." >&2
  fi
  exit 1
}

# ── Pull → up (las migraciones idempotentes las aplica el entrypoint) ───────────
echo "→ Pull de imágenes (IMAGE_TAG=${IMAGE_TAG})"
"${COMPOSE[@]}" pull
echo "→ Levantando servicios"
"${COMPOSE[@]}" up -d --remove-orphans

# ── Healthcheck con reintentos ─────────────────────────────────────────────────
URL="${HEALTHCHECK_URL:-https://${APP_DOMAIN}/}"
echo "→ Healthcheck contra ${URL}"
ok=0
for i in $(seq 1 "${HEALTHCHECK_RETRIES:-20}"); do
  code="$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 8 "$URL" 2>/dev/null || true)"
  if [ "$code" = "200" ]; then ok=1; echo "  healthcheck OK (200) en intento $i"; break; fi
  echo "  intento $i: $code — reintento en ${HEALTHCHECK_INTERVAL:-6}s"
  sleep "${HEALTHCHECK_INTERVAL:-6}"
done
[ "$ok" = "1" ] || rollback

"${COMPOSE[@]}" ps
docker image prune -f >/dev/null 2>&1 || true
echo "✓ Despliegue completado (IMAGE_TAG=${IMAGE_TAG})."

# Redeploy opcional vía webhook de Portainer
[ -n "${PORTAINER_WEBHOOK_URL:-}" ] && curl -fsS -X POST "$PORTAINER_WEBHOOK_URL" >/dev/null 2>&1 || true
