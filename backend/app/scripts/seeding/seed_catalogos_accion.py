"""Seed catálogos del módulo Acción: TipoAccion y EstadoAccion."""
import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_database_url
from app.modules.actividades.models.accion import TipoAccion
from app.modules.configuracion.models.estados import EstadoAccion, EstadoTarea


TIPOS_ACCION = [
    {
        "id": uuid.UUID("11111111-0001-0000-0000-000000000001"),
        "nombre": "Evento público",
        "descripcion": "Concentración, mitin, marcha o acto público",
        "tiene_lugar": True,
        "tiene_participantes": True,
    },
    {
        "id": uuid.UUID("11111111-ac01-0000-0000-000000000002"),
        "nombre": "Reunión",
        "descripcion": "Reunión interna del grupo o de coordinación",
        "tiene_lugar": True,
        "tiene_participantes": True,
    },
    {
        "id": uuid.UUID("11111111-ac01-0000-0000-000000000003"),
        "nombre": "Taller / Formación",
        "descripcion": "Actividad formativa o de capacitación",
        "tiene_lugar": True,
        "tiene_participantes": True,
    },
    {
        "id": uuid.UUID("11111111-ac01-0000-0000-000000000004"),
        "nombre": "Acción de comunicación",
        "descripcion": "Nota de prensa, publicación, campaña en redes sociales",
        "tiene_lugar": False,
        "tiene_participantes": False,
    },
    {
        "id": uuid.UUID("11111111-ac01-0000-0000-000000000005"),
        "nombre": "Acción legal",
        "descripcion": "Denuncia, recurso, acción judicial o administrativa",
        "tiene_lugar": False,
        "tiene_participantes": False,
    },
    {
        "id": uuid.UUID("11111111-ac01-0000-0000-000000000006"),
        "nombre": "Trabajo voluntario",
        "descripcion": "Jornada de voluntariado, recogida de firmas presencial",
        "tiene_lugar": True,
        "tiene_participantes": True,
    },
    {
        "id": uuid.UUID("11111111-ac01-0000-0000-000000000007"),
        "nombre": "Recaudación",
        "descripcion": "Campaña de fundraising, colecta, subvención",
        "tiene_lugar": False,
        "tiene_participantes": False,
    },
]

ESTADOS_ACCION = [
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000001"), "nombre": "Propuesta","orden": 1},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000002"), "nombre": "Aprobada", "orden": 2},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000003"), "nombre": "En preparación", "orden": 3},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000004"), "nombre": "En curso", "orden": 4},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000005"), "nombre": "Finalizada", "orden": 5},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000006"), "nombre": "Cancelada", "orden": 6},
]

ESTADOS_TAREA = [
    {"id": uuid.UUID("33333333-0001-0000-0000-000000000001"), "nombre": "Pendiente", "orden": 1},
    {"id": uuid.UUID("33333333-0001-0000-0000-000000000002"), "nombre": "En curso", "orden": 2},
    {"id": uuid.UUID("33333333-0001-0000-0000-000000000003"), "nombre": "Completada", "orden": 3},
    {"id": uuid.UUID("33333333-0001-0000-0000-000000000004"), "nombre": "Cancelada", "orden": 4},
]


async def seed(session: AsyncSession) -> None:
    for data in TIPOS_ACCION:
        exists = await session.get(TipoAccion, data["id"])
        if not exists:
            session.add(TipoAccion(**data))
            print(f"  + TipoAccion: {data['nombre']}")

    for data in ESTADOS_ACCION:
        exists = await session.get(EstadoAccion, data["id"])
        if not exists:
            session.add(EstadoAccion(**data))
            print(f"  + EstadoAccion: {data['nombre']}")

    for data in ESTADOS_TAREA:
        exists = await session.get(EstadoTarea, data["id"])
        if not exists:
            session.add(EstadoTarea(**data))
            print(f"  + EstadoTarea: {data['nombre']}")

    await session.commit()


async def main() -> None:
    print("Seeding catálogos de Acción...")
    url = get_database_url()
    engine = create_async_engine(
        url, echo=False,
        connect_args={"server_settings": {"jit": "off"}, "statement_cache_size": 0},
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await seed(session)
    await engine.dispose()
    print("Listo.")


if __name__ == "__main__":
    asyncio.run(main())
