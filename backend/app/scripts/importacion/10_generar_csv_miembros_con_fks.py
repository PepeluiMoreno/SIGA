"""
Script para generar miembros_import.csv con todas las FKs incrustadas.

Este CSV está listo para cargarse con COPY en PostgreSQL.
"""
import asyncio
import csv
import uuid
from pathlib import Path
from datetime import date, datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = 'postgresql+asyncpg://siga:siga_dev_2024@localhost:5432/siga'

# UUIDs constantes de catálogos
ESTADO_ACTIVO_ID = 'e1e721ff-47cf-457d-9075-3d26585bbb60'
ESTADO_BAJA_ID = 'd8f71531-affb-4435-b654-bed41e66dcab'
MOTIVO_BAJA_VOLUNTARIA_ID = '185c7b6d-868c-44e9-b386-2576423ffbff'
MOTIVO_FALLECIMIENTO_ID = '49145bb3-fd13-40cc-85a7-d71cda16c7a6'
TIPO_miembro_ID = '54e92576-219d-41cb-a544-b005b2d48b34'
TIPO_SIMPATIZANTE_ID = '037696ee-2648-4c67-8e59-55f7f9f40e30'


def normalizar_nombre(nombre):
    """Normaliza nombres: primera letra mayúscula."""
    if not nombre:
        return None
    nombre_str = str(nombre).strip()
    if not nombre_str or nombre_str.upper() in ('NULL', 'NONE', ''):
        return None
    return nombre_str.title()


def parse_fecha(fecha_str):
    """Parsea fecha a formato ISO."""
    if not fecha_str:
        return None
    if isinstance(fecha_str, (date, datetime)):
        if hasattr(fecha_str, 'date'):
            fecha_str = fecha_str.date()
        if fecha_str.year < 1900:
            return None
        return fecha_str.isoformat()
    try:
        fecha_str_clean = str(fecha_str).strip()
        if fecha_str_clean in ('', 'NULL', '0000-00-00', 'None', 'null'):
            return None
        dt = datetime.strptime(fecha_str_clean.split(' ')[0], '%Y-%m-%d')
        if dt.year < 1900:
            return None
        return dt.date().isoformat()
    except:
        return None


async def cargar_mapeos(session):
    """Carga los mapeos de IDs antiguos a UUIDs."""
    mapeos = {}

    # Agrupaciones
    result = await session.execute(text(
        "SELECT old_id, new_uuid FROM temp_id_mapping WHERE tabla = 'AGRUPACION'"
    ))
    mapeos['agrupaciones'] = {str(row[0]): str(row[1]) for row in result}

    # Provincias
    result = await session.execute(text(
        "SELECT old_id, new_uuid FROM temp_id_mapping WHERE tabla = 'PROVINCIA'"
    ))
    mapeos['provincias'] = {str(row[0]): str(row[1]) for row in result}

    # Paises
    result = await session.execute(text(
        "SELECT old_id, new_uuid FROM temp_id_mapping WHERE tabla = 'PAIS'"
    ))
    mapeos['paises'] = {str(row[0]): str(row[1]) for row in result}

    return mapeos


async def main():
    """Función principal."""
    data_dir = Path(__file__).parent / 'data'

    print("\n" + "="*70)
    print("GENERACIÓN DE CSV DE MIEMBROS CON FKs")
    print("="*70)

    # Conectar a PostgreSQL para obtener mapeos
    print("\nConectando a PostgreSQL...")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        mapeos = await cargar_mapeos(session)
        print(f"  Agrupaciones: {len(mapeos['agrupaciones'])}")
        print(f"  Provincias: {len(mapeos['provincias'])}")
        print(f"  Paises: {len(mapeos['paises'])}")

    await engine.dispose()

    # Cargar CSVs fuente
    print("\nCargando CSVs fuente...")

    miembros = {}
    with open(data_dir / 'miembros.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            miembros[row['CODUSER']] = row
    print(f"  miembros.csv: {len(miembros)} registros")

    # Cargar bajas con sus observaciones Y datos de nombre
    bajas = {}  # coduser -> {observaciones, nom, ape1, ape2}
    with open(data_dir / 'miembros_baja.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bajas[row['CODUSER']] = {
                'observaciones': row.get('OBSERVACIONES', '').strip(),
                'NOM': row.get('NOM', '').strip(),
                'APE1': row.get('APE1', '').strip(),
                'APE2': row.get('APE2', '').strip(),
            }
    print(f"  miembros_baja.csv: {len(bajas)} registros")

    # Cargar fallecidos con sus observaciones Y datos de nombre
    fallecidos = {}  # coduser -> {observaciones, nom, ape1, ape2}
    with open(data_dir / 'miembros_fallecidos.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fallecidos[row['CODUSER']] = {
                'observaciones': row.get('OBSERVACIONES', '').strip(),
                'NOM': row.get('NOM', '').strip(),
                'APE1': row.get('APE1', '').strip(),
                'APE2': row.get('APE2', '').strip(),
            }
    print(f"  miembros_fallecidos.csv: {len(fallecidos)} registros")

    # Completar datos de miembros con info de bajas/fallecidos
    completados = 0
    for coduser, m in miembros.items():
        nom = m.get('NOM', '').strip()
        ape1 = m.get('APE1', '').strip()

        # Si falta nombre o apellido, buscar en bajas/fallecidos
        if not nom or not ape1 or nom.upper() in ('NULL', 'NONE') or ape1.upper() in ('NULL', 'NONE'):
            # Prioridad: fallecidos > bajas
            fuente = fallecidos.get(coduser) or bajas.get(coduser)
            if fuente:
                if fuente['NOM'] and fuente['NOM'].upper() not in ('NULL', 'NONE'):
                    m['NOM'] = fuente['NOM']
                if fuente['APE1'] and fuente['APE1'].upper() not in ('NULL', 'NONE'):
                    m['APE1'] = fuente['APE1']
                if fuente['APE2'] and fuente['APE2'].upper() not in ('NULL', 'NONE'):
                    m['APE2'] = fuente['APE2']
                completados += 1

    if completados:
        print(f"  [INFO] Completados {completados} registros con datos de bajas/fallecidos")

    # Detectar fallecidos adicionales en bajas por texto de observaciones
    palabras_fallecimiento = ['fallec', 'murió', 'murio', 'muerte', 'defunc']
    fallecidos_detectados = set()
    for coduser, data in bajas.items():
        obs = data.get('observaciones', '')
        if obs:
            obs_lower = obs.lower()
            if any(palabra in obs_lower for palabra in palabras_fallecimiento):
                if coduser not in fallecidos:
                    fallecidos_detectados.add(coduser)
                    fallecidos[coduser] = data  # Añadir como fallecido con todos sus datos
    if fallecidos_detectados:
        print(f"  [INFO] Detectados {len(fallecidos_detectados)} fallecidos adicionales por observaciones")

    # Campos de salida (orden de columnas en tabla miembros)
    output_fields = [
        'id', 'nombre', 'apellido1', 'apellido2', 'sexo', 'fecha_nacimiento',
        'tipo_miembro_id', 'estado_id', 'motivo_baja_id',
        'tipo_documento', 'numero_documento', 'pais_documento_id',
        'direccion', 'codigo_postal', 'localidad', 'provincia_id', 'pais_domicilio_id',
        'telefono', 'telefono2', 'email', 'agrupacion_id', 'iban',
        'fecha_alta', 'fecha_baja', 'observaciones', 'activo',
        'es_voluntario', 'profesion', 'nivel_estudios', 'intereses',
        'puede_conducir', 'vehiculo_propio', 'disponibilidad_viajar',
        'datos_anonimizados', 'fecha_creacion', 'eliminado'
    ]

    # Generar CSV
    print("\nGenerando miembros_import.csv...")

    stats = {'ACTIVO': 0, 'BAJA': 0, 'FALLECIDO': 0}
    ahora = datetime.now().isoformat()

    with open(data_dir / 'miembros_import.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()

        for coduser, m in miembros.items():
            # Determinar estado y motivo de baja
            obs_extra = ''  # Observaciones adicionales de bajas/fallecidos
            if coduser in fallecidos:
                estado_id = ESTADO_BAJA_ID
                motivo_baja_id = MOTIVO_FALLECIMIENTO_ID
                obs_extra = fallecidos[coduser].get('observaciones', '')
                stats['FALLECIDO'] += 1
            elif coduser in bajas:
                estado_id = ESTADO_BAJA_ID
                motivo_baja_id = MOTIVO_BAJA_VOLUNTARIA_ID
                obs_extra = bajas[coduser].get('observaciones', '')
                stats['BAJA'] += 1
            else:
                estado_id = ESTADO_ACTIVO_ID
                motivo_baja_id = ''
                stats['ACTIVO'] += 1

            # Mapear tipo de miembro
            tipo_mysql = str(m.get('TIPOMIEMBRO', '')).lower()
            if 'simpatizante' in tipo_mysql:
                tipo_miembro_id = TIPO_SIMPATIZANTE_ID
            else:
                tipo_miembro_id = TIPO_miembro_ID

            # Procesar teléfonos (prioridad: móvil > casa > trabajo)
            telefonos = []
            for tel in [m.get('TELMOVIL'), m.get('TELFIJOCASA'), m.get('TELFIJOTRABAJO')]:
                if tel and str(tel).strip() and str(tel).strip().upper() != 'NULL':
                    telefonos.append(str(tel).strip()[:20])

            # Mapear FKs usando mapeos
            agrupacion_id = mapeos['agrupaciones'].get(str(m.get('CODAGRUPACION', '')).strip(), '')
            provincia_id = mapeos['provincias'].get(str(m.get('CODPROV', '')).strip(), '')
            pais_doc_id = mapeos['paises'].get(str(m.get('CODPAISDOC', '')).strip(), '')
            pais_dom_id = mapeos['paises'].get(str(m.get('CODPAISDOM', '')).strip(), '')

            # Determinar es_voluntario (campo COLABORA)
            colabora = m.get('COLABORA', '')
            es_voluntario = bool(colabora and str(colabora).strip() and
                                str(colabora).strip().upper() not in ('NULL', 'NO', ''))

            # Combinar observaciones (incluir las de bajas/fallecidos)
            obs = []
            if m.get('COMENTARIOmiembro') and str(m['COMENTARIOmiembro']).strip():
                obs.append(str(m['COMENTARIOmiembro']).strip())
            if m.get('OBSERVACIONES') and str(m['OBSERVACIONES']).strip():
                obs.append(str(m['OBSERVACIONES']).strip())
            if obs_extra:
                obs.append(f"[BAJA] {obs_extra}")
            observaciones = ' | '.join(obs) if obs else ''

            # Escribir fila
            row_out = {
                'id': str(uuid.uuid4()),
                'nombre': normalizar_nombre(m.get('NOM')) or 'Sin nombre',
                'apellido1': normalizar_nombre(m.get('APE1')) or 'Sin apellido',
                'apellido2': normalizar_nombre(m.get('APE2')) or '',
                'sexo': m.get('SEXO', '').strip().upper() if m.get('SEXO', '').strip().upper() in ('H', 'M') else '',
                'fecha_nacimiento': parse_fecha(m.get('FECHANAC')) or '',
                'tipo_miembro_id': tipo_miembro_id,
                'estado_id': estado_id,
                'motivo_baja_id': motivo_baja_id,
                'tipo_documento': m.get('TIPODOCUMENTOMIEMBRO', '').strip() or '',
                'numero_documento': m.get('NUMDOCUMENTOMIEMBRO', '').strip() or '',
                'pais_documento_id': pais_doc_id,
                'direccion': m.get('DIRECCION', '').strip() or '',
                'codigo_postal': m.get('CP', '').strip() or '',
                'localidad': m.get('LOCALIDAD', '').strip() or '',
                'provincia_id': provincia_id,
                'pais_domicilio_id': pais_dom_id,
                'telefono': telefonos[0] if telefonos else '',
                'telefono2': telefonos[1] if len(telefonos) > 1 else '',
                'email': m.get('EMAIL', '').strip() or '',
                'agrupacion_id': agrupacion_id,
                'iban': m.get('CUENTAIBAN', '').strip() or '',
                'fecha_alta': parse_fecha(m.get('FECHAALTA')) or '',
                'fecha_baja': parse_fecha(m.get('FECHABAJA')) or '',
                'observaciones': observaciones,
                'activo': 'true' if estado_id == ESTADO_ACTIVO_ID else 'false',
                'es_voluntario': 'true' if es_voluntario else 'false',
                'profesion': m.get('PROFESION', '').strip() if es_voluntario else '',
                'nivel_estudios': m.get('ESTUDIOS', '').strip() if es_voluntario else '',
                'intereses': str(colabora).strip() if es_voluntario and colabora else '',
                'puede_conducir': 'false',
                'vehiculo_propio': 'false',
                'disponibilidad_viajar': 'false',
                'datos_anonimizados': 'false',
                'fecha_creacion': ahora,
                'eliminado': 'false'
            }
            writer.writerow(row_out)

    print(f"  [OK] {len(miembros)} registros exportados")

    print("\n" + "="*70)
    print("ESTADÍSTICAS")
    print("="*70)
    print(f"  ACTIVOS:              {stats['ACTIVO']:>5}")
    print(f"  BAJAS (voluntarias):  {stats['BAJA']:>5}")
    print(f"  BAJAS (fallecidos):   {stats['FALLECIDO']:>5}")
    print(f"  ---------------------------------")
    print(f"  TOTAL:                {sum(stats.values()):>5}")

    print("\n[OK] CSV generado: miembros_import.csv")
    print("     Listo para cargar con COPY en PostgreSQL")


if __name__ == "__main__":
    asyncio.run(main())
