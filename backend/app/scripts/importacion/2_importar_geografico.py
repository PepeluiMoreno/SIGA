"""
Script para importar datos geograficos desde el dump SQL.

Importa las tablas:
- PAIS -> paises
- PROVINCIA -> provincias

Este script debe ejecutarse DESPUES de crear los catalogos base.
"""
import asyncio
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import get_database_url
from app.domains.geografico.models.direccion import Pais, Provincia
from app.scripts.importacion.sql_dump_parser import SQLDumpParser
from sqlalchemy import text


# Ruta al archivo dump SQL
DUMP_FILE_PATH = r"C:\Users\Jose\dev\AIEL\data\europalaica_com_2026_01_01 apertura de año.sql"


class MapeadorGeografico:
    """Mapea datos geograficos de MySQL a PostgreSQL."""

    def __init__(self):
        self.mapeo_paises: dict[int, uuid.UUID] = {}
        self.mapeo_provincias: dict[int, uuid.UUID] = {}

    async def importar_paises(self, session: AsyncSession, parser: SQLDumpParser) -> dict[int, uuid.UUID]:
        """Importa paises desde el dump SQL."""

        print("\nImportando paises...")

        paises_importados = 0
        paises_existentes = 0

        for row in parser.extraer_inserts('PAIS'):
            # Estructura de PAIS: (CODPAIS1, CODPAIS2, CODPAIS3, NOMBREPAIS, SEPA)
            # CODPAIS1 = ISO Alpha-2
            # CODPAIS2 = ISO Alpha-3
            # CODPAIS3 = ISO Numeric
            # NOMBREPAIS = Name
            codigo_iso_alpha2 = row[0]  # 'AD'
            codigo_iso_alpha3 = row[1]  # 'AND'
            codigo_iso_numerico = row[2]  # 20
            nombre = row[3]  # 'Andorra'
            sepa = row[4] if len(row) > 4 else None  # 'SI'

            # Usar el codigo numerico como ID para mapeo
            codpais = codigo_iso_numerico

            # Verificar si ya existe por codigo ISO alpha-2
            codigo = str(codigo_iso_alpha2).strip() if codigo_iso_alpha2 else None

            if codigo and len(codigo) == 2:  # Solo codigo ISO valido de 2 caracteres
                result = await session.execute(
                    select(Pais).where(Pais.codigo == codigo)
                )
                pais_existente = result.scalar_one_or_none()

                if pais_existente:
                    self.mapeo_paises[codpais] = pais_existente.id
                    paises_existentes += 1
                    continue

            # Crear nuevo pais
            codigo_iso3 = str(codigo_iso_alpha3).strip() if codigo_iso_alpha3 else "XXX"

            pais = Pais(
                codigo=codigo,  # ISO Alpha-2 (2 chars)
                codigo_iso3=codigo_iso3,  # ISO Alpha-3 (3 chars) - required field
                nombre=nombre.strip() if nombre else f"Pais {codpais}",
                activo=True
            )

            session.add(pais)
            self.mapeo_paises[codpais] = pais.id
            paises_importados += 1

            if paises_importados % 50 == 0:
                await session.flush()  # Flush every 50 records
                print(f"  Procesados {paises_importados} paises...")

        print(f"  [OK] {paises_importados} paises importados")
        print(f"  [OK] {paises_existentes} paises ya existian")

        return self.mapeo_paises

    async def importar_provincias(self, session: AsyncSession, parser: SQLDumpParser) -> dict[int, uuid.UUID]:
        """Importa provincias desde el dump SQL."""

        print("\nImportando provincias...")

        provincias_importadas = 0
        provincias_sin_pais = 0

        for row in parser.extraer_inserts('PROVINCIA'):
            # Estructura de PROVINCIA: (CODPROV, CCAA, NOMPROVINCIA)
            if len(row) < 3:
                print(f"  [WARN] Fila de provincia invalida (longitud {len(row)}): {row}")
                continue

            codprov = row[0]  # int - province code
            ccaa = row[1]  # int - autonomous community (ignored for now)
            nombre = row[2]  # str - province name

            # Spanish provinces don't have CODPAIS in this table, always Spain
            codpais = None  # Will default to Spain

            # Buscar pais relacionado
            pais_id = None
            if codpais and codpais in self.mapeo_paises:
                pais_id = self.mapeo_paises[codpais]
            else:
                # Intentar buscar España por defecto (codigo ISO ES)
                result = await session.execute(
                    select(Pais).where(Pais.codigo == 'ES')
                )
                pais_espana = result.scalar_one_or_none()
                if pais_espana:
                    pais_id = pais_espana.id
                else:
                    print(f"  [WARN] Provincia '{nombre}' sin pais valido, se omite")
                    provincias_sin_pais += 1
                    continue

            # Verificar si ya existe por codigo (mas confiable que por nombre)
            result = await session.execute(
                select(Provincia).where(
                    Provincia.codigo == str(codprov).zfill(2),
                    Provincia.pais_id == pais_id
                )
            )
            provincia_existente = result.scalar_one_or_none()

            if provincia_existente:
                self.mapeo_provincias[codprov] = provincia_existente.id
                continue

            # Crear nueva provincia
            provincia = Provincia(
                nombre=str(nombre).strip() if nombre else f"Provincia {codprov}",
                pais_id=pais_id,
                codigo=str(codprov).zfill(2),  # Codigo de 2 digitos con padding
                activo=True
            )

            session.add(provincia)
            self.mapeo_provincias[codprov] = provincia.id
            provincias_importadas += 1

            if provincias_importadas % 50 == 0:
                await session.flush()  # Flush every 50 records

        print(f"  [OK] {provincias_importadas} provincias importadas")
        if provincias_sin_pais > 0:
            print(f"  [WARN] {provincias_sin_pais} provincias omitidas (sin pais valido)")

        return self.mapeo_provincias


async def guardar_mapeo_temporal(session: AsyncSession, mapeo_paises: dict, mapeo_provincias: dict):
    """Guarda el mapeo de IDs en una tabla temporal."""

    print("\nCreando tabla temporal de mapeo...")

    # Crear tabla temporal si no existe
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS temp_id_mapping (
            tabla VARCHAR(50),
            old_id INTEGER,
            new_uuid UUID,
            PRIMARY KEY (tabla, old_id)
        )
    """))

    # Insertar mapeos de paises
    for old_id, new_uuid in mapeo_paises.items():
        await session.execute(
            text("""
            INSERT INTO temp_id_mapping (tabla, old_id, new_uuid)
            VALUES ('PAIS', :old_id, :new_uuid)
            ON CONFLICT (tabla, old_id) DO UPDATE SET new_uuid = EXCLUDED.new_uuid
            """),
            {"old_id": old_id, "new_uuid": new_uuid}
        )

    # Insertar mapeos de provincias
    for old_id, new_uuid in mapeo_provincias.items():
        await session.execute(
            text("""
            INSERT INTO temp_id_mapping (tabla, old_id, new_uuid)
            VALUES ('PROVINCIA', :old_id, :new_uuid)
            ON CONFLICT (tabla, old_id) DO UPDATE SET new_uuid = EXCLUDED.new_uuid
            """),
            {"old_id": old_id, "new_uuid": new_uuid}
        )

    print("  [OK] Mapeos guardados en temp_id_mapping")


async def main():
    """Funcion principal."""

    print("\n" + "="*80)
    print("IMPORTACION DE DATOS GEOGRAFICOS")
    print("="*80 + "\n")

    # Crear parser del dump SQL
    print("Cargando dump SQL...")
    try:
        parser = SQLDumpParser(DUMP_FILE_PATH)
        print(f"  [OK] Dump cargado: {DUMP_FILE_PATH}")
    except FileNotFoundError as e:
        print(f"  [ERROR] Archivo dump no encontrado: {e}")
        print("\n  Ajusta DUMP_FILE_PATH en el script con la ruta correcta.")
        return

    # Conectar a PostgreSQL
    print("\nConectando a PostgreSQL...")
    database_url = get_database_url()
    # Disable prepared statement cache to avoid pgbouncer issues
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"statement_cache_size": 0}
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            mapeador = MapeadorGeografico()

            # Importar paises
            mapeo_paises = await mapeador.importar_paises(session, parser)

            # Importar provincias
            mapeo_provincias = await mapeador.importar_provincias(session, parser)

            # Guardar mapeos
            await guardar_mapeo_temporal(session, mapeo_paises, mapeo_provincias)

            # Commit
            await session.commit()

            print("\n" + "="*80)
            print("[OK] IMPORTACION COMPLETADA")
            print("="*80)
            print(f"\nPaises: {len(mapeo_paises)} mapeados")
            print(f"Provincias: {len(mapeo_provincias)} mapeadas")
            print(f"\nMapeos guardados en: temp_id_mapping")

        except Exception as e:
            await session.rollback()
            print(f"\n[ERROR]: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
