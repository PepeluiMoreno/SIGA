"""Resolvers GraphQL del módulo Protección de Datos (RGPD).

Mutations custom (las que tienen lógica más allá del CRUD):
- Solicitudes ARSULIPO: tramitar, prorrogar, resolver/denegar (con cómputo
  automático de fecha límite de respuesta a 1 mes / prorrogable a 3).
- Consentimientos: retirar.
- Brechas: notificar a la AEPD, cerrar.
- Auditoría: registrar acceso (utilidad para que otros módulos llamen).
- Genera códigos internos legibles (ARS-2026-NNNN / BRE-2026-NNNN).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import Optional

import strawberry
from sqlalchemy import select, func

from .context import Context
from .permissions import RequireTransaction
from .types_auto import (
    SolicitudDerechoRGPDType,
    ConsentimientoType,
    BrechaSeguridadType,
    AuditoriaAccesoDatosType,
)
from ..modules.proteccion_datos.models import (
    SolicitudDerechoRGPD,
    Consentimiento,
    BrechaSeguridad,
    AuditoriaAccesoDatos,
)
from ..modules.proteccion_datos.models.solicitud_derecho import (
    TIPOS_DERECHO, ESTADOS_SOLICITUD, CANALES_PRESENTACION,
)
from ..modules.proteccion_datos.models.brecha import ORIGENES_BRECHA, SEVERIDADES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _add_months(d: date, months: int) -> date:
    """Suma `months` meses a una fecha conservando el día (clampado al fin de mes)."""
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    # Día clampado al último día válido del nuevo mes
    if month == 12:
        last_day = 31
    else:
        last_day = (date(year, month + 1, 1) - timedelta(days=1)).day
    return date(year, month, min(d.day, last_day))


async def _siguiente_codigo(session, modelo, prefijo: str) -> str:
    """Genera un código legible PREFIJO-YYYY-NNNN buscando el máximo del año."""
    anio = date.today().year
    like_pattern = f"{prefijo}-{anio}-%"
    result = await session.execute(
        select(func.count(modelo.id)).where(modelo.codigo_interno.like(like_pattern))
    )
    n = (result.scalar() or 0) + 1
    return f"{prefijo}-{anio}-{n:04d}"


# ---------------------------------------------------------------------------
# Mutation type
# ---------------------------------------------------------------------------

@strawberry.type
class ProteccionDatosMutation:
    """Operaciones custom del módulo RGPD."""

    # -----------------------------------------------------------------
    # Solicitudes de derechos (ARSULIPO)
    # -----------------------------------------------------------------

    @strawberry.mutation(permission_classes=[RequireTransaction("RGPD_SOLICITUD_REGISTRAR")])
    async def registrar_solicitud_derecho_rgpd(
        self,
        info: strawberry.Info,
        tipo: str,
        nombre_solicitante: str,
        fecha_presentacion: date,
        canal_presentacion: str = "EMAIL",
        miembro_id: Optional[uuid.UUID] = None,
        usuario_id: Optional[uuid.UUID] = None,
        documento_solicitante: Optional[str] = None,
        email_solicitante: Optional[str] = None,
        telefono_solicitante: Optional[str] = None,
        descripcion_solicitud: Optional[str] = None,
    ) -> SolicitudDerechoRGPDType:
        if tipo not in TIPOS_DERECHO:
            raise ValueError(f"Tipo de derecho inválido. Permitidos: {TIPOS_DERECHO}")
        if canal_presentacion not in CANALES_PRESENTACION:
            raise ValueError(f"Canal de presentación inválido. Permitidos: {CANALES_PRESENTACION}")

        ctx: Context = info.context
        codigo = await _siguiente_codigo(ctx.session, SolicitudDerechoRGPD, "ARS")

        solicitud = SolicitudDerechoRGPD(
            id=uuid.uuid4(),
            codigo_interno=codigo,
            tipo=tipo,
            estado="PRESENTADA",
            miembro_id=miembro_id,
            usuario_id=usuario_id,
            nombre_solicitante=nombre_solicitante,
            documento_solicitante=documento_solicitante,
            email_solicitante=email_solicitante,
            telefono_solicitante=telefono_solicitante,
            canal_presentacion=canal_presentacion,
            fecha_presentacion=fecha_presentacion,
            fecha_limite_respuesta=_add_months(fecha_presentacion, 1),
            descripcion_solicitud=descripcion_solicitud,
            creado_por_id=uuid.UUID(ctx.user_id) if ctx.user_id else None,
        )
        ctx.session.add(solicitud)
        await ctx.session.flush()
        return solicitud  # type: ignore[return-value]

    @strawberry.mutation(permission_classes=[RequireTransaction("RGPD_SOLICITUD_TRAMITAR")])
    async def iniciar_tramite_solicitud_rgpd(
        self,
        info: strawberry.Info,
        solicitud_id: uuid.UUID,
    ) -> SolicitudDerechoRGPDType:
        ctx: Context = info.context
        solicitud = await ctx.session.get(SolicitudDerechoRGPD, solicitud_id)
        if not solicitud:
            raise ValueError("Solicitud no encontrada")
        if solicitud.estado != "PRESENTADA":
            raise ValueError(f"Solo se pueden iniciar trámites de solicitudes en estado PRESENTADA (actual: {solicitud.estado})")
        solicitud.estado = "EN_TRAMITE"
        if ctx.user_id:
            solicitud.tramitada_por_id = uuid.UUID(ctx.user_id)
            solicitud.modificado_por_id = uuid.UUID(ctx.user_id)
        await ctx.session.flush()
        return solicitud  # type: ignore[return-value]

    @strawberry.mutation(permission_classes=[RequireTransaction("RGPD_SOLICITUD_TRAMITAR")])
    async def prorrogar_solicitud_rgpd(
        self,
        info: strawberry.Info,
        solicitud_id: uuid.UUID,
        motivo_prorroga: str,
    ) -> SolicitudDerechoRGPDType:
        """Prórroga del plazo de respuesta: de 1 mes a 3 meses (art. 12.3 RGPD)."""
        ctx: Context = info.context
        solicitud = await ctx.session.get(SolicitudDerechoRGPD, solicitud_id)
        if not solicitud:
            raise ValueError("Solicitud no encontrada")
        if solicitud.estado not in ("PRESENTADA", "EN_TRAMITE"):
            raise ValueError("Solo se pueden prorrogar solicitudes presentadas o en trámite")
        if solicitud.prorrogada:
            raise ValueError("Esta solicitud ya está prorrogada")
        solicitud.prorrogada = True
        solicitud.fecha_limite_prorroga = _add_months(solicitud.fecha_presentacion, 3)
        solicitud.motivo_prorroga = motivo_prorroga
        solicitud.estado = "PRORROGADA"
        if ctx.user_id:
            solicitud.modificado_por_id = uuid.UUID(ctx.user_id)
        await ctx.session.flush()
        return solicitud  # type: ignore[return-value]

    @strawberry.mutation(permission_classes=[RequireTransaction("RGPD_SOLICITUD_RESOLVER")])
    async def resolver_solicitud_rgpd(
        self,
        info: strawberry.Info,
        solicitud_id: uuid.UUID,
        resolucion: str,
        denegada: bool = False,
        documento_resolucion_url: Optional[str] = None,
    ) -> SolicitudDerechoRGPDType:
        ctx: Context = info.context
        solicitud = await ctx.session.get(SolicitudDerechoRGPD, solicitud_id)
        if not solicitud:
            raise ValueError("Solicitud no encontrada")
        if solicitud.estado in ("RESUELTA", "DENEGADA"):
            raise ValueError("Esta solicitud ya está cerrada")
        solicitud.estado = "DENEGADA" if denegada else "RESUELTA"
        solicitud.resolucion = resolucion
        solicitud.documento_resolucion_url = documento_resolucion_url
        solicitud.fecha_resolucion = datetime.utcnow()
        if ctx.user_id:
            solicitud.tramitada_por_id = uuid.UUID(ctx.user_id)
            solicitud.modificado_por_id = uuid.UUID(ctx.user_id)
        await ctx.session.flush()
        return solicitud  # type: ignore[return-value]

    # -----------------------------------------------------------------
    # Consentimientos
    # -----------------------------------------------------------------

    @strawberry.mutation(permission_classes=[RequireTransaction("RGPD_CONSENTIMIENTO_REGISTRAR")])
    async def retirar_consentimiento_rgpd(
        self,
        info: strawberry.Info,
        consentimiento_id: uuid.UUID,
    ) -> ConsentimientoType:
        ctx: Context = info.context
        consentimiento = await ctx.session.get(Consentimiento, consentimiento_id)
        if not consentimiento:
            raise ValueError("Consentimiento no encontrado")
        if consentimiento.estado == "RETIRADO":
            raise ValueError("El consentimiento ya está retirado")
        consentimiento.estado = "RETIRADO"
        consentimiento.fecha_retirada = datetime.utcnow()
        if ctx.user_id:
            consentimiento.modificado_por_id = uuid.UUID(ctx.user_id)
        await ctx.session.flush()
        return consentimiento  # type: ignore[return-value]

    # -----------------------------------------------------------------
    # Brechas de seguridad
    # -----------------------------------------------------------------

    @strawberry.mutation(permission_classes=[RequireTransaction("RGPD_BRECHA_REGISTRAR")])
    async def registrar_brecha_seguridad(
        self,
        info: strawberry.Info,
        descripcion: str,
        origen: str,
        fecha_deteccion: datetime,
        severidad: str = "MEDIA",
        fecha_ocurrencia: Optional[date] = None,
        datos_afectados: Optional[str] = None,
        personas_afectadas_num: Optional[int] = None,
        datos_sensibles_afectados: bool = False,
        medidas_inmediatas: Optional[str] = None,
    ) -> BrechaSeguridadType:
        if origen not in ORIGENES_BRECHA:
            raise ValueError(f"Origen inválido. Permitidos: {ORIGENES_BRECHA}")
        if severidad not in SEVERIDADES:
            raise ValueError(f"Severidad inválida. Permitidas: {SEVERIDADES}")

        ctx: Context = info.context
        codigo = await _siguiente_codigo(ctx.session, BrechaSeguridad, "BRE")

        brecha = BrechaSeguridad(
            id=uuid.uuid4(),
            codigo_interno=codigo,
            descripcion=descripcion,
            origen=origen,
            severidad=severidad,
            fecha_deteccion=fecha_deteccion,
            fecha_ocurrencia=fecha_ocurrencia,
            datos_afectados=datos_afectados,
            personas_afectadas_num=personas_afectadas_num,
            datos_sensibles_afectados=datos_sensibles_afectados,
            medidas_inmediatas=medidas_inmediatas,
            detectada_por_id=uuid.UUID(ctx.user_id) if ctx.user_id else None,
            creado_por_id=uuid.UUID(ctx.user_id) if ctx.user_id else None,
        )
        ctx.session.add(brecha)
        await ctx.session.flush()
        return brecha  # type: ignore[return-value]

    @strawberry.mutation(permission_classes=[RequireTransaction("RGPD_BRECHA_NOTIFICAR_AEPD")])
    async def notificar_brecha_aepd(
        self,
        info: strawberry.Info,
        brecha_id: uuid.UUID,
        fecha_notificacion: datetime,
        referencia_aepd: Optional[str] = None,
        documento_url: Optional[str] = None,
    ) -> BrechaSeguridadType:
        ctx: Context = info.context
        brecha = await ctx.session.get(BrechaSeguridad, brecha_id)
        if not brecha:
            raise ValueError("Brecha no encontrada")
        brecha.notificada_aepd = True
        brecha.fecha_notificacion_aepd = fecha_notificacion
        brecha.referencia_aepd = referencia_aepd
        brecha.notificacion_aepd_documento_url = documento_url
        if ctx.user_id:
            brecha.modificado_por_id = uuid.UUID(ctx.user_id)
        await ctx.session.flush()
        return brecha  # type: ignore[return-value]

    @strawberry.mutation(permission_classes=[RequireTransaction("RGPD_BRECHA_CERRAR")])
    async def cerrar_brecha_seguridad(
        self,
        info: strawberry.Info,
        brecha_id: uuid.UUID,
        medidas_correctivas: str,
    ) -> BrechaSeguridadType:
        ctx: Context = info.context
        brecha = await ctx.session.get(BrechaSeguridad, brecha_id)
        if not brecha:
            raise ValueError("Brecha no encontrada")
        if brecha.cerrada:
            raise ValueError("La brecha ya está cerrada")
        brecha.medidas_correctivas = medidas_correctivas
        brecha.cerrada = True
        brecha.fecha_cierre = datetime.utcnow()
        if ctx.user_id:
            brecha.responsable_gestion_id = uuid.UUID(ctx.user_id)
            brecha.modificado_por_id = uuid.UUID(ctx.user_id)
        await ctx.session.flush()
        return brecha  # type: ignore[return-value]

    # -----------------------------------------------------------------
    # Auditoría de accesos
    # -----------------------------------------------------------------

    @strawberry.mutation
    async def registrar_acceso_datos_personales(
        self,
        info: strawberry.Info,
        entidad: str,
        entidad_id: Optional[uuid.UUID] = None,
        tipo_acceso: str = "LECTURA",
        campos_accedidos: Optional[str] = None,
        motivo: Optional[str] = None,
    ) -> AuditoriaAccesoDatosType:
        """Append-only. Cualquier usuario autenticado puede registrar su propio acceso."""
        ctx: Context = info.context
        if not ctx.is_authenticated:
            raise PermissionError("Se requiere autenticación para registrar accesos")

        request = info.context.request if hasattr(info.context, 'request') else None
        ip = None
        user_agent = None
        if request is not None:
            ip = request.client.host if request.client else None
            user_agent = request.headers.get('user-agent')

        log = AuditoriaAccesoDatos(
            id=uuid.uuid4(),
            usuario_id=uuid.UUID(ctx.user_id) if ctx.user_id else None,
            usuario_email_snapshot=ctx.user.email if ctx.user and hasattr(ctx.user, 'email') else None,
            entidad=entidad,
            entidad_id=entidad_id,
            tipo_acceso=tipo_acceso,
            campos_accedidos=campos_accedidos,
            motivo=motivo,
            ip=ip,
            user_agent=user_agent,
        )
        ctx.session.add(log)
        await ctx.session.flush()
        return log  # type: ignore[return-value]
