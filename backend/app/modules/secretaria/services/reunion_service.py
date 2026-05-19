"""Servicio de reuniones: convocatoria, asistencia, quórum y acuerdos."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.reunion import (
    TipoReunion,
    Reunion,
    AsistenteReunion,
    PuntoOrdenDia,
    Acuerdo,
    VotacionAcuerdo,
)


class ReunionService:
    """Gestiona el ciclo de vida completo de una reunión de órgano de gobierno."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------ #
    # Tipos de reunión                                                     #
    # ------------------------------------------------------------------ #

    async def listar_tipos_reunion(self, activos_solo: bool = True) -> List[TipoReunion]:
        query = select(TipoReunion).order_by(TipoReunion.orden)
        if activos_solo:
            query = query.where(TipoReunion.activo == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def obtener_tipo_reunion(self, tipo_id: UUID) -> Optional[TipoReunion]:
        result = await self.session.execute(
            select(TipoReunion).where(TipoReunion.id == tipo_id)
        )
        return result.scalars().first()

    # ------------------------------------------------------------------ #
    # Reuniones                                                            #
    # ------------------------------------------------------------------ #

    async def _siguiente_numero_convocatoria(self, tipo_reunion_id: UUID, anio: int) -> int:
        """Calcula el número correlativo de convocatoria para el tipo y año."""
        result = await self.session.execute(
            select(func.count(Reunion.id)).where(
                and_(
                    Reunion.tipo_reunion_id == tipo_reunion_id,
                    Reunion.anio == anio,
                    Reunion.eliminado == False,
                )
            )
        )
        return (result.scalar() or 0) + 1

    async def convocar_reunion(
        self,
        tipo_reunion_id: UUID,
        fecha_convocatoria: date,
        fecha_celebracion: Optional[datetime] = None,
        lugar: Optional[str] = None,
        es_telematica: bool = False,
        plataforma_telematica: Optional[str] = None,
        tiene_segunda_convocatoria: bool = True,
        fecha_segunda_convocatoria: Optional[datetime] = None,
        agrupacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> Reunion:
        """Crea una nueva convocatoria de reunión."""
        anio = fecha_convocatoria.year
        numero = await self._siguiente_numero_convocatoria(tipo_reunion_id, anio)

        reunion = Reunion(
            tipo_reunion_id=tipo_reunion_id,
            agrupacion_id=agrupacion_id,
            numero_convocatoria=numero,
            anio=anio,
            fecha_convocatoria=fecha_convocatoria,
            fecha_celebracion=fecha_celebracion,
            lugar=lugar,
            es_telematica=es_telematica,
            plataforma_telematica=plataforma_telematica,
            tiene_segunda_convocatoria=tiene_segunda_convocatoria,
            fecha_segunda_convocatoria=fecha_segunda_convocatoria,
            estado='CONVOCADA',
            observaciones=observaciones,
            creado_por_id=creado_por_id,
        )
        self.session.add(reunion)
        await self.session.commit()
        await self.session.refresh(reunion)
        return reunion

    async def obtener_reunion(self, reunion_id: UUID) -> Optional[Reunion]:
        result = await self.session.execute(
            select(Reunion).where(
                and_(Reunion.id == reunion_id, Reunion.eliminado == False)
            )
        )
        return result.scalars().first()

    async def listar_reuniones(
        self,
        anio: Optional[int] = None,
        tipo_reunion_id: Optional[UUID] = None,
        agrupacion_id: Optional[UUID] = None,
        estado: Optional[str] = None,
    ) -> List[Reunion]:
        query = select(Reunion).where(Reunion.eliminado == False)
        if anio:
            query = query.where(Reunion.anio == anio)
        if tipo_reunion_id:
            query = query.where(Reunion.tipo_reunion_id == tipo_reunion_id)
        if agrupacion_id:
            query = query.where(Reunion.agrupacion_id == agrupacion_id)
        if estado:
            query = query.where(Reunion.estado == estado)
        query = query.order_by(Reunion.fecha_convocatoria.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def registrar_celebracion(
        self,
        reunion_id: UUID,
        socios_totales: int,
        socios_presentes: int,
        socios_representados: int = 0,
        convocatoria_utilizada: int = 1,
        modificado_por_id: Optional[UUID] = None,
    ) -> Reunion:
        """Registra los datos de celebración y calcula el quórum."""
        reunion = await self.obtener_reunion(reunion_id)
        if not reunion:
            raise ValueError(f"Reunión {reunion_id} no encontrada")

        tipo = await self.obtener_tipo_reunion(reunion.tipo_reunion_id)

        reunion.socios_totales = socios_totales
        reunion.socios_presentes = socios_presentes
        reunion.socios_representados = socios_representados
        reunion.convocatoria_utilizada = convocatoria_utilizada
        reunion.estado = 'CELEBRADA'
        reunion.modificado_por_id = modificado_por_id

        # Calcular quórum
        presentes_total = socios_presentes + socios_representados
        if socios_totales > 0 and tipo:
            porcentaje = presentes_total / socios_totales * 100
            umbral = (
                tipo.quorum_primera_convocatoria
                if convocatoria_utilizada == 1
                else tipo.quorum_segunda_convocatoria
            )
            # umbral=0 significa que cualquier número es suficiente (2ª convocatoria)
            reunion.hay_quorum = (umbral is None or umbral == 0 or porcentaje >= umbral)
        else:
            reunion.hay_quorum = True

        await self.session.commit()
        await self.session.refresh(reunion)
        return reunion

    async def cancelar_reunion(
        self,
        reunion_id: UUID,
        motivo: Optional[str] = None,
        modificado_por_id: Optional[UUID] = None,
    ) -> Reunion:
        reunion = await self.obtener_reunion(reunion_id)
        if not reunion:
            raise ValueError(f"Reunión {reunion_id} no encontrada")
        if reunion.estado == 'ACTA_APROBADA':
            raise ValueError("No se puede cancelar una reunión con acta aprobada")

        reunion.estado = 'CANCELADA'
        if motivo:
            reunion.observaciones = motivo
        reunion.modificado_por_id = modificado_por_id
        await self.session.commit()
        await self.session.refresh(reunion)
        return reunion

    # ------------------------------------------------------------------ #
    # Asistencia                                                           #
    # ------------------------------------------------------------------ #

    async def registrar_asistente(
        self,
        reunion_id: UUID,
        miembro_id: UUID,
        tipo_asistencia: str = 'PRESENCIAL',
        representado_por_id: Optional[UUID] = None,
        cargo: Optional[str] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> AsistenteReunion:
        """Registra la asistencia de un miembro a una reunión."""
        # Evitar duplicados
        existente = await self.session.execute(
            select(AsistenteReunion).where(
                and_(
                    AsistenteReunion.reunion_id == reunion_id,
                    AsistenteReunion.miembro_id == miembro_id,
                    AsistenteReunion.eliminado == False,
                )
            )
        )
        if existente.scalars().first():
            raise ValueError(f"El miembro {miembro_id} ya está registrado en esta reunión")

        asistente = AsistenteReunion(
            reunion_id=reunion_id,
            miembro_id=miembro_id,
            tipo_asistencia=tipo_asistencia,
            representado_por_id=representado_por_id,
            cargo=cargo,
            creado_por_id=creado_por_id,
        )
        self.session.add(asistente)
        await self.session.commit()
        await self.session.refresh(asistente)
        return asistente

    async def listar_asistentes(self, reunion_id: UUID) -> List[AsistenteReunion]:
        result = await self.session.execute(
            select(AsistenteReunion).where(
                and_(
                    AsistenteReunion.reunion_id == reunion_id,
                    AsistenteReunion.eliminado == False,
                )
            )
        )
        return list(result.scalars().all())

    # ------------------------------------------------------------------ #
    # Orden del día y acuerdos                                            #
    # ------------------------------------------------------------------ #

    async def añadir_punto_orden_dia(
        self,
        reunion_id: UUID,
        titulo: str,
        orden: Optional[int] = None,
        descripcion: Optional[str] = None,
        tipo: str = 'ORDINARIO',
        creado_por_id: Optional[UUID] = None,
    ) -> PuntoOrdenDia:
        """Añade un punto al orden del día. Si no se indica orden, se añade al final."""
        if orden is None:
            result = await self.session.execute(
                select(func.count(PuntoOrdenDia.id)).where(
                    and_(
                        PuntoOrdenDia.reunion_id == reunion_id,
                        PuntoOrdenDia.eliminado == False,
                    )
                )
            )
            orden = (result.scalar() or 0) + 1

        punto = PuntoOrdenDia(
            reunion_id=reunion_id,
            orden=orden,
            titulo=titulo,
            descripcion=descripcion,
            tipo=tipo,
            creado_por_id=creado_por_id,
        )
        self.session.add(punto)
        await self.session.commit()
        await self.session.refresh(punto)
        return punto

    async def registrar_acuerdo(
        self,
        punto_orden_dia_id: UUID,
        descripcion: str,
        tipo_mayoria: str = 'SIMPLE',
        resultado: Optional[str] = None,
        votos_favor: int = 0,
        votos_contra: int = 0,
        abstenciones: int = 0,
        votos_nulos: int = 0,
        es_votacion_secreta: bool = False,
        responsable_id: Optional[UUID] = None,
        fecha_limite_ejecucion: Optional[date] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> Acuerdo:
        """Registra un acuerdo y su votación."""
        # Número correlativo dentro del punto
        result = await self.session.execute(
            select(func.count(Acuerdo.id)).where(
                and_(
                    Acuerdo.punto_orden_dia_id == punto_orden_dia_id,
                    Acuerdo.eliminado == False,
                )
            )
        )
        numero = (result.scalar() or 0) + 1

        acuerdo = Acuerdo(
            punto_orden_dia_id=punto_orden_dia_id,
            numero=numero,
            descripcion=descripcion,
            tipo_mayoria=tipo_mayoria,
            resultado=resultado,
            responsable_id=responsable_id,
            fecha_limite_ejecucion=fecha_limite_ejecucion,
            estado_ejecucion='PENDIENTE',
            creado_por_id=creado_por_id,
        )
        self.session.add(acuerdo)
        await self.session.flush()  # Para obtener el ID antes del commit

        votacion = VotacionAcuerdo(
            acuerdo_id=acuerdo.id,
            votos_favor=votos_favor,
            votos_contra=votos_contra,
            abstenciones=abstenciones,
            votos_nulos=votos_nulos,
            es_votacion_secreta=es_votacion_secreta,
            creado_por_id=creado_por_id,
        )
        self.session.add(votacion)
        await self.session.commit()
        await self.session.refresh(acuerdo)
        return acuerdo

    async def actualizar_seguimiento_acuerdo(
        self,
        acuerdo_id: UUID,
        estado_ejecucion: str,
        observaciones_ejecucion: Optional[str] = None,
        responsable_id: Optional[UUID] = None,
        fecha_limite_ejecucion: Optional[date] = None,
        modificado_por_id: Optional[UUID] = None,
    ) -> Acuerdo:
        """Actualiza el estado de ejecución de un acuerdo."""
        result = await self.session.execute(
            select(Acuerdo).where(
                and_(Acuerdo.id == acuerdo_id, Acuerdo.eliminado == False)
            )
        )
        acuerdo = result.scalars().first()
        if not acuerdo:
            raise ValueError(f"Acuerdo {acuerdo_id} no encontrado")

        acuerdo.estado_ejecucion = estado_ejecucion
        if observaciones_ejecucion is not None:
            acuerdo.observaciones_ejecucion = observaciones_ejecucion
        if responsable_id is not None:
            acuerdo.responsable_id = responsable_id
        if fecha_limite_ejecucion is not None:
            acuerdo.fecha_limite_ejecucion = fecha_limite_ejecucion
        acuerdo.modificado_por_id = modificado_por_id

        await self.session.commit()
        await self.session.refresh(acuerdo)
        return acuerdo

    async def listar_acuerdos_pendientes(
        self, agrupacion_id: Optional[UUID] = None
    ) -> List[Acuerdo]:
        """Lista acuerdos pendientes de ejecutar, opcionalmente filtrados por agrupación."""
        query = (
            select(Acuerdo)
            .join(PuntoOrdenDia, Acuerdo.punto_orden_dia_id == PuntoOrdenDia.id)
            .join(Reunion, PuntoOrdenDia.reunion_id == Reunion.id)
            .where(
                and_(
                    Acuerdo.estado_ejecucion.in_(['PENDIENTE', 'EN_CURSO']),
                    Acuerdo.resultado == 'APROBADO',
                    Acuerdo.eliminado == False,
                    Reunion.eliminado == False,
                )
            )
        )
        if agrupacion_id:
            query = query.where(Reunion.agrupacion_id == agrupacion_id)
        query = query.order_by(Acuerdo.fecha_limite_ejecucion.asc().nullslast())
        result = await self.session.execute(query)
        return list(result.scalars().all())
