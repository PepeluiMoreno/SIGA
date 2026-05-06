"""Resolvers GraphQL para parámetros de configuración de la organización."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

import strawberry
from sqlalchemy import select

from app.modules.configuracion.models.configuracion import Configuracion
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.usuario import UsuarioRol


# ---------------------------------------------------------------------------
# Tipos de salida
# ---------------------------------------------------------------------------

@strawberry.type
class ParametrosOrganizacion:
    nombre: str
    nif: str
    tipo_entidad: str
    contabilidad_compleja: bool
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
    logo: str
    implantacion_geografica: str
    tipo_agrupacion_territorial: str
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
    # Edad máxima para socio joven
    edad_max_joven: int


# ---------------------------------------------------------------------------
# Input de mutación
# ---------------------------------------------------------------------------

@strawberry.input
class ParametrosOrganizacionInput:
    nombre: Optional[str] = ''
    nif: Optional[str] = ''
    tipo_entidad: Optional[str] = 'ASOCIACION'
    contabilidad_compleja: Optional[bool] = False
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
    logo: Optional[str] = ''
    implantacion_geografica: Optional[str] = ''
    tipo_agrupacion_territorial: Optional[str] = ''
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
    # Edad máxima para socio joven
    edad_max_joven: Optional[int] = 30


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MAPPING = [
    ('org.nombre',              'string', 'nombre'),
    ('org.nif',                 'string', 'nif'),
    ('org.tipo_entidad',        'string', 'tipo_entidad'),
    ('org.contabilidad_compleja','bool',  'contabilidad_compleja'),
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
    ('org.logo',                'string', 'logo'),
    ('org.implantacion_geografica',       'string', 'implantacion_geografica'),
    ('org.tipo_agrupacion_territorial',   'string', 'tipo_agrupacion_territorial'),
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
    ('org.edad_max_joven',                'int',    'edad_max_joven'),
]


async def _load_org_params(session) -> ParametrosOrganizacion:
    result = await session.execute(
        select(Configuracion).where(Configuracion.grupo == 'organizacion')
    )
    cfg = {c.clave: c.get_valor() for c in result.scalars()}
    return ParametrosOrganizacion(
        nombre=cfg.get('org.nombre', ''),
        nif=cfg.get('org.nif', ''),
        tipo_entidad=cfg.get('org.tipo_entidad', 'ASOCIACION'),
        contabilidad_compleja=bool(cfg.get('org.contabilidad_compleja', False)),
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
        logo=cfg.get('org.logo', ''),
        implantacion_geografica=cfg.get('org.implantacion_geografica', ''),
        tipo_agrupacion_territorial=cfg.get('org.tipo_agrupacion_territorial', ''),
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
        edad_max_joven=int(cfg.get('org.edad_max_joven', 30)),
    )


# ---------------------------------------------------------------------------
# Query mixin
# ---------------------------------------------------------------------------

_REQUIRED_KEYS = {'org.nombre', 'org.nif', 'org.telefono', 'org.email', 'org.logo'}


async def _require_superadmin(session, user_id) -> None:
    """Lanza PermissionError si el usuario no tiene el rol SUPERADMIN activo."""
    superadmin = (
        await session.execute(select(Rol).where(Rol.codigo == 'SUPERADMIN'))
    ).scalar_one_or_none()
    if superadmin is None:
        return  # No hay rol SUPERADMIN configurado — permitir (entorno de arranque)
    link = (
        await session.execute(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == user_id,
                UsuarioRol.rol_id == superadmin.id,
                UsuarioRol.activo == True,
                UsuarioRol.eliminado == False,
            )
        )
    ).scalar_one_or_none()
    if link is None:
        raise PermissionError("Solo el SUPERADMIN puede modificar los parámetros de la organización")


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
            if not info.context.is_authenticated:
                raise PermissionError("Autenticación requerida para modificar los parámetros")
            await _require_superadmin(session, info.context.user.id)

        result = await session.execute(
            select(Configuracion).where(Configuracion.grupo == 'organizacion')
        )
        existing = {c.clave: c for c in result.scalars()}

        input_dict = {
            'nombre': datos.nombre or '',
            'nif': datos.nif or '',
            'tipo_entidad': datos.tipo_entidad or 'ASOCIACION',
            'contabilidad_compleja': datos.contabilidad_compleja or False,
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
            'logo': datos.logo or '',
            'implantacion_geografica': datos.implantacion_geografica or '',
            'tipo_agrupacion_territorial': datos.tipo_agrupacion_territorial or '',
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
            'edad_max_joven': datos.edad_max_joven if datos.edad_max_joven is not None else 30,
        }

        # No sobreescribir la contraseña SMTP si el frontend devuelve el placeholder
        if input_dict.get('smtp_password', '').startswith('•'):
            input_dict['smtp_password'] = existing.get('smtp.password', existing.get('smtp.password'))
            # mantener valor actual — se resolverá en el bucle al no encontrarlo en input_dict
            input_dict['smtp_password'] = None  # señal para omitir

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
        return await _load_org_params(session)
