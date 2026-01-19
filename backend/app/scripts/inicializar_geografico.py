"""Script para inicializar datos geográficos básicos (España)."""

import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..domains.geografico.models import Pais, Provincia, Municipio


# Datos de país España
PAIS_ESPANA = {
    'codigo': 'ES',
    'codigo_iso3': 'ESP',
    'nombre': 'España',
    'nombre_oficial': 'Reino de España',
    'codigo_telefono': '+34',
    'continente': 'Europa',
    'activo': True
}

# Provincias de España
PROVINCIAS_ESPANA = [
    {'codigo': '01', 'nombre': 'Araba/Álava'},
    {'codigo': '02', 'nombre': 'Albacete'},
    {'codigo': '03', 'nombre': 'Alicante/Alacant'},
    {'codigo': '04', 'nombre': 'Almería'},
    {'codigo': '05', 'nombre': 'Ávila'},
    {'codigo': '06', 'nombre': 'Badajoz'},
    {'codigo': '07', 'nombre': 'Balears, Illes'},
    {'codigo': '08', 'nombre': 'Barcelona'},
    {'codigo': '09', 'nombre': 'Burgos'},
    {'codigo': '10', 'nombre': 'Cáceres'},
    {'codigo': '11', 'nombre': 'Cádiz'},
    {'codigo': '12', 'nombre': 'Castellón/Castelló'},
    {'codigo': '13', 'nombre': 'Ciudad Real'},
    {'codigo': '14', 'nombre': 'Córdoba'},
    {'codigo': '15', 'nombre': 'Coruña, A'},
    {'codigo': '16', 'nombre': 'Cuenca'},
    {'codigo': '17', 'nombre': 'Girona'},
    {'codigo': '18', 'nombre': 'Granada'},
    {'codigo': '19', 'nombre': 'Guadalajara'},
    {'codigo': '20', 'nombre': 'Gipuzkoa'},
    {'codigo': '21', 'nombre': 'Huelva'},
    {'codigo': '22', 'nombre': 'Huesca'},
    {'codigo': '23', 'nombre': 'Jaén'},
    {'codigo': '24', 'nombre': 'León'},
    {'codigo': '25', 'nombre': 'Lleida'},
    {'codigo': '26', 'nombre': 'Rioja, La'},
    {'codigo': '27', 'nombre': 'Lugo'},
    {'codigo': '28', 'nombre': 'Madrid'},
    {'codigo': '29', 'nombre': 'Málaga'},
    {'codigo': '30', 'nombre': 'Murcia'},
    {'codigo': '31', 'nombre': 'Navarra'},
    {'codigo': '32', 'nombre': 'Ourense'},
    {'codigo': '33', 'nombre': 'Asturias'},
    {'codigo': '34', 'nombre': 'Palencia'},
    {'codigo': '35', 'nombre': 'Palmas, Las'},
    {'codigo': '36', 'nombre': 'Pontevedra'},
    {'codigo': '37', 'nombre': 'Salamanca'},
    {'codigo': '38', 'nombre': 'Santa Cruz de Tenerife'},
    {'codigo': '39', 'nombre': 'Cantabria'},
    {'codigo': '40', 'nombre': 'Segovia'},
    {'codigo': '41', 'nombre': 'Sevilla'},
    {'codigo': '42', 'nombre': 'Soria'},
    {'codigo': '43', 'nombre': 'Tarragona'},
    {'codigo': '44', 'nombre': 'Teruel'},
    {'codigo': '45', 'nombre': 'Toledo'},
    {'codigo': '46', 'nombre': 'Valencia/València'},
    {'codigo': '47', 'nombre': 'Valladolid'},
    {'codigo': '48', 'nombre': 'Bizkaia'},
    {'codigo': '49', 'nombre': 'Zamora'},
    {'codigo': '50', 'nombre': 'Zaragoza'},
    {'codigo': '51', 'nombre': 'Ceuta'},
    {'codigo': '52', 'nombre': 'Melilla'},
]

# Algunos municipios principales (capitales de provincia)
MUNICIPIOS_PRINCIPALES = [
    {'provincia_codigo': '28', 'codigo': '28079', 'nombre': 'Madrid', 'codigo_postal': '28001'},
    {'provincia_codigo': '08', 'codigo': '08019', 'nombre': 'Barcelona', 'codigo_postal': '08001'},
    {'provincia_codigo': '46', 'codigo': '46250', 'nombre': 'Valencia', 'codigo_postal': '46001'},
    {'provincia_codigo': '41', 'codigo': '41091', 'nombre': 'Sevilla', 'codigo_postal': '41001'},
    {'provincia_codigo': '50', 'codigo': '50297', 'nombre': 'Zaragoza', 'codigo_postal': '50001'},
    {'provincia_codigo': '29', 'codigo': '29067', 'nombre': 'Málaga', 'codigo_postal': '29001'},
    {'provincia_codigo': '30', 'codigo': '30030', 'nombre': 'Murcia', 'codigo_postal': '30001'},
    {'provincia_codigo': '35', 'codigo': '35016', 'nombre': 'Las Palmas de Gran Canaria', 'codigo_postal': '35001'},
    {'provincia_codigo': '07', 'codigo': '07040', 'nombre': 'Palma', 'codigo_postal': '07001'},
    {'provincia_codigo': '48', 'codigo': '48020', 'nombre': 'Bilbao', 'codigo_postal': '48001'},
    {'provincia_codigo': '03', 'codigo': '03014', 'nombre': 'Alicante/Alacant', 'codigo_postal': '03001'},
    {'provincia_codigo': '14', 'codigo': '14021', 'nombre': 'Córdoba', 'codigo_postal': '14001'},
    {'provincia_codigo': '47', 'codigo': '47186', 'nombre': 'Valladolid', 'codigo_postal': '47001'},
    {'provincia_codigo': '20', 'codigo': '20069', 'nombre': 'Donostia-San Sebastián', 'codigo_postal': '20001'},
    {'provincia_codigo': '18', 'codigo': '18087', 'nombre': 'Granada', 'codigo_postal': '18001'},
    {'provincia_codigo': '15', 'codigo': '15030', 'nombre': 'A Coruña', 'codigo_postal': '15001'},
    {'provincia_codigo': '01', 'codigo': '01059', 'nombre': 'Vitoria-Gasteiz', 'codigo_postal': '01001'},
    {'provincia_codigo': '33', 'codigo': '33044', 'nombre': 'Oviedo', 'codigo_postal': '33001'},
    {'provincia_codigo': '38', 'codigo': '38038', 'nombre': 'Santa Cruz de Tenerife', 'codigo_postal': '38001'},
    {'provincia_codigo': '31', 'codigo': '31201', 'nombre': 'Pamplona/Iruña', 'codigo_postal': '31001'},
]


async def inicializar_pais_espana(session: AsyncSession) -> Pais:
    """Inicializa el país España."""
    result = await session.execute(
        select(Pais).where(Pais.codigo == PAIS_ESPANA['codigo'])
    )
    pais = result.scalar_one_or_none()

    if not pais:
        pais = Pais(id=uuid.uuid4(), **PAIS_ESPANA)
        session.add(pais)
        await session.commit()
        await session.refresh(pais)
        print(f"  * País creado: {pais.nombre}")
    else:
        print(f"  - País ya existe: {pais.nombre}")

    return pais


async def inicializar_provincias(session: AsyncSession, pais: Pais) -> dict:
    """Inicializa las provincias de España."""
    provincias_map = {}

    for provincia_data in PROVINCIAS_ESPANA:
        result = await session.execute(
            select(Provincia).where(
                Provincia.pais_id == pais.id,
                Provincia.codigo == provincia_data['codigo']
            )
        )
        provincia = result.scalar_one_or_none()

        if not provincia:
            provincia = Provincia(
                id=uuid.uuid4(),
                pais_id=pais.id,
                codigo=provincia_data['codigo'],
                nombre=provincia_data['nombre'],
                activo=True
            )
            session.add(provincia)
            print(f"  * Provincia creada: {provincia_data['nombre']}")
        else:
            print(f"  - Provincia ya existe: {provincia_data['nombre']}")

        provincias_map[provincia_data['codigo']] = provincia

    await session.commit()
    return provincias_map


async def inicializar_municipios(session: AsyncSession, provincias_map: dict) -> None:
    """Inicializa municipios principales."""
    for municipio_data in MUNICIPIOS_PRINCIPALES:
        provincia_codigo = municipio_data.pop('provincia_codigo')
        provincia = provincias_map.get(provincia_codigo)

        if not provincia:
            print(f"  ⚠ Provincia {provincia_codigo} no encontrada para municipio {municipio_data['nombre']}")
            continue

        result = await session.execute(
            select(Municipio).where(
                Municipio.provincia_id == provincia.id,
                Municipio.codigo == municipio_data['codigo']
            )
        )
        municipio = result.scalar_one_or_none()

        if not municipio:
            municipio = Municipio(
                id=uuid.uuid4(),
                provincia_id=provincia.id,
                codigo=municipio_data['codigo'],
                nombre=municipio_data['nombre'],
                codigo_postal=municipio_data.get('codigo_postal'),
                activo=True
            )
            session.add(municipio)
            print(f"  * Municipio creado: {municipio_data['nombre']}")
        else:
            print(f"  - Municipio ya existe: {municipio_data['nombre']}")

    await session.commit()


async def inicializar_geografico(session: AsyncSession) -> None:
    """Inicializa datos geográficos básicos."""
    print("\n=== Inicializando Datos Geográficos ===\n")

    print("1. País:")
    pais = await inicializar_pais_espana(session)

    print("\n2. Provincias:")
    provincias_map = await inicializar_provincias(session, pais)

    print(f"\n3. Municipios principales ({len(MUNICIPIOS_PRINCIPALES)} capitales):")
    await inicializar_municipios(session, provincias_map)

    print("\n=== Datos geográficos inicializados correctamente ===")
    print(f"Total: 1 país, {len(PROVINCIAS_ESPANA)} provincias, {len(MUNICIPIOS_PRINCIPALES)} municipios\n")


# Función main para ejecutar el script directamente
async def main():
    """Función principal para ejecutar el script."""
    from ..infrastructure.database import get_session

    async with get_session() as session:
        await inicializar_geografico(session)


if __name__ == "__main__":
    asyncio.run(main())
