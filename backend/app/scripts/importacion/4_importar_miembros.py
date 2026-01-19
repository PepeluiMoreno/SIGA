"""
Script para importar miembros desde el dump MySQL.

Importa las tablas:
- MIEMBRO → miembros
- MIEMBROELIMINADO5ANIOS → miembros (con fecha_baja)
- SOCIOSFALLECIDOS → miembros (con motivo_baja='Fallecido')

Este script implementa toda la lógica de mapeo confirmada en DECISIONES_MAPEO_CONFIRMADAS.md

IMPORTANTE:
- Encripta DNI/NIE e IBANs antes de almacenarlos
- Prioridad de teléfonos: móvil > fijo_casa > fijo_trabajo
- Profesión/estudios solo si es_voluntario=True
- Agrupación inferida de última cuota
- Provincia inferida por código postal

Este script debe ejecutarse DESPUÉS de importar agrupaciones.
"""
import asyncio
import uuid
import pymysql
import re
from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import get_database_url
from app.infrastructure.services.encriptacion_service import get_encriptacion_service
from app.domains.miembros.models.miembro import Miembro, TipoMiembro
from app.domains.miembros.models.estado_miembro import EstadoMiembro
from app.domains.geografico.models.direccion import Provincia


# Configuración de conexión MySQL (ajustar según necesidad)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Ajustar
    'database': 'europalaica_com',
    'charset': 'utf8mb4'
}


class MapeadorMiembros:
    """Mapea miembros de MySQL a PostgreSQL."""

    def __init__(self):
        self.mapeo_miembros: dict[int, uuid.UUID] = {}  # CODUSER → UUID
        self.servicio_encriptacion = get_encriptacion_service()
        self.tipo_miembro_socio_id: Optional[uuid.UUID] = None
        self.tipo_miembro_simpatizante_id: Optional[uuid.UUID] = None
        self.tipo_miembro_voluntario_id: Optional[uuid.UUID] = None
        self.estado_activo_id: Optional[uuid.UUID] = None
        self.estado_baja_id: Optional[uuid.UUID] = None
        self.cache_provincias_por_cp: dict[str, uuid.UUID] = {}

    async def cargar_tipos_miembro(self, session: AsyncSession):
        """Carga los UUIDs de tipos de miembro."""

        result = await session.execute(
            select(TipoMiembro).where(TipoMiembro.codigo == 'SOCIO')
        )
        tipo_socio = result.scalar_one_or_none()
        if tipo_socio:
            self.tipo_miembro_socio_id = tipo_socio.id

        result = await session.execute(
            select(TipoMiembro).where(TipoMiembro.codigo == 'SIMPATIZANTE')
        )
        tipo_simpatizante = result.scalar_one_or_none()
        if tipo_simpatizante:
            self.tipo_miembro_simpatizante_id = tipo_simpatizante.id

        result = await session.execute(
            select(TipoMiembro).where(TipoMiembro.codigo == 'VOLUNTARIO')
        )
        tipo_voluntario = result.scalar_one_or_none()
        if tipo_voluntario:
            self.tipo_miembro_voluntario_id = tipo_voluntario.id

        print(f"  Tipos de miembro cargados:")
        print(f"    SOCIO: {self.tipo_miembro_socio_id}")
        print(f"    SIMPATIZANTE: {self.tipo_miembro_simpatizante_id}")
        print(f"    VOLUNTARIO: {self.tipo_miembro_voluntario_id}")

    async def cargar_estados_miembro(self, session: AsyncSession):
        """Carga los UUIDs de estados de miembro."""

        result = await session.execute(
            select(EstadoMiembro).where(EstadoMiembro.codigo == 'ACTIVO')
        )
        estado_activo = result.scalar_one_or_none()
        if estado_activo:
            self.estado_activo_id = estado_activo.id

        result = await session.execute(
            select(EstadoMiembro).where(EstadoMiembro.codigo == 'BAJA')
        )
        estado_baja = result.scalar_one_or_none()
        if estado_baja:
            self.estado_baja_id = estado_baja.id

        print(f"  Estados de miembro cargados:")
        print(f"    ACTIVO: {self.estado_activo_id}")
        print(f"    BAJA: {self.estado_baja_id}")

    def mapear_tipo_miembro(self, tipo_mysql: Optional[str]) -> uuid.UUID:
        """Mapea TIPOMIEMBRO de MySQL a tipo_miembro_id."""

        if not tipo_mysql:
            return self.tipo_miembro_socio_id

        tipo_lower = tipo_mysql.lower().strip()

        if 'simpatizante' in tipo_lower:
            return self.tipo_miembro_simpatizante_id
        elif 'voluntario' in tipo_lower:
            return self.tipo_miembro_voluntario_id
        else:
            return self.tipo_miembro_socio_id

    def procesar_telefonos(self, movil: Optional[str], fijo_casa: Optional[str], fijo_trabajo: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """
        Prioriza teléfonos según decisión confirmada:
        móvil > fijo_casa > fijo_trabajo

        Retorna: (telefono, telefono2)
        """

        telefonos = []

        if movil and movil.strip():
            telefonos.append(movil.strip())

        if fijo_casa and fijo_casa.strip():
            telefonos.append(fijo_casa.strip())

        if fijo_trabajo and fijo_trabajo.strip():
            telefonos.append(fijo_trabajo.strip())

        telefono = telefonos[0] if len(telefonos) > 0 else None
        telefono2 = telefonos[1] if len(telefonos) > 1 else None

        return telefono, telefono2

    async def obtener_uuid_pais(self, session: AsyncSession, codigo_pais: Optional[int]) -> Optional[uuid.UUID]:
        """Obtiene el UUID de un país desde temp_id_mapping."""

        if not codigo_pais:
            return None

        result = await session.execute(
            """
            SELECT new_uuid FROM temp_id_mapping
            WHERE tabla = 'PAIS' AND old_id = :old_id
            """,
            {"old_id": codigo_pais}
        )
        row = result.fetchone()
        return row[0] if row else None

    async def inferir_provincia_por_cp(self, session: AsyncSession, codigo_postal: Optional[str]) -> Optional[uuid.UUID]:
        """
        Infiere la provincia por código postal (Decisión 4).

        Lógica:
        - Los 2 primeros dígitos del CP español corresponden a la provincia
        - Busca en caché primero
        - Si no existe, busca en BD por código
        """

        if not codigo_postal or len(codigo_postal) < 2:
            return None

        # Extraer los 2 primeros dígitos
        codigo_provincia = codigo_postal[:2]

        # Verificar caché
        if codigo_provincia in self.cache_provincias_por_cp:
            return self.cache_provincias_por_cp[codigo_provincia]

        # Buscar en BD
        result = await session.execute(
            select(Provincia).where(Provincia.codigo == codigo_provincia)
        )
        provincia = result.scalar_one_or_none()

        if provincia:
            self.cache_provincias_por_cp[codigo_provincia] = provincia.id
            return provincia.id

        return None

    async def obtener_agrupacion_por_ultima_cuota(self, mysql_conn, coduser: int) -> Optional[str]:
        """
        Infiere la agrupación del miembro por su última cuota (Decisión 3).

        Retorna: CODAGRUPACION de la última CUOTAANIOSOCIO
        """

        cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT CODAGRUPACION
            FROM CUOTAANIOSOCIO
            WHERE CODUSER = %s
            ORDER BY ANIO DESC
            LIMIT 1
        """, (coduser,))

        row = cursor.fetchone()
        cursor.close()

        if row and row['CODAGRUPACION']:
            return row['CODAGRUPACION'].strip()

        return None

    async def obtener_uuid_agrupacion(self, session: AsyncSession, codigo_agrupacion: Optional[str]) -> Optional[uuid.UUID]:
        """Obtiene el UUID de una agrupación por su código."""

        if not codigo_agrupacion:
            return None

        result = await session.execute(
            """
            SELECT id FROM agrupaciones_territoriales
            WHERE codigo = :codigo
            """,
            {"codigo": codigo_agrupacion}
        )
        row = result.fetchone()
        return row[0] if row else None

    def determinar_es_voluntario(self, colabora: Optional[str]) -> bool:
        """
        Determina si el miembro es voluntario basado en el campo COLABORA.

        Si COLABORA tiene contenido significativo, se marca como voluntario.
        """

        if not colabora:
            return False

        colabora_limpio = colabora.strip().lower()

        # Palabras clave que indican que NO es voluntario
        palabras_negativas = ['no', 'n/a', 'ninguna', 'ninguno', 'nada']

        if colabora_limpio in palabras_negativas:
            return False

        # Si tiene contenido, consideramos que es voluntario
        return len(colabora_limpio) > 0

    async def importar_miembros(self, session: AsyncSession, mysql_conn):
        """Importa la tabla MIEMBRO."""

        print("\nImportando miembros...")

        cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT
                CODUSER,
                TIPOMIEMBRO,
                APE1,
                APE2,
                NOM,
                TIPODOCUMENTOMIEMBRO,
                NUMDOCUMENTOMIEMBRO,
                CODPAISDOC,
                CODPAISDOM,
                CODPROV,
                DIRECCION,
                CP,
                LOCALIDAD,
                FIJO_CASA,
                FIJO_TRABAJO,
                MOVIL,
                EMAIL,
                CUENTAMIEMBROIBAN,
                COLABORA,
                FECHABAJA,
                MOTIVOBAJA,
                FECHANAC
            FROM MIEMBRO
            ORDER BY CODUSER
        """)

        importados = 0
        omitidos = 0

        for row in cursor:
            coduser = row['CODUSER']

            if not coduser:
                omitidos += 1
                continue

            # Mapear tipo de miembro
            tipo_miembro_id = self.mapear_tipo_miembro(row['TIPOMIEMBRO'])

            # Procesar teléfonos (Decisión 1)
            telefono, telefono2 = self.procesar_telefonos(
                row['MOVIL'],
                row['FIJO_CASA'],
                row['FIJO_TRABAJO']
            )

            # Obtener país de documento
            pais_documento_id = await self.obtener_uuid_pais(session, row['CODPAISDOC'])

            # Obtener país de domicilio
            pais_domicilio_id = await self.obtener_uuid_pais(session, row['CODPAISDOM'])

            # Inferir provincia por CP (Decisión 4)
            provincia_id = await self.inferir_provincia_por_cp(session, row['CP'])

            # Si no se pudo inferir, intentar por CODPROV directo
            if not provincia_id and row['CODPROV']:
                result = await session.execute(
                    """
                    SELECT new_uuid FROM temp_id_mapping
                    WHERE tabla = 'PROVINCIA' AND old_id = :old_id
                    """,
                    {"old_id": row['CODPROV']}
                )
                provincia_row = result.fetchone()
                if provincia_row:
                    provincia_id = provincia_row[0]

            # Obtener agrupación por última cuota (Decisión 3)
            codigo_agrupacion = await self.obtener_agrupacion_por_ultima_cuota(mysql_conn, coduser)
            agrupacion_id = await self.obtener_uuid_agrupacion(session, codigo_agrupacion)

            # Determinar si es voluntario
            es_voluntario = self.determinar_es_voluntario(row['COLABORA'])

            # Encriptar DNI/NIE si existe
            numero_documento_encriptado = None
            if row['NUMDOCUMENTOMIEMBRO']:
                doc_limpio = row['NUMDOCUMENTOMIEMBRO'].strip().replace(' ', '').replace('-', '')
                if doc_limpio:
                    numero_documento_encriptado = self.servicio_encriptacion.encriptar(doc_limpio)

            # Encriptar IBAN si existe
            iban_encriptado = None
            if row['CUENTAMIEMBROIBAN']:
                iban_limpio = row['CUENTAMIEMBROIBAN'].strip().replace(' ', '')
                if iban_limpio:
                    iban_encriptado = self.servicio_encriptacion.encriptar_iban(iban_limpio)

            # Procesar fecha de baja
            fecha_baja = None
            if row['FECHABAJA']:
                if isinstance(row['FECHABAJA'], date):
                    fecha_baja = row['FECHABAJA']
                elif isinstance(row['FECHABAJA'], str):
                    try:
                        fecha_baja = date.fromisoformat(row['FECHABAJA'])
                    except:
                        pass

            # Procesar fecha de nacimiento
            fecha_nacimiento = None
            if row['FECHANAC']:
                if isinstance(row['FECHANAC'], date):
                    fecha_nacimiento = row['FECHANAC']
                elif isinstance(row['FECHANAC'], str):
                    try:
                        fecha_nacimiento = date.fromisoformat(row['FECHANAC'])
                    except:
                        pass

            # Profesión y estudios solo si es voluntario (Decisión 2)
            # En este script, no tenemos esos campos en MIEMBRO,
            # se deberán completar manualmente o desde otra fuente

            # Determinar estado: BAJA si tiene fecha_baja, ACTIVO en caso contrario
            estado_id = self.estado_baja_id if fecha_baja else self.estado_activo_id

            # Crear miembro
            miembro = Miembro(
                nombre=row['NOM'].strip() if row['NOM'] else "Sin nombre",
                apellido1=row['APE1'].strip() if row['APE1'] else "Sin apellido",
                apellido2=row['APE2'].strip() if row['APE2'] else None,
                fecha_nacimiento=fecha_nacimiento,
                tipo_miembro_id=tipo_miembro_id,
                estado_id=estado_id,
                tipo_documento=row['TIPODOCUMENTOMIEMBRO'].strip() if row['TIPODOCUMENTOMIEMBRO'] else None,
                numero_documento=numero_documento_encriptado,
                pais_documento_id=pais_documento_id,
                direccion=row['DIRECCION'].strip() if row['DIRECCION'] else None,
                codigo_postal=row['CP'].strip() if row['CP'] else None,
                localidad=row['LOCALIDAD'].strip() if row['LOCALIDAD'] else None,
                provincia_id=provincia_id,
                pais_domicilio_id=pais_domicilio_id,
                telefono=telefono,
                telefono2=telefono2,
                email=row['EMAIL'].strip() if row['EMAIL'] else None,
                agrupacion_id=agrupacion_id,
                iban=iban_encriptado,
                fecha_baja=fecha_baja,
                motivo_baja=row['MOTIVOBAJA'].strip() if row['MOTIVOBAJA'] else None,
                activo=(fecha_baja is None),
                es_voluntario=es_voluntario,
                observaciones_voluntariado=row['COLABORA'].strip() if row['COLABORA'] else None,
                intereses=row['COLABORA'].strip() if row['COLABORA'] else None
            )

            session.add(miembro)
            await session.flush()

            self.mapeo_miembros[coduser] = miembro.id
            importados += 1

            if importados % 100 == 0:
                print(f"  Procesados {importados} miembros...")

        cursor.close()

        print(f"  ✓ {importados} miembros importados")
        print(f"  ⚠ {omitidos} miembros omitidos (sin CODUSER)")

    async def importar_miembros_eliminados(self, session: AsyncSession, mysql_conn):
        """Importa la tabla MIEMBROELIMINADO5ANIOS (miembros con baja)."""

        print("\nImportando miembros eliminados...")

        cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)

        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'MIEMBROELIMINADO5ANIOS'")
        if not cursor.fetchone():
            print("  ⚠ Tabla MIEMBROELIMINADO5ANIOS no existe, se omite")
            cursor.close()
            return

        cursor.execute("""
            SELECT
                CODUSER,
                TIPOMIEMBRO,
                APE1,
                APE2,
                NOM,
                FECHABAJA,
                MOTIVOBAJA,
                EMAIL
            FROM MIEMBROELIMINADO5ANIOS
            ORDER BY CODUSER
        """)

        importados = 0

        for row in cursor:
            coduser = row['CODUSER']

            # Si ya existe en mapeo, skip (ya se importó de MIEMBRO)
            if coduser in self.mapeo_miembros:
                continue

            # Mapear tipo de miembro
            tipo_miembro_id = self.mapear_tipo_miembro(row['TIPOMIEMBRO'])

            # Procesar fecha de baja
            fecha_baja = None
            if row['FECHABAJA']:
                if isinstance(row['FECHABAJA'], date):
                    fecha_baja = row['FECHABAJA']
                elif isinstance(row['FECHABAJA'], str):
                    try:
                        fecha_baja = date.fromisoformat(row['FECHABAJA'])
                    except:
                        pass

            # Crear miembro dado de baja (estado BAJA)
            miembro = Miembro(
                nombre=row['NOM'].strip() if row['NOM'] else "Sin nombre",
                apellido1=row['APE1'].strip() if row['APE1'] else "Sin apellido",
                apellido2=row['APE2'].strip() if row['APE2'] else None,
                tipo_miembro_id=tipo_miembro_id,
                estado_id=self.estado_baja_id,
                email=row['EMAIL'].strip() if row['EMAIL'] else None,
                fecha_baja=fecha_baja or date.today(),
                motivo_baja=row['MOTIVOBAJA'].strip() if row['MOTIVOBAJA'] else "Baja registrada",
                activo=False,
                es_voluntario=False
            )

            session.add(miembro)
            await session.flush()

            self.mapeo_miembros[coduser] = miembro.id
            importados += 1

        cursor.close()

        print(f"  ✓ {importados} miembros eliminados importados")

    async def importar_miembros_fallecidos(self, session: AsyncSession, mysql_conn):
        """Importa la tabla SOCIOSFALLECIDOS."""

        print("\nImportando miembros fallecidos...")

        cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)

        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'SOCIOSFALLECIDOS'")
        if not cursor.fetchone():
            print("  ⚠ Tabla SOCIOSFALLECIDOS no existe, se omite")
            cursor.close()
            return

        cursor.execute("""
            SELECT
                CODUSER,
                APE1,
                APE2,
                NOM,
                FECHABAJA,
                EMAIL
            FROM SOCIOSFALLECIDOS
            ORDER BY CODUSER
        """)

        importados = 0
        actualizados = 0

        for row in cursor:
            coduser = row['CODUSER']

            # Si ya existe, actualizar motivo de baja
            if coduser in self.mapeo_miembros:
                miembro_uuid = self.mapeo_miembros[coduser]
                result = await session.execute(
                    select(Miembro).where(Miembro.id == miembro_uuid)
                )
                miembro = result.scalar_one_or_none()

                if miembro:
                    miembro.motivo_baja = "Fallecido"
                    miembro.estado_id = self.estado_baja_id
                    if not miembro.fecha_baja and row['FECHABAJA']:
                        if isinstance(row['FECHABAJA'], date):
                            miembro.fecha_baja = row['FECHABAJA']
                    miembro.activo = False
                    actualizados += 1
                continue

            # Si no existe, crear como fallecido (estado BAJA)
            fecha_baja = None
            if row['FECHABAJA']:
                if isinstance(row['FECHABAJA'], date):
                    fecha_baja = row['FECHABAJA']

            miembro = Miembro(
                nombre=row['NOM'].strip() if row['NOM'] else "Sin nombre",
                apellido1=row['APE1'].strip() if row['APE1'] else "Sin apellido",
                apellido2=row['APE2'].strip() if row['APE2'] else None,
                tipo_miembro_id=self.tipo_miembro_socio_id,
                estado_id=self.estado_baja_id,
                email=row['EMAIL'].strip() if row['EMAIL'] else None,
                fecha_baja=fecha_baja or date.today(),
                motivo_baja="Fallecido",
                activo=False,
                es_voluntario=False
            )

            session.add(miembro)
            await session.flush()

            self.mapeo_miembros[coduser] = miembro.id
            importados += 1

        cursor.close()

        print(f"  ✓ {importados} miembros fallecidos importados")
        print(f"  ✓ {actualizados} miembros existentes actualizados como fallecidos")

    async def guardar_mapeo_temporal(self, session: AsyncSession):
        """Guarda el mapeo de CODUSER en temp_id_mapping."""

        print("\nGuardando mapeo de miembros...")

        for coduser, uuid_val in self.mapeo_miembros.items():
            await session.execute(
                """
                INSERT INTO temp_id_mapping (tabla, old_id, new_uuid)
                VALUES ('MIEMBRO', :old_id, :new_uuid)
                ON CONFLICT (tabla, old_id) DO UPDATE SET new_uuid = EXCLUDED.new_uuid
                """,
                {"old_id": coduser, "new_uuid": uuid_val}
            )

        print(f"  ✓ {len(self.mapeo_miembros)} mapeos guardados")


async def main():
    """Función principal."""

    print("\n" + "="*80)
    print("IMPORTACIÓN DE MIEMBROS")
    print("="*80 + "\n")

    # Conectar a MySQL
    print("Conectando a MySQL...")
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        print("  ✓ Conexión MySQL establecida")
    except Exception as e:
        print(f"  ✗ Error conectando a MySQL: {e}")
        print("\n  Ajusta MYSQL_CONFIG en el script con las credenciales correctas.")
        return

    # Conectar a PostgreSQL
    print("\nConectando a PostgreSQL...")
    database_url = get_database_url()
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            mapeador = MapeadorMiembros()

            # Cargar tipos de miembro
            print("\nCargando tipos de miembro...")
            await mapeador.cargar_tipos_miembro(session)

            # Cargar estados de miembro
            print("\nCargando estados de miembro...")
            await mapeador.cargar_estados_miembro(session)

            # Importar miembros activos
            await mapeador.importar_miembros(session, mysql_conn)

            # Importar miembros eliminados
            await mapeador.importar_miembros_eliminados(session, mysql_conn)

            # Importar miembros fallecidos
            await mapeador.importar_miembros_fallecidos(session, mysql_conn)

            # Guardar mapeos
            await mapeador.guardar_mapeo_temporal(session)

            # Commit
            await session.commit()

            print("\n" + "="*80)
            print("✓ IMPORTACIÓN COMPLETADA")
            print("="*80)
            print(f"\nMiembros importados: {len(mapeador.mapeo_miembros)}")

        except Exception as e:
            await session.rollback()
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            mysql_conn.close()
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
