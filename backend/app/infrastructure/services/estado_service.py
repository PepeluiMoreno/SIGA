"""Servicio para gestionar cambios de estado de entidades."""

import logging
from typing import Optional, Type, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect

from ..base_model import BaseModel

logger = logging.getLogger(__name__)


class EstadoService:
    """Servicio genérico para gestionar cambios de estado."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def cambiar_estado(self, entidad, nuevo_estado_codigo: str,
                            usuario_id: Optional[str] = None, motivo: Optional[str] = None):
        """Cambia el estado de cualquier entidad que tenga un campo de estado."""
        from ...domains.core.models.estados import HistorialEstado
        import uuid

        # Obtener el tipo de entidad
        entidad_tipo = entidad.__class__.__name__.lower()

        # Buscar el campo de estado en la entidad
        estado_field = None
        mapper = inspect(entidad.__class__)

        for prop in mapper.attrs:
            if hasattr(prop, 'columns') and 'estado' in prop.key:
                estado_field = prop.key
                break

        if not estado_field:
            raise ValueError(f"La entidad {entidad_tipo} no tiene un campo de estado")

        # Obtener estado anterior
        estado_anterior = getattr(entidad, estado_field)
        estado_anterior_codigo = estado_anterior.codigo if estado_anterior else None

        # Buscar el nuevo estado
        estado_class = self._get_estado_class(entidad_tipo)
        if not estado_class:
            raise ValueError(f"No se encontró clase de estado para {entidad_tipo}")

        result = await self.session.execute(
            select(estado_class).where(estado_class.codigo == nuevo_estado_codigo)
        )
        nuevo_estado = result.scalar_one_or_none()

        if not nuevo_estado:
            raise ValueError(f"Estado {nuevo_estado_codigo} no encontrado para {entidad_tipo}")

        # Actualizar el estado
        setattr(entidad, estado_field, nuevo_estado)

        # Registrar en historial
        historial = HistorialEstado(
            id=uuid.uuid4(),
            entidad_tipo=entidad_tipo,
            entidad_id=str(entidad.id),
            estado_anterior_codigo=estado_anterior_codigo,
            estado_nuevo_codigo=nuevo_estado_codigo,
            usuario_id=usuario_id,
            motivo=motivo
        )
        self.session.add(historial)

        logger.info(f"Estado cambiado: {entidad_tipo}:{entidad.id} "
                   f"{estado_anterior_codigo}->{nuevo_estado_codigo}")

        return historial

    def _get_estado_class(self, entidad_tipo: str):
        """Obtiene la clase de estado correspondiente al tipo de entidad."""
        from ...domains.core.models import estados

        estado_mapping = {
            'cuotaanual': estados.EstadoCuota,
            'cuotaanio': estados.EstadoCuota,  # Alias
            'campania': estados.EstadoCampania,
            'tarea': estados.EstadoTarea,
            'tareagrupo': estados.EstadoTarea,  # Alias
            'participantecampania': estados.EstadoParticipante,
            'ordencobro': estados.EstadoOrdenCobro,
            'remesa': estados.EstadoRemesa,
            'remesasepa': estados.EstadoRemesa,  # Alias
            'donacion': estados.EstadoDonacion,
        }

        return estado_mapping.get(entidad_tipo)

    async def get_estados_disponibles(self, entidad_tipo: str, es_inicial: bool = False) -> List:
        """Obtiene todos los estados disponibles para un tipo de entidad."""
        estado_class = self._get_estado_class(entidad_tipo)
        if not estado_class:
            return []

        stmt = select(estado_class).where(estado_class.activo == True)

        if es_inicial:
            stmt = stmt.where(estado_class.es_inicial == True)

        stmt = stmt.order_by(estado_class.orden)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_estado_actual(self, entidad) -> Optional[str]:
        """Obtiene el código del estado actual de una entidad."""
        estado_field = None
        mapper = inspect(entidad.__class__)

        for prop in mapper.attrs:
            if hasattr(prop, 'columns') and 'estado' in prop.key:
                estado_field = prop.key
                break

        if estado_field:
            estado = getattr(entidad, estado_field)
            return estado.codigo if estado else None

        return None

    async def es_estado_final(self, entidad) -> bool:
        """Verifica si la entidad está en un estado final."""
        estado_field = None
        mapper = inspect(entidad.__class__)

        for prop in mapper.attrs:
            if hasattr(prop, 'columns') and 'estado' in prop.key:
                estado_field = prop.key
                break

        if estado_field:
            estado = getattr(entidad, estado_field)
            return estado.es_final if estado else False

        return False

    async def es_transicion_valida(self, entidad, nuevo_estado_codigo: str) -> bool:
        """Valida si una transición de estado es válida."""
        estado_actual = await self.get_estado_actual(entidad)
        if not estado_actual:
            return True  # Si no hay estado actual, cualquier transición es válida

        estado_class = self._get_estado_class(entidad.__class__.__name__.lower())
        if not estado_class:
            return False

        # Obtener el estado actual de la BD
        result_actual = await self.session.execute(
            select(estado_class).where(estado_class.codigo == estado_actual)
        )
        estado_actual_obj = result_actual.scalar_one_or_none()

        if not estado_actual_obj:
            return True

        # Obtener el nuevo estado
        result_nuevo = await self.session.execute(
            select(estado_class).where(estado_class.codigo == nuevo_estado_codigo)
        )
        nuevo_estado_obj = result_nuevo.scalar_one_or_none()

        if not nuevo_estado_obj:
            return False

        # Regla básica: no se puede cambiar desde un estado final
        if estado_actual_obj.es_final:
            return False

        # Regla básica: no se puede cambiar al mismo estado
        if estado_actual == nuevo_estado_codigo:
            return False

        return True
