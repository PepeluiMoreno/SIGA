"""Servicio del módulo Campañas (parte 1/2).

Concentra la lógica de negocio que antes vivía en campania_resolvers.py:
renderizado de plantillas de email, envío de notificaciones, cierre,
clónación (con recursión) y propagación a subcampañas.

Para ensamblar el servicio completo en local:
  cat campania_service_p1.py campania_service_p2.py > campania_service.py
"""
from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.campana import (
    Campania, MetaCampania, CanalDifusionCampania,
    PartidaPresupuestoCampania, PlantillaCampania, PlantillaMeta,
    PlantillaPartida, PlantillaActividad, PlantillaTarea,
)


class CampaniaService:
    """Servicio de campañas: ciclo de vida, notificaciones, plantillas y clonación."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Helpers internos ───────────────────────────────────────────────────────────

    async def _get(self, campania_id: uuid.UUID) -> Campania:
        r = await self.session.execute(select(Campania).where(Campania.id == campania_id))
        return r.scalar_one()

    async def _cfg(self, clave: str, default: str = "") -> str:
        from app.modules.configuracion.models.configuracion import Configuracion
        r = await self.session.execute(select(Configuracion).where(Configuracion.clave == clave))
        row = r.scalars().first()
        return (row.valor if row and row.valor else default) or default

    # ── CRUD básico ───────────────────────────────────────────────────────────────────

    async def crear(self, *, nombre: str, tipo_campania_id: uuid.UUID, estado_id: uuid.UUID, **kwargs) -> Campania:
        campania = Campania(nombre=nombre, tipo_campania_id=tipo_campania_id, estado_id=estado_id, **kwargs)
        self.session.add(campania)
        await self.session.commit()
        return await self._get(campania.id)

    async def actualizar(self, campania_id: uuid.UUID, campos: dict) -> Campania:
        campania = await self._get(campania_id)
        for k, v in campos.items():
            if v is not None:
                setattr(campania, k, v)
        await self.session.commit()
        return await self._get(campania_id)

    async def transicionar_estado(self, campania_id, estado_id, notas=None) -> Campania:
        campania = await self._get(campania_id)
        campania.estado_id = estado_id
        if notas:
            campania.notas_aprobacion = notas
        await self.session.commit()
        return await self._get(campania_id)

    async def aprobar(self, campania_id, estado_id, aprobado_por_id=None, notas=None) -> Campania:
        campania = await self._get(campania_id)
        campania.estado_id = estado_id
        if aprobado_por_id:
            campania.aprobado_por_id = aprobado_por_id
            campania.fecha_aprobacion = date.today()
        if notas is not None:
            campania.notas_aprobacion = notas
        await self.session.commit()
        return await self._get(campania_id)

    # ── Metas, canales, partidas ──────────────────────────────────────────────────────

    async def guardar_metas(self, campania_id, metas: list) -> Campania:
        await self.session.execute(sa_delete(MetaCampania).where(MetaCampania.campania_id == campania_id))
        for m in metas:
            self.session.add(MetaCampania(campania_id=campania_id, **m))
        await self.session.commit()
        return await self._get(campania_id)

    async def guardar_canales(self, campania_id, canal_ids: list) -> Campania:
        await self.session.execute(sa_delete(CanalDifusionCampania).where(CanalDifusionCampania.campania_id == campania_id))
        for canal_id in canal_ids:
            self.session.add(CanalDifusionCampania(campania_id=campania_id, canal_id=canal_id))
        await self.session.commit()
        return await self._get(campania_id)

    async def guardar_partidas(self, campania_id, partidas: list) -> Campania:
        await self.session.execute(sa_delete(PartidaPresupuestoCampania).where(PartidaPresupuestoCampania.campania_id == campania_id))
        for p in partidas:
            self.session.add(PartidaPresupuestoCampania(campania_id=campania_id, **p))
        await self.session.commit()
        return await self._get(campania_id)

    # ── Cierre ────────────────────────────────────────────────────────────────────────

    async def cerrar(
        self, campania_id, estado_id, presupuesto_ejecutado: Decimal,
        resultados_metas: list, resultados_partidas: list, valoracion=None,
    ) -> Campania:
        """Cierra la campaña registrando valores reales de metas y partidas."""
        campania = await self._get(campania_id)
        campania.presupuesto_ejecutado = presupuesto_ejecutado
        campania.estado_id = estado_id
        if valoracion is not None:
            campania.valoracion = valoracion
        for r in resultados_metas:
            meta = (await self.session.execute(
                select(MetaCampania).where(MetaCampania.id == r["meta_id"])
            )).scalar_one()
            meta.valor_real = r["valor_real"]
        for r in resultados_partidas:
            partida = (await self.session.execute(
                select(PartidaPresupuestoCampania).where(PartidaPresupuestoCampania.id == r["partida_id"])
            )).scalar_one()
            partida.importe_real = r["importe_real"]
        await self.session.commit()
        return await self._get(campania_id)

    # ── Notificaciones ────────────────────────────────────────────────────────────────

    @staticmethod
    def renderizar_plantilla(asunto: str, cuerpo_html: str, **variables) -> tuple:
        """Sustituye {{ variable }} y procesa {% if %}...{% endif %} / {% for %}...{% endfor %}."""
        import re
        def _render(texto: str) -> str:
            def repl_if(m):
                key = m.group(1).strip()
                val = variables.get(key)
                return m.group(2) if val and (not isinstance(val, (list, str)) or val) else ""
            texto = re.sub(r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}', repl_if, texto, flags=re.DOTALL)
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
            texto = re.sub(r'\{%\s*for\s+req\s+in\s+requisitos_recursos\s*%\}(.*?)\{%\s*endfor\s*%\}',
                           repl_for, texto, flags=re.DOTALL)
            for key, val in variables.items():
                if not isinstance(val, list):
                    texto = texto.replace(f"{{{{ {key} }}}}", str(val) if val else "")
            return texto
        return _render(asunto), _render(cuerpo_html)

    async def previsualizar_notificacion(self, campania_id, plantilla_codigo=None) -> dict:
        """Renderiza la plantilla con datos reales SIN enviar. Devuelve dict con asunto/cuerpo/total."""
        from app.modules.core.comunicacion.plantilla_email import PlantillaEmail
        from app.modules.actividades.models.grupo import RequisitoRecurso, GrupoIniciativa
        from app.modules.membresia.models.contacto import Contacto

        campania = await self._get(campania_id)
        codigo = plantilla_codigo or "CAMP_APROBACION"
        plantilla = (await self.session.execute(
            select(PlantillaEmail).where(PlantillaEmail.codigo == codigo, PlantillaEmail.activo == True)
        )).scalar_one_or_none()
        if plantilla is None:
            raise ValueError(f"Plantilla '{codigo}' no encontrada o desactivada.")

        nombre_org = await self._cfg("org.nombre", "La organización")
        url_base = (await self._cfg("org.web", "")).rstrip("/")
        url_campanias = f"{url_base}/campanias" if url_base else "/campanias"

        gi_rows = (await self.session.execute(
            select(GrupoIniciativa).where(GrupoIniciativa.campania_id == campania_id)
        )).scalars().all()
        grupo_ids = {gi.grupo_id for gi in gi_rows}
        requisitos = []
        if grupo_ids:
            req_rows = (await self.session.execute(
                select(RequisitoRecurso).where(RequisitoRecurso.grupo_id.in_(grupo_ids))
            )).scalars().all()
            requisitos = [{"habilidad": str(r.especialidad_id),
                           "nivel": str(r.nivel_id) if r.nivel_id else "—",
                           "horas": str(r.horas_necesarias)} for r in req_rows]

        total_destinatarios = 0
        if campania.agrupacion_id:
            total_destinatarios = len((await self.session.execute(
                select(Contacto).where(
                    Contacto.agrupacion_id == campania.agrupacion_id,
                    Contacto.email.isnot(None), Contacto.eliminado == False,
                )
            )).scalars().all())

        asunto, cuerpo_html = self.renderizar_plantilla(
            plantilla.asunto, plantilla.cuerpo_html,
            nombre_miembro="[nombre destinatario]",
            nombre_campania=campania.nombre, lema=campania.lema or "",
            objetivo_principal=campania.objetivo_principal or "",
            presupuesto_estimado=str(campania.presupuesto_estimado or ""),
            requisitos_recursos=requisitos, url_campanias=url_campanias, nombre_organizacion=nombre_org,
        )
        return {"asunto": asunto, "cuerpo_html": cuerpo_html, "total_destinatarios": total_destinatarios}

    async def enviar_notificacion(self, campania_id, asunto: str, cuerpo_html: str) -> dict:
        """Envía el correo a los miembros activos. Marca notificacion_enviada=True al finalizar."""
        from app.core.email_service import EmailService, _load_smtp_config
        from app.modules.membresia.models.contacto import Contacto

        campania = await self._get(campania_id)
        if campania.notificacion_enviada:
            raise ValueError("Esta campaña ya fue notificada a la membresía.")
        if not campania.agrupacion_id:
            campania.notificacion_enviada = True
            await self.session.commit()
            return {"enviados": 0, "fallidos": 0, "sin_email": 0, "total": 0, "simulado": True,
                    "mensaje": "La campaña no tiene agrupación asignada — sin destinatarios."}

        miembros = (await self.session.execute(
            select(Contacto).where(Contacto.agrupacion_id == campania.agrupacion_id, Contacto.eliminado == False)
        )).scalars().all()
        smtp_cfg = await _load_smtp_config(self.session)
        if not smtp_cfg.configured:
            con_email = sum(1 for m in miembros if m.email)
            campania.notificacion_enviada = True
            await self.session.commit()
            faltantes = ", ".join(smtp_cfg.campos_faltantes) if smtp_cfg.campos_faltantes else "parámetros incompletos"
            return {"enviados": con_email, "fallidos": 0, "sin_email": len(miembros) - con_email,
                    "total": len(miembros), "simulado": True,
                    "mensaje": f"Envío simulado: SMTP no configurado ({faltantes}). Se habrían notificado {con_email} miembros."}

        email_svc = EmailService(self.session)
        enviados = fallidos = sin_email = 0
        for m in miembros:
            if not m.email:
                sin_email += 1
                continue
            nombre_dest = f"{m.nombre} {m.apellido1}".strip()
            try:
                await email_svc.enviar(destinatario=m.email, asunto=asunto,
                                       cuerpo_html=cuerpo_html.replace("[nombre destinatario]", nombre_dest))
                enviados += 1
            except Exception:
                fallidos += 1
        campania.notificacion_enviada = True
        await self.session.commit()
        return {"enviados": enviados, "fallidos": fallidos, "sin_email": sin_email,
                "total": len(miembros), "simulado": False, "mensaje": None}

    async def aplicar_plantilla(
        self, campania_id: uuid.UUID, plantilla_id: uuid.UUID,
    ) -> "Campania":
        """Clona metas, partidas, actividades y tareas de una plantilla a la campaña."""
        from app.modules.actividades.models.actividad import Actividad, TipoActividad
        from app.modules.actividades.models.tarea import Tarea
        from app.modules.configuracion.models.estados import EstadoAccion, EstadoTarea
        from sqlalchemy import select
        from datetime import timedelta

        plantilla = (await self.session.execute(
            select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id)
        )).scalar_one()
        campania = await self._get(campania_id)

        default_tipo = (await self.session.execute(
            select(TipoActividad).order_by(TipoActividad.nombre).limit(1)
        )).scalar_one_or_none()
        default_ea = (await self.session.execute(
            select(EstadoAccion).order_by(EstadoAccion.orden.asc().nulls_last()).limit(1)
        )).scalar_one_or_none()
        default_et = (await self.session.execute(
            select(EstadoTarea).order_by(EstadoTarea.orden.asc().nulls_last()).limit(1)
        )).scalar_one_or_none()

        for pm in plantilla.metas:
            self.session.add(MetaCampania(
                campania_id=campania_id, tipo_meta_id=pm.tipo_meta_id,
                valor_planificado=pm.valor_sugerido, notas=pm.notas, orden=pm.orden,
            ))
        for pp in plantilla.partidas:
            self.session.add(PartidaPresupuestoCampania(
                campania_id=campania_id, concepto=pp.concepto,
                importe_estimado=pp.importe_estimado, tipo_partida=pp.tipo_partida, orden=pp.orden,
            ))
        for pa in plantilla.actividades:
            act = Actividad(
                nombre=pa.nombre, descripcion=pa.descripcion,
                tipo_actividad_id=pa.tipo_actividad_id or (default_tipo.id if default_tipo else None),
                estado_id=default_ea.id if default_ea else None, campania_id=campania_id,
            )
            if campania.fecha_inicio_plan and pa.duracion_dias is not None:
                act.fecha_inicio = campania.fecha_inicio_plan + timedelta(days=pa.duracion_dias)
            self.session.add(act)
            await self.session.flush()
            for pt in pa.tareas:
                self.session.add(Tarea(
                    titulo=pt.titulo, descripcion=pt.descripcion,
                    horas_estimadas=pt.horas_estimadas, orden=pt.orden,
                    actividad_id=act.id, estado_id=default_et.id if default_et else None,
                ))
        await self.session.commit()
        return await self._get(campania_id)

    async def crear_plantilla(self, tipo_campania_id, nombre, descripcion=None, activo=True):
        from sqlalchemy import select
        p = PlantillaCampania(tipo_campania_id=tipo_campania_id, nombre=nombre,
                               descripcion=descripcion, activo=activo)
        self.session.add(p)
        await self.session.commit()
        return (await self.session.execute(select(PlantillaCampania).where(PlantillaCampania.id == p.id))).scalar_one()

    async def actualizar_plantilla(self, plantilla_id, campos: dict):
        from sqlalchemy import select
        p = (await self.session.execute(select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id))).scalar_one()
        for k, v in campos.items():
            if v is not None:
                setattr(p, k, v)
        await self.session.commit()
        return (await self.session.execute(select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id))).scalar_one()

    async def guardar_metas_plantilla(self, plantilla_id, metas: list):
        from sqlalchemy import select
        await self.session.execute(sa_delete(PlantillaMeta).where(PlantillaMeta.plantilla_id == plantilla_id))
        for m in metas:
            self.session.add(PlantillaMeta(plantilla_id=plantilla_id, **m))
        await self.session.commit()
        return (await self.session.execute(select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id))).scalar_one()

    async def guardar_partidas_plantilla(self, plantilla_id, partidas: list):
        from sqlalchemy import select
        await self.session.execute(sa_delete(PlantillaPartida).where(PlantillaPartida.plantilla_id == plantilla_id))
        for p in partidas:
            self.session.add(PlantillaPartida(plantilla_id=plantilla_id, **p))
        await self.session.commit()
        return (await self.session.execute(select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id))).scalar_one()

    async def crear_plantilla_desde_campania(
        self, campania_id, nombre, descripcion=None,
    ):
        """Fabrica una PLANTILLA a partir de una campaña existente (inverso de aplicar_plantilla).

        La plantilla es un molde reutilizable del MISMO tipo de campaña. Copia:
          - metas (valor_planificado → valor_sugerido),
          - partidas presupuestarias CON su importe_estimado (presupuesto orientativo),
          - actividades y sus tareas CON horas_estimadas.
        NO copia datos concretos de la instancia: fechas reales, estado, responsable,
        asistencias, documentos ni valores ejecutados. La `duracion_dias` de cada
        actividad se deriva como offset (días desde el inicio planificado de la campaña).
        """
        from app.modules.actividades.models.actividad import Actividad
        from app.modules.actividades.models.tarea import Tarea
        from sqlalchemy import select

        origen = (await self.session.execute(
            select(Campania).where(Campania.id == campania_id)
        )).scalar_one()

        plantilla = PlantillaCampania(
            tipo_campania_id=origen.tipo_campania_id,
            nombre=nombre, descripcion=descripcion, activo=True,
        )
        self.session.add(plantilla)
        await self.session.flush()

        for m in origen.metas:
            self.session.add(PlantillaMeta(
                plantilla_id=plantilla.id, tipo_meta_id=m.tipo_meta_id,
                valor_sugerido=m.valor_planificado, notas=getattr(m, "notas", None),
                orden=getattr(m, "orden", 0),
            ))
        for p in origen.partidas_presupuesto:
            self.session.add(PlantillaPartida(
                plantilla_id=plantilla.id, concepto=p.concepto,
                importe_estimado=p.importe_estimado, tipo_partida=p.tipo_partida, orden=p.orden,
            ))
        inicio = origen.fecha_inicio_plan
        for act in (await self.session.execute(
            select(Actividad).where(Actividad.campania_id == origen.id)
        )).scalars().all():
            duracion_dias = None
            if inicio and act.fecha_inicio:
                duracion_dias = (act.fecha_inicio - inicio).days
            pa = PlantillaActividad(
                plantilla_id=plantilla.id, nombre=act.nombre, descripcion=act.descripcion,
                tipo_actividad_id=act.tipo_actividad_id, duracion_dias=duracion_dias,
                orden=getattr(act, "orden", 0),
            )
            self.session.add(pa)
            await self.session.flush()
            for t in (await self.session.execute(
                select(Tarea).where(Tarea.actividad_id == act.id)
            )).scalars().all():
                self.session.add(PlantillaTarea(
                    actividad_id=pa.id, titulo=t.titulo, descripcion=t.descripcion,
                    horas_estimadas=t.horas_estimadas, orden=t.orden,
                    habilidad_id=getattr(t, "habilidad_id", None),
                    nivel_habilidad_id=getattr(t, "nivel_habilidad_id", None),
                ))

        await self.session.commit()
        return (await self.session.execute(
            select(PlantillaCampania).where(PlantillaCampania.id == plantilla.id)
        )).scalar_one()

    async def clonar(
        self, campania_id, nombre, offset_dias=0,
        incluir_metas=True, incluir_partidas=True, incluir_canales=True,
        incluir_actividades=True, incluir_subcampanias=False, padre_id=None,
    ):
        """Clona una campaña con todas sus entidades. Soporta recursión para subcampañas."""
        from app.modules.actividades.models.actividad import Actividad
        from app.modules.actividades.models.tarea import Tarea
        from app.modules.configuracion.models.estados import EstadoAccion, EstadoTarea, EstadoCampania
        from sqlalchemy import select
        from datetime import timedelta

        origen = (await self.session.execute(select(Campania).where(Campania.id == campania_id))).scalar_one()
        estado_inicial = (await self.session.execute(
            select(EstadoCampania).order_by(EstadoCampania.orden.asc().nulls_last()).limit(1)
        )).scalar_one_or_none()

        nueva = Campania(
            nombre=nombre, tipo_campania_id=origen.tipo_campania_id,
            estado_id=estado_inicial.id if estado_inicial else origen.estado_id,
            lema=origen.lema, descripcion_corta=origen.descripcion_corta,
            descripcion_larga=origen.descripcion_larga, url_externa=origen.url_externa,
            foto_url=origen.foto_url, objetivo_principal=origen.objetivo_principal,
            responsable_id=origen.responsable_id, agrupacion_id=origen.agrupacion_id,
            es_recurrente=origen.es_recurrente, periodicidad=origen.periodicidad,
            padre_id=padre_id,
            fecha_inicio_plan=(origen.fecha_inicio_plan + timedelta(days=offset_dias) if origen.fecha_inicio_plan else None),
            fecha_fin_plan=(origen.fecha_fin_plan + timedelta(days=offset_dias) if origen.fecha_fin_plan else None),
        )
        self.session.add(nueva)
        await self.session.flush()

        if incluir_metas:
            for m in origen.metas:
                self.session.add(MetaCampania(campania_id=nueva.id, tipo_meta_id=m.tipo_meta_id,
                                               unidad=m.unidad, valor_planificado=m.valor_planificado))
        if incluir_canales:
            for c in origen.canales:
                self.session.add(CanalDifusionCampania(campania_id=nueva.id, canal_id=c.canal_id, notas=c.notas))
        if incluir_partidas:
            for p in origen.partidas_presupuesto:
                self.session.add(PartidaPresupuestoCampania(campania_id=nueva.id, concepto=p.concepto,
                    importe_estimado=p.importe_estimado, tipo_partida=p.tipo_partida, orden=p.orden))
        if incluir_actividades:
            default_ea = (await self.session.execute(select(EstadoAccion).order_by(EstadoAccion.orden.asc().nulls_last()).limit(1))).scalar_one_or_none()
            default_et = (await self.session.execute(select(EstadoTarea).order_by(EstadoTarea.orden.asc().nulls_last()).limit(1))).scalar_one_or_none()
            for act in (await self.session.execute(select(Actividad).where(Actividad.campania_id == origen.id))).scalars().all():
                nueva_act = Actividad(
                    nombre=act.nombre, descripcion=act.descripcion, tipo_actividad_id=act.tipo_actividad_id,
                    estado_id=default_ea.id if default_ea else act.estado_id, campania_id=nueva.id,
                    grupo_id=act.grupo_id, responsable_id=act.responsable_id,
                    lugar=act.lugar, aforo=act.aforo, es_online=act.es_online, url_online=act.url_online,
                    presupuesto_estimado=act.presupuesto_estimado,
                    fecha_inicio=(act.fecha_inicio + timedelta(days=offset_dias) if act.fecha_inicio else None),
                    fecha_fin=(act.fecha_fin + timedelta(days=offset_dias) if act.fecha_fin else None),
                )
                self.session.add(nueva_act)
                await self.session.flush()
                for t in (await self.session.execute(select(Tarea).where(Tarea.actividad_id == act.id))).scalars().all():
                    self.session.add(Tarea(titulo=t.titulo, descripcion=t.descripcion,
                        horas_estimadas=t.horas_estimadas, orden=t.orden, actividad_id=nueva_act.id,
                        estado_id=default_et.id if default_et else t.estado_id))
        if incluir_subcampanias:
            for hija in (await self.session.execute(select(Campania).where(Campania.padre_id == origen.id))).scalars().all():
                await self.clonar(hija.id, f"{nombre} — {hija.nombre}",
                    offset_dias=offset_dias, incluir_metas=incluir_metas,
                    incluir_partidas=incluir_partidas, incluir_canales=incluir_canales,
                    incluir_actividades=incluir_actividades, incluir_subcampanias=True, padre_id=nueva.id)

        await self.session.commit()
        await self.session.refresh(nueva)
        return nueva

    CAMPOS_PROPAGABLES = frozenset({
        "tipo_campania_id", "responsable_id", "agrupacion_id",
        "objetivo_principal", "periodicidad", "es_recurrente",
    })

    async def propagar_a_subcampanias(self, campania_id, campos: list):
        from sqlalchemy import select
        campos_validos = [c for c in campos if c in self.CAMPOS_PROPAGABLES]
        if not campos_validos:
            return []
        padre = (await self.session.execute(select(Campania).where(Campania.id == campania_id))).scalar_one()
        valores = {c: getattr(padre, c) for c in campos_validos}
        procesadas = []
        cola = [campania_id]
        while cola:
            pid = cola.pop(0)
            for h in (await self.session.execute(select(Campania).where(Campania.padre_id == pid))).scalars().all():
                for campo, valor in valores.items():
                    setattr(h, campo, valor)
                procesadas.append(h.id)
                cola.append(h.id)
        await self.session.commit()
        if not procesadas:
            return []
        return list((await self.session.execute(select(Campania).where(Campania.id.in_(procesadas)))).scalars().all())
