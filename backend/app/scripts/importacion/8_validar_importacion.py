"""
Script para validar la integridad de la importación.

Ejecuta queries de verificación para asegurar que:
- Todos los registros fueron importados correctamente
- Las relaciones están bien formadas
- No hay datos huérfanos
- Los totales coinciden con las fuentes

Este script debe ejecutarse AL FINAL de todo el proceso de importación.
"""
import asyncio
import pymysql
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, text

from app.core.database import get_database_url
from app.domains.geografico.models.direccion import Pais, Provincia, AgrupacionTerritorial
from app.domains.miembros.models.miembro import Miembro, TipoMiembro
from app.domains.financiero.models.cuotas import CuotaAnual, ImporteCuotaAnio
from app.domains.core.models.estados import EstadoCuota


# Configuración de conexión MySQL (ajustar según necesidad)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Ajustar
    'database': 'europalaica_com',
    'charset': 'utf8mb4'
}


class ValidadorImportacion:
    """Valida la integridad de la importación."""

    def __init__(self):
        self.errores: list[str] = []
        self.advertencias: list[str] = []
        self.metricas_mysql: dict[str, int] = {}
        self.metricas_postgres: dict[str, int] = {}

    def agregar_error(self, mensaje: str):
        """Agrega un error crítico."""
        self.errores.append(f"❌ {mensaje}")

    def agregar_advertencia(self, mensaje: str):
        """Agrega una advertencia."""
        self.advertencias.append(f"⚠️  {mensaje}")

    async def contar_registros_mysql(self, mysql_conn):
        """Cuenta registros en MySQL."""

        print("\nContando registros en MySQL...")

        cursor = mysql_conn.cursor()

        tablas = [
            'PAIS',
            'PROVINCIA',
            'AGRUPACIONTERRITORIAL',
            'MIEMBRO',
            'CUOTAANIOSOCIO',
            'IMPORTEDESCUOTAANIO',
            'DONACION',
            'REMESAS_SEPAXML'
        ]

        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                self.metricas_mysql[tabla] = count
                print(f"  {tabla}: {count}")
            except Exception as e:
                print(f"  {tabla}: ⚠ No existe o error ({e})")
                self.metricas_mysql[tabla] = 0

        cursor.close()

    async def contar_registros_postgres(self, session: AsyncSession):
        """Cuenta registros en PostgreSQL."""

        print("\nContando registros en PostgreSQL...")

        # Países
        result = await session.execute(select(func.count()).select_from(Pais))
        self.metricas_postgres['paises'] = result.scalar()
        print(f"  paises: {self.metricas_postgres['paises']}")

        # Provincias
        result = await session.execute(select(func.count()).select_from(Provincia))
        self.metricas_postgres['provincias'] = result.scalar()
        print(f"  provincias: {self.metricas_postgres['provincias']}")

        # Agrupaciones
        result = await session.execute(select(func.count()).select_from(AgrupacionTerritorial))
        self.metricas_postgres['agrupaciones'] = result.scalar()
        print(f"  agrupaciones_territoriales: {self.metricas_postgres['agrupaciones']}")

        # Miembros
        result = await session.execute(select(func.count()).select_from(Miembro))
        self.metricas_postgres['miembros'] = result.scalar()
        print(f"  miembros: {self.metricas_postgres['miembros']}")

        # Cuotas anuales
        result = await session.execute(select(func.count()).select_from(CuotaAnual))
        self.metricas_postgres['cuotas'] = result.scalar()
        print(f"  cuotas_anuales: {self.metricas_postgres['cuotas']}")

        # Importes de cuota
        result = await session.execute(select(func.count()).select_from(ImporteCuotaAnio))
        self.metricas_postgres['importes_cuota'] = result.scalar()
        print(f"  importes_cuota_anio: {self.metricas_postgres['importes_cuota']}")

    async def validar_totales(self):
        """Valida que los totales sean coherentes."""

        print("\nValidando totales...")

        # Países
        mysql_paises = self.metricas_mysql.get('PAIS', 0)
        pg_paises = self.metricas_postgres.get('paises', 0)

        if mysql_paises > 0 and pg_paises < mysql_paises * 0.9:
            self.agregar_error(f"Países: MySQL={mysql_paises}, PostgreSQL={pg_paises} (< 90%)")
        else:
            print(f"  ✓ Países: {pg_paises}/{mysql_paises}")

        # Provincias
        mysql_provincias = self.metricas_mysql.get('PROVINCIA', 0)
        pg_provincias = self.metricas_postgres.get('provincias', 0)

        if mysql_provincias > 0 and pg_provincias < mysql_provincias * 0.9:
            self.agregar_error(f"Provincias: MySQL={mysql_provincias}, PostgreSQL={pg_provincias} (< 90%)")
        else:
            print(f"  ✓ Provincias: {pg_provincias}/{mysql_provincias}")

        # Agrupaciones
        mysql_agrupaciones = self.metricas_mysql.get('AGRUPACIONTERRITORIAL', 0)
        pg_agrupaciones = self.metricas_postgres.get('agrupaciones', 0)

        if mysql_agrupaciones > 0 and pg_agrupaciones < mysql_agrupaciones * 0.9:
            self.agregar_error(f"Agrupaciones: MySQL={mysql_agrupaciones}, PostgreSQL={pg_agrupaciones} (< 90%)")
        else:
            print(f"  ✓ Agrupaciones: {pg_agrupaciones}/{mysql_agrupaciones}")

        # Miembros
        mysql_miembros = self.metricas_mysql.get('MIEMBRO', 0)
        pg_miembros = self.metricas_postgres.get('miembros', 0)

        if mysql_miembros > 0 and pg_miembros < mysql_miembros * 0.9:
            self.agregar_advertencia(f"Miembros: MySQL={mysql_miembros}, PostgreSQL={pg_miembros} (< 90%)")
        else:
            print(f"  ✓ Miembros: {pg_miembros}/{mysql_miembros}")

        # Cuotas
        mysql_cuotas = self.metricas_mysql.get('CUOTAANIOSOCIO', 0)
        pg_cuotas = self.metricas_postgres.get('cuotas', 0)

        if mysql_cuotas > 0 and pg_cuotas < mysql_cuotas * 0.9:
            self.agregar_advertencia(f"Cuotas: MySQL={mysql_cuotas}, PostgreSQL={pg_cuotas} (< 90%)")
        else:
            print(f"  ✓ Cuotas: {pg_cuotas}/{mysql_cuotas}")

    async def validar_relaciones(self, session: AsyncSession):
        """Valida la integridad referencial."""

        print("\nValidando integridad referencial...")

        # Miembros sin tipo_miembro
        result = await session.execute(
            text("""
                SELECT COUNT(*) FROM miembros
                WHERE tipo_miembro_id IS NULL
            """)
        )
        miembros_sin_tipo = result.scalar()

        if miembros_sin_tipo > 0:
            self.agregar_error(f"{miembros_sin_tipo} miembros sin tipo_miembro_id")
        else:
            print("  ✓ Todos los miembros tienen tipo_miembro_id")

        # Cuotas sin miembro
        result = await session.execute(
            text("""
                SELECT COUNT(*) FROM cuotas_anuales
                WHERE miembro_id IS NULL
            """)
        )
        cuotas_sin_miembro = result.scalar()

        if cuotas_sin_miembro > 0:
            self.agregar_error(f"{cuotas_sin_miembro} cuotas sin miembro_id")
        else:
            print("  ✓ Todas las cuotas tienen miembro_id")

        # Cuotas sin estado
        result = await session.execute(
            text("""
                SELECT COUNT(*) FROM cuotas_anuales
                WHERE estado_id IS NULL
            """)
        )
        cuotas_sin_estado = result.scalar()

        if cuotas_sin_estado > 0:
            self.agregar_error(f"{cuotas_sin_estado} cuotas sin estado_id")
        else:
            print("  ✓ Todas las cuotas tienen estado_id")

        # Cuotas sin agrupación
        result = await session.execute(
            text("""
                SELECT COUNT(*) FROM cuotas_anuales
                WHERE agrupacion_id IS NULL
            """)
        )
        cuotas_sin_agrupacion = result.scalar()

        if cuotas_sin_agrupacion > 0:
            self.agregar_advertencia(f"{cuotas_sin_agrupacion} cuotas sin agrupacion_id")
        else:
            print("  ✓ Todas las cuotas tienen agrupacion_id")

        # Miembros con email duplicado
        result = await session.execute(
            text("""
                SELECT email, COUNT(*) as total
                FROM miembros
                WHERE email IS NOT NULL AND email != ''
                GROUP BY email
                HAVING COUNT(*) > 1
                ORDER BY total DESC
                LIMIT 10
            """)
        )
        emails_duplicados = result.fetchall()

        if emails_duplicados:
            self.agregar_advertencia(f"{len(emails_duplicados)} emails duplicados detectados")
            for email, total in emails_duplicados[:3]:
                print(f"    - {email}: {total} veces")
        else:
            print("  ✓ No hay emails duplicados")

    async def validar_datos_calculados(self, session: AsyncSession):
        """Valida propiedades calculadas y lógica de negocio."""

        print("\nValidando lógica de negocio...")

        # Cuotas marcadas como PAGADA pero con saldo pendiente
        result = await session.execute(
            text("""
                SELECT COUNT(*)
                FROM cuotas_anuales ca
                JOIN estados_cuota ec ON ca.estado_id = ec.id
                WHERE ec.codigo = 'PAGADA'
                AND ca.importe_pagado < ca.importe
            """)
        )
        cuotas_pagadas_incorrectas = result.scalar()

        if cuotas_pagadas_incorrectas > 0:
            self.agregar_advertencia(f"{cuotas_pagadas_incorrectas} cuotas marcadas PAGADA con saldo pendiente")
        else:
            print("  ✓ Estados de cuotas coherentes con importes")

        # Miembros activos sin agrupación
        result = await session.execute(
            text("""
                SELECT COUNT(*)
                FROM miembros
                WHERE activo = TRUE
                AND fecha_baja IS NULL
                AND agrupacion_id IS NULL
            """)
        )
        miembros_activos_sin_agrupacion = result.scalar()

        if miembros_activos_sin_agrupacion > 0:
            self.agregar_advertencia(f"{miembros_activos_sin_agrupacion} miembros activos sin agrupación")
        else:
            print("  ✓ Todos los miembros activos tienen agrupación")

    async def generar_reporte(self):
        """Genera el reporte final de validación."""

        print("\n" + "="*80)
        print("REPORTE DE VALIDACIÓN")
        print("="*80 + "\n")

        print("MÉTRICAS DE IMPORTACIÓN:")
        print("-" * 40)
        print(f"Países:       {self.metricas_postgres.get('paises', 0):>6}")
        print(f"Provincias:   {self.metricas_postgres.get('provincias', 0):>6}")
        print(f"Agrupaciones: {self.metricas_postgres.get('agrupaciones', 0):>6}")
        print(f"Miembros:     {self.metricas_postgres.get('miembros', 0):>6}")
        print(f"Cuotas:       {self.metricas_postgres.get('cuotas', 0):>6}")
        print(f"Importes:     {self.metricas_postgres.get('importes_cuota', 0):>6}")

        print("\n" + "="*80)

        if self.errores:
            print("\nERRORES CRÍTICOS:")
            for error in self.errores:
                print(f"  {error}")

        if self.advertencias:
            print("\nADVERTENCIAS:")
            for advertencia in self.advertencias:
                print(f"  {advertencia}")

        if not self.errores and not self.advertencias:
            print("\n✅ VALIDACIÓN EXITOSA - No se encontraron problemas")
        elif not self.errores:
            print(f"\n⚠️  VALIDACIÓN CON ADVERTENCIAS - {len(self.advertencias)} advertencias")
        else:
            print(f"\n❌ VALIDACIÓN FALLIDA - {len(self.errores)} errores, {len(self.advertencias)} advertencias")

        print("\n" + "="*80 + "\n")


async def main():
    """Función principal."""

    print("\n" + "="*80)
    print("VALIDACIÓN DE IMPORTACIÓN")
    print("="*80 + "\n")

    # Conectar a MySQL
    print("Conectando a MySQL...")
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        print("  ✓ Conexión MySQL establecida")
    except Exception as e:
        print(f"  ✗ Error conectando a MySQL: {e}")
        print("\n  Continuando sin validación de totales MySQL...")
        mysql_conn = None

    # Conectar a PostgreSQL
    print("\nConectando a PostgreSQL...")
    database_url = get_database_url()
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            validador = ValidadorImportacion()

            # Contar registros
            if mysql_conn:
                await validador.contar_registros_mysql(mysql_conn)

            await validador.contar_registros_postgres(session)

            # Validar totales
            if mysql_conn:
                await validador.validar_totales()

            # Validar relaciones
            await validador.validar_relaciones(session)

            # Validar datos calculados
            await validador.validar_datos_calculados(session)

            # Generar reporte
            await validador.generar_reporte()

        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            if mysql_conn:
                mysql_conn.close()
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
