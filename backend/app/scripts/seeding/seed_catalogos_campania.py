"""
Seed de catálogos para el módulo de campañas.

Crea/actualiza:
  - TipoCampania  (7 tipos con tipología real de Europa Laica)
  - EstadoCampania (UUIDs fijos — idempotente vía ON CONFLICT)
"""
import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url
from app.modules.actividades.models.campana import TipoCampania


TIPOS = [
    ("Recogida de firmas",         "Petición dirigida a institución o administración pública"),
    ("Sensibilización",            "Concienciación y divulgación pública sobre laicidad"),
    ("Captación de socios",        "Captación de nuevos socios o donaciones económicas"),
    ("Campaña formativa",          "Cursos, talleres, jornadas y actividades educativas"),
    ("Movilización",               "Manifestaciones, concentraciones y actos públicos"),
    ("Acción legal/institucional", "Recursos, denuncias, lobbying y relaciones institucionales"),
    ("Comunicación mediática",     "Notas de prensa, presencia en medios y redes sociales"),
]

# UUIDs fijos: garantizan que el mismo estado tenga el mismo ID en cualquier entorno.
# Nunca cambiar estos UUIDs. Si se necesita un estado nuevo, añadir una fila con un UUID nuevo.
# (id, nombre, orden, es_inicial, es_final, descripcion)
ESTADOS = [
    ("f181fc67-a7e1-44db-8b57-344f37bfe1c4", "Borrador",   1, True,  False, "Campaña en elaboración, no publicada"),
    ("2a55d055-7055-4657-9f1d-30ba76277bd6", "Programada", 2, False, False, "Campaña aprobada y pendiente de inicio"),
    ("c7d882d2-1aa0-4e74-b212-95ea731c19a0", "En curso",   3, False, False, "Campaña activa en ejecución"),
    ("05b3edc1-1230-48ee-b7e5-fb7c5f632eff", "Pausada",    4, False, False, "Campaña temporalmente suspendida"),
    ("7db81ba1-b5ed-4834-8b11-dd1d6c46d71f", "Finalizada", 5, False, True,  "Campaña concluida satisfactoriamente"),
    ("156dbbf9-46de-4550-ab2a-a7fef2a546ff", "Cancelada",  6, False, True,  "Campaña cancelada antes de finalizar"),
]


async def seed(session: AsyncSession):
    # ── Tipos ─────────────────────────────────────────────────────────────────
    print("\n— Tipos de campaña —")

    nombres_nuevos = {nombre for nombre, _ in TIPOS}
    res = await session.execute(select(TipoCampania))
    for tipo in res.scalars().all():
        if tipo.nombre not in nombres_nuevos:
            campanas = await session.execute(
                text("SELECT 1 FROM campanias WHERE tipo_campania_id = :id LIMIT 1"),
                {"id": tipo.id},
            )
            if campanas.fetchone() is None:
                await session.delete(tipo)
                print(f"  [elimina obsoleto] {tipo.nombre}")

    for nombre, descripcion in TIPOS:
        res = await session.execute(select(TipoCampania).where(TipoCampania.nombre == nombre))
        existing = res.scalar_one_or_none()
        if existing:
            existing.descripcion = descripcion
            existing.activo = True
            print(f"  [ok] {nombre}")
        else:
            session.add(TipoCampania(id=uuid.uuid4(), nombre=nombre, descripcion=descripcion, activo=True))
            print(f"  [+] {nombre}")

    # ── Estados ───────────────────────────────────────────────────────────────
    print("\n— Estados de campaña —")
    for id_fijo, nombre, orden, es_inicial, es_final, descripcion in ESTADOS:
        await session.execute(
            text("""
                INSERT INTO estados_campania
                  (id, nombre, orden, es_inicial, es_final, activo, descripcion)
                VALUES
                  (:id, :nombre, :orden, :es_inicial, :es_final, true, :descripcion)
                ON CONFLICT (id) DO UPDATE SET
                  nombre      = EXCLUDED.nombre,
                  orden       = EXCLUDED.orden,
                  es_inicial  = EXCLUDED.es_inicial,
                  es_final    = EXCLUDED.es_final,
                  descripcion = EXCLUDED.descripcion,
                  activo      = true
            """),
            {"id": id_fijo, "nombre": nombre, "orden": orden,
             "es_inicial": es_inicial, "es_final": es_final, "descripcion": descripcion},
        )
        print(f"  [upsert] {id_fijo[:8]}… {nombre}")

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
