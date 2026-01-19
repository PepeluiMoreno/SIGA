"""Servicio de auditoría y soft delete para async SQLAlchemy."""

import logging
from typing import Optional, Any
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..base_model import BaseModel

logger = logging.getLogger(__name__)


class AuditoriaService:
    """Servicio para gestionar auditoría y soft delete."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def soft_delete(self, entidad: BaseModel, usuario_id: Optional[str] = None) -> bool:
        """Realiza soft delete de cualquier entidad que herede de BaseModel."""
        try:
            entidad.soft_delete(usuario_id)
            await self.session.commit()

            # Registrar en log
            logger.info(f"Soft delete realizado en {entidad.__class__.__name__} "
                       f"id={entidad.id} por usuario_id={usuario_id}")

            return True
        except Exception as e:
            logger.error(f"Error en soft delete: {e}")
            await self.session.rollback()
            return False

    async def restore(self, entidad: BaseModel, usuario_id: Optional[str] = None) -> bool:
        """Restaura una entidad eliminada."""
        try:
            entidad.restore(usuario_id)
            await self.session.commit()

            logger.info(f"Restauración realizada en {entidad.__class__.__name__} "
                       f"id={entidad.id} por usuario_id={usuario_id}")

            return True
        except Exception as e:
            logger.error(f"Error en restore: {e}")
            await self.session.rollback()
            return False

    async def get_active_query(self, model_class, **filters):
        """Obtiene query filtrando por no eliminados."""
        # Construir la query base
        stmt = select(model_class).where(model_class.eliminado == False)

        # Aplicar filtros adicionales
        for key, value in filters.items():
            if hasattr(model_class, key):
                stmt = stmt.where(getattr(model_class, key) == value)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_deleted_query(self, model_class, **filters):
        """Obtiene query de registros eliminados."""
        # Construir la query base
        stmt = select(model_class).where(model_class.eliminado == True)

        # Aplicar filtros adicionales
        for key, value in filters.items():
            if hasattr(model_class, key):
                stmt = stmt.where(getattr(model_class, key) == value)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_with_deleted(self, model_class, record_id: str):
        """Obtiene un registro incluyendo si está eliminado."""
        result = await self.session.execute(
            select(model_class).where(model_class.id == record_id)
        )
        return result.scalar_one_or_none()

    async def registrar_cambio_estado(self, entidad, estado_anterior_codigo: Optional[str],
                                     estado_nuevo_codigo: str, usuario_id: Optional[str] = None,
                                     motivo: Optional[str] = None):
        """Registra cambios de estado en el historial."""
        from ...domains.core.models.estados import HistorialEstado
        import uuid

        historial = HistorialEstado(
            id=uuid.uuid4(),
            entidad_tipo=entidad.__class__.__name__.lower(),
            entidad_id=str(entidad.id),
            estado_anterior_codigo=estado_anterior_codigo,
            estado_nuevo_codigo=estado_nuevo_codigo,
            usuario_id=usuario_id,
            motivo=motivo
        )

        self.session.add(historial)
        await self.session.commit()

        logger.info(f"Cambio de estado registrado: {entidad.__class__.__name__}:{entidad.id} "
                   f"{estado_anterior_codigo} -> {estado_nuevo_codigo}")

        return historial


# Event listeners para async SQLAlchemy
# Nota: En async SQLAlchemy, los event listeners funcionan diferente
# Se pueden usar pero con consideraciones especiales para operaciones async
# Por ahora, manejamos la actualización de fecha_modificacion en el modelo BaseModel
