#!/usr/bin/env bash
# Despliegue de SIGA en DESARROLLO (optiplex-790).
# Estándar de Ingeniería §2: el desarrollo construye la imagen en sitio
# (build local), disparo manual. No usa GHCR.
#
# Combina el compose BASE (build local) con el override de desarrollo
# (hot-reload + Traefik en el optiplex).
#
#   ./scripts/dev-up.sh           levanta/reconstruye y deja en marcha
#   ./scripts/dev-up.sh down      detiene (conserva volúmenes de datos)
#   ./scripts/dev-up.sh logs      sigue los logs
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "ERROR: falta .env. Copia .env.example a .env y rellena los marcadores." >&2
  exit 1
fi

COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.dev.yml)

case "${1:-up}" in
  up)
    "${COMPOSE[@]}" up -d --build
    echo
    "${COMPOSE[@]}" ps
    echo
    echo "SIGA dev en marcha → https://${APP_DEV_DOMAIN:-siga.optiplex-790}"
    ;;
  down)
    "${COMPOSE[@]}" down
    ;;
  logs)
    "${COMPOSE[@]}" logs -f --tail=100
    ;;
  *)
    echo "Uso: $0 [up|down|logs]" >&2
    exit 2
    ;;
esac
