"""Servicio CRUD de reglas de categorización por concepto."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.contabilidad import ReglaCategorizacion, TipoCoincidencia


class ReglaCategorizacionService:
    """Gestión de las reglas de autoclasificación de apuntes por concepto."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar(self, activas_solo: bool = False) -> List[ReglaCategorizacion]:
        query = select(ReglaCategorizacion).where(ReglaCategorizacion.eliminado == False)
        if activas_solo:
            query = query.where(ReglaCategorizacion.activa == True)
        query = query.order_by(ReglaCategorizacion.orden, ReglaCategorizacion.patron)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def obtener(self, regla_id: UUID) -> Optional[ReglaCategorizacion]:
        result = await self.session.execute(
            select(ReglaCategorizacion).where(ReglaCategorizacion.id == regla_id)
        )
        return result.scalars().first()

    async def crear(
        self,
        patron: str,
        categoria_fiscal_id: UUID,
        tipo_coincidencia: TipoCoincidencia = TipoCoincidencia.CONTIENE,
        tipo_apunte: Optional[str] = None,
        orden: int = 10,
        descripcion: Optional[str] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> ReglaCategorizacion:
        if not patron or not patron.strip():
            raise ValueError("El patrón no puede estar vacío")
        regla = ReglaCategorizacion(
            patron=patron.strip(),
            tipo_coincidencia=tipo_coincidencia,
            tipo_apunte=tipo_apunte,
            categoria_fiscal_id=categoria_fiscal_id,
            orden=orden,
            descripcion=descripcion,
            creado_por_id=creado_por_id,
        )
        self.session.add(regla)
        await self.session.commit()
        await self.session.refresh(regla)
        return regla

    async def actualizar(self, regla_id: UUID, **kwargs) -> ReglaCategorizacion:
        regla = await self.obtener(regla_id)
        if not regla:
            raise ValueError(f"Regla {regla_id} no encontrada")
        for key, value in kwargs.items():
            if hasattr(regla, key) and value is not None:
                setattr(regla, key, value)
        self.session.add(regla)
        await self.session.commit()
        await self.session.refresh(regla)
        return regla

    async def eliminar(self, regla_id: UUID) -> None:
        regla = await self.obtener(regla_id)
        if not regla:
            raise ValueError(f"Regla {regla_id} no encontrada")
        regla.soft_delete()
        self.session.add(regla)
        await self.session.commit()
