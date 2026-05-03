"""
Script para importar datos geográficos desde MySQL.

Importa las tablas:
- PAIS → paises
- PROVINCIA → provincias

Este script debe ejecutarse DESPUÉS de crear los catálogos base.
"""
import asyncio
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url
from app.modules.core.geografico.direccion import Pais, Provincia
from .mysql_helper import get_mysql_connection


class MapeadorGeografico:
    """Mapea datos geográficos de MySQL a PostgreSQL."""

    def __init__(self):
        self.mapeo_paises: dict[int, uuid.UUID] = {}
        self.mapeo_paises_codigo: dict[str, uuid.UUID] = {}  # Por código ISO alpha-2
        self.mapeo_provincias: dict[int, uuid.UUID] = {}

    async def importar_paises(self, session: AsyncSession) -> dict[int, uuid.UUID]:
        """Importa países desde MySQL."""
        print("\nImportando países desde MySQL...")

        paises_importados = 0
        paises_existentes = 0

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT CODPAIS1, CODPAIS2, CODPAIS3, NOMBREPAIS, SEPA
                    FROM pais
                    ORDER BY CODPAIS3
                """)
                rows = await cursor.fetchall()

                for row in rows:
                    # CODPAIS1 = ISO Alpha-2 (ES)
                    # CODPAIS2 = ISO Alpha-3 (ESP)
                    # CODPAIS3 = ISO Numeric (724)
                    # NOMBREPAIS = Nombre
                    # SEPA = Si es zona SEPA
                    codigo_iso_alpha2 = str(row[0]).strip() if row[0] else None
                    codigo_iso_alpha3 = str(row[1]).strip() if row[1] else "XXX"
                    codigo_iso_numerico = int(row[2]) if row[2] else 0
                    nombre = str(row[3]).strip() if row[3] else f"País {codigo_iso_numerico}"

                    # Validar código ISO alpha-2
                    if not codigo_iso_alpha2 or len(codigo_iso_alpha2) != 2:
                        continue

                    # Verificar si ya existe
                    result = await session.execute(
                        select(Pais).where(Pais.codigo == codigo_iso_alpha2)
                    )
                    pais_existente = result.scalar_one_or_none()

                    if pais_existente:
                        self.mapeo_paises[codigo_iso_numerico] = pais_existente.id
                        self.mapeo_paises_codigo[codigo_iso_alpha2] = pais_existente.id
                        paises_existentes += 1
                        continue

                    # Crear nuevo país
                    pais = Pais(
                        codigo=codigo_iso_alpha2,
                        codigo_iso3=codigo_iso_alpha3[:3],
                        nombre=nombre,
                        activo=True
                    )

                    session.add(pais)
                    await session.flush()

                    self.mapeo_paises[codigo_iso_numerico] = pais.id
                    self.mapeo_paises_codigo[codigo_iso_alpha2] = pais.id
                    paises_importados += 1

                    if paises_importados % 50 == 0:
                        print(f"  Procesados {paises_importados} países...")

        print(f"  [OK] {paises_importados} países importados")
        print(f"  [OK] {paises_existentes} países ya existían")

        return self.mapeo_paises

    async def importar_provincias(self, session: AsyncSession) -> dict[int, uuid.UUID]:
        """Importa provincias desde MySQL."""
        print("\nImportando provincias desde MySQL...")

        provincias_importadas = 0
        provincias_existentes = 0

        # Obtener España (todas las provincias son españolas)
        result = await session.execute(
            select(Pais).where(Pais.codigo == 'ES')
        )
        pais_espana = result.scalar_one_or_none()

        if not pais_espana:
            print("  [ERROR] No se encontró España en la base de datos")
            return self.mapeo_provincias

        pais_id = pais_espana.id

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT CODPROV, CCAA, NOMPROVINCIA
                    FROM provincia
                    ORDER BY CODPROV
                """)
                rows = await cursor.fetchall()

                for row in rows:
                    codprov = int(row[0]) if row[0] else 0
                    nombre = str(row[2]).strip() if row[2] else f"Provincia {codprov}"
                    codigo = str(codprov).zfill(2)  # Código de 2 dígitos

                    # Verificar si ya existe
                    result = await session.execute(
                        select(Provincia).where(
                            Provincia.codigo == codigo,
                            Provincia.pais_id == pais_id
                        )
                    )
                    provincia_existente = result.scalar_one_or_none()

                    if provincia_existente:
                        self.mapeo_provincias[codprov] = provincia_existente.id
                        provincias_existentes += 1
                        continue

                    # Crear nueva provincia
                    provincia = Provincia(
                        nombre=nombre,
                        pais_id=pais_id,
                        codigo=codigo,
                        activo=True
                    )

                    session.add(provincia)
                    await session.flush()

                    self.mapeo_provincias[codprov] = provincia.id
                    provincias_importadas += 1

        print(f"  [OK] {provincias_importadas} provincias importadas")
        print(f"  [OK] {provincias_existentes} provincias ya existían")

        return self.mapeo_provincias


async def guardar_mapeo_temporal(session: AsyncSession, mapeo_paises: dict, mapeo_provincias: dict):
    """Guarda el mapeo de IDs en una tabla temporal."""
    print("\nGuardando mapeos en temp_id_mapping...")

    # Crear tabla temporal si no existe
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS temp_id_mapping (
            tabla VARCHAR(50),
            old_id INTEGER,
            new_uuid UUID,
            PRIMARY KEY (tabla, old_id)
        )
    """))

    # Insertar mapeos de países
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

    print(f"  [OK] {len(mapeo_paises)} países + {len(mapeo_provincias)} provincias mapeados")


async def main():
    """Función principal."""
    print("\n" + "="*80)
    print("IMPORTACIÓN DE DATOS GEOGRÁFICOS DESDE MYSQL")
    print("="*80 + "\n")

    # Conectar a PostgreSQL
    print("Conectando a PostgreSQL...")
    database_url = get_database_url()
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"server_settings": {"jit": "off"}, "statement_cache_size": 0}
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            mapeador = MapeadorGeografico()

            # Importar países
            mapeo_paises = await mapeador.importar_paises(session)

            # Importar provincias
            mapeo_provincias = await mapeador.importar_provincias(session)

            # Guardar mapeos
            await guardar_mapeo_temporal(session, mapeo_paises, mapeo_provincias)

            # Commit
            await session.commit()

            print("\n" + "="*80)
            print("[OK] IMPORTACIÓN COMPLETADA")
            print("="*80)
            print(f"\nPaíses: {len(mapeo_paises)} mapeados")
            print(f"Provincias: {len(mapeo_provincias)} mapeadas")

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
