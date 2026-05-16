"""Resolvers custom para Campañas."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

import strawberry
from sqlalchemy import select, delete as sa_delete

from app.modules.actividades.models.campana import (
    Campania, MetaCampania, PartidaPresupuestoCampania,
    PlantillaCampania, PlantillaMeta, PlantillaPartida, PlantillaActividad, PlantillaTarea,
)
from app.modules.core.comunicacion.plantilla_email import PlantillaEmail
from app.modules.actividades.models.grupo import RequisitoRecurso
from app.modules.membresia.models.miembro import Miembro
from app.modules.core.geografico.direccion import UnidadOrganizativa
from app.modules.configuracion.models.configuracion import Configuracion
from app.core.email_service import EmailService
from app.graphql.types_auto import CampaniaType, PlantillaCampaniaType, PlantillaActividadType, PlantillaTareaType
from app.graphql.permissions import RequireTransaction


@strawberry.input
class CampaniaCreateInput:
    nombre: str
    tipo_campania_id: uuid.UUID
    estado_id: uuid.UUID
    fecha_inicio_plan: Optional[date] = None
    fecha_fin_plan: Optional[date] = None
    responsable_id: Optional[uuid.UUID] = None
    agrupacion_id: Optional[uuid.UUID] = None
    lema: Optional[str] = None
    descripcion_corta: Optional[str] = None
    descripcion_larga: Optional[str] = None
    url_externa: Optional[str] = None
    foto_url: Optional[str] = None
    objetivo_principal: Optional[str] = None
    es_recurrente: Optional[bool] = None
    periodicidad: Optional[str] = None


@strawberry.input
class CampaniaUpdateInput:
    campania_id: uuid.UUID
    nombre: Optional[str] = None
    tipo_campania_id: Optional[uuid.UUID] = None
    estado_id: Optional[uuid.UUID] = None
    fecha_inicio_plan: Optional[date] = None
    fecha_fin_plan: Optional[date] = None
    responsable_id: Optional[uuid.UUID] = None
    agrupacion_id: Optional[uuid.UUID] = None
    lema: Optional[str] = None
    descripcion_corta: Optional[str] = None
    descripcion_larga: Optional[str] = None
    url_externa: Optional[str] = None
    foto_url: Optional[str] = None
    objetivo_principal: Optional[str] = None
    es_recurrente: Optional[bool] = None
    periodicidad: Optional[str] = None


@strawberry.input
class MetaInput:
    tipo_meta_id: uuid.UUID
    valor_planificado: Optional[Decimal] = None
    notas: Optional[str] = None
    orden: int = 0


@strawberry.input
class PartidaInput:
    concepto: str
    importe_estimado: Optional[Decimal] = None
    tipo_partida: str = 'gasto'
    orden: int = 0


@strawberry.input
class ResultadoMetaInput:
    meta_id: uuid.UUID
    valor_real: Decimal


@strawberry.input
class ResultadoPartidaInput:
    partida_id: uuid.UUID
    importe_real: Decimal


@strawberry.input
class PlantillaCreateInput:
    tipo_campania_id: uuid.UUID
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class PlantillaUpdateInput:
    plantilla_id: uuid.UUID
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


@strawberry.input
class PlantillaMetaItemInput:
    tipo_meta_id: uuid.UUID
    valor_sugerido: Optional[Decimal] = None
    notas: Optional[str] = None
    orden: int = 0


@strawberry.input
class PlantillaPartidaItemInput:
    concepto: str
    importe_estimado: Optional[Decimal] = None
    tipo_partida: str = 'gasto'
    orden: int = 0


@strawberry.input
class PlantillaActividadItemInput:
    plantilla_id: uuid.UUID
    nombre: str
    descripcion: Optional[str] = None
    duracion_dias: int = 0
    orden: int = 0
    tipo_actividad_id: Optional[uuid.UUID] = None


@strawberry.input
class PlantillaActividadUpdateItemInput:
    actividad_id: uuid.UUID
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    duracion_dias: Optional[int] = None
    orden: Optional[int] = None
    tipo_actividad_id: Optional[uuid.UUID] = None


@strawberry.input
class PlantillaTareaItemInput:
    actividad_id: uuid.UUID
    titulo: str
    descripcion: Optional[str] = None
    horas_estimadas: Optional[Decimal] = None
    orden: int = 0
    habilidad_id: Optional[uuid.UUID] = None
    nivel_habilidad_id: Optional[uuid.UUID] = None


@strawberry.input
class PlantillaTareaUpdateItemInput:
    tarea_id: uuid.UUID
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    horas_estimadas: Optional[Decimal] = None
    orden: Optional[int] = None
    habilidad_id: Optional[uuid.UUID] = None
    nivel_habilidad_id: Optional[uuid.UUID] = None


@strawberry.type
class NotificacionCampaniaPreview:
    asunto: str
    cuerpo_html: str
    total_destinatarios: int


@strawberry.type
class ResultadoEnvioNotificacion:
    enviados: int
    fallidos: int
    sin_email: int
    total: int
    simulado: bool = False
    mensaje: Optional[str] = None


def _renderizar_plantilla(asunto: str, cuerpo_html: str, **variables) -> tuple[str, str]:
    """Sustituye {{ variable }} en asunto y cuerpo_html con los valores dados.

    También procesa bloques {% if var %}…{% endif %} eliminando el bloque entero
    cuando la variable es falsa/vacía.
    """
    import re

    def _render(texto: str) -> str:
        # {% if var %}…{% endif %} — elimina el bloque si var es falso/vacío
        def repl_if(m):
            key = m.group(1).strip()
            val = variables.get(key)
            if val and (not isinstance(val, (list, str)) or val):
                inner = m.group(2)
                return inner
            return ""
        texto = re.sub(r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}', repl_if, texto, flags=re.DOTALL)

        # {% for req in requisitos_recursos %}…{% endfor %}
        def repl_for(m):
            lista = variables.get("requisitos_recursos") or []
            item_tmpl = m.group(1)
            parts = []
            for item in lista:
                line = item_tmpl
                for k, v in item.items():
                    line = line.replace(f"{{{{ req.{k} }}}}", str(v))
                parts.append(line)
            return "".join(parts)
        texto = re.sub(r'\{%\s*for\s+req\s+in\s+requisitos_recursos\s*%\}(.*?)\{%\s*endfor\s*%\}', repl_for, texto, flags=re.DOTALL)

        # {{ variable }}
        for key, val in variables.items():
            if isinstance(val, list):
                continue
            texto = texto.replace(f"{{{{ {key} }}}}", str(val) if val else "")

        return texto

    return _render(asunto), _render(cuerpo_html)


async def _fetch_campania(session, campania_id: uuid.UUID) -> Campania:
    stmt = select(Campania).where(Campania.id == campania_id)
    result = await session.execute(stmt)
    return result.scalar_one()


async def _fetch_plantilla(session, plantilla_id: uuid.UUID) -> PlantillaCampania:
    stmt = select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id)
    result = await session.execute(stmt)
    return result.scalar_one()


@strawberry.type
class CampaniaResolverMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_CREATE")])
    async def crear_campania(
        self,
        info: strawberry.Info,
        data: CampaniaCreateInput,
    ) -> CampaniaType:
        session = info.context.session
        campania = Campania(
            nombre=data.nombre,
            tipo_campania_id=data.tipo_campania_id,
            estado_id=data.estado_id,
            fecha_inicio_plan=data.fecha_inicio_plan,
            fecha_fin_plan=data.fecha_fin_plan,
            responsable_id=data.responsable_id,
            agrupacion_id=data.agrupacion_id,
            lema=data.lema,
            descripcion_corta=data.descripcion_corta,
            descripcion_larga=data.descripcion_larga,
            url_externa=data.url_externa,
            foto_url=data.foto_url,
            objetivo_principal=data.objetivo_principal,
            es_recurrente=data.es_recurrente or False,
            periodicidad=data.periodicidad,
        )
        session.add(campania)
        await session.commit()
        return await _fetch_campania(session, campania.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def actualizar_campania(
        self,
        info: strawberry.Info,
        data: CampaniaUpdateInput,
    ) -> CampaniaType:
        session = info.context.session
        campania = await _fetch_campania(session, data.campania_id)
        campos = [
            'nombre', 'tipo_campania_id', 'estado_id',
            'fecha_inicio_plan', 'fecha_fin_plan',
            'responsable_id', 'agrupacion_id',
            'lema', 'descripcion_corta', 'descripcion_larga', 'url_externa', 'foto_url',
            'objetivo_principal', 'es_recurrente', 'periodicidad',
        ]
        for campo in campos:
            valor = getattr(data, campo, None)
            if valor is not None:
                setattr(campania, campo, valor)
        await session.commit()
        return await _fetch_campania(session, campania.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def transicionar_campania(
        self, info: strawberry.Info,
        id: uuid.UUID,
        estado_id: uuid.UUID,
        notas: Optional[str] = None,
    ) -> CampaniaType:
        """Cambia el estado de una campaña."""
        session = info.context.session
        campania = await _fetch_campania(session, id)
        campania.estado_id = estado_id
        if notas:
            campania.notas_aprobacion = notas
        await session.commit()
        return await _fetch_campania(session, id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_APPROVE")])
    async def aprobar_campania(
        self, info: strawberry.Info,
        id: uuid.UUID,
        estado_id: uuid.UUID,
        notas: Optional[str] = None,
    ) -> CampaniaType:
        """Aprueba o rechaza una campaña (requiere CAMP_APPROVE)."""
        session = info.context.session
        campania = await _fetch_campania(session, id)
        campania.estado_id = estado_id
        user_id = getattr(info.context, 'user_id', None)
        if user_id:
            campania.aprobado_por_id = user_id
            campania.fecha_aprobacion = date.today()
        if notas is not None:
            campania.notas_aprobacion = notas
        await session.commit()
        return await _fetch_campania(session, id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def previsualizar_notificacion_campania(
        self, info: strawberry.Info,
        campania_id: uuid.UUID,
        plantilla_codigo: Optional[str] = None,
    ) -> "NotificacionCampaniaPreview":
        """Carga la plantilla indicada y sustituye las variables con los datos reales.

        Si no se indica `plantilla_codigo`, usa `CAMP_APROBACION` por defecto.
        Devuelve asunto, cuerpo HTML renderizado y total de destinatarios.
        No envía nada — sólo genera la previsualización.
        """
        session = info.context.session
        campania = await _fetch_campania(session, campania_id)

        codigo = plantilla_codigo or 'CAMP_APROBACION'
        plantilla = (
            await session.execute(
                select(PlantillaEmail).where(
                    PlantillaEmail.codigo == codigo,
                    PlantillaEmail.activo == True,
                )
            )
        ).scalar_one_or_none()
        if plantilla is None:
            raise ValueError(f"Plantilla '{codigo}' no encontrada o desactivada.")

        # Nombre organización
        cfg_nombre = (
            await session.execute(
                select(Configuracion).where(Configuracion.clave == 'org.nombre')
            )
        ).scalar_one_or_none()
        nombre_org = cfg_nombre.valor if cfg_nombre else "La organización"

        # URL base de la app para el enlace
        cfg_url = (
            await session.execute(
                select(Configuracion).where(Configuracion.clave == 'org.web')
            )
        ).scalar_one_or_none()
        url_base = cfg_url.valor.rstrip('/') if cfg_url and cfg_url.valor else ""
        url_campanias = f"{url_base}/campanias" if url_base else "/campanias"

        # Requisitos de recursos del primer grupo vinculado a la campaña
        # (usamos RequisitoRecurso de los grupos de campaña)
        req_rows = (
            await session.execute(
                select(RequisitoRecurso).where(
                    RequisitoRecurso.grupo_id.in_(
                        select(RequisitoRecurso.grupo_id)
                    )
                )
            )
        ).scalars().all()
        # Simplificado: buscar requisitos cuyos grupos estén vinculados a la campaña
        from app.modules.actividades.models.grupo import GrupoIniciativa
        gi_rows = (
            await session.execute(
                select(GrupoIniciativa).where(GrupoIniciativa.campania_id == campania_id)
            )
        ).scalars().all()
        grupo_ids = {gi.grupo_id for gi in gi_rows}
        requisitos = []
        if grupo_ids:
            req_rows = (
                await session.execute(
                    select(RequisitoRecurso).where(
                        RequisitoRecurso.grupo_id.in_(grupo_ids)
                    )
                )
            ).scalars().all()
            requisitos = [
                {
                    "habilidad": str(r.especialidad_id),
                    "nivel": str(r.nivel_id) if r.nivel_id else "—",
                    "horas": str(r.horas_necesarias),
                }
                for r in req_rows
            ]

        # Total de destinatarios: miembros activos con email de la agrupación
        total_destinatarios = 0
        if campania.agrupacion_id:
            count = (
                await session.execute(
                    select(Miembro).where(
                        Miembro.agrupacion_id == campania.agrupacion_id,
                        Miembro.email.isnot(None),
                        Miembro.eliminado == False,
                    )
                )
            ).scalars().all()
            total_destinatarios = len(count)

        # Renderizar con Jinja2-lite (sustitución simple de variables {{ }})
        asunto, cuerpo_html = _renderizar_plantilla(
            plantilla.asunto,
            plantilla.cuerpo_html,
            nombre_miembro="[nombre destinatario]",
            nombre_campania=campania.nombre,
            lema=campania.lema or "",
            objetivo_principal=campania.objetivo_principal or "",
            presupuesto_estimado=str(campania.presupuesto_estimado or ""),
            requisitos_recursos=requisitos,
            url_campanias=url_campanias,
            nombre_organizacion=nombre_org,
        )

        return NotificacionCampaniaPreview(
            asunto=asunto,
            cuerpo_html=cuerpo_html,
            total_destinatarios=total_destinatarios,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def enviar_notificacion_campania(
        self, info: strawberry.Info,
        campania_id: uuid.UUID,
        asunto: str,
        cuerpo_html: str,
    ) -> "ResultadoEnvioNotificacion":
        """Envía el correo personalizado a todos los miembros activos con email de la agrupación.

        Si SMTP no está configurado, marca igualmente la campaña como notificada y
        devuelve un resultado simulado (no se puede volver a notificar).
        Marca `campania.notificacion_enviada = True` al finalizar.
        """
        session = info.context.session
        campania = await _fetch_campania(session, campania_id)

        if campania.notificacion_enviada:
            raise ValueError("Esta campaña ya fue notificada a la membresía.")

        if not campania.agrupacion_id:
            campania.notificacion_enviada = True
            await session.commit()
            return ResultadoEnvioNotificacion(
                enviados=0, fallidos=0, sin_email=0, total=0,
                simulado=True,
                mensaje="La campaña no tiene agrupación asignada — sin destinatarios.",
            )

        miembros = (
            await session.execute(
                select(Miembro).where(
                    Miembro.agrupacion_id == campania.agrupacion_id,
                    Miembro.eliminado == False,
                )
            )
        ).scalars().all()

        # Comprobar si SMTP está configurado antes de iterar.
        from app.core.email_service import _load_smtp_config
        smtp_cfg = await _load_smtp_config(session)
        if not smtp_cfg.configured:
            # Modo simulado: contar destinatarios potenciales y marcar flag.
            con_email = sum(1 for m in miembros if m.email)
            sin_email = len(miembros) - con_email
            campania.notificacion_enviada = True
            await session.commit()
            faltantes = ', '.join(smtp_cfg.campos_faltantes) if smtp_cfg.campos_faltantes else 'parámetros incompletos'
            return ResultadoEnvioNotificacion(
                enviados=con_email,
                fallidos=0,
                sin_email=sin_email,
                total=len(miembros),
                simulado=True,
                mensaje=f"Envío simulado: SMTP no configurado ({faltantes}). Se habrían notificado {con_email} miembros.",
            )

        email_svc = EmailService(session)
        enviados = fallidos = sin_email = 0

        for m in miembros:
            if not m.email:
                sin_email += 1
                continue
            nombre_destinatario = f"{m.nombre} {m.apellido1}".strip()
            cuerpo_personalizado = cuerpo_html.replace("[nombre destinatario]", nombre_destinatario)
            try:
                await email_svc.enviar(
                    destinatario=m.email,
                    asunto=asunto,
                    cuerpo_html=cuerpo_personalizado,
                )
                enviados += 1
            except Exception:
                fallidos += 1

        campania.notificacion_enviada = True
        await session.commit()

        return ResultadoEnvioNotificacion(
            enviados=enviados,
            fallidos=fallidos,
            sin_email=sin_email,
            total=len(miembros),
            simulado=False,
            mensaje=None,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def cerrar_campania(
        self, info: strawberry.Info,
        id: uuid.UUID,
        estado_id: uuid.UUID,
        presupuesto_ejecutado: Decimal,
        resultados_metas: list[ResultadoMetaInput],
        resultados_partidas: list[ResultadoPartidaInput],
        valoracion: Optional[str] = None,
    ) -> CampaniaType:
        """Cierra una campaña. Requiere presupuesto ejecutado + valor real de cada meta y partida."""
        from sqlalchemy import select as sa_select
        session = info.context.session
        campania = await _fetch_campania(session, id)

        # Cierre financiero
        campania.presupuesto_ejecutado = presupuesto_ejecutado

        # Resultados por meta (cierre operativo)
        for r in resultados_metas:
            meta = (await session.execute(
                sa_select(MetaCampania).where(MetaCampania.id == r.meta_id)
            )).scalar_one()
            meta.valor_real = r.valor_real

        # Resultados por partida
        for r in resultados_partidas:
            partida = (await session.execute(
                sa_select(PartidaPresupuestoCampania).where(PartidaPresupuestoCampania.id == r.partida_id)
            )).scalar_one()
            partida.importe_real = r.importe_real

        campania.estado_id = estado_id
        if valoracion is not None:
            campania.valoracion = valoracion

        await session.commit()
        return await _fetch_campania(session, id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def guardar_metas_campania(
        self, info: strawberry.Info,
        campania_id: uuid.UUID,
        metas: list[MetaInput],
    ) -> CampaniaType:
        """Reemplaza todas las metas de una campaña (delete + insert)."""
        session = info.context.session
        await session.execute(sa_delete(MetaCampania).where(MetaCampania.campania_id == campania_id))
        for m in metas:
            session.add(MetaCampania(
                campania_id=campania_id,
                tipo_meta_id=m.tipo_meta_id,
                valor_planificado=m.valor_planificado,
                notas=m.notas,
                orden=m.orden,
            ))
        await session.commit()
        return await _fetch_campania(session, campania_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def guardar_canales_campania(
        self, info: strawberry.Info,
        campania_id: uuid.UUID,
        canal_ids: list[uuid.UUID],
    ) -> CampaniaType:
        """Reemplaza todos los canales de difusión de una campaña."""
        from app.modules.actividades.models.campana import CanalDifusionCampania
        session = info.context.session
        await session.execute(sa_delete(CanalDifusionCampania).where(CanalDifusionCampania.campania_id == campania_id))
        for canal_id in canal_ids:
            session.add(CanalDifusionCampania(campania_id=campania_id, canal_id=canal_id))
        await session.commit()
        return await _fetch_campania(session, campania_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def guardar_partidas_campania(
        self, info: strawberry.Info,
        campania_id: uuid.UUID,
        partidas: list[PartidaInput],
    ) -> CampaniaType:
        """Reemplaza todas las partidas de presupuesto de una campaña."""
        session = info.context.session
        await session.execute(sa_delete(PartidaPresupuestoCampania).where(PartidaPresupuestoCampania.campania_id == campania_id))
        for p in partidas:
            session.add(PartidaPresupuestoCampania(
                campania_id=campania_id,
                concepto=p.concepto,
                importe_estimado=p.importe_estimado,
                tipo_partida=p.tipo_partida,
                orden=p.orden,
            ))
        await session.commit()
        return await _fetch_campania(session, campania_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def aplicar_plantilla(
        self, info: strawberry.Info,
        campania_id: uuid.UUID,
        plantilla_id: uuid.UUID,
    ) -> CampaniaType:
        """Clona las metas, partidas, actividades y tareas de una plantilla a una campaña."""
        from sqlalchemy import select as sa_select
        from app.modules.actividades.models.campana import CanalDifusionCampania
        from app.modules.actividades.models.actividad import Actividad
        from app.modules.actividades.models.tarea import Tarea
        session = info.context.session

        plantilla = (await session.execute(
            sa_select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id)
        )).scalar_one()

        campania = await _fetch_campania(session, campania_id)

        # Clonar metas
        for pm in plantilla.metas:
            session.add(MetaCampania(
                campania_id=campania_id,
                tipo_meta_id=pm.tipo_meta_id,
                valor_planificado=pm.valor_sugerido,
                notas=pm.notas,
                orden=pm.orden,
            ))

        # Clonar partidas de presupuesto
        for pp in plantilla.partidas:
            session.add(PartidaPresupuestoCampania(
                campania_id=campania_id,
                concepto=pp.concepto,
                importe_estimado=pp.importe_estimado,
                tipo_partida=pp.tipo_partida,
                orden=pp.orden,
            ))

        # Clonar actividades y sus tareas
        for pa in plantilla.actividades:
            actividad = Actividad(
                nombre=pa.nombre,
                descripcion=pa.descripcion,
                tipo_actividad_id=pa.tipo_actividad_id,
                campania_id=campania_id,
            )
            # Calcular fecha si la campaña tiene fecha de inicio y el offset está definido
            if campania.fecha_inicio_plan and pa.duracion_dias is not None:
                from datetime import timedelta
                actividad.fecha_inicio = campania.fecha_inicio_plan + timedelta(days=pa.duracion_dias)
            session.add(actividad)
            await session.flush()  # obtener actividad.id

            for pt in pa.tareas:
                session.add(Tarea(
                    titulo=pt.titulo,
                    descripcion=pt.descripcion,
                    horas_estimadas=pt.horas_estimadas,
                    orden=pt.orden,
                    actividad_id=actividad.id,
                ))

        await session.commit()
        return await _fetch_campania(session, campania_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def crear_plantilla(
        self, info: strawberry.Info, data: PlantillaCreateInput,
    ) -> PlantillaCampaniaType:
        session = info.context.session
        plantilla = PlantillaCampania(
            tipo_campania_id=data.tipo_campania_id,
            nombre=data.nombre,
            descripcion=data.descripcion,
            activo=data.activo,
        )
        session.add(plantilla)
        await session.commit()
        return await _fetch_plantilla(session, plantilla.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def actualizar_plantilla(
        self, info: strawberry.Info, data: PlantillaUpdateInput,
    ) -> PlantillaCampaniaType:
        session = info.context.session
        plantilla = await _fetch_plantilla(session, data.plantilla_id)
        for campo in ('nombre', 'descripcion', 'activo'):
            valor = getattr(data, campo, None)
            if valor is not None:
                setattr(plantilla, campo, valor)
        await session.commit()
        return await _fetch_plantilla(session, plantilla.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def guardar_metas_plantilla(
        self, info: strawberry.Info,
        plantilla_id: uuid.UUID,
        metas: list[PlantillaMetaItemInput],
    ) -> PlantillaCampaniaType:
        session = info.context.session
        await session.execute(sa_delete(PlantillaMeta).where(PlantillaMeta.plantilla_id == plantilla_id))
        for m in metas:
            session.add(PlantillaMeta(
                plantilla_id=plantilla_id,
                tipo_meta_id=m.tipo_meta_id,
                valor_sugerido=m.valor_sugerido,
                notas=m.notas,
                orden=m.orden,
            ))
        await session.commit()
        return await _fetch_plantilla(session, plantilla_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def guardar_partidas_plantilla(
        self, info: strawberry.Info,
        plantilla_id: uuid.UUID,
        partidas: list[PlantillaPartidaItemInput],
    ) -> PlantillaCampaniaType:
        session = info.context.session
        await session.execute(sa_delete(PlantillaPartida).where(PlantillaPartida.plantilla_id == plantilla_id))
        for p in partidas:
            session.add(PlantillaPartida(
                plantilla_id=plantilla_id,
                concepto=p.concepto,
                importe_estimado=p.importe_estimado,
                tipo_partida=p.tipo_partida,
                orden=p.orden,
            ))
        await session.commit()
        return await _fetch_plantilla(session, plantilla_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def crear_plantilla_actividad(
        self, info: strawberry.Info, data: PlantillaActividadItemInput,
    ) -> PlantillaActividadType:
        session = info.context.session
        actividad = PlantillaActividad(
            plantilla_id=data.plantilla_id,
            nombre=data.nombre,
            descripcion=data.descripcion,
            duracion_dias=data.duracion_dias,
            orden=data.orden,
            tipo_actividad_id=data.tipo_actividad_id,
        )
        session.add(actividad)
        await session.commit()
        await session.refresh(actividad)
        return actividad

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def actualizar_plantilla_actividad(
        self, info: strawberry.Info, data: PlantillaActividadUpdateItemInput,
    ) -> PlantillaActividadType:
        session = info.context.session
        stmt = select(PlantillaActividad).where(PlantillaActividad.id == data.actividad_id)
        actividad = (await session.execute(stmt)).scalar_one()
        for campo in ('nombre', 'descripcion', 'duracion_dias', 'orden', 'tipo_actividad_id'):
            valor = getattr(data, campo, None)
            if valor is not None:
                setattr(actividad, campo, valor)
        await session.commit()
        await session.refresh(actividad)
        return actividad

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def crear_plantilla_tarea(
        self, info: strawberry.Info, data: PlantillaTareaItemInput,
    ) -> PlantillaTareaType:
        session = info.context.session
        tarea = PlantillaTarea(
            actividad_id=data.actividad_id,
            titulo=data.titulo,
            descripcion=data.descripcion,
            horas_estimadas=data.horas_estimadas,
            orden=data.orden,
            habilidad_id=data.habilidad_id,
            nivel_habilidad_id=data.nivel_habilidad_id,
        )
        session.add(tarea)
        await session.commit()
        await session.refresh(tarea)
        return tarea

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMP_EDIT")])
    async def actualizar_plantilla_tarea(
        self, info: strawberry.Info, data: PlantillaTareaUpdateItemInput,
    ) -> PlantillaTareaType:
        session = info.context.session
        stmt = select(PlantillaTarea).where(PlantillaTarea.id == data.tarea_id)
        tarea = (await session.execute(stmt)).scalar_one()
        for campo in ('titulo', 'descripcion', 'horas_estimadas', 'orden', 'habilidad_id', 'nivel_habilidad_id'):
            valor = getattr(data, campo, None)
            if valor is not None:
                setattr(tarea, campo, valor)
        await session.commit()
        await session.refresh(tarea)
        return tarea
