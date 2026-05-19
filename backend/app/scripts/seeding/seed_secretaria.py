"""Seeding del módulo de Secretaría: tipos de reunión y tipos de convenio."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.secretaria.models.reunion import TipoReunion
from app.modules.secretaria.models.convenio import TipoConvenio

TIPOS_REUNION = [
    {
        "nombre": "Asamblea General Ordinaria",
        "organo": "ASAMBLEA_GENERAL",
        "descripcion": "Reunión anual ordinaria de todos los socios (Ley 1/2002 art. 11)",
        "quorum_primera_convocatoria": 50,   # mayoría absoluta en 1ª
        "quorum_segunda_convocatoria": 0,     # cualquier número en 2ª
        "antelacion_minima_dias": 15,
        "orden": 1,
        "es_inmutable": True,
    },
    {
        "nombre": "Asamblea General Extraordinaria",
        "organo": "ASAMBLEA_GENERAL",
        "descripcion": "Convocada por la Junta o a petición de socios para asuntos urgentes",
        "quorum_primera_convocatoria": 50,
        "quorum_segunda_convocatoria": 0,
        "antelacion_minima_dias": 10,
        "orden": 2,
        "es_inmutable": True,
    },
    {
        "nombre": "Reunión de Junta Directiva",
        "organo": "JUNTA_DIRECTIVA",
        "descripcion": "Reunión del órgano de representación y gestión",
        "quorum_primera_convocatoria": 50,
        "quorum_segunda_convocatoria": None,
        "antelacion_minima_dias": 3,
        "orden": 3,
        "es_inmutable": True,
    },
    {
        "nombre": "Comisión de Trabajo",
        "organo": "COMISION",
        "descripcion": "Reuniones de comisiones delegadas de la Junta",
        "quorum_primera_convocatoria": None,
        "quorum_segunda_convocatoria": None,
        "antelacion_minima_dias": 2,
        "orden": 4,
        "es_inmutable": False,
    },
]

TIPOS_CONVENIO = [
    {
        "nombre": "Convenio de colaboración",
        "descripcion": "Acuerdos de colaboración con entidades sin contraprestación económica directa",
        "es_inmutable": True,
    },
    {
        "nombre": "Acuerdo de patrocinio",
        "descripcion": "Aportaciones económicas a cambio de imagen o visibilidad",
        "es_inmutable": True,
    },
    {
        "nombre": "Adhesión a red o plataforma",
        "descripcion": "Incorporación a redes, federaciones o plataformas de tercer sector",
        "es_inmutable": True,
    },
    {
        "nombre": "Contrato de servicios",
        "descripcion": "Prestación de servicios con contraprestación económica",
        "es_inmutable": False,
    },
    {
        "nombre": "Protocolo de actuación",
        "descripcion": "Acuerdos de coordinación operativa con administraciones públicas",
        "es_inmutable": False,
    },
]


async def seed_tipos_reunion(session: AsyncSession) -> None:
    for datos in TIPOS_REUNION:
        existente = await session.execute(
            select(TipoReunion).where(TipoReunion.nombre == datos["nombre"])
        )
        if existente.scalars().first():
            continue

        tipo = TipoReunion(
            nombre=datos["nombre"],
            organo=datos["organo"],
            descripcion=datos.get("descripcion"),
            quorum_primera_convocatoria=datos.get("quorum_primera_convocatoria"),
            quorum_segunda_convocatoria=datos.get("quorum_segunda_convocatoria"),
            antelacion_minima_dias=datos.get("antelacion_minima_dias", 15),
            orden=datos.get("orden", 0),
            activo=True,
            es_inmutable=datos.get("es_inmutable", False),
        )
        session.add(tipo)

    await session.commit()
    print(f"[secretaria] Tipos de reunión: {len(TIPOS_REUNION)} registros verificados")


async def seed_tipos_convenio(session: AsyncSession) -> None:
    for datos in TIPOS_CONVENIO:
        existente = await session.execute(
            select(TipoConvenio).where(TipoConvenio.nombre == datos["nombre"])
        )
        if existente.scalars().first():
            continue

        tipo = TipoConvenio(
            nombre=datos["nombre"],
            descripcion=datos.get("descripcion"),
            activo=True,
            es_inmutable=datos.get("es_inmutable", False),
        )
        session.add(tipo)

    await session.commit()
    print(f"[secretaria] Tipos de convenio: {len(TIPOS_CONVENIO)} registros verificados")


async def seed_secretaria(session: AsyncSession) -> None:
    """Punto de entrada único para el seeding del módulo de secretaría."""
    await seed_tipos_reunion(session)
    await seed_tipos_convenio(session)
