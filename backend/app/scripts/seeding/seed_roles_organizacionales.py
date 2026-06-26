"""Seed de roles organizacionales (tipos de cargo).

Crea los roles de tipo ORGANIZACION que representan los cargos:
- PRESIDENTE, VICEPRESIDENTE, SECRETARIO, TESORERO, VOCAL
- COORDINADOR (territorial, autonómico, etc.)
- OTROS cargos organizativos
"""
import asyncio
import uuid
from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol, TipoRol


ORGANIZACION_ROLES = [
    {
        "codigo": "PRESIDENTE",
        "nombre": "Presidente",
        "descripcion": "Presidencia de la organización",
        "nivel": 1,
        "es_territorial": False,
        "nivel_territorial": None,
    },
    {
        "codigo": "VICEPRESIDENTE",
        "nombre": "Vicepresidente",
        "descripcion": "Vicepresidencia",
        "nivel": 2,
        "es_territorial": False,
        "nivel_territorial": None,
    },
    {
        "codigo": "SECRETARIO",
        "nombre": "Secretario",
        "descripcion": "Secretaría",
        "nivel": 3,
        "es_territorial": False,
        "nivel_territorial": None,
    },
    {
        "codigo": "TESORERO",
        "nombre": "Tesorero",
        "descripcion": "Tesorería",
        "nivel": 4,
        "es_territorial": False,
        "nivel_territorial": None,
    },
    {
        "codigo": "VOCAL",
        "nombre": "Vocal",
        "descripcion": "Vocal de la junta directiva",
        "nivel": 5,
        "es_territorial": False,
        "nivel_territorial": None,
    },
    {
        "codigo": "COORDINADOR",
        "nombre": "Coordinador",
        "descripcion": "Coordinador territorial/autonómico",
        "nivel": 6,
        "es_territorial": True,
        "nivel_territorial": "AUTONOMICO",
    },
    # COORD_PROV / COORD_LOCAL retirados (2026-06-26): el título del coordinador se
    # compone dinámicamente con la denominación del nivel (ver tituloCargo en
    # DetalleAgrupacion); existe un único rol territorial genérico COORDINADOR.
    {
        # Ámbito = su campaña (no territorial). Se asigna al nombrar coordinador de una campaña.
        "codigo": "COORDINADOR_CAMPANA",
        "nombre": "Coordinador de campaña",
        "descripcion": "Coordinador responsable de una campaña concreta",
        "nivel": 9,
        "es_territorial": False,
        "nivel_territorial": None,
    },
    {
        # Captación de socios / extensión: gestiona el CRM de contactos (leads).
        "codigo": "EXTENSION",
        "nombre": "Extensión",
        "descripcion": "Captación de socios y extensión: gestión del CRM de contactos",
        "nivel": 10,
        "es_territorial": False,
        "nivel_territorial": None,
    },
]


async def seed():
    print("\n" + "=" * 60)
    print("SEED ROLES ORGANIZACIONALES")
    print("=" * 60)

    async with async_session() as session:
        # Verificar existentes
        existing = (await session.execute(
            select(Rol).where(Rol.tipo == TipoRol.ORGANIZACION)
        )).scalars().all()
        existing_by_codigo = {r.codigo: r for r in existing}
        
        print(f"\n  Roles ORGANIZACION existentes: {len(existing)}")
        
        creados = 0
        for rol_data in ORGANIZACION_ROLES:
            if rol_data["codigo"] in existing_by_codigo:
                print(f"  [EXISTE] {rol_data['codigo']}")
                continue
            
            rol = Rol(
                id=uuid.uuid4(),
                codigo=rol_data["codigo"],
                nombre=rol_data["nombre"],
                descripcion=rol_data["descripcion"],
                tipo=TipoRol.ORGANIZACION,
                nivel=rol_data["nivel"],
                es_territorial=rol_data["es_territorial"],
                nivel_territorial=rol_data["nivel_territorial"],
                activo=True,
                sistema=False,
            )
            session.add(rol)
            creados += 1
            print(f"  [OK] {rol_data['codigo']}: {rol_data['nombre']}")
        
        await session.commit()
        print(f"\n  Total creados: {creados}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed())
