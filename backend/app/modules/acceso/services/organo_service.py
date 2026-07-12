"""Instanciación de órganos de gobierno en las agrupaciones.

La configuración de la gobernanza vive por NIVEL (`NivelOrgano` + `NivelOrganoCargo`):
«el nivel *Delegación* tiene una Junta Directiva compuesta por Presidencia,
Secretaría y Tesorería». Este servicio **materializa** esa configuración en una
agrupación concreta: crea sus `Organo` y su composición `OrganoCargo`.

Sin esto, la configuración es una promesa que nadie cumple: `organos` queda a 0
filas y una reunión no tiene a qué órgano apuntar.

La composición del nivel es el **punto de partida**: una vez instanciada, cada
agrupación puede ajustar la suya (añadir una vocalía, quitar un cargo) sin que eso
afecte a las demás.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.organo import NivelOrgano, Organo, OrganoCargo
from ...core.geografico.direccion import UnidadOrganizativa


class OrganoService:
    """Materializa la configuración de órganos de un nivel en las agrupaciones."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def instanciar_organos(
        self,
        agrupacion_id: uuid.UUID,
        *,
        fecha_constitucion: Optional[date] = None,
    ) -> List[Organo]:
        """Crea los órganos que el NIVEL de esta agrupación tiene configurados.

        Idempotente: omite los tipos de órgano que la agrupación ya tenga. Devuelve
        solo los órganos **creados** en esta llamada (lista vacía si ya estaban todos
        o si el nivel no configura ninguno).
        """
        agrupacion = (await self.session.execute(
            select(UnidadOrganizativa).where(UnidadOrganizativa.id == agrupacion_id)
        )).scalar_one_or_none()
        if agrupacion is None:
            raise ValueError("Agrupación no encontrada")
        if agrupacion.tipo_id is None:
            # Sin nivel no hay configuración de gobernanza que aplicar.
            return []

        # Configuración del nivel: qué órganos y con qué composición.
        niveles_organo = (await self.session.execute(
            select(NivelOrgano).where(
                NivelOrgano.nivel_id == agrupacion.tipo_id,
                NivelOrgano.activo == True,        # noqa: E712
                NivelOrgano.eliminado == False,    # noqa: E712
            )
        )).scalars().all()
        if not niveles_organo:
            return []

        # Tipos de órgano que la agrupación YA tiene (idempotencia).
        ya_tiene = {
            o.tipo_organo_id for o in (await self.session.execute(
                select(Organo).where(
                    Organo.agrupacion_id == agrupacion_id,
                    Organo.eliminado == False,     # noqa: E712
                )
            )).scalars().all()
        }

        creados: List[Organo] = []
        for no in niveles_organo:
            if no.tipo_organo_id in ya_tiene:
                continue

            organo = Organo(
                tipo_organo_id=no.tipo_organo_id,
                agrupacion_id=agrupacion_id,
                nombre=f"{no.tipo_organo.nombre} — {agrupacion.nombre}",
                fecha_constitucion=fecha_constitucion or date.today(),
                activo=True,
            )
            self.session.add(organo)
            await self.session.flush()   # necesitamos organo.id

            # Copiar la composición del nivel. Los órganos de composición PLENO
            # (la asamblea: su membresía es el pleno de socios) no llevan cargos.
            if no.tipo_organo.composicion.value == "CARGOS":
                for nc in no.composicion:
                    self.session.add(OrganoCargo(
                        organo_id=organo.id,
                        cargo_id=nc.cargo_id,
                        orden_protocolario=nc.orden_protocolario,
                    ))

            creados.append(organo)

        return creados
