"""Servicio del módulo de configuración.

Centraliza toda la lógica de negocio sobre los parámetros de la organización:
  - Lectura de parámetros (con enmascaramiento de secretos)
  - Escritura / upsert de parámetros (con detección de first-run)
  - Invalidación de caché de feature-flags tras cambio
  - Creación de tipos de unidad organizativa

El resolver GraphQL (configuracion_resolvers.py) delega completamente aquí.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.configuracion import Configuracion
from app.modules.core.geografico import NivelOrganizativo, NaturalezaUnidad, VinculoUnidad


# ---------------------------------------------------------------------------
# Tabla de mapeo: (clave_bd, tipo_dato, attr_en_input)
# Fuente única de verdad para qué parámetros existen y cómo se llaman.
# ---------------------------------------------------------------------------

_MAPPING: tuple[tuple[str, str, str], ...] = (
    ('org.nombre',                              'string', 'nombre'),
    ('org.nif',                                 'string', 'nif'),
    ('org.numero_registro',                     'string', 'numero_registro'),
    ('org.tipo_entidad',                        'string', 'tipo_entidad'),
    ('org.contabilidad_compleja',               'bool',   'contabilidad_compleja'),
    ('org.usa_presupuesto',                     'bool',   'usa_presupuesto'),
    ('org.sede_social',                         'string', 'sede_social'),
    ('org.localidad',                           'string', 'localidad'),
    ('org.cp',                                  'string', 'cp'),
    ('org.provincia',                           'string', 'provincia'),
    ('org.pais',                                'string', 'pais'),
    ('org.telefono',                            'string', 'telefono'),
    ('org.email',                               'string', 'email'),
    ('org.web',                                 'string', 'web'),
    ('org.rrss.twitter',                        'string', 'rrss_twitter'),
    ('org.rrss.facebook',                       'string', 'rrss_facebook'),
    ('org.rrss.instagram',                      'string', 'rrss_instagram'),
    ('org.rrss.linkedin',                       'string', 'rrss_linkedin'),
    ('org.rrss.youtube',                        'string', 'rrss_youtube'),
    ('org.rrss.telegram',                       'string', 'rrss_telegram'),
    ('org.logo',                                'string', 'logo'),
    ('org.implantacion_geografica',             'string', 'implantacion_geografica'),
    ('org.tipo_agrupacion_territorial',         'string', 'tipo_unidad_organizativa'),
    ('org.denominacion_miembro',                'string', 'denominacion_miembro'),
    ('org.denominacion_miembro_plural',         'string', 'denominacion_miembro_plural'),
    ('org.multiterritorial',                    'bool',   'multiterritorial'),
    ('auth.modo',                               'string', 'auth_modo'),
    ('auth.authelia_url',                       'string', 'auth_authelia_url'),
    ('auth.oidc_issuer',                        'string', 'auth_oidc_issuer'),
    ('smtp.host',                               'string', 'smtp_host'),
    ('smtp.port',                               'string', 'smtp_port'),
    ('smtp.usuario',                            'string', 'smtp_usuario'),
    ('smtp.password',                           'string', 'smtp_password'),
    ('smtp.from',                               'string', 'smtp_from'),
    ('smtp.tls',                                'bool',   'smtp_tls'),
    ('smtp.ssl',                                'bool',   'smtp_ssl'),
    ('funcion.indico.activo',                   'bool',   'indico_activo'),
    ('funcion.indico.url',                      'string', 'indico_url'),
    ('funcion.indico.api_token',                'string', 'indico_api_token'),
    ('org.edad_max_joven',                      'int',    'edad_max_joven'),
    ('org.denominacion_organo_gobierno',        'string', 'denominacion_organo_gobierno'),
    ('org.denominacion_organo_gobierno_plural', 'string', 'denominacion_organo_gobierno_plural'),
    ('auth.session_inactividad_minutos',        'int',    'session_inactividad_minutos'),
    ('auth.session_maximo_minutos',             'int',    'session_maximo_minutos'),
    ('org.tema',                                'string', 'tema'),
    ('org.fuente_principal',                    'string', 'fuente_principal'),
    ('sepa.creditor_name',                      'string', 'sepa_creditor_name'),
    ('sepa.creditor_iban',                      'string', 'sepa_creditor_iban'),
    ('sepa.creditor_bic',                       'string', 'sepa_creditor_bic'),
    ('sepa.creditor_id',                        'string', 'sepa_creditor_id'),
    ('funcion.openbanking.activo',              'bool',   'openbanking_activo'),
    # RGPD — datos del responsable / DPD y plazos de retención
    ('rgpd.dpd_nombre',                         'string', 'rgpd_dpd_nombre'),
    ('rgpd.dpd_email',                          'string', 'rgpd_dpd_email'),
    ('rgpd.dpd_telefono',                       'string', 'rgpd_dpd_telefono'),
    ('rgpd.dpd_externo',                        'bool',   'rgpd_dpd_externo'),
    ('rgpd.anios_retencion_baja',               'int',    'rgpd_anios_retencion_baja'),
)

# Claves cuya presencia con valor no-vacío indica que el sistema ya fue inicializado.
_REQUIRED_KEYS: frozenset[str] = frozenset({'org.nombre', 'org.nif', 'org.telefono', 'org.email'})

# Valores de retorno que indican "no cambiar este secreto" (el frontend devuelve el placeholder).
_PLACEHOLDER_PREFIX = '•'


class ConfiguracionService:
    """Orquesta la lectura y escritura de parámetros de configuración."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    async def esta_inicializado(self) -> bool:
        """True cuando los parámetros obligatorios de la organización están rellenos."""
        result = await self.session.execute(
            select(Configuracion).where(
                Configuracion.grupo == 'organizacion',
                Configuracion.clave.in_(_REQUIRED_KEYS),
            )
        )
        cfg = {c.clave: c.valor for c in result.scalars()}
        return all(cfg.get(k, '') != '' for k in _REQUIRED_KEYS)

    async def cargar_parametros(self) -> dict:
        """Devuelve todos los parámetros de la organización como dict clave→valor tipado.

        Los secretos (smtp_password, indico_api_token) se enmascaran con '••••••••'
        para que el frontend los muestre pero no los exponga.
        """
        result = await self.session.execute(
            select(Configuracion).where(Configuracion.grupo == 'organizacion')
        )
        cfg = {c.clave: c.get_valor() for c in result.scalars()}

        # Enmascarar secretos
        if cfg.get('smtp.password'):
            cfg['smtp.password'] = '••••••••'
        if cfg.get('funcion.indico.api_token'):
            cfg['funcion.indico.api_token'] = '••••••••'

        # Derivar nombre del nivel de agrupación desde el catálogo (nivel 2 = justo bajo la raíz)
        tipo_agrup_row = (await self.session.execute(
            select(NivelOrganizativo)
            .where(NivelOrganizativo.nivel == 2, NivelOrganizativo.eliminado == False)
            .limit(1)
        )).scalar_one_or_none()
        cfg['_tipo_unidad_organizativa_derivado'] = (
            tipo_agrup_row.nombre if tipo_agrup_row
            else cfg.get('org.tipo_unidad_organizativa', '')
            or cfg.get('org.tipo_agrupacion_territorial', '')
        )

        return cfg

    # ------------------------------------------------------------------
    # Escritura
    # ------------------------------------------------------------------

    async def guardar_parametros(self, datos: object, *, ya_inicializado: bool) -> None:
        """Guarda (upsert) los parámetros de la organización.

        Args:
            datos: Input con los atributos definidos en _MAPPING (normalmente
                   ParametrosOrganizacionInput del resolver).
            ya_inicializado: Si True, el caller ya verificó que el usuario tiene
                             permiso CFG_EDIT. El servicio no comprueba permisos
                             directamente (eso es responsabilidad del resolver).

        Side effects:
            - Upsert en tabla `configuraciones` para cada clave del _MAPPING.
            - Invalida la caché de feature-flags tras el commit.
        """
        # Normalizar input a dict attr→valor
        input_dict = self._normalizar_input(datos)

        # Omitir secretos que el frontend devuelve enmascarados
        for campo_secreto in ('smtp_password', 'indico_api_token'):
            val = input_dict.get(campo_secreto, '')
            if isinstance(val, str) and val.startswith(_PLACEHOLDER_PREFIX):
                input_dict[campo_secreto] = None  # señal: no sobreescribir

        result = await self.session.execute(
            select(Configuracion).where(Configuracion.grupo == 'organizacion')
        )
        existing = {c.clave: c for c in result.scalars()}

        now = datetime.utcnow()
        for clave, tipo_dato, attr in _MAPPING:
            valor = input_dict.get(attr)
            if valor is None:
                continue  # omitir secretos sin cambio
            str_valor = str(valor).lower() if tipo_dato == 'bool' else str(valor)

            if clave in existing:
                existing[clave].valor = str_valor
                existing[clave].fecha_modificacion = now
            else:
                self.session.add(Configuracion(
                    id=uuid.uuid4(),
                    clave=clave,
                    valor=str_valor,
                    tipo_dato=tipo_dato,
                    grupo='organizacion',
                    modificable=True,
                    fecha_creacion=now,
                ))

        await self.session.commit()

        # Invalidar caché del flag de contabilidad compleja tras guardar
        from app.modules.economico.core.feature_flags import invalidar_cache
        invalidar_cache()

    # ------------------------------------------------------------------
    # Tipos de unidad organizativa
    # ------------------------------------------------------------------

    async def crear_tipo_unidad_organizativa(
        self,
        nombre: str,
        naturaleza: str,
        vinculo: str,
        nivel: Optional[int] = None,
        padre_tipo_id: Optional[uuid.UUID] = None,
        activo: bool = True,
    ) -> uuid.UUID:
        """Crea un nuevo nivel / tipo de unidad organizativa.

        Returns:
            El UUID del registro creado.
        """
        tipo = NivelOrganizativo(
            id=uuid.uuid4(),
            nombre=nombre,
            naturaleza=NaturalezaUnidad(naturaleza),
            vinculo=VinculoUnidad(vinculo),
            nivel=nivel,
            padre_tipo_id=padre_tipo_id,
            activo=activo,
        )
        self.session.add(tipo)
        await self.session.commit()
        return tipo.id

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    @staticmethod
    def _normalizar_input(datos: object) -> dict:
        """Convierte el input strawberry en un dict attr→valor con defaults aplicados."""
        defaults = {
            'nombre': '', 'nif': '', 'numero_registro': '',
            'tipo_entidad': 'ASOCIACION',
            'contabilidad_compleja': False, 'usa_presupuesto': False,
            'sede_social': '', 'localidad': '', 'cp': '', 'provincia': '',
            'pais': 'España', 'telefono': '', 'email': '', 'web': '',
            'rrss_twitter': '', 'rrss_facebook': '', 'rrss_instagram': '',
            'rrss_linkedin': '', 'rrss_youtube': '', 'rrss_telegram': '',
            'logo': '', 'implantacion_geografica': '', 'tipo_unidad_organizativa': '',
            'denominacion_miembro': 'miembro',
            'denominacion_miembro_plural': 'miembros',
            'multiterritorial': False,
            'auth_modo': 'LOCAL', 'auth_authelia_url': '', 'auth_oidc_issuer': '',
            'smtp_host': '', 'smtp_port': '587', 'smtp_usuario': '',
            'smtp_password': '', 'smtp_from': '',
            'smtp_tls': True, 'smtp_ssl': False,
            'indico_activo': False, 'indico_url': '', 'indico_api_token': '',
            'edad_max_joven': 30,
            'denominacion_organo_gobierno': 'junta directiva',
            'denominacion_organo_gobierno_plural': 'juntas directivas',
            'session_inactividad_minutos': 30, 'session_maximo_minutos': 480,
            'tema': 'violeta', 'fuente_principal': 'Inter',
            'sepa_creditor_name': '', 'sepa_creditor_iban': '',
            'sepa_creditor_bic': '', 'sepa_creditor_id': '',
            'openbanking_activo': False,
            'rgpd_dpd_nombre': '', 'rgpd_dpd_email': '', 'rgpd_dpd_telefono': '',
            'rgpd_dpd_externo': False, 'rgpd_anios_retencion_baja': 6,
        }
        result = {}
        for attr, default in defaults.items():
            val = getattr(datos, attr, None)
            if val is None:
                result[attr] = default
            elif isinstance(default, str) and val == '':
                result[attr] = default
            else:
                result[attr] = val
        return result
