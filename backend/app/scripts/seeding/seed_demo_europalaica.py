"""Datos de demostración de Europa Laica (fake). Idempotente y autónomo.

Genera un entorno completo de prueba SIN depender de ningún volcado externo
ni de datos reales:

  1. País España + sus 50 provincias y 2 ciudades autónomas.
  2. Niveles organizativos territoriales (Nacional / Autonómica / Provincial).
  3. Estructura Europa Laica: 1 nacional → 19 agrupaciones autonómicas →
     50 agrupaciones provinciales.
  4. Roles orgánicos (PRESIDENTE, SECRETARIO, TESORERO, VOCAL, COORDINADOR…)
     y sus cargos con el enlace CargoRol.
  5. Miembros ficticios repartidos por agrupación (nombres y DNI generados).
  6. Una junta directiva por agrupación autonómica + la nacional.
  7. Nombramientos vigentes (presidencia, secretaría, tesorería y vocalías)
     asignando miembros reales de cada agrupación.

Todo se identifica por claves naturales (código de país, nombre de unidad,
email de miembro…) para poder re-ejecutarlo sin duplicar.

Ejecutar:
    docker exec <backend> python -m app.scripts.seeding.seed_demo_europalaica
"""
from __future__ import annotations

import asyncio
import random
import uuid
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.modules.core.geografico.direccion import Pais, Provincia, UnidadOrganizativa
from app.modules.core.geografico.nivel_organizativo import (
    NivelOrganizativo, NaturalezaUnidad, VinculoUnidad,
)
from app.modules.acceso.models.rol import Rol, TipoRol
from app.modules.acceso.models.cargo import Cargo, CargoRol
from app.modules.membresia.models.miembro import Miembro, TipoMiembro
from app.modules.membresia.models.estado_miembro import EstadoMiembro
from app.modules.membresia.models.junta import JuntaDirectiva
from app.modules.membresia.models.historial_nombramiento import HistorialNombramiento


random.seed(20260528)  # reproducible

# ---------------------------------------------------------------------------
# Comunidades autónomas → (nombre_corto, [(codigo_provincia, nombre_provincia)])
# ---------------------------------------------------------------------------
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

NOMBRES = [
    "Ana", "Carmen", "María", "Laura", "Marta", "Lucía", "Elena", "Sara", "Paula", "Cristina",
    "José", "Antonio", "Manuel", "Francisco", "David", "Javier", "Daniel", "Carlos", "Miguel", "Alejandro",
    "Pablo", "Sergio", "Jorge", "Alberto", "Raúl", "Rosa", "Pilar", "Isabel", "Teresa", "Nuria",
]
APELLIDOS = [
    "García", "Martínez", "López", "Sánchez", "González", "Rodríguez", "Fernández", "Gómez", "Martín", "Jiménez",
    "Ruiz", "Hernández", "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez", "Navarro",
    "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Serrano", "Blanco", "Molina", "Castro", "Ortiz",
]

DNI_LETRAS = "TRWAGMYFPDXBNJZSQVHLCKE"


def _dni() -> str:
    n = random.randint(10_000_000, 99_999_999)
    return f"{n}{DNI_LETRAS[n % 23]}"


def _nombre_completo() -> tuple[str, str, str]:
    return random.choice(NOMBRES), random.choice(APELLIDOS), random.choice(APELLIDOS)


# Cargos a nombrar en cada junta: (codigo_rol, nombre_cargo)
CARGOS_JUNTA = [
    ("PRESIDENTE", "Presidente/a"),
    ("VICEPRESIDENTE", "Vicepresidente/a"),
    ("SECRETARIO", "Secretario/a"),
    ("TESORERO", "Tesorero/a"),
    ("VOCAL", "Vocal"),
]

ROLES_ORG = [
    ("PRESIDENTE", "Presidente"),
    ("VICEPRESIDENTE", "Vicepresidente"),
    ("SECRETARIO", "Secretario"),
    ("TESORERO", "Tesorero"),
    ("VOCAL", "Vocal"),
    ("COORDINADOR", "Coordinador territorial"),
]


async def _get_or_create_pais_espana(s: AsyncSession) -> Pais:
    pais = (await s.execute(select(Pais).where(Pais.codigo == "ES"))).scalar_one_or_none()
    if pais is None:
        pais = Pais(id=uuid.uuid4(), codigo="ES", codigo_iso3="ESP", nombre="España",
                    nombre_oficial="Reino de España", codigo_telefono="+34",
                    continente="Europa", activo=True)
        s.add(pais)
        await s.flush()
        print("[demo] País España creado")
    return pais


async def _ensure_provincias(s: AsyncSession, pais: Pais) -> dict[str, Provincia]:
    """Devuelve {nombre_provincia: Provincia}, creando las que falten."""
    out: dict[str, Provincia] = {}
    creadas = 0
    for _ccaa, (_corto, provs) in CCAA.items():
        for codigo, nombre in provs:
            prov = (await s.execute(
                select(Provincia).where(Provincia.pais_id == pais.id, Provincia.codigo == codigo)
            )).scalars().first()
            if prov is None:
                prov = Provincia(id=uuid.uuid4(), pais_id=pais.id, codigo=codigo,
                                 nombre=nombre, comunidad_autonoma=_ccaa, activo=True)
                s.add(prov)
                creadas += 1
            out[nombre] = prov
    if creadas:
        await s.flush()
        print(f"[demo] Provincias: +{creadas} creadas")
    return out


async def _ensure_niveles(s: AsyncSession) -> dict[int, NivelOrganizativo]:
    nombres = {1: "Europa Laica España", 2: "Agrupación autonómica", 3: "Agrupación provincial"}
    niveles: dict[int, NivelOrganizativo] = {}
    padre = None
    for n in (1, 2, 3):
        nv = (await s.execute(
            select(NivelOrganizativo).where(NivelOrganizativo.nivel == n,
                                            NivelOrganizativo.naturaleza == NaturalezaUnidad.TERRITORIAL)
        )).scalars().first()
        if nv is None:
            nv = NivelOrganizativo(id=uuid.uuid4(), nombre=nombres[n],
                                   naturaleza=NaturalezaUnidad.TERRITORIAL,
                                   vinculo=VinculoUnidad.INTERNA, nivel=n,
                                   padre_tipo_id=padre, activo=True)
            s.add(nv)
            await s.flush()
            print(f"[demo] NivelOrganizativo nivel={n} creado")
        niveles[n] = nv
        padre = nv.id
    return niveles


async def _get_unidad(s: AsyncSession, nombre: str) -> UnidadOrganizativa | None:
    return (await s.execute(
        select(UnidadOrganizativa).where(UnidadOrganizativa.nombre == nombre)
    )).scalars().first()


async def _ensure_estructura(s: AsyncSession, pais: Pais, niveles, provincias) -> list[UnidadOrganizativa]:
    """Crea nacional + CCAA + provinciales. Devuelve todas las unidades hoja+ramas."""
    todas: list[UnidadOrganizativa] = []

    nacional = await _get_unidad(s, "Europa Laica")
    if nacional is None:
        nacional = UnidadOrganizativa(id=uuid.uuid4(), nombre="Europa Laica", nombre_corto="EL",
                                      tipo_id=niveles[1].id, pais_id=pais.id, activo=True)
        s.add(nacional)
        await s.flush()
        print("[demo] Unidad nacional 'Europa Laica' creada")
    todas.append(nacional)

    creadas_ccaa = creadas_prov = 0
    for ccaa_nombre, (corto, provs) in CCAA.items():
        u_ccaa_nombre = f"{ccaa_nombre} Europa Laica"
        u_ccaa = await _get_unidad(s, u_ccaa_nombre)
        if u_ccaa is None:
            u_ccaa = UnidadOrganizativa(id=uuid.uuid4(), nombre=u_ccaa_nombre, nombre_corto=corto,
                                        tipo_id=niveles[2].id, agrupacion_padre_id=nacional.id,
                                        pais_id=pais.id, activo=True)
            s.add(u_ccaa)
            await s.flush()
            creadas_ccaa += 1
        todas.append(u_ccaa)

        for codigo, prov_nombre in provs:
            u_prov_nombre = f"{prov_nombre} Europa Laica"
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
            todas.append(u_prov)

    if creadas_ccaa or creadas_prov:
        print(f"[demo] Unidades: +{creadas_ccaa} autonómicas, +{creadas_prov} provinciales")
    return todas


async def _ensure_roles(s: AsyncSession) -> dict[str, Rol]:
    out: dict[str, Rol] = {}
    for codigo, nombre in ROLES_ORG:
        rol = (await s.execute(select(Rol).where(Rol.codigo == codigo))).scalars().first()
        if rol is None:
            rol = Rol(id=uuid.uuid4(), codigo=codigo, nombre=nombre,
                      descripcion=f"Cargo orgánico: {nombre}", tipo=TipoRol.ORGANIZACION,
                      activo=True)
            s.add(rol)
            await s.flush()
        out[codigo] = rol
    return out


async def _ensure_cargos(s: AsyncSession, roles) -> dict[str, Cargo]:
    out: dict[str, Cargo] = {}
    for codigo_rol, nombre_cargo in CARGOS_JUNTA:
        cargo = (await s.execute(select(Cargo).where(Cargo.nombre == nombre_cargo))).scalars().first()
        if cargo is None:
            cargo = Cargo(id=uuid.uuid4(), nombre=nombre_cargo,
                          descripcion=f"Cargo de {nombre_cargo} en junta directiva", activo=True)
            s.add(cargo)
            await s.flush()
            # enlace Cargo↔Rol
            rol = roles.get(codigo_rol)
            if rol:
                existe = (await s.execute(
                    select(CargoRol).where(CargoRol.cargo_id == cargo.id, CargoRol.rol_id == rol.id)
                )).scalars().first()
                if existe is None:
                    s.add(CargoRol(id=uuid.uuid4(), cargo_id=cargo.id, rol_id=rol.id))
                    await s.flush()
        out[codigo_rol] = cargo
    return out


async def _ensure_miembros(s: AsyncSession, unidades, niveles, tipo_miembro, estado_alta) -> dict[uuid.UUID, list[Miembro]]:
    """Crea miembros fake por unidad. Devuelve {agrupacion_id: [miembros]}.

    Reparto por nivel: nacional 8, autonómica 4, provincial 6.
    """
    objetivo_por_nivel = {niveles[1].id: 8, niveles[2].id: 4, niveles[3].id: 6}
    por_agrupacion: dict[uuid.UUID, list[Miembro]] = {}
    creados = 0
    for u in unidades:
        existentes = (await s.execute(
            select(Miembro).where(Miembro.agrupacion_id == u.id, Miembro.eliminado == False)
        )).scalars().all()
        por_agrupacion[u.id] = list(existentes)

        objetivo = objetivo_por_nivel.get(u.tipo_id, 6)
        faltan = max(0, objetivo - len(existentes))
        for _ in range(faltan):
            nombre, ap1, ap2 = _nombre_completo()
            slug = f"{nombre}.{ap1}".lower().replace(" ", "")
            m = Miembro(
                id=uuid.uuid4(),
                nombre=nombre, apellido1=ap1, apellido2=ap2,
                tipo_documento="DNI", numero_documento=_dni(),
                email=f"{slug}.{random.randint(100,999)}@demo.europalaica.test",
                telefono=f"6{random.randint(10_000_000, 99_999_999)}",
                agrupacion_id=u.id,
                tipo_miembro_id=tipo_miembro.id if tipo_miembro else None,
                estado_id=estado_alta.id if estado_alta else None,
                fecha_alta=date(2024, random.randint(1, 12), random.randint(1, 28)),
                activo=True,
                es_voluntario=random.random() < 0.3,
            )
            s.add(m)
            por_agrupacion[u.id].append(m)
            creados += 1
    if creados:
        await s.flush()
        print(f"[demo] Miembros fake: +{creados} creados")
    return por_agrupacion


async def _ensure_juntas_y_nombramientos(s: AsyncSession, unidades, niveles, miembros_por_agr, cargos, roles) -> None:
    juntas_creadas = nombr_creados = 0
    nivel_provincial = niveles[3].id
    for u in unidades:
        # Solo nacional + autonómicas tienen junta directiva en la demo
        if u.tipo_id == nivel_provincial:
            continue
        junta = (await s.execute(
            select(JuntaDirectiva).where(JuntaDirectiva.agrupacion_id == u.id, JuntaDirectiva.eliminado == False)
        )).scalars().first()
        if junta is None:
            junta = JuntaDirectiva(id=uuid.uuid4(), agrupacion_id=u.id,
                                   nombre=f"Junta Directiva — {u.nombre}",
                                   fecha_constitucion=date(2024, 1, 15), activa=True)
            s.add(junta)
            await s.flush()
            juntas_creadas += 1

        # Nombramientos: asigna miembros de esa agrupación a los cargos
        candidatos = list(miembros_por_agr.get(u.id, []))
        random.shuffle(candidatos)
        # ¿ya hay nombramientos vigentes en esta agrupación?
        vigentes = (await s.execute(
            select(func.count(HistorialNombramiento.id)).where(
                HistorialNombramiento.agrupacion_id == u.id,
                HistorialNombramiento.estado == "ACTIVO",
                HistorialNombramiento.eliminado == False,
            )
        )).scalar() or 0
        if vigentes > 0 or not candidatos:
            continue
        for i, (codigo_rol, _nombre) in enumerate(CARGOS_JUNTA):
            if i >= len(candidatos):
                break
            miembro = candidatos[i]
            cargo = cargos.get(codigo_rol)
            rol = roles.get(codigo_rol)
            s.add(HistorialNombramiento(
                id=uuid.uuid4(), miembro_id=miembro.id,
                cargo_id=cargo.id if cargo else None,
                rol_id=rol.id if rol else None,
                agrupacion_id=u.id,
                fecha_inicio=date(2024, 1, 15), estado="ACTIVO",
                tipo_origen="DEMO",
                motivo="Nombramiento de demostración",
            ))
            nombr_creados += 1
    if juntas_creadas or nombr_creados:
        await s.flush()
        print(f"[demo] Juntas: +{juntas_creadas} · Nombramientos: +{nombr_creados}")


async def main() -> None:
    async with async_session() as s:
        try:
            pais = await _get_or_create_pais_espana(s)
            provincias = await _ensure_provincias(s, pais)
            niveles = await _ensure_niveles(s)
            unidades = await _ensure_estructura(s, pais, niveles, provincias)

            tipo_miembro = (await s.execute(select(TipoMiembro).order_by(TipoMiembro.nombre))).scalars().first()
            estado_alta = (await s.execute(select(EstadoMiembro).where(EstadoMiembro.nombre == "Alta"))).scalars().first()

            miembros_por_agr = await _ensure_miembros(s, unidades, niveles, tipo_miembro, estado_alta)
            roles = await _ensure_roles(s)
            cargos = await _ensure_cargos(s, roles)
            await _ensure_juntas_y_nombramientos(s, unidades, niveles, miembros_por_agr, cargos, roles)

            await s.commit()
            print("[demo] ✓ Datos de demostración Europa Laica listos.")
        except Exception:
            await s.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
