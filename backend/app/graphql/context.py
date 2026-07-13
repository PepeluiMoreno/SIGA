"""Contexto GraphQL con sesión de base de datos, usuario autenticado y permisos."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import AsyncGenerator, FrozenSet, Optional

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from ..core.database import async_session
from ..core.security import extract_bearer_token, load_user_from_token
from ..modules.acceso.models.usuario import Usuario, UsuarioRol


# Centinela: distingue «ámbito aún no calculado» de «ámbito calculado = None (global)».
# Sin él, un usuario global recalcularía el ámbito en cada comprobación.
_AMBITO_NO_CARGADO = object()


@dataclass
class Context(BaseContext):
    """Contexto GraphQL: sesión de BD + usuario autenticado + permisos en memoria."""
    session: AsyncSession
    user: Optional[Usuario] = None
    _role_ids_cache: Optional[FrozenSet[str]] = field(default=None, repr=False, compare=False)
    _ambito_cache: object = field(default=_AMBITO_NO_CARGADO, repr=False, compare=False)

    # ------------------------------------------------------------------
    # Identidad
    # ------------------------------------------------------------------

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None

    @property
    def user_id(self) -> Optional[str]:
        return str(self.user.id) if self.user else None

    # ------------------------------------------------------------------
    # Roles efectivos (un solo query por request, luego cached)
    # ------------------------------------------------------------------

    async def get_role_ids(self) -> FrozenSet[str]:
        """Carga los role_ids activos del usuario desde DB (una sola vez por request)."""
        if self._role_ids_cache is not None:
            return self._role_ids_cache
        if self.user is None:
            self._role_ids_cache = frozenset()
            return self._role_ids_cache
        result = await self.session.execute(
            select(UsuarioRol.rol_id).where(
                UsuarioRol.usuario_id == self.user.id,
                UsuarioRol.activo == True,
                UsuarioRol.eliminado == False,
            )
        )
        self._role_ids_cache = frozenset(str(row[0]) for row in result.all())
        return self._role_ids_cache

    # ------------------------------------------------------------------
    # Ámbito territorial (una sola vez por request, luego cached)
    # ------------------------------------------------------------------

    async def get_ambito(self) -> Optional[set]:
        """Unidades sobre las que el usuario puede actuar. `None` = ámbito GLOBAL.

        Un `UsuarioRol` lleva el `agrupacion_id` del mandato que lo originó: el
        territorio donde esa persona ejerce el cargo. El ámbito del usuario es la unión
        de los **subárboles** de esas agrupaciones (mandar en una unidad es mandar
        también en las que cuelgan de ella).

        **La regla del ámbito global**: hace falta un rol activo que sea de sistema *y*
        que **no** tenga agrupación. Las dos condiciones, no una:

        - El `agrupacion_id` del mandato **siempre** ancla. Un Gestor de miembros con
          mandato en Sevilla manda en Sevilla, aunque su rol esté marcado `sistema`.
        - `Rol.sistema` por sí solo no basta, porque no significa «manda en todo» sino
          «rol de catálogo, no borrable». De hecho el sembrador lo pone a `True` en
          bloque (`seed_init_accesos.py`), ignorando el `es_territorial` que las propias
          definiciones declaran: Gestor de miembros, Interventor/a y Planificador están
          marcados como territoriales y aun así salen con `sistema=True`. Concederles
          ámbito global por ese flag sería reabrir el agujero justo en los roles
          operativos que más necesitan estar acotados.

        Así, lo único que queda global es el mandato sin territorio de un rol de
        sistema — el superadmin. Todo lo demás se ancla donde ejerce.

        Devuelve:
          - `None`      → global, sin restricción.
          - `set()`     → no alcanza ninguna unidad.
          - `{ids...}`  → el subárbol de sus agrupaciones.
        """
        if self._ambito_cache is not _AMBITO_NO_CARGADO:
            return self._ambito_cache
        if self.user is None:
            self._ambito_cache = set()
            return self._ambito_cache

        from ..modules.acceso.models.rol import Rol
        from ..modules.acceso.services.ambito_territorial import _subarbol

        filas = (await self.session.execute(
            select(UsuarioRol.agrupacion_id, Rol.sistema)
            .join(Rol, Rol.id == UsuarioRol.rol_id)
            .where(
                UsuarioRol.usuario_id == self.user.id,
                UsuarioRol.activo == True,      # noqa: E712
                UsuarioRol.eliminado == False,  # noqa: E712
            )
        )).all()

        if any(sistema and agr is None for (agr, sistema) in filas):
            self._ambito_cache = None
            return None

        raices = {agr for (agr, _s) in filas if agr is not None}
        if not raices:
            # Ni territorio ni mandato global: no alcanza nada.
            self._ambito_cache = set()
            return self._ambito_cache

        self._ambito_cache = await _subarbol(self.session, raices)
        return self._ambito_cache

    # ------------------------------------------------------------------
    # Autorización (usando PermissionMatrix en memoria — sin DB adicional)
    # ------------------------------------------------------------------

    async def check_permission(self, transaction_id: str) -> bool:
        """True si el usuario posee el permiso indicado."""
        from ..modules.acceso.services.matrix import matrix_cache
        if not self.is_authenticated or not matrix_cache.is_ready():
            return False
        role_ids = await self.get_role_ids()
        return matrix_cache.can(role_ids, transaction_id)

    async def require_permission(self, transaction_id: str) -> None:
        """Lanza PermissionError si el usuario no tiene el permiso."""
        if not await self.check_permission(transaction_id):
            raise PermissionError(f"Permiso denegado: {transaction_id}")

    async def check_ambito(self, transaction_id: str, objetivo, kwargs: dict):
        """¿Puede el usuario ejercer esta transacción **sobre este objetivo**?

        Devuelve `(permitido, motivo)`. Aplica el ámbito declarado de la transacción:

          - GLOBAL      → no mira territorio (configuración, catálogos).
          - TERRITORIAL → la agrupación del objetivo debe caer en el subárbol del
                          usuario. Aquí es donde se cierra el agujero: «puedes editar
                          socios» pasa a ser «puedes editar A ESTE socio».
          - PROPIO      → solo sobre uno mismo (autoservicio).

        Falla CERRADO: si el objetivo no se puede resolver, se deniega. Un permiso no
        se concede por no saber sobre qué se ejerce.
        """
        from ..modules.acceso.models.funcionalidad import AmbitoTransaccion
        from ..modules.acceso.services.registry import ModuleCatalog

        ambito_tx = ModuleCatalog.get_ambito_de_transaccion(transaction_id)
        if ambito_tx == AmbitoTransaccion.GLOBAL:
            return True, ""

        # El id de la entidad sobre la que se actúa, tomado de los argumentos de la
        # llamada (puede venir anidado en un input: `data.id`).
        valor = kwargs.get(objetivo.arg)
        if valor is not None and objetivo.ruta:
            for parte in objetivo.ruta.split("."):
                valor = getattr(valor, parte, None)
                if valor is None:
                    break
        if valor is None:
            return False, (
                f"Permiso denegado: {transaction_id} no indica sobre qué actúa "
                f"(falta «{objetivo.arg}»)."
            )

        if ambito_tx == AmbitoTransaccion.PROPIO:
            # Autoservicio: el objetivo tiene que ser uno mismo. Aquí `resolver` NO
            # devuelve una agrupación sino el contacto sobre el que se actúa: cuando el
            # argumento ya ES el contacto se usa la identidad (`Objetivo.contacto`), y
            # cuando llega por un salto (p. ej. `solicitud_id` → su miembro) lo resuelve
            # `Objetivo.miembro_de_traslado`. Por eso se pasa siempre por el resolver: si
            # se comparase el argumento crudo, un id de solicitud jamás igualaría a un id
            # de contacto y el autoservicio quedaría permanentemente denegado.
            propio = self.user.contacto_id if self.user else None
            if propio is None or objetivo.resolver_propio is None:
                return False, f"Permiso denegado: {transaction_id} solo se ejerce sobre uno mismo."
            destinatario = await objetivo.resolver_propio(self.session, valor)
            if destinatario is not None and str(destinatario) == str(propio):
                return True, ""
            return False, f"Permiso denegado: {transaction_id} solo se ejerce sobre uno mismo."

        # TERRITORIAL
        ambito = await self.get_ambito()
        if ambito is None:
            return True, ""      # rol de sistema: manda en toda la organización

        agrupacion = await objetivo.resolver(self.session, valor)
        if agrupacion is None:
            # Entidad sin territorio (o inexistente): solo la alcanza un ámbito global.
            return False, (
                f"Permiso denegado: {transaction_id} — el objetivo no pertenece a "
                "ninguna agrupación de tu ámbito."
            )
        if agrupacion in ambito:
            return True, ""
        return False, (
            f"Permiso denegado: {transaction_id} — el objetivo está fuera de tu "
            "ámbito territorial."
        )


async def get_context(request: Request) -> AsyncGenerator[Context, None]:
    """Construye el contexto: abre sesión de BD y resuelve el usuario actual."""
    async with async_session() as session:
        token = extract_bearer_token(request.headers.get("authorization"))
        user = await load_user_from_token(session, token) if token else None

        ctx = Context(session=session, user=user)
        try:
            yield ctx
            await session.commit()
        except Exception:
            await session.rollback()
            raise
