"""Script para cargar datos mock en la base de datos usando mutaciones GraphQL."""

import asyncio
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.database import get_session
from ..domains import *


async def cargar_datos_geograficos():
    """Carga países, provincias y municipios básicos."""
    print("Cargando datos geográficos...")

    async for session in get_session():
        # España
        espana = Pais(
            codigo_iso="ES",
            nombre="España",
            codigo_telefono="+34",
            activo=True
        )
        session.add(espana)
        await session.commit()
        await session.refresh(espana)
        print(f"  Creado país: {espana.nombre} (ID: {espana.id})")

        # Provincias principales
        provincias_data = [
            ("28", "Madrid"),
            ("08", "Barcelona"),
            ("41", "Sevilla"),
            ("46", "Valencia"),
            ("29", "Málaga"),
        ]

        provincias = {}
        for codigo, nombre in provincias_data:
            provincia = Provincia(
                codigo_iso=codigo,
                nombre=nombre,
                pais_id=espana.id,
                activo=True
            )
            session.add(provincia)
            await session.commit()
            await session.refresh(provincia)
            provincias[nombre] = provincia.id
            print(f"  Creada provincia: {nombre} (ID: {provincia.id})")

        # Municipios ejemplo
        municipios_data = [
            ("28079", "Madrid", "Madrid"),
            ("08019", "Barcelona", "Barcelona"),
            ("41091", "Sevilla", "Sevilla"),
            ("46250", "Valencia", "Valencia"),
            ("29067", "Málaga", "Málaga"),
        ]

        for codigo, nombre, provincia_nombre in municipios_data:
            municipio = Municipio(
                codigo_ine=codigo,
                nombre=nombre,
                provincia_id=provincias[provincia_nombre],
                activo=True
            )
            session.add(municipio)
            await session.commit()
            await session.refresh(municipio)
            print(f"  Creado municipio: {nombre} (ID: {municipio.id})")

        # Agrupaciones territoriales
        agrupaciones_data = [
            ("AGR-MAD", "Agrupación Madrid", "LOCAL", provincias["Madrid"]),
            ("AGR-BCN", "Agrupación Barcelona", "LOCAL", provincias["Barcelona"]),
            ("AGR-AND", "Agrupación Andalucía", "REGIONAL", provincias["Sevilla"]),
        ]

        for codigo, nombre, tipo, provincia_id in agrupaciones_data:
            agrupacion = AgrupacionTerritorial(
                codigo=codigo,
                nombre=nombre,
                tipo=tipo,
                provincia_id=provincia_id,
                activo=True
            )
            session.add(agrupacion)
            await session.commit()
            await session.refresh(agrupacion)
            print(f"  Creada agrupación: {nombre} (ID: {agrupacion.id})")

    print("Datos geográficos cargados.\n")


async def cargar_tipos_catalogos():
    """Carga tipos y catálogos básicos."""
    print("Cargando tipos y catálogos...")

    async for session in get_session():
        # Tipos de miembro
        tipos_miembro_data = [
            ("SOCIO", "Socio", "Miembro con derecho a voto y cuota", True, True),
            ("SIMPATIZANTE", "Simpatizante", "Miembro sin derecho a voto", False, False),
            ("COLABORADOR", "Colaborador", "Miembro colaborador ocasional", False, False),
        ]

        for codigo, nombre, descripcion, requiere_cuota, puede_votar in tipos_miembro_data:
            tipo = TipoMiembro(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                requiere_cuota=requiere_cuota,
                puede_votar=puede_votar,
                activo=True
            )
            session.add(tipo)
            await session.commit()
            await session.refresh(tipo)
            print(f"  Creado tipo de miembro: {nombre} (ID: {tipo.id})")

        # Estados de cuota
        estados_cuota_data = [
            ("PENDIENTE", "Pendiente", "Cuota pendiente de pago"),
            ("PAGADA", "Pagada", "Cuota pagada"),
            ("VENCIDA", "Vencida", "Cuota vencida no pagada"),
            ("EXENTA", "Exenta", "Cuota exenta de pago"),
        ]

        for codigo, nombre, descripcion in estados_cuota_data:
            estado = EstadoCuota(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            print(f"  Creado estado de cuota: {nombre} (ID: {estado.id})")

        # Estados de campaña
        estados_campania_data = [
            ("PLANIFICACION", "En planificación", "Campaña en fase de planificación"),
            ("ACTIVA", "Activa", "Campaña en ejecución"),
            ("FINALIZADA", "Finalizada", "Campaña finalizada"),
            ("CANCELADA", "Cancelada", "Campaña cancelada"),
        ]

        for codigo, nombre, descripcion in estados_campania_data:
            estado = EstadoCampania(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            print(f"  Creado estado de campaña: {nombre} (ID: {estado.id})")

        # Estados de tarea
        estados_tarea_data = [
            ("PENDIENTE", "Pendiente", "Tarea pendiente de iniciar"),
            ("EN_CURSO", "En curso", "Tarea en ejecución"),
            ("COMPLETADA", "Completada", "Tarea completada"),
            ("BLOQUEADA", "Bloqueada", "Tarea bloqueada por dependencias"),
        ]

        for codigo, nombre, descripcion in estados_tarea_data:
            estado = EstadoTarea(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            print(f"  Creado estado de tarea: {nombre} (ID: {estado.id})")

        # Estados de participante
        estados_participante_data = [
            ("INVITADO", "Invitado", "Participante invitado"),
            ("CONFIRMADO", "Confirmado", "Participante confirmado"),
            ("ASISTIO", "Asistió", "Participante que asistió"),
            ("NO_ASISTIO", "No asistió", "Participante que no asistió"),
        ]

        for codigo, nombre, descripcion in estados_participante_data:
            estado = EstadoParticipante(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            print(f"  Creado estado de participante: {nombre} (ID: {estado.id})")

        # Estados de actividad
        estados_actividad_data = [
            ("PLANIFICADA", "Planificada", "Actividad planificada"),
            ("EN_CURSO", "En curso", "Actividad en ejecución"),
            ("COMPLETADA", "Completada", "Actividad completada"),
            ("CANCELADA", "Cancelada", "Actividad cancelada"),
        ]

        for codigo, nombre, descripcion in estados_actividad_data:
            estado = EstadoActividad(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            print(f"  Creado estado de actividad: {nombre} (ID: {estado.id})")

        # Estados de propuesta
        estados_propuesta_data = [
            ("BORRADOR", "Borrador", "Propuesta en borrador"),
            ("PRESENTADA", "Presentada", "Propuesta presentada para evaluación"),
            ("APROBADA", "Aprobada", "Propuesta aprobada"),
            ("RECHAZADA", "Rechazada", "Propuesta rechazada"),
        ]

        for codigo, nombre, descripcion in estados_propuesta_data:
            estado = EstadoPropuesta(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            print(f"  Creado estado de propuesta: {nombre} (ID: {estado.id})")

        # Tipos de grupo
        tipos_grupo_data = [
            ("TRABAJO", "Grupo de Trabajo", "Grupo de trabajo permanente"),
            ("PROYECTO", "Grupo de Proyecto", "Grupo temporal para un proyecto"),
            ("COMISION", "Comisión", "Comisión especializada"),
        ]

        for codigo, nombre, descripcion in tipos_grupo_data:
            tipo = TipoGrupo(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(tipo)
            await session.commit()
            await session.refresh(tipo)
            print(f"  Creado tipo de grupo: {nombre} (ID: {tipo.id})")

        # Roles de grupo
        roles_grupo_data = [
            ("COORDINADOR", "Coordinador", "Coordinador del grupo"),
            ("SECRETARIO", "Secretario", "Secretario del grupo"),
            ("MIEMBRO", "Miembro", "Miembro del grupo"),
        ]

        for codigo, nombre, descripcion in roles_grupo_data:
            rol = RolGrupo(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(rol)
            await session.commit()
            await session.refresh(rol)
            print(f"  Creado rol de grupo: {nombre} (ID: {rol.id})")

        # Tipos de campaña
        tipos_campania_data = [
            ("CAPTACION", "Captación", "Campaña de captación de miembros"),
            ("SENSIBILIZACION", "Sensibilización", "Campaña de sensibilización"),
            ("RECAUDACION", "Recaudación", "Campaña de recaudación de fondos"),
        ]

        for codigo, nombre, descripcion in tipos_campania_data:
            tipo = TipoCampania(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(tipo)
            await session.commit()
            await session.refresh(tipo)
            print(f"  Creado tipo de campaña: {nombre} (ID: {tipo.id})")

        # Tipos de actividad
        tipos_actividad_data = [
            ("FORMACION", "Formación", "Actividad de formación"),
            ("ACCION", "Acción directa", "Acción directa"),
            ("EVENTO", "Evento", "Evento público"),
            ("REUNION", "Reunión", "Reunión de trabajo"),
        ]

        for codigo, nombre, descripcion in tipos_actividad_data:
            tipo = TipoActividad(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(tipo)
            await session.commit()
            await session.refresh(tipo)
            print(f"  Creado tipo de actividad: {nombre} (ID: {tipo.id})")

        # Categorías de competencia
        categorias_competencia_data = [
            ("TECNICA", "Competencias técnicas", "Competencias técnicas y especializadas"),
            ("SOCIAL", "Competencias sociales", "Habilidades sociales y comunicación"),
            ("ORGANIZATIVA", "Competencias organizativas", "Capacidades de organización"),
        ]

        for codigo, nombre, descripcion in categorias_competencia_data:
            categoria = CategoriaCompetencia(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            session.add(categoria)
            await session.commit()
            await session.refresh(categoria)
            print(f"  Creada categoría de competencia: {nombre} (ID: {categoria.id})")

        # Niveles de competencia
        niveles_competencia_data = [
            ("BASICO", "Básico", 1),
            ("INTERMEDIO", "Intermedio", 2),
            ("AVANZADO", "Avanzado", 3),
            ("EXPERTO", "Experto", 4),
        ]

        for codigo, nombre, orden in niveles_competencia_data:
            nivel = NivelCompetencia(
                codigo=codigo,
                nombre=nombre,
                orden=orden,
                activo=True
            )
            session.add(nivel)
            await session.commit()
            await session.refresh(nivel)
            print(f"  Creado nivel de competencia: {nombre} (ID: {nivel.id})")

    print("Tipos y catálogos cargados.\n")


async def main():
    """Función principal para cargar todos los datos mock."""
    print("=" * 60)
    print("CARGANDO DATOS MOCK EN AIEL")
    print("=" * 60)
    print()

    try:
        await cargar_datos_geograficos()
        await cargar_tipos_catalogos()

        print("=" * 60)
        print("TODOS LOS DATOS MOCK HAN SIDO CARGADOS CORRECTAMENTE")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error al cargar datos mock: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
