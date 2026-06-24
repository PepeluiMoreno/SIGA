"""Read-model `socios`: vista denormalizada de un socio para el frontend.

En el modelo CRM la identidad vive en `Contacto` y los datos de socio se reparten
entre `Vinculacion(SOCIO)`, su satélite `Socio`, la `Membresia` (tipo de miembro) y,
opcionalmente, `Vinculacion(VOLUNTARIO)` + `Voluntario`. El frontend, sin embargo,
necesita un registro plano «tipo Miembro». Este módulo lo reconstruye con unas pocas
consultas por lote (sin N+1) y lo expone como `socios` / `socio(id)` / `sociosCount`.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

import strawberry
from sqlalchemy import select, func

from app.modules.membresia.models.contacto import Contacto
from app.modules.membresia.models.vinculacion import Vinculacion, Socio, Voluntario
from app.modules.membresia.models.tipo_vinculacion import TipoVinculacion
from app.modules.membresia.models.participacion import Participacion, Membresia
from app.modules.membresia.models.miembro import TipoMiembro
from app.modules.membresia.models.motivo_baja import MotivoBaja
from app.modules.membresia.models.nivel_estudios import NivelEstudios
from app.modules.economico.models.cuotas import MotivoReduccionCuota
from app.modules.core.geografico.direccion import UnidadOrganizativa
from app.modules.acceso.models.usuario import Usuario

from app.graphql.types_auto import (
    TipoMiembroType, UnidadOrganizativaType, MotivoBajaType, NivelEstudiosType,
    MotivoReduccionCuotaType, UsuarioType,
)
from app.graphql.permissions import RequireTransaction


# Mapa estado_socio -> color del badge (la situación ya no es un EstadoMiembro).
_ESTADO_COLOR = {
    "activo": "#28A745",
    "suspendido": "#FFA500",
    "baja": "#DC3545",
}


@strawberry.type
class EstadoSocioBadge:
    """Situación del socio derivada de `Socio.estado_socio` (no es un catálogo)."""
    id: Optional[uuid.UUID] = None
    nombre: str = ""
    color: str = "#6B7280"


@strawberry.type(name="SocioVista")
class SocioVistaType:
    # Identidad (Contacto)
    id: uuid.UUID
    nombre: str
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    foto_url: Optional[str] = None
    sexo: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    telefono2: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    codigo_postal: Optional[str] = None
    agrupacion_id: Optional[uuid.UUID] = None
    provincia_id: Optional[uuid.UUID] = None
    pais_documento_id: Optional[uuid.UUID] = None
    pais_domicilio_id: Optional[uuid.UUID] = None
    pais_nacimiento_id: Optional[uuid.UUID] = None
    profesion: Optional[str] = None
    nivel_estudios_id: Optional[uuid.UUID] = None
    activo: bool = True
    datos_anonimizados: bool = False
    solicita_supresion_datos: bool = False
    fecha_solicitud_supresion: Optional[date] = None
    fecha_limite_retencion: Optional[date] = None
    fecha_anonimizacion: Optional[date] = None
    fecha_creacion: Optional[datetime] = None
    fecha_modificacion: Optional[datetime] = None

    # Vinculación de socio
    vinculacion_socio_id: Optional[uuid.UUID] = None
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None

    # Satélite Socio (datos económicos)
    iban: Optional[str] = None
    swift_bic: Optional[str] = None
    referencia_pago: Optional[str] = None
    forma_pago_id: Optional[uuid.UUID] = None
    es_socio_honor: bool = False
    numero_socio: Optional[str] = None
    motivo_baja_id: Optional[uuid.UUID] = None
    motivo_baja_texto: Optional[str] = None
    motivo_reduccion_id: Optional[uuid.UUID] = None
    incremento_cuota: Optional[Decimal] = None
    incremento_cuota_obs: Optional[str] = None

    # Membresía (tipo de miembro)
    tipo_miembro_id: Optional[uuid.UUID] = None
    estado_id: Optional[uuid.UUID] = None

    # Voluntariado
    es_voluntario: bool = False
    disponibilidad: Optional[str] = None
    horas_disponibles_semana: Optional[int] = None
    intereses: Optional[str] = None
    experiencia_voluntariado: Optional[str] = None
    observaciones_voluntariado: Optional[str] = None
    puede_conducir: bool = False
    vehiculo_propio: bool = False
    disponibilidad_viajar: bool = False

    tiene_acceso: bool = False

    # Relaciones (objetos ORM resueltos por sus tipos strawchemy)
    tipo_miembro: Optional[TipoMiembroType] = None
    agrupacion: Optional[UnidadOrganizativaType] = None
    motivo_baja_rel: Optional[MotivoBajaType] = None
    motivo_reduccion: Optional[MotivoReduccionCuotaType] = None
    nivel_estudios_rel: Optional[NivelEstudiosType] = None
    usuario: Optional[UsuarioType] = None
    estado: Optional[EstadoSocioBadge] = None


async def _construir_socios(session, contacto_id: Optional[uuid.UUID] = None) -> List[SocioVistaType]:
    """Reconstruye los `SocioVistaType` con consultas por lote (sin N+1)."""
    # 1) Vinculaciones SOCIO (+ satélite + contacto)
    q = (
        select(Vinculacion)
        .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
        .where(TipoVinculacion.codigo == "SOCIO", Vinculacion.eliminado == False)  # noqa: E712
    )
    if contacto_id is not None:
        q = q.where(Vinculacion.contacto_id == contacto_id)
    vincs = list((await session.execute(q)).scalars().all())
    if not vincs:
        return []

    contacto_ids = [v.contacto_id for v in vincs]

    # 2) Membresía por contacto (tipo de miembro)
    memb_rows = (await session.execute(
        select(Participacion.contacto_id, Membresia)
        .join(Membresia, Membresia.participacion_id == Participacion.id)
        .where(Participacion.contacto_id.in_(contacto_ids), Participacion.tipo == "MEMBRESIA")
    )).all()
    membresia_por_contacto = {cid: mb for (cid, mb) in memb_rows}

    # 3) Voluntario por contacto (vinculación VOLUNTARIO activa + satélite)
    vol_rows = (await session.execute(
        select(Vinculacion)
        .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
        .where(
            TipoVinculacion.codigo == "VOLUNTARIO",
            Vinculacion.estado == "activa",
            Vinculacion.contacto_id.in_(contacto_ids),
        )
    )).scalars().all()
    voluntario_por_contacto = {v.contacto_id: (v.voluntario if v.voluntario else None) for v in vol_rows}

    # 4) Usuario por contacto
    usr_rows = (await session.execute(
        select(Usuario).where(Usuario.contacto_id.in_(contacto_ids), Usuario.eliminado == False)  # noqa: E712
    )).scalars().all()
    usuario_por_contacto = {u.contacto_id: u for u in usr_rows}

    # 5) Agrupaciones, niveles de estudios y motivos de baja referenciados
    agr_ids = {v.contacto.agrupacion_id for v in vincs if v.contacto and v.contacto.agrupacion_id}
    agrupaciones = {}
    if agr_ids:
        agrupaciones = {u.id: u for u in (await session.execute(
            select(UnidadOrganizativa).where(UnidadOrganizativa.id.in_(agr_ids))
        )).scalars().all()}

    niv_ids = {v.contacto.nivel_estudios_id for v in vincs if v.contacto and v.contacto.nivel_estudios_id}
    niveles = {}
    if niv_ids:
        niveles = {n.id: n for n in (await session.execute(
            select(NivelEstudios).where(NivelEstudios.id.in_(niv_ids))
        )).scalars().all()}

    mb_ids = {v.socio.motivo_baja_id for v in vincs if v.socio and v.socio.motivo_baja_id}
    motivos_baja = {}
    if mb_ids:
        motivos_baja = {m.id: m for m in (await session.execute(
            select(MotivoBaja).where(MotivoBaja.id.in_(mb_ids))
        )).scalars().all()}

    socios: List[SocioVistaType] = []
    for v in vincs:
        c = v.contacto
        if not c:
            continue
        s = v.socio
        memb = membresia_por_contacto.get(c.id)
        vol = voluntario_por_contacto.get(c.id)
        usr = usuario_por_contacto.get(c.id)
        estado_socio = (s.estado_socio if s else None) or ("baja" if v.fecha_fin else "activo")

        socios.append(SocioVistaType(
            id=c.id, nombre=c.nombre, apellido1=c.apellido1, apellido2=c.apellido2,
            foto_url=c.foto_url, sexo=c.sexo, email=c.email, telefono=c.telefono,
            telefono2=c.telefono2, fecha_nacimiento=c.fecha_nacimiento,
            tipo_documento=c.tipo_documento, numero_documento=c.numero_documento,
            direccion=c.direccion, localidad=c.localidad, codigo_postal=c.codigo_postal,
            agrupacion_id=c.agrupacion_id, provincia_id=c.provincia_id,
            pais_documento_id=c.pais_documento_id, pais_domicilio_id=c.pais_domicilio_id,
            pais_nacimiento_id=c.pais_nacimiento_id, profesion=c.profesion,
            nivel_estudios_id=c.nivel_estudios_id, activo=c.activo,
            datos_anonimizados=c.datos_anonimizados,
            solicita_supresion_datos=c.solicita_supresion_datos,
            fecha_solicitud_supresion=c.fecha_solicitud_supresion,
            fecha_limite_retencion=c.fecha_limite_retencion,
            fecha_anonimizacion=c.fecha_anonimizacion,
            fecha_creacion=c.fecha_creacion, fecha_modificacion=c.fecha_modificacion,
            vinculacion_socio_id=v.id, fecha_alta=v.fecha_inicio, fecha_baja=v.fecha_fin,
            iban=(s.iban if s else None), swift_bic=(s.swift_bic if s else None),
            referencia_pago=(s.referencia_pago if s else None),
            forma_pago_id=(s.forma_pago_id if s else None),
            es_socio_honor=bool(s.es_honor) if s else False,
            numero_socio=(s.numero_socio if s else None),
            motivo_baja_id=(s.motivo_baja_id if s else None),
            motivo_baja_texto=(s.motivo_baja_texto if s else None),
            motivo_reduccion_id=(s.motivo_reduccion_id if s else None),
            incremento_cuota=(s.incremento_cuota if s else None),
            incremento_cuota_obs=(s.incremento_cuota_obs if s else None),
            tipo_miembro_id=(memb.tipo_miembro_id if memb else None),
            estado_id=None,
            es_voluntario=vol is not None,
            disponibilidad=(vol.disponibilidad if vol else None),
            horas_disponibles_semana=(vol.horas_disponibles_semana if vol else None),
            intereses=(vol.intereses if vol else None),
            experiencia_voluntariado=(vol.experiencia_voluntariado if vol else None),
            observaciones_voluntariado=(vol.observaciones_voluntariado if vol else None),
            puede_conducir=bool(vol.puede_conducir) if vol else False,
            vehiculo_propio=bool(vol.vehiculo_propio) if vol else False,
            disponibilidad_viajar=bool(vol.disponibilidad_viajar) if vol else False,
            tiene_acceso=usr is not None,
            tipo_miembro=(memb.tipo_miembro if memb else None),
            agrupacion=agrupaciones.get(c.agrupacion_id),
            motivo_baja_rel=(motivos_baja.get(s.motivo_baja_id) if s else None),
            motivo_reduccion=(s.motivo_reduccion if s else None),
            nivel_estudios_rel=niveles.get(c.nivel_estudios_id),
            usuario=usr,
            estado=EstadoSocioBadge(
                nombre=estado_socio.capitalize(),
                color=_ESTADO_COLOR.get(estado_socio, "#6B7280"),
            ),
        ))
    return socios


@strawberry.type
class SociosQuery:
    @strawberry.field(permission_classes=[RequireTransaction("SOC_VIEW")])
    async def socios(self, info: strawberry.Info) -> List[SocioVistaType]:
        """Listado denormalizado de socios (sustituye a la antigua query `miembros`)."""
        return await _construir_socios(info.context.session)

    @strawberry.field(permission_classes=[RequireTransaction("SOC_VIEW")])
    async def socio(self, info: strawberry.Info, id: uuid.UUID) -> Optional[SocioVistaType]:
        """Un socio por id de contacto."""
        res = await _construir_socios(info.context.session, contacto_id=id)
        return res[0] if res else None

    @strawberry.field(permission_classes=[RequireTransaction("SOC_VIEW")])
    async def socios_count(self, info: strawberry.Info) -> int:
        """Nº de vinculaciones de socio (no eliminadas)."""
        session = info.context.session
        return (await session.execute(
            select(func.count(Vinculacion.id))
            .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
            .where(TipoVinculacion.codigo == "SOCIO", Vinculacion.eliminado == False)  # noqa: E712
        )).scalar() or 0
