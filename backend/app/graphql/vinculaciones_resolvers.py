"""Resolvers CRM de vinculaciones: las facetas tipadas de un Contacto.

En el modelo contacto-céntrico, un mismo Contacto (persona física o jurídica)
puede tener varias *facetas* simultáneas, cada una representada por una
`Vinculacion` tipada (SOCIO, VOLUNTARIO, …) con su satélite de datos.

Este módulo expone:
- Lectura:  `vinculacionesDeContacto(contactoId)` — todas las facetas del contacto.
- Escritura: `crearContacto` / `actualizarContacto` (identidad PF/PJ),
             `altaVinculacionSocio` / `altaVinculacionVoluntario` (añadir faceta),
             `cerrarVinculacion` (dar de baja una faceta).

Nota sobre permisos: el alta de socio "completa" (Contacto + Socio + Membresía +
opcional Voluntario) sigue viviendo en `crearMiembro` (membresia_resolvers). Aquí
se reutilizan los permisos `MEMBRESIA_MIEMBRO_CREAR` / `MEMBRESIA_MIEMBRO_EDITAR`;
los códigos dedicados (CNT_*/VINC_*) se introducirán al cablear los permisos del
frontend (fase de UI).
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import List, Optional

import strawberry
from sqlalchemy import select

from app.modules.membresia.models.contacto import Contacto
from app.modules.membresia.models.vinculacion import Vinculacion, Socio, Voluntario
from app.modules.membresia.models.tipo_vinculacion import TipoVinculacion
from app.graphql.permissions import RequireTransaction
from app.graphql.types_auto import VinculacionType, ContactoType


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


async def _fetch_vinculacion(session, vinculacion_id: uuid.UUID) -> Vinculacion:
    """Recarga una Vinculacion con sus relaciones selectin."""
    v = (await session.execute(
        select(Vinculacion).where(Vinculacion.id == vinculacion_id)
    )).scalar_one_or_none()
    if v is None:
        raise ValueError("Vinculación no encontrada.")
    return v


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
    "direccion", "codigo_postal", "localidad", "provincia_id", "pais_domicilio_id",
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
        """Todas las facetas (vinculaciones) de un contacto, vigentes o cerradas."""
        session = info.context.session
        rows = (await session.execute(
            select(Vinculacion)
            .where(
                Vinculacion.contacto_id == contacto_id,
                Vinculacion.eliminado == False,  # noqa: E712
            )
            .order_by(Vinculacion.fecha_inicio)
        )).scalars().all()
        return list(rows)


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------
@strawberry.type
class VinculacionesMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_CREAR")])
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

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_EDITAR")])
    async def actualizar_contacto(self, info: strawberry.Info, data: ContactoUpdateInput) -> ContactoType:
        """Actualiza la identidad de un Contacto (campos no nulos del input)."""
        session = info.context.session
        contacto = (await session.execute(
            select(Contacto).where(Contacto.id == data.id)
        )).scalar_one_or_none()
        if contacto is None:
            raise ValueError("Contacto no encontrado.")
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

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_CREAR")])
    async def alta_vinculacion_socio(
        self, info: strawberry.Info, data: AltaVinculacionSocioInput,
    ) -> VinculacionType:
        """Añade la faceta SOCIO a un contacto existente (Vinculacion + satélite)."""
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
        """Añade la faceta VOLUNTARIO a un contacto existente (Vinculacion + satélite)."""
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
        """Cierra una faceta (fecha_fin + estado='cerrada'). No la elimina."""
        session = info.context.session
        vinc = await _fetch_vinculacion(session, vinculacion_id)
        vinc.fecha_fin = fecha_cierre or date.today()
        vinc.estado = "cerrada"
        # Si el satélite de socio existe, reflejar la baja en su estado.
        if vinc.socio is not None:
            vinc.socio.estado_socio = "baja"
        await session.commit()
        return await _fetch_vinculacion(session, vinc.id)
