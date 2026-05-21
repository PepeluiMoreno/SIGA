"""Servicio de categorización de apuntes de caja (contabilidad simplificada).

Combina tres mecanismos para minimizar la clasificación manual:
  1. Derivación por origen — apuntes de cuotas/donaciones/etc. se clasifican solos
  2. Reglas por concepto — patrones configurables ("Endesa" → Suministros)
  3. Clasificación masiva — asignar categoría a varios apuntes a la vez
"""

from typing import List, Optional, Dict
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.tesoreria import ApunteCaja, TipoApunte, OrigenApunte
from ..models.contabilidad import CategoriaFiscal, ReglaCategorizacion


# Mapeo de origen del apunte → código de categoría fiscal (derivación automática #1).
# Si el apunte tiene uno de estos orígenes, su categoría se deduce sin intervención.
_ORIGEN_A_CATEGORIA: Dict[str, str] = {
    "CUOTA": "ING_CUOTAS",
    "DONACION": "ING_DONATIVOS",
    "REMESA": "ING_CUOTAS",            # las remesas suelen ser cobro de cuotas
    "PAYPAL": "ING_CUOTAS",
    "JUSTIFICANTE_GASTO": "GAS_OTROS", # gasto justificado; el detalle se afina por regla/manual
}


class CategorizacionService:
    """Resuelve y aplica la categoría fiscal de los apuntes de caja."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Resolución de categoría ────────────────────────────────────────────────

    async def _categoria_por_codigo(self, codigo: str) -> Optional[CategoriaFiscal]:
        result = await self.session.execute(
            select(CategoriaFiscal).where(
                and_(CategoriaFiscal.codigo == codigo, CategoriaFiscal.activa == True)
            )
        )
        return result.scalars().first()

    async def resolver_categoria(self, apunte: ApunteCaja) -> Optional[UUID]:
        """Determina la categoría fiscal de un apunte sin guardarla.

        Orden: derivación por origen → reglas por concepto → None (sin clasificar).
        """
        # 1. Derivación por origen
        origen = apunte.origen.value if apunte.origen else None
        if origen and origen in _ORIGEN_A_CATEGORIA:
            cat = await self._categoria_por_codigo(_ORIGEN_A_CATEGORIA[origen])
            if cat:
                return cat.id

        # 2. Reglas por concepto (primera que coincide, por orden)
        tipo_str = apunte.tipo.value if apunte.tipo else None
        reglas_result = await self.session.execute(
            select(ReglaCategorizacion)
            .where(ReglaCategorizacion.activa == True)
            .order_by(ReglaCategorizacion.orden)
        )
        for regla in reglas_result.scalars().all():
            if regla.coincide(apunte.concepto or "", tipo_str):
                return regla.categoria_fiscal_id

        # 3. Sin clasificar
        return None

    async def clasificar_apunte(self, apunte: ApunteCaja, forzar: bool = False) -> Optional[UUID]:
        """Resuelve y asigna la categoría a un apunte. No sobrescribe si ya tiene
        categoría, salvo forzar=True. Devuelve la categoría asignada (o la existente)."""
        if apunte.categoria_fiscal_id and not forzar:
            return apunte.categoria_fiscal_id
        categoria_id = await self.resolver_categoria(apunte)
        if categoria_id:
            apunte.categoria_fiscal_id = categoria_id
            self.session.add(apunte)
        return categoria_id

    # ── Clasificación masiva ────────────────────────────────────────────────────

    async def clasificar_pendientes(
        self,
        ejercicio: Optional[int] = None,
        forzar: bool = False,
    ) -> Dict[str, int]:
        """Aplica derivación + reglas a todos los apuntes sin clasificar (o a todos si forzar).

        Devuelve {'procesados': n, 'clasificados': m}.
        """
        query = select(ApunteCaja).where(ApunteCaja.eliminado == False)
        if not forzar:
            query = query.where(ApunteCaja.categoria_fiscal_id.is_(None))
        if ejercicio:
            from sqlalchemy import extract
            query = query.where(extract("year", ApunteCaja.fecha) == ejercicio)

        result = await self.session.execute(query)
        apuntes = list(result.scalars().all())

        clasificados = 0
        for apunte in apuntes:
            categoria_id = await self.resolver_categoria(apunte)
            if categoria_id and categoria_id != apunte.categoria_fiscal_id:
                apunte.categoria_fiscal_id = categoria_id
                self.session.add(apunte)
                clasificados += 1

        await self.session.commit()
        return {"procesados": len(apuntes), "clasificados": clasificados}

    async def asignar_categoria_masiva(
        self,
        apunte_ids: List[UUID],
        categoria_fiscal_id: UUID,
    ) -> int:
        """Asigna una categoría concreta a un lote de apuntes seleccionados.
        Devuelve el número de apuntes actualizados."""
        if not apunte_ids:
            return 0
        # Validar que la categoría existe
        cat = await self.session.execute(
            select(CategoriaFiscal).where(CategoriaFiscal.id == categoria_fiscal_id)
        )
        if not cat.scalars().first():
            raise ValueError(f"Categoría fiscal {categoria_fiscal_id} no encontrada")

        result = await self.session.execute(
            select(ApunteCaja).where(ApunteCaja.id.in_(apunte_ids))
        )
        apuntes = list(result.scalars().all())
        for apunte in apuntes:
            apunte.categoria_fiscal_id = categoria_fiscal_id
            self.session.add(apunte)
        await self.session.commit()
        return len(apuntes)

    async def contar_sin_clasificar(self, ejercicio: Optional[int] = None) -> int:
        """Cuenta los apuntes pendientes de clasificación."""
        query = select(ApunteCaja).where(
            and_(ApunteCaja.eliminado == False, ApunteCaja.categoria_fiscal_id.is_(None))
        )
        if ejercicio:
            from sqlalchemy import extract
            query = query.where(extract("year", ApunteCaja.fecha) == ejercicio)
        result = await self.session.execute(query)
        return len(list(result.scalars().all()))
