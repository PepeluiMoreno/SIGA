#!/usr/bin/env bash
# Backup de la base de datos ANTES del deploy/migración.
#
# La migración Miembro→Contacto (p1→p4) transforma datos de forma irreversible:
# haz SIEMPRE este backup antes de mergear/desplegar. Correr en el servidor, en el
# directorio del proyecto (p. ej. /opt/docker/apps/SIGA):
#
#     ENV_FILE=.env.staging deploy/backup_db.sh
#
# Restaurar:
#     gunzip -c backup_pre_deploy_XXXX.sql.gz | \
#       docker compose --env-file .env.staging -f docker-compose.yml -f docker-compose.staging.yml \
#         exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
set -euo pipefail

cd "$(dirname "$0")/.."
ENV_FILE="${ENV_FILE:-.env.staging}"
[ -f "$ENV_FILE" ] || { echo "[backup] No existe $ENV_FILE"; exit 1; }

# Cargar POSTGRES_USER / POSTGRES_DB del entorno de compose
set -a; # shellcheck disable=SC1090
source "$ENV_FILE"; set +a

COMPOSE="docker compose --env-file $ENV_FILE -f docker-compose.yml -f docker-compose.staging.yml"
TS="$(date +%Y%m%d_%H%M%S)"
OUT="backup_pre_deploy_${TS}.sql.gz"

echo "[backup] pg_dump de '$POSTGRES_DB' (usuario $POSTGRES_USER) -> $OUT"
$COMPOSE exec -T db pg_dump -U "$POSTGRES_USER" --clean --if-exists "$POSTGRES_DB" | gzip > "$OUT"

SIZE="$(du -h "$OUT" | cut -f1)"
echo "[backup] OK: $OUT ($SIZE) en $(pwd)"
echo "[backup] Guarda este fichero FUERA del servidor antes de migrar."
