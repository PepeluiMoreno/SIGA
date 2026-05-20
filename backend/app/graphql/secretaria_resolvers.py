"""Resolvers GraphQL del módulo de Secretaría.

Queries y mutations para reuniones, actas, certificados,
libro de socios, convenios y delegaciones de firma.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional

import strawberry
from sqlalchemy import select

from app.modules.secretaria.models.reunion import (
    TipoReunion, Reunion, AsistenteReunionSecretaria, PuntoOrdenDia, Acuerdo, VotacionAcuerdo
)
from app.modules.secretaria.models.acta import Acta, CertificadoAcuerdo
from app.modules.secretaria.models.libro_socios import LibroSociosSnapshot
from app.modules.secretaria.models.convenio import TipoConvenio, ConvenioInstitucional, DelegacionFirma
from app.modules.secretaria.services.reunion_service import ReunionService
from app.modules.secretaria.services.acta_service import ActaService
from app.modules.secretaria.services.libro_socios_service import LibroSociosService
from app.modules.secretaria.services.convenio_service import ConvenioService
from app.graphql.permissions import RequireTransaction


# ---------------------------------------------------------------------------
# Tipos Strawberry — inline (los tipos_auto no cubren aún este módulo)
# ---------------------------------------------------------------------------

@strawberry.type
class TipoReunionGQL:
    id: uuid.UUID
    nombre: str
    organo: str
    descripcion: Optional[str]
    quorum_primera_convocatoria: Optional[int]
    quorum_segunda_convocatoria: Optional[int]
    antelacion_minima_dias: int
    activo: bool
    orden: int

    @staticmethod
    def from_model(m: TipoReunion) -> 'TipoReunionGQL':
        return TipoReunionGQL(
            id=m.id, nombre=m.nombre, organo=m.organo,
            descripcion=m.descripcion,
            quorum_primera_convocatoria=m.quorum_primera_convocatoria,
            quorum_segunda_convocatoria=m.quorum_segunda_convocatoria,
            antelacion_minima_dias=m.antelacion_minima_dias,
            activo=m.activo, orden=m.orden,
        )


@strawberry.type
class ReunionGQL:
    id: uuid.UUID
    tipo_reunion_id: uuid.UUID
    agrupacion_id: Optional[uuid.UUID]
    numero_convocatoria: int
    anio: int
    fecha_convocatoria: date
    fecha_celebracion: Optional[datetime]
    lugar: Optional[str]
    es_telematica: bool
    tiene_segunda_convocatoria: bool
    convocatoria_utilizada: Optional[int]
    socios_totales: Optional[int]
    socios_presentes: Optional[int]
    socios_representados: Optional[int]
    hay_quorum: Optional[bool]
    estado_codigo: str
    estado_id: Optional[uuid.UUID]
    observaciones: Optional[str]

    @staticmethod
    def from_model(m: Reunion) -> 'ReunionGQL':
        return ReunionGQL(
            id=m.id, tipo_reunion_id=m.tipo_reunion_id,
            agrupacion_id=m.agrupacion_id,
            numero_convocatoria=m.numero_convocatoria, anio=m.anio,
            fecha_convocatoria=m.fecha_convocatoria,
            fecha_celebracion=m.fecha_celebracion,
            lugar=m.lugar, es_telematica=m.es_telematica,
            tiene_segunda_convocatoria=m.tiene_segunda_convocatoria,
            convocatoria_utilizada=m.convocatoria_utilizada,
            socios_totales=m.socios_totales,
            socios_presentes=m.socios_presentes,
            socios_representados=m.socios_representados,
            hay_quorum=m.hay_quorum, estado_codigo=m.estado_codigo, estado_id=m.estado_id,
            observaciones=m.observaciones,
        )


@strawberry.type
class AcuerdoGQL:
    id: uuid.UUID
    punto_orden_dia_id: uuid.UUID
    numero: int
    descripcion: str
    tipo_mayoria: str
    resultado: Optional[str]
    responsable_id: Optional[uuid.UUID]
    fecha_limite_ejecucion: Optional[date]
    estado_ejecucion_codigo: str
    estado_ejecucion_id: Optional[uuid.UUID]
    observaciones_ejecucion: Optional[str]

    @staticmethod
    def from_model(m: Acuerdo) -> 'AcuerdoGQL':
        return AcuerdoGQL(
            id=m.id, punto_orden_dia_id=m.punto_orden_dia_id,
            numero=m.numero, descripcion=m.descripcion,
            tipo_mayoria=m.tipo_mayoria, resultado=m.resultado,
            responsable_id=m.responsable_id,
            fecha_limite_ejecucion=m.fecha_limite_ejecucion,
            estado_ejecucion_codigo=m.estado_ejecucion_codigo, estado_ejecucion_id=m.estado_ejecucion_id,
            observaciones_ejecucion=m.observaciones_ejecucion,
        )


@strawberry.type
class ActaGQL:
    id: uuid.UUID
    reunion_id: uuid.UUID
    numero: int
    anio: int
    texto_acta: Optional[str]
    estado_codigo: str
    estado_id: Optional[uuid.UUID]
    fecha_aprobacion: Optional[date]
    secretario_id: Optional[uuid.UUID]
    presidente_id: Optional[uuid.UUID]
    fecha_firma: Optional[datetime]

    @staticmethod
    def from_model(m: Acta) -> 'ActaGQL':
        return ActaGQL(
            id=m.id, reunion_id=m.reunion_id,
            numero=m.numero, anio=m.anio,
            texto_acta=m.texto_acta, estado_codigo=m.estado_codigo, estado_id=m.estado_id,
            fecha_aprobacion=m.fecha_aprobacion,
            secretario_id=m.secretario_id,
            presidente_id=m.presidente_id,
            fecha_firma=m.fecha_firma,
        )


@strawberry.type
class CertificadoGQL:
    id: uuid.UUID
    acta_id: uuid.UUID
    acuerdo_id: uuid.UUID
    numero_certificado: str
    fecha_emision: date
    destinatario: Optional[str]
    proposito: Optional[str]
    texto_certificado: str
    secretario_id: Optional[uuid.UUID]
    presidente_id: Optional[uuid.UUID]

    @staticmethod
    def from_model(m: CertificadoAcuerdo) -> 'CertificadoGQL':
        return CertificadoGQL(
            id=m.id, acta_id=m.acta_id, acuerdo_id=m.acuerdo_id,
            numero_certificado=m.numero_certificado,
            fecha_emision=m.fecha_emision,
            destinatario=m.destinatario, proposito=m.proposito,
            texto_certificado=m.texto_certificado,
            secretario_id=m.secretario_id,
            presidente_id=m.presidente_id,
        )


@strawberry.type
class LibroSociosSnapshotGQL:
    id: uuid.UUID
    fecha_corte: date
    fecha_generacion: datetime
    total_socios_activos: int
    total_socios_baja: int
    total_socios_historico: int
    motivo: Optional[str]
    observaciones: Optional[str]

    @staticmethod
    def from_model(m: LibroSociosSnapshot) -> 'LibroSociosSnapshotGQL':
        return LibroSociosSnapshotGQL(
            id=m.id, fecha_corte=m.fecha_corte,
            fecha_generacion=m.fecha_generacion,
            total_socios_activos=m.total_socios_activos,
            total_socios_baja=m.total_socios_baja,
            total_socios_historico=m.total_socios_historico,
            motivo=m.motivo, observaciones=m.observaciones,
        )


@strawberry.type
class ConvenioGQL:
    id: uuid.UUID
    tipo_convenio_id: uuid.UUID
    referencia: str
    titulo: str
    entidad_contraparte: str
    cif_contraparte: Optional[str]
    fecha_firma: date
    fecha_inicio: date
    fecha_fin: Optional[date]
    renovacion_automatica: bool
    estado: str
    objeto: Optional[str]
    firmante_id: Optional[uuid.UUID]

    @staticmethod
    def from_model(m: ConvenioInstitucional) -> 'ConvenioGQL':
        return ConvenioGQL(
            id=m.id, tipo_convenio_id=m.tipo_convenio_id,
            referencia=m.referencia, titulo=m.titulo,
            entidad_contraparte=m.entidad_contraparte,
            cif_contraparte=m.cif_contraparte,
            fecha_firma=m.fecha_firma, fecha_inicio=m.fecha_inicio,
            fecha_fin=m.fecha_fin,
            renovacion_automatica=m.renovacion_automatica,
            estado=m.estado, objeto=m.objeto,
            firmante_id=m.firmante_id,
        )


@strawberry.type
class DelegacionFirmaGQL:
    id: uuid.UUID
    delegante_id: uuid.UUID
    delegado_id: uuid.UUID
    descripcion_actos: str
    limite_importe: Optional[float]
    fecha_inicio: date
    fecha_fin: Optional[date]
    activa: bool

    @staticmethod
    def from_model(m: DelegacionFirma) -> 'DelegacionFirmaGQL':
        return DelegacionFirmaGQL(
            id=m.id, delegante_id=m.delegante_id,
            delegado_id=m.delegado_id,
            descripcion_actos=m.descripcion_actos,
            limite_importe=float(m.limite_importe) if m.limite_importe else None,
            fecha_inicio=m.fecha_inicio, fecha_fin=m.fecha_fin,
            activa=m.activa,
        )


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

@strawberry.input
class ConvocarReunionInput:
    tipo_reunion_id: uuid.UUID
    fecha_convocatoria: date
    fecha_celebracion: Optional[datetime] = None
    lugar: Optional[str] = None
    es_telematica: bool = False
    plataforma_telematica: Optional[str] = None
    tiene_segunda_convocatoria: bool = True
    fecha_segunda_convocatoria: Optional[datetime] = None
    agrupacion_id: Optional[uuid.UUID] = None
    observaciones: Optional[str] = None


@strawberry.input
class RegistrarCelebracionInput:
    reunion_id: uuid.UUID
    socios_totales: int
    socios_presentes: int
    socios_representados: int = 0
    convocatoria_utilizada: int = 1


@strawberry.input
class RegistrarAcuerdoInput:
    punto_orden_dia_id: uuid.UUID
    descripcion: str
    tipo_mayoria: str = 'SIMPLE'
    resultado: Optional[str] = None
    votos_favor: int = 0
    votos_contra: int = 0
    abstenciones: int = 0
    votos_nulos: int = 0
    es_votacion_secreta: bool = False
    responsable_id: Optional[uuid.UUID] = None
    fecha_limite_ejecucion: Optional[date] = None


@strawberry.input
class ActualizarSeguimientoInput:
    acuerdo_id: uuid.UUID
    estado_ejecucion: str
    observaciones_ejecucion: Optional[str] = None
    responsable_id: Optional[uuid.UUID] = None
    fecha_limite_ejecucion: Optional[date] = None


@strawberry.input
class CrearActaInput:
    reunion_id: uuid.UUID
    texto_acta: Optional[str] = None
    secretario_id: Optional[uuid.UUID] = None
    presidente_id: Optional[uuid.UUID] = None


@strawberry.input
class EmitirCertificadoInput:
    acta_id: uuid.UUID
    acuerdo_id: uuid.UUID
    texto_certificado: str
    destinatario: Optional[str] = None
    proposito: Optional[str] = None
    secretario_id: Optional[uuid.UUID] = None
    presidente_id: Optional[uuid.UUID] = None


@strawberry.input
class RegistrarConvenioInput:
    tipo_convenio_id: uuid.UUID
    titulo: str
    entidad_contraparte: str
    fecha_firma: date
    fecha_inicio: date
    cif_contraparte: Optional[str] = None
    fecha_fin: Optional[date] = None
    renovacion_automatica: bool = False
    dias_preaviso_no_renovacion: Optional[int] = None
    objeto: Optional[str] = None
    obligaciones_asociacion: Optional[str] = None
    obligaciones_contraparte: Optional[str] = None
    firmante_id: Optional[uuid.UUID] = None
    acuerdo_autorizacion_id: Optional[uuid.UUID] = None
    observaciones: Optional[str] = None


@strawberry.input
class CrearDelegacionInput:
    delegante_id: uuid.UUID
    delegado_id: uuid.UUID
    descripcion_actos: str
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    limite_importe: Optional[float] = None
    acuerdo_autorizacion_id: Optional[uuid.UUID] = None
    observaciones: Optional[str] = None


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

@strawberry.type
class SecretariaQuery:

    @strawberry.field(permission_classes=[RequireTransaction("SEC_REUNION_LISTAR")])
    async def tipos_reunion(self, info: strawberry.Info) -> List[TipoReunionGQL]:
        svc = ReunionService(info.context.session)
        tipos = await svc.listar_tipos_reunion()
        return [TipoReunionGQL.from_model(t) for t in tipos]

    @strawberry.field(permission_classes=[RequireTransaction("SEC_REUNION_LISTAR")])
    async def reuniones(
        self,
        info: strawberry.Info,
        anio: Optional[int] = None,
        tipo_reunion_id: Optional[uuid.UUID] = None,
        agrupacion_id: Optional[uuid.UUID] = None,
        estado_codigo: Optional[str] = None,
    ) -> List[ReunionGQL]:
        svc = ReunionService(info.context.session)
        items = await svc.listar_reuniones(
            anio=anio, tipo_reunion_id=tipo_reunion_id,
            agrupacion_id=agrupacion_id, estado=estado_codigo,
        )
        return [ReunionGQL.from_model(r) for r in items]

    @strawberry.field(permission_classes=[RequireTransaction("SEC_ACUERDO_LISTAR")])
    async def acuerdos_pendientes(
        self,
        info: strawberry.Info,
        agrupacion_id: Optional[uuid.UUID] = None,
    ) -> List[AcuerdoGQL]:
        svc = ReunionService(info.context.session)
        items = await svc.listar_acuerdos_pendientes(agrupacion_id=agrupacion_id)
        return [AcuerdoGQL.from_model(a) for a in items]

    @strawberry.field(permission_classes=[RequireTransaction("SEC_ACTA_LISTAR")])
    async def actas(
        self,
        info: strawberry.Info,
        anio: Optional[int] = None,
        estado_codigo: Optional[str] = None,
    ) -> List[ActaGQL]:
        svc = ActaService(info.context.session)
        items = await svc.listar_actas(anio=anio, estado=estado_codigo)
        return [ActaGQL.from_model(a) for a in items]

    @strawberry.field(permission_classes=[RequireTransaction("SEC_ACTA_LISTAR")])
    async def actas_pendientes_aprobacion(
        self, info: strawberry.Info
    ) -> List[ActaGQL]:
        svc = ActaService(info.context.session)
        items = await svc.listar_pendientes_aprobacion()
        return [ActaGQL.from_model(a) for a in items]

    @strawberry.field(permission_classes=[RequireTransaction("SEC_CERTIFICADO_LISTAR")])
    async def certificados_acuerdo(
        self,
        info: strawberry.Info,
        acta_id: Optional[uuid.UUID] = None,
        anio: Optional[int] = None,
    ) -> List[CertificadoGQL]:
        svc = ActaService(info.context.session)
        items = await svc.listar_certificados(acta_id=acta_id, anio=anio)
        return [CertificadoGQL.from_model(c) for c in items]

    @strawberry.field(permission_classes=[RequireTransaction("SEC_LIBRO_SOCIOS_CONSULTAR")])
    async def libro_socios_snapshots(
        self, info: strawberry.Info
    ) -> List[LibroSociosSnapshotGQL]:
        svc = LibroSociosService(info.context.session)
        items = await svc.listar_snapshots()
        return [LibroSociosSnapshotGQL.from_model(s) for s in items]

    @strawberry.field(permission_classes=[RequireTransaction("SEC_CONVENIO_LISTAR")])
    async def convenios(
        self,
        info: strawberry.Info,
        estado: Optional[str] = None,
        proximos_a_vencer_dias: Optional[int] = None,
    ) -> List[ConvenioGQL]:
        svc = ConvenioService(info.context.session)
        items = await svc.listar_convenios(
            estado=estado, proximos_a_vencer_dias=proximos_a_vencer_dias
        )
        return [ConvenioGQL.from_model(c) for c in items]

    @strawberry.field(permission_classes=[RequireTransaction("SEC_DELEGACION_LISTAR")])
    async def delegaciones_firma(
        self,
        info: strawberry.Info,
        activas_solo: bool = True,
        delegado_id: Optional[uuid.UUID] = None,
    ) -> List[DelegacionFirmaGQL]:
        svc = ConvenioService(info.context.session)
        items = await svc.listar_delegaciones(
            activas_solo=activas_solo, delegado_id=delegado_id
        )
        return [DelegacionFirmaGQL.from_model(d) for d in items]


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------

@strawberry.type
class SecretariaResolverMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_REUNION_CREAR")])
    async def convocar_reunion(
        self, info: strawberry.Info, data: ConvocarReunionInput
    ) -> ReunionGQL:
        svc = ReunionService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        reunion = await svc.convocar_reunion(
            tipo_reunion_id=data.tipo_reunion_id,
            fecha_convocatoria=data.fecha_convocatoria,
            fecha_celebracion=data.fecha_celebracion,
            lugar=data.lugar,
            es_telematica=data.es_telematica,
            plataforma_telematica=data.plataforma_telematica,
            tiene_segunda_convocatoria=data.tiene_segunda_convocatoria,
            fecha_segunda_convocatoria=data.fecha_segunda_convocatoria,
            agrupacion_id=data.agrupacion_id,
            observaciones=data.observaciones,
            creado_por_id=usuario_id,
        )
        return ReunionGQL.from_model(reunion)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_REUNION_REGISTRAR_ASIST")])
    async def registrar_celebracion_reunion(
        self, info: strawberry.Info, data: RegistrarCelebracionInput
    ) -> ReunionGQL:
        svc = ReunionService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        reunion = await svc.registrar_celebracion(
            reunion_id=data.reunion_id,
            socios_totales=data.socios_totales,
            socios_presentes=data.socios_presentes,
            socios_representados=data.socios_representados,
            convocatoria_utilizada=data.convocatoria_utilizada,
            modificado_por_id=usuario_id,
        )
        return ReunionGQL.from_model(reunion)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_REUNION_CANCELAR")])
    async def cancelar_reunion(
        self,
        info: strawberry.Info,
        reunion_id: uuid.UUID,
        motivo: Optional[str] = None,
    ) -> ReunionGQL:
        svc = ReunionService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        reunion = await svc.cancelar_reunion(
            reunion_id=reunion_id, motivo=motivo, modificado_por_id=usuario_id
        )
        return ReunionGQL.from_model(reunion)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_ACUERDO_CREAR")])
    async def registrar_acuerdo(
        self, info: strawberry.Info, data: RegistrarAcuerdoInput
    ) -> AcuerdoGQL:
        svc = ReunionService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        acuerdo = await svc.registrar_acuerdo(
            punto_orden_dia_id=data.punto_orden_dia_id,
            descripcion=data.descripcion,
            tipo_mayoria=data.tipo_mayoria,
            resultado=data.resultado,
            votos_favor=data.votos_favor,
            votos_contra=data.votos_contra,
            abstenciones=data.abstenciones,
            votos_nulos=data.votos_nulos,
            es_votacion_secreta=data.es_votacion_secreta,
            responsable_id=data.responsable_id,
            fecha_limite_ejecucion=data.fecha_limite_ejecucion,
            creado_por_id=usuario_id,
        )
        return AcuerdoGQL.from_model(acuerdo)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_ACUERDO_SEGUIMIENTO")])
    async def actualizar_seguimiento_acuerdo(
        self, info: strawberry.Info, data: ActualizarSeguimientoInput
    ) -> AcuerdoGQL:
        svc = ReunionService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        acuerdo = await svc.actualizar_seguimiento_acuerdo(
            acuerdo_id=data.acuerdo_id,
            estado_ejecucion=data.estado_ejecucion,
            observaciones_ejecucion=data.observaciones_ejecucion,
            responsable_id=data.responsable_id,
            fecha_limite_ejecucion=data.fecha_limite_ejecucion,
            modificado_por_id=usuario_id,
        )
        return AcuerdoGQL.from_model(acuerdo)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_ACTA_CREAR")])
    async def crear_acta_borrador(
        self, info: strawberry.Info, data: CrearActaInput
    ) -> ActaGQL:
        svc = ActaService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        acta = await svc.crear_acta_borrador(
            reunion_id=data.reunion_id,
            texto_acta=data.texto_acta,
            secretario_id=data.secretario_id,
            presidente_id=data.presidente_id,
            creado_por_id=usuario_id,
        )
        return ActaGQL.from_model(acta)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_ACTA_APROBAR")])
    async def aprobar_acta(
        self,
        info: strawberry.Info,
        acta_id: uuid.UUID,
        fecha_aprobacion: date,
        reunion_aprobacion_id: Optional[uuid.UUID] = None,
    ) -> ActaGQL:
        svc = ActaService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        acta = await svc.aprobar_acta(
            acta_id=acta_id,
            fecha_aprobacion=fecha_aprobacion,
            reunion_aprobacion_id=reunion_aprobacion_id,
            modificado_por_id=usuario_id,
        )
        return ActaGQL.from_model(acta)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_ACTA_FIRMAR")])
    async def firmar_acta(
        self,
        info: strawberry.Info,
        acta_id: uuid.UUID,
        secretario_id: uuid.UUID,
        presidente_id: uuid.UUID,
    ) -> ActaGQL:
        svc = ActaService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        acta = await svc.firmar_acta(
            acta_id=acta_id,
            secretario_id=secretario_id,
            presidente_id=presidente_id,
            modificado_por_id=usuario_id,
        )
        return ActaGQL.from_model(acta)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_CERTIFICADO_EMITIR")])
    async def emitir_certificado_acuerdo(
        self, info: strawberry.Info, data: EmitirCertificadoInput
    ) -> CertificadoGQL:
        svc = ActaService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        cert = await svc.emitir_certificado(
            acta_id=data.acta_id,
            acuerdo_id=data.acuerdo_id,
            texto_certificado=data.texto_certificado,
            destinatario=data.destinatario,
            proposito=data.proposito,
            secretario_id=data.secretario_id,
            presidente_id=data.presidente_id,
            creado_por_id=usuario_id,
        )
        return CertificadoGQL.from_model(cert)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_LIBRO_SOCIOS_GENERAR")])
    async def generar_libro_socios(
        self,
        info: strawberry.Info,
        fecha_corte: Optional[date] = None,
        motivo: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> LibroSociosSnapshotGQL:
        svc = LibroSociosService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        snapshot = await svc.generar_snapshot(
            fecha_corte=fecha_corte, motivo=motivo,
            observaciones=observaciones, creado_por_id=usuario_id,
        )
        return LibroSociosSnapshotGQL.from_model(snapshot)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_CONVENIO_CREAR")])
    async def registrar_convenio(
        self, info: strawberry.Info, data: RegistrarConvenioInput
    ) -> ConvenioGQL:
        svc = ConvenioService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        convenio = await svc.registrar_convenio(
            tipo_convenio_id=data.tipo_convenio_id,
            titulo=data.titulo,
            entidad_contraparte=data.entidad_contraparte,
            fecha_firma=data.fecha_firma,
            fecha_inicio=data.fecha_inicio,
            cif_contraparte=data.cif_contraparte,
            fecha_fin=data.fecha_fin,
            renovacion_automatica=data.renovacion_automatica,
            dias_preaviso_no_renovacion=data.dias_preaviso_no_renovacion,
            objeto=data.objeto,
            obligaciones_asociacion=data.obligaciones_asociacion,
            obligaciones_contraparte=data.obligaciones_contraparte,
            firmante_id=data.firmante_id,
            acuerdo_autorizacion_id=data.acuerdo_autorizacion_id,
            observaciones=data.observaciones,
            creado_por_id=usuario_id,
        )
        return ConvenioGQL.from_model(convenio)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_CONVENIO_EDITAR")])
    async def cambiar_estado_convenio(
        self,
        info: strawberry.Info,
        convenio_id: uuid.UUID,
        nuevo_estado: str,
    ) -> ConvenioGQL:
        svc = ConvenioService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        convenio = await svc.cambiar_estado_convenio(
            convenio_id=convenio_id,
            nuevo_estado=nuevo_estado,
            modificado_por_id=usuario_id,
        )
        return ConvenioGQL.from_model(convenio)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_DELEGACION_GESTIONAR")])
    async def crear_delegacion_firma(
        self, info: strawberry.Info, data: CrearDelegacionInput
    ) -> DelegacionFirmaGQL:
        svc = ConvenioService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        delegacion = await svc.crear_delegacion(
            delegante_id=data.delegante_id,
            delegado_id=data.delegado_id,
            descripcion_actos=data.descripcion_actos,
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
            limite_importe=data.limite_importe,
            acuerdo_autorizacion_id=data.acuerdo_autorizacion_id,
            observaciones=data.observaciones,
            creado_por_id=usuario_id,
        )
        return DelegacionFirmaGQL.from_model(delegacion)

    @strawberry.mutation(permission_classes=[RequireTransaction("SEC_DELEGACION_GESTIONAR")])
    async def revocar_delegacion_firma(
        self,
        info: strawberry.Info,
        delegacion_id: uuid.UUID,
    ) -> DelegacionFirmaGQL:
        svc = ConvenioService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        delegacion = await svc.revocar_delegacion(
            delegacion_id=delegacion_id, modificado_por_id=usuario_id
        )
        return DelegacionFirmaGQL.from_model(delegacion)
