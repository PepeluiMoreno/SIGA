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
from typing import Optional

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


async def miembros_de_campanias_coordinadas(
    session: AsyncSession, usuario_id: uuid.UUID,
) -> set[uuid.UUID]:
    """IDs de socios participantes en las campañas que coordina el usuario.

    El coordinador de campaña es el `responsable_id` de la campaña; su ámbito son los socios
    que participan en actividades de esas campañas. (Vía complementaria a la territorial.)
    """
    from app.modules.acceso.models.usuario import Usuario
    from app.modules.actividades.models.campana import Campania
    from app.modules.actividades.models.actividad import Actividad, AsistenciaActividad
    from app.modules.membresia.models.participacion import Participacion

    contacto_id = await session.scalar(select(Usuario.contacto_id).where(Usuario.id == usuario_id))
    if not contacto_id:
        return set()
    camp_ids = (await session.execute(
        select(Campania.id).where(Campania.responsable_id == contacto_id)
    )).scalars().all()
    if not camp_ids:
        return set()
    # Contactos que asistieron a actividades de esas campañas (vía Participacion)
    rows = await session.execute(
        select(Participacion.contacto_id)
        .join(AsistenciaActividad, AsistenciaActividad.participacion_id == Participacion.id)
        .join(Actividad, Actividad.id == AsistenciaActividad.actividad_id)
        .where(Actividad.campania_id.in_(camp_ids), Participacion.contacto_id.isnot(None))
    )
    return {r[0] for r in rows.all()}


async def ensure_rol_coordinador_campania(
    session: AsyncSession, miembro_id: Optional[uuid.UUID],
) -> None:
    """Concede el rol COORDINADOR_CAMPANA al usuario del socio responsable de una campaña.

    Idempotente. Se llama al fijar el responsable de una campaña. No se revoca al cambiar el
    responsable: el ámbito se deriva dinámicamente de las campañas que coordina, así que si deja
    de coordinar campañas su ámbito queda vacío (no ve nada) aunque conserve el rol.
    """
    if not miembro_id:
        return
    from app.modules.acceso.models.usuario import Usuario
    from app.modules.acceso.models.rol import Rol

    usuario_id = await session.scalar(select(Usuario.id).where(Usuario.contacto_id == miembro_id))
    if not usuario_id:
        return  # el socio no tiene cuenta de acceso
    rol_id = await session.scalar(select(Rol.id).where(Rol.codigo == "COORDINADOR_CAMPANA"))
    if not rol_id:
        return
    existe = await session.scalar(
        select(UsuarioRol.id).where(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.rol_id == rol_id,
            UsuarioRol.activo.is_(True),
        )
    )
    if existe:
        return
    session.add(UsuarioRol(usuario_id=usuario_id, rol_id=rol_id, agrupacion_id=None, activo=True))
    await session.commit()


async def assert_unidad_en_ambito(
    session: AsyncSession, usuario_id: uuid.UUID, unidad_id: uuid.UUID | None,
) -> None:
    """Lanza PermissionError si la unidad está fuera del ámbito territorial del usuario.

    Global ⇒ no restringe. Guard para gestionar por delegación (editar la unidad,
    registrar cargos en ella, trasladar socios a ella, editar su subestructura).
    `unidad_id` None ⇒ se exige ámbito global (operación sobre la matriz / plantilla).
    """
    ambito = await agrupaciones_en_ambito(session, usuario_id)
    if ambito is None:
        return  # global
    if unidad_id is not None and unidad_id in ambito:
        return
    raise PermissionError("La unidad está fuera de tu ámbito territorial.")


async def assert_miembro_en_ambito(
    session: AsyncSession, usuario_id: uuid.UUID, miembro_id: uuid.UUID,
) -> None:
    """Lanza PermissionError si el socio está fuera del ámbito del usuario.

    Ámbito = territorial (agrupación del rol + subárbol) ∪ campañas coordinadas. Global ⇒ no
    restringe. Guard para mutaciones de gestión por delegación: no se salta por API.
    """
    ambito = await agrupaciones_en_ambito(session, usuario_id)
    if ambito is None:
        return  # global
    from app.modules.membresia.models.contacto import Contacto
    m_agr = await session.scalar(
        select(Contacto.agrupacion_id).where(Contacto.id == miembro_id)
    )
    if m_agr is not None and m_agr in ambito:
        return
    if miembro_id in await miembros_de_campanias_coordinadas(session, usuario_id):
        return
    raise PermissionError("El socio está fuera de tu ámbito.")
