"""Seeding de agrupaciones territoriales de Europa Laica."""

import asyncio
from sqlalchemy import select

from app.core.database import async_session
from app.domains.geografico.models.direccion import AgrupacionTerritorial, Pais


# Europa Laica primero (NACIONAL, nivel 4), luego autonómicas (nivel 3) hijas de ella.
# nombre_corto se usa como clave idempotente y para búsqueda desde miembros.py.
AGRUPACIONES = [
    {
        "nombre": "Europa Laica",
        "nombre_corto": "EL",
        "tipo": "NACIONAL",
        "nivel": 4,
        "email": "info@laicismo.org",
        "web": "https://laicismo.org",
        "padre": None,
    },
    {"nombre": "Andalucía Laica",        "nombre_corto": "AND", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
    {"nombre": "Aragón Laico",           "nombre_corto": "ARA", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
    {"nombre": "Asturias Laica",         "nombre_corto": "AST", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
    {"nombre": "Canarias Laica",         "nombre_corto": "CAN", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
    {"nombre": "Catalunya Laica",        "nombre_corto": "CAT", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
    {"nombre": "Euskadi Laica",          "nombre_corto": "EUS", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
    {"nombre": "Extremadura Laica",      "nombre_corto": "EXT", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
    {"nombre": "Galicia Laica",          "nombre_corto": "GAL", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
    {"nombre": "Madrid Laica",           "nombre_corto": "MAD", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
    {"nombre": "Murcia Laica",           "nombre_corto": "MUR", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
    {"nombre": "País Valenciano Laico",  "nombre_corto": "VAL", "tipo": "AUTONOMICO", "nivel": 3, "padre": "EL"},
]


async def seed_agrupaciones():
    async with async_session() as db:
        # Obtener España (requerida como pais_id, NOT NULL en el modelo)
        pais_result = await db.execute(select(Pais).where(Pais.codigo == "ES"))
        espana = pais_result.scalar_one_or_none()
        if not espana:
            print("  ! ERROR: País España (codigo='ES') no encontrado. Ejecuta inicializar_geografico.py primero.")
            return

        # Índice nombre_corto → agrupacion para resolver jerarquía padre-hijo
        creadas: dict[str, AgrupacionTerritorial] = {}

        for data in AGRUPACIONES:
            padre_corto = data.pop("padre")

            result = await db.execute(
                select(AgrupacionTerritorial).where(
                    AgrupacionTerritorial.nombre_corto == data["nombre_corto"]
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"  = Agrupación ya existe: {data['nombre']}")
                creadas[data["nombre_corto"]] = existing
                continue

            agrupacion_padre_id = creadas[padre_corto].id if padre_corto else None

            agrupacion = AgrupacionTerritorial(
                **data,
                pais_id=espana.id,
                agrupacion_padre_id=agrupacion_padre_id,
                activo=True,
            )
            db.add(agrupacion)
            await db.flush()  # Para que .id esté disponible como padre antes del siguiente
            creadas[data["nombre_corto"]] = agrupacion
            print(f"  + Agrupación: {data['nombre']}")

        await db.commit()
        print("Agrupaciones territoriales completadas.")


if __name__ == "__main__":
    asyncio.run(seed_agrupaciones())
