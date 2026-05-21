"""Resolvers GraphQL para parámetros de configuración de la organización."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

import strawberry
from sqlalchemy import select

from app.modules.configuracion.models.configuracion import Configuracion
from app.modules.core.geografico import NivelOrganizativo, NaturalezaUnidad, VinculoUnidad
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
    # Autenticación
    auth_modo: str
    auth_authelia_url: str
    auth_oidc_issuer: str
    # SMTP
    smtp_host: str
    smtp_port: str
    smtp_usuario: str
    smtp_password: str          # devuelto enmascarado al frontend
    smtp_from: str
    smtp_tls: bool
    smtp_ssl: bool
    # Funcionalidades opcionales
    indico_activo: bool
    indico_url: str
    indico_api_token: str     # devuelto enmascarado al frontend
    # Edad máxima para socio joven
    edad_max_joven: int
    # Denominaciones configurables
    denominacion_organo_gobierno: str
    denominacion_organo_gobierno_plural: str
    # Sesión
    session_inactividad_minutos: int
    session_maximo_minutos: int
    # Apariencia
    tema: str
    fuente_principal: str
    # SEPA — acreedor para remesas (D3.5, flujo 3)
    sepa_creditor_name: str
    sepa_creditor_iban: str
    sepa_creditor_bic: str
    sepa_creditor_id: str
    # Open Banking — conciliación bancaria automática (flujo 8)
    openbanking_activo: bool


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
    # Autenticación
    auth_modo: Optional[str] = 'LOCAL'
    auth_authelia_url: Optional[str] = ''
    auth_oidc_issuer: Optional[str] = ''
    # SMTP
    smtp_host: Optional[str] = ''
    smtp_port: Optional[str] = '587'
    smtp_usuario: Optional[str] = ''
    smtp_password: Optional[str] = ''   # vacío = no cambiar
    smtp_from: Optional[str] = ''
    smtp_tls: Optional[bool] = True
    smtp_ssl: Optional[bool] = False
    # Funcionalidades opcionales
    indico_activo: Optional[bool] = False
    indico_url: Optional[str] = ''
    indico_api_token: Optional[str] = ''   # vacío = no cambiar
    # Edad máxima para socio joven
    edad_max_joven: Optional[int] = 30
    # Denominaciones configurables
    denominacion_organo_gobierno: Optional[str] = 'junta directiva'
    denominacion_organo_gobierno_plural: Optional[str] = 'juntas directivas'
    # Sesión
    session_inactividad_minutos: Optional[int] = 30
    session_maximo_minutos: Optional[int] = 480
    # Apariencia
    tema: Optional[str] = 'violeta'
    fuente_principal: Optional[str] = 'Inter'
    # SEPA — acreedor para remesas (D3.5, flujo 3)
    sepa_creditor_name: Optional[str] = ''
    sepa_creditor_iban: Optional[str] = ''
    sepa_creditor_bic: Optional[str] = ''
    sepa_creditor_id: Optional[str] = ''
    # Open Banking — conciliación bancaria automática (flujo 8)
    openbanking_activo: Optional[bool] = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MAPPING = [
    ('org.nombre',              'string', 'nombre'),
    ('org.nif',                 'string', 'nif'),
    ('org.numero_registro',     'string', 'numero_registro'),
    ('org.tipo_entidad',        'string', 'tipo_entidad'),
    ('org.contabilidad_compleja','bool',  'contabilidad_compleja'),
    ('org.usa_presupuesto',     'bool',  'usa_presupuesto'),
    ('org.sede_social',         'string', 'sede_social'),
    ('org.localidad',           'string', 'localidad'),
    ('org.cp',                  'string', 'cp'),
    ('org.provincia',           'string', 'provincia'),
    ('org.pais',                'string', 'pais'),
    ('org.telefono',            'string', 'telefono'),
    ('org.email',               'string', 'email'),
    ('org.web',                 'string', 'web'),
    ('org.rrss.twitter',        'string', 'rrss_twitter'),
    ('org.rrss.facebook',       'string', 'rrss_facebook'),
    ('org.rrss.instagram',      'string', 'rrss_instagram'),
    ('org.rrss.linkedin',       'string', 'rrss_linkedin'),
    ('org.rrss.youtube',        'string', 'rrss_youtube'),
    ('org.rrss.telegram',       'string', 'rrss_telegram'),
    ('org.logo',                'string', 'logo'),
    ('org.implantacion_geografica',       'string', 'implantacion_geografica'),
    ('org.tipo_agrupacion_territorial',   'string', 'tipo_unidad_organizativa'),
    ('org.denominacion_miembro',          'string', 'denominacion_miembro'),
    ('org.denominacion_miembro_plural',   'string', 'denominacion_miembro_plural'),
    ('org.multiterritorial',              'bool',   'multiterritorial'),
    ('auth.modo',                         'string', 'auth_modo'),
    ('auth.authelia_url',                 'string', 'auth_authelia_url'),
    ('auth.oidc_issuer',                  'string', 'auth_oidc_issuer'),
    ('smtp.host',                         'string', 'smtp_host'),
    ('smtp.port',                         'string', 'smtp_port'),
    ('smtp.usuario',                      'string', 'smtp_usuario'),
    ('smtp.password',                     'string', 'smtp_password'),
    ('smtp.from',                         'string', 'smtp_from'),
    ('smtp.tls',                          'bool',   'smtp_tls'),
    ('smtp.ssl',                          'bool',   'smtp_ssl'),
    ('funcion.indico.activo',             'bool',   'indico_activo'),
    ('funcion.indico.url',                'string', 'indico_url'),
    ('funcion.indico.api_token',          'string', 'indico_api_token'),
    ('org.edad_max_joven',                        'int',    'edad_max_joven'),
    ('org.denominacion_organo_gobierno',           'string', 'denominacion_organo_gobierno'),
    ('org.denominacion_organo_gobierno_plural',    'string', 'denominacion_organo_gobierno_plural'),
    ('auth.session_inactividad_minutos',           'int',    'session_inactividad_minutos'),
    ('auth.session_maximo_minutos',                'int',    'session_maximo_minutos'),
    ('org.tema',                                   'string', 'tema'),
    ('org.fuente_principal',                       'string', 'fuente_principal'),
    # SEPA — acreedor para remesas (D3.5)
    ('sepa.creditor_name',                         'string', 'sepa_creditor_name'),
    ('sepa.creditor_iban',                         'string', 'sepa_creditor_iban'),
    ('sepa.creditor_bic',                          'string', 'sepa_creditor_bic'),
    ('sepa.creditor_id',                           'string', 'sepa_creditor_id'),
    # Open Banking (flujo 8)
    ('funcion.openbanking.activo',                 'bool',   'openbanking_activo'),
]


async def _load_org_params(session) -> ParametrosOrganizacion:
    result = await session.execute(
        select(Configuracion).where(Configuracion.grupo == 'organizacion')
    )
    cfg = {c.clave: c.get_valor() for c in result.scalars()}

    # Deriva el nombre del nivel de agrupación desde el catálogo (nivel 2 = justo bajo la raíz)
    tipo_agrup_row = (await session.execute(
        select(NivelOrganizativo)
        .where(NivelOrganizativo.nivel == 2, NivelOrganizativo.eliminado == False)
        .limit(1)
    )).scalar_one_or_none()
    tipo_unidad_organizativa = (
        tipo_agrup_row.nombre if tipo_agrup_row
        else cfg.get('org.tipo_unidad_organizativa', '')
        or cfg.get('org.tipo_agrupacion_territorial', '')
    )

    return ParametrosOrganizacion(
        nombre=cfg.get('org.nombre', ''),
        nif=cfg.get('org.nif', ''),
        numero_registro=cfg.get('org.numero_registro', ''),
        tipo_entidad=cfg.get('org.tipo_entidad', 'ASOCIACION'),
        contabilidad_compleja=bool(cfg.get('org.contabilidad_compleja', False)),
        usa_presupuesto=bool(cfg.get('org.usa_presupuesto', False)),
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
        tipo_unidad_organizativa=tipo_unidad_organizativa,
        denominacion_miembro=cfg.get('org.denominacion_miembro', 'miembro'),
        denominacion_miembro_plural=cfg.get('org.denominacion_miembro_plural', 'miembros'),
        multiterritorial=bool(cfg.get('org.multiterritorial', False)),
        auth_modo=cfg.get('auth.modo', 'LOCAL'),
        auth_authelia_url=cfg.get('auth.authelia_url', ''),
        auth_oidc_issuer=cfg.get('auth.oidc_issuer', ''),
        smtp_host=cfg.get('smtp.host', ''),
        smtp_port=cfg.get('smtp.port', '587'),
        smtp_usuario=cfg.get('smtp.usuario', ''),
        smtp_password='••••••••' if cfg.get('smtp.password') else '',
        smtp_from=cfg.get('smtp.from', ''),
        smtp_tls=bool(cfg.get('smtp.tls', True)),
        smtp_ssl=bool(cfg.get('smtp.ssl', False)),
        indico_activo=bool(cfg.get('funcion.indico.activo', False)),
        indico_url=cfg.get('funcion.indico.url', ''),
        indico_api_token='••••••••' if cfg.get('funcion.indico.api_token') else '',
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
    )


# ---------------------------------------------------------------------------
# Query mixin
# ---------------------------------------------------------------------------

_REQUIRED_KEYS = {'org.nombre', 'org.nif', 'org.telefono', 'org.email'}


@strawberry.type
class ConfiguracionOrganizacionQuery:
    @strawberry.field
    async def app_initialized(self, info: strawberry.Info) -> bool:
        """True cuando los parámetros obligatorios de la organización están rellenos."""
        result = await info.context.session.execute(
            select(Configuracion).where(
                Configuracion.grupo == 'organizacion',
                Configuracion.clave.in_(_REQUIRED_KEYS),
            )
        )
        cfg = {c.clave: c.valor for c in result.scalars()}
        return all(cfg.get(k, '') != '' for k in _REQUIRED_KEYS)

    @strawberry.field
    async def parametros_organizacion(self, info: strawberry.Info) -> ParametrosOrganizacion:
        return await _load_org_params(info.context.session)

    @strawberry.field
    async def smtp_configurado(self, info: strawberry.Info) -> bool:
        """True si los parámetros SMTP obligatorios están rellenos (host, usuario, password)."""
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
        session = info.context.session

        # Comprobar si ya está inicializado (si lo está, exigir permiso)
        check = await session.execute(
            select(Configuracion).where(
                Configuracion.grupo == 'organizacion',
                Configuracion.clave.in_(_REQUIRED_KEYS),
            )
        )
        existing_required = {c.clave: c.valor for c in check.scalars()}
        already_initialized = all(existing_required.get(k, '') != '' for k in _REQUIRED_KEYS)

        if already_initialized:
            if not await info.context.check_permission("CFG_EDIT"):
                raise PermissionError("Permiso denegado: CFG_EDIT")

        result = await session.execute(
            select(Configuracion).where(Configuracion.grupo == 'organizacion')
        )
        existing = {c.clave: c for c in result.scalars()}

        input_dict = {
            'nombre': datos.nombre or '',
            'nif': datos.nif or '',
            'numero_registro': datos.numero_registro or '',
            'tipo_entidad': datos.tipo_entidad or 'ASOCIACION',
            'contabilidad_compleja': datos.contabilidad_compleja or False,
            'usa_presupuesto': datos.usa_presupuesto or False,
            'sede_social': datos.sede_social or '',
            'localidad': datos.localidad or '',
            'cp': datos.cp or '',
            'provincia': datos.provincia or '',
            'pais': datos.pais or 'España',
            'telefono': datos.telefono or '',
            'email': datos.email or '',
            'web': datos.web or '',
            'rrss_twitter': datos.rrss_twitter or '',
            'rrss_facebook': datos.rrss_facebook or '',
            'rrss_instagram': datos.rrss_instagram or '',
            'rrss_linkedin': datos.rrss_linkedin or '',
            'rrss_youtube': datos.rrss_youtube or '',
            'rrss_telegram': datos.rrss_telegram or '',
            'logo': datos.logo or '',
            'implantacion_geografica': datos.implantacion_geografica or '',
            'tipo_unidad_organizativa': datos.tipo_unidad_organizativa or '',
            'denominacion_miembro': datos.denominacion_miembro or 'miembro',
            'denominacion_miembro_plural': datos.denominacion_miembro_plural or 'miembros',
            'multiterritorial': datos.multiterritorial or False,
            'auth_modo': datos.auth_modo or 'LOCAL',
            'auth_authelia_url': datos.auth_authelia_url or '',
            'auth_oidc_issuer': datos.auth_oidc_issuer or '',
            'smtp_host': datos.smtp_host or '',
            'smtp_port': datos.smtp_port or '587',
            'smtp_usuario': datos.smtp_usuario or '',
            'smtp_password': datos.smtp_password or '',
            'smtp_from': datos.smtp_from or '',
            'smtp_tls': datos.smtp_tls if datos.smtp_tls is not None else True,
            'smtp_ssl': datos.smtp_ssl or False,
            'indico_activo': datos.indico_activo or False,
            'indico_url': datos.indico_url or '',
            'indico_api_token': datos.indico_api_token or '',
            'edad_max_joven': datos.edad_max_joven if datos.edad_max_joven is not None else 30,
            'denominacion_organo_gobierno': datos.denominacion_organo_gobierno or 'junta directiva',
            'denominacion_organo_gobierno_plural': datos.denominacion_organo_gobierno_plural or 'juntas directivas',
            'session_inactividad_minutos': datos.session_inactividad_minutos if datos.session_inactividad_minutos is not None else 30,
            'session_maximo_minutos': datos.session_maximo_minutos if datos.session_maximo_minutos is not None else 480,
            'tema': datos.tema or 'violeta',
            'fuente_principal': datos.fuente_principal or 'Inter',
            'sepa_creditor_name': datos.sepa_creditor_name or '',
            'sepa_creditor_iban': datos.sepa_creditor_iban or '',
            'sepa_creditor_bic': datos.sepa_creditor_bic or '',
            'sepa_creditor_id': datos.sepa_creditor_id or '',
            'openbanking_activo': datos.openbanking_activo or False,
        }

        # No sobreescribir la contraseña SMTP si el frontend devuelve el placeholder
        if input_dict.get('smtp_password', '').startswith('•'):
            input_dict['smtp_password'] = None  # señal para omitir — no sobreescribir

        if input_dict.get('indico_api_token', '').startswith('•'):
            input_dict['indico_api_token'] = None  # ídem

        now = datetime.utcnow()
        for clave, tipo_dato, attr in _MAPPING:
            valor = input_dict[attr]
            if valor is None:
                continue  # omitir (ej: contraseña SMTP sin cambios)
            str_valor = str(valor).lower() if tipo_dato == 'bool' else str(valor)

            if clave in existing:
                existing[clave].valor = str_valor
                existing[clave].fecha_modificacion = now
            else:
                session.add(Configuracion(
                    id=uuid.uuid4(),
                    clave=clave,
                    valor=str_valor,
                    tipo_dato=tipo_dato,
                    grupo='organizacion',
                    modificable=True,
                    fecha_creacion=now,
                ))

        await session.commit()

        # Invalidar caché del flag de contabilidad compleja
        from app.modules.economico.core.feature_flags import invalidar_cache
        invalidar_cache()

        return await _load_org_params(session)

    # ── NivelOrganizativo: create custom (strawchemy no persiste FKs UUID) ──

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
        session = info.context.session
        tipo = NivelOrganizativo(
            id=uuid.uuid4(),
            nombre=nombre,
            naturaleza=NaturalezaUnidad(naturaleza),
            vinculo=VinculoUnidad(vinculo),
            nivel=nivel,
            padre_tipo_id=padre_tipo_id,
            activo=activo,
        )
        session.add(tipo)
        await session.commit()
        return tipo.id
