"""
Seed de catálogos para el módulo de campañas.

Crea (si no existen):
  - TipoCampania
  - EstadoCampania
"""
import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url
from app.modules.actividades.models.campana import TipoCampania
from app.modules.configuracion.models.estados import EstadoCampania


TIPOS = [
    ("Sensibilización",  "Campaña de concienciación y divulgación pública"),
    ("Recaudación",      "Campaña orientada a captación de fondos o donaciones"),
    ("Institucional",    "Relaciones con administraciones y organismos públicos"),
    ("Formación",        "Cursos, talleres o jornadas formativas"),
    ("Judicial",         "Seguimiento o apoyo a procedimientos judiciales"),
    ("Evento",           "Organización de un evento público o acto"),
]

ESTADOS = [
    ("Borrador",    1, "Campaña en elaboración, no publicada"),
    ("Programada",  2, "Campaña aprobada y pendiente de inicio"),
    ("En Curso",    3, "Campaña activa en ejecución"),
    ("Pausada",     4, "Campaña temporalmente suspendida"),
    ("Finalizada",  5, "Campaña concluida satisfactoriamente"),
    ("Cancelada",   6, "Campaña cancelada antes de finalizar"),
]


async def seed(session: AsyncSession):
    print("\n— Tipos de campaña —")
    for nombre, descripcion in TIPOS:
        res = await session.execute(select(TipoCampania).where(TipoCampania.nombre == nombre))
        if res.scalar_one_or_none():
            print(f"  [ya existe] {nombre}")
            continue
        session.add(TipoCampania(id=uuid.uuid4(), nombre=nombre, descripcion=descripcion, activo=True))
        print(f"  [+] {nombre}")

    print("\n— Estados de campaña —")
    for nombre, orden, descripcion in ESTADOS:
        res = await session.execute(
            text("SELECT id FROM estados_campania WHERE nombre = :n"), {"n": nombre}
        )
        if res.fetchone():
            print(f"  [ya existe] {nombre}")
            continue
        await session.execute(
            text("""
                INSERT INTO estados_campania (id, nombre, orden, activo, descripcion)
                VALUES (:id, :nombre, :orden, true, :descripcion)
            """),
            {"id": uuid.uuid4(), "nombre": nombre, "orden": orden, "descripcion": descripcion},
        )
        print(f"  [+] {nombre}")

    await session.commit()
    print("\n[OK] Seed de catálogos de campaña completado.")


async def main():
    url = get_database_url()
    engine = create_async_engine(url, echo=False, connect_args={"server_settings": {"jit": "off"}, "statement_cache_size": 0})
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
