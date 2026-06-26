"""Resolvers GraphQL para parámetros de configuración de la organización.

Responsabilidad única: traducir peticiones GraphQL en llamadas al
ConfiguracionService. Ninguna lógica de negocio ni acceso directo a BD aquí.
"""

from __future__ import annotations

import uuid
from typing import Optional

import strawberry

from app.modules.configuracion.services.configuracion_service import ConfiguracionService
from app.modules.configuracion.services.indico_client import IndicoClient
from app.core.email_service import _load_smtp_config
from app.graphql.permissions import RequireTransaction


# ---------------------------------------------------------------------------
# Tipos de salida
# ---------------------------------------------------------------------------

@strawberry.type
class ParametrosOrganizacion:
    nombre: str
    nif: str
    numero_registro: str
    tipo_entidad: str
    contabilidad_compleja: bool
    usa_presupuesto: bool
    chat_activo: bool
    sede_social: str
    localidad: str
    cp: str
    provincia: str
    pais: str
    telefono: str
    email: str
    web: str
    rrss_twitter: str
    rrss_facebook: str
    rrss_instagram: str
    rrss_linkedin: str
    rrss_youtube: str
    rrss_telegram: str
    logo: str
    implantacion_geografica: str
    tipo_unidad_organizativa: Optional[str]
    denominacion_miembro: str
    denominacion_miembro_plural: str
    multiterritorial: bool
    auth_modo: str
    auth_authelia_url: str
    auth_oidc_issuer: str
    smtp_host: str
    smtp_port: str
    smtp_usuario: str
    smtp_password: str
    smtp_from: str
    smtp_tls: bool
    smtp_ssl: bool
    indico_activo: bool
    indico_url: str
    indico_api_token: str
    edad_max_joven: int
    denominacion_organo_gobierno: str
    denominacion_organo_gobierno_plural: str
    session_inactividad_minutos: int
    session_maximo_minutos: int
    tema: str
    fuente_principal: str
    sepa_creditor_name: str
    sepa_creditor_iban: str
    sepa_creditor_bic: str
    sepa_creditor_id: str
    openbanking_activo: bool
    rgpd_dpd_nombre: str
    rgpd_dpd_email: str
    rgpd_dpd_telefono: str
    rgpd_dpd_externo: bool
    rgpd_anios_retencion_baja: int


def _dict_to_parametros(cfg: dict) -> ParametrosOrganizacion:
    """Convierte el dict devuelto por ConfiguracionService al tipo GraphQL."""
    return ParametrosOrganizacion(
        nombre=cfg.get('org.nombre', ''),
        nif=cfg.get('org.nif', ''),
        numero_registro=cfg.get('org.numero_registro', ''),
        tipo_entidad=cfg.get('org.tipo_entidad', 'ASOCIACION'),
        contabilidad_compleja=bool(cfg.get('org.contabilidad_compleja', False)),
        usa_presupuesto=bool(cfg.get('org.usa_presupuesto', False)),
        chat_activo=str(cfg.get('chat.activo', '')).strip().lower() in ('1', 'true', 'si', 'sí', 'on'),
        sede_social=cfg.get('org.sede_social', ''),
        localidad=cfg.get('org.localidad', ''),
        cp=cfg.get('org.cp', ''),
        provincia=cfg.get('org.provincia', ''),
        pais=cfg.get('org.pais', 'España'),
        telefono=cfg.get('org.telefono', ''),
        email=cfg.get('org.email', ''),
        web=cfg.get('org.web', ''),
        rrss_twitter=cfg.get('org.rrss.twitter', ''),
        rrss_facebook=cfg.get('org.rrss.facebook', ''),
        rrss_instagram=cfg.get('org.rrss.instagram', ''),
        rrss_linkedin=cfg.get('org.rrss.linkedin', ''),
        rrss_youtube=cfg.get('org.rrss.youtube', ''),
        rrss_telegram=cfg.get('org.rrss.telegram', ''),
        logo=cfg.get('org.logo', ''),
        implantacion_geografica=cfg.get('org.implantacion_geografica', ''),
        tipo_unidad_organizativa=cfg.get('_tipo_unidad_organizativa_derivado', ''),
        denominacion_miembro=cfg.get('org.denominacion_miembro', 'miembro'),
        denominacion_miembro_plural=cfg.get('org.denominacion_miembro_plural', 'miembros'),
        multiterritorial=bool(cfg.get('org.multiterritorial', False)),
        auth_modo=cfg.get('auth.modo', 'LOCAL'),
        auth_authelia_url=cfg.get('auth.authelia_url', ''),
        auth_oidc_issuer=cfg.get('auth.oidc_issuer', ''),
        smtp_host=cfg.get('smtp.host', ''),
        smtp_port=cfg.get('smtp.port', '587'),
        smtp_usuario=cfg.get('smtp.usuario', ''),
        smtp_password=cfg.get('smtp.password', ''),
        smtp_from=cfg.get('smtp.from', ''),
        smtp_tls=bool(cfg.get('smtp.tls', True)),
        smtp_ssl=bool(cfg.get('smtp.ssl', False)),
        indico_activo=bool(cfg.get('funcion.indico.activo', False)),
        indico_url=cfg.get('funcion.indico.url', ''),
        indico_api_token=cfg.get('funcion.indico.api_token', ''),
        edad_max_joven=int(cfg.get('org.edad_max_joven', 30)),
        denominacion_organo_gobierno=cfg.get('org.denominacion_organo_gobierno', 'junta directiva'),
        denominacion_organo_gobierno_plural=cfg.get('org.denominacion_organo_gobierno_plural', 'juntas directivas'),
        session_inactividad_minutos=int(cfg.get('auth.session_inactividad_minutos', 30)),
        session_maximo_minutos=int(cfg.get('auth.session_maximo_minutos', 480)),
        tema=cfg.get('org.tema', 'violeta'),
        fuente_principal=cfg.get('org.fuente_principal', 'Inter'),
        sepa_creditor_name=cfg.get('sepa.creditor_name', ''),
        sepa_creditor_iban=cfg.get('sepa.creditor_iban', ''),
        sepa_creditor_bic=cfg.get('sepa.creditor_bic', ''),
        sepa_creditor_id=cfg.get('sepa.creditor_id', ''),
        openbanking_activo=bool(cfg.get('funcion.openbanking.activo', False)),
        rgpd_dpd_nombre=cfg.get('rgpd.dpd_nombre', ''),
        rgpd_dpd_email=cfg.get('rgpd.dpd_email', ''),
        rgpd_dpd_telefono=cfg.get('rgpd.dpd_telefono', ''),
        rgpd_dpd_externo=bool(cfg.get('rgpd.dpd_externo', False)),
        rgpd_anios_retencion_baja=int(cfg.get('rgpd.anios_retencion_baja', 6)),
    )


# ---------------------------------------------------------------------------
# Input de mutación
# ---------------------------------------------------------------------------

@strawberry.input
class ParametrosOrganizacionInput:
    nombre: Optional[str] = ''
    nif: Optional[str] = ''
    numero_registro: Optional[str] = ''
    tipo_entidad: Optional[str] = 'ASOCIACION'
    contabilidad_compleja: Optional[bool] = False
    usa_presupuesto: Optional[bool] = False
    sede_social: Optional[str] = ''
    localidad: Optional[str] = ''
    cp: Optional[str] = ''
    provincia: Optional[str] = ''
    pais: Optional[str] = 'España'
    telefono: Optional[str] = ''
    email: Optional[str] = ''
    web: Optional[str] = ''
    rrss_twitter: Optional[str] = ''
    rrss_facebook: Optional[str] = ''
    rrss_instagram: Optional[str] = ''
    rrss_linkedin: Optional[str] = ''
    rrss_youtube: Optional[str] = ''
    rrss_telegram: Optional[str] = ''
    logo: Optional[str] = ''
    implantacion_geografica: Optional[str] = ''
    tipo_unidad_organizativa: Optional[str] = ''
    denominacion_miembro: Optional[str] = 'miembro'
    denominacion_miembro_plural: Optional[str] = 'miembros'
    multiterritorial: Optional[bool] = False
    auth_modo: Optional[str] = 'LOCAL'
    auth_authelia_url: Optional[str] = ''
    auth_oidc_issuer: Optional[str] = ''
    smtp_host: Optional[str] = ''
    smtp_port: Optional[str] = '587'
    smtp_usuario: Optional[str] = ''
    smtp_password: Optional[str] = ''
    smtp_from: Optional[str] = ''
    smtp_tls: Optional[bool] = True
    smtp_ssl: Optional[bool] = False
    indico_activo: Optional[bool] = False
    indico_url: Optional[str] = ''
    indico_api_token: Optional[str] = ''
    edad_max_joven: Optional[int] = 30
    denominacion_organo_gobierno: Optional[str] = 'junta directiva'
    denominacion_organo_gobierno_plural: Optional[str] = 'juntas directivas'
    session_inactividad_minutos: Optional[int] = 30
    session_maximo_minutos: Optional[int] = 480
    tema: Optional[str] = 'violeta'
    fuente_principal: Optional[str] = 'Inter'
    sepa_creditor_name: Optional[str] = ''
    sepa_creditor_iban: Optional[str] = ''
    sepa_creditor_bic: Optional[str] = ''
    sepa_creditor_id: Optional[str] = ''
    openbanking_activo: Optional[bool] = False
    rgpd_dpd_nombre: Optional[str] = ''
    rgpd_dpd_email: Optional[str] = ''
    rgpd_dpd_telefono: Optional[str] = ''
    rgpd_dpd_externo: Optional[bool] = False
    rgpd_anios_retencion_baja: Optional[int] = 6


# ---------------------------------------------------------------------------
# Query mixin
# ---------------------------------------------------------------------------

@strawberry.type
class ConfiguracionOrganizacionQuery:

    @strawberry.field
    async def app_initialized(self, info: strawberry.Info) -> bool:
        """True cuando los parámetros obligatorios de la organización están rellenos."""
        svc = ConfiguracionService(info.context.session)
        return await svc.esta_inicializado()

    @strawberry.field
    async def parametros_organizacion(self, info: strawberry.Info) -> ParametrosOrganizacion:
        svc = ConfiguracionService(info.context.session)
        cfg = await svc.cargar_parametros()
        return _dict_to_parametros(cfg)

    @strawberry.field
    async def smtp_configurado(self, info: strawberry.Info) -> bool:
        """True si los parámetros SMTP obligatorios están rellenos."""
        config = await _load_smtp_config(info.context.session)
        return config.configured


# ---------------------------------------------------------------------------
# Mutation mixin
# ---------------------------------------------------------------------------

@strawberry.type
class ConfiguracionOrganizacionMutation:

    @strawberry.mutation
    async def guardar_parametros_organizacion(
        self,
        info: strawberry.Info,
        datos: ParametrosOrganizacionInput,
    ) -> ParametrosOrganizacion:
        svc = ConfiguracionService(info.context.session)

        ya_inicializado = await svc.esta_inicializado()
        if ya_inicializado:
            if not await info.context.check_permission("CFG_EDIT"):
                raise PermissionError("Permiso denegado: CFG_EDIT")

        await svc.guardar_parametros(datos, ya_inicializado=ya_inicializado)

        cfg = await svc.cargar_parametros()
        return _dict_to_parametros(cfg)

    @strawberry.mutation(permission_classes=[RequireTransaction("CFG_EDIT")])
    async def crear_tipo_unidad_organizativa(
        self,
        info: strawberry.Info,
        nombre: str,
        naturaleza: str,
        vinculo: str,
        nivel: Optional[int] = None,
        padre_tipo_id: Optional[uuid.UUID] = None,
        activo: bool = True,
    ) -> uuid.UUID:
        svc = ConfiguracionService(info.context.session)
        return await svc.crear_tipo_unidad_organizativa(
            nombre=nombre,
            naturaleza=naturaleza,
            vinculo=vinculo,
            nivel=nivel,
            padre_tipo_id=padre_tipo_id,
            activo=activo,
        )
