"""
Script para importar miembros de baja y fallecidos desde los CSVs generados.

Importa:
- miembros_baja.csv → miembros en estado BAJA
- miembros_fallecidos.csv → miembros en estado BAJA con motivo FALLECIMIENTO

Los CSVs se generaron desde las tablas MySQL:
- miembroeliminado5anios (604 registros)
- miembrosfallecidos (43 registros)
"""
import asyncio
import csv
import uuid
from pathlib import Path
from datetime import date, datetime
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

# UUIDs de catálogos (obtenidos de la base de datos)
ESTADO_BAJA_ID = uuid.UUID('d8f71531-affb-4435-b654-bed41e66dcab')
MOTIVO_FALLECIMIENTO_ID = uuid.UUID('49145bb3-fd13-40cc-85a7-d71cda16c7a6')
MOTIVO_BAJA_VOLUNTARIA_ID = uuid.UUID('185c7b6d-868c-44e9-b386-2576423ffbff')
TIPO_miembro_ID = uuid.UUID('54e92576-219d-41cb-a544-b005b2d48b34')

DATABASE_URL = 'postgresql+asyncpg://siga:siga_dev_2024@localhost:5432/siga'


def normalizar_nombre(nombre: Optional[str]) -> Optional[str]:
    """Normaliza nombres: primera letra mayúscula, resto minúsculas."""
    if not nombre:
        return None
    nombre_str = str(nombre).strip()
    if not nombre_str or nombre_str.upper() in ('NULL', 'NONE', ''):
        return None
    return nombre_str.title()


def parse_fecha(fecha_str) -> Optional[date]:
    """Parsea una fecha desde el CSV."""
    if not fecha_str:
        return None

    if isinstance(fecha_str, date):
        return fecha_str

    try:
        fecha_str_clean = str(fecha_str).strip()
        if fecha_str_clean in ('', 'NULL', '0000-00-00', 'None', 'null'):
            return None

        # Intentar varios formatos
        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y']:
            try:
                return datetime.strptime(fecha_str_clean.split(' ')[0], fmt).date()
            except ValueError:
                continue
    except (ValueError, AttributeError):
        pass

    return None


async def importar_miembros_baja(session: AsyncSession, data_dir: Path) -> int:
    """
    Importa miembros de baja desde miembros_baja.csv.

    Campos del CSV:
    CODUSER, CODPAISDOC, TIPOMIEMBRO, NUMDOCUMENTOMIEMBRO, TIPODOCUMENTOMIEMBRO,
    FECHABAJA, FECHAELIMINAR5, APE1, APE2, NOM, OBSERVACIONES, ESTADO_MIEMBRO

    NOTA: No se importa el numero_documento para evitar duplicados con miembros existentes.
    Estos registros ya están anonimizados (datos_anonimizados=true).
    """
    csv_path = data_dir / 'miembros_baja.csv'
    if not csv_path.exists():
        print(f"  [WARN] No existe {csv_path}")
        return 0

    print(f"\nImportando miembros de baja desde {csv_path}...")

    importados = 0
    omitidos = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                nombre = normalizar_nombre(row.get('NOM')) or "Sin nombre"
                apellido1 = normalizar_nombre(row.get('APE1')) or "Sin apellido"
                apellido2 = normalizar_nombre(row.get('APE2'))

                fecha_baja = parse_fecha(row.get('FECHABAJA'))
                observaciones = row.get('OBSERVACIONES', '').strip() or None

                # Tipo documento (sin número para evitar duplicados)
                tipo_documento = row.get('TIPODOCUMENTOMIEMBRO', '').strip() or None

                # Insertar miembro (sin numero_documento para evitar constraint violation)
                await session.execute(
                    text("""
                        INSERT INTO miembros (
                            id, nombre, apellido1, apellido2,
                            tipo_miembro_id, estado_id, motivo_baja_id,
                            tipo_documento,
                            fecha_baja, observaciones, activo,
                            es_voluntario, puede_conducir, vehiculo_propio, disponibilidad_viajar,
                            datos_anonimizados, fecha_creacion, eliminado
                        ) VALUES (
                            :id, :nombre, :apellido1, :apellido2,
                            :tipo_miembro_id, :estado_id, :motivo_baja_id,
                            :tipo_documento,
                            :fecha_baja, :observaciones, false,
                            false, false, false, false,
                            true, NOW(), false
                        )
                    """),
                    {
                        'id': uuid.uuid4(),
                        'nombre': nombre,
                        'apellido1': apellido1,
                        'apellido2': apellido2,
                        'tipo_miembro_id': TIPO_miembro_ID,
                        'estado_id': ESTADO_BAJA_ID,
                        'motivo_baja_id': MOTIVO_BAJA_VOLUNTARIA_ID,
                        'tipo_documento': tipo_documento,
                        'fecha_baja': fecha_baja,
                        'observaciones': observaciones,
                    }
                )
                importados += 1

                if importados % 100 == 0:
                    await session.flush()
                    print(f"  Procesados {importados} miembros de baja...")

            except Exception as e:
                omitidos += 1
                if omitidos < 5:
                    print(f"  [ERROR] {row.get('NOM', '?')}: {e}")

    await session.flush()
    print(f"  [OK] {importados} miembros de baja importados")
    if omitidos > 0:
        print(f"  [WARN] {omitidos} omitidos por errores")

    return importados


async def importar_miembros_fallecidos(session: AsyncSession, data_dir: Path) -> int:
    """
    Importa miembros fallecidos desde miembros_fallecidos.csv.

    Campos del CSV:
    CODmiembro, CODUSER, NOM, APE1, APE2, SEXO, FECHAALTA, FECHABAJA, FECHANAC,
    NOMAGRUPACION, CODAGRUPACION, NOMBREPAISDOM, NOMPROVINCIA, LOCALIDAD, CP,
    OBSERVACIONES, ESTADO_MIEMBRO, MOTIVO_BAJA
    """
    csv_path = data_dir / 'miembros_fallecidos.csv'
    if not csv_path.exists():
        print(f"  [WARN] No existe {csv_path}")
        return 0

    print(f"\nImportando miembros fallecidos desde {csv_path}...")

    # Cargar cache de agrupaciones por nombre
    result = await session.execute(
        text("SELECT id, nombre FROM organizaciones WHERE eliminado = false")
    )
    cache_agrupaciones = {row[1].lower(): row[0] for row in result}

    importados = 0
    omitidos = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                nombre = normalizar_nombre(row.get('NOM')) or "Sin nombre"
                apellido1 = normalizar_nombre(row.get('APE1')) or "Sin apellido"
                apellido2 = normalizar_nombre(row.get('APE2'))

                sexo = row.get('SEXO', '').strip().upper()
                if sexo not in ('H', 'M'):
                    sexo = None

                fecha_alta = parse_fecha(row.get('FECHAALTA'))
                fecha_baja = parse_fecha(row.get('FECHABAJA'))
                fecha_nacimiento = parse_fecha(row.get('FECHANAC'))

                localidad = row.get('LOCALIDAD', '').strip() or None
                codigo_postal = row.get('CP', '').strip() or None
                observaciones = row.get('OBSERVACIONES', '').strip() or None

                # Buscar agrupación por nombre
                agrupacion_nombre = row.get('NOMAGRUPACION', '').strip().lower()
                agrupacion_id = cache_agrupaciones.get(agrupacion_nombre)

                # Insertar miembro
                await session.execute(
                    text("""
                        INSERT INTO miembros (
                            id, nombre, apellido1, apellido2, sexo,
                            fecha_nacimiento, tipo_miembro_id, estado_id, motivo_baja_id,
                            localidad, codigo_postal, agrupacion_id,
                            fecha_alta, fecha_baja, observaciones, activo,
                            es_voluntario, puede_conducir, vehiculo_propio, disponibilidad_viajar,
                            fecha_creacion, eliminado
                        ) VALUES (
                            :id, :nombre, :apellido1, :apellido2, :sexo,
                            :fecha_nacimiento, :tipo_miembro_id, :estado_id, :motivo_baja_id,
                            :localidad, :codigo_postal, :agrupacion_id,
                            :fecha_alta, :fecha_baja, :observaciones, false,
                            false, false, false, false,
                            NOW(), false
                        )
                    """),
                    {
                        'id': uuid.uuid4(),
                        'nombre': nombre,
                        'apellido1': apellido1,
                        'apellido2': apellido2,
                        'sexo': sexo,
                        'fecha_nacimiento': fecha_nacimiento,
                        'tipo_miembro_id': TIPO_miembro_ID,
                        'estado_id': ESTADO_BAJA_ID,
                        'motivo_baja_id': MOTIVO_FALLECIMIENTO_ID,
                        'localidad': localidad,
                        'codigo_postal': codigo_postal,
                        'agrupacion_id': agrupacion_id,
                        'fecha_alta': fecha_alta,
                        'fecha_baja': fecha_baja,
                        'observaciones': observaciones,
                    }
                )
                importados += 1

            except Exception as e:
                omitidos += 1
                if omitidos < 5:
                    print(f"  [ERROR] {row.get('NOM', '?')}: {e}")

    await session.flush()
    print(f"  [OK] {importados} miembros fallecidos importados")
    if omitidos > 0:
        print(f"  [WARN] {omitidos} omitidos por errores")

    return importados


async def main():
    """Función principal."""
    print("\n" + "="*80)
    print("IMPORTACIÓN DE MIEMBROS DE BAJA Y FALLECIDOS")
    print("="*80)

    # Directorio de datos
    data_dir = Path(__file__).parent / 'data'

    # Conectar a PostgreSQL
    print("\nConectando a PostgreSQL...")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Importar miembros de baja
            bajas = await importar_miembros_baja(session, data_dir)

            # Importar miembros fallecidos
            fallecidos = await importar_miembros_fallecidos(session, data_dir)

            # Commit
            await session.commit()

            print("\n" + "="*80)
            print("[OK] IMPORTACIÓN COMPLETADA")
            print("="*80)
            print(f"\nResumen:")
            print(f"  - Miembros de baja: {bajas}")
            print(f"  - Miembros fallecidos: {fallecidos}")
            print(f"  - Total: {bajas + fallecidos}")

        except Exception as e:
            await session.rollback()
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
