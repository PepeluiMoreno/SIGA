"""Servicio del Libro de Socios (Ley Orgánica 1/2002)."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.libro_socios import LibroSociosSnapshot


class LibroSociosService:
    """Genera y custodia snapshots del Libro de Socios."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generar_snapshot(
        self,
        fecha_corte: Optional[date] = None,
        motivo: Optional[str] = None,
        observaciones: Optional[str] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> LibroSociosSnapshot:
        """Genera un snapshot del libro de socios en la fecha de corte indicada.

        Los conteos se calculan contra la tabla miembros en tiempo real.
        La generación del PDF queda pendiente de implementación posterior.
        """
        if fecha_corte is None:
            fecha_corte = date.today()

        # Importación diferida para evitar circularidad. El "socio" ahora es una
        # VINCULACIÓN de tipo SOCIO (no la persona): activa = estado 'activa'.
        from ...membresia.models.vinculacion import Vinculacion
        from ...membresia.models.tipo_vinculacion import TipoVinculacion

        base = (
            select(func.count(Vinculacion.id))
            .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
            .where(TipoVinculacion.codigo == "SOCIO", Vinculacion.eliminado == False)
        )
        total_historico = (await self.session.execute(base)).scalar() or 0
        total_activos = (
            await self.session.execute(base.where(Vinculacion.estado == "activa"))
        ).scalar() or 0
        total_baja = total_historico - total_activos

        snapshot = LibroSociosSnapshot(
            fecha_corte=fecha_corte,
            fecha_generacion=datetime.utcnow(),
            total_socios_activos=total_activos,
            total_socios_baja=max(total_baja, 0),
            total_socios_historico=total_historico,
            motivo=motivo,
            observaciones=observaciones,
            creado_por_id=creado_por_id,
        )
        self.session.add(snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)
        return snapshot

    async def listar_snapshots(self) -> List[LibroSociosSnapshot]:
        result = await self.session.execute(
            select(LibroSociosSnapshot)
            .where(LibroSociosSnapshot.eliminado == False)
            .order_by(LibroSociosSnapshot.fecha_corte.desc())
        )
        return list(result.scalars().all())

    async def obtener_ultimo_snapshot(self) -> Optional[LibroSociosSnapshot]:
        result = await self.session.execute(
            select(LibroSociosSnapshot)
            .where(LibroSociosSnapshot.eliminado == False)
            .order_by(LibroSociosSnapshot.fecha_corte.desc())
            .limit(1)
        )
        return result.scalars().first()
