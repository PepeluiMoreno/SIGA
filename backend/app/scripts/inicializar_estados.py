"""Script para inicializar los estados del sistema."""

import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..domains.core.models import estados


# Definición de estados por defecto para cada tipo
ESTADOS_CUOTA = [
    {'codigo': 'PENDIENTE', 'nombre': 'Pendiente', 'descripcion': 'Cuota creada pero no cobrada', 'orden': 1, 'es_inicial': True, 'color': 'warning'},
    {'codigo': 'COBRADA', 'nombre': 'Cobrada', 'descripcion': 'Cuota cobrada exitosamente', 'orden': 2, 'es_final': True, 'color': 'success'},
    {'codigo': 'IMPAGADA', 'nombre': 'Impagada', 'descripcion': 'Intento de cobro fallido', 'orden': 3, 'color': 'danger'},
    {'codigo': 'ANULADA', 'nombre': 'Anulada', 'descripcion': 'Cuota anulada/cancelada', 'orden': 4, 'es_final': True, 'color': 'secondary'},
    {'codigo': 'EXENTA', 'nombre': 'Exenta', 'descripcion': 'Cuota exenta de pago', 'orden': 5, 'es_final': True, 'color': 'info'},
]

ESTADOS_CAMPANIA = [
    {'codigo': 'BORRADOR', 'nombre': 'Borrador', 'descripcion': 'Campaña en creación', 'orden': 1, 'es_inicial': True, 'color': 'secondary'},
    {'codigo': 'PROGRAMADA', 'nombre': 'Programada', 'descripcion': 'Campaña programada para envío', 'orden': 2, 'color': 'info'},
    {'codigo': 'EN_CURSO', 'nombre': 'En Curso', 'descripcion': 'Campaña activa/enviándose', 'orden': 3, 'color': 'primary'},
    {'codigo': 'PAUSADA', 'nombre': 'Pausada', 'descripcion': 'Campaña pausada temporalmente', 'orden': 4, 'color': 'warning'},
    {'codigo': 'FINALIZADA', 'nombre': 'Finalizada', 'descripcion': 'Campaña completada', 'orden': 5, 'es_final': True, 'color': 'success'},
    {'codigo': 'CANCELADA', 'nombre': 'Cancelada', 'descripcion': 'Campaña cancelada', 'orden': 6, 'es_final': True, 'color': 'danger'},
]

ESTADOS_TAREA = [
    {'codigo': 'PENDIENTE', 'nombre': 'Pendiente', 'descripcion': 'Tarea por hacer', 'orden': 1, 'es_inicial': True, 'color': 'secondary'},
    {'codigo': 'EN_PROGRESO', 'nombre': 'En Progreso', 'descripcion': 'Tarea en ejecución', 'orden': 2, 'color': 'primary'},
    {'codigo': 'BLOQUEADA', 'nombre': 'Bloqueada', 'descripcion': 'Tarea bloqueada por dependencias', 'orden': 3, 'color': 'warning'},
    {'codigo': 'COMPLETADA', 'nombre': 'Completada', 'descripcion': 'Tarea finalizada', 'orden': 4, 'es_final': True, 'color': 'success'},
    {'codigo': 'CANCELADA', 'nombre': 'Cancelada', 'descripcion': 'Tarea cancelada', 'orden': 5, 'es_final': True, 'color': 'danger'},
]

ESTADOS_PARTICIPANTE = [
    {'codigo': 'INCLUIDO', 'nombre': 'Incluido', 'descripcion': 'Participante añadido a la campaña', 'orden': 1, 'es_inicial': True, 'color': 'info'},
    {'codigo': 'ENVIADO', 'nombre': 'Enviado', 'descripcion': 'Comunicación enviada', 'orden': 2, 'color': 'primary'},
    {'codigo': 'ENTREGADO', 'nombre': 'Entregado', 'descripcion': 'Comunicación entregada', 'orden': 3, 'color': 'primary'},
    {'codigo': 'LEIDO', 'nombre': 'Leído', 'descripcion': 'Comunicación leída/abierta', 'orden': 4, 'color': 'success'},
    {'codigo': 'RESPONDIDO', 'nombre': 'Respondido', 'descripcion': 'Participante respondió', 'orden': 5, 'es_final': True, 'color': 'success'},
    {'codigo': 'REBOTADO', 'nombre': 'Rebotado', 'descripcion': 'Comunicación rebotada', 'orden': 6, 'es_final': True, 'color': 'danger'},
    {'codigo': 'EXCLUIDO', 'nombre': 'Excluido', 'descripcion': 'Participante excluido de la campaña', 'orden': 7, 'es_final': True, 'color': 'secondary'},
]

ESTADOS_ORDEN_COBRO = [
    {'codigo': 'PENDIENTE', 'nombre': 'Pendiente', 'descripcion': 'Orden creada, pendiente de procesar', 'orden': 1, 'es_inicial': True, 'color': 'warning'},
    {'codigo': 'PROCESADA', 'nombre': 'Procesada', 'descripcion': 'Orden procesada, cobro realizado', 'orden': 2, 'es_final': True, 'color': 'success'},
    {'codigo': 'FALLIDA', 'nombre': 'Fallida', 'descripcion': 'Cobro fallido', 'orden': 3, 'es_final': True, 'color': 'danger'},
    {'codigo': 'ANULADA', 'nombre': 'Anulada', 'descripcion': 'Orden anulada', 'orden': 4, 'es_final': True, 'color': 'secondary'},
]

ESTADOS_REMESA = [
    {'codigo': 'BORRADOR', 'nombre': 'Borrador', 'descripcion': 'Remesa en creación', 'orden': 1, 'es_inicial': True, 'color': 'secondary'},
    {'codigo': 'GENERADA', 'nombre': 'Generada', 'descripcion': 'Remesa generada, pendiente de envío', 'orden': 2, 'color': 'info'},
    {'codigo': 'ENVIADA', 'nombre': 'Enviada', 'descripcion': 'Remesa enviada al banco', 'orden': 3, 'color': 'primary'},
    {'codigo': 'PROCESADA', 'nombre': 'Procesada', 'descripcion': 'Remesa procesada por el banco', 'orden': 4, 'es_final': True, 'color': 'success'},
    {'codigo': 'PARCIAL', 'nombre': 'Parcial', 'descripcion': 'Remesa procesada parcialmente', 'orden': 5, 'es_final': True, 'color': 'warning'},
    {'codigo': 'RECHAZADA', 'nombre': 'Rechazada', 'descripcion': 'Remesa rechazada', 'orden': 6, 'es_final': True, 'color': 'danger'},
]

ESTADOS_DONACION = [
    {'codigo': 'PENDIENTE', 'nombre': 'Pendiente', 'descripcion': 'Donación prometida pero no recibida', 'orden': 1, 'es_inicial': True, 'color': 'warning'},
    {'codigo': 'RECIBIDA', 'nombre': 'Recibida', 'descripcion': 'Donación recibida', 'orden': 2, 'color': 'success'},
    {'codigo': 'CERTIFICADA', 'nombre': 'Certificada', 'descripcion': 'Certificado de donación emitido', 'orden': 3, 'es_final': True, 'color': 'success'},
    {'codigo': 'ANULADA', 'nombre': 'Anulada', 'descripcion': 'Donación anulada', 'orden': 4, 'es_final': True, 'color': 'danger'},
]


async def inicializar_estados_cuota(session: AsyncSession) -> None:
    """Inicializa los estados de cuotas."""
    for estado_data in ESTADOS_CUOTA:
        result = await session.execute(
            select(estados.EstadoCuota).where(estados.EstadoCuota.codigo == estado_data['codigo'])
        )
        existe = result.scalar_one_or_none()

        if not existe:
            estado = estados.EstadoCuota(
                id=uuid.uuid4(),
                **estado_data
            )
            session.add(estado)
            print(f"  * Estado cuota creado: {estado_data['codigo']}")
        else:
            print(f"  - Estado cuota ya existe: {estado_data['codigo']}")


async def inicializar_estados_campania(session: AsyncSession) -> None:
    """Inicializa los estados de campañas."""
    for estado_data in ESTADOS_CAMPANIA:
        result = await session.execute(
            select(estados.EstadoCampania).where(estados.EstadoCampania.codigo == estado_data['codigo'])
        )
        existe = result.scalar_one_or_none()

        if not existe:
            estado = estados.EstadoCampania(
                id=uuid.uuid4(),
                **estado_data
            )
            session.add(estado)
            print(f"  * Estado campaña creado: {estado_data['codigo']}")
        else:
            print(f"  - Estado campaña ya existe: {estado_data['codigo']}")


async def inicializar_estados_tarea(session: AsyncSession) -> None:
    """Inicializa los estados de tareas."""
    for estado_data in ESTADOS_TAREA:
        result = await session.execute(
            select(estados.EstadoTarea).where(estados.EstadoTarea.codigo == estado_data['codigo'])
        )
        existe = result.scalar_one_or_none()

        if not existe:
            estado = estados.EstadoTarea(
                id=uuid.uuid4(),
                **estado_data
            )
            session.add(estado)
            print(f"  * Estado tarea creado: {estado_data['codigo']}")
        else:
            print(f"  - Estado tarea ya existe: {estado_data['codigo']}")


async def inicializar_estados_participante(session: AsyncSession) -> None:
    """Inicializa los estados de participantes."""
    for estado_data in ESTADOS_PARTICIPANTE:
        result = await session.execute(
            select(estados.EstadoParticipante).where(estados.EstadoParticipante.codigo == estado_data['codigo'])
        )
        existe = result.scalar_one_or_none()

        if not existe:
            estado = estados.EstadoParticipante(
                id=uuid.uuid4(),
                **estado_data
            )
            session.add(estado)
            print(f"  * Estado participante creado: {estado_data['codigo']}")
        else:
            print(f"  - Estado participante ya existe: {estado_data['codigo']}")


async def inicializar_estados_orden_cobro(session: AsyncSession) -> None:
    """Inicializa los estados de órdenes de cobro."""
    for estado_data in ESTADOS_ORDEN_COBRO:
        result = await session.execute(
            select(estados.EstadoOrdenCobro).where(estados.EstadoOrdenCobro.codigo == estado_data['codigo'])
        )
        existe = result.scalar_one_or_none()

        if not existe:
            estado = estados.EstadoOrdenCobro(
                id=uuid.uuid4(),
                **estado_data
            )
            session.add(estado)
            print(f"  * Estado orden cobro creado: {estado_data['codigo']}")
        else:
            print(f"  - Estado orden cobro ya existe: {estado_data['codigo']}")


async def inicializar_estados_remesa(session: AsyncSession) -> None:
    """Inicializa los estados de remesas."""
    for estado_data in ESTADOS_REMESA:
        result = await session.execute(
            select(estados.EstadoRemesa).where(estados.EstadoRemesa.codigo == estado_data['codigo'])
        )
        existe = result.scalar_one_or_none()

        if not existe:
            estado = estados.EstadoRemesa(
                id=uuid.uuid4(),
                **estado_data
            )
            session.add(estado)
            print(f"  * Estado remesa creado: {estado_data['codigo']}")
        else:
            print(f"  - Estado remesa ya existe: {estado_data['codigo']}")


async def inicializar_estados_donacion(session: AsyncSession) -> None:
    """Inicializa los estados de donaciones."""
    for estado_data in ESTADOS_DONACION:
        result = await session.execute(
            select(estados.EstadoDonacion).where(estados.EstadoDonacion.codigo == estado_data['codigo'])
        )
        existe = result.scalar_one_or_none()

        if not existe:
            estado = estados.EstadoDonacion(
                id=uuid.uuid4(),
                **estado_data
            )
            session.add(estado)
            print(f"  * Estado donación creado: {estado_data['codigo']}")
        else:
            print(f"  - Estado donación ya existe: {estado_data['codigo']}")


async def inicializar_estados(session: AsyncSession) -> None:
    """Inicializa todos los estados del sistema."""
    print("\n=== Inicializando Estados del Sistema ===\n")

    print("1. Estados de Cuotas:")
    await inicializar_estados_cuota(session)

    print("\n2. Estados de Campañas:")
    await inicializar_estados_campania(session)

    print("\n3. Estados de Tareas:")
    await inicializar_estados_tarea(session)

    print("\n4. Estados de Participantes:")
    await inicializar_estados_participante(session)

    print("\n5. Estados de Órdenes de Cobro:")
    await inicializar_estados_orden_cobro(session)

    print("\n6. Estados de Remesas:")
    await inicializar_estados_remesa(session)

    print("\n7. Estados de Donaciones:")
    await inicializar_estados_donacion(session)

    await session.commit()
    print("\n=== Estados inicializados correctamente ===\n")


# Función main para ejecutar el script directamente
async def main():
    """Función principal para ejecutar el script."""
    from ..infrastructure.database import get_session

    async with get_session() as session:
        await inicializar_estados(session)


if __name__ == "__main__":
    asyncio.run(main())
