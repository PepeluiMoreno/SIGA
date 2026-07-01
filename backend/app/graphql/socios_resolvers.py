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
from app.modules.membresia.models.habilidad import MiembroHabilidad
from app.modules.membresia.models.disponibilidad import FranjaDisponibilidad

from app.graphql.types_auto import (
    TipoMiembroType, UnidadOrganizativaType, MotivoBajaType, NivelEstudiosType,
    MotivoReduccionCuotaType, UsuarioType, MiembroHabilidadType, FranjaDisponibilidadType,
)
from app.graphql.permissions import RequireTransaction


# El color del badge por situación es ahora property del satélite (Socio.estado_color),
# fuente única. Aquí solo queda el namespace para el id estable del badge.

# Namespace fijo para derivar un id ESTABLE de la situación (estado_socio). El
# badge ya no cuelga de un catálogo EstadoMiembro, pero el frontend necesita un id
# consistente para poder filtrar por situación.
_ESTADO_NS = uuid.UUID("5161ac0f-e5da-5e5a-9e5a-510ca10c0001")


def _estado_badge_id(estado_socio: str) -> uuid.UUID:
    return uuid.uuid5(_ESTADO_NS, estado_socio)


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
    entidad_geografica_id: Optional[uuid.UUID] = None
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
    fecha_eliminacion: Optional[datetime] = None

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
    habilidades: List[MiembroHabilidadType] = strawberry.field(default_factory=list)
    franjas_disponibilidad: List[FranjaDisponibilidadType] = strawberry.field(default_factory=list)


async def _construir_socios(
    session,
    contacto_id: Optional[uuid.UUID] = None,
    *,
    agrupacion_id: Optional[uuid.UUID] = None,
    activo: Optional[bool] = None,
    es_voluntario: Optional[bool] = None,
    eliminado: bool = False,
) -> List[SocioVistaType]:
    """Reconstruye los `SocioVistaType` con consultas por lote (sin N+1)."""
    # 1) Vinculaciones SOCIO (+ satélite + contacto), con filtros opcionales.
    q = (
        select(Vinculacion)
        .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
        .join(Contacto, Vinculacion.contacto_id == Contacto.id)
        .where(TipoVinculacion.codigo == "SOCIO", Vinculacion.eliminado == eliminado)
    )
    if contacto_id is not None:
        q = q.where(Vinculacion.contacto_id == contacto_id)
    if agrupacion_id is not None:
        q = q.where(Contacto.agrupacion_id == agrupacion_id)
    if activo is not None:
        q = q.where(Contacto.activo == activo)
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

    # 6) Habilidades y franjas de disponibilidad. Ahora cuelgan de la extensión
    #    Voluntario (voluntario_id); se indexan por contacto vía Voluntario→Vinculacion.
    from app.modules.membresia.models.vinculacion import Voluntario
    hab_por_contacto: dict = {}
    for h, contacto_id in (await session.execute(
        select(MiembroHabilidad, Vinculacion.contacto_id)
        .join(Voluntario, Voluntario.id == MiembroHabilidad.voluntario_id)
        .join(Vinculacion, Vinculacion.id == Voluntario.vinculacion_id)
        .where(Vinculacion.contacto_id.in_(contacto_ids))
    )).all():
        hab_por_contacto.setdefault(contacto_id, []).append(h)
    franjas_por_contacto: dict = {}
    for fr, contacto_id in (await session.execute(
        select(FranjaDisponibilidad, Vinculacion.contacto_id)
        .join(Voluntario, Voluntario.id == FranjaDisponibilidad.voluntario_id)
        .join(Vinculacion, Vinculacion.id == Voluntario.vinculacion_id)
        .where(Vinculacion.contacto_id.in_(contacto_ids))
    )).all():
        franjas_por_contacto.setdefault(contacto_id, []).append(fr)

    socios: List[SocioVistaType] = []
    for v in vincs:
        c = v.contacto
        if not c:
            continue
        s = v.socio
        memb = membresia_por_contacto.get(c.id)
        vol = voluntario_por_contacto.get(c.id)
        usr = usuario_por_contacto.get(c.id)
        # Situación efectiva: property del satélite Socio (deriva de estado_socio o de
        # la vinculación). Sin socio, se deriva aquí del cierre de la vinculación.
        estado_socio = s.estado_efectivo if s else ("baja" if v.fecha_fin else "activo")

        socios.append(SocioVistaType(
            id=c.id, nombre=c.nombre, apellido1=c.apellido1, apellido2=c.apellido2,
            foto_url=c.foto_url, sexo=c.sexo, email=c.email, telefono=c.telefono,
            telefono2=c.telefono2, fecha_nacimiento=c.fecha_nacimiento,
            tipo_documento=c.tipo_documento, numero_documento=c.numero_documento,
            direccion=c.direccion, localidad=c.localidad, codigo_postal=c.codigo_postal,
            entidad_geografica_id=c.entidad_geografica_id,
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
            fecha_eliminacion=c.fecha_eliminacion,
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
                id=_estado_badge_id(estado_socio),
                nombre=estado_socio.capitalize(),
                color=(s.estado_color if s else Socio._ESTADO_COLOR.get(estado_socio, "#6B7280")),
            ),
            habilidades=hab_por_contacto.get(c.id, []),
            franjas_disponibilidad=franjas_por_contacto.get(c.id, []),
        ))
    if es_voluntario is not None:
        socios = [x for x in socios if x.es_voluntario == es_voluntario]
    return socios


_BANK_FIELDS = ("iban", "swift_bic", "referencia_pago")


async def _enmascarar_datos_bancarios(info, session, socios):
    """Oculta IBAN/SWIFT/referencia salvo al tesorero del ámbito del socio (o superior).

    Exige el permiso `MEMBRESIA_MIEMBRO_VER_IBAN` y que la agrupación del socio caiga en el
    ámbito territorial del usuario (o que su ámbito sea global = `None`).
    """
    from app.modules.acceso.services.ambito_territorial import agrupaciones_en_ambito
    user = getattr(info.context, "user", None)
    puede = bool(user) and await info.context.check_permission("MEMBRESIA_MIEMBRO_VER_IBAN")
    ambito = await agrupaciones_en_ambito(session, user.id) if puede else set()
    for s in socios:
        visible = puede and (ambito is None or s.agrupacion_id in ambito)
        if not visible:
            for f in _BANK_FIELDS:
                setattr(s, f, None)
    return socios


@strawberry.type(name="ContactoDotable")
class ContactoDotableType:
    """Contacto candidato a recibir cuenta de usuario, con su vínculo y estado de acceso.

    Vista plana para el panel de «Nuevo usuario»: identidad mínima del contacto,
    el tipo de vínculo vigente que lo hace dotable y si ya tiene cuenta.
    """
    id: uuid.UUID
    tipo: str = "PERSONA_FISICA"  # PERSONA_FISICA | PERSONA_JURIDICA
    nombre: str = ""
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    razon_social: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    foto_url: Optional[str] = None

    tipo_vinculacion_id: Optional[uuid.UUID] = None
    tipo_vinculacion_nombre: Optional[str] = None
    tipo_vinculacion_codigo: Optional[str] = None

    agrupacion_id: Optional[uuid.UUID] = None
    agrupacion: Optional[UnidadOrganizativaType] = None

    tiene_acceso: bool = False


async def _construir_contactos_dotables(
    session,
    *,
    tipo_vinculacion_id: Optional[uuid.UUID] = None,
    texto: Optional[str] = None,
) -> List[ContactoDotableType]:
    """Reconstruye los `ContactoDotableType` con consultas por lote (sin N+1).

    Un contacto es dotable si tiene una vinculación vigente (no cerrada, no
    eliminada) cuyo tipo declara `permite_cuenta=True`. Si un mismo contacto
    tiene varios vínculos dotables, se prioriza el de mayor «peso» de acceso
    (por orden de aparición); basta uno para que aparezca una vez.
    """
    q = (
        select(Vinculacion, TipoVinculacion, Contacto)
        .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
        .join(Contacto, Vinculacion.contacto_id == Contacto.id)
        .where(
            TipoVinculacion.permite_cuenta == True,  # noqa: E712
            TipoVinculacion.activo == True,  # noqa: E712
            Vinculacion.eliminado == False,  # noqa: E712
            Vinculacion.estado != "cerrada",
            Contacto.eliminado == False,  # noqa: E712
            Contacto.activo == True,  # noqa: E712
        )
    )
    if tipo_vinculacion_id is not None:
        q = q.where(Vinculacion.tipo_vinculacion_id == tipo_vinculacion_id)
    if texto:
        patron = f"%{texto.strip().lower()}%"
        q = q.where(
            func.lower(
                func.concat_ws(
                    " ", Contacto.nombre, Contacto.apellido1,
                    Contacto.apellido2, Contacto.razon_social,
                )
            ).like(patron)
        )

    filas = (await session.execute(q)).all()

    # Dedup por contacto: un contacto dotable aparece una sola vez. Conservamos
    # el primer vínculo encontrado (orden de la consulta).
    por_contacto: dict[uuid.UUID, ContactoDotableType] = {}
    for vinc, tipo, contacto in filas:
        if contacto.id in por_contacto:
            continue
        por_contacto[contacto.id] = ContactoDotableType(
            id=contacto.id,
            tipo=contacto.tipo,
            nombre=contacto.nombre,
            apellido1=contacto.apellido1,
            apellido2=contacto.apellido2,
            razon_social=contacto.razon_social,
            email=contacto.email,
            telefono=contacto.telefono,
            foto_url=contacto.foto_url,
            tipo_vinculacion_id=tipo.id,
            tipo_vinculacion_nombre=tipo.nombre,
            tipo_vinculacion_codigo=tipo.codigo,
            agrupacion_id=contacto.agrupacion_id,
        )

    if not por_contacto:
        return []

    ids = list(por_contacto.keys())

    # Agrupaciones por lote (Contacto solo guarda el FK, sin relación cargada).
    agr_ids = {c.agrupacion_id for c in por_contacto.values() if c.agrupacion_id}
    if agr_ids:
        agrupaciones = {
            u.id: u
            for u in (await session.execute(
                select(UnidadOrganizativa).where(UnidadOrganizativa.id.in_(agr_ids))
            )).scalars().all()
        }
        for c in por_contacto.values():
            if c.agrupacion_id:
                c.agrupacion = agrupaciones.get(c.agrupacion_id)

    # tiene_acceso: existe un Usuario (no eliminado) ligado a ese contacto.
    con_cuenta = set(
        (await session.execute(
            select(Usuario.contacto_id).where(
                Usuario.contacto_id.in_(ids),
                Usuario.eliminado == False,  # noqa: E712
            )
        )).scalars().all()
    )
    for cid in con_cuenta:
        if cid in por_contacto:
            por_contacto[cid].tiene_acceso = True

    # Orden estable: apellidos / razón social.
    return sorted(
        por_contacto.values(),
        key=lambda c: (
            (c.apellido1 or c.razon_social or c.nombre or "").lower(),
            (c.apellido2 or "").lower(),
            (c.nombre or "").lower(),
        ),
    )


@strawberry.type
class SociosQuery:
    @strawberry.field
    async def socios(
        self,
        info: strawberry.Info,
        contacto_id: Optional[uuid.UUID] = None,
        agrupacion_id: Optional[uuid.UUID] = None,
        activo: Optional[bool] = None,
        es_voluntario: Optional[bool] = None,
        eliminado: bool = False,
    ) -> List[SocioVistaType]:
        """Listado denormalizado de socios (sustituye a la antigua query `miembros`).

        Filtros opcionales planos: contactoId, agrupacionId, activo, esVoluntario,
        eliminado. (Con contactoId devuelve una lista de 0/1 elementos, para que el
        frontend pueda aliasar `miembros: socios(contactoId: $id)` y seguir leyendo
        `data.miembros[0]`.)
        """
        res = await _construir_socios(
            info.context.session, contacto_id=contacto_id, agrupacion_id=agrupacion_id,
            activo=activo, es_voluntario=es_voluntario, eliminado=eliminado,
        )
        return await _enmascarar_datos_bancarios(info, info.context.session, res)

    @strawberry.field
    async def socio(self, info: strawberry.Info, id: uuid.UUID) -> Optional[SocioVistaType]:
        """Un socio por id de contacto."""
        res = await _construir_socios(info.context.session, contacto_id=id)
        res = await _enmascarar_datos_bancarios(info, info.context.session, res)
        return res[0] if res else None

    @strawberry.field
    async def socios_count(self, info: strawberry.Info) -> int:
        """Nº de vinculaciones de socio (no eliminadas)."""
        session = info.context.session
        return (await session.execute(
            select(func.count(Vinculacion.id))
            .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
            .where(TipoVinculacion.codigo == "SOCIO", Vinculacion.eliminado == False)  # noqa: E712
        )).scalar() or 0

    @strawberry.field
    async def cuentas_acceso(
        self,
        info: strawberry.Info,
        activo: Optional[bool] = None,
    ) -> List[SocioVistaType]:
        """Listado de CUENTAS DE ACCESO (todos los usuarios), para la gestión de usuarios.

        A diferencia de `socios` (que parte de la vinculación SOCIO), esto parte de la
        tabla `usuarios`: incluye TODA cuenta, tenga o no contacto y sea cual sea su
        vinculación (también la cuenta de sistema sin contacto, p. ej. `superadmin`).
        Devuelve `SocioVistaType` por reutilizar la forma que la vista ya consume:
        identidad tomada del `Contacto` ligado (vacía si la cuenta no tiene contacto).
        """
        session = info.context.session
        q = select(Usuario).where(Usuario.eliminado == False)  # noqa: E712
        if activo is not None:
            q = q.where(Usuario.activo == activo)
        usuarios = list((await session.execute(q)).scalars().all())
        if not usuarios:
            return []

        # Agrupaciones referenciadas por los contactos de esas cuentas (para el filtro
        # territorial de la vista), en un solo lote.
        agr_ids = {u.contacto.agrupacion_id for u in usuarios
                   if u.contacto and u.contacto.agrupacion_id}
        agrupaciones = {}
        if agr_ids:
            agrupaciones = {a.id: a for a in (await session.execute(
                select(UnidadOrganizativa).where(UnidadOrganizativa.id.in_(agr_ids))
            )).scalars().all()}

        filas: List[SocioVistaType] = []
        for u in usuarios:
            c = u.contacto
            # id de fila: el del contacto si lo hay; si no (cuenta de sistema), el del
            # usuario, para que la fila tenga clave estable. El panel de roles opera
            # siempre sobre usuario.id, que está presente en ambos casos.
            fila_id = c.id if c else u.id
            filas.append(SocioVistaType(
                id=fila_id,
                nombre=(c.nombre if c else (u.username or u.email or "—")),
                apellido1=(c.apellido1 if c else None),
                apellido2=(c.apellido2 if c else None),
                foto_url=(c.foto_url if c else None),
                email=(c.email if c else u.email),
                telefono=(c.telefono if c else None),
                agrupacion_id=(c.agrupacion_id if c else None),
                activo=(c.activo if c else u.activo),
                tiene_acceso=True,
                agrupacion=(agrupaciones.get(c.agrupacion_id) if c else None),
                usuario=u,
            ))

        # Orden estable por apellidos / nombre / username.
        return sorted(
            filas,
            key=lambda f: (
                (f.apellido1 or f.nombre or "").lower(),
                (f.apellido2 or "").lower(),
                (f.nombre or "").lower(),
            ),
        )

    @strawberry.field(permission_classes=[RequireTransaction("ACCESO_USUARIO_CREAR")])
    async def contactos_dotables(
        self,
        info: strawberry.Info,
        tipo_vinculacion_id: Optional[uuid.UUID] = None,
        texto: Optional[str] = None,
    ) -> List['ContactoDotableType']:
        """Contactos que pueden ser dotados de cuenta de usuario de la aplicación.

        Un contacto es «dotable» si tiene una vinculación vigente cuyo
        `TipoVinculacion.permite_cuenta` es True. Alimenta el panel de la vista
        «Nuevo usuario», donde se elige a quién se le da acceso.

        Filtros opcionales:
          - tipoVinculacionId: restringe a un tipo de vínculo concreto (debe ser
            de los que permiten cuenta).
          - texto: subcadena (case-insensitive) sobre nombre/apellidos/razón social.
        """
        session = info.context.session
        return await _construir_contactos_dotables(
            session, tipo_vinculacion_id=tipo_vinculacion_id, texto=texto,
        )
