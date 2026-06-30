"""Guard de entorno para los seeds de DATOS DE PRUEBA.

Defensa en profundidad contra sembrar datos ficticios en producción:

  - Capa física: producción no bind-montea estos scripts (ver docker-compose).
  - Capa lógica: este guard. Aunque el módulo esté presente en la imagen y
    alguien lo ejecute por error en producción, aborta.

Política fail-closed: el entorno se lee de `Settings.siga_env`, cuyo default y
fail-safe es "production" (ver app/core/config.py). Si SIGA_ENV no está definido
o trae un valor raro, se considera producción y se bloquea.

Uso: importar y llamar al INICIO de cualquier seed que cree datos ficticios:

    from app.scripts.seeding._guard import abort_if_production
    abort_if_production("poblado demo de staging")
"""
from __future__ import annotations

import sys

from app.core.config import get_settings


def abort_if_production(operacion: str = "seeding de datos de prueba") -> None:
    """Aborta el proceso (exit 2) si SIGA_ENV indica producción.

    Pensado para scripts ejecutables (`python -m ...`), no para código de la app.
    """
    settings = get_settings()
    if settings.is_production:
        print(
            f"ABORTADO: '{operacion}' está prohibido con SIGA_ENV=production. "
            "Los datos de prueba no se siembran en producción.",
            file=sys.stderr,
        )
        sys.exit(2)
