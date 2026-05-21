"""Servicio de actas y certificados de acuerdos."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.acta import Acta, CertificadoAcuerdo
from ..models.reunion import Acuerdo, PuntoOrdenDia, Reunion


class ActaService:
    """Gestiona el ciclo de vida de actas y certificados."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------ #
    # Numeración correlativa                                               #
    # ------------------------------------------------------------------ #

    async def _siguiente_numero_acta(self, tipo_reunion_id: UUID, anio: int) -> int:
        """Número correlativo de acta por tipo de órgano y año."""
        result = await self.session.execute(
            select(func.count(Acta.id))
            .join(Reunion, Acta.reunion_id == Reunion.id)
            .where(
                and_(
                    Reunion.tipo_reunion_id == tipo_reunion_id,
                    Acta.anio == anio,
                    Acta.eliminado == False,
                )
            )
        )
        return (result.scalar() or 0) + 1

    async def _siguiente_numero_certificado(self, anio: int) -> str:
        """Genera el número de certificado: CERT-AAAA-NNN."""
        result = await self.session.execute(
            select(func.count(CertificadoAcuerdo.id)).where(
                and_(
                    func.extract('year', CertificadoAcuerdo.fecha_emision) == anio,
                    CertificadoAcuerdo.eliminado == False,
                )
            )
        )
        numero = (result.scalar() or 0) + 1
        return f"CERT-{anio}-{numero:03d}"

    # ------------------------------------------------------------------ #
    # Actas                                                                #
    # ------------------------------------------------------------------ #

    async def crear_acta_borrador(
        self,
        reunion_id: UUID,
        texto_acta: Optional[str] = None,
        secretario_id: Optional[UUID] = None,
        presidente_id: Optional[UUID] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> Acta:
        """Crea el borrador del acta de una reunión."""
        # Verificar que no existe ya un acta para esta reunión
        existente = await self.session.execute(
            select(Acta).where(
                and_(Acta.reunion_id == reunion_id, Acta.eliminado == False)
            )
        )
        if existente.scalars().first():
            raise ValueError(f"Ya existe un acta para la reunión {reunion_id}")

        # Obtener datos de la reunión para la numeración
        reunion_result = await self.session.execute(
            select(Reunion).where(Reunion.id == reunion_id)
        )
        reunion = reunion_result.scalars().first()
        if not reunion:
            raise ValueError(f"Reunión {reunion_id} no encontrada")

        anio = reunion.anio
        numero = await self._siguiente_numero_acta(reunion.tipo_reunion_id, anio)

        acta = Acta(
            reunion_id=reunion_id,
            numero=numero,
            anio=anio,
            texto_acta=texto_acta,
            estado_codigo='BORRADOR',
            secretario_id=secretario_id,
            presidente_id=presidente_id,
            creado_por_id=creado_por_id,
        )
        self.session.add(acta)

        # Actualizar estado de la reunión
        reunion.estado_codigo = 'ACTA_BORRADOR'
        reunion.modificado_por_id = creado_por_id

        await self.session.commit()
        await self.session.refresh(acta)

        # Aviso de flujo: acta en borrador pendiente de revisión.
        try:
            from app.core.events import event_bus, ActaEnBorrador
            await event_bus.publish(ActaEnBorrador(
                acta_id=str(acta.id),
                reunion_titulo=f"convocatoria {reunion.numero_convocatoria}/{reunion.anio}",
                agrupacion_id=str(reunion.agrupacion_id) if reunion.agrupacion_id else None,
            ))
        except Exception:
            pass

        return acta

    async def obtener_acta(self, acta_id: UUID) -> Optional[Acta]:
        result = await self.session.execute(
            select(Acta).where(and_(Acta.id == acta_id, Acta.eliminado == False))
        )
        return result.scalars().first()

    async def obtener_acta_por_reunion(self, reunion_id: UUID) -> Optional[Acta]:
        result = await self.session.execute(
            select(Acta).where(
                and_(Acta.reunion_id == reunion_id, Acta.eliminado == False)
            )
        )
        return result.scalars().first()

    async def listar_actas(
        self,
        anio: Optional[int] = None,
        estado: Optional[str] = None,
        tipo_reunion_id: Optional[UUID] = None,
    ) -> List[Acta]:
        query = select(Acta).where(Acta.eliminado == False)
        if anio:
            query = query.where(Acta.anio == anio)
        if estado:
            query = query.where(Acta.estado_codigo == estado)
        if tipo_reunion_id:
            query = (
                query.join(Reunion, Acta.reunion_id == Reunion.id)
                .where(Reunion.tipo_reunion_id == tipo_reunion_id)
            )
        query = query.order_by(Acta.anio.desc(), Acta.numero.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def aprobar_acta(
        self,
        acta_id: UUID,
        fecha_aprobacion: date,
        reunion_aprobacion_id: Optional[UUID] = None,
        modificado_por_id: Optional[UUID] = None,
    ) -> Acta:
        """Aprueba el acta y actualiza el estado de la reunión."""
        acta = await self.obtener_acta(acta_id)
        if not acta:
            raise ValueError(f"Acta {acta_id} no encontrada")
        if acta.estado_codigo not in ('BORRADOR',):
            raise ValueError(f"El acta está en estado '{acta.estado}' y no puede aprobarse")

        acta.estado_codigo = 'APROBADA'
        acta.fecha_aprobacion = fecha_aprobacion
        acta.reunion_aprobacion_id = reunion_aprobacion_id
        acta.modificado_por_id = modificado_por_id

        # Actualizar estado de la reunión
        reunion_result = await self.session.execute(
            select(Reunion).where(Reunion.id == acta.reunion_id)
        )
        reunion = reunion_result.scalars().first()
        if reunion:
            reunion.estado_codigo = 'ACTA_APROBADA'
            reunion.modificado_por_id = modificado_por_id

        await self.session.commit()
        await self.session.refresh(acta)

        # Aviso de flujo: acta lista para firma. Publicado tras el commit; un
        # fallo de aviso no afecta a la aprobación (el event bus captura).
        try:
            from app.core.events import event_bus, ActaAprobada
            if reunion is not None:
                desc = f"convocatoria {reunion.numero_convocatoria}/{reunion.anio}"
                agr = str(reunion.agrupacion_id) if reunion.agrupacion_id else None
            else:
                desc = f"reunión {acta.reunion_id}"
                agr = None
            await event_bus.publish(ActaAprobada(
                acta_id=str(acta.id),
                reunion_titulo=desc,
                agrupacion_id=agr,
            ))
        except Exception:
            pass

        return acta

    async def firmar_acta(
        self,
        acta_id: UUID,
        secretario_id: UUID,
        presidente_id: UUID,
        modificado_por_id: Optional[UUID] = None,
    ) -> Acta:
        """Registra la firma del acta por secretario y presidente."""
        acta = await self.obtener_acta(acta_id)
        if not acta:
            raise ValueError(f"Acta {acta_id} no encontrada")
        if acta.estado_codigo != 'APROBADA':
            raise ValueError("Solo se pueden firmar actas aprobadas")

        acta.estado_codigo = 'FIRMADA'
        acta.secretario_id = secretario_id
        acta.presidente_id = presidente_id
        acta.fecha_firma = datetime.utcnow()
        acta.modificado_por_id = modificado_por_id

        await self.session.commit()
        await self.session.refresh(acta)
        return acta

    async def listar_pendientes_aprobacion(self) -> List[Acta]:
        """Actas en borrador pendientes de aprobación."""
        result = await self.session.execute(
            select(Acta)
            .where(and_(Acta.estado_codigo == 'BORRADOR', Acta.eliminado == False))
            .order_by(Acta.anio.asc(), Acta.numero.asc())
        )
        return list(result.scalars().all())

    # ------------------------------------------------------------------ #
    # Certificados de acuerdos                                            #
    # ------------------------------------------------------------------ #

    async def emitir_certificado(
        self,
        acta_id: UUID,
        acuerdo_id: UUID,
        texto_certificado: str,
        fecha_emision: Optional[date] = None,
        destinatario: Optional[str] = None,
        proposito: Optional[str] = None,
        secretario_id: Optional[UUID] = None,
        presidente_id: Optional[UUID] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> CertificadoAcuerdo:
        """Emite un certificado de un acuerdo concreto."""
        if fecha_emision is None:
            fecha_emision = date.today()

        numero = await self._siguiente_numero_certificado(fecha_emision.year)

        certificado = CertificadoAcuerdo(
            acta_id=acta_id,
            acuerdo_id=acuerdo_id,
            numero_certificado=numero,
            fecha_emision=fecha_emision,
            destinatario=destinatario,
            proposito=proposito,
            texto_certificado=texto_certificado,
            secretario_id=secretario_id,
            presidente_id=presidente_id,
            creado_por_id=creado_por_id,
        )
        self.session.add(certificado)
        await self.session.commit()
        await self.session.refresh(certificado)
        return certificado

    async def listar_certificados(
        self, acta_id: Optional[UUID] = None, anio: Optional[int] = None
    ) -> List[CertificadoAcuerdo]:
        query = select(CertificadoAcuerdo).where(CertificadoAcuerdo.eliminado == False)
        if acta_id:
            query = query.where(CertificadoAcuerdo.acta_id == acta_id)
        if anio:
            query = query.where(
                func.extract('year', CertificadoAcuerdo.fecha_emision) == anio
            )
        query = query.order_by(CertificadoAcuerdo.fecha_emision.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
