"""Ámbito territorial de un usuario según sus roles (para scoping de datos).

Regla (ver docs/modulo_membresia.md y docs/modulo_actividades.md §9):
- El ámbito NO depende de dónde milita la persona (`Miembro.agrupacion_id`), sino del
  ámbito de sus cargos (`UsuarioRol.agrupacion_id`).
- Un rol con `agrupacion_id` NULL **o** igual a una unidad raíz (sin padre) ⇒ ámbito GLOBAL.
- Un rol territorial (adscrito a una unidad por debajo de la raíz) ⇒ esa unidad + su subárbol.
- Sin despliegue territorial (una sola unidad raíz) ⇒ siempre GLOBAL, sin filtro.

`agrupaciones_en_ambito(session, usuario_id)`:
  → None  ⇒ GLOBAL (no aplicar filtro: el usuario alcanza a todos los socios).
  → set[UUID] ⇒ conjunto de agrupaciones (unidad(es) del rol + descendientes) al que se limita.

Pensado para Fase 2: enchufar como filtro `Miembro.agrupacion_id IN (...)` en las queries y
como guard en las mutaciones. En Fase 1 no se invoca todavía.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.acceso.models.usuario import UsuarioRol
from app.modules.acceso.models.rol import Rol
from app.modules.core.geografico.direccion import UnidadOrganizativa

# Roles cuyo ámbito NO es territorial (se resuelven por otra vía, p. ej. por campaña).
# No deben entrar en el cálculo del ámbito territorial.
_ROLES_NO_TERRITORIALES = ("COORDINADOR_CAMPANA",)


async def _ids_raiz(session: AsyncSession) -> set[uuid.UUID]:
    """IDs de las unidades raíz (sin padre)."""
    r = await session.execute(
        select(UnidadOrganizativa.id).where(UnidadOrganizativa.agrupacion_padre_id.is_(None))
    )
    return {row[0] for row in r.all()}


async def _subarbol(session: AsyncSession, raices: set[uuid.UUID]) -> set[uuid.UUID]:
    """Una o varias agrupaciones + todos sus descendientes (CTE recursivo)."""
    if not raices:
        return set()
    sql = text(
        """
        WITH RECURSIVE sub AS (
            SELECT id FROM unidades_organizativas WHERE id = ANY(:raices)
            UNION ALL
            SELECT u.id FROM unidades_organizativas u
            JOIN sub ON u.agrupacion_padre_id = sub.id
        )
        SELECT id FROM sub
        """
    ).bindparams(raices=list(raices))
    r = await session.execute(sql)
    return {row[0] for row in r.all()}


async def agrupaciones_en_ambito(
    session: AsyncSession, usuario_id: uuid.UUID,
) -> set[uuid.UUID] | None:
    """Devuelve el conjunto de agrupaciones que el usuario gobierna, o None si es GLOBAL."""
    r = await session.execute(
        select(UsuarioRol.agrupacion_id)
        .join(Rol, Rol.id == UsuarioRol.rol_id)
        .where(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.activo.is_(True),
            Rol.codigo.notin_(_ROLES_NO_TERRITORIALES),
        )
    )
    ambitos = [row[0] for row in r.all()]
    if not ambitos:
        return set()  # sin roles territoriales → sin ámbito territorial (no ve nada por esta vía)

    raices = await _ids_raiz(session)
    # Rol global: agrupacion_id NULL o adscrito a una unidad raíz.
    for a in ambitos:
        if a is None or a in raices:
            return None  # GLOBAL → no aplicar filtro

    territoriales = {a for a in ambitos if a is not None}
    return await _subarbol(session, territoriales)


async def assert_miembro_en_ambito(
    session: AsyncSession, usuario_id: uuid.UUID, miembro_id: uuid.UUID,
) -> None:
    """Lanza PermissionError si el socio está fuera del ámbito territorial del usuario.

    Guard para mutaciones de gestión por delegación: el filtro de la UI no se puede saltar
    por API. Ámbito global ⇒ no restringe.
    """
    ambito = await agrupaciones_en_ambito(session, usuario_id)
    if ambito is None:
        return  # global
    from app.modules.membresia.models.miembro import Miembro
    m_agr = await session.scalar(
        select(Miembro.agrupacion_id).where(Miembro.id == miembro_id)
    )
    if m_agr is None or m_agr not in ambito:
        raise PermissionError("El socio está fuera de tu ámbito territorial.")
