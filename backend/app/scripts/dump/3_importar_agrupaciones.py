"""
Script para importar agrupaciones territoriales desde MySQL.

Importa la tabla:
- AGRUPACIONTERRITORIAL → agrupaciones_territoriales

Este script debe ejecutarse DESPUÉS de importar datos geográficos.
"""
import asyncio
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url
from app.modules.organizaciones.models.agrupacion_territorial import AgrupacionTerritorial
from app.modules.geografico.models.direccion import Pais, Provincia
from .mysql_helper import get_mysql_connection


class MapeadorAgrupaciones:
    """Mapea agrupaciones de MySQL a PostgreSQL."""

    def __init__(self):
        self.mapeo_agrupaciones: dict[str, uuid.UUID] = {}  # CODAGRUPACION → UUID
        self.cache_provincias: dict[str, uuid.UUID] = {}  # código CP → UUID provincia
        self.cache_paises: dict[str, uuid.UUID] = {}  # código ISO → UUID país

    async def cargar_cache_provincias(self, session: AsyncSession):
        """Carga cache de provincias por código."""
        print("\nCargando cache de provincias...")

        result = await session.execute(select(Provincia))
        provincias = result.scalars().all()

        for provincia in provincias:
            self.cache_provincias[provincia.codigo] = provincia.id

        print(f"  [OK] {len(self.cache_provincias)} provincias en cache")

    async def cargar_cache_paises(self, session: AsyncSession):
        """Carga cache de países por código ISO."""
        print("\nCargando cache de países...")

        result = await session.execute(select(Pais))
        paises = result.scalars().all()

        for pais in paises:
            self.cache_paises[pais.codigo] = pais.id

        print(f"  [OK] {len(self.cache_paises)} países en cache")

    def inferir_provincia_desde_cp(self, codigo_postal: Optional[str]) -> Optional[uuid.UUID]:
        """Infiere la provincia desde el código postal."""
        if not codigo_postal:
            return None

        cp = str(codigo_postal).strip()
        if len(cp) >= 2:
            codigo_provincia = cp[:2]
            return self.cache_provincias.get(codigo_provincia)

        return None

    def mapear_tipo_agrupacion(self, ambito: Optional[str]) -> str:
        """Mapea el ámbito de MySQL a tipo de agrupación."""
        if not ambito:
            return "LOCAL"

        ambito_lower = ambito.lower().strip()

        if "estatal" in ambito_lower or "internacional" in ambito_lower:
            return "ESTATAL"
        elif "regional" in ambito_lower or "autonomic" in ambito_lower:
            return "REGIONAL"
        elif "provincial" in ambito_lower:
            return "PROVINCIAL"
        else:
            return "LOCAL"

    async def importar_agrupaciones(self, session: AsyncSession):
        """Importa agrupaciones desde MySQL."""
        print("\nImportando agrupaciones desde MySQL...")

        importadas = 0
        existentes = 0

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT
                        CODAGRUPACION, NOMAGRUPACION, CIF, GESTIONCUOTAS,
                        EMAIL, EMAILCOORD, WEB, TELFIJOTRABAJO, TELMOV,
                        AMBITO, ESTADO, CODPAISDOM, DIRECCION, CP, LOCALIDAD,
                        OBSERVACIONES
                    FROM agrupacionterritorial
                    ORDER BY CODAGRUPACION
                """)
                rows = await cursor.fetchall()

                for row in rows:
                    codigo = str(row[0]).strip() if row[0] else None
                    nombre = str(row[1]).strip() if row[1] else f"Agrupación {codigo}"
                    cif = str(row[2]).strip() if row[2] else None
                    email = str(row[4]).strip() if row[4] else None
                    web = str(row[6]).strip() if row[6] else None
                    telefono = str(row[7]).strip() if row[7] else None
                    telefono_movil = str(row[8]).strip() if row[8] else None
                    ambito = str(row[9]).strip() if row[9] else None
                    estado = str(row[10]).strip().lower() if row[10] else "activa"
                    codigo_pais = str(row[11]).strip() if row[11] else None
                    direccion = str(row[12]).strip() if row[12] else None
                    codigo_postal = str(row[13]).strip() if row[13] else None
                    localidad = str(row[14]).strip() if row[14] else None
                    observaciones = str(row[15]).strip() if row[15] else None

                    if not codigo:
                        continue

                    # Verificar si ya existe
                    result = await session.execute(
                        select(AgrupacionTerritorial).where(
                            AgrupacionTerritorial.codigo == codigo
                        )
                    )
                    existente = result.scalar_one_or_none()

                    if existente:
                        self.mapeo_agrupaciones[codigo] = existente.id
                        existentes += 1
                        continue

                    # Inferir provincia desde CP
                    provincia_id = self.inferir_provincia_desde_cp(codigo_postal)

                    # Obtener país
                    pais_id = None
                    if codigo_pais and codigo_pais != "--" and len(codigo_pais) == 2:
                        pais_id = self.cache_paises.get(codigo_pais)
                    if not pais_id:
                        # Default a España
                        pais_id = self.cache_paises.get("ES")

                    # Mapear tipo
                    tipo = self.mapear_tipo_agrupacion(ambito)

                    # Estado activo
                    activo = estado == "activa"

                    # Crear agrupación
                    agrupacion = AgrupacionTerritorial(
                        codigo=codigo,
                        nombre=nombre,
                        tipo=tipo,
                        cif=cif,
                        email=email,
                        web=web,
                        telefono=telefono or telefono_movil,
                        provincia_id=provincia_id,
                        pais_id=pais_id,
                        direccion=direccion,
                        codigo_postal=codigo_postal,
                        localidad=localidad,
                        observaciones=observaciones,
                        activo=activo
                    )

                    session.add(agrupacion)
                    await session.flush()

                    self.mapeo_agrupaciones[codigo] = agrupacion.id
                    importadas += 1

        print(f"  [OK] {importadas} agrupaciones importadas")
        print(f"  [OK] {existentes} agrupaciones ya existían")

    async def guardar_mapeo_temporal(self, session: AsyncSession):
        """Guarda el mapeo de IDs en temp_id_mapping."""
        print("\nGuardando mapeos de agrupaciones...")

        for codigo, uuid_val in self.mapeo_agrupaciones.items():
            # Usar el código como string para old_id (convertir a int si es numérico)
            try:
                old_id = int(codigo)
            except ValueError:
                # Si no es numérico, usar hash
                old_id = hash(codigo) % (10**9)

            await session.execute(
                text("""
                    INSERT INTO temp_id_mapping (tabla, old_id, new_uuid)
                    VALUES ('AGRUPACION', :old_id, :new_uuid)
                    ON CONFLICT (tabla, old_id) DO UPDATE SET new_uuid = EXCLUDED.new_uuid
                """),
                {"old_id": old_id, "new_uuid": uuid_val}
            )

        print(f"  [OK] {len(self.mapeo_agrupaciones)} mapeos guardados")


async def main():
    """Función principal."""
    print("\n" + "="*80)
    print("IMPORTACIÓN DE AGRUPACIONES TERRITORIALES DESDE MYSQL")
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
            mapeador = MapeadorAgrupaciones()

            # Cargar caches
            await mapeador.cargar_cache_provincias(session)
            await mapeador.cargar_cache_paises(session)

            # Importar agrupaciones
            await mapeador.importar_agrupaciones(session)

            # Guardar mapeos
            await mapeador.guardar_mapeo_temporal(session)

            # Commit
            await session.commit()

            print("\n" + "="*80)
            print("[OK] IMPORTACIÓN COMPLETADA")
            print("="*80)
            print(f"\nAgrupaciones: {len(mapeador.mapeo_agrupaciones)} mapeadas")

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
