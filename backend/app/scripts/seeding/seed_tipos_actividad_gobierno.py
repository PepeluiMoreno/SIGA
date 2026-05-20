"""Seed: tipos de actividad para reuniones de gobierno.

Amplía el catálogo tipos_accion con los cuatro tipos correspondientes
a actividades de secretaría y presidencia (asambleas, juntas, comisiones),
vinculándolos a sus TipoReunion de secretaría.

El mapeo a cuentas contables PCESFL se establece mediante reglas en
la tabla ReglaContableActividad — pendiente de implementar en la PR
feature/reglas-contables-actividades.
"""

import uuid
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.actividades.models.actividad import TipoActividad
from app.modules.secretaria.models.reunion import TipoReunion


# UUIDs fijos para idempotencia y referencias cruzadas
_ID_ASAMBLEA_ORDINARIA   = uuid.UUID('33333333-sec1-0000-0000-000000000001')
_ID_ASAMBLEA_EXTRAORDINARIA = uuid.UUID('33333333-sec1-0000-0000-000000000002')
_ID_JUNTA_DIRECTIVA      = uuid.UUID('33333333-sec1-0000-0000-000000000003')
_ID_COMISION_TRABAJO     = uuid.UUID('33333333-sec1-0000-0000-000000000004')

TIPOS_GOBIERNO = [
    {
        'id': _ID_ASAMBLEA_ORDINARIA,
        'nombre': 'Asamblea General Ordinaria',
        'descripcion': 'Asamblea anual de socios — órgano soberano de la asociación (Ley 1/2002)',
        'tiene_lugar': True,
        'tiene_participantes': True,
        'es_actividad_gobierno': True,
        'tipo_reunion_nombre': 'Asamblea General Ordinaria',
        # Recurrente anual — la plantilla se crea con es_recurrente=True, periodicidad='anual'
        'es_recurrente': True,
        'periodicidad': 'anual',
    },
    {
        'id': _ID_ASAMBLEA_EXTRAORDINARIA,
        'nombre': 'Asamblea General Extraordinaria',
        'descripcion': 'Asamblea convocada fuera del calendario ordinario para asuntos urgentes',
        'tiene_lugar': True,
        'tiene_participantes': True,
        'es_actividad_gobierno': True,
        'tipo_reunion_nombre': 'Asamblea General Extraordinaria',
        'es_recurrente': False,
        'periodicidad': None,
    },
    {
        'id': _ID_JUNTA_DIRECTIVA,
        'nombre': 'Reunión de Junta Directiva',
        'descripcion': 'Reunión del órgano de representación y gestión de la asociación',
        'tiene_lugar': True,
        'tiene_participantes': True,
        'es_actividad_gobierno': True,
        'tipo_reunion_nombre': 'Reunión de Junta Directiva',
        'es_recurrente': True,
        'periodicidad': 'mensual',        # Periodicidad habitual; se ajusta por instancia
    },
    {
        'id': _ID_COMISION_TRABAJO,
        'nombre': 'Reunión de Comisión',
        'descripcion': 'Reunión de comisiones delegadas de la Junta Directiva',
        'tiene_lugar': True,
        'tiene_participantes': True,
        'es_actividad_gobierno': True,
        'tipo_reunion_nombre': 'Comisión de Trabajo',
        'es_recurrente': False,
        'periodicidad': None,
    },
]


async def seed_tipos_actividad_gobierno(session: AsyncSession) -> None:
    """Crea o actualiza los tipos de actividad de gobierno. Idempotente."""

    # Cargar tipos de reunión para establecer FK
    tipos_reunion_result = await session.execute(select(TipoReunion))
    tipos_reunion: dict[str, uuid.UUID] = {
        tr.nombre: tr.id for tr in tipos_reunion_result.scalars().all()
    }

    creados = 0
    actualizados = 0

    for datos in TIPOS_GOBIERNO:
        tipo_reunion_id = tipos_reunion.get(datos['tipo_reunion_nombre'])

        existente = await session.execute(
            select(TipoActividad).where(TipoActividad.id == datos['id'])
        )
        tipo = existente.scalars().first()

        if tipo is None:
            # Crear nuevo
            tipo = TipoActividad(
                id=datos['id'],
                nombre=datos['nombre'],
                descripcion=datos['descripcion'],
                tiene_lugar=datos['tiene_lugar'],
                tiene_participantes=datos['tiene_participantes'],
                es_actividad_gobierno=datos['es_actividad_gobierno'],
                tipo_reunion_secretaria_id=tipo_reunion_id,
                activo=True,
            )
            session.add(tipo)
            creados += 1
        else:
            # Actualizar campos contables si ya existe
            tipo.es_actividad_gobierno = True
            if tipo_reunion_id:
                tipo.tipo_reunion_secretaria_id = tipo_reunion_id
            actualizados += 1

    await session.commit()
    print(f"[tipos_actividad_gobierno] {creados} creados, {actualizados} actualizados")
