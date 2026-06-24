"""Resolvers custom para membresía.

strawchemy excluye las columnas FK UUID de los inputs auto-generados.
Este módulo define MiembroCreateInput y MiembroUpdateInput completos
(con todos los FK UUID fields) y los resolvers que los usan.
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import Optional, List

import strawberry
from sqlalchemy import select, or_

from app.modules.membresia.models.miembro import Miembro
from app.modules.acceso.services.acceso_service import AccesoService
from app.graphql.types_auto import MiembroType
from app.graphql.permissions import RequireTransaction
from app.core.events import event_bus, MiembroPerfilIncompleto


_CAMPOS_PERFIL_CLAVE: tuple[tuple[str, str], ...] = (
    ("tipo_miembro_id", "tipo de socio"),
    ("estado_id",       "estado"),
    ("email",           "email"),
    ("telefono",        "teléfono"),
)


def _campos_perfil_faltantes(miembro: Miembro) -> tuple[str, ...]:
    """Devuelve los nombres legibles de los campos clave sin rellenar."""
    return tuple(
        etiqueta for attr, etiqueta in _CAMPOS_PERFIL_CLAVE
        if not getattr(miembro, attr, None)
    )


async def _publicar_perfil_incompleto(miembro: Miembro) -> None:
    """Publica MiembroPerfilIncompleto si faltan campos clave. Nunca lanza."""
    faltantes = _campos_perfil_faltantes(miembro)
    if not faltantes:
        return
    try:
        nombre = " ".join(filter(None, [miembro.nombre, miembro.apellido1])).strip()
        await event_bus.publish(MiembroPerfilIncompleto(
            miembro_id=str(miembro.id),
            miembro_nombre=nombre or "(sin nombre)",
            agrupacion_id=str(miembro.agrupacion_id) if miembro.agrupacion_id else None,
            campos_faltantes=faltantes,
        ))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

@strawberry.input
class MiembroCreateInput:
    nombre: str
    apellido1: str
    tipo_miembro_id: Optional[uuid.UUID] = None
    estado_id: Optional[uuid.UUID] = None
    apellido2: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    pais_documento_id: Optional[uuid.UUID] = None
    pais_nacimiento_id: Optional[uuid.UUID] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[uuid.UUID] = None
    pais_domicilio_id: Optional[uuid.UUID] = None
    telefono: Optional[str] = None
    telefono2: Optional[str] = None
    email: Optional[str] = None
    agrupacion_id: Optional[uuid.UUID] = None
    iban: Optional[str] = None
    swift_bic: Optional[str] = None
    referencia_pago: Optional[str] = None
    forma_pago_id: Optional[uuid.UUID] = None
    es_socio_honor: bool = False
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None
    motivo_baja_id: Optional[uuid.UUID] = None
    motivo_baja_texto: Optional[str] = None
    observaciones: Optional[str] = None
    solicita_supresion_datos: bool = False
    fecha_solicitud_supresion: Optional[date] = None
    fecha_limite_retencion: Optional[date] = None
    datos_anonimizados: bool = False
    fecha_anonimizacion: Optional[date] = None
    activo: bool = True
    es_voluntario: bool = False
    disponibilidad: Optional[str] = None
    horas_disponibles_semana: Optional[int] = None
    profesion: Optional[str] = None
    nivel_estudios_id: Optional[uuid.UUID] = None
    motivo_reduccion_id: Optional[uuid.UUID] = None
    experiencia_voluntariado: Optional[str] = None
    intereses: Optional[str] = None
    observaciones_voluntariado: Optional[str] = None
    puede_conducir: bool = False
    vehiculo_propio: bool = False
    disponibilidad_viajar: bool = False


@strawberry.input
class MiembroUpdateInput:
    id: uuid.UUID
    nombre: Optional[str] = None
    apellido1: Optional[str] = None
    tipo_miembro_id: Optional[uuid.UUID] = None
    estado_id: Optional[uuid.UUID] = None
    apellido2: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    pais_documento_id: Optional[uuid.UUID] = None
    pais_nacimiento_id: Optional[uuid.UUID] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[uuid.UUID] = None
    pais_domicilio_id: Optional[uuid.UUID] = None
    telefono: Optional[str] = None
    telefono2: Optional[str] = None
    email: Optional[str] = None
    agrupacion_id: Optional[uuid.UUID] = None
    iban: Optional[str] = None
    swift_bic: Optional[str] = None
    referencia_pago: Optional[str] = None
    forma_pago_id: Optional[uuid.UUID] = None
    es_socio_honor: Optional[bool] = None
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None
    motivo_baja_id: Optional[uuid.UUID] = None
    motivo_baja_texto: Optional[str] = None
    observaciones: Optional[str] = None
    solicita_supresion_datos: Optional[bool] = None
    fecha_solicitud_supresion: Optional[date] = None
    fecha_limite_retencion: Optional[date] = None
    datos_anonimizados: Optional[bool] = None
    fecha_anonimizacion: Optional[date] = None
    activo: Optional[bool] = None
    es_voluntario: Optional[bool] = None
    disponibilidad: Optional[str] = None
    horas_disponibles_semana: Optional[int] = None
    profesion: Optional[str] = None
    nivel_estudios_id: Optional[uuid.UUID] = None
    motivo_reduccion_id: Optional[uuid.UUID] = None
    experiencia_voluntariado: Optional[str] = None
    intereses: Optional[str] = None
    observaciones_voluntariado: Optional[str] = None
    puede_conducir: Optional[bool] = None
    vehiculo_propio: Optional[bool] = None
    disponibilidad_viajar: Optional[bool] = None


# ---------------------------------------------------------------------------
# Mixin de mutaciones
# ---------------------------------------------------------------------------

_MIEMBRO_FIELDS = [
    'nombre', 'apellido1', 'apellido2', 'sexo', 'fecha_nacimiento',
    'tipo_miembro_id', 'estado_id', 'tipo_documento', 'numero_documento',
    'pais_documento_id', 'pais_nacimiento_id', 'direccion', 'codigo_postal',
    'localidad', 'provincia_id', 'pais_domicilio_id', 'telefono', 'telefono2',
    'email', 'agrupacion_id', 'iban', 'swift_bic', 'referencia_pago', 'forma_pago_id', 'es_socio_honor',
    'fecha_alta', 'fecha_baja', 'motivo_baja_id', 'motivo_baja_texto',
    'observaciones', 'solicita_supresion_datos', 'fecha_solicitud_supresion',
    'fecha_limite_retencion', 'datos_anonimizados', 'fecha_anonimizacion',
    'activo', 'es_voluntario', 'disponibilidad', 'horas_disponibles_semana',
    'profesion', 'nivel_estudios_id', 'motivo_reduccion_id',
    'experiencia_voluntariado', 'intereses',
    'observaciones_voluntariado', 'puede_conducir', 'vehiculo_propio',
    'disponibilidad_viajar',
]


async def _fetch_miembro(session, miembro_id: uuid.UUID):
    """Recarga el miembro con todas las relaciones selectin."""
    stmt = select(Miembro).where(Miembro.id == miembro_id)
    result = await session.execute(stmt)
    return result.scalar_one()


@strawberry.input
class PerfilVoluntarioInput:
    """Campos de voluntariado editables por delegación (no toca el resto del socio)."""
    miembro_id: uuid.UUID
    es_voluntario: Optional[bool] = None
    disponibilidad: Optional[str] = None
    horas_disponibles_semana: Optional[int] = None
    profesion: Optional[str] = None
    nivel_estudios_id: Optional[uuid.UUID] = None
    intereses: Optional[str] = None
    experiencia_voluntariado: Optional[str] = None
    observaciones_voluntariado: Optional[str] = None
    puede_conducir: Optional[bool] = None
    vehiculo_propio: Optional[bool] = None
    disponibilidad_viajar: Optional[bool] = None


_CAMPOS_VOLUNTARIO = (
    'es_voluntario', 'disponibilidad', 'horas_disponibles_semana', 'profesion',
    'nivel_estudios_id', 'intereses', 'experiencia_voluntariado',
    'observaciones_voluntariado', 'puede_conducir', 'vehiculo_propio',
    'disponibilidad_viajar',
)


@strawberry.type
class MembresiaResolverMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_VOLUNTARIO_GESTIONAR")])
    async def gestionar_perfil_voluntario(
        self,
        info: strawberry.Info,
        data: PerfilVoluntarioInput,
    ) -> 'MiembroType':
        """Edita el perfil de voluntario (disponibilidad, profesión, intereses…) por delegación.

        Solo toca campos de voluntariado, no el resto de datos del socio. Aplica el guard de
        ámbito territorial: un cargo territorial solo puede gestionar socios de su ámbito.
        """
        from app.modules.acceso.services.ambito_territorial import assert_miembro_en_ambito
        session = info.context.session
        user = info.context.user
        await assert_miembro_en_ambito(session, user.id, data.miembro_id)

        miembro = await _fetch_miembro(session, data.miembro_id)
        for field in _CAMPOS_VOLUNTARIO:
            val = getattr(data, field, None)
            if val is not None:
                setattr(miembro, field, val)
        await session.commit()
        return await _fetch_miembro(session, miembro.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("HAB_ASSIGN")])
    async def asignar_habilidad_voluntario(
        self,
        info: strawberry.Info,
        miembro_id: uuid.UUID,
        habilidad_id: uuid.UUID,
        nivel_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """Asigna (o actualiza el nivel de) una habilidad a un socio, por delegación.
        Con guard de ámbito territorial."""
        from app.modules.acceso.services.ambito_territorial import assert_miembro_en_ambito
        from app.modules.membresia.models.habilidad import MiembroHabilidad
        session = info.context.session
        await assert_miembro_en_ambito(session, info.context.user.id, miembro_id)
        existente = (await session.execute(
            select(MiembroHabilidad).where(
                MiembroHabilidad.miembro_id == miembro_id,
                MiembroHabilidad.habilidad_id == habilidad_id,
            )
        )).scalar_one_or_none()
        if existente:
            existente.nivel_id = nivel_id
        else:
            session.add(MiembroHabilidad(
                miembro_id=miembro_id, habilidad_id=habilidad_id, nivel_id=nivel_id,
            ))
        await session.commit()
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("HAB_ASSIGN")])
    async def quitar_habilidad_voluntario(
        self,
        info: strawberry.Info,
        miembro_id: uuid.UUID,
        habilidad_id: uuid.UUID,
    ) -> bool:
        """Quita una habilidad de un socio, por delegación. Con guard de ámbito territorial."""
        from app.modules.acceso.services.ambito_territorial import assert_miembro_en_ambito
        from app.modules.membresia.models.habilidad import MiembroHabilidad
        session = info.context.session
        await assert_miembro_en_ambito(session, info.context.user.id, miembro_id)
        existente = (await session.execute(
            select(MiembroHabilidad).where(
                MiembroHabilidad.miembro_id == miembro_id,
                MiembroHabilidad.habilidad_id == habilidad_id,
            )
        )).scalar_one_or_none()
        if existente:
            await session.delete(existente)
            await session.commit()
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_CREAR")])
    async def crear_miembro(
        self,
        info: strawberry.Info,
        data: MiembroCreateInput,
    ) -> 'MiembroType':
        session = info.context.session

        kwargs = {field: getattr(data, field) for field in _MIEMBRO_FIELDS}
        miembro = Miembro(**kwargs)
        session.add(miembro)
        await session.commit()

        await _publicar_perfil_incompleto(miembro)

        return await _fetch_miembro(session, miembro.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_CREAR")])
    async def crear_miembro_con_acceso(
        self,
        info: strawberry.Info,
        data: MiembroCreateInput,
        email: str,
        password: str,
        tipo_vinculacion_id: Optional[uuid.UUID] = None,
        activo_usuario: bool = True,
    ) -> 'MiembroType':
        """Crea un miembro y su usuario de acceso en una única transacción atómica."""
        session = info.context.session

        kwargs = {field: getattr(data, field) for field in _MIEMBRO_FIELDS}
        miembro = Miembro(**kwargs)
        session.add(miembro)
        await session.flush()

        svc = AccesoService(session)
        await svc.crear_usuario(
            email=email,
            password=password,
            activo=activo_usuario,
            miembro_id=miembro.id,
            tipo_vinculacion_id=tipo_vinculacion_id,
        )

        await session.commit()

        await _publicar_perfil_incompleto(miembro)

        return await _fetch_miembro(session, miembro.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_EDITAR")])
    async def actualizar_miembro(
        self,
        info: strawberry.Info,
        data: MiembroUpdateInput,
    ) -> 'MiembroType':
        session = info.context.session

        miembro = await _fetch_miembro(session, data.id)
        faltantes_antes = _campos_perfil_faltantes(miembro)

        for field in _MIEMBRO_FIELDS:
            val = getattr(data, field, None)
            if val is not None or field not in (
                'nombre', 'apellido1', 'tipo_miembro_id', 'estado_id'
            ):
                setattr(miembro, field, val)

        await session.commit()

        # Notificar solo si la edición ha cambiado el conjunto de campos
        # faltantes y siguen quedando huecos. Si los huecos son los mismos
        # que antes, evitamos el spam por cada edición del coordinador.
        faltantes_despues = _campos_perfil_faltantes(miembro)
        if faltantes_despues and faltantes_despues != faltantes_antes:
            await _publicar_perfil_incompleto(miembro)

        return await _fetch_miembro(session, miembro.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_EDITAR")])
    async def anonimizar_miembro(
        self,
        info: strawberry.Info,
        miembro_id: uuid.UUID,
    ) -> 'MiembroType':
        """RGPD — anonimiza de forma irreversible los datos personales del
        miembro. El registro se conserva (para estadística e histórico) pero
        despojado de toda información identificativa. Solo se permite sobre
        miembros dados de baja.
        """
        session = info.context.session
        miembro = await _fetch_miembro(session, miembro_id)

        if miembro.datos_anonimizados:
            raise ValueError("Los datos de este miembro ya están anonimizados.")
        if miembro.fecha_baja is None:
            raise ValueError(
                "Solo pueden anonimizarse los datos de un miembro dado de baja."
            )

        # Despojar de toda información personal identificativa.
        miembro.nombre = "Anonimizado"
        miembro.apellido1 = "Anonimizado"
        miembro.apellido2 = None
        miembro.fecha_nacimiento = None
        miembro.sexo = None
        miembro.tipo_documento = None
        miembro.numero_documento = None
        miembro.direccion = None
        miembro.codigo_postal = None
        miembro.localidad = None
        miembro.telefono = None
        miembro.telefono2 = None
        miembro.email = None
        miembro.iban = None
        miembro.swift_bic = None
        miembro.referencia_pago = None
        miembro.foto_url = None
        miembro.observaciones = None
        miembro.observaciones_voluntariado = None

        miembro.datos_anonimizados = True
        miembro.fecha_anonimizacion = date.today()

        await session.commit()
        return await _fetch_miembro(session, miembro_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("SOC_EXPORT")])
    async def exportar_miembros_xlsx(
        self,
        info: strawberry.Info,
        ids: List[uuid.UUID],
    ) -> str:
        """Exporta a XLSX los miembros indicados (los visibles con los filtros
        aplicados en el listado). Devuelve el contenido del fichero en base64.
        """
        import base64
        import io
        from openpyxl import Workbook
        from openpyxl.styles import Font
        from openpyxl.utils import get_column_letter

        session = info.context.session
        if not ids:
            raise ValueError("No hay miembros que exportar.")

        result = await session.execute(select(Miembro).where(Miembro.id.in_(ids)))
        miembros = list(result.scalars().all())
        miembros.sort(key=lambda m: (
            (m.apellido1 or '').lower(),
            (m.apellido2 or '').lower(),
            (m.nombre or '').lower(),
        ))

        wb = Workbook()
        ws = wb.active
        ws.title = "Miembros"
        cabecera = [
            "Nombre", "Primer apellido", "Segundo apellido", "Tipo", "Situación",
            "Email", "Teléfono", "Agrupación", "Localidad", "Fecha de alta", "Fecha de baja",
        ]
        ws.append(cabecera)
        for celda in ws[1]:
            celda.font = Font(bold=True)

        for m in miembros:
            ws.append([
                m.nombre or '',
                m.apellido1 or '',
                m.apellido2 or '',
                m.tipo_miembro.nombre if m.tipo_miembro else '',
                m.estado.nombre if m.estado else '',
                m.email or '',
                m.telefono or '',
                m.agrupacion.nombre if m.agrupacion else '',
                m.localidad or '',
                m.fecha_alta.isoformat() if m.fecha_alta else '',
                m.fecha_baja.isoformat() if m.fecha_baja else '',
            ])

        anchos = [16, 16, 16, 14, 14, 30, 14, 26, 20, 13, 13]
        for i, ancho in enumerate(anchos, start=1):
            ws.column_dimensions[get_column_letter(i)].width = ancho
        ws.freeze_panes = "A2"

        buf = io.BytesIO()
        wb.save(buf)
        return base64.b64encode(buf.getvalue()).decode()


@strawberry.type(name="VoluntarioAmbito")
class VoluntarioAmbitoType:
    """Voluntario (subconjunto de Miembro) para el listado con scoping de ámbito.

    Vista de listado; no confundir con la entidad `Voluntario` (satélite de
    Vinculacion del modelo CRM), que posee el nombre GraphQL `Voluntario`.
    """
    id: uuid.UUID
    nombre: str
    apellido1: str
    apellido2: Optional[str]
    email: Optional[str]
    telefono: Optional[str]
    disponibilidad: Optional[str]
    horas_disponibles_semana: Optional[int]
    profesion: Optional[str]
    nivel_estudios_id: Optional[uuid.UUID]
    intereses: Optional[str]
    puede_conducir: bool
    vehiculo_propio: bool
    disponibilidad_viajar: bool
    activo: bool
    fecha_alta: Optional[date]


@strawberry.type
class MembresiaQuery:
    @strawberry.field(permission_classes=[RequireTransaction("VOL_LIST")])
    async def voluntarios_en_ambito(self, info: strawberry.Info) -> List[VoluntarioAmbitoType]:
        """Voluntarios visibles según el ámbito territorial del usuario (Fase 2).

        - Rol general (presidencia / rol en unidad raíz) → todos los voluntarios.
        - Rol territorial → voluntarios de su agrupación + descendientes.
        - Sin ámbito territorial → lista vacía por esta vía.
        (El scoping por campaña de COORDINADOR_CAMPANA se resolverá aparte.)
        """
        from app.modules.acceso.services.ambito_territorial import (
            agrupaciones_en_ambito, miembros_de_campanias_coordinadas,
        )
        session = info.context.session
        user = info.context.user
        ambito = await agrupaciones_en_ambito(session, user.id) if user else set()

        q = select(Miembro).where(
            Miembro.es_voluntario == True,  # noqa: E712
            Miembro.eliminado == False,     # noqa: E712
        )
        if ambito is not None:              # None = global (sin filtro)
            conds = []
            if ambito:
                conds.append(Miembro.agrupacion_id.in_(ambito))
            camp_ids = await miembros_de_campanias_coordinadas(session, user.id) if user else set()
            if camp_ids:
                conds.append(Miembro.id.in_(camp_ids))
            if not conds:
                return []
            q = q.where(or_(*conds))

        r = await session.execute(q.order_by(Miembro.apellido1, Miembro.nombre))
        return [
            VoluntarioAmbitoType(
                id=m.id, nombre=m.nombre, apellido1=m.apellido1, apellido2=m.apellido2,
                email=m.email, telefono=m.telefono, disponibilidad=m.disponibilidad,
                horas_disponibles_semana=m.horas_disponibles_semana, profesion=m.profesion,
                nivel_estudios_id=m.nivel_estudios_id, intereses=m.intereses,
                puede_conducir=m.puede_conducir, vehiculo_propio=m.vehiculo_propio,
                disponibilidad_viajar=m.disponibilidad_viajar,
                activo=m.activo, fecha_alta=m.fecha_alta,
            )
            for m in r.scalars().all()
        ]
