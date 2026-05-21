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
        from app.modules.membresia.models.miembro import Miembro

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
                select(Miembro).where(
                    Miembro.agrupacion_id == campania.agrupacion_id,
                    Miembro.email.isnot(None), Miembro.eliminado == False,
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
        from app.modules.membresia.models.miembro import Miembro

        campania = await self._get(campania_id)
        if campania.notificacion_enviada:
            raise ValueError("Esta campaña ya fue notificada a la membresía.")
        if not campania.agrupacion_id:
            campania.notificacion_enviada = True
            await self.session.commit()
            return {"enviados": 0, "fallidos": 0, "sin_email": 0, "total": 0, "simulado": True,
                    "mensaje": "La campaña no tiene agrupación asignada — sin destinatarios."}

        miembros = (await self.session.execute(
            select(Miembro).where(Miembro.agrupacion_id == campania.agrupacion_id, Miembro.eliminado == False)
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

    # Continúa en campania_service_p2.py
