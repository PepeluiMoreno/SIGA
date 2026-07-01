"""Catálogo de TIPOS DE META de campaña (objetivos medibles). Idempotente por nombre.

Sin este catálogo, el selector "Tipo de meta" de las plantillas/campañas sale vacío.

Ejecutar:
  docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend \\
      python -m app.scripts.seeding.seed_tipos_meta_campania
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.database import async_session
from app.modules.actividades.models.campana import TipoMeta


# (nombre, unidad_medida, descripción)
TIPOS_META = [
    ("Participantes", "personas", "Personas que participan o son contactadas."),
    ("Firmas",        "firmas",   "Firmas recogidas en una campaña de recogida."),
    ("Visitas",       "visitas",  "Puntos, actos o visitas realizadas."),
    ("Menciones",     "menciones","Apariciones o menciones en medios / redes."),
    ("Recaudación",   "€",        "Importe recaudado o captado."),
]


async def seed(session=None) -> None:
    own = session is None
    if own:
        session = async_session()
        await session.__aenter__()
    try:
        existentes = {t.nombre for t in (await session.execute(select(TipoMeta))).scalars().all()}
        creados = 0
        for nombre, unidad, desc in TIPOS_META:
            if nombre in existentes:
                continue
            session.add(TipoMeta(
                nombre=nombre, unidad_medida=unidad, descripcion=desc, activo=True,
            ))
            creados += 1
        await session.commit()
        print(f"[tipos_meta_campania] +{creados} creados.")
    finally:
        if own:
            await session.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(seed())
