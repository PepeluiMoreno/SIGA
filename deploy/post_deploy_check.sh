#!/usr/bin/env bash
# Verificación POST-deploy: estado de migraciones, conteos y smoke GraphQL.
# Correr en el servidor tras el deploy (cuando el backend ya está arriba):
#
#     ENV_FILE=.env.staging SMOKE_EMAIL=admin@... SMOKE_PASSWORD=... deploy/post_deploy_check.sh
#
# (Si no pasas SMOKE_EMAIL/PASSWORD usa INITIAL_ADMIN_* del .env.) Sale !=0 si algo falla.
set -euo pipefail

cd "$(dirname "$0")/.."
ENV_FILE="${ENV_FILE:-.env.staging}"
[ -f "$ENV_FILE" ] || { echo "[check] No existe $ENV_FILE"; exit 1; }
COMPOSE="docker compose --env-file $ENV_FILE -f docker-compose.yml -f docker-compose.staging.yml"

echo "== 1. Servicios =="
$COMPOSE ps

echo; echo "== 2. Migraciones (debe estar en head) =="
$COMPOSE exec -T backend alembic current

echo; echo "== 3. Conteos del modelo nuevo =="
$COMPOSE exec -T backend python -c "
import asyncio
from sqlalchemy import text
from app.core.database import async_session
async def main():
    async with async_session() as s:
        for t in ['contactos','vinculaciones','socios','voluntarios','participaciones',
                  'membresias','cuotas_anuales','recibos','usuarios']:
            try:
                n = await s.scalar(text(f'select count(*) from {t}'))
            except Exception as e:
                n = f'ERROR ({e.__class__.__name__})'
            print(f'  {t:18} {n}')
        # tabla legacy debe existir como histórico
        try:
            n = await s.scalar(text('select count(*) from miembros_legacy'))
            print(f'  miembros_legacy    {n} (histórico)')
        except Exception:
            print('  miembros_legacy    (no presente)')
asyncio.run(main())
"

echo; echo "== 4. Smoke GraphQL (login + miPerfil + socios + cuotas) =="
$COMPOSE exec -T \
  -e SMOKE_EMAIL="${SMOKE_EMAIL:-}" -e SMOKE_PASSWORD="${SMOKE_PASSWORD:-}" \
  backend python -m app.scripts.smoke_test

echo; echo "[check] OK — verificación post-deploy completada."
