"""Resolvers custom para membresía.

Responsabilidad única: traducir la petición GraphQL en una llamada al
MembresiaService y devolver el resultado. Ninguna lógica de negocio aquí.

Motivo por el que este módulo existe (en lugar de usar strawchemy puro):
  strawchemy excluye las columnas FK UUID de los inputs auto-generados.
  Los inputs completos (con todos los FK UUID) se definen aquí.
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import Optional, List

import strawberry

from app.modules.membresia.services.membresia_service import MembresiaService
from app.graphql.types_auto import MiembroType
from app.graphql.permissions import RequireTransaction


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

@strawberry.input
class _MiembroBaseInput:
    """Campos compartidos entre creación y actualización."""
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


@strawberry.input
class MiembroCreateInput(_MiembroBaseInput):
    """Input para crear un miembro. Los campos obligatorios dejan de ser Optional."""
    nombre: str
    apellido1: str
    # Los demás se heredan como Optional desde la base.
    # Defaults explícitos para los booleanos no-nulos del modelo:
    es_socio_honor: bool = False
    activo: bool = True
    es_voluntario: bool = False
    puede_conducir: bool = False
    vehiculo_propio: bool = False
    disponibilidad_viajar: bool = False
    solicita_supresion_datos: bool = False
    datos_anonimizados: bool = False


@strawberry.input
class MiembroUpdateInput(_MiembroBaseInput):
    """Input para actualizar un miembro. Requiere id; el resto es opcional."""
    id: uuid.UUID


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------

@strawberry.type
class MembresiaResolverMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_CREAR")])
    async def crear_miembro(
        self,
        info: strawberry.Info,
        data: MiembroCreateInput,
    ) -> 'MiembroType':
        svc = MembresiaService(info.context.session)
        return await svc.crear(data)

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
        svc = MembresiaService(info.context.session)
        return await svc.crear_con_acceso(
            data=data,
            email=email,
            password=password,
            tipo_vinculacion_id=tipo_vinculacion_id,
            activo_usuario=activo_usuario,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_EDITAR")])
    async def actualizar_miembro(
        self,
        info: strawberry.Info,
        data: MiembroUpdateInput,
    ) -> 'MiembroType':
        svc = MembresiaService(info.context.session)
        return await svc.actualizar(data)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_EDITAR")])
    async def anonimizar_miembro(
        self,
        info: strawberry.Info,
        miembro_id: uuid.UUID,
    ) -> 'MiembroType':
        svc = MembresiaService(info.context.session)
        return await svc.anonimizar(miembro_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("SOC_EXPORT")])
    async def exportar_miembros_xlsx(
        self,
        info: strawberry.Info,
        ids: List[uuid.UUID],
    ) -> str:
        svc = MembresiaService(info.context.session)
        return await svc.exportar_xlsx(ids)
