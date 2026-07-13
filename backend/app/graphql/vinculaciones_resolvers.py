"""Resolvers CRM de vinculaciones: las vinculaciones tipadas de un Contacto.

En el modelo contacto-céntrico, un mismo Contacto (persona física o jurídica)
puede tener varias *vinculaciones* simultáneas, cada una representada por una
`Vinculacion` tipada (SOCIO, VOLUNTARIO, …) con su satélite de datos.

Este módulo expone:
- Lectura:  `vinculacionesDeContacto(contactoId)` — todas las vinculaciones del contacto.
- Escritura: `crearContacto` / `actualizarContacto` (identidad PF/PJ),
             `altaVinculacionSocio` / `altaVinculacionVoluntario` (añadir vinculación),
             `cerrarVinculacion` (dar de baja una vinculación).

Nota sobre permisos: el alta de socio "completa" (Contacto + Socio + Membresía +
opcional Voluntario) sigue viviendo en `crearMiembro` (membresia_resolvers). Aquí
se reutilizan los permisos `MEMBRESIA_MIEMBRO_CREAR` / `MEMBRESIA_MIEMBRO_EDITAR`;
los códigos dedicados (CNT_*/VINC_*) se introducirán al cablear los permisos del
frontend (fase de UI).
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional

import strawberry
from sqlalchemy import select

from app.modules.membresia.models.contacto import Contacto
from app.modules.membresia.models.vinculacion import Vinculacion, Socio, Voluntario
from app.modules.membresia.models.tipo_vinculacion import TipoVinculacion
from app.modules.membresia.models.historial_nombramiento import HistorialNombramiento
from app.modules.membresia.models.historial_agrupacion import HistorialAgrupacion
from app.modules.membresia.models.traslados.modelos import SolicitudTraslado, EstadoTraslado
from app.graphql.permissions import RequireTransaction
from app.modules.acceso.services.objetivo import Objetivo
from app.graphql.types_auto import (
    VinculacionType, ContactoType, HistorialNombramientoType, SolicitudTrasladoType,
)
from app.modules.acceso.services.ambito_territorial import (
    assert_unidad_en_ambito,
    assert_miembro_en_ambito,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _tipo_vinc_id(session, codigo: str) -> uuid.UUID:
    """Devuelve el id del TipoVinculacion por código (SOCIO, VOLUNTARIO, …)."""
    tid = await session.scalar(
        select(TipoVinculacion.id).where(TipoVinculacion.codigo == codigo)
    )
    if tid is None:
        raise ValueError(f"No existe el tipo de vinculación '{codigo}'.")
    return tid


async def _vinculacion_activa(session, contacto_id: uuid.UUID, codigo: str):
    """Vinculación vigente (sin cierre) del contacto para un tipo dado, o None."""
    return (await session.execute(
        select(Vinculacion)
        .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
        .where(
            Vinculacion.contacto_id == contacto_id,
            TipoVinculacion.codigo == codigo,
            Vinculacion.fecha_fin.is_(None),
            Vinculacion.eliminado == False,  # noqa: E712
        )
    )).scalar_one_or_none()


async def _ultima_vinculacion(session, contacto_id: uuid.UUID, codigo: str):
    """Última vinculación del contacto para un tipo dado (esté vigente o cerrada),
    por fecha_inicio descendente. Útil para reactivar una baja."""
    return (await session.execute(
        select(Vinculacion)
        .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
        .where(
            Vinculacion.contacto_id == contacto_id,
            TipoVinculacion.codigo == codigo,
            Vinculacion.eliminado == False,  # noqa: E712
        )
        .order_by(Vinculacion.fecha_inicio.desc())
    )).scalars().first()


async def _fetch_vinculacion(session, vinculacion_id: uuid.UUID) -> Vinculacion:
    """Recarga una Vinculacion con sus relaciones selectin."""
    v = (await session.execute(
        select(Vinculacion).where(Vinculacion.id == vinculacion_id)
    )).scalar_one_or_none()
    if v is None:
        raise ValueError("Vinculación no encontrada.")
    return v


async def _fetch_traslado(session, solicitud_id: uuid.UUID) -> SolicitudTraslado:
    """Recarga una SolicitudTraslado por id."""
    sol = await session.get(SolicitudTraslado, solicitud_id)
    if sol is None:
        raise ValueError("Solicitud de traslado no encontrada.")
    return sol


_ESTADOS_TRASLADO_EN_CURSO = frozenset({
    EstadoTraslado.PENDIENTE, EstadoTraslado.APROBADO_ORIGEN,
    EstadoTraslado.APROBADO_DESTINO, EstadoTraslado.APROBADO,
})


async def _traslado_en_curso(session, solicitud_id: uuid.UUID) -> SolicitudTraslado:
    """Recarga una SolicitudTraslado y valida que sigue en un estado que admite
    aprobación/rechazo/cancelación (no ejecutada ni ya cerrada)."""
    sol = await _fetch_traslado(session, solicitud_id)
    if sol.eliminado or sol.estado not in _ESTADOS_TRASLADO_EN_CURSO:
        raise ValueError(f"La solicitud no admite cambios (estado: {sol.estado}).")
    return sol


def _recalcular_estado_traslado(sol: SolicitudTraslado) -> None:
    """Deriva el estado a partir de las aprobaciones de origen y destino."""
    if sol.aprobado_origen and sol.aprobado_destino:
        sol.estado = EstadoTraslado.APROBADO
    elif sol.aprobado_origen:
        sol.estado = EstadoTraslado.APROBADO_ORIGEN
    elif sol.aprobado_destino:
        sol.estado = EstadoTraslado.APROBADO_DESTINO
    else:
        sol.estado = EstadoTraslado.PENDIENTE


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
@strawberry.input
class ContactoCreateInput:
    # Discriminador: PERSONA_FISICA (por defecto) | PERSONA_JURIDICA
    tipo: str = "PERSONA_FISICA"
    # Identidad (PF: nombre + apellidos | PJ: razon_social)
    nombre: str = ""
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    razon_social: Optional[str] = None
    # Documento
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    pais_documento_id: Optional[uuid.UUID] = None
    # Persona física
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    pais_nacimiento_id: Optional[uuid.UUID] = None
    profesion: Optional[str] = None
    nivel_estudios_id: Optional[uuid.UUID] = None
    # Persona jurídica
    cif: Optional[str] = None
    tipo_entidad_juridica_id: Optional[uuid.UUID] = None
    actividad_principal: Optional[str] = None
    representante_legal_id: Optional[uuid.UUID] = None
    # Domicilio
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[uuid.UUID] = None
    entidad_geografica_id: Optional[uuid.UUID] = None
    pais_domicilio_id: Optional[uuid.UUID] = None
    # Contacto
    telefono: Optional[str] = None
    telefono2: Optional[str] = None
    email: Optional[str] = None
    # Contexto
    agrupacion_id: Optional[uuid.UUID] = None
    foto_url: Optional[str] = None
    activo: bool = True


@strawberry.input
class ContactoUpdateInput:
    id: uuid.UUID
    nombre: Optional[str] = None
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    razon_social: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    pais_documento_id: Optional[uuid.UUID] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    pais_nacimiento_id: Optional[uuid.UUID] = None
    profesion: Optional[str] = None
    nivel_estudios_id: Optional[uuid.UUID] = None
    cif: Optional[str] = None
    tipo_entidad_juridica_id: Optional[uuid.UUID] = None
    actividad_principal: Optional[str] = None
    representante_legal_id: Optional[uuid.UUID] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[uuid.UUID] = None
    entidad_geografica_id: Optional[uuid.UUID] = None
    pais_domicilio_id: Optional[uuid.UUID] = None
    telefono: Optional[str] = None
    telefono2: Optional[str] = None
    email: Optional[str] = None
    agrupacion_id: Optional[uuid.UUID] = None
    foto_url: Optional[str] = None
    activo: Optional[bool] = None


# Campos de Contacto que aceptan las mutaciones (para copiar sin repetir).
_CONTACTO_FIELDS: tuple[str, ...] = (
    "nombre", "apellido1", "apellido2", "razon_social",
    "tipo_documento", "numero_documento", "pais_documento_id",
    "sexo", "fecha_nacimiento", "pais_nacimiento_id", "profesion", "nivel_estudios_id",
    "cif", "tipo_entidad_juridica_id", "actividad_principal", "representante_legal_id",
    "direccion", "codigo_postal", "localidad", "provincia_id", "entidad_geografica_id",
    "pais_domicilio_id",
    "telefono", "telefono2", "email", "agrupacion_id", "foto_url",
)


@strawberry.input
class AltaVinculacionSocioInput:
    contacto_id: uuid.UUID
    fecha_alta: Optional[date] = None
    agrupacion_id: Optional[uuid.UUID] = None
    numero_socio: Optional[str] = None
    cuota_mensual: Optional[float] = None
    iban: Optional[str] = None
    swift_bic: Optional[str] = None
    referencia_pago: Optional[str] = None
    forma_pago_id: Optional[uuid.UUID] = None
    es_honor: bool = False
    motivo_reduccion_id: Optional[uuid.UUID] = None


@strawberry.input
class AltaVinculacionVoluntarioInput:
    contacto_id: uuid.UUID
    fecha_alta: Optional[date] = None
    agrupacion_id: Optional[uuid.UUID] = None
    disponibilidad: Optional[str] = None
    horas_disponibles_semana: Optional[int] = None
    profesion: Optional[str] = None
    nivel_estudios_id: Optional[uuid.UUID] = None
    experiencia_voluntariado: Optional[str] = None
    intereses: Optional[str] = None
    observaciones_voluntariado: Optional[str] = None
    puede_conducir: bool = False
    vehiculo_propio: bool = False
    disponibilidad_viajar: bool = False


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------
@strawberry.type
class VinculacionesQuery:
    @strawberry.field
    async def vinculaciones_de_contacto(
        self, info: strawberry.Info, contacto_id: uuid.UUID,
    ) -> List[VinculacionType]:
        """Todas las vinculaciones de un contacto, vigentes o cerradas."""
        session = info.context.session
        rows = list((await session.execute(
            select(Vinculacion)
            .where(
                Vinculacion.contacto_id == contacto_id,
                Vinculacion.eliminado == False,  # noqa: E712
            )
            .order_by(Vinculacion.fecha_inicio)
        )).scalars().all())
        await _ocultar_iban_vinculaciones(info, session, rows)
        return rows


async def _ocultar_iban_vinculaciones(info, session, vincs):
    """Oculta los datos bancarios del satélite Socio salvo al tesorero del ámbito
    del contacto (o superior). Mismo criterio que el read-model `socios`.

    Para no marcar el ORM como sucio (es una query, no debe persistir), se
    desacopla el satélite de la sesión antes de anular los campos.
    """
    from app.modules.acceso.services.ambito_territorial import agrupaciones_en_ambito
    user = getattr(info.context, "user", None)
    puede = bool(user) and await info.context.check_permission("MEMBRESIA_MIEMBRO_VER_IBAN")
    ambito = await agrupaciones_en_ambito(session, user.id) if puede else set()
    for v in vincs:
        socio = getattr(v, "socio", None)
        if socio is None:
            continue
        agr = v.contacto.agrupacion_id if v.contacto else None
        visible = puede and (ambito is None or agr in ambito)
        if not visible:
            session.expunge(socio)
            socio.iban = None
            socio.swift_bic = None
            socio.referencia_pago = None


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------
@strawberry.type
class VinculacionesMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("CONTACTO_CREAR")])
    async def crear_contacto(self, info: strawberry.Info, data: ContactoCreateInput) -> ContactoType:
        """Crea un Contacto (persona física o jurídica) sin vinculación inicial."""
        session = info.context.session
        tipo = (data.tipo or "PERSONA_FISICA").upper()
        if tipo not in ("PERSONA_FISICA", "PERSONA_JURIDICA"):
            raise ValueError("tipo debe ser PERSONA_FISICA o PERSONA_JURIDICA.")
        if tipo == "PERSONA_JURIDICA":
            nombre = (data.razon_social or data.nombre or "").strip()
            if not nombre:
                raise ValueError("Una persona jurídica requiere razón social.")
        else:
            nombre = (data.nombre or "").strip()
            if not nombre:
                raise ValueError("Una persona física requiere nombre.")

        contacto = Contacto(tipo=tipo)
        contacto.nombre = nombre
        for field in _CONTACTO_FIELDS:
            if field == "nombre":
                continue
            val = getattr(data, field, None)
            if val is not None:
                setattr(contacto, field, val)
        contacto.activo = data.activo
        session.add(contacto)
        await session.commit()
        return (await session.execute(
            select(Contacto).where(Contacto.id == contacto.id)
        )).scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("CONTACTO_EDITAR")])
    async def actualizar_contacto(self, info: strawberry.Info, data: ContactoUpdateInput) -> ContactoType:
        """Actualiza la identidad de un Contacto (campos no nulos del input)."""
        session = info.context.session
        contacto = (await session.execute(
            select(Contacto).where(Contacto.id == data.id)
        )).scalar_one_or_none()
        if contacto is None:
            raise ValueError("Contacto no encontrado.")
        # Cambiar de agrupación toca DOS territorios, y el motor no lo cubre: un
        # `Objetivo` ancla en un solo punto, y aquí hay que exigir origen *y* destino.
        # Por eso este guard sobrevive al motor territorial (igual que los dos extremos
        # del traslado, más abajo). Ver `docs/arquitectura/MOTOR_TERRITORIAL.md`.
        usuario = info.context.user
        if data.agrupacion_id is not None and data.agrupacion_id != contacto.agrupacion_id:
            if usuario is None:
                raise PermissionError("Cambiar de agrupación exige un usuario autenticado.")
            await assert_miembro_en_ambito(session, usuario.id, contacto.id)   # origen
            await assert_unidad_en_ambito(session, usuario.id, data.agrupacion_id)  # destino
        for field in _CONTACTO_FIELDS:
            val = getattr(data, field, None)
            if val is not None:
                setattr(contacto, field, val)
        if data.activo is not None:
            contacto.activo = data.activo
        await session.commit()
        return (await session.execute(
            select(Contacto).where(Contacto.id == contacto.id)
        )).scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("CONTACTO_ELIMINAR")])
    async def eliminar_contacto(self, info: strawberry.Info, id: uuid.UUID) -> ContactoType:
        """Baja lógica (soft delete) de un Contacto: lo retira del directorio.

        No es purga física (eso compete al módulo RGPD). Queda con eliminado=True y
        deja de aparecer en los listados (que filtran eliminado=false). Distinto de
        'dar de baja' (activo=False), que solo marca el contacto como inactivo.
        """
        session = info.context.session
        contacto = (await session.execute(
            select(Contacto).where(Contacto.id == id)
        )).scalar_one_or_none()
        if contacto is None:
            raise ValueError("Contacto no encontrado.")
        contacto.soft_delete()
        await session.commit()
        return (await session.execute(
            select(Contacto).where(Contacto.id == id)
        )).scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_CREAR")])
    async def alta_vinculacion_socio(
        self, info: strawberry.Info, data: AltaVinculacionSocioInput,
    ) -> VinculacionType:
        """Añade la vinculación SOCIO a un contacto existente (Vinculacion + satélite)."""
        session = info.context.session
        contacto = (await session.execute(
            select(Contacto).where(Contacto.id == data.contacto_id)
        )).scalar_one_or_none()
        if contacto is None:
            raise ValueError("Contacto no encontrado.")
        if await _vinculacion_activa(session, data.contacto_id, "SOCIO"):
            raise ValueError("El contacto ya tiene una vinculación de socio vigente.")

        vinc = Vinculacion(
            contacto_id=data.contacto_id,
            tipo_vinculacion_id=await _tipo_vinc_id(session, "SOCIO"),
            fecha_inicio=data.fecha_alta or date.today(),
            estado="activa",
            agrupacion_id=data.agrupacion_id,
        )
        session.add(vinc)
        await session.flush()
        session.add(Socio(
            vinculacion_id=vinc.id,
            numero_socio=data.numero_socio,
            cuota_mensual=data.cuota_mensual,
            iban=data.iban,
            swift_bic=data.swift_bic,
            referencia_pago=data.referencia_pago,
            forma_pago_id=data.forma_pago_id,
            es_honor=data.es_honor,
            motivo_reduccion_id=data.motivo_reduccion_id,
        ))
        await session.commit()
        return await _fetch_vinculacion(session, vinc.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_CREAR")])
    async def alta_vinculacion_voluntario(
        self, info: strawberry.Info, data: AltaVinculacionVoluntarioInput,
    ) -> VinculacionType:
        """Añade la vinculación VOLUNTARIO a un contacto existente (Vinculacion + satélite)."""
        session = info.context.session
        contacto = (await session.execute(
            select(Contacto).where(Contacto.id == data.contacto_id)
        )).scalar_one_or_none()
        if contacto is None:
            raise ValueError("Contacto no encontrado.")
        if await _vinculacion_activa(session, data.contacto_id, "VOLUNTARIO"):
            raise ValueError("El contacto ya tiene una vinculación de voluntario vigente.")

        vinc = Vinculacion(
            contacto_id=data.contacto_id,
            tipo_vinculacion_id=await _tipo_vinc_id(session, "VOLUNTARIO"),
            fecha_inicio=data.fecha_alta or date.today(),
            estado="activa",
            agrupacion_id=data.agrupacion_id,
        )
        session.add(vinc)
        await session.flush()
        session.add(Voluntario(
            vinculacion_id=vinc.id,
            disponibilidad=data.disponibilidad,
            horas_disponibles_semana=data.horas_disponibles_semana,
            profesion=data.profesion,
            nivel_estudios_id=data.nivel_estudios_id,
            experiencia_voluntariado=data.experiencia_voluntariado,
            intereses=data.intereses,
            observaciones_voluntariado=data.observaciones_voluntariado,
            puede_conducir=data.puede_conducir,
            vehiculo_propio=data.vehiculo_propio,
            disponibilidad_viajar=data.disponibilidad_viajar,
        ))
        await session.commit()
        return await _fetch_vinculacion(session, vinc.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_EDITAR")])
    async def cerrar_vinculacion(
        self, info: strawberry.Info, vinculacion_id: uuid.UUID,
        fecha_cierre: Optional[date] = None,
    ) -> VinculacionType:
        """Cierra una vinculación (fecha_fin + estado='cerrada'). No la elimina."""
        session = info.context.session
        vinc = await _fetch_vinculacion(session, vinculacion_id)
        vinc.fecha_fin = fecha_cierre or date.today()
        vinc.estado = "cerrada"
        # Si el satélite de socio existe, reflejar la baja en su estado.
        if vinc.socio is not None:
            vinc.socio.estado_socio = "baja"
        await session.commit()
        return await _fetch_vinculacion(session, vinc.id)

    # ── Ciclo de vida del socio (suspender / baja / reactivar) ───────────────
    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_SUSPENDER", objetivo=Objetivo.contacto("contacto_id"))])
    async def suspender_socio(
        self, info: strawberry.Info, contacto_id: uuid.UUID,
    ) -> VinculacionType:
        """Suspende temporalmente a un socio: su satélite pasa a estado_socio
        'suspendido' y la vinculación a 'inactiva' (no se cierra). Se revierte con
        `reactivar_socio`."""
        session = info.context.session
        vinc = await _vinculacion_activa(session, contacto_id, "SOCIO")
        if vinc is None:
            raise ValueError("El contacto no tiene una vinculación de socio vigente.")
        if vinc.socio is not None:
            vinc.socio.estado_socio = "suspendido"
        vinc.estado = "inactiva"
        await session.commit()
        return await _fetch_vinculacion(session, vinc.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_BAJA", objetivo=Objetivo.contacto("contacto_id"))])
    async def dar_de_baja_socio(
        self, info: strawberry.Info, contacto_id: uuid.UUID,
        fecha_baja: Optional[date] = None,
        motivo_baja_id: Optional[uuid.UUID] = None,
        motivo_baja_texto: Optional[str] = None,
    ) -> VinculacionType:
        """Da de baja a un socio: cierra su vinculación SOCIO (fecha_fin +
        estado='cerrada') y marca el satélite como 'baja', registrando el motivo.
        Atajo a nivel de socio sobre `cerrar_vinculacion` (que trabaja por id de
        vinculación y no guarda motivo)."""
        session = info.context.session
        vinc = await _vinculacion_activa(session, contacto_id, "SOCIO")
        if vinc is None:
            raise ValueError("El contacto no tiene una vinculación de socio vigente.")
        vinc.fecha_fin = fecha_baja or date.today()
        vinc.estado = "cerrada"
        if vinc.socio is not None:
            vinc.socio.estado_socio = "baja"
            vinc.socio.motivo_baja_id = motivo_baja_id
            vinc.socio.motivo_baja_texto = motivo_baja_texto
        await session.commit()
        return await _fetch_vinculacion(session, vinc.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_BAJA", objetivo=Objetivo.contacto("contacto_id"))])
    async def reactivar_socio(
        self, info: strawberry.Info, contacto_id: uuid.UUID,
    ) -> VinculacionType:
        """Reactiva a un socio suspendido o de baja: reabre su última vinculación
        SOCIO (estado='activa', fecha_fin=NULL) y pone el satélite en 'activo',
        limpiando el motivo de baja. Operación inversa de suspender/baja."""
        session = info.context.session
        vinc = await _ultima_vinculacion(session, contacto_id, "SOCIO")
        if vinc is None:
            raise ValueError("El contacto no tiene ninguna vinculación de socio.")
        if vinc.estado == "activa" and vinc.fecha_fin is None:
            raise ValueError("El socio ya está activo.")
        vinc.estado = "activa"
        vinc.fecha_fin = None
        if vinc.socio is not None:
            vinc.socio.estado_socio = "activo"
            vinc.socio.motivo_baja_id = None
            vinc.socio.motivo_baja_texto = None
        await session.commit()
        return await _fetch_vinculacion(session, vinc.id)

    # ── Conversión simpatizante → socio ──────────────────────────────────────
    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_CREAR")])
    async def convertir_simpatizante_en_socio(
        self, info: strawberry.Info, contacto_id: uuid.UUID,
        numero_socio: Optional[str] = None,
        cuota_mensual: Optional[float] = None,
        iban: Optional[str] = None,
        swift_bic: Optional[str] = None,
        forma_pago_id: Optional[uuid.UUID] = None,
        agrupacion_id: Optional[uuid.UUID] = None,
    ) -> VinculacionType:
        """Convierte a un simpatizante en socio: crea la vinculación SOCIO (+
        satélite con sus datos económicos) y cierra la vinculación SIMPATIZANTE.
        Equivale al `cambioSimpSocio` de GSH."""
        session = info.context.session
        simp = await _vinculacion_activa(session, contacto_id, "SIMPATIZANTE")
        if simp is None:
            raise ValueError("El contacto no tiene una vinculación de simpatizante vigente.")
        if await _vinculacion_activa(session, contacto_id, "SOCIO") is not None:
            raise ValueError("El contacto ya tiene una vinculación de socio vigente.")

        from app.core.documento import normalizar_iban, validar_iban
        if iban and not validar_iban(iban):
            raise ValueError("El IBAN no es válido.")

        socio_vinc = Vinculacion(
            contacto_id=contacto_id,
            tipo_vinculacion_id=await _tipo_vinc_id(session, "SOCIO"),
            fecha_inicio=date.today(),
            estado="activa",
            agrupacion_id=agrupacion_id or simp.agrupacion_id,
        )
        session.add(socio_vinc)
        await session.flush()
        session.add(Socio(
            vinculacion_id=socio_vinc.id,
            numero_socio=numero_socio,
            cuota_mensual=cuota_mensual,
            iban=normalizar_iban(iban) or None,
            swift_bic=(swift_bic or "").strip().upper() or None,
            forma_pago_id=forma_pago_id,
            estado_socio="activo",
        ))
        # El simpatizante pasa a socio: se cierra su vinculación de simpatizante.
        simp.estado = "cerrada"
        simp.fecha_fin = date.today()
        await session.commit()
        return await _fetch_vinculacion(session, socio_vinc.id)

    # ── Traslados entre agrupaciones (máquina de estados) ────────────────────
    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_TRASLADO_SOLICITAR", objetivo=Objetivo.contacto("miembro_id"))])
    async def solicitar_traslado(
        self, info: strawberry.Info, miembro_id: uuid.UUID,
        agrupacion_destino_id: uuid.UUID, motivo_traslado_id: uuid.UUID,
        detalle: Optional[str] = None,
        fecha_efectiva_deseada: Optional[date] = None,
    ) -> SolicitudTrasladoType:
        """Crea una solicitud de traslado (estado PENDIENTE). El origen se toma de
        la agrupación actual del contacto. `motivo_traslado_id` es del catálogo
        `motivos_traslado`; `detalle` es texto libre opcional. Requiere doble
        aprobación (origen y destino) antes de poder ejecutarse."""
        session = info.context.session
        contacto = await session.get(Contacto, miembro_id)
        if contacto is None:
            raise ValueError("Contacto no encontrado.")
        if contacto.agrupacion_id is None:
            raise ValueError("El contacto no tiene agrupación de origen asignada.")
        if contacto.agrupacion_id == agrupacion_destino_id:
            raise ValueError("La agrupación de destino coincide con la de origen.")
        pendiente = await session.scalar(
            select(SolicitudTraslado).where(
                SolicitudTraslado.miembro_id == miembro_id,
                SolicitudTraslado.estado.in_([
                    EstadoTraslado.PENDIENTE, EstadoTraslado.APROBADO_ORIGEN,
                    EstadoTraslado.APROBADO_DESTINO, EstadoTraslado.APROBADO,
                ]),
                SolicitudTraslado.eliminado == False,  # noqa: E712
            )
        )
        if pendiente is not None:
            raise ValueError("Ya hay una solicitud de traslado en curso para este contacto.")
        sol = SolicitudTraslado(
            miembro_id=miembro_id,
            agrupacion_origen_id=contacto.agrupacion_id,
            agrupacion_destino_id=agrupacion_destino_id,
            motivo_traslado_id=motivo_traslado_id,
            motivo=(detalle or "").strip() or None,
            estado=EstadoTraslado.PENDIENTE,
            fecha_efectiva_deseada=fecha_efectiva_deseada,
        )
        session.add(sol)
        await session.commit()
        return await _fetch_traslado(session, sol.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_TRASLADO_APROBAR")])
    async def aprobar_traslado_origen(
        self, info: strawberry.Info, solicitud_id: uuid.UUID,
        observaciones: Optional[str] = None,
    ) -> SolicitudTrasladoType:
        """Aprobación por el coordinador de ORIGEN. Cuando origen y destino han
        aprobado, la solicitud pasa a APROBADO (lista para ejecutar)."""
        session = info.context.session
        sol = await _traslado_en_curso(session, solicitud_id)
        # Cada extremo del traslado lo aprueba quien manda EN ESE extremo. El motor no
        # lo cubre: un `Objetivo` ancla en un punto, y aquí el punto depende de la
        # mutación. Por eso este guard sobrevive.
        usuario = info.context.user
        if usuario is None:
            raise PermissionError("Aprobar un traslado exige un usuario autenticado.")
        await assert_unidad_en_ambito(session, usuario.id, sol.agrupacion_origen_id)
        sol.aprobado_origen = True
        sol.fecha_aprobacion_origen = datetime.now()
        sol.coordinador_origen_id = usuario.id if usuario else None
        sol.observaciones_origen = observaciones
        _recalcular_estado_traslado(sol)
        await session.commit()
        return await _fetch_traslado(session, sol.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_TRASLADO_APROBAR")])
    async def aprobar_traslado_destino(
        self, info: strawberry.Info, solicitud_id: uuid.UUID,
        observaciones: Optional[str] = None,
    ) -> SolicitudTrasladoType:
        """Aprobación por el coordinador de DESTINO."""
        session = info.context.session
        sol = await _traslado_en_curso(session, solicitud_id)
        # Cada extremo del traslado lo aprueba quien manda EN ESE extremo. El motor no
        # lo cubre: un `Objetivo` ancla en un punto, y aquí el punto depende de la
        # mutación. Por eso este guard sobrevive.
        usuario = info.context.user
        if usuario is None:
            raise PermissionError("Aprobar un traslado exige un usuario autenticado.")
        await assert_unidad_en_ambito(session, usuario.id, sol.agrupacion_destino_id)
        sol.aprobado_destino = True
        sol.fecha_aprobacion_destino = datetime.now()
        sol.coordinador_destino_id = usuario.id if usuario else None
        sol.observaciones_destino = observaciones
        _recalcular_estado_traslado(sol)
        await session.commit()
        return await _fetch_traslado(session, sol.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_TRASLADO_RECHAZAR", objetivo=Objetivo.solicitud_traslado())])
    async def rechazar_traslado(
        self, info: strawberry.Info, solicitud_id: uuid.UUID, motivo: str,
        lado: str = "origen",
    ) -> SolicitudTrasladoType:
        """Rechaza el traslado desde un lado ('origen' o 'destino'), con motivo."""
        session = info.context.session
        sol = await _traslado_en_curso(session, solicitud_id)
        sol.estado = (EstadoTraslado.RECHAZADO_DESTINO if lado == "destino"
                      else EstadoTraslado.RECHAZADO_ORIGEN)
        sol.motivo_rechazo = motivo
        await session.commit()
        return await _fetch_traslado(session, sol.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_TRASLADO_SOLICITAR", objetivo=Objetivo.solicitud_traslado())])
    async def cancelar_traslado(
        self, info: strawberry.Info, solicitud_id: uuid.UUID,
    ) -> SolicitudTrasladoType:
        """El solicitante cancela un traslado que aún no se ha ejecutado."""
        session = info.context.session
        sol = await _traslado_en_curso(session, solicitud_id)
        sol.estado = EstadoTraslado.CANCELADO
        await session.commit()
        return await _fetch_traslado(session, sol.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_TRASLADO_APROBAR")])
    async def ejecutar_traslado(
        self, info: strawberry.Info, solicitud_id: uuid.UUID,
    ) -> SolicitudTrasladoType:
        """Ejecuta un traslado APROBADO: mueve la agrupación del contacto y de su
        vinculación SOCIO, cierra el tramo de HistorialAgrupacion vigente y abre
        uno nuevo en la agrupación de destino."""
        session = info.context.session
        sol = await session.get(SolicitudTraslado, solicitud_id)
        if sol is None or sol.eliminado:
            raise ValueError("Solicitud de traslado no encontrada.")
        if sol.estado != EstadoTraslado.APROBADO:
            raise ValueError(
                f"El traslado no está aprobado por ambos lados (estado: {sol.estado})."
            )
        contacto = await session.get(Contacto, sol.miembro_id)
        if contacto is None:
            raise ValueError("Contacto no encontrado.")

        hoy = date.today()
        # Cierra el tramo de historial vigente (fecha_fin NULL) del contacto.
        tramo_abierto = await session.scalar(
            select(HistorialAgrupacion).where(
                HistorialAgrupacion.miembro_id == contacto.id,
                HistorialAgrupacion.fecha_fin.is_(None),
                HistorialAgrupacion.eliminado == False,  # noqa: E712
            ).order_by(HistorialAgrupacion.fecha_inicio.desc())
        )
        if tramo_abierto is not None:
            tramo_abierto.fecha_fin = hoy
        # Abre el nuevo tramo en destino.
        session.add(HistorialAgrupacion(
            miembro_id=contacto.id, agrupacion_id=sol.agrupacion_destino_id,
            fecha_inicio=hoy, motivo="Traslado",
        ))

        # Mueve la agrupación del contacto y de su vinculación SOCIO vigente.
        contacto.agrupacion_id = sol.agrupacion_destino_id
        socio_vinc = await _vinculacion_activa(session, contacto.id, "SOCIO")
        if socio_vinc is not None:
            socio_vinc.agrupacion_id = sol.agrupacion_destino_id

        usuario = info.context.user
        sol.estado = EstadoTraslado.EJECUTADO
        sol.fecha_ejecucion = datetime.now()
        sol.usuario_ejecutor_id = usuario.id if usuario else None
        await session.commit()
        return await _fetch_traslado(session, sol.id)
