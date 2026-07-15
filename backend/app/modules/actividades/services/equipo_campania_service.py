"""Equipo de una campaña y matching de voluntarios por habilidad.

Dos lecturas que hasta ahora no existían como query reutilizable (vivían embebidas en el
armado del correo de reclutamiento):

  - **equipo de una campaña**: sus grupos, con miembros, requisitos de recurso y cobertura
    de horas — para ver de un vistazo qué hace falta y qué está cubierto.
  - **matching por habilidad**: dado un requisito (habilidad + nivel), qué voluntarios del
    ámbito lo cumplen. Esto es "reclutar" de verdad: sugerir candidatos, no solo listar
    huecos.

Gap estructural que este servicio puentea: los requisitos y aportaciones referencian
`Contacto`, pero las habilidades cuelgan de `Voluntario` (la extensión del vínculo). El
matching recorre `Contacto → Vinculacion(VOLUNTARIO) → Voluntario → MiembroHabilidad`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.actividades.models.grupo import (
    GrupoTrabajo, RequisitoRecurso, MiembroGrupo,
)
from app.modules.membresia.models.habilidad import Habilidad, MiembroHabilidad
from app.modules.membresia.models.nivel_habilidad import NivelHabilidad
from app.modules.membresia.models.contacto import Contacto
from app.modules.membresia.models.vinculacion import Vinculacion, Voluntario
from app.modules.membresia.models.tipo_vinculacion import TipoVinculacion


@dataclass
class RequisitoInfo:
    id: uuid.UUID
    especialidad_id: Optional[uuid.UUID]
    especialidad_nombre: str
    nivel_id: Optional[uuid.UUID]
    nivel_nombre: str
    horas_necesarias: float
    horas_cubiertas: float
    horas_pendientes: float


@dataclass
class GrupoCampaniaInfo:
    id: uuid.UUID
    nombre: str
    num_miembros: int
    requisitos: list[RequisitoInfo] = field(default_factory=list)


@dataclass
class CandidatoInfo:
    contacto_id: uuid.UUID
    nombre: str
    nivel_nombre: str
    validado: bool


class EquipoCampaniaService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _nombres_habilidad(self) -> dict[uuid.UUID, str]:
        return {
            h.id: h.nombre
            for h in (await self.session.execute(select(Habilidad))).scalars()
        }

    async def _nombres_nivel(self) -> dict[uuid.UUID, str]:
        return {
            n.id: n.nombre
            for n in (await self.session.execute(select(NivelHabilidad))).scalars()
        }

    async def equipo(self, campania_id: uuid.UUID) -> list[GrupoCampaniaInfo]:
        """Grupos de la campaña con sus miembros, requisitos y cobertura de horas.

        Vínculo canónico: `GrupoTrabajo.campania_id` (con FK real; `GrupoIniciativa`
        quedó deprecada)."""
        grupos = (await self.session.execute(
            select(GrupoTrabajo).where(
                GrupoTrabajo.campania_id == campania_id,
                GrupoTrabajo.eliminado == False,  # noqa: E712
            )
        )).scalars().all()
        if not grupos:
            return []

        hab = await self._nombres_habilidad()
        niv = await self._nombres_nivel()
        out: list[GrupoCampaniaInfo] = []
        for g in grupos:
            num = (await self.session.execute(
                select(MiembroGrupo).where(
                    MiembroGrupo.grupo_id == g.id,
                    MiembroGrupo.activo == True,       # noqa: E712
                    MiembroGrupo.eliminado == False,   # noqa: E712
                )
            )).scalars().all()
            reqs = (await self.session.execute(
                select(RequisitoRecurso).where(
                    RequisitoRecurso.grupo_id == g.id,
                    RequisitoRecurso.eliminado == False,  # noqa: E712
                )
            )).scalars().all()
            out.append(GrupoCampaniaInfo(
                id=g.id, nombre=g.nombre, num_miembros=len(num),
                requisitos=[
                    RequisitoInfo(
                        id=r.id,
                        especialidad_id=r.especialidad_id,
                        especialidad_nombre=hab.get(r.especialidad_id, "—"),
                        nivel_id=r.nivel_id,
                        nivel_nombre=niv.get(r.nivel_id, "—"),
                        horas_necesarias=float(r.horas_necesarias or 0),
                        horas_cubiertas=float(r.horas_cubiertas or 0),
                        horas_pendientes=float(r.horas_pendientes or 0),
                    )
                    for r in reqs
                ],
            ))
        return out

    async def candidatos_para_requisito(
        self, requisito_id: uuid.UUID, ambito: Optional[set] = None,
    ) -> list[CandidatoInfo]:
        """Voluntarios que cumplen la habilidad del requisito, con nivel >= el pedido.

        `ambito`: si se pasa (subárbol territorial del usuario), filtra a candidatos de
        esas agrupaciones. `None` = sin filtro territorial (ámbito global). Recorre el
        salto Contacto→Voluntario→MiembroHabilidad que separa habilidades (del voluntario)
        de la composición del equipo (por contacto)."""
        req = (await self.session.execute(
            select(RequisitoRecurso).where(RequisitoRecurso.id == requisito_id)
        )).scalar_one_or_none()
        if req is None:
            raise ValueError("El requisito de recurso no existe.")

        # Nivel mínimo pedido (ordinal). Si el requisito no fija nivel, vale cualquiera.
        orden_min = 0
        if req.nivel_id is not None:
            nivel_req = (await self.session.execute(
                select(NivelHabilidad).where(NivelHabilidad.id == req.nivel_id)
            )).scalar_one_or_none()
            orden_min = nivel_req.orden if nivel_req else 0

        niveles = await self._nombres_nivel()
        ordenes = {
            n.id: n.orden
            for n in (await self.session.execute(select(NivelHabilidad))).scalars()
        }

        # Voluntarios con esa habilidad → su contacto y su nivel.
        filas = (await self.session.execute(
            select(Contacto, MiembroHabilidad)
            .join(Vinculacion, Vinculacion.contacto_id == Contacto.id)
            .join(TipoVinculacion, TipoVinculacion.id == Vinculacion.tipo_vinculacion_id)
            .join(Voluntario, Voluntario.vinculacion_id == Vinculacion.id)
            .join(MiembroHabilidad, MiembroHabilidad.voluntario_id == Voluntario.id)
            .where(
                MiembroHabilidad.habilidad_id == req.especialidad_id,
                TipoVinculacion.codigo == "VOLUNTARIO",
                Vinculacion.fecha_fin.is_(None),
                Vinculacion.eliminado == False,   # noqa: E712
                Contacto.eliminado == False,      # noqa: E712
                MiembroHabilidad.eliminado == False,  # noqa: E712
            )
        )).all()

        out: list[CandidatoInfo] = []
        vistos: set[uuid.UUID] = set()
        for contacto, mh in filas:
            # Nivel suficiente
            orden_cand = ordenes.get(mh.nivel_id, 0) if mh.nivel_id else 0
            if orden_cand < orden_min:
                continue
            # Ámbito territorial
            if ambito is not None and contacto.agrupacion_id not in ambito:
                continue
            if contacto.id in vistos:
                continue
            vistos.add(contacto.id)
            out.append(CandidatoInfo(
                contacto_id=contacto.id,
                nombre=(f"{contacto.nombre or ''} {contacto.apellido1 or ''}".strip()
                        or contacto.razon_social or "—"),
                nivel_nombre=niveles.get(mh.nivel_id, "—") if mh.nivel_id else "—",
                validado=mh.validado,
            ))
        return out
