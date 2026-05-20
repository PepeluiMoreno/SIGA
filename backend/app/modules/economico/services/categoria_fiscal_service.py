"""Servicio para gestión de categorías fiscales (contabilidad simplificada)."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.contabilidad import CategoriaFiscal, TipoCategoriaFiscal


class CategoriaFiscalService:
    """CRUD de categorías fiscales: la estructura de clasificación del modo simplificado."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar(
        self,
        tipo: Optional[TipoCategoriaFiscal] = None,
        activas_solo: bool = True,
    ) -> List[CategoriaFiscal]:
        query = select(CategoriaFiscal).where(CategoriaFiscal.eliminado == False)
        if tipo:
            query = query.where(CategoriaFiscal.tipo == tipo)
        if activas_solo:
            query = query.where(CategoriaFiscal.activa == True)
        query = query.order_by(CategoriaFiscal.tipo, CategoriaFiscal.orden, CategoriaFiscal.nombre)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def obtener(self, categoria_id: UUID) -> Optional[CategoriaFiscal]:
        result = await self.session.execute(
            select(CategoriaFiscal).where(CategoriaFiscal.id == categoria_id)
        )
        return result.scalars().first()

    async def obtener_por_codigo(self, codigo: str) -> Optional[CategoriaFiscal]:
        result = await self.session.execute(
            select(CategoriaFiscal).where(CategoriaFiscal.codigo == codigo)
        )
        return result.scalars().first()

    async def crear(
        self,
        codigo: str,
        nombre: str,
        tipo: TipoCategoriaFiscal,
        descripcion: Optional[str] = None,
        computa_modelo_182: bool = False,
        computa_modelo_347: bool = False,
        casilla_modelo: Optional[str] = None,
        orden: int = 10,
        color: Optional[str] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> CategoriaFiscal:
        # Validar unicidad del código
        existente = await self.obtener_por_codigo(codigo)
        if existente:
            raise ValueError(f"Ya existe una categoría fiscal con código {codigo}")

        categoria = CategoriaFiscal(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            descripcion=descripcion,
            computa_modelo_182=computa_modelo_182,
            computa_modelo_347=computa_modelo_347,
            casilla_modelo=casilla_modelo,
            orden=orden,
            color=color,
            creado_por_id=creado_por_id,
        )
        self.session.add(categoria)
        await self.session.commit()
        await self.session.refresh(categoria)
        return categoria

    async def actualizar(self, categoria_id: UUID, **kwargs) -> CategoriaFiscal:
        categoria = await self.obtener(categoria_id)
        if not categoria:
            raise ValueError(f"Categoría fiscal {categoria_id} no encontrada")

        # Si se cambia el código, validar unicidad
        nuevo_codigo = kwargs.get("codigo")
        if nuevo_codigo and nuevo_codigo != categoria.codigo:
            otra = await self.obtener_por_codigo(nuevo_codigo)
            if otra:
                raise ValueError(f"Ya existe una categoría fiscal con código {nuevo_codigo}")

        for key, value in kwargs.items():
            if hasattr(categoria, key) and value is not None:
                setattr(categoria, key, value)

        self.session.add(categoria)
        await self.session.commit()
        await self.session.refresh(categoria)
        return categoria

    async def desactivar(self, categoria_id: UUID) -> CategoriaFiscal:
        return await self.actualizar(categoria_id, activa=False)

    async def eliminar(self, categoria_id: UUID) -> None:
        """Soft delete. No permite eliminar si tiene apuntes asociados."""
        categoria = await self.obtener(categoria_id)
        if not categoria:
            raise ValueError(f"Categoría fiscal {categoria_id} no encontrada")

        # Comprobar que no haya apuntes que la usen
        from ..models.tesoreria import ApunteCaja
        result = await self.session.execute(
            select(ApunteCaja).where(ApunteCaja.categoria_fiscal_id == categoria_id).limit(1)
        )
        if result.scalars().first():
            raise ValueError(
                "No se puede eliminar la categoría: tiene apuntes asociados. "
                "Desactívala en su lugar."
            )

        categoria.soft_delete()
        self.session.add(categoria)
        await self.session.commit()
