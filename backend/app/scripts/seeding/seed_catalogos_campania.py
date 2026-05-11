"""
Seed de catálogos para el módulo de campañas.

Crea/actualiza:
  - TipoCampania  (7 tipos con tipología real de Europa Laica)
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
    ("Recogida de firmas",         "Petición dirigida a institución o administración pública"),
    ("Sensibilización",            "Concienciación y divulgación pública sobre laicidad"),
    ("Captación de socios",        "Captación de nuevos socios o donaciones económicas"),
    ("Campaña formativa",          "Cursos, talleres, jornadas y actividades educativas"),
    ("Movilización",               "Manifestaciones, concentraciones y actos públicos"),
    ("Acción legal/institucional", "Recursos, denuncias, lobbying y relaciones institucionales"),
    ("Comunicación mediática",     "Notas de prensa, presencia en medios y redes sociales"),
]

# (nombre, orden, es_inicial, es_final, descripcion)
ESTADOS = [
    ("Borrador",   1, True,  False, "Campaña en elaboración, no publicada"),
    ("Programada", 2, False, False, "Campaña aprobada y pendiente de inicio"),
    ("En Curso",   3, False, False, "Campaña activa en ejecución"),
    ("Pausada",    4, False, False, "Campaña temporalmente suspendida"),
    ("Finalizada", 5, False, True,  "Campaña concluida satisfactoriamente"),
    ("Cancelada",  6, False, True,  "Campaña cancelada antes de finalizar"),
]


async def seed(session: AsyncSession):
    # ── Tipos ─────────────────────────────────────────────────────────────────
    print("\n— Tipos de campaña —")

    # Eliminar tipos obsoletos que no tengan campañas asociadas
    nombres_nuevos = {nombre for nombre, _ in TIPOS}
    res = await session.execute(select(TipoCampania))
    tipos_existentes = res.scalars().all()
    for tipo in tipos_existentes:
        if tipo.nombre not in nombres_nuevos:
            campanas = await session.execute(
                text("SELECT 1 FROM campanias WHERE tipo_campania_id = :id LIMIT 1"),
                {"id": tipo.id},
            )
            if campanas.fetchone() is None:
                await session.delete(tipo)
                print(f"  [elimina obsoleto] {tipo.nombre}")

    # Insertar o actualizar
    for nombre, descripcion in TIPOS:
        res = await session.execute(select(TipoCampania).where(TipoCampania.nombre == nombre))
        existing = res.scalar_one_or_none()
        if existing:
            existing.descripcion = descripcion
            existing.activo = True
            print(f"  [actualiza] {nombre}")
        else:
            session.add(TipoCampania(id=uuid.uuid4(), nombre=nombre, descripcion=descripcion, activo=True))
            print(f"  [+] {nombre}")

    # ── Estados ───────────────────────────────────────────────────────────────
    print("\n— Estados de campaña —")
    for nombre, orden, es_inicial, es_final, descripcion in ESTADOS:
        res = await session.execute(
            text("SELECT id FROM estados_campania WHERE nombre = :n"), {"n": nombre}
        )
        if res.fetchone():
            print(f"  [ya existe] {nombre}")
            continue
        await session.execute(
            text("""
                INSERT INTO estados_campania
                  (id, nombre, orden, es_inicial, es_final, activo, descripcion)
                VALUES
                  (:id, :nombre, :orden, :es_inicial, :es_final, true, :descripcion)
            """),
            {
                "id": str(uuid.uuid4()), "nombre": nombre, "orden": orden,
                "es_inicial": es_inicial, "es_final": es_final, "descripcion": descripcion,
            },
        )
        print(f"  [+] {nombre}")

    await session.commit()
    print("\n[OK] Seed de catálogos de campaña completado.")


async def main():
    url = get_database_url()
    engine = create_async_engine(
        url, echo=False,
        connect_args={"server_settings": {"jit": "off"}, "statement_cache_size": 0},
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
