"""Script para inicializar datos geográficos básicos (España)."""

import uuid
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..modules.core.geografico import Pais, Provincia, Municipio


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

# Países adicionales (Europa y principales)
PAISES_ADICIONALES = [
    # ── Europa Occidental ──
    {'codigo': 'PT', 'codigo_iso3': 'PRT', 'nombre': 'Portugal', 'codigo_telefono': '+351', 'continente': 'Europa'},
    {'codigo': 'FR', 'codigo_iso3': 'FRA', 'nombre': 'Francia', 'codigo_telefono': '+33', 'continente': 'Europa'},
    {'codigo': 'DE', 'codigo_iso3': 'DEU', 'nombre': 'Alemania', 'codigo_telefono': '+49', 'continente': 'Europa'},
    {'codigo': 'IT', 'codigo_iso3': 'ITA', 'nombre': 'Italia', 'codigo_telefono': '+39', 'continente': 'Europa'},
    {'codigo': 'GB', 'codigo_iso3': 'GBR', 'nombre': 'Reino Unido', 'codigo_telefono': '+44', 'continente': 'Europa'},
    {'codigo': 'IE', 'codigo_iso3': 'IRL', 'nombre': 'Irlanda', 'codigo_telefono': '+353', 'continente': 'Europa'},
    {'codigo': 'BE', 'codigo_iso3': 'BEL', 'nombre': 'Bélgica', 'codigo_telefono': '+32', 'continente': 'Europa'},
    {'codigo': 'NL', 'codigo_iso3': 'NLD', 'nombre': 'Países Bajos', 'codigo_telefono': '+31', 'continente': 'Europa'},
    {'codigo': 'LU', 'codigo_iso3': 'LUX', 'nombre': 'Luxemburgo', 'codigo_telefono': '+352', 'continente': 'Europa'},
    {'codigo': 'MC', 'codigo_iso3': 'MCO', 'nombre': 'Mónaco', 'codigo_telefono': '+377', 'continente': 'Europa'},
    {'codigo': 'AD', 'codigo_iso3': 'AND', 'nombre': 'Andorra', 'codigo_telefono': '+376', 'continente': 'Europa'},
    {'codigo': 'LI', 'codigo_iso3': 'LIE', 'nombre': 'Liechtenstein', 'codigo_telefono': '+423', 'continente': 'Europa'},
    # ── Europa Nórdica ──
    {'codigo': 'SE', 'codigo_iso3': 'SWE', 'nombre': 'Suecia', 'codigo_telefono': '+46', 'continente': 'Europa'},
    {'codigo': 'NO', 'codigo_iso3': 'NOR', 'nombre': 'Noruega', 'codigo_telefono': '+47', 'continente': 'Europa'},
    {'codigo': 'DK', 'codigo_iso3': 'DNK', 'nombre': 'Dinamarca', 'codigo_telefono': '+45', 'continente': 'Europa'},
    {'codigo': 'FI', 'codigo_iso3': 'FIN', 'nombre': 'Finlandia', 'codigo_telefono': '+358', 'continente': 'Europa'},
    {'codigo': 'IS', 'codigo_iso3': 'ISL', 'nombre': 'Islandia', 'codigo_telefono': '+354', 'continente': 'Europa'},
    {'codigo': 'EE', 'codigo_iso3': 'EST', 'nombre': 'Estonia', 'codigo_telefono': '+372', 'continente': 'Europa'},
    {'codigo': 'LV', 'codigo_iso3': 'LVA', 'nombre': 'Letonia', 'codigo_telefono': '+371', 'continente': 'Europa'},
    {'codigo': 'LT', 'codigo_iso3': 'LTU', 'nombre': 'Lituania', 'codigo_telefono': '+370', 'continente': 'Europa'},
    # ── Europa Central ──
    {'codigo': 'AT', 'codigo_iso3': 'AUT', 'nombre': 'Austria', 'codigo_telefono': '+43', 'continente': 'Europa'},
    {'codigo': 'CH', 'codigo_iso3': 'CHE', 'nombre': 'Suiza', 'codigo_telefono': '+41', 'continente': 'Europa'},
    {'codigo': 'PL', 'codigo_iso3': 'POL', 'nombre': 'Polonia', 'codigo_telefono': '+48', 'continente': 'Europa'},
    {'codigo': 'CZ', 'codigo_iso3': 'CZE', 'nombre': 'República Checa', 'codigo_telefono': '+420', 'continente': 'Europa'},
    {'codigo': 'SK', 'codigo_iso3': 'SVK', 'nombre': 'Eslovaquia', 'codigo_telefono': '+421', 'continente': 'Europa'},
    {'codigo': 'HU', 'codigo_iso3': 'HUN', 'nombre': 'Hungría', 'codigo_telefono': '+36', 'continente': 'Europa'},
    {'codigo': 'SI', 'codigo_iso3': 'SVN', 'nombre': 'Eslovenia', 'codigo_telefono': '+386', 'continente': 'Europa'},
    # ── Europa del Sur ──
    {'codigo': 'GR', 'codigo_iso3': 'GRC', 'nombre': 'Grecia', 'codigo_telefono': '+30', 'continente': 'Europa'},
    {'codigo': 'CY', 'codigo_iso3': 'CYP', 'nombre': 'Chipre', 'codigo_telefono': '+357', 'continente': 'Europa'},
    {'codigo': 'MT', 'codigo_iso3': 'MLT', 'nombre': 'Malta', 'codigo_telefono': '+356', 'continente': 'Europa'},
    {'codigo': 'HR', 'codigo_iso3': 'HRV', 'nombre': 'Croacia', 'codigo_telefono': '+385', 'continente': 'Europa'},
    {'codigo': 'BA', 'codigo_iso3': 'BIH', 'nombre': 'Bosnia y Herzegovina', 'codigo_telefono': '+387', 'continente': 'Europa'},
    {'codigo': 'RS', 'codigo_iso3': 'SRB', 'nombre': 'Serbia', 'codigo_telefono': '+381', 'continente': 'Europa'},
    {'codigo': 'ME', 'codigo_iso3': 'MNE', 'nombre': 'Montenegro', 'codigo_telefono': '+382', 'continente': 'Europa'},
    {'codigo': 'AL', 'codigo_iso3': 'ALB', 'nombre': 'Albania', 'codigo_telefono': '+355', 'continente': 'Europa'},
    {'codigo': 'MK', 'codigo_iso3': 'MKD', 'nombre': 'Macedonia del Norte', 'codigo_telefono': '+389', 'continente': 'Europa'},
    {'codigo': 'XK', 'codigo_iso3': 'XKX', 'nombre': 'Kosovo', 'codigo_telefono': '+383', 'continente': 'Europa'},
    {'codigo': 'BG', 'codigo_iso3': 'BGR', 'nombre': 'Bulgaria', 'codigo_telefono': '+359', 'continente': 'Europa'},
    {'codigo': 'RO', 'codigo_iso3': 'ROU', 'nombre': 'Rumanía', 'codigo_telefono': '+40', 'continente': 'Europa'},
    {'codigo': 'MD', 'codigo_iso3': 'MDA', 'nombre': 'Moldavia', 'codigo_telefono': '+373', 'continente': 'Europa'},
    {'codigo': 'SM', 'codigo_iso3': 'SMR', 'nombre': 'San Marino', 'codigo_telefono': '+378', 'continente': 'Europa'},
    {'codigo': 'VA', 'codigo_iso3': 'VAT', 'nombre': 'Ciudad del Vaticano', 'codigo_telefono': '+379', 'continente': 'Europa'},
    # ── Europa del Este ──
    {'codigo': 'RU', 'codigo_iso3': 'RUS', 'nombre': 'Rusia', 'codigo_telefono': '+7', 'continente': 'Europa'},
    {'codigo': 'UA', 'codigo_iso3': 'UKR', 'nombre': 'Ucrania', 'codigo_telefono': '+380', 'continente': 'Europa'},
    {'codigo': 'BY', 'codigo_iso3': 'BLR', 'nombre': 'Bielorrusia', 'codigo_telefono': '+375', 'continente': 'Europa'},
    # ── Europa Transcontinental ──
    {'codigo': 'TR', 'codigo_iso3': 'TUR', 'nombre': 'Turquía', 'codigo_telefono': '+90', 'continente': 'Europa'},
    {'codigo': 'GE', 'codigo_iso3': 'GEO', 'nombre': 'Georgia', 'codigo_telefono': '+995', 'continente': 'Europa'},
    {'codigo': 'AM', 'codigo_iso3': 'ARM', 'nombre': 'Armenia', 'codigo_telefono': '+374', 'continente': 'Europa'},
    {'codigo': 'AZ', 'codigo_iso3': 'AZE', 'nombre': 'Azerbaiyán', 'codigo_telefono': '+994', 'continente': 'Europa'},
    {'codigo': 'KZ', 'codigo_iso3': 'KAZ', 'nombre': 'Kazajistán', 'codigo_telefono': '+7', 'continente': 'Europa'},
    # ── América Latina ──
    {'codigo': 'AR', 'codigo_iso3': 'ARG', 'nombre': 'Argentina', 'codigo_telefono': '+54', 'continente': 'América'},
    {'codigo': 'BR', 'codigo_iso3': 'BRA', 'nombre': 'Brasil', 'codigo_telefono': '+55', 'continente': 'América'},
    {'codigo': 'MX', 'codigo_iso3': 'MEX', 'nombre': 'México', 'codigo_telefono': '+52', 'continente': 'América'},
    {'codigo': 'CO', 'codigo_iso3': 'COL', 'nombre': 'Colombia', 'codigo_telefono': '+57', 'continente': 'América'},
    {'codigo': 'CL', 'codigo_iso3': 'CHL', 'nombre': 'Chile', 'codigo_telefono': '+56', 'continente': 'América'},
    {'codigo': 'PE', 'codigo_iso3': 'PER', 'nombre': 'Perú', 'codigo_telefono': '+51', 'continente': 'América'},
    {'codigo': 'VE', 'codigo_iso3': 'VEN', 'nombre': 'Venezuela', 'codigo_telefono': '+58', 'continente': 'América'},
    {'codigo': 'EC', 'codigo_iso3': 'ECU', 'nombre': 'Ecuador', 'codigo_telefono': '+593', 'continente': 'América'},
    {'codigo': 'CU', 'codigo_iso3': 'CUB', 'nombre': 'Cuba', 'codigo_telefono': '+53', 'continente': 'América'},
    {'codigo': 'DO', 'codigo_iso3': 'DOM', 'nombre': 'República Dominicana', 'codigo_telefono': '+1', 'continente': 'América'},
    {'codigo': 'UY', 'codigo_iso3': 'URY', 'nombre': 'Uruguay', 'codigo_telefono': '+598', 'continente': 'América'},
    {'codigo': 'PY', 'codigo_iso3': 'PRY', 'nombre': 'Paraguay', 'codigo_telefono': '+595', 'continente': 'América'},
    {'codigo': 'BO', 'codigo_iso3': 'BOL', 'nombre': 'Bolivia', 'codigo_telefono': '+591', 'continente': 'América'},
    {'codigo': 'CR', 'codigo_iso3': 'CRI', 'nombre': 'Costa Rica', 'codigo_telefono': '+506', 'continente': 'América'},
    {'codigo': 'PA', 'codigo_iso3': 'PAN', 'nombre': 'Panamá', 'codigo_telefono': '+507', 'continente': 'América'},
    {'codigo': 'GT', 'codigo_iso3': 'GTM', 'nombre': 'Guatemala', 'codigo_telefono': '+502', 'continente': 'América'},
    {'codigo': 'HN', 'codigo_iso3': 'HND', 'nombre': 'Honduras', 'codigo_telefono': '+504', 'continente': 'América'},
    {'codigo': 'SV', 'codigo_iso3': 'SLV', 'nombre': 'El Salvador', 'codigo_telefono': '+503', 'continente': 'América'},
    {'codigo': 'NI', 'codigo_iso3': 'NIC', 'nombre': 'Nicaragua', 'codigo_telefono': '+505', 'continente': 'América'},
    # ── África ──
    {'codigo': 'MA', 'codigo_iso3': 'MAR', 'nombre': 'Marruecos', 'codigo_telefono': '+212', 'continente': 'África'},
    {'codigo': 'DZ', 'codigo_iso3': 'DZA', 'nombre': 'Argelia', 'codigo_telefono': '+213', 'continente': 'África'},
    {'codigo': 'TN', 'codigo_iso3': 'TUN', 'nombre': 'Túnez', 'codigo_telefono': '+216', 'continente': 'África'},
    {'codigo': 'EG', 'codigo_iso3': 'EGY', 'nombre': 'Egipto', 'codigo_telefono': '+20', 'continente': 'África'},
    {'codigo': 'NG', 'codigo_iso3': 'NGA', 'nombre': 'Nigeria', 'codigo_telefono': '+234', 'continente': 'África'},
    {'codigo': 'SN', 'codigo_iso3': 'SEN', 'nombre': 'Senegal', 'codigo_telefono': '+221', 'continente': 'África'},
    {'codigo': 'GH', 'codigo_iso3': 'GHA', 'nombre': 'Ghana', 'codigo_telefono': '+233', 'continente': 'África'},
    {'codigo': 'KE', 'codigo_iso3': 'KEN', 'nombre': 'Kenia', 'codigo_telefono': '+254', 'continente': 'África'},
    {'codigo': 'ZA', 'codigo_iso3': 'ZAF', 'nombre': 'Sudáfrica', 'codigo_telefono': '+27', 'continente': 'África'},
    # ── Asia ──
    {'codigo': 'CN', 'codigo_iso3': 'CHN', 'nombre': 'China', 'codigo_telefono': '+86', 'continente': 'Asia'},
    {'codigo': 'JP', 'codigo_iso3': 'JPN', 'nombre': 'Japón', 'codigo_telefono': '+81', 'continente': 'Asia'},
    {'codigo': 'KR', 'codigo_iso3': 'KOR', 'nombre': 'Corea del Sur', 'codigo_telefono': '+82', 'continente': 'Asia'},
    {'codigo': 'IN', 'codigo_iso3': 'IND', 'nombre': 'India', 'codigo_telefono': '+91', 'continente': 'Asia'},
    {'codigo': 'PK', 'codigo_iso3': 'PAK', 'nombre': 'Pakistán', 'codigo_telefono': '+92', 'continente': 'Asia'},
    {'codigo': 'BD', 'codigo_iso3': 'BGD', 'nombre': 'Bangladés', 'codigo_telefono': '+880', 'continente': 'Asia'},
    {'codigo': 'PH', 'codigo_iso3': 'PHL', 'nombre': 'Filipinas', 'codigo_telefono': '+63', 'continente': 'Asia'},
    {'codigo': 'ID', 'codigo_iso3': 'IDN', 'nombre': 'Indonesia', 'codigo_telefono': '+62', 'continente': 'Asia'},
    {'codigo': 'TH', 'codigo_iso3': 'THA', 'nombre': 'Tailandia', 'codigo_telefono': '+66', 'continente': 'Asia'},
    {'codigo': 'VN', 'codigo_iso3': 'VNM', 'nombre': 'Vietnam', 'codigo_telefono': '+84', 'continente': 'Asia'},
    {'codigo': 'MY', 'codigo_iso3': 'MYS', 'nombre': 'Malasia', 'codigo_telefono': '+60', 'continente': 'Asia'},
    {'codigo': 'SG', 'codigo_iso3': 'SGP', 'nombre': 'Singapur', 'codigo_telefono': '+65', 'continente': 'Asia'},
    {'codigo': 'IL', 'codigo_iso3': 'ISR', 'nombre': 'Israel', 'codigo_telefono': '+972', 'continente': 'Asia'},
    {'codigo': 'SA', 'codigo_iso3': 'SAU', 'nombre': 'Arabia Saudí', 'codigo_telefono': '+966', 'continente': 'Asia'},
    {'codigo': 'AE', 'codigo_iso3': 'ARE', 'nombre': 'Emiratos Árabes Unidos', 'codigo_telefono': '+971', 'continente': 'Asia'},
    {'codigo': 'IR', 'codigo_iso3': 'IRN', 'nombre': 'Irán', 'codigo_telefono': '+98', 'continente': 'Asia'},
    {'codigo': 'IQ', 'codigo_iso3': 'IRQ', 'nombre': 'Irak', 'codigo_telefono': '+964', 'continente': 'Asia'},
    # ── Oceanía ──
    {'codigo': 'AU', 'codigo_iso3': 'AUS', 'nombre': 'Australia', 'codigo_telefono': '+61', 'continente': 'Oceanía'},
    {'codigo': 'NZ', 'codigo_iso3': 'NZL', 'nombre': 'Nueva Zelanda', 'codigo_telefono': '+64', 'continente': 'Oceanía'},
    # ── Norteamérica ──
    {'codigo': 'US', 'codigo_iso3': 'USA', 'nombre': 'Estados Unidos', 'codigo_telefono': '+1', 'continente': 'América'},
    {'codigo': 'CA', 'codigo_iso3': 'CAN', 'nombre': 'Canadá', 'codigo_telefono': '+1', 'continente': 'América'},
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
                activo=True,
                fecha_creacion=datetime.utcnow(),
            )
            session.add(municipio)
            print(f"  * Municipio creado: {municipio_data['nombre']}")
        else:
            print(f"  - Municipio ya existe: {municipio_data['nombre']}")

    await session.commit()


async def inicializar_paises_adicionales(session: AsyncSession) -> int:
    """Inicializa países adicionales."""
    creados = 0
    for pais_data in PAISES_ADICIONALES:
        result = await session.execute(
            select(Pais).where(Pais.codigo == pais_data['codigo'])
        )
        pais = result.scalar_one_or_none()
        if not pais:
            pais = Pais(
                id=uuid.uuid4(),
                nombre_oficial=pais_data['nombre'],
                activo=True,
                **pais_data
            )
            session.add(pais)
            creados += 1
            print(f"  * País creado: {pais_data['nombre']}")
    await session.commit()
    return creados


async def inicializar_geografico(session: AsyncSession) -> None:
    """Inicializa datos geográficos básicos."""
    print("\n=== Inicializando Datos Geográficos ===\n")

    print("1. País España:")
    pais = await inicializar_pais_espana(session)

    print("\n2. Provincias:")
    provincias_map = await inicializar_provincias(session, pais)

    print(f"\n3. Municipios principales ({len(MUNICIPIOS_PRINCIPALES)} capitales):")
    await inicializar_municipios(session, provincias_map)

    print("\n4. Países adicionales:")
    creados = await inicializar_paises_adicionales(session)
    print(f"  {creados} países creados")

    print("\n=== Datos geográficos inicializados correctamente ===")
    print(f"Total: 1 país base, {len(PROVINCIAS_ESPANA)} provincias, {len(MUNICIPIOS_PRINCIPALES)} municipios, {creados} países adicionales\n")


# Función main para ejecutar el script directamente
async def main():
    """Función principal para ejecutar el script."""
    from ..core.database import async_session

    async with async_session() as session:
        await inicializar_geografico(session)


if __name__ == "__main__":
    asyncio.run(main())
