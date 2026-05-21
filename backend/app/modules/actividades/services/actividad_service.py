"""Servicio del módulo Actividades.

Cubre el ciclo de vida completo de Actividad, Tarea, Participacion y GrupoTrabajo:
  - Creación con validación de la taxonomía (PUNTUAL / RECURRENTE / PERMANENTE)
  - Actualización parcial con re-validación de reglas duras
  - Transiciones de estado (genérica y con aprobación)
  - Cierre con datos de valoración final
  - Gestión de participantes (miembro o externo, deduplicación)
  - Grupos de trabajo con resolución de TipoGrupo por defecto

Decisiones de diseño:
  D-ACT-1  La validación del carácter (PUNTUAL/RECURRENTE/PERMANENTE) es responsabilidad
           del servicio, no del resolver.
  D-ACT-2  El helper _apply_fields() aplica solo valores no-None para actualizaciones parciales.
  D-ACT-3  aprobar_actividad() registra aprobado_por_id y fecha_aprobacion;
           transicionar_actividad() solo cambia el estado.
  D-ACT-4  crear_grupo_trabajo() resuelve el TipoGrupo activo por defecto si no se indica.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.actividades.models.actividad import Actividad, Participacion
from app.modules.actividades.models.tarea import Tarea
from app.modules.actividades.models.grupo import GrupoTrabajo, TipoGrupo


# ─── Constantes de dominio ──────────────────────────────────────────────

_CARACTERES_VALIDOS = frozenset({"PUNTUAL", "RECURRENTE", "PERMANENTE"})

_ACTIVIDAD_CAMPOS = (
    "nombre", "tipo_actividad_id", "estado_id", "descripcion",
    "padre_id", "es_recurrente", "periodicidad", "caracter",
    "campania_id", "grupo_id", "responsable_id",
    "fecha_inicio", "hora_inicio", "fecha_fin", "hora_fin",
    "duracion_horas", "duracion_dias",
    "lugar", "direccion", "localidad", "provincia",
    "aforo", "es_online", "url_online",
    "presupuesto_estimado", "presupuesto_ejecutado", "eliminado",
)

_TAREA_CAMPOS = (
    "titulo", "estado_id", "descripcion", "prioridad", "orden",
    "responsable_id", "horas_estimadas", "horas_reales", "fecha_limite",
)


def _apply_fields(target, data, fields: tuple, *, skip_none: bool = True) -> None:
    """Aplica campos de `data` a `target` omitiendo None (actualización parcial)."""
    for f in fields:
        v = getattr(data, f, None)
        if skip_none and v is None:
            continue
        setattr(target, f, v)


# ─── Validación de dominio ───────────────────────────────────────────────

def validar_caracter_actividad(
    *,
    caracter: str,
    campania_id,
    es_recurrente: bool,
    padre_id,
) -> None:
    """Aplica las reglas duras de la taxonomía de actividades.

    PERMANENTE  → sin campaña, sin recurrencia, sin padre
    PUNTUAL     → sin recurrencia, sin padre
    RECURRENTE  → plantilla (es_recurrente=True, padre_id=None)
                  o instancia (padre_id != None)

    Raises ValueError con mensaje claro si se viola una regla.
    """
    if caracter not in _CARACTERES_VALIDOS:
        raise ValueError(
            f"caracter '{caracter}' no es válido. "
            f"Valores aceptados: PUNTUAL, RECURRENTE, PERMANENTE."
        )
    if caracter == "PERMANENTE":
        if campania_id is not None:
            raise ValueError("Una actividad PERMANENTE no puede estar adscrita a una campaña.")
        if es_recurrente:
            raise ValueError("Una actividad PERMANENTE no puede ser recurrente.")
        if padre_id is not None:
            raise ValueError("Una actividad PERMANENTE no puede tener padre.")
    elif caracter == "PUNTUAL":
        if es_recurrente:
            raise ValueError("Una actividad PUNTUAL no puede ser recurrente.")
        if padre_id is not None:
            raise ValueError("Una actividad PUNTUAL no puede tener padre.")
    elif caracter == "RECURRENTE":
        if not es_recurrente and padre_id is None:
            raise ValueError(
                "Una actividad RECURRENTE debe ser plantilla (es_recurrente=True) "
                "o instancia (padre_id informado)."
            )


# ─── Servicio ────────────────────────────────────────────────────────────

class ActividadService:
    """Servicio para el ciclo de vida de actividades, tareas, participaciones y grupos."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Actividades ───────────────────────────────────────────────────────────

    async def crear_actividad(self, data) -> Actividad:
        """Crea una actividad validando la taxonomía (D-ACT-1)."""
        validar_caracter_actividad(
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
        self.session.add(actividad)
        await self.session.commit()
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad.id))
        return r.scalar_one()

    async def actualizar_actividad(self, data) -> Actividad:
        """Actualización parcial con re-validación de reglas duras (D-ACT-2)."""
        r = await self.session.execute(select(Actividad).where(Actividad.id == data.id))
        actividad = r.scalar_one()
        _apply_fields(actividad, data, _ACTIVIDAD_CAMPOS)
        validar_caracter_actividad(
            caracter=actividad.caracter,
            campania_id=actividad.campania_id,
            es_recurrente=actividad.es_recurrente,
            padre_id=actividad.padre_id,
        )
        if data.eliminado is True and not actividad.fecha_eliminacion:
            actividad.fecha_eliminacion = datetime.utcnow()
        await self.session.commit()
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad.id))
        return r.scalar_one()

    async def transicionar_actividad(
        self, id: UUID, estado_id: UUID, notas: Optional[str] = None,
    ) -> Actividad:
        """Cambia el estado de una actividad sin registrar aprobador (D-ACT-3)."""
        r = await self.session.execute(select(Actividad).where(Actividad.id == id))
        actividad = r.scalar_one()
        actividad.estado_id = estado_id
        if notas:
            actividad.notas_aprobacion = notas
        await self.session.commit()
        r = await self.session.execute(select(Actividad).where(Actividad.id == id))
        return r.scalar_one()

    async def aprobar_actividad(
        self,
        id: UUID,
        estado_id: UUID,
        aprobado_por_id: Optional[UUID] = None,
        notas: Optional[str] = None,
    ) -> Actividad:
        """Aprueba o rechaza registrando aprobador y fecha (D-ACT-3)."""
        r = await self.session.execute(select(Actividad).where(Actividad.id == id))
        actividad = r.scalar_one()
        actividad.estado_id = estado_id
        if aprobado_por_id:
            actividad.aprobado_por_id = aprobado_por_id
            actividad.fecha_aprobacion = date.today()
        if notas is not None:
            actividad.notas_aprobacion = notas
        await self.session.commit()
        r = await self.session.execute(select(Actividad).where(Actividad.id == id))
        return r.scalar_one()

    async def cerrar_actividad(
        self,
        id: UUID,
        valoracion: Optional[str] = None,
        objetivos_cumplidos: Optional[bool] = None,
        asistencia_real: Optional[int] = None,
        presupuesto_ejecutado: Optional[Decimal] = None,
        estado_id: Optional[UUID] = None,
    ) -> Actividad:
        """Cierre con datos de valoración final."""
        r = await self.session.execute(select(Actividad).where(Actividad.id == id))
        actividad = r.scalar_one()
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
        await self.session.commit()
        r = await self.session.execute(select(Actividad).where(Actividad.id == id))
        return r.scalar_one()

    # ── Tareas ───────────────────────────────────────────────────────────────

    async def crear_tarea(self, data) -> Tarea:
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
        self.session.add(tarea)
        await self.session.commit()
        r = await self.session.execute(select(Tarea).where(Tarea.id == tarea.id))
        return r.scalar_one()

    async def actualizar_tarea(self, data) -> Tarea:
        r = await self.session.execute(select(Tarea).where(Tarea.id == data.id))
        tarea = r.scalar_one()
        _apply_fields(tarea, data, _TAREA_CAMPOS)
        await self.session.commit()
        r = await self.session.execute(select(Tarea).where(Tarea.id == tarea.id))
        return r.scalar_one()

    # ── Participaciones ─────────────────────────────────────────────────────────

    async def crear_participacion(self, data) -> Participacion:
        """Crea una participación evitando duplicados por miembro o email externo."""
        if data.miembro_id is not None:
            existe = await self.session.execute(
                select(Participacion).where(
                    Participacion.actividad_id == data.actividad_id,
                    Participacion.miembro_id == data.miembro_id,
                )
            )
            if existe.scalar_one_or_none() is not None:
                raise ValueError("Este miembro ya está registrado como participante de la actividad.")
        elif data.email_externo:
            existe = await self.session.execute(
                select(Participacion).where(
                    Participacion.actividad_id == data.actividad_id,
                    Participacion.email_externo == data.email_externo,
                )
            )
            if existe.scalar_one_or_none() is not None:
                raise ValueError("Ya existe un participante externo con ese email en la actividad.")

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
        self.session.add(p)
        await self.session.commit()
        r = await self.session.execute(select(Participacion).where(Participacion.id == p.id))
        return r.scalar_one()

    # ── Grupos de trabajo ──────────────────────────────────────────────────────

    async def crear_grupo_trabajo(
        self,
        nombre: str,
        tipo_grupo_id: Optional[UUID] = None,
        descripcion: Optional[str] = None,
        objetivo: Optional[str] = None,
        fecha_inicio=None,
        fecha_fin=None,
        coordinador_id: Optional[UUID] = None,
        agrupacion_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
    ) -> GrupoTrabajo:
        """Crea GrupoTrabajo resolviendo TipoGrupo por defecto si no se indica (D-ACT-4)."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del grupo es obligatorio.")

        if tipo_grupo_id is None:
            r = await self.session.execute(
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
            r = await self.session.execute(
                select(TipoGrupo).where(TipoGrupo.id == tipo_grupo_id)
            )
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
        self.session.add(grupo)
        await self.session.commit()
        await self.session.refresh(grupo)
        return grupo
