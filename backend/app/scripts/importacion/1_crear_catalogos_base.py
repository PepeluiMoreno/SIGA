"""
Script para crear catálogos base necesarios para la importación.

Este script debe ejecutarse PRIMERO antes de cualquier importación de datos.
Crea los tipos de miembro y estados necesarios para el sistema.
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import get_database_url
from app.domains.miembros.models.miembro import TipoMiembro
from app.domains.miembros.models.estado_miembro import EstadoMiembro
from app.domains.core.models.estados import EstadoCuota
from app.domains.core.models.estados import EstadoCampania
from app.domains.core.models.estados import EstadoActividad
from app.domains.core.models.estados import EstadoParticipante


async def crear_tipos_miembro(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Crea los tipos de miembro base y retorna mapeo código → UUID."""

    tipos_data = [
        {
            "codigo": "SOCIO",
            "nombre": "Socio",
            "descripcion": "Miembro de pleno derecho con derecho a voto",
            "requiere_cuota": True,
            "puede_votar": True,
            "activo": True
        },
        {
            "codigo": "SIMPATIZANTE",
            "nombre": "Simpatizante",
            "descripcion": "Persona simpatizante sin derecho a voto",
            "requiere_cuota": False,
            "puede_votar": False,
            "activo": True
        },
        {
            "codigo": "VOLUNTARIO",
            "nombre": "Voluntario",
            "descripcion": "Voluntario sin cuota ni derecho a voto",
            "requiere_cuota": False,
            "puede_votar": False,
            "activo": True
        },
        {
            "codigo": "COLABORADOR",
            "nombre": "Colaborador",
            "descripcion": "Colaborador puntual",
            "requiere_cuota": False,
            "puede_votar": False,
            "activo": True
        }
    ]

    mapeo = {}

    for tipo_data in tipos_data:
        # Verificar si ya existe
        result = await session.execute(
            select(TipoMiembro).where(TipoMiembro.codigo == tipo_data["codigo"])
        )
        tipo_existente = result.scalar_one_or_none()

        if tipo_existente:
            print(f"  [OK] TipoMiembro '{tipo_data['codigo']}' ya existe (UUID: {tipo_existente.id})")
            mapeo[tipo_data["codigo"]] = tipo_existente.id
        else:
            tipo = TipoMiembro(**tipo_data)
            session.add(tipo)
            await session.flush()
            print(f"  + TipoMiembro '{tipo_data['codigo']}' creado (UUID: {tipo.id})")
            mapeo[tipo_data["codigo"]] = tipo.id

    return mapeo


async def crear_estados_miembro(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Crea los estados de miembro y retorna mapeo código → UUID."""

    estados_data = [
        {
            "codigo": "PENDIENTE_APROBACION",
            "nombre": "Pendiente de Aprobación",
            "descripcion": "Alta solicitada, pendiente de revisión por un gestor",
            "color": "#FFC107",
            "orden": 1,
            "activo": True
        },
        {
            "codigo": "ACTIVO",
            "nombre": "Activo",
            "descripcion": "Miembro activo en la organización",
            "color": "#28A745",
            "orden": 2,
            "activo": True
        },
        {
            "codigo": "SUSPENDIDO",
            "nombre": "Suspendido",
            "descripcion": "Miembro temporalmente suspendido",
            "color": "#FFA500",
            "orden": 3,
            "activo": True
        },
        {
            "codigo": "BAJA",
            "nombre": "Baja",
            "descripcion": "Miembro dado de baja definitiva",
            "color": "#DC3545",
            "orden": 4,
            "activo": True
        }
    ]

    mapeo = {}

    for estado_data in estados_data:
        result = await session.execute(
            select(EstadoMiembro).where(EstadoMiembro.codigo == estado_data["codigo"])
        )
        estado_existente = result.scalar_one_or_none()

        if estado_existente:
            print(f"  [OK] EstadoMiembro '{estado_data['codigo']}' ya existe (UUID: {estado_existente.id})")
            mapeo[estado_data["codigo"]] = estado_existente.id
        else:
            estado = EstadoMiembro(**estado_data)
            session.add(estado)
            await session.flush()
            print(f"  + EstadoMiembro '{estado_data['codigo']}' creado (UUID: {estado.id})")
            mapeo[estado_data["codigo"]] = estado.id

    return mapeo


async def crear_estados_cuota(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Crea los estados de cuota y retorna mapeo código → UUID."""

    estados_data = [
        {
            "codigo": "PENDIENTE",
            "nombre": "Pendiente",
            "descripcion": "Cuota pendiente de pago",
            "color": "#FFA500",
            "orden": 1,
            "activo": True
        },
        {
            "codigo": "PAGADA",
            "nombre": "Pagada",
            "descripcion": "Cuota completamente pagada",
            "color": "#28A745",
            "orden": 2,
            "activo": True
        },
        {
            "codigo": "PARCIAL",
            "nombre": "Pago Parcial",
            "descripcion": "Cuota pagada parcialmente",
            "color": "#17A2B8",
            "orden": 3,
            "activo": True
        },
        {
            "codigo": "VENCIDA",
            "nombre": "Vencida",
            "descripcion": "Cuota con fecha de pago vencida",
            "color": "#DC3545",
            "orden": 4,
            "activo": True
        },
        {
            "codigo": "EXENTA",
            "nombre": "Exenta",
            "descripcion": "Cuota exenta de pago",
            "color": "#6C757D",
            "orden": 5,
            "activo": True
        },
        {
            "codigo": "CANCELADA",
            "nombre": "Cancelada",
            "descripcion": "Cuota cancelada",
            "color": "#6C757D",
            "orden": 6,
            "activo": True
        }
    ]

    mapeo = {}

    for estado_data in estados_data:
        result = await session.execute(
            select(EstadoCuota).where(EstadoCuota.codigo == estado_data["codigo"])
        )
        estado_existente = result.scalar_one_or_none()

        if estado_existente:
            print(f"  [OK] EstadoCuota '{estado_data['codigo']}' ya existe (UUID: {estado_existente.id})")
            mapeo[estado_data["codigo"]] = estado_existente.id
        else:
            estado = EstadoCuota(**estado_data)
            session.add(estado)
            await session.flush()
            print(f"  + EstadoCuota '{estado_data['codigo']}' creado (UUID: {estado.id})")
            mapeo[estado_data["codigo"]] = estado.id

    return mapeo


async def crear_estados_campania(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Crea los estados de campaña y retorna mapeo código → UUID."""

    estados_data = [
        {
            "codigo": "BORRADOR",
            "nombre": "Borrador",
            "descripcion": "Campaña en fase de planificación",
            "color": "#6C757D",
            "orden": 1,
            "activo": True
        },
        {
            "codigo": "PLANIFICADA",
            "nombre": "Planificada",
            "descripcion": "Campaña planificada pendiente de inicio",
            "color": "#17A2B8",
            "orden": 2,
            "activo": True
        },
        {
            "codigo": "ACTIVA",
            "nombre": "Activa",
            "descripcion": "Campaña en ejecución",
            "color": "#28A745",
            "orden": 3,
            "activo": True
        },
        {
            "codigo": "SUSPENDIDA",
            "nombre": "Suspendida",
            "descripcion": "Campaña temporalmente suspendida",
            "color": "#FFC107",
            "orden": 4,
            "activo": True
        },
        {
            "codigo": "FINALIZADA",
            "nombre": "Finalizada",
            "descripcion": "Campaña completada",
            "color": "#007BFF",
            "orden": 5,
            "activo": True
        },
        {
            "codigo": "CANCELADA",
            "nombre": "Cancelada",
            "descripcion": "Campaña cancelada",
            "color": "#DC3545",
            "orden": 6,
            "activo": True
        }
    ]

    mapeo = {}

    for estado_data in estados_data:
        result = await session.execute(
            select(EstadoCampania).where(EstadoCampania.codigo == estado_data["codigo"])
        )
        estado_existente = result.scalar_one_or_none()

        if estado_existente:
            print(f"  [OK] EstadoCampania '{estado_data['codigo']}' ya existe (UUID: {estado_existente.id})")
            mapeo[estado_data["codigo"]] = estado_existente.id
        else:
            estado = EstadoCampania(**estado_data)
            session.add(estado)
            await session.flush()
            print(f"  + EstadoCampania '{estado_data['codigo']}' creado (UUID: {estado.id})")
            mapeo[estado_data["codigo"]] = estado.id

    return mapeo


async def crear_estados_actividad(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Crea los estados de actividad y retorna mapeo código → UUID."""

    estados_data = [
        {
            "codigo": "PROPUESTA",
            "nombre": "Propuesta",
            "descripcion": "Actividad propuesta pendiente de aprobación",
            "color": "#6C757D",
            "orden": 1,
            "activo": True
        },
        {
            "codigo": "APROBADA",
            "nombre": "Aprobada",
            "descripcion": "Actividad aprobada pendiente de programación",
            "color": "#17A2B8",
            "orden": 2,
            "activo": True
        },
        {
            "codigo": "PROGRAMADA",
            "nombre": "Programada",
            "descripcion": "Actividad programada con fecha definida",
            "color": "#FFC107",
            "orden": 3,
            "activo": True
        },
        {
            "codigo": "EN_CURSO",
            "nombre": "En Curso",
            "descripcion": "Actividad en ejecución",
            "color": "#28A745",
            "orden": 4,
            "activo": True
        },
        {
            "codigo": "COMPLETADA",
            "nombre": "Completada",
            "descripcion": "Actividad finalizada exitosamente",
            "color": "#007BFF",
            "orden": 5,
            "activo": True
        },
        {
            "codigo": "CANCELADA",
            "nombre": "Cancelada",
            "descripcion": "Actividad cancelada",
            "color": "#DC3545",
            "orden": 6,
            "activo": True
        }
    ]

    mapeo = {}

    for estado_data in estados_data:
        result = await session.execute(
            select(EstadoActividad).where(EstadoActividad.codigo == estado_data["codigo"])
        )
        estado_existente = result.scalar_one_or_none()

        if estado_existente:
            print(f"  [OK] EstadoActividad '{estado_data['codigo']}' ya existe (UUID: {estado_existente.id})")
            mapeo[estado_data["codigo"]] = estado_existente.id
        else:
            estado = EstadoActividad(**estado_data)
            session.add(estado)
            await session.flush()
            print(f"  + EstadoActividad '{estado_data['codigo']}' creado (UUID: {estado.id})")
            mapeo[estado_data["codigo"]] = estado.id

    return mapeo


async def crear_estados_participante(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Crea los estados de participante en grupos y retorna mapeo código → UUID."""

    estados_data = [
        {
            "codigo": "INVITADO",
            "nombre": "Invitado",
            "descripcion": "Persona invitada a participar",
            "color": "#6C757D",
            "orden": 1,
            "activo": True
        },
        {
            "codigo": "ACTIVO",
            "nombre": "Activo",
            "descripcion": "Participante activo",
            "color": "#28A745",
            "orden": 2,
            "activo": True
        },
        {
            "codigo": "INACTIVO",
            "nombre": "Inactivo",
            "descripcion": "Participante temporalmente inactivo",
            "color": "#FFC107",
            "orden": 3,
            "activo": True
        },
        {
            "codigo": "RETIRADO",
            "nombre": "Retirado",
            "descripcion": "Participante que se ha retirado",
            "color": "#DC3545",
            "orden": 4,
            "activo": True
        }
    ]

    mapeo = {}

    for estado_data in estados_data:
        result = await session.execute(
            select(EstadoParticipante).where(EstadoParticipante.codigo == estado_data["codigo"])
        )
        estado_existente = result.scalar_one_or_none()

        if estado_existente:
            print(f"  [OK] EstadoParticipante '{estado_data['codigo']}' ya existe (UUID: {estado_existente.id})")
            mapeo[estado_data["codigo"]] = estado_existente.id
        else:
            estado = EstadoParticipante(**estado_data)
            session.add(estado)
            await session.flush()
            print(f"  + EstadoParticipante '{estado_data['codigo']}' creado (UUID: {estado.id})")
            mapeo[estado_data["codigo"]] = estado.id

    return mapeo


async def main():
    """Función principal que ejecuta la creación de catálogos."""

    print("\n" + "="*80)
    print("CREACIÓN DE CATÁLOGOS BASE")
    print("="*80 + "\n")

    # Crear engine y session
    database_url = get_database_url()
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        }
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("1. Creando Tipos de Miembro...")
            tipos_miembro = await crear_tipos_miembro(session)

            print("\n2. Creando Estados de Miembro...")
            estados_miembro = await crear_estados_miembro(session)

            print("\n3. Creando Estados de Cuota...")
            estados_cuota = await crear_estados_cuota(session)

            print("\n4. Creando Estados de Campaña...")
            estados_campania = await crear_estados_campania(session)

            print("\n5. Creando Estados de Actividad...")
            estados_actividad = await crear_estados_actividad(session)

            print("\n6. Creando Estados de Participante...")
            estados_participante = await crear_estados_participante(session)

            # Commit final
            await session.commit()

            print("\n" + "="*80)
            print("[OK] CATÁLOGOS CREADOS EXITOSAMENTE")
            print("="*80)

            print("\nResumen de UUIDs generados:")
            print("\nTipos de Miembro:")
            for codigo, uuid_val in tipos_miembro.items():
                print(f"  {codigo}: {uuid_val}")

            print("\nEstados de Miembro:")
            for codigo, uuid_val in estados_miembro.items():
                print(f"  {codigo}: {uuid_val}")

            print("\nEstados de Cuota:")
            for codigo, uuid_val in estados_cuota.items():
                print(f"  {codigo}: {uuid_val}")

            print("\nEstados de Campaña:")
            for codigo, uuid_val in estados_campania.items():
                print(f"  {codigo}: {uuid_val}")

            print("\nEstados de Actividad:")
            for codigo, uuid_val in estados_actividad.items():
                print(f"  {codigo}: {uuid_val}")

            print("\nEstados de Participante:")
            for codigo, uuid_val in estados_participante.items():
                print(f"  {codigo}: {uuid_val}")

            print("\n[OK] Todos los catálogos están listos para la importación de datos.\n")

        except Exception as e:
            await session.rollback()
            print(f"\n[X] ERROR: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
