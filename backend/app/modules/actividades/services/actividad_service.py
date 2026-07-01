"""Servicio del módulo Actividades.

Cubre la lógica de negocio de actividades, tareas, participaciones y grupos
de trabajo que antes vivía directamente en los resolvers GraphQL.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.actividad import Actividad, AsistenciaActividad
from ..models.tarea import Tarea
from ..models.grupo import GrupoTrabajo, TipoGrupo
from app.modules.membresia.models.participacion import Participacion
from app.modules.configuracion.models.estados import EstadoAccion


CARACTERES_VALIDOS = frozenset({"PUNTUAL", "RECURRENTE", "PERMANENTE"})


class ActividadService:
    """Servicio de actividades, tareas, participaciones y grupos de trabajo."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Validación de dominio ─────────────────────────────────────────────────

    def validar_caracter(
        self, *, caracter: str, campania_id, es_recurrente: bool, padre_id,
    ) -> None:
        """Aplica las reglas duras de la taxonomía. Raises ValueError con mensaje claro."""
        if caracter not in CARACTERES_VALIDOS:
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

    # ── Actividades ────────────────────────────────────────────────────────────────

    async def crear(
        self, *, nombre: str, tipo_actividad_id: uuid.UUID, estado_id: uuid.UUID,
        caracter: str = "PUNTUAL", descripcion=None, padre_id=None,
        es_recurrente: bool = False, periodicidad=None, campania_id=None,
        grupo_id=None, responsable_id=None, fecha_inicio=None, hora_inicio=None,
        fecha_fin=None, hora_fin=None, duracion_horas=None, duracion_dias=None,
        lugar=None, direccion=None, localidad=None, provincia=None, aforo=None,
        es_online: bool = False, url_online=None,
        plataforma_telematica_id=None, datos_conexion_telematica=None,
        presupuesto_estimado: Decimal = Decimal("0.00"),
    ) -> Actividad:
        self.validar_caracter(
            caracter=caracter, campania_id=campania_id,
            es_recurrente=es_recurrente, padre_id=padre_id,
        )
        actividad = Actividad(
            nombre=nombre, tipo_actividad_id=tipo_actividad_id, estado_id=estado_id,
            descripcion=descripcion, padre_id=padre_id, es_recurrente=es_recurrente,
            periodicidad=periodicidad, caracter=caracter, campania_id=campania_id,
            grupo_id=grupo_id, responsable_id=responsable_id,
            fecha_inicio=fecha_inicio, hora_inicio=hora_inicio,
            fecha_fin=fecha_fin, hora_fin=hora_fin,
            duracion_horas=duracion_horas, duracion_dias=duracion_dias,
            lugar=lugar, direccion=direccion, localidad=localidad, provincia=provincia,
            aforo=aforo, es_online=es_online, url_online=url_online,
            plataforma_telematica_id=plataforma_telematica_id,
            datos_conexion_telematica=datos_conexion_telematica,
            presupuesto_estimado=presupuesto_estimado,
        )
        self.session.add(actividad)
        await self.session.commit()
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad.id))
        return r.scalar_one()

    async def actualizar(self, actividad_id: uuid.UUID, campos: dict) -> Actividad:
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad_id))
        actividad = r.scalar_one()
        for k, v in campos.items():
            if v is not None:
                setattr(actividad, k, v)
        self.validar_caracter(
            caracter=actividad.caracter, campania_id=actividad.campania_id,
            es_recurrente=actividad.es_recurrente, padre_id=actividad.padre_id,
        )
        if campos.get("eliminado") is True and not actividad.fecha_eliminacion:
            actividad.fecha_eliminacion = datetime.utcnow()
        await self.session.commit()
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad_id))
        return r.scalar_one()

    async def _validar_transicion(
        self, actividad: Actividad, estado_destino_id: uuid.UUID, notas=None,
    ) -> None:
        """Reglas duras de transición de estado de una actividad.

        Reglas:
          - Ninguna actividad puede pasar a 'En curso' sin una planificación de
            tareas. Toda actividad, por insignificante que sea, requiere preparación.
          - La cancelación de una actividad exige indicar los motivos.
        """
        if estado_destino_id == actividad.estado_id:
            return
        destino = await self.session.get(EstadoAccion, estado_destino_id)
        if destino is None:
            raise ValueError("El estado de destino no existe.")
        nombre_destino = (destino.nombre or "").lower()
        if "curso" in nombre_destino:
            n_tareas = await self.session.scalar(
                select(func.count(Tarea.id)).where(Tarea.actividad_id == actividad.id)
            )
            if not n_tareas:
                raise ValueError(
                    "No se puede iniciar la actividad sin una planificación de tareas. "
                    "Añade al menos una tarea de preparación antes de ponerla en curso."
                )
        if "cancel" in nombre_destino and not (notas and notas.strip()):
            raise ValueError(
                "Para cancelar la actividad debes indicar los motivos de la cancelación."
            )

    async def transicionar_estado(
        self, actividad_id: uuid.UUID, estado_id: uuid.UUID, notas=None,
    ) -> Actividad:
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad_id))
        actividad = r.scalar_one()
        await self._validar_transicion(actividad, estado_id, notas)
        actividad.estado_id = estado_id
        if notas:
            actividad.notas_aprobacion = notas
        await self.session.commit()
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad_id))
        return r.scalar_one()

    async def aprobar(
        self, actividad_id: uuid.UUID, estado_id: uuid.UUID,
        aprobado_por_id=None, notas=None,
    ) -> Actividad:
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad_id))
        actividad = r.scalar_one()
        actividad.estado_id = estado_id
        if aprobado_por_id:
            actividad.aprobado_por_id = aprobado_por_id
            actividad.fecha_aprobacion = date.today()
        if notas is not None:
            actividad.notas_aprobacion = notas
        await self.session.commit()
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad_id))
        return r.scalar_one()

    async def cerrar(
        self, actividad_id: uuid.UUID, estado_id=None, valoracion=None,
        objetivos_cumplidos=None, asistencia_real=None, presupuesto_ejecutado=None,
    ) -> Actividad:
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad_id))
        actividad = r.scalar_one()
        if estado_id is not None:
            destino = await self.session.get(EstadoAccion, estado_id)
            nombre_destino = (destino.nombre or "").lower() if destino else ""
            # El cierre/valoración no puede hacerse antes de la fecha de celebración.
            # La cancelación sí se permite en cualquier momento (va por transicionar_estado).
            if "finaliz" in nombre_destino and actividad.fecha_inicio and date.today() < actividad.fecha_inicio:
                raise ValueError(
                    "No se puede cerrar ni valorar la actividad antes de su fecha de "
                    f"celebración ({actividad.fecha_inicio.isoformat()}). "
                    "Si no va a celebrarse, cancélala indicando los motivos."
                )
            actividad.estado_id = estado_id
        if valoracion is not None: actividad.valoracion = valoracion
        if objetivos_cumplidos is not None: actividad.objetivos_cumplidos = objetivos_cumplidos
        if asistencia_real is not None: actividad.asistencia_real = asistencia_real
        if presupuesto_ejecutado is not None: actividad.presupuesto_ejecutado = presupuesto_ejecutado
        await self.session.commit()
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad_id))
        return r.scalar_one()

    # ── Tareas ──────────────────────────────────────────────────────────────────────

    async def crear_tarea(
        self, *, titulo: str, estado_id: uuid.UUID, descripcion=None,
        prioridad: int = 2, orden: int = 0, responsable_id=None,
        horas_estimadas=None, horas_reales=None, fecha_limite=None,
        actividad_id=None, grupo_id=None,
    ) -> Tarea:
        tarea = Tarea(
            titulo=titulo, estado_id=estado_id, descripcion=descripcion,
            prioridad=prioridad, orden=orden, responsable_id=responsable_id,
            horas_estimadas=horas_estimadas, horas_reales=horas_reales,
            fecha_limite=fecha_limite, actividad_id=actividad_id, grupo_id=grupo_id,
        )
        self.session.add(tarea)
        await self.session.commit()
        r = await self.session.execute(select(Tarea).where(Tarea.id == tarea.id))
        return r.scalar_one()

    async def actualizar_tarea(self, tarea_id: uuid.UUID, campos: dict) -> Tarea:
        r = await self.session.execute(select(Tarea).where(Tarea.id == tarea_id))
        tarea = r.scalar_one()
        for k, v in campos.items():
            if v is not None:
                setattr(tarea, k, v)
        await self.session.commit()
        r = await self.session.execute(select(Tarea).where(Tarea.id == tarea.id))
        return r.scalar_one()

    # ── Participaciones ───────────────────────────────────────────────────────────

    async def crear_participacion(
        self, *, actividad_id: uuid.UUID, rol: str = "asistente",
        miembro_id=None, nombre_externo=None, email_externo=None,
        confirmado: bool = False, asistio=None,
        horas_aportadas: Decimal = Decimal("0.00"),
    ) -> AsistenciaActividad:
        """Registra la asistencia de un contacto a una actividad.

        Modelo nuevo (Party-Role): se crea una `Participacion` base (tipo
        ASISTENCIA, ligada al Contacto) y su satélite `AsistenciaActividad`.
        El identificador de miembro coincide con el de su Contacto (la migración
        miembros→contactos preserva el UUID), por lo que `miembro_id` se usa
        como `contacto_id`.
        """
        if miembro_id is None:
            # El alta de un externo "al vuelo" como Contacto PF todavía no está
            # reconducida en este bundle (ver PENDIENTE_flujos del refactor CRM).
            raise ValueError(
                "Registrar un asistente externo requiere crear primero su Contacto; "
                "flujo pendiente de reconducción tras el refactor CRM."
            )

        contacto_id = miembro_id
        # Dedup: ¿ya hay asistencia de este contacto en esta actividad?
        existe = await self.session.execute(
            select(AsistenciaActividad)
            .join(Participacion, AsistenciaActividad.participacion_id == Participacion.id)
            .where(
                AsistenciaActividad.actividad_id == actividad_id,
                Participacion.contacto_id == contacto_id,
            )
        )
        if existe.scalar_one_or_none() is not None:
            raise ValueError("Este contacto ya está registrado como asistente de la actividad")

        participacion = Participacion(
            contacto_id=contacto_id, tipo="ASISTENCIA",
            estado="confirmada" if confirmado else "registrada",
        )
        self.session.add(participacion)
        await self.session.flush()

        asistencia = AsistenciaActividad(
            participacion_id=participacion.id, actividad_id=actividad_id,
            rol=rol, confirmado=confirmado, asistio=asistio,
            horas_aportadas=horas_aportadas,
        )
        self.session.add(asistencia)
        await self.session.commit()
        r = await self.session.execute(
            select(AsistenciaActividad).where(AsistenciaActividad.id == asistencia.id)
        )
        return r.scalar_one()

    # ── Grupos de trabajo ────────────────────────────────────────────────────────

    async def crear_grupo_trabajo(
        self, *, nombre: str, tipo_grupo_id=None, descripcion=None,
        objetivo=None, fecha_inicio=None, fecha_fin=None,
        coordinador_id=None, agrupacion_id=None, campania_id=None,
    ) -> GrupoTrabajo:
        """Crea un GrupoTrabajo resolviendo el tipo por defecto si no se indica.

        La agrupación territorial es obligatoria: fija el ámbito del que se nutren
        los integrantes (no puede entrar alguien de otra agrupación fuera de ese
        subárbol). Ver `candidatos_grupo(agrupacion_id=…)`."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del grupo es obligatorio.")
        if agrupacion_id is None:
            raise ValueError(
                "La agrupación territorial del grupo es obligatoria: define el ámbito "
                "del que se eligen sus integrantes."
            )
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
            r = await self.session.execute(select(TipoGrupo).where(TipoGrupo.id == tipo_grupo_id))
            if not r.scalars().first():
                raise ValueError(f"TipoGrupo {tipo_grupo_id} no encontrado.")
        grupo = GrupoTrabajo(
            nombre=nombre.strip(), tipo_grupo_id=tipo_grupo_id,
            descripcion=descripcion, objetivo=objetivo,
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
            coordinador_id=coordinador_id, agrupacion_id=agrupacion_id,
            campania_id=campania_id, activo=True,
        )
        self.session.add(grupo)
        await self.session.flush()

        # El coordinador designado al crear el grupo ENTRA como miembro con rol de
        # coordinador (tratamiento único: coordinador = uno de los miembros). Evita
        # el doble tratamiento cabecera vs miembro y que se pueda añadir dos veces.
        if coordinador_id:
            from ..models.grupo import RolGrupo, MiembroGrupo
            rol_coord = (await self.session.execute(
                select(RolGrupo).where(RolGrupo.es_coordinador == True)  # noqa: E712
            )).scalars().first()
            if rol_coord:
                self.session.add(MiembroGrupo(
                    grupo_id=grupo.id, miembro_id=coordinador_id,
                    rol_grupo_id=rol_coord.id, activo=True,
                ))

        await self.session.commit()
        await self.session.refresh(grupo)

        # Aviso de flujo: crear el canal de chat del grupo. Tras commit, envuelto;
        # un fallo de la creación del canal no afecta a la creación del grupo.
        try:
            from app.core.events import event_bus, GrupoTrabajoCreado
            await event_bus.publish(GrupoTrabajoCreado(
                grupo_id=str(grupo.id), nombre=grupo.nombre,
            ))
        except Exception:
            pass

        return grupo
