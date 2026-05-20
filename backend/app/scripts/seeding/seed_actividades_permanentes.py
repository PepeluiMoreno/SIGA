"""Seed de actividades permanentes / internas (sin campaña).

Las actividades permanentes son las que la entidad realiza de forma continua,
no vinculadas a una campaña concreta: estructura, administración, coordinación
interna, mantenimiento del software, etc.

Sirven como destino de imputación de gastos directos (alquiler, suministros,
salarios, software, asesoría…) en el modal "Registro de gasto" de Tesorería.

Idempotente: si una actividad permanente con el mismo nombre ya existe, no se
duplica.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_actividades_permanentes
"""
import asyncio
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.modules.actividades.models.actividad import Actividad


# Estado por defecto (En curso = activa, listo para imputar gastos).
ESTADO_EN_CURSO_ID = uuid.UUID("22222222-ac01-0000-0000-000000000004")
# Tipo de acción por defecto: Reunión (es la categoría más cercana a "interna").
TIPO_REUNION_ID = uuid.UUID("11111111-ac01-0000-0000-000000000002")
# Tipo de acción para administración / estructura.
TIPO_TRABAJO_VOLUNTARIO_ID = uuid.UUID("11111111-ac01-0000-0000-000000000006")


PERMANENTES = [
    ("Estructura y administración",
     "Gastos generales de funcionamiento: oficina, asesoría, gestoría, software, suministros.",
     TIPO_TRABAJO_VOLUNTARIO_ID),
    ("Coordinación interna",
     "Reuniones de coordinación entre órganos y agrupaciones, viajes internos.",
     TIPO_REUNION_ID),
    ("Comunicación interna y boletines",
     "Mantenimiento de canales de comunicación con la membresía, boletines, encuestas.",
     TIPO_REUNION_ID),
    ("Junta directiva",
     "Reuniones ordinarias y extraordinarias de la junta, viajes y dietas asociadas.",
     TIPO_REUNION_ID),
    ("Asamblea general",
     "Asamblea anual ordinaria y, si procede, extraordinarias.",
     TIPO_REUNION_ID),
    ("Formación interna",
     "Formación de socios, voluntarios y miembros de órganos.",
     TIPO_REUNION_ID),
    ("Atención a socios y voluntariado",
     "Soporte, altas, bajas, gestión de incidencias del programa de voluntariado.",
     TIPO_TRABAJO_VOLUNTARIO_ID),
    ("Cumplimientos legales y fiscales",
     "Modelos AEAT, libros oficiales, cuentas anuales, depósito, RGPD.",
     TIPO_TRABAJO_VOLUNTARIO_ID),
]


async def seed():
    async with async_session() as session:
        creadas = 0
        omitidas = 0
        for nombre, descripcion, tipo_id in PERMANENTES:
            r = await session.execute(
                select(Actividad).where(
                    Actividad.nombre == nombre,
                    Actividad.campania_id.is_(None),
                    Actividad.eliminado.is_(False),
                )
            )
            if r.scalars().first():
                omitidas += 1
                continue
            session.add(Actividad(
                id=uuid.uuid4(),
                nombre=nombre,
                descripcion=descripcion,
                tipo_actividad_id=tipo_id,
                estado_id=ESTADO_EN_CURSO_ID,
                campania_id=None,
                es_recurrente=False,
                padre_id=None,
                caracter="PERMANENTE",
                presupuesto_estimado=Decimal("0.00"),
                presupuesto_ejecutado=Decimal("0.00"),
            ))
            creadas += 1
        await session.commit()
        print(f"✓ Actividades permanentes: +{creadas} creadas, {omitidas} ya existían.")


if __name__ == "__main__":
    asyncio.run(seed())
