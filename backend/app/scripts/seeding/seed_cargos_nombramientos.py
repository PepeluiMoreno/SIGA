"""Seed de cargos orgánicos, su mapeo a roles y nombramientos territoriales.

Hace tres cosas, todas idempotentes:

  1. Asegura los roles organizacionales TESORERO y COORDINADOR.
  2. Crea los cargos «Tesorero» y «Coordinador territorial» y los enlaza
     con sus roles de sistema vía CargoRol.
  3. Genera una pareja de nombramientos ACTIVOS (un tesorero + un
     coordinador) para cada agrupación territorial (unidad organizativa),
     asignando a cada cargo un miembro distinto que no tenga ya un
     nombramiento vigente.

Ejecutar:
    docker exec <backend> python -m app.scripts.seeding.seed_cargos_nombramientos
"""
import asyncio
from datetime import date

from sqlalchemy import select, text

from app.core.database import async_session
from app.modules.acceso.models.cargo import Cargo, CargoRol
from app.modules.acceso.models.rol import Rol, TipoRol
from app.modules.membresia.models.historial_nombramiento import HistorialNombramiento
from app.modules.membresia.models.miembro import Miembro


# (codigo, nombre, descripcion, nivel, es_territorial, nivel_territorial)
_ROLES = [
    ("TESORERO",    "Tesorero",    "Tesorería",                          4, False, None),
    ("COORDINADOR", "Coordinador", "Coordinador territorial/autonómico",  6, True,  "AUTONOMICO"),
]

# (clave, nombre_cargo, descripcion, codigo_rol)
_CARGOS = [
    ("tesorero",    "Tesorero",
     "Responsable de la tesorería de la agrupación territorial.",        "TESORERO"),
    ("coordinador", "Coordinador territorial",
     "Coordina la actividad de la agrupación territorial.",              "COORDINADOR"),
]


async def _ensure_roles(session) -> dict[str, Rol]:
    """Asegura los roles organizacionales necesarios. Devuelve {codigo: Rol}."""
    roles: dict[str, Rol] = {}
    for codigo, nombre, descripcion, nivel, es_terr, niv_terr in _ROLES:
        rol = (await session.execute(
            select(Rol).where(Rol.codigo == codigo)
        )).scalar_one_or_none()
        if rol is None:
            rol = Rol(
                codigo=codigo, nombre=nombre, descripcion=descripcion,
                tipo=TipoRol.ORGANIZACION, nivel=nivel,
                es_territorial=es_terr, nivel_territorial=niv_terr,
                activo=True, sistema=False,
            )
            session.add(rol)
            await session.flush()
            print(f"  [rol   +] {codigo}")
        else:
            print(f"  [rol   =] {codigo}")
        roles[codigo] = rol
    return roles


async def _ensure_cargos(session, roles: dict[str, Rol]) -> dict[str, tuple[Cargo, Rol]]:
    """Crea los cargos y su enlace CargoRol. Devuelve {clave: (Cargo, Rol)}."""
    cargos: dict[str, tuple[Cargo, Rol]] = {}
    for clave, nombre, descripcion, codigo_rol in _CARGOS:
        cargo = (await session.execute(
            select(Cargo).where(Cargo.nombre == nombre)
        )).scalar_one_or_none()
        if cargo is None:
            cargo = Cargo(
                nombre=nombre, descripcion=descripcion,
                tipo_unidad_id=None,          # válido en cualquier nivel territorial
                requiere_aprobacion=False,
                max_simultaneos=1, activo=True,
            )
            session.add(cargo)
            await session.flush()
            print(f"  [cargo +] {nombre}")
        else:
            print(f"  [cargo =] {nombre}")

        rol = roles[codigo_rol]
        enlace = (await session.execute(
            select(CargoRol).where(
                CargoRol.cargo_id == cargo.id, CargoRol.rol_id == rol.id
            )
        )).scalar_one_or_none()
        if enlace is None:
            session.add(CargoRol(cargo_id=cargo.id, rol_id=rol.id))
            print(f"  [c-rol +] {nombre} → {codigo_rol}")
        else:
            print(f"  [c-rol =] {nombre} → {codigo_rol}")
        cargos[clave] = (cargo, rol)
    return cargos


async def _normalizar_coord_legacy(session, roles: dict[str, Rol]) -> None:
    """Idempotente: repunta los nombramientos que aún usan roles coordinador de
    nombre fijo (COORD_PROV/COORD_LOCAL) al COORDINADOR genérico. El título del
    cargo se compone dinámicamente con la denominación del nivel de la unidad
    (ver DetalleAgrupacion.tituloCargo), así que no hace falta un rol por nivel.
    """
    coord = roles.get("COORDINADOR")
    if coord is None:
        return
    legacy_ids = (await session.execute(
        select(Rol.id).where(Rol.codigo.in_(["COORD_PROV", "COORD_LOCAL"]))
    )).scalars().all()
    if not legacy_ids:
        return
    nombramientos = (await session.execute(
        select(HistorialNombramiento).where(HistorialNombramiento.rol_id.in_(legacy_ids))
    )).scalars().all()
    for nom in nombramientos:
        nom.rol_id = coord.id
    if nombramientos:
        print(f"  [norm  ~] {len(nombramientos)} nombramiento(s) coordinador legacy → COORDINADOR")


async def seed() -> None:
    print("=" * 60)
    print("SEED CARGOS + NOMBRAMIENTOS TERRITORIALES")
    print("=" * 60)

    async with async_session() as session:
        roles = await _ensure_roles(session)
        await _normalizar_coord_legacy(session, roles)
        cargos = await _ensure_cargos(session, roles)
        await session.flush()

        # Agrupaciones territoriales (tabla unidad organizativa, destino del FK
        # historial_nombramientos.agrupacion_id).
        agrupaciones = (await session.execute(text(
            "SELECT id, nombre FROM unidades_organizativas "
            "WHERE eliminado = false ORDER BY nombre"
        ))).all()
        print(f"\n  Agrupaciones territoriales: {len(agrupaciones)}")

        # Miembros que ya ostentan un cargo vigente — no se reutilizan.
        ocupados = set((await session.execute(
            select(HistorialNombramiento.miembro_id).where(
                HistorialNombramiento.fecha_fin.is_(None),
                HistorialNombramiento.estado == "ACTIVO",
                HistorialNombramiento.eliminado.is_(False),
            )
        )).scalars().all())

        disponibles = [
            m for m in (await session.execute(
                select(Miembro)
                .where(Miembro.eliminado.is_(False))
                .order_by(Miembro.apellido1, Miembro.nombre)
            )).scalars().all()
            if m.id not in ocupados
        ]
        pool = iter(disponibles)
        print(f"  Miembros disponibles: {len(disponibles)}")

        hoy = date.today()
        creados = saltados = sin_miembros = 0

        for agr_id, agr_nombre in agrupaciones:
            for clave in ("tesorero", "coordinador"):
                cargo, rol = cargos[clave]

                # ¿ya hay un titular vigente de ese cargo en la agrupación?
                existe = (await session.execute(
                    select(HistorialNombramiento.id).where(
                        HistorialNombramiento.cargo_id == cargo.id,
                        HistorialNombramiento.agrupacion_id == agr_id,
                        HistorialNombramiento.fecha_fin.is_(None),
                        HistorialNombramiento.estado == "ACTIVO",
                        HistorialNombramiento.eliminado.is_(False),
                    )
                )).first()
                if existe:
                    saltados += 1
                    continue

                miembro = next(pool, None)
                if miembro is None:
                    sin_miembros += 1
                    continue

                session.add(HistorialNombramiento(
                    miembro_id=miembro.id,
                    cargo_id=cargo.id,
                    rol_id=rol.id,
                    agrupacion_id=agr_id,
                    fecha_inicio=hoy,
                    fecha_fin=None,
                    estado="ACTIVO",
                    tipo_origen="SEED",
                    motivo=f"Nombramiento inicial de {cargo.nombre.lower()} "
                           f"({agr_nombre}) — seed de datos.",
                ))
                creados += 1

        await session.commit()

        print("\n" + "-" * 60)
        print(f"  Nombramientos creados:  {creados}")
        print(f"  Saltados (ya existían): {saltados}")
        if sin_miembros:
            print(f"  Sin miembro disponible: {sin_miembros}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(seed())
