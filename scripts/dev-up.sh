#!/usr/bin/env bash
# Despliegue de SIGA en DESARROLLO (optiplex-790).
# Estándar de Ingeniería §2: build local en sitio, disparo manual, sin GHCR.
# Combina el compose BASE (build local) con el override de desarrollo
# (hot-reload: Vite + uvicorn --reload; Traefik en el optiplex).
#
#   ./scripts/dev-up.sh            arranque LIGERO: reusa imágenes, NO reconstruye.
#                                  Es lo normal del día a día (hay hot-reload).
#   ./scripts/dev-up.sh rebuild    reconstruye la imagen del BACKEND y arranca.
#                                  Úsalo solo si cambian requirements.txt o el Dockerfile.
#   ./scripts/dev-up.sh resetdb    reinicia la BD (borra el volumen pgdata_dev) y arranca;
#                                  conserva node_modules y uploads.
#   ./scripts/dev-up.sh down       detiene (conserva volúmenes de datos).
#   ./scripts/dev-up.sh logs       sigue los logs.
#
# El frontend en dev corre sobre node:22-alpine con Vite (hot-reload); su imagen
# NO se construye aquí (build neutralizado en el override), por eso 'rebuild'
# solo reconstruye el backend.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "ERROR: falta .env. Copia .env.example a .env y rellena los marcadores." >&2
  exit 1
fi

COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.dev.yml)

arrancar() {              # $@ = flags extra para 'up' (p. ej. --build)
  "${COMPOSE[@]}" up -d "$@"
  echo
  "${COMPOSE[@]}" ps
  echo
  echo "SIGA dev en marcha → https://${APP_DEV_DOMAIN:-siga.optiplex-790}"
}

case "${1:-up}" in
  up)
    arrancar
    ;;
  rebuild)
    # Solo el backend tiene 'build'; el frontend (node:22-alpine) se omite.
    arrancar --build
    ;;
  resetdb)
    echo "Reiniciando la BD: se borra el volumen pgdata_dev (no hay datos que conservar en dev)…"
    "${COMPOSE[@]}" rm -fsv db
    arrancar
    ;;
  down)
    "${COMPOSE[@]}" down
    ;;
  logs)
    "${COMPOSE[@]}" logs -f --tail=100
    ;;
  *)
    echo "Uso: $0 [up|rebuild|resetdb|down|logs]" >&2
    exit 2
    ;;
esac
