"""Siembra grupos de trabajo de demo (idempotente por nombre).

Crea unos grupos orgánicos (Comisión/Permanente) y alguno temporal ligado a una
campaña, sobre los datos ya sembrados (tipos_grupo, campañas, contactos). Sirve para
ver el módulo de Grupos de Trabajo con contenido en dev.

Ejecutar:
  docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend \\
      python -m app.scripts.seeding.seed_grupos_demo
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.database import async_session
from app.modules.actividades.models.grupo import GrupoTrabajo, TipoGrupo
from app.modules.actividades.models.campana import Campania
from app.modules.membresia.models.contacto import Contacto


# Un grupo de campaña por cada una de estas campañas (match por substring del nombre).
# Son grupos EFÍMEROS ligados a su campaña (tipo "Temporal").
GRUPOS_CAMPANIA = [
    ("Grupo de campaña: Concordato", "Concordato",
     "Grupo de trabajo de la campaña de denuncia del Concordato con la Santa Sede."),
    ("Grupo de campaña: Escuela Laica", "escuela pública",
     "Grupo de trabajo de la campaña por una escuela pública, laica y gratuita."),
    ("Grupo de campaña: Inmatriculaciones", "inmatriculados",
     "Grupo de trabajo de la campaña de recuperación de bienes inmatriculados por la Iglesia."),
    ("Grupo de campaña: Exenciones fiscales", "exenciones fiscales",
     "Grupo de trabajo de la campaña contra las exenciones fiscales de la Iglesia."),
    ("Grupo de campaña: Crucifijos", "crucifijos",
     "Grupo de trabajo de la campaña de retirada de símbolos religiosos de espacios públicos."),
]


async def seed(session=None) -> None:
    own = session is None
    if own:
        session = async_session()
        await session.__aenter__()
    try:
        tipos = {t.nombre: t.id for t in (await session.execute(select(TipoGrupo))).scalars().all()}
        if not tipos:
            print("[grupos] No hay tipos_grupo sembrados; abortando.")
            return
        tipo_temporal = tipos.get("Temporal") or next(iter(tipos.values()))

        coordinador_id = (await session.execute(
            select(Contacto.id).where(Contacto.nombre.isnot(None)).limit(1)
        )).scalar_one_or_none()
        campanias = (await session.execute(select(Campania.id, Campania.nombre))).all()

        creados = 0
        for nombre_grupo, patron, objetivo in GRUPOS_CAMPANIA:
            existe = (await session.execute(
                select(GrupoTrabajo.id).where(GrupoTrabajo.nombre == nombre_grupo)
            )).scalar_one_or_none()
            if existe:
                continue
            # Localiza la campaña por substring (case-insensitive).
            campania_id = next(
                (cid for (cid, cnom) in campanias if patron.lower() in (cnom or "").lower()),
                None,
            )
            if campania_id is None:
                print(f"  · '{nombre_grupo}' omitido (no hay campaña que contenga '{patron}')")
                continue
            session.add(GrupoTrabajo(
                nombre=nombre_grupo,
                tipo_grupo_id=tipo_temporal,
                objetivo=objetivo,
                descripcion=objetivo,
                coordinador_id=coordinador_id,
                campania_id=campania_id,
                activo=True,
            ))
            creados += 1

        await session.commit()
        total = (await session.execute(select(GrupoTrabajo.id))).scalars().all()
        print(f"[grupos] +{creados} creados · {len(total)} en total.")
    finally:
        if own:
            await session.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(seed())
