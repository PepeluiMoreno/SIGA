"""Seeding de contactos FAKE para desarrollo (NO usar en producción).

Puebla el directorio CRM con un surtido representativo:
- Personas físicas con distintas facetas (socio, voluntario, donante, firmante,
  simpatizante, empleado), algunas multi-faceta.
- Un caso con histórico: una vinculación de socio cerrada + otra vigente (re-alta).
- Personas jurídicas (instituciones) con/ sin faceta.

Idempotente: identifica cada contacto por su documento (numeroDocumento/cif) y
omite los que ya existan, así que se puede ejecutar varias veces sin duplicar.

Uso (en el contenedor backend de dev):
    python -m app.scripts.seed_fake_contactos
"""
from __future__ import annotations

import asyncio
from datetime import date

from sqlalchemy import select, func

from app.core.database import async_session
from app.modules.membresia.models.contacto import Contacto
from app.modules.membresia.models.vinculacion import Vinculacion, Socio, Voluntario
from app.modules.membresia.models.tipo_vinculacion import TipoVinculacion
from app.modules.core.geografico.direccion import UnidadOrganizativa


# Definiciones canónicas de los tipos de vinculación (mismas que catalogos_base).
# El seed las crea si faltan, para no depender de que el bootstrap ya corriera.
_TIPOS_DEF = [
    ("FIRMANTE",     "Firmante",     "central",     "COMUNICACION_FIRMAS",            False),
    ("SIMPATIZANTE", "Simpatizante", "central",     "COMUNICACION_SIMPATIZANTES",     False),
    ("SOCIO",        "Socio",        "territorial", "MEMBRESIA_SOCIO_GESTIONAR",       True),
    ("VOLUNTARIO",   "Voluntario",   "territorial", "MEMBRESIA_VOLUNTARIO_GESTIONAR",  True),
    ("DONANTE",      "Donante",      "central",     "TESORERIA_DONANTES",              False),
    ("EMPLEADO",     "Empleado",     "central",     "RECURSOS_HUMANOS",                True),
]


# --- Catálogo de datos fake (determinista) -----------------------------------
# Cada faceta es (codigo_tipo_vinculacion, dict_satelite_o_None, dict_overrides).
# El dict de overrides admite fecha_inicio/fecha_fin/estado para casos históricos.

_PF = [
    {
        "nombre": "Ana", "apellido1": "García", "apellido2": "López",
        "email": "ana.garcia@fake.siga.local", "telefono": "600100101", "doc": "FAKE-PF-0001",
        "sexo": "M", "facetas": [
            ("SOCIO", {"numero_socio": "S-0001", "iban": "ES7620770024003102575766", "cuota_mensual": 10}, {}),
            ("VOLUNTARIO", {"disponibilidad": "tardes", "horas_disponibles_semana": 6,
                            "intereses": "comunicación", "puede_conducir": True, "vehiculo_propio": True}, {}),
        ],
    },
    {
        "nombre": "Bruno", "apellido1": "Martín", "apellido2": "Ruiz",
        "email": "bruno.martin@fake.siga.local", "telefono": "600100102", "doc": "FAKE-PF-0002",
        "sexo": "H", "facetas": [
            ("SOCIO", {"numero_socio": "S-0002", "es_honor": True}, {}),
        ],
    },
    {
        "nombre": "Carmen", "apellido1": "Díaz", "apellido2": "Soler",
        "email": "carmen.diaz@fake.siga.local", "telefono": "600100103", "doc": "FAKE-PF-0003",
        "sexo": "M", "facetas": [
            ("SOCIO", {"numero_socio": "S-0003", "iban": "ES9121000418450200051332", "cuota_mensual": 15}, {}),
            ("DONANTE", None, {}),
        ],
    },
    {
        "nombre": "David", "apellido1": "Fernández", "apellido2": "Gil",
        "email": "david.fernandez@fake.siga.local", "telefono": "600100104", "doc": "FAKE-PF-0004",
        "sexo": "H", "facetas": [
            ("VOLUNTARIO", {"disponibilidad": "fines de semana", "horas_disponibles_semana": 4,
                            "intereses": "eventos", "vehiculo_propio": False}, {}),
        ],
    },
    {
        "nombre": "Elena", "apellido1": "Romero", "apellido2": "Vega",
        "email": "elena.romero@fake.siga.local", "telefono": "600100105", "doc": "FAKE-PF-0005",
        "sexo": "M", "facetas": [("DONANTE", None, {})],
    },
    {
        "nombre": "Félix", "apellido1": "Moreno", "apellido2": "Sanz",
        "email": "felix.moreno@fake.siga.local", "telefono": "600100106", "doc": "FAKE-PF-0006",
        "sexo": "H", "facetas": [("FIRMANTE", None, {})],
    },
    {
        "nombre": "Gloria", "apellido1": "Navarro", "apellido2": "Pol",
        "email": "gloria.navarro@fake.siga.local", "telefono": "600100107", "doc": "FAKE-PF-0007",
        "sexo": "M", "facetas": [("SIMPATIZANTE", None, {})],
    },
    {
        "nombre": "Hugo", "apellido1": "Castro", "apellido2": "León",
        "email": "hugo.castro@fake.siga.local", "telefono": "600100108", "doc": "FAKE-PF-0008",
        "sexo": "H", "facetas": [("EMPLEADO", None, {})],
    },
    {
        # Histórico: socio que se dio de baja (2014-2017) y volvió (2021-vigente).
        "nombre": "Irene", "apellido1": "Prieto", "apellido2": "Mas",
        "email": "irene.prieto@fake.siga.local", "telefono": "600100109", "doc": "FAKE-PF-0009",
        "sexo": "M", "facetas": [
            ("SOCIO", {"numero_socio": "S-0009-OLD", "estado_socio": "baja"},
             {"fecha_inicio": date(2014, 1, 1), "fecha_fin": date(2017, 6, 30), "estado": "cerrada"}),
            ("SOCIO", {"numero_socio": "S-0009", "iban": "ES8023100001180000012345", "cuota_mensual": 12},
             {"fecha_inicio": date(2021, 3, 1)}),
        ],
    },
    {
        "nombre": "Jorge", "apellido1": "Ortega", "apellido2": "Ríos",
        "email": "jorge.ortega@fake.siga.local", "telefono": "600100110", "doc": "FAKE-PF-0010",
        "sexo": "H", "facetas": [
            ("SOCIO", {"numero_socio": "S-0010", "iban": "ES1000492352082414205416", "cuota_mensual": 10}, {}),
            ("VOLUNTARIO", {"disponibilidad": "mañanas", "horas_disponibles_semana": 8,
                            "intereses": "logística", "puede_conducir": True}, {}),
            ("FIRMANTE", None, {}),
        ],
    },
    {
        "nombre": "Lucía", "apellido1": "Santos", "apellido2": "Vidal",
        "email": "lucia.santos@fake.siga.local", "telefono": "600100111", "doc": "FAKE-PF-0011",
        "sexo": "M", "facetas": [
            ("VOLUNTARIO", {"disponibilidad": "flexible", "horas_disponibles_semana": 10}, {}),
            ("SIMPATIZANTE", None, {}),
        ],
    },
    {
        # Contacto suelto, sin ninguna faceta (solo está en el directorio).
        "nombre": "Marcos", "apellido1": "Iglesias", "apellido2": "Cano",
        "email": "marcos.iglesias@fake.siga.local", "telefono": "600100112", "doc": "FAKE-PF-0012",
        "sexo": "H", "facetas": [],
    },
]

_PJ = [
    {
        "razon_social": "Fundación Laicismo Activo", "cif": "FAKE-PJ-0001",
        "email": "contacto@laicismoactivo.fake", "telefono": "910200201",
        "actividad_principal": "Promoción del laicismo", "facetas": [("DONANTE", None, {})],
    },
    {
        "razon_social": "Asociación Cultural Libre Pensamiento", "cif": "FAKE-PJ-0002",
        "email": "info@librepensamiento.fake", "telefono": "910200202",
        "actividad_principal": "Actividades culturales", "facetas": [],
    },
    {
        "razon_social": "Editorial Razón S.L.", "cif": "FAKE-PJ-0003",
        "email": "pedidos@editorialrazon.fake", "telefono": "910200203",
        "actividad_principal": "Edición de libros", "facetas": [("DONANTE", None, {})],
    },
    {
        "razon_social": "Ayuntamiento de Villaejemplo", "cif": "FAKE-PJ-0004",
        "email": "registro@villaejemplo.fake", "telefono": "910200204",
        "actividad_principal": "Administración local", "facetas": [],
    },
]


async def _ensure_tipos(session) -> int:
    """Crea los TipoVinculacion que falten (idempotente). Devuelve cuántos creó."""
    existentes = {c for (c,) in (await session.execute(select(TipoVinculacion.codigo))).all()}
    creados = 0
    for codigo, nombre, ambito, area, sat in _TIPOS_DEF:
        if codigo in existentes:
            continue
        session.add(TipoVinculacion(
            codigo=codigo, nombre=nombre, ambito=ambito,
            area_responsable=area, requiere_satelite=sat, activo=True,
        ))
        creados += 1
    if creados:
        await session.flush()
    return creados


async def _tipo_ids(session) -> dict[str, "uuid.UUID"]:  # noqa: F821
    rows = (await session.execute(select(TipoVinculacion.codigo, TipoVinculacion.id))).all()
    return {codigo: tid for (codigo, tid) in rows}


async def _alta_faceta(session, contacto_id, codigo, tipo_ids, *, sat, overrides, agrupacion_id):
    tid = tipo_ids.get(codigo)
    if tid is None:
        print(f"  · faceta {codigo} omitida (TipoVinculacion no sembrado)")
        return
    vinc = Vinculacion(
        contacto_id=contacto_id,
        tipo_vinculacion_id=tid,
        fecha_inicio=overrides.get("fecha_inicio", date(2022, 1, 1)),
        fecha_fin=overrides.get("fecha_fin"),
        estado=overrides.get("estado", "activa"),
        agrupacion_id=agrupacion_id,
    )
    session.add(vinc)
    await session.flush()
    if codigo == "SOCIO":
        session.add(Socio(vinculacion_id=vinc.id, **(sat or {})))
    elif codigo == "VOLUNTARIO":
        session.add(Voluntario(vinculacion_id=vinc.id, **(sat or {})))
    # DONANTE/FIRMANTE/SIMPATIZANTE/EMPLEADO: sin satélite (requiere_satelite=False).


async def _num_vinculaciones(session, contacto_id) -> int:
    return (await session.execute(
        select(func.count(Vinculacion.id)).where(Vinculacion.contacto_id == contacto_id)
    )).scalar() or 0


async def main() -> None:
    async with async_session() as session:
        nuevos_tipos = await _ensure_tipos(session)
        if nuevos_tipos:
            print(f"[seed] TipoVinculacion creados: {nuevos_tipos}")
        tipo_ids = await _tipo_ids(session)
        agrupacion_id = (await session.execute(
            select(UnidadOrganizativa.id).limit(1)
        )).scalar_one_or_none()

        stats = {"creados": 0, "rellenados": 0, "intactos": 0}

        async def procesar(p, tipo, doc, etiqueta, build_kwargs):
            existe = (await session.execute(
                select(Contacto.id).where(Contacto.numero_documento == doc)
            )).scalar_one_or_none()

            if existe is None:
                c = Contacto(tipo=tipo, numero_documento=doc,
                             agrupacion_id=agrupacion_id, activo=True, **build_kwargs)
                session.add(c)
                await session.flush()
                cid, facetas, marca, accion = c.id, p["facetas"], "+", "creados"
            elif await _num_vinculaciones(session, existe) == 0:
                # Existe pero sin facetas (p.ej. de una ejecución anterior fallida): rellenar.
                cid, facetas, marca, accion = existe, p["facetas"], "~", "rellenados"
            else:
                stats["intactos"] += 1
                return

            for (codigo, sat, overrides) in facetas:
                await _alta_faceta(session, cid, codigo, tipo_ids,
                                   sat=sat, overrides=overrides, agrupacion_id=agrupacion_id)
            stats[accion] += 1
            print(f"{marca} {etiqueta} ({len(facetas)} facetas)")

        for p in _PF:
            await procesar(
                p, "PERSONA_FISICA", p["doc"],
                f"PF {p['nombre']} {p['apellido1']}",
                dict(nombre=p["nombre"], apellido1=p["apellido1"], apellido2=p.get("apellido2"),
                     email=p.get("email"), telefono=p.get("telefono"), sexo=p.get("sexo"),
                     tipo_documento="DNI"),
            )

        for p in _PJ:
            await procesar(
                p, "PERSONA_JURIDICA", p["cif"],
                f"PJ {p['razon_social']}",
                dict(nombre=p["razon_social"], razon_social=p["razon_social"],
                     tipo_documento="CIF", cif=p["cif"],
                     actividad_principal=p.get("actividad_principal"),
                     email=p.get("email"), telefono=p.get("telefono")),
            )

        await session.commit()
        print(f"\n[seed_fake_contactos] Creados: {stats['creados']} · "
              f"Rellenados: {stats['rellenados']} · Intactos: {stats['intactos']}")


if __name__ == "__main__":
    asyncio.run(main())
