"""Resolución de destinatarios para la comunicación dirigida por flujos de trabajo.

El corazón del módulo. Un flujo de trabajo no conoce *qué personas concretas*
deben recibir un aviso, solo conoce *un criterio*: «el tesorero de esta
agrupación», «todos los que tengan el rol de secretaría», «este usuario». Este
servicio traduce ese criterio (una `EspecificacionAudiencia`) a una lista
deduplicada de `Destinatario` (usuario + email + nombre legible).

Estrategia de resolución por rol/cargo (robusta y general)
----------------------------------------------------------
Para una audiencia de tipo ROL, se UNEN dos fuentes y se deduplica por usuario:

  1. Nombramiento orgánico vigente — la vista de solo lectura
     `v_nombramientos_vigentes` (modelo `NombramientoVigente`), derivada de
     `historial_nombramientos` con estado ACTIVO y sin fecha de fin. Traduce
     cargo → rol mediante `CargoRol`. Es la fuente coherente y autosanada de
     «quién ocupa el puesto ahora mismo».

  2. Asignación directa de rol — `UsuarioRol`, que es además la definición que
     usa la `PermissionMatrix`. Cubre lo que el nombramiento no ve: usuarios
     técnicos sin miembro asociado, asignaciones manuales puntuales y roles que
     no derivan de ningún cargo.

La unión a nivel de usuario final (no de criterio) garantiza que un mismo
destinatario nunca reciba el aviso dos veces aunque le llegue por ambas vías, y
que el sistema tolere desajustes entre nombramiento y asignación.

Ámbito territorial
-------------------
Una asignación/nombramiento de ámbito GLOBAL (`agrupacion_id IS NULL`) recibe
siempre. Una acotada a una agrupación recibe solo si coincide con la agrupación
objetivo de la especificación. Si la especificación no fija agrupación, no se
filtra por ámbito (recibe todo el que tenga el rol/cargo en cualquier ámbito).
"""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass
from typing import Iterable, Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.acceso.models.usuario import Usuario, UsuarioRol
from app.modules.acceso.models.cargo import CargoRol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion
from app.modules.acceso.models.funcionalidad import RolFuncionalidad, FuncionalidadTransaccion
from app.modules.membresia.models.contacto import Contacto
from app.modules.membresia.models.nombramiento_vigente import NombramientoVigente


class TipoAudiencia(str, enum.Enum):
    """Cómo se especifica a quién va dirigido un aviso."""
    ROL = "ROL"            # Todos los que ostentan un rol (por nombramiento o asignación)
    CARGO = "CARGO"        # Los que ocupan un cargo orgánico vigente
    PERMISO = "PERMISO"    # Todos los que pueden ejecutar una transacción (RBAC efectivo)
    USUARIO = "USUARIO"    # Un usuario concreto por id
    MIEMBRO = "MIEMBRO"    # El usuario asociado a un miembro concreto


@dataclass(frozen=True)
class EspecificacionAudiencia:
    """Criterio de audiencia que un flujo de trabajo entrega al resolver.

    Solo el campo correspondiente al `tipo` es obligatorio:
      - ROL      → rol_id   (+ agrupacion_id opcional para acotar el ámbito)
      - CARGO    → cargo_id (+ agrupacion_id opcional para acotar el ámbito)
      - USUARIO  → usuario_id
      - MIEMBRO  → miembro_id
    """
    tipo: TipoAudiencia
    rol_id: Optional[uuid.UUID] = None
    cargo_id: Optional[uuid.UUID] = None
    usuario_id: Optional[uuid.UUID] = None
    miembro_id: Optional[uuid.UUID] = None
    transaccion_codigo: Optional[str] = None
    agrupacion_id: Optional[uuid.UUID] = None

    # Constructores de conveniencia ----------------------------------------

    @classmethod
    def por_rol(cls, rol_id: uuid.UUID, agrupacion_id: Optional[uuid.UUID] = None) -> "EspecificacionAudiencia":
        return cls(tipo=TipoAudiencia.ROL, rol_id=rol_id, agrupacion_id=agrupacion_id)

    @classmethod
    def por_cargo(cls, cargo_id: uuid.UUID, agrupacion_id: Optional[uuid.UUID] = None) -> "EspecificacionAudiencia":
        return cls(tipo=TipoAudiencia.CARGO, cargo_id=cargo_id, agrupacion_id=agrupacion_id)

    @classmethod
    def por_permiso(cls, transaccion_codigo: str, agrupacion_id: Optional[uuid.UUID] = None) -> "EspecificacionAudiencia":
        return cls(tipo=TipoAudiencia.PERMISO, transaccion_codigo=transaccion_codigo, agrupacion_id=agrupacion_id)

    @classmethod
    def por_usuario(cls, usuario_id: uuid.UUID) -> "EspecificacionAudiencia":
        return cls(tipo=TipoAudiencia.USUARIO, usuario_id=usuario_id)

    @classmethod
    def por_miembro(cls, miembro_id: uuid.UUID) -> "EspecificacionAudiencia":
        return cls(tipo=TipoAudiencia.MIEMBRO, miembro_id=miembro_id)


@dataclass(frozen=True)
class Destinatario:
    """Un destinatario resuelto, listo para notificar."""
    usuario_id: uuid.UUID
    email: str
    nombre: str
    miembro_id: Optional[uuid.UUID] = None


class DestinatarioResolver:
    """Traduce especificaciones de audiencia a destinatarios concretos.

    Instanciar por request con la sesión de BD activa.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    async def resolver(
        self,
        especificaciones: Iterable[EspecificacionAudiencia],
    ) -> list[Destinatario]:
        """Resuelve una o varias especificaciones y devuelve destinatarios únicos.

        La deduplicación es por `usuario_id`: si la misma persona aparece por
        varias especificaciones o por varias vías, se incluye una sola vez.
        """
        ids: set[uuid.UUID] = set()
        for spec in especificaciones:
            ids |= await self._resolver_ids(spec)
        if not ids:
            return []
        return await self._cargar_destinatarios(ids)

    async def resolver_una(self, spec: EspecificacionAudiencia) -> list[Destinatario]:
        """Atajo para una sola especificación."""
        return await self.resolver([spec])

    # ------------------------------------------------------------------
    # Resolución de ids de usuario por especificación
    # ------------------------------------------------------------------

    async def _resolver_ids(self, spec: EspecificacionAudiencia) -> set[uuid.UUID]:
        if spec.tipo == TipoAudiencia.USUARIO:
            return {spec.usuario_id} if spec.usuario_id else set()

        if spec.tipo == TipoAudiencia.MIEMBRO:
            return await self._ids_por_miembros({spec.miembro_id}) if spec.miembro_id else set()

        if spec.tipo == TipoAudiencia.CARGO:
            return await self._ids_por_cargo(spec.cargo_id, spec.agrupacion_id) if spec.cargo_id else set()

        if spec.tipo == TipoAudiencia.PERMISO:
            return await self._ids_por_permiso(spec.transaccion_codigo, spec.agrupacion_id) if spec.transaccion_codigo else set()

        if spec.tipo == TipoAudiencia.ROL:
            if not spec.rol_id:
                return set()
            # Unión de las dos fuentes (nombramiento vigente + asignación directa)
            por_nombramiento = await self._ids_por_rol_via_nombramiento(spec.rol_id, spec.agrupacion_id)
            por_asignacion = await self._ids_por_rol_via_usuariorol(spec.rol_id, spec.agrupacion_id)
            return por_nombramiento | por_asignacion

        return set()

    # ------------------------------------------------------------------
    # Vías de resolución concretas
    # ------------------------------------------------------------------

    async def _ids_por_cargo(
        self,
        cargo_id: uuid.UUID,
        agrupacion_id: Optional[uuid.UUID],
    ) -> set[uuid.UUID]:
        """Ocupantes vigentes de un cargo orgánico (vía v_nombramientos_vigentes)."""
        stmt = select(NombramientoVigente.miembro_id).where(
            NombramientoVigente.cargo_id == cargo_id
        )
        stmt = self._aplicar_ambito(stmt, NombramientoVigente.agrupacion_id, agrupacion_id)
        result = await self._session.execute(stmt)
        miembro_ids = {row[0] for row in result.all() if row[0] is not None}
        return await self._ids_por_miembros(miembro_ids)

    async def _ids_por_permiso(
        self,
        transaccion_codigo: str,
        agrupacion_id: Optional[uuid.UUID],
    ) -> set[uuid.UUID]:
        """Usuarios que pueden ejecutar una transacción (permiso efectivo RBAC).

        Cubre los DOS caminos por los que un rol obtiene un permiso:
          - directo: RolTransaccion → Transaccion
          - vía funcionalidad: RolFuncionalidad → FuncionalidadTransaccion → Transaccion
        Se obtienen los rol_id que conceden el permiso y se resuelven sus
        portadores reutilizando la misma unión que para audiencia por rol
        (nombramiento vigente ∪ asignación directa), respetando el ámbito.
        """
        stmt_directo = (
            select(RolTransaccion.rol_id)
            .join(Transaccion, Transaccion.id == RolTransaccion.transaccion_id)
            .where(
                Transaccion.codigo == transaccion_codigo,
                RolTransaccion.eliminado == False,  # noqa: E712
                Transaccion.eliminado == False,     # noqa: E712
            )
        )
        stmt_func = (
            select(RolFuncionalidad.rol_id)
            .join(
                FuncionalidadTransaccion,
                FuncionalidadTransaccion.funcionalidad_id == RolFuncionalidad.funcionalidad_id,
            )
            .join(Transaccion, Transaccion.id == FuncionalidadTransaccion.transaccion_id)
            .where(
                Transaccion.codigo == transaccion_codigo,
                RolFuncionalidad.eliminado == False,          # noqa: E712
                FuncionalidadTransaccion.eliminado == False,  # noqa: E712
                Transaccion.eliminado == False,               # noqa: E712
            )
        )
        rol_ids: set[uuid.UUID] = set()
        for stmt in (stmt_directo, stmt_func):
            result = await self._session.execute(stmt)
            rol_ids |= {row[0] for row in result.all() if row[0] is not None}

        if not rol_ids:
            return set()

        ids: set[uuid.UUID] = set()
        for rid in rol_ids:
            ids |= await self._ids_por_rol_via_nombramiento(rid, agrupacion_id)
            ids |= await self._ids_por_rol_via_usuariorol(rid, agrupacion_id)
        return ids

    async def _ids_por_rol_via_nombramiento(
        self,
        rol_id: uuid.UUID,
        agrupacion_id: Optional[uuid.UUID],
    ) -> set[uuid.UUID]:
        """Portadores del rol por cargo vigente: vista → CargoRol → miembro → usuario."""
        stmt = (
            select(NombramientoVigente.miembro_id)
            .join(CargoRol, CargoRol.cargo_id == NombramientoVigente.cargo_id)
            .where(
                CargoRol.rol_id == rol_id,
                CargoRol.eliminado == False,  # noqa: E712
            )
        )
        stmt = self._aplicar_ambito(stmt, NombramientoVigente.agrupacion_id, agrupacion_id)
        result = await self._session.execute(stmt)
        miembro_ids = {row[0] for row in result.all() if row[0] is not None}
        return await self._ids_por_miembros(miembro_ids)

    async def _ids_por_rol_via_usuariorol(
        self,
        rol_id: uuid.UUID,
        agrupacion_id: Optional[uuid.UUID],
    ) -> set[uuid.UUID]:
        """Portadores del rol por asignación directa (UsuarioRol activa)."""
        stmt = (
            select(UsuarioRol.usuario_id)
            .join(Usuario, Usuario.id == UsuarioRol.usuario_id)
            .where(
                UsuarioRol.rol_id == rol_id,
                UsuarioRol.activo == True,       # noqa: E712
                UsuarioRol.eliminado == False,   # noqa: E712
                Usuario.activo == True,          # noqa: E712
                Usuario.eliminado == False,      # noqa: E712
            )
        )
        stmt = self._aplicar_ambito(stmt, UsuarioRol.agrupacion_id, agrupacion_id)
        result = await self._session.execute(stmt)
        return {row[0] for row in result.all() if row[0] is not None}

    async def _ids_por_miembros(self, miembro_ids: set[uuid.UUID]) -> set[uuid.UUID]:
        """Usuarios activos asociados a un conjunto de miembros."""
        if not miembro_ids:
            return set()
        result = await self._session.execute(
            select(Usuario.id).where(
                Usuario.contacto_id.in_(miembro_ids),
                Usuario.activo == True,        # noqa: E712
                Usuario.eliminado == False,    # noqa: E712
            )
        )
        return {row[0] for row in result.all()}

    # ------------------------------------------------------------------
    # Carga final de destinatarios (un solo query)
    # ------------------------------------------------------------------

    async def _cargar_destinatarios(self, usuario_ids: set[uuid.UUID]) -> list[Destinatario]:
        """Carga usuarios + miembro asociado y construye los Destinatario.

        El email de envío es `Usuario.email` (NOT NULL, login). Si el usuario
        tiene miembro con email de contacto, se conserva para trazabilidad pero
        el canal de envío sigue siendo el del usuario.
        """
        result = await self._session.execute(
            select(Usuario).where(
                Usuario.id.in_(usuario_ids),
                Usuario.activo == True,        # noqa: E712
                Usuario.eliminado == False,    # noqa: E712
            )
        )
        usuarios = result.scalars().all()

        destinatarios: list[Destinatario] = []
        for u in usuarios:
            contacto: Optional[Contacto] = u.contacto
            nombre = contacto.nombre_completo if contacto else u.email
            destinatarios.append(
                Destinatario(
                    usuario_id=u.id,
                    email=u.email,
                    nombre=nombre,
                    miembro_id=u.contacto_id,
                )
            )
        # Orden estable por nombre para salidas reproducibles
        destinatarios.sort(key=lambda d: (d.nombre or "").lower())
        return destinatarios

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    @staticmethod
    def _aplicar_ambito(stmt, columna_agrupacion, agrupacion_id: Optional[uuid.UUID]):
        """Aplica la regla de ámbito territorial.

        - Sin agrupación objetivo → no se filtra (cualquier ámbito).
        - Con agrupación objetivo → ámbito global (NULL) o coincidente.
        """
        if agrupacion_id is None:
            return stmt
        return stmt.where(
            or_(
                columna_agrupacion.is_(None),
                columna_agrupacion == agrupacion_id,
            )
        )
