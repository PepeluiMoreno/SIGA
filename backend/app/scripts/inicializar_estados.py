"""Script para inicializar los estados del sistema."""

import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..modules.configuracion.models.estados import (
    EstadoCuota, EstadoCampania, EstadoTarea, EstadoParticipante,
    EstadoOrdenCobro, EstadoRemesa, EstadoDonacion, EstadoNotificacion,
    EstadoReunion, EstadoActa, EstadoEjecucionAcuerdo,
)


ESTADOS_CUOTA = [
    {'nombre': 'Pendiente',  'descripcion': 'Cuota creada pero no cobrada',       'orden': 1, 'es_inicial': True,  'color': 'warning'},
    {'nombre': 'Cobrada',    'descripcion': 'Cuota cobrada exitosamente',          'orden': 2, 'es_final': True,   'color': 'success'},
    {'nombre': 'Impagada',   'descripcion': 'Intento de cobro fallido',            'orden': 3,                     'color': 'danger'},
    {'nombre': 'Anulada',    'descripcion': 'Cuota anulada/cancelada',             'orden': 4, 'es_final': True,   'color': 'secondary'},
    {'nombre': 'Exenta',     'descripcion': 'Cuota exenta de pago',                'orden': 5, 'es_final': True,   'color': 'info'},
]

ESTADOS_CAMPANIA = [
    {'nombre': 'Borrador',    'descripcion': 'Campaña en creación',                'orden': 1, 'es_inicial': True,  'color': 'secondary'},
    {'nombre': 'Programada',  'descripcion': 'Campaña programada para envío',      'orden': 2,                      'color': 'info'},
    {'nombre': 'En Curso',    'descripcion': 'Campaña activa/enviándose',           'orden': 3,                      'color': 'primary'},
    {'nombre': 'Pausada',     'descripcion': 'Campaña pausada temporalmente',       'orden': 4,                      'color': 'warning'},
    {'nombre': 'Finalizada',  'descripcion': 'Campaña completada',                 'orden': 5, 'es_final': True,   'color': 'success'},
    {'nombre': 'Cancelada',   'descripcion': 'Campaña cancelada',                  'orden': 6, 'es_final': True,   'color': 'danger'},
]

ESTADOS_TAREA = [
    {'nombre': 'Pendiente',   'descripcion': 'Tarea por hacer',                    'orden': 1, 'es_inicial': True,  'color': 'secondary'},
    {'nombre': 'En Progreso', 'descripcion': 'Tarea en ejecución',                 'orden': 2,                      'color': 'primary'},
    {'nombre': 'Bloqueada',   'descripcion': 'Tarea bloqueada por dependencias',   'orden': 3,                      'color': 'warning'},
    {'nombre': 'Completada',  'descripcion': 'Tarea finalizada',                   'orden': 4, 'es_final': True,   'color': 'success'},
    {'nombre': 'Cancelada',   'descripcion': 'Tarea cancelada',                    'orden': 5, 'es_final': True,   'color': 'danger'},
]

ESTADOS_PARTICIPANTE = [
    {'nombre': 'Incluido',    'descripcion': 'Participante añadido a la campaña',  'orden': 1, 'es_inicial': True,  'color': 'info'},
    {'nombre': 'Enviado',     'descripcion': 'Comunicación enviada',               'orden': 2,                      'color': 'primary'},
    {'nombre': 'Entregado',   'descripcion': 'Comunicación entregada',             'orden': 3,                      'color': 'primary'},
    {'nombre': 'Leído',       'descripcion': 'Comunicación leída/abierta',         'orden': 4,                      'color': 'success'},
    {'nombre': 'Respondido',  'descripcion': 'Participante respondió',             'orden': 5, 'es_final': True,   'color': 'success'},
    {'nombre': 'Rebotado',    'descripcion': 'Comunicación rebotada',              'orden': 6, 'es_final': True,   'color': 'danger'},
    {'nombre': 'Excluido',    'descripcion': 'Participante excluido de la campaña','orden': 7, 'es_final': True,   'color': 'secondary'},
]

ESTADOS_ORDEN_COBRO = [
    {'nombre': 'Pendiente',   'descripcion': 'Orden creada, pendiente de procesar','orden': 1, 'es_inicial': True,  'color': 'warning'},
    {'nombre': 'Procesada',   'descripcion': 'Orden procesada, cobro realizado',   'orden': 2, 'es_final': True,   'color': 'success'},
    {'nombre': 'Fallida',     'descripcion': 'Cobro fallido',                      'orden': 3, 'es_final': True,   'color': 'danger'},
    {'nombre': 'Anulada',     'descripcion': 'Orden anulada',                      'orden': 4, 'es_final': True,   'color': 'secondary'},
]

ESTADOS_REMESA = [
    {'nombre': 'Borrador',    'descripcion': 'Remesa en creación',                 'orden': 1, 'es_inicial': True,  'color': 'secondary'},
    {'nombre': 'Generada',    'descripcion': 'Remesa generada, pendiente de envío','orden': 2,                      'color': 'info'},
    {'nombre': 'Enviada',     'descripcion': 'Remesa enviada al banco',            'orden': 3,                      'color': 'primary'},
    {'nombre': 'Procesada',   'descripcion': 'Remesa procesada por el banco',      'orden': 4, 'es_final': True,   'color': 'success'},
    {'nombre': 'Parcial',     'descripcion': 'Remesa procesada parcialmente',      'orden': 5, 'es_final': True,   'color': 'warning'},
    {'nombre': 'Rechazada',   'descripcion': 'Remesa rechazada',                   'orden': 6, 'es_final': True,   'color': 'danger'},
]

ESTADOS_DONACION = [
    {'nombre': 'Pendiente',   'descripcion': 'Donación prometida pero no recibida','orden': 1, 'es_inicial': True,  'color': 'warning'},
    {'nombre': 'Recibida',    'descripcion': 'Donación recibida',                  'orden': 2,                      'color': 'success'},
    {'nombre': 'Certificada', 'descripcion': 'Certificado de donación emitido',    'orden': 3, 'es_final': True,   'color': 'success'},
    {'nombre': 'Anulada',     'descripcion': 'Donación anulada',                   'orden': 4, 'es_final': True,   'color': 'danger'},
]


ESTADOS_REUNION = [
    {'nombre': 'Convocada',     'codigo': 'CONVOCADA',     'descripcion': 'Reunión convocada pendiente de celebración', 'orden': 1, 'es_inicial': True,  'color': '#3b82f6'},
    {'nombre': 'Celebrada',     'codigo': 'CELEBRADA',     'descripcion': 'Reunión celebrada, pendiente de acta',       'orden': 2,                      'color': '#f59e0b'},
    {'nombre': 'Acta borrador', 'codigo': 'ACTA_BORRADOR', 'descripcion': 'Acta redactada pendiente de aprobación',     'orden': 3,                      'color': '#f97316'},
    {'nombre': 'Acta aprobada', 'codigo': 'ACTA_APROBADA', 'descripcion': 'Acta aprobada en la siguiente reunión',      'orden': 4, 'es_final': True,   'color': '#22c55e'},
    {'nombre': 'Cancelada',     'codigo': 'CANCELADA',     'descripcion': 'Reunión cancelada',                          'orden': 5, 'es_final': True,   'color': '#6b7280'},
]

ESTADOS_ACTA = [
    {'nombre': 'Borrador', 'codigo': 'BORRADOR', 'descripcion': 'Acta en redacción, pendiente de aprobación', 'orden': 1, 'es_inicial': True,  'color': '#f97316'},
    {'nombre': 'Aprobada', 'codigo': 'APROBADA', 'descripcion': 'Acta aprobada en reunión posterior',          'orden': 2,                      'color': '#6366f1'},
    {'nombre': 'Firmada',  'codigo': 'FIRMADA',  'descripcion': 'Acta firmada por secretario y presidente',    'orden': 3, 'es_final': True,   'color': '#22c55e'},
]

ESTADOS_EJECUCION_ACUERDO = [
    {'nombre': 'Pendiente',   'codigo': 'PENDIENTE',   'descripcion': 'Acuerdo adoptado pendiente de ejecutar', 'orden': 1, 'es_inicial': True,  'color': '#f59e0b'},
    {'nombre': 'En curso',    'codigo': 'EN_CURSO',    'descripcion': 'Ejecución en marcha',                    'orden': 2,                      'color': '#3b82f6'},
    {'nombre': 'Completado',  'codigo': 'COMPLETADO',  'descripcion': 'Acuerdo ejecutado satisfactoriamente',   'orden': 3, 'es_final': True,   'color': '#22c55e'},
    {'nombre': 'Archivado',   'codigo': 'ARCHIVADO',   'descripcion': 'Acuerdo archivado sin ejecución',        'orden': 4, 'es_final': True,   'color': '#6b7280'},
]


def _upsert(model_class, data_list):
    """Genera pares (filtro, datos) para cada estado."""
    return [(model_class.nombre == d['nombre'], d) for d in data_list]


async def _seed_estados(session, model_class, data_list, label):
    for filtro, data in _upsert(model_class, data_list):
        existe = (await session.execute(select(model_class).where(filtro))).scalar_one_or_none()
        if not existe:
            session.add(model_class(id=uuid.uuid4(), **data))
            print(f"  + {data['nombre']}")


async def inicializar_estados(session: AsyncSession) -> None:
    print("\n=== Inicializando Estados del Sistema ===\n")
    await _seed_estados(session, estados.EstadoCuota,      ESTADOS_CUOTA,        "Cuotas")
    await _seed_estados(session, estados.EstadoCampania,   ESTADOS_CAMPANIA,     "Campañas")
    await _seed_estados(session, estados.EstadoTarea,      ESTADOS_TAREA,        "Tareas")
    await _seed_estados(session, estados.EstadoParticipante, ESTADOS_PARTICIPANTE, "Participantes")
    await _seed_estados(session, estados.EstadoOrdenCobro, ESTADOS_ORDEN_COBRO,  "Órdenes cobro")
    await _seed_estados(session, estados.EstadoRemesa,     ESTADOS_REMESA,       "Remesas")
    await _seed_estados(session, estados.EstadoDonacion,   ESTADOS_DONACION,     "Donaciones")
    await session.commit()
    print("\n=== Estados inicializados ===\n")


async def main():
    from app.core.database import async_session
    async with async_session() as session:
        await inicializar_estados(session)


if __name__ == "__main__":
    asyncio.run(main())
