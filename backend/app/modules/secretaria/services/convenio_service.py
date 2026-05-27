"""Servicio de convenios institucionales y delegaciones de firma."""

from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.convenio import TipoConvenio, ConvenioInstitucional, DelegacionFirma


class ConvenioService:
    """Gestiona convenios institucionales y delegaciones de representación."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------ #
    # Tipos de convenio                                                    #
    # ------------------------------------------------------------------ #

    async def listar_tipos_convenio(self, activos_solo: bool = True) -> List[TipoConvenio]:
        query = select(TipoConvenio).where(TipoConvenio.eliminado == False)
        if activos_solo:
            query = query.where(TipoConvenio.activo == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ------------------------------------------------------------------ #
    # Convenios                                                            #
    # ------------------------------------------------------------------ #

    async def _siguiente_referencia(self, anio: int) -> str:
        """Genera la referencia interna: CONV-AAAA-NNN."""
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count(ConvenioInstitucional.id)).where(
                and_(
                    func.extract('year', ConvenioInstitucional.fecha_firma) == anio,
                    ConvenioInstitucional.eliminado == False,
                )
            )
        )
        numero = (result.scalar() or 0) + 1
        return f"CONV-{anio}-{numero:03d}"

    async def registrar_convenio(
        self,
        tipo_convenio_id: UUID,
        titulo: str,
        entidad_contraparte: str,
        fecha_firma: date,
        fecha_inicio: date,
        objeto: Optional[str] = None,
        nif_contraparte: Optional[str] = None,
        fecha_fin: Optional[date] = None,
        renovacion_automatica: bool = False,
        dias_preaviso_no_renovacion: Optional[int] = None,
        obligaciones_asociacion: Optional[str] = None,
        obligaciones_contraparte: Optional[str] = None,
        firmante_id: Optional[UUID] = None,
        acuerdo_autorizacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> ConvenioInstitucional:
        referencia = await self._siguiente_referencia(fecha_firma.year)

        convenio = ConvenioInstitucional(
            tipo_convenio_id=tipo_convenio_id,
            referencia=referencia,
            titulo=titulo,
            entidad_contraparte=entidad_contraparte,
            nif_contraparte=nif_contraparte,
            fecha_firma=fecha_firma,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            renovacion_automatica=renovacion_automatica,
            dias_preaviso_no_renovacion=dias_preaviso_no_renovacion,
            estado='VIGENTE',
            objeto=objeto,
            obligaciones_asociacion=obligaciones_asociacion,
            obligaciones_contraparte=obligaciones_contraparte,
            firmante_id=firmante_id,
            acuerdo_autorizacion_id=acuerdo_autorizacion_id,
            observaciones=observaciones,
            creado_por_id=creado_por_id,
        )
        self.session.add(convenio)
        await self.session.commit()
        await self.session.refresh(convenio)
        return convenio

    async def obtener_convenio(self, convenio_id: UUID) -> Optional[ConvenioInstitucional]:
        result = await self.session.execute(
            select(ConvenioInstitucional).where(
                and_(ConvenioInstitucional.id == convenio_id, ConvenioInstitucional.eliminado == False)
            )
        )
        return result.scalars().first()

    async def listar_convenios(
        self,
        estado: Optional[str] = None,
        tipo_convenio_id: Optional[UUID] = None,
        proximos_a_vencer_dias: Optional[int] = None,
    ) -> List[ConvenioInstitucional]:
        query = select(ConvenioInstitucional).where(ConvenioInstitucional.eliminado == False)
        if estado:
            query = query.where(ConvenioInstitucional.estado == estado)
        if tipo_convenio_id:
            query = query.where(ConvenioInstitucional.tipo_convenio_id == tipo_convenio_id)
        if proximos_a_vencer_dias is not None:
            from sqlalchemy import text
            hoy = date.today()
            from datetime import timedelta
            limite = hoy + timedelta(days=proximos_a_vencer_dias)
            query = query.where(
                and_(
                    ConvenioInstitucional.fecha_fin.is_not(None),
                    ConvenioInstitucional.fecha_fin <= limite,
                    ConvenioInstitucional.fecha_fin >= hoy,
                    ConvenioInstitucional.estado == 'VIGENTE',
                )
            )
        query = query.order_by(ConvenioInstitucional.fecha_inicio.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def cambiar_estado_convenio(
        self,
        convenio_id: UUID,
        nuevo_estado: str,
        modificado_por_id: Optional[UUID] = None,
    ) -> ConvenioInstitucional:
        convenio = await self.obtener_convenio(convenio_id)
        if not convenio:
            raise ValueError(f"ConvenioInstitucional {convenio_id} no encontrado")

        estados_validos = {'VIGENTE', 'VENCIDO', 'RESCINDIDO', 'SUSPENDIDO'}
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado '{nuevo_estado}' no válido")

        convenio.estado = nuevo_estado
        convenio.modificado_por_id = modificado_por_id
        await self.session.commit()
        await self.session.refresh(convenio)
        return convenio

    # ------------------------------------------------------------------ #
    # Delegaciones de firma                                                #
    # ------------------------------------------------------------------ #

    async def crear_delegacion(
        self,
        delegante_id: UUID,
        delegado_id: UUID,
        descripcion_actos: str,
        fecha_inicio: date,
        fecha_fin: Optional[date] = None,
        limite_importe: Optional[float] = None,
        acuerdo_autorizacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> DelegacionFirma:
        delegacion = DelegacionFirma(
            delegante_id=delegante_id,
            delegado_id=delegado_id,
            descripcion_actos=descripcion_actos,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            limite_importe=limite_importe,
            activa=True,
            acuerdo_autorizacion_id=acuerdo_autorizacion_id,
            observaciones=observaciones,
            creado_por_id=creado_por_id,
        )
        self.session.add(delegacion)
        await self.session.commit()
        await self.session.refresh(delegacion)
        return delegacion

    async def listar_delegaciones(
        self, activas_solo: bool = True, delegado_id: Optional[UUID] = None
    ) -> List[DelegacionFirma]:
        query = select(DelegacionFirma).where(DelegacionFirma.eliminado == False)
        if activas_solo:
            query = query.where(DelegacionFirma.activa == True)
        if delegado_id:
            query = query.where(DelegacionFirma.delegado_id == delegado_id)
        query = query.order_by(DelegacionFirma.fecha_inicio.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def revocar_delegacion(
        self, delegacion_id: UUID, modificado_por_id: Optional[UUID] = None
    ) -> DelegacionFirma:
        result = await self.session.execute(
            select(DelegacionFirma).where(
                and_(DelegacionFirma.id == delegacion_id, DelegacionFirma.eliminado == False)
            )
        )
        delegacion = result.scalars().first()
        if not delegacion:
            raise ValueError(f"Delegación {delegacion_id} no encontrada")

        delegacion.activa = False
        delegacion.fecha_fin = date.today()
        delegacion.modificado_por_id = modificado_por_id
        await self.session.commit()
        await self.session.refresh(delegacion)
        return delegacion
