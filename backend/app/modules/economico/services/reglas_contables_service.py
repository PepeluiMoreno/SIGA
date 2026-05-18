"""Servicio para gestión de reglas contables configurables."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.contabilidad import ReglaContable
from ..models.tesoreria import TipoApunte, OrigenApunte


class ReglasContablesService:
    """CRUD y consulta de reglas de generación automática de asientos."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_reglas(self, activas_solo: bool = False) -> List[ReglaContable]:
        query = select(ReglaContable)
        if activas_solo:
            query = query.where(ReglaContable.activa == True)
        query = query.order_by(ReglaContable.orden, ReglaContable.tipo_apunte)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def obtener_regla(self, regla_id: UUID) -> Optional[ReglaContable]:
        result = await self.session.execute(
            select(ReglaContable).where(ReglaContable.id == regla_id)
        )
        return result.scalars().first()

    async def crear_regla(
        self,
        tipo_apunte: str,
        cuenta_debe_codigo: str,
        cuenta_haber_codigo: str,
        origen: Optional[str] = None,
        descripcion: Optional[str] = None,
        orden: int = 10,
    ) -> ReglaContable:
        regla = ReglaContable(
            origen=origen,
            tipo_apunte=tipo_apunte,
            cuenta_debe_codigo=cuenta_debe_codigo,
            cuenta_haber_codigo=cuenta_haber_codigo,
            descripcion=descripcion,
            orden=orden,
        )
        self.session.add(regla)
        await self.session.commit()
        await self.session.refresh(regla)
        return regla

    async def actualizar_regla(self, regla_id: UUID, **kwargs) -> ReglaContable:
        regla = await self.obtener_regla(regla_id)
        if not regla:
            raise ValueError(f"Regla {regla_id} no encontrada")
        for key, value in kwargs.items():
            if hasattr(regla, key):
                setattr(regla, key, value)
        self.session.add(regla)
        await self.session.commit()
        await self.session.refresh(regla)
        return regla

    async def desactivar_regla(self, regla_id: UUID) -> ReglaContable:
        return await self.actualizar_regla(regla_id, activa=False)

    async def resolver_cuentas(
        self,
        tipo_apunte: str,
        origen: Optional[str] = None,
    ) -> Optional[tuple[str, str]]:
        """Busca la primera regla activa que coincida y devuelve (debe, haber)."""
        # Buscar por origen exacto primero, luego comodín (origen=NULL)
        for origen_busqueda in ([origen, None] if origen else [None]):
            query = (
                select(ReglaContable)
                .where(
                    and_(
                        ReglaContable.tipo_apunte == tipo_apunte,
                        ReglaContable.activa == True,
                        ReglaContable.origen == origen_busqueda,
                    )
                )
                .order_by(ReglaContable.orden)
                .limit(1)
            )
            result = await self.session.execute(query)
            regla = result.scalars().first()
            if regla:
                return (regla.cuenta_debe_codigo, regla.cuenta_haber_codigo)
        return None
