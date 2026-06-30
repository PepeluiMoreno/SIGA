"""Siembra la estructura territorial completa de España, jerárquica, con la
palabra «Laica» detrás del nombre de cada unidad. Idempotente.

Jerarquía (3 niveles):
    Europa Laica                      (estatal)
      └─ «{Comunidad autónoma} Laica» (autonómico)
           └─ «{Provincia} Laica»     (provincial)

Reutiliza el catálogo de CCAA/provincias del demo de Europa Laica, pero contra
el modelo vigente (Contacto/UnidadOrganizativa), sin depender de la clase
`Miembro` retirada en el refactor CRM. Además asigna los contactos existentes a
unas cuantas provincias para que el filtro de ámbito territorial muestre
resultados.

Ejecutar:
    docker exec siga_dev_backend python -m app.scripts.seeding.seed_demo_territorial
"""
from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.modules.core.geografico.direccion import Pais, Provincia, UnidadOrganizativa
from app.modules.core.geografico.nivel_organizativo import (
    NivelOrganizativo, NaturalezaUnidad, VinculoUnidad,
)
from app.modules.membresia.models.contacto import Contacto

# Comunidades autónomas → (nombre_corto, [(codigo_provincia, nombre_provincia)])
CCAA = {
    "Andalucía":            ("AND",  [("04", "Almería"), ("11", "Cádiz"), ("14", "Córdoba"), ("18", "Granada"), ("21", "Huelva"), ("23", "Jaén"), ("29", "Málaga"), ("41", "Sevilla")]),
    "Aragón":               ("ARA",  [("22", "Huesca"), ("44", "Teruel"), ("50", "Zaragoza")]),
    "Asturias":             ("AST",  [("33", "Asturias")]),
    "Illes Balears":        ("BAL",  [("07", "Illes Balears")]),
    "Canarias":             ("CAN",  [("35", "Las Palmas"), ("38", "Santa Cruz de Tenerife")]),
    "Cantabria":            ("CANT", [("39", "Cantabria")]),
    "Castilla y León":      ("CYL",  [("05", "Ávila"), ("09", "Burgos"), ("24", "León"), ("34", "Palencia"), ("37", "Salamanca"), ("40", "Segovia"), ("42", "Soria"), ("47", "Valladolid"), ("49", "Zamora")]),
    "Castilla-La Mancha":   ("CLM",  [("02", "Albacete"), ("13", "Ciudad Real"), ("16", "Cuenca"), ("19", "Guadalajara"), ("45", "Toledo")]),
    "Cataluña":             ("CAT",  [("08", "Barcelona"), ("17", "Girona"), ("25", "Lleida"), ("43", "Tarragona")]),
    "Comunitat Valenciana": ("VAL",  [("03", "Alicante/Alacant"), ("12", "Castellón/Castelló"), ("46", "Valencia/València")]),
    "Extremadura":          ("EXT",  [("06", "Badajoz"), ("10", "Cáceres")]),
    "Galicia":              ("GAL",  [("15", "Coruña, A"), ("27", "Lugo"), ("32", "Ourense"), ("36", "Pontevedra")]),
    "La Rioja":             ("RIOJA",[("26", "Rioja, La")]),
    "Madrid":               ("MAD",  [("28", "Madrid")]),
    "Murcia":               ("MUR",  [("30", "Murcia")]),
    "Navarra":              ("NAV",  [("31", "Navarra")]),
    "País Vasco":           ("PVA",  [("01", "Araba/Álava"), ("20", "Gipuzkoa"), ("48", "Bizkaia")]),
    "Ceuta":                ("CEU",  [("51", "Ceuta")]),
    "Melilla":              ("MEL",  [("52", "Melilla")]),
}

NIVELES = {1: "Ámbito estatal", 2: "Comunidad autónoma", 3: "Provincia"}


async def _get_or_create_pais_espana(s: AsyncSession) -> Pais:
    pais = (await s.execute(select(Pais).where(Pais.codigo == "ES"))).scalar_one_or_none()
    if pais is None:
        pais = Pais(id=uuid.uuid4(), codigo="ES", codigo_iso3="ESP", nombre="España",
                    nombre_oficial="Reino de España", codigo_telefono="+34",
                    continente="Europa", activo=True)
        s.add(pais)
        await s.flush()
        print("[territorial] País España creado")
    return pais


async def _ensure_provincias(s: AsyncSession, pais: Pais) -> dict[str, Provincia]:
    out: dict[str, Provincia] = {}
    creadas = 0
    for ccaa, (_corto, provs) in CCAA.items():
        for codigo, nombre in provs:
            prov = (await s.execute(
                select(Provincia).where(Provincia.pais_id == pais.id, Provincia.codigo == codigo)
            )).scalars().first()
            if prov is None:
                prov = Provincia(id=uuid.uuid4(), pais_id=pais.id, codigo=codigo,
                                 nombre=nombre, comunidad_autonoma=ccaa, activo=True)
                s.add(prov)
                creadas += 1
            out[nombre] = prov
    if creadas:
        await s.flush()
        print(f"[territorial] Provincias: +{creadas} creadas")
    return out


async def _ensure_niveles(s: AsyncSession) -> dict[int, NivelOrganizativo]:
    niveles: dict[int, NivelOrganizativo] = {}
    padre = None
    for n in (1, 2, 3):
        nv = (await s.execute(
            select(NivelOrganizativo).where(
                NivelOrganizativo.nivel == n,
                NivelOrganizativo.naturaleza == NaturalezaUnidad.TERRITORIAL,
            )
        )).scalars().first()
        if nv is None:
            nv = NivelOrganizativo(id=uuid.uuid4(), nombre=NIVELES[n],
                                   naturaleza=NaturalezaUnidad.TERRITORIAL,
                                   vinculo=VinculoUnidad.INTERNA, nivel=n,
                                   padre_tipo_id=padre, activo=True)
            s.add(nv)
            await s.flush()
            print(f"[territorial] NivelOrganizativo nivel={n} '{NIVELES[n]}' creado")
        niveles[n] = nv
        padre = nv.id
    return niveles


async def _get_unidad(s: AsyncSession, nombre: str) -> UnidadOrganizativa | None:
    return (await s.execute(
        select(UnidadOrganizativa).where(UnidadOrganizativa.nombre == nombre)
    )).scalars().first()


async def _ensure_estructura(s: AsyncSession, pais, niveles, provincias) -> list[UnidadOrganizativa]:
    """Crea Europa Laica (estatal) + «{CCAA} Laica» + «{Provincia} Laica»."""
    provinciales: list[UnidadOrganizativa] = []

    nacional = await _get_unidad(s, "Europa Laica")
    if nacional is None:
        nacional = UnidadOrganizativa(id=uuid.uuid4(), nombre="Europa Laica", nombre_corto="EL",
                                      tipo_id=niveles[1].id, pais_id=pais.id, activo=True)
        s.add(nacional)
        await s.flush()
        print("[territorial] Unidad estatal 'Europa Laica' creada")

    creadas_ccaa = creadas_prov = 0
    for ccaa_nombre, (corto, provs) in CCAA.items():
        u_ccaa_nombre = f"{ccaa_nombre} Laica"
        u_ccaa = await _get_unidad(s, u_ccaa_nombre)
        if u_ccaa is None:
            u_ccaa = UnidadOrganizativa(id=uuid.uuid4(), nombre=u_ccaa_nombre, nombre_corto=corto,
                                        tipo_id=niveles[2].id, agrupacion_padre_id=nacional.id,
                                        pais_id=pais.id, activo=True)
            s.add(u_ccaa)
            await s.flush()
            creadas_ccaa += 1

        for codigo, prov_nombre in provs:
            u_prov_nombre = f"{prov_nombre} Laica"
            u_prov = await _get_unidad(s, u_prov_nombre)
            if u_prov is None:
                prov = provincias.get(prov_nombre)
                u_prov = UnidadOrganizativa(id=uuid.uuid4(), nombre=u_prov_nombre, nombre_corto=codigo,
                                            tipo_id=niveles[3].id, agrupacion_padre_id=u_ccaa.id,
                                            pais_id=pais.id,
                                            provincia_id=prov.id if prov else None, activo=True)
                s.add(u_prov)
                await s.flush()
                creadas_prov += 1
            provinciales.append(u_prov)

    if creadas_ccaa or creadas_prov:
        print(f"[territorial] Unidades: +{creadas_ccaa} autonómicas, +{creadas_prov} provinciales")
    return provinciales


async def _asignar_contactos(s: AsyncSession, provinciales: list[UnidadOrganizativa]) -> None:
    """Asigna a unas pocas provincias los contactos que aún no tienen agrupación,
    para que el filtro de ámbito territorial muestre resultados."""
    if not provinciales:
        return
    # Provincias destino preferentes (si existen), para concentrar la demo.
    preferidas = ["Madrid Laica", "Sevilla Laica", "Barcelona Laica", "Valencia/València Laica"]
    destino = [u for n in preferidas for u in provinciales if u.nombre == n] or provinciales[:4]

    contactos = (await s.execute(
        select(Contacto).where(Contacto.agrupacion_id.is_(None), Contacto.eliminado == False)
    )).scalars().all()

    asignados = 0
    for i, c in enumerate(contactos):
        c.agrupacion_id = destino[i % len(destino)].id
        asignados += 1
    if asignados:
        await s.flush()
        print(f"[territorial] Contactos asignados a agrupación: {asignados} "
              f"(en {', '.join(u.nombre for u in destino)})")


async def main() -> None:
    from app.scripts.seeding._guard import abort_if_production
    abort_if_production("seeding demo territorial")
    async with async_session() as s:
        try:
            pais = await _get_or_create_pais_espana(s)
            provincias = await _ensure_provincias(s, pais)
            niveles = await _ensure_niveles(s)
            provinciales = await _ensure_estructura(s, pais, niveles, provincias)
            await _asignar_contactos(s, provinciales)
            await s.commit()
            print("[territorial] Estructura territorial sembrada.")
        except Exception:
            await s.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
