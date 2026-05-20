"""Resolvers custom para Actividades, Tareas y Participaciones."""
from __future__ import annotations

import uuid
from datetime import date, time
from decimal import Decimal
from typing import Optional

import strawberry
from sqlalchemy import select

from app.modules.actividades.models.actividad import Actividad, Participacion
from app.modules.actividades.models.tarea import Tarea
from app.modules.actividades.models.grupo import GrupoTrabajo, TipoGrupo
from app.graphql.types_auto import ActividadType, TareaType, ParticipacionType, GrupoTrabajoType
from app.graphql.permissions import RequireTransaction


# ─────────────────────────────────────────────────────────────────────────────
# Actividad
# ─────────────────────────────────────────────────────────────────────────────

@strawberry.input
class ActividadCreateData:
    nombre: str
    tipo_actividad_id: uuid.UUID
    estado_id: uuid.UUID
    descripcion: Optional[str] = None
    padre_id: Optional[uuid.UUID] = None
    es_recurrente: bool = False
    periodicidad: Optional[str] = None
    # Taxonomía: PUNTUAL | RECURRENTE | PERMANENTE
    caracter: str = "PUNTUAL"
    campania_id: Optional[uuid.UUID] = None
    grupo_id: Optional[uuid.UUID] = None
    responsable_id: Optional[uuid.UUID] = None
    fecha_inicio: Optional[date] = None
    hora_inicio: Optional[time] = None
    fecha_fin: Optional[date] = None
    hora_fin: Optional[time] = None
    duracion_horas: Optional[Decimal] = None
    duracion_dias: Optional[int] = None
    lugar: Optional[str] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    aforo: Optional[int] = None
    es_online: bool = False
    url_online: Optional[str] = None
    presupuesto_estimado: Decimal = Decimal('0.00')


@strawberry.input
class ActividadUpdateData:
    id: uuid.UUID
    nombre: Optional[str] = None
    tipo_actividad_id: Optional[uuid.UUID] = None
    estado_id: Optional[uuid.UUID] = None
    descripcion: Optional[str] = None
    padre_id: Optional[uuid.UUID] = None
    es_recurrente: Optional[bool] = None
    periodicidad: Optional[str] = None
    caracter: Optional[str] = None
    campania_id: Optional[uuid.UUID] = None
    grupo_id: Optional[uuid.UUID] = None
    responsable_id: Optional[uuid.UUID] = None
    fecha_inicio: Optional[date] = None
    hora_inicio: Optional[time] = None
    fecha_fin: Optional[date] = None
    hora_fin: Optional[time] = None
    duracion_horas: Optional[Decimal] = None
    duracion_dias: Optional[int] = None
    lugar: Optional[str] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    aforo: Optional[int] = None
    es_online: Optional[bool] = None
    url_online: Optional[str] = None
    presupuesto_estimado: Optional[Decimal] = None
    presupuesto_ejecutado: Optional[Decimal] = None
    eliminado: Optional[bool] = None


# ─────────────────────────────────────────────────────────────────────────────
# Tarea
# ─────────────────────────────────────────────────────────────────────────────

@strawberry.input
class TareaCreateData:
    titulo: str
    estado_id: uuid.UUID
    descripcion: Optional[str] = None
    prioridad: int = 2
    orden: int = 0
    responsable_id: Optional[uuid.UUID] = None
    horas_estimadas: Optional[Decimal] = None
    horas_reales: Optional[Decimal] = None
    fecha_limite: Optional[date] = None
    actividad_id: Optional[uuid.UUID] = None
    grupo_id: Optional[uuid.UUID] = None


@strawberry.input
class TareaUpdateData:
    id: uuid.UUID
    titulo: Optional[str] = None
    estado_id: Optional[uuid.UUID] = None
    descripcion: Optional[str] = None
    prioridad: Optional[int] = None
    orden: Optional[int] = None
    responsable_id: Optional[uuid.UUID] = None
    horas_estimadas: Optional[Decimal] = None
    horas_reales: Optional[Decimal] = None
    fecha_limite: Optional[date] = None


# ─────────────────────────────────────────────────────────────────────────────
# Participacion
# ─────────────────────────────────────────────────────────────────────────────

@strawberry.input
class ParticipacionCreateData:
    actividad_id: uuid.UUID
    rol: str = 'asistente'
    miembro_id: Optional[uuid.UUID] = None
    nombre_externo: Optional[str] = None
    email_externo: Optional[str] = None
    confirmado: bool = False
    asistio: Optional[bool] = None
    horas_aportadas: Decimal = Decimal('0.00')


# ─────────────────────────────────────────────────────────────────────────────
# Mutation mixin
# ─────────────────────────────────────────────────────────────────────────────

def _apply(obj, data, fields):
    for f in fields:
        v = getattr(data, f, None)
        if v is not None:
            setattr(obj, f, v)


CARACTERES_VALIDOS = frozenset({"PUNTUAL", "RECURRENTE", "PERMANENTE"})


def _validar_caracter_actividad(*, caracter: str, campania_id, es_recurrente: bool, padre_id):
    """Aplica las reglas duras de la taxonomía. Lanza ValueError con mensaje claro."""
    if caracter not in CARACTERES_VALIDOS:
        raise ValueError(
            f"caracter '{caracter}' no es válido. Valores aceptados: PUNTUAL, RECURRENTE, PERMANENTE."
        )
    if caracter == "PERMANENTE":
        if campania_id is not None:
            raise ValueError("Una actividad PERMANENTE no puede estar adscrita a una campaña.")
        if es_recurrente:
            raise ValueError("Una actividad PERMANENTE no puede ser recurrente (es_recurrente=False obligatorio).")
        if padre_id is not None:
            raise ValueError("Una actividad PERMANENTE no puede tener padre (es independiente).")
    elif caracter == "PUNTUAL":
        if es_recurrente:
            raise ValueError("Una actividad PUNTUAL no puede ser recurrente.")
        if padre_id is not None:
            raise ValueError("Una actividad PUNTUAL no puede tener padre.")
    elif caracter == "RECURRENTE":
        # Permitido: plantilla (es_recurrente=True, padre_id=None) o instancia (padre_id != None).
        if not es_recurrente and padre_id is None:
            raise ValueError(
                "Una actividad RECURRENTE debe ser plantilla (es_recurrente=True) "
                "o instancia (padre_id informado)."
            )


@strawberry.type
class ActividadResolverMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_CREATE")])
    async def crear_actividad(self, info: strawberry.Info, data: ActividadCreateData) -> ActividadType:
        session = info.context.session
        _validar_caracter_actividad(
            caracter=data.caracter,
            campania_id=data.campania_id,
            es_recurrente=data.es_recurrente,
            padre_id=data.padre_id,
        )
        actividad = Actividad(
            nombre=data.nombre,
            tipo_actividad_id=data.tipo_actividad_id,
            estado_id=data.estado_id,
            descripcion=data.descripcion,
            padre_id=data.padre_id,
            es_recurrente=data.es_recurrente,
            periodicidad=data.periodicidad,
            caracter=data.caracter,
            campania_id=data.campania_id,
            grupo_id=data.grupo_id,
            responsable_id=data.responsable_id,
            fecha_inicio=data.fecha_inicio,
            hora_inicio=data.hora_inicio,
            fecha_fin=data.fecha_fin,
            hora_fin=data.hora_fin,
            duracion_horas=data.duracion_horas,
            duracion_dias=data.duracion_dias,
            lugar=data.lugar,
            direccion=data.direccion,
            localidad=data.localidad,
            provincia=data.provincia,
            aforo=data.aforo,
            es_online=data.es_online,
            url_online=data.url_online,
            presupuesto_estimado=data.presupuesto_estimado,
        )
        session.add(actividad)
        await session.commit()
        result = await session.execute(select(Actividad).where(Actividad.id == actividad.id))
        return result.scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def actualizar_actividad(self, info: strawberry.Info, data: ActividadUpdateData) -> ActividadType:
        session = info.context.session
        result = await session.execute(select(Actividad).where(Actividad.id == data.id))
        actividad = result.scalar_one()
        _apply(actividad, data, [
            'nombre', 'tipo_actividad_id', 'estado_id', 'descripcion',
            'padre_id', 'es_recurrente', 'periodicidad', 'caracter', 'campania_id',
            'grupo_id', 'responsable_id',
            'fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin',
            'duracion_horas', 'duracion_dias',
            'lugar', 'direccion', 'localidad', 'provincia', 'aforo',
            'es_online', 'url_online',
            'presupuesto_estimado', 'presupuesto_ejecutado', 'eliminado',
        ])
        # Re-validar reglas duras con el estado post-aplicación
        _validar_caracter_actividad(
            caracter=actividad.caracter,
            campania_id=actividad.campania_id,
            es_recurrente=actividad.es_recurrente,
            padre_id=actividad.padre_id,
        )
        if data.eliminado is True and not actividad.fecha_eliminacion:
            from datetime import datetime
            actividad.fecha_eliminacion = datetime.utcnow()
        await session.commit()
        result = await session.execute(select(Actividad).where(Actividad.id == actividad.id))
        return result.scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def crear_tarea(self, info: strawberry.Info, data: TareaCreateData) -> TareaType:
        session = info.context.session
        tarea = Tarea(
            titulo=data.titulo,
            estado_id=data.estado_id,
            descripcion=data.descripcion,
            prioridad=data.prioridad,
            orden=data.orden,
            responsable_id=data.responsable_id,
            horas_estimadas=data.horas_estimadas,
            horas_reales=data.horas_reales,
            fecha_limite=data.fecha_limite,
            actividad_id=data.actividad_id,
            grupo_id=data.grupo_id,
        )
        session.add(tarea)
        await session.commit()
        result = await session.execute(select(Tarea).where(Tarea.id == tarea.id))
        return result.scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def actualizar_tarea(self, info: strawberry.Info, data: TareaUpdateData) -> TareaType:
        session = info.context.session
        result = await session.execute(select(Tarea).where(Tarea.id == data.id))
        tarea = result.scalar_one()
        _apply(tarea, data, [
            'titulo', 'estado_id', 'descripcion', 'prioridad', 'orden',
            'responsable_id', 'horas_estimadas', 'horas_reales', 'fecha_limite',
        ])
        await session.commit()
        result = await session.execute(select(Tarea).where(Tarea.id == tarea.id))
        return result.scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("PART_MANAGE")])
    async def crear_participacion(self, info: strawberry.Info, data: ParticipacionCreateData) -> ParticipacionType:
        session = info.context.session

        if data.miembro_id is not None:
            existe = await session.execute(
                select(Participacion).where(
                    Participacion.actividad_id == data.actividad_id,
                    Participacion.miembro_id == data.miembro_id,
                )
            )
            if existe.scalar_one_or_none() is not None:
                raise ValueError("Este miembro ya está registrado como participante de la actividad")
        elif data.email_externo:
            existe = await session.execute(
                select(Participacion).where(
                    Participacion.actividad_id == data.actividad_id,
                    Participacion.email_externo == data.email_externo,
                )
            )
            if existe.scalar_one_or_none() is not None:
                raise ValueError("Ya existe un participante externo con ese email en la actividad")

        p = Participacion(
            actividad_id=data.actividad_id,
            rol=data.rol,
            miembro_id=data.miembro_id,
            nombre_externo=data.nombre_externo,
            email_externo=data.email_externo,
            confirmado=data.confirmado,
            asistio=data.asistio,
            horas_aportadas=data.horas_aportadas,
        )
        session.add(p)
        await session.commit()
        result = await session.execute(select(Participacion).where(Participacion.id == p.id))
        return result.scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def transicionar_actividad(
        self, info: strawberry.Info,
        id: uuid.UUID,
        estado_id: uuid.UUID,
        notas: Optional[str] = None,
    ) -> ActividadType:
        """Cambia el estado de una actividad (no aprobación — usar aprobar_actividad para eso)."""
        session = info.context.session
        result = await session.execute(select(Actividad).where(Actividad.id == id))
        actividad = result.scalar_one()
        actividad.estado_id = estado_id
        if notas:
            actividad.notas_aprobacion = notas
        await session.commit()
        result = await session.execute(select(Actividad).where(Actividad.id == id))
        return result.scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_APPROVE")])
    async def aprobar_actividad(
        self, info: strawberry.Info,
        id: uuid.UUID,
        estado_id: uuid.UUID,
        notas: Optional[str] = None,
    ) -> ActividadType:
        """Aprueba o rechaza una actividad (requiere ACT_APPROVE)."""
        from datetime import date as _date
        session = info.context.session
        result = await session.execute(select(Actividad).where(Actividad.id == id))
        actividad = result.scalar_one()
        actividad.estado_id = estado_id
        user_id = getattr(info.context, 'user_id', None)
        if user_id:
            actividad.aprobado_por_id = user_id
            actividad.fecha_aprobacion = _date.today()
        if notas is not None:
            actividad.notas_aprobacion = notas
        await session.commit()
        result = await session.execute(select(Actividad).where(Actividad.id == id))
        return result.scalar_one()

    # ─── Grupos de trabajo ─────────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("TEAM_CREATE")])
    async def crear_grupo_trabajo_seguro(
        self,
        info: strawberry.Info,
        nombre: str,
        tipo_grupo_id: Optional[uuid.UUID] = None,
        descripcion: Optional[str] = None,
        objetivo: Optional[str] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        coordinador_id: Optional[uuid.UUID] = None,
        agrupacion_id: Optional[uuid.UUID] = None,
        campania_id: Optional[uuid.UUID] = None,
    ) -> GrupoTrabajoType:
        """Crea un GrupoTrabajo con validación de `tipo_grupo_id`.

        Si no se indica tipo, usa el primer TipoGrupo activo como default
        (en su defecto eleva ValueError con mensaje claro, en lugar del
        IntegrityError críptico del NOT NULL).
        """
        session = info.context.session
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del grupo es obligatorio.")

        # Resolver tipo: si no llega, buscar uno activo por defecto
        if tipo_grupo_id is None:
            r = await session.execute(
                select(TipoGrupo).where(TipoGrupo.activo == True).order_by(TipoGrupo.nombre)
            )
            tipo = r.scalars().first()
            if not tipo:
                raise ValueError(
                    "No hay ningún TipoGrupo activo en el catálogo. "
                    "Crea al menos uno antes de crear grupos."
                )
            tipo_grupo_id = tipo.id
        else:
            r = await session.execute(select(TipoGrupo).where(TipoGrupo.id == tipo_grupo_id))
            if not r.scalars().first():
                raise ValueError(f"TipoGrupo {tipo_grupo_id} no encontrado.")

        grupo = GrupoTrabajo(
            nombre=nombre.strip(),
            tipo_grupo_id=tipo_grupo_id,
            descripcion=descripcion,
            objetivo=objetivo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            coordinador_id=coordinador_id,
            agrupacion_id=agrupacion_id,
            campania_id=campania_id,
            activo=True,
        )
        session.add(grupo)
        await session.commit()
        await session.refresh(grupo)
        return grupo

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def cerrar_actividad(
        self, info: strawberry.Info,
        id: uuid.UUID,
        valoracion: Optional[str] = None,
        objetivos_cumplidos: Optional[bool] = None,
        asistencia_real: Optional[int] = None,
        presupuesto_ejecutado: Optional[Decimal] = None,
        estado_id: Optional[uuid.UUID] = None,
    ) -> ActividadType:
        """Cierra una actividad con datos de valoración final."""
        session = info.context.session
        result = await session.execute(select(Actividad).where(Actividad.id == id))
        actividad = result.scalar_one()
        if valoracion is not None:
            actividad.valoracion = valoracion
        if objetivos_cumplidos is not None:
            actividad.objetivos_cumplidos = objetivos_cumplidos
        if asistencia_real is not None:
            actividad.asistencia_real = asistencia_real
        if presupuesto_ejecutado is not None:
            actividad.presupuesto_ejecutado = presupuesto_ejecutado
        if estado_id is not None:
            actividad.estado_id = estado_id
        await session.commit()
        result = await session.execute(select(Actividad).where(Actividad.id == id))
        return result.scalar_one()
