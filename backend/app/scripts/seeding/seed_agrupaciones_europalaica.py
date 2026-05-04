"""Seed agrupaciones territoriales de Europa Laica. Idempotente.

Crea la estructura completa de agrupaciones desde los datos del volcado SQL:
- 1 agrupación NACIONAL (Europa Laica, ya creada por bootstrap — se reutiliza)
- 10 CC.AA. sintéticas para regiones sin entidad propia en el dump
- 9 CC.AA. explícitas del dump (Asturias, Baleares, Cantabria…)
- 37 agrupaciones provinciales con padre asignado

Se ejecuta via:
    docker exec <backend-container> python -m app.scripts.seeding.seed_agrupaciones_europalaica
"""

import asyncio
from sqlalchemy import select

from app.core.database import async_session
from app.modules.core.geografico.direccion import AgrupacionTerritorial, Pais


# ---------------------------------------------------------------------------
# Datos: autonomías sintéticas (no aparecen en el dump pero sus provincias sí)
# nombre_corto sirve como clave de idempotencia
# ---------------------------------------------------------------------------
CCAA_SINTETICAS = [
    ("AND", "Andalucía Europa Laica"),
    ("ARA", "Aragón Europa Laica"),
    ("CAN", "Canarias Europa Laica"),
    ("CYL", "Castilla y León Europa Laica"),
    ("CLM", "Castilla-La Mancha Europa Laica"),
    ("CAT", "Catalunya Europa Laica"),
    ("VAL", "Comunitat Valenciana Europa Laica"),
    ("EXT", "Extremadura Europa Laica"),
    ("GAL", "Galicia Europa Laica"),
    ("PVA", "País Vasco Europa Laica"),
]

# ---------------------------------------------------------------------------
# Autonomías que SÍ aparecen en el dump (padre = "EL")
# (codigo_dump, nombre_corto, nombre, email, web, telefono)
# ---------------------------------------------------------------------------
CCAA_DUMP = [
    ("00300000", "AST",   "Asturias Europa Laica",         "asturias@europalaica.org",   "www.asturiaslaica.com",  None),
    ("00400000", "BAL",   "Balears/Baleares Europa Laica", "balears@europalaica.org",    "www.europalaica.org",    None),
    ("00600000", "CANT",  "Cantabria Europa Laica",        "cantabria@europalaica.org",  "www.europalaica.org",    None),
    ("01300000", "MAD",   "Madrid Europa Laica",           "madrid@europalaica.org",     "www.europalaica.org",    None),
    ("01400000", "MUR",   "Murcia Europa Laica",           "murcia@europalaica.org",     "www.europalaica.org",    None),
    ("01500000", "NAV",   "Navarra Europa Laica",          "navarra@europalaica.org",    "www.europalaica.org",    None),
    ("01700000", "RIOJA", "La Rioja Europa Laica",         "larioja@europalaica.com",    "www.europalaica.org",    None),
    ("01800000", "CEU",   "Ceuta Europa Laica",            "ceuta@europalaica.org",      "www.europalaica.org",    None),
    ("01900000", "MEL",   "Melilla Europa Laica",          "melilla@europalaica.org",    "www.europalaica.org",    None),
]

# ---------------------------------------------------------------------------
# Provincias: (codigo_dump, nombre_corto_padre_ccaa, nombre, email)
# nombre_corto = codigo_dump (8 chars, único)
# ---------------------------------------------------------------------------
PROVINCIALES = [
    # Andalucía
    ("00104000", "AND", "Almería Europa Laica",               "almeria@europalaica.org"),
    ("00111000", "AND", "Cádiz Europa Laica",                 "cadiz@europalaica.org"),
    ("00114000", "AND", "Córdoba Europa Laica",               "cordoba@europalaica.org"),
    ("00118000", "AND", "Granada Europa Laica",               "granada@europalaica.org"),
    ("00121000", "AND", "Huelva Europa Laica",                "huelva@europalaica.org"),
    ("00123000", "AND", "Jaén Europa Laica",                  "jaen@europalaica.org"),
    ("00129000", "AND", "Málaga Europa Laica",                "malaga@europalaica.org"),
    ("00141000", "AND", "Sevilla Europa Laica",               "sevilla@europalaica.org"),
    # Aragón
    ("00222000", "ARA", "Huesca Europa Laica",                "huesca@europalaica.org"),
    ("00244000", "ARA", "Teruel Europa Laica",                "teruel@europalaica.org"),
    ("00250000", "ARA", "Zaragoza Europa Laica",              "zaragoza@europalaica.org"),
    # Canarias
    ("00535000", "CAN", "Las Palmas Europa Laica",            "laspalmas@europalaica.org"),
    ("00538000", "CAN", "Santa Cruz de Tenerife Europa Laica","santacruzdetenerife@europalaica.org"),
    # Castilla y León
    ("00705000", "CYL", "Ávila Europa Laica",                 "avila@europalaica.org"),
    ("00709000", "CYL", "Burgos Europa Laica",                "burgos@europalaica.org"),
    ("00724000", "CYL", "León Europa Laica",                  "leon@europalaica.org"),
    ("00734000", "CYL", "Palencia Europa Laica",              "palencia@europalaica.org"),
    ("00737000", "CYL", "Salamanca Europa Laica",             "salamanca@europalaica.org"),
    ("00740000", "CYL", "Segovia Europa Laica",               "segovia@europalaica.org"),
    ("00742000", "CYL", "Soria Europa Laica",                 "soria@europalaica.org"),
    ("00747000", "CYL", "Valladolid Europa Laica",            "valladolid@europalaica.org"),
    ("00749000", "CYL", "Zamora Europa Laica",                "zamora@europalaica.org"),
    # Castilla-La Mancha
    ("00802000", "CLM", "Albacete Europa Laica",              "albacete@europalaica.org"),
    ("00813000", "CLM", "Ciudad Real Europa Laica",           "ciudadreal@europalaica.org"),
    ("00816000", "CLM", "Cuenca Europa Laica",                "cuenca@europalaica.org"),
    ("00819000", "CLM", "Guadalajara Europa Laica",           "guadalajara@europalaica.org"),
    ("00845000", "CLM", "Toledo Europa Laica",                "toledo@europalaica.org"),
    # Catalunya
    ("00908000", "CAT", "Barcelona Europa Laica",             "barcelona@europalaica.org"),
    ("00917000", "CAT", "Girona/Gerona Europa Laica",         "girona@europalaica.org"),
    ("00925000", "CAT", "LLeida/Lérida Europa Laica",         "lleida@europalaica.org"),
    ("00943000", "CAT", "Tarragona Europa Laica",             "tarragona@europalaica.org"),
    # Comunitat Valenciana
    ("01003000", "VAL", "Alacant/Alicante Europa Laica",      "alicante@europalaica.org"),
    ("01012000", "VAL", "Castelló/Castellón Europa Laica",    "castello@europalaica.org"),
    ("01046000", "VAL", "València/Valencia Europa Laica",     "valencia@europalaica.org"),
    # Extremadura
    ("01106000", "EXT", "Badajoz Europa Laica",               "badajoz@europalaica.org"),
    ("01110000", "EXT", "Cáceres Europa Laica",               "caceres@europalaica.org"),
    # Galicia
    ("01215000", "GAL", "A Coruña/La Coruña Europa Laica",   "acoruna@europalaica.org"),
    ("01227000", "GAL", "Lugo Europa Laica",                  "lugo@europalaica.org"),
    ("01232000", "GAL", "Ourense/Orense Europa Laica",        "ourense@europalaica.org"),
    ("01236000", "GAL", "Pontevedra Europa Laica",            "pontevedra@europalaica.org"),
    # País Vasco
    ("01601000", "PVA", "Araba/Álava Europa Laica",           "alava@europalaica.org"),
    ("01620000", "PVA", "Gipuzkoa/Guipúzcoa Europa Laica",   "guipuzcoa@europalaica.org"),
    ("01648000", "PVA", "Bizkaia/Vizcaya Europa Laica",       "vizcaya@europalaica.org"),
]


async def _get_or_create(session, nombre_corto: str, nombre: str, tipo: str, nivel: int,
                          pais_id, padre_id, email: str | None = None,
                          web: str | None = None) -> AgrupacionTerritorial:
    existing = (
        await session.execute(
            select(AgrupacionTerritorial).where(AgrupacionTerritorial.nombre_corto == nombre_corto)
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    ag = AgrupacionTerritorial(
        nombre=nombre,
        nombre_corto=nombre_corto,
        tipo=tipo,
        nivel=nivel,
        pais_id=pais_id,
        agrupacion_padre_id=padre_id,
        email=email,
        web=web,
        activo=True,
    )
    session.add(ag)
    await session.flush()
    print(f"  + {tipo:12} {nombre}")
    return ag


async def seed():
    async with async_session() as session:
        try:
            # 1. País España
            espana = (
                await session.execute(select(Pais).where(Pais.codigo == "ES"))
            ).scalar_one_or_none()
            if not espana:
                print("[ERROR] País España (ES) no encontrado. Ejecuta bootstrap primero.")
                return
            pais_id = espana.id

            # 2. Europa Laica central (ya creada por bootstrap con nombre_corto="EL")
            europa_laica = (
                await session.execute(
                    select(AgrupacionTerritorial).where(AgrupacionTerritorial.nombre_corto == "EL")
                )
            ).scalar_one_or_none()
            if not europa_laica:
                print("[ERROR] Agrupación 'Europa Laica' (EL) no encontrada. Ejecuta bootstrap primero.")
                return
            el_id = europa_laica.id

            # Índice nombre_corto → AgrupacionTerritorial para resolución de padres
            idx: dict[str, AgrupacionTerritorial] = {"EL": europa_laica}

            # 3. CC.AA. sintéticas (padre = Europa Laica)
            print("\n--- CC.AA. sintéticas ---")
            for nc, nombre in CCAA_SINTETICAS:
                ag = await _get_or_create(session, nc, nombre, "AUTONOMICO", 3, pais_id, el_id)
                idx[nc] = ag

            # 4. CC.AA. explícitas del dump (padre = Europa Laica)
            print("\n--- CC.AA. del dump ---")
            for cod, nc, nombre, email, web, _ in CCAA_DUMP:
                ag = await _get_or_create(session, nc, nombre, "AUTONOMICO", 3, pais_id, el_id,
                                          email=email, web=web)
                idx[nc] = ag

            # 5. Agrupaciones provinciales
            print("\n--- Agrupaciones provinciales ---")
            for cod, padre_nc, nombre, email in PROVINCIALES:
                padre = idx.get(padre_nc)
                padre_id = padre.id if padre else el_id
                ag = await _get_or_create(session, cod, nombre, "PROVINCIAL", 2, pais_id, padre_id,
                                          email=email, web="www.europalaica.org")
                idx[cod] = ag

            await session.commit()
            print(f"\n[OK] Seeding completado. {len(idx) - 1} agrupaciones en total.")

        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed())
