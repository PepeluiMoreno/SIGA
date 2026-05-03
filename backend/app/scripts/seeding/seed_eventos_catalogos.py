"""
Script de seeding de catálogos del dominio de Eventos.

Crea los tipos de evento y estados del ciclo de vida.
Ejecutar tras aplicar la migración a2b3c4d5e6f7_add_eventos_domain.

Uso:
    cd /opt/docker/apps/SIGA/backend
    python -m app.scripts.seeding.seed_eventos_catalogos
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import get_database_url
from app.modules.eventos.models import TipoEvento, EstadoEvento


TIPOS_EVENTO = [
    {
        "nombre": "Asamblea General",
        "descripcion": "Asamblea general ordinaria o extraordinaria de la organización",
        "requiere_inscripcion": False,
        "requiere_aforo": False,
    },
    {
        "nombre": "Conferencia",
        "descripcion": "Conferencia o charla pública sobre laicismo u otros temas",
        "requiere_inscripcion": True,
        "requiere_aforo": True,
    },
    {
        "nombre": "Jornada",
        "descripcion": "Jornada de debate, reflexión o formación de duración extendida",
        "requiere_inscripcion": True,
        "requiere_aforo": True,
    },
    {
        "nombre": "Taller",
        "descripcion": "Taller de formación o trabajo en grupo reducido",
        "requiere_inscripcion": True,
        "requiere_aforo": True,
    },
    {
        "nombre": "Concentración",
        "descripcion": "Concentración o manifestación pública",
        "requiere_inscripcion": False,
        "requiere_aforo": False,
    },
    {
        "nombre": "Acto público",
        "descripcion": "Acto público de la organización (presentación, homenaje, celebración)",
        "requiere_inscripcion": False,
        "requiere_aforo": True,
    },
    {
        "nombre": "Rueda de prensa",
        "descripcion": "Rueda de prensa o comparecencia ante medios",
        "requiere_inscripcion": False,
        "requiere_aforo": False,
    },
    {
        "nombre": "Reunión de trabajo",
        "descripcion": "Reunión interna de coordinación o trabajo de grupos",
        "requiere_inscripcion": False,
        "requiere_aforo": False,
    },
    {
        "nombre": "Formación interna",
        "descripcion": "Sesión de formación para miembros y voluntarios de la organización",
        "requiere_inscripcion": True,
        "requiere_aforo": True,
    },
]

ESTADOS_EVENTO = [
    {"nombre": "Planificado",   "orden": 1, "color": "#3B82F6", "es_final": False},
    {"nombre": "En preparación","orden": 2, "color": "#8B5CF6", "es_final": False},
    {"nombre": "Confirmado",    "orden": 3, "color": "#10B981", "es_final": False},
    {"nombre": "Celebrado",     "orden": 4, "color": "#6B7280", "es_final": True},
    {"nombre": "Cancelado",     "orden": 5, "color": "#EF4444", "es_final": True},
    {"nombre": "Aplazado",      "orden": 6, "color": "#F59E0B", "es_final": False},
]


async def seed_tipos_evento(session: AsyncSession) -> None:
    for datos in TIPOS_EVENTO:
        existing = await session.execute(
            select(TipoEvento).where(TipoEvento.nombre == datos["nombre"])
        )
        if existing.scalar_one_or_none() is None:
            session.add(TipoEvento(id=uuid.uuid4(), **datos))
            print(f"  + TipoEvento: {datos['nombre']}")
        else:
            print(f"  · TipoEvento ya existe: {datos['nombre']}")


async def seed_estados_evento(session: AsyncSession) -> None:
    for datos in ESTADOS_EVENTO:
        existing = await session.execute(
            select(EstadoEvento).where(EstadoEvento.nombre == datos["nombre"])
        )
        if existing.scalar_one_or_none() is None:
            session.add(EstadoEvento(id=uuid.uuid4(), **datos))
            print(f"  + EstadoEvento: {datos['nombre']}")
        else:
            print(f"  · EstadoEvento ya existe: {datos['nombre']}")


async def main() -> None:
    engine = create_async_engine(get_database_url(), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            print("Seeding tipos de evento...")
            await seed_tipos_evento(session)
            print("Seeding estados de evento...")
            await seed_estados_evento(session)

    await engine.dispose()
    print("✓ Seeding de catálogos de eventos completado.")


if __name__ == "__main__":
    asyncio.run(main())
