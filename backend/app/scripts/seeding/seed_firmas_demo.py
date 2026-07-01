"""Firmas de demo para las campañas de recogida de firmas (idempotente).

Para cada campaña de tipo "Recogida de firmas" crea (si no existen):
  - una ACTIVIDAD de recogida ligada a la campaña,
  - una META de firmas (tipo de meta "Firmas") con valor planificado,
  - varias FIRMAS demo: Participacion(FIRMA) + FirmaCampania, mezcla de verificadas
    y no verificadas, sobre los contactos existentes.

Así la métrica de firmas (firmasVerificadasCampania) tiene datos que mostrar.

Ejecutar:
  docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend \\
      python -m app.scripts.seeding.seed_firmas_demo
"""
from __future__ import annotations

import asyncio
from decimal import Decimal

from sqlalchemy import select, text, func

from app.core.database import async_session
from app.modules.actividades.models.campana import Campania, FirmaCampania, MetaCampania, TipoMeta
from app.modules.actividades.models.actividad import Actividad
from app.modules.membresia.models.contacto import Contacto
from app.modules.membresia.models.participacion import Participacion


# meta planificada de firmas por campaña (orientativa para la demo)
META_FIRMAS = Decimal("100000")


async def seed(session=None) -> None:
    own = session is None
    if own:
        session = async_session()
        await session.__aenter__()
    try:
        # Campañas de recogida de firmas.
        campanias = (await session.execute(text("""
            SELECT c.id, c.nombre FROM campanias c
            JOIN tipos_campania tc ON tc.id = c.tipo_campania_id
            WHERE tc.nombre = 'Recogida de firmas' AND c.eliminado = false
        """))).all()
        if not campanias:
            print("[firmas] No hay campañas de 'Recogida de firmas'; nada que sembrar.")
            return

        tipo_meta_firmas = (await session.execute(
            select(TipoMeta.id).where(TipoMeta.nombre == "Firmas")
        )).scalar_one_or_none()
        tipo_act = (await session.execute(text("SELECT id FROM tipos_accion LIMIT 1"))).scalar()
        estado_act = (await session.execute(
            text("SELECT id FROM estados_accion ORDER BY orden LIMIT 1")
        )).scalar()

        # Contactos disponibles para firmar (personas físicas).
        contactos = (await session.execute(
            select(Contacto.id).where(Contacto.tipo == "PERSONA_FISICA").limit(12)
        )).scalars().all()
        if not contactos:
            print("[firmas] No hay contactos para firmar.")
            return

        n_act = n_meta = n_firmas = 0
        for i, (cid, nombre) in enumerate(campanias):
            # 1) Actividad de recogida (si no hay ninguna ligada a la campaña).
            act_id = (await session.execute(
                select(Actividad.id).where(Actividad.campania_id == cid).limit(1)
            )).scalar_one_or_none()
            if act_id is None:
                act = Actividad(
                    nombre=f"Recogida de firmas — {nombre}",
                    tipo_actividad_id=tipo_act, estado_id=estado_act,
                    campania_id=cid, es_recurrente=False, es_online=True,
                    presupuesto_estimado=Decimal("0"), presupuesto_ejecutado=Decimal("0"),
                )
                session.add(act)
                await session.flush()
                act_id = act.id
                n_act += 1

            # 2) Meta de firmas (si el tipo de meta existe y no está ya puesta).
            if tipo_meta_firmas is not None:
                ya = (await session.execute(
                    select(MetaCampania.id).where(
                        MetaCampania.campania_id == cid,
                        MetaCampania.tipo_meta_id == tipo_meta_firmas,
                    )
                )).scalar_one_or_none()
                if ya is None:
                    session.add(MetaCampania(
                        campania_id=cid, tipo_meta_id=tipo_meta_firmas,
                        valor_planificado=META_FIRMAS, notas="Meta de firmas de la campaña.",
                    ))
                    n_meta += 1

            # 3) Firmas demo (si la campaña aún no tiene). Nº y verificadas variables.
            tiene = (await session.execute(
                select(func.count(FirmaCampania.id)).where(FirmaCampania.campania_id == cid)
            )).scalar() or 0
            if tiene == 0:
                cuantas = 4 + (i % 4)  # 4..7 firmas por campaña
                for j in range(cuantas):
                    contacto_id = contactos[(i + j) % len(contactos)]
                    part = Participacion(contacto_id=contacto_id, tipo="FIRMA", estado="registrada")
                    session.add(part)
                    await session.flush()
                    session.add(FirmaCampania(
                        participacion_id=part.id, actividad_id=act_id, campania_id=cid,
                        contacto_id=contacto_id, acepta_terminos=True,
                        verificado=(j % 2 == 0),  # la mitad verificadas
                    ))
                    n_firmas += 1

        await session.commit()
        print(f"[firmas] +{n_act} actividades · +{n_meta} metas · +{n_firmas} firmas.")
    finally:
        if own:
            await session.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(seed())
