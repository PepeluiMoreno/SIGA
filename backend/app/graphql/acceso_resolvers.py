"""Resolvers custom para gestión de roles, transacciones y asignaciones.

Reemplaza las mutaciones strawchemy para los modelos de acceso que tienen
campos FK UUID, porque strawchemy en modo create_input no los incluye en el
INSERT automáticamente. Además agrupa las operaciones en una sola transacción.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

import strawberry
from sqlalchemy import select

from sqlalchemy import delete as sa_delete

from app.modules.acceso.models.rol import Rol, TipoRol
from app.modules.acceso.models.funcionalidad import RolFuncionalidad
from app.modules.acceso.models.rol_transaccion import RolTransaccion
from app.modules.acceso.models.usuario import UsuarioRol
from app.graphql.permissions import RequireTransaction


# ---------------------------------------------------------------------------
# Inputs de mutación
# ---------------------------------------------------------------------------

@strawberry.input
class CrearRolInput:
    codigo: str
    nombre: str
    tipo: str
    nivel: int
    descripcion: Optional[str] = None
    activo: bool = True
    es_territorial: bool = False
    nivel_territorial: Optional[str] = None
    funcionalidad_ids: List[uuid.UUID] = strawberry.field(default_factory=list)
    transaccion_ids: List[uuid.UUID] = strawberry.field(default_factory=list)


@strawberry.input
class ActualizarRolInput:
    id: uuid.UUID
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    nivel: Optional[int] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    es_territorial: Optional[bool] = None
    nivel_territorial: Optional[str] = None
    funcionalidad_ids: Optional[List[uuid.UUID]] = None
    transaccion_ids: Optional[List[uuid.UUID]] = None


# ---------------------------------------------------------------------------
# Mixin de mutaciones
# ---------------------------------------------------------------------------

@strawberry.type
class AccesoMutation:

    # ── Roles ────────────────────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ACCESO_ROL_CREAR")])
    async def crear_rol(
        self,
        info: strawberry.Info,
        data: CrearRolInput,
    ) -> uuid.UUID:
        session = info.context.session

        res = await session.execute(
            select(Rol).where(Rol.codigo == data.codigo, Rol.eliminado == False)
        )
        if res.scalar_one_or_none() is not None:
            raise ValueError(f"Ya existe un rol con el código «{data.codigo}»")

        rol = Rol(
            codigo=data.codigo,
            nombre=data.nombre,
            tipo=TipoRol(data.tipo),
            nivel=data.nivel,
            descripcion=data.descripcion,
            activo=data.activo,
            es_territorial=data.es_territorial,
            nivel_territorial=data.nivel_territorial,
        )
        session.add(rol)
        await session.flush()

        for fid in data.funcionalidad_ids:
            session.add(RolFuncionalidad(rol_id=rol.id, funcionalidad_id=fid))

        for tid in data.transaccion_ids:
            session.add(RolTransaccion(rol_id=rol.id, transaccion_id=tid))

        await session.commit()
        return rol.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ACCESO_ROL_EDITAR")])
    async def actualizar_rol(
        self,
        info: strawberry.Info,
        data: ActualizarRolInput,
    ) -> uuid.UUID:
        session = info.context.session

        res = await session.execute(
            select(Rol).where(Rol.id == data.id, Rol.eliminado == False)
        )
        rol = res.scalar_one_or_none()
        if rol is None:
            raise ValueError("Rol no encontrado")
        if rol.sistema:
            raise ValueError("Los roles del sistema no se pueden modificar")

        if data.codigo is not None and data.codigo != rol.codigo:
            dup = await session.execute(
                select(Rol).where(
                    Rol.codigo == data.codigo,
                    Rol.eliminado == False,
                    Rol.id != data.id,
                )
            )
            if dup.scalar_one_or_none() is not None:
                raise ValueError(f"Ya existe un rol con el código «{data.codigo}»")
            rol.codigo = data.codigo

        if data.nombre is not None:
            rol.nombre = data.nombre
        if data.tipo is not None:
            rol.tipo = TipoRol(data.tipo)
        if data.nivel is not None:
            rol.nivel = data.nivel
        if data.descripcion is not None:
            rol.descripcion = data.descripcion
        if data.activo is not None:
            rol.activo = data.activo
        if data.es_territorial is not None:
            rol.es_territorial = data.es_territorial
        if data.nivel_territorial is not None:
            rol.nivel_territorial = data.nivel_territorial or None
        # Si tipo ya no es TERRITORIAL, limpiar campos territoriales
        if data.tipo is not None and TipoRol(data.tipo) != TipoRol.TERRITORIAL:
            rol.es_territorial = False
            rol.nivel_territorial = None

        if data.funcionalidad_ids is not None:
            current_res = await session.execute(
                select(RolFuncionalidad).where(RolFuncionalidad.rol_id == rol.id)
            )
            current_rfs = current_res.scalars().all()
            current_ids = {rf.funcionalidad_id for rf in current_rfs}
            desired_ids = set(data.funcionalidad_ids)

            for rf in current_rfs:
                if rf.funcionalidad_id not in desired_ids:
                    await session.delete(rf)
            for fid in desired_ids - current_ids:
                session.add(RolFuncionalidad(rol_id=rol.id, funcionalidad_id=fid))

        if data.transaccion_ids is not None:
            current_tx_res = await session.execute(
                select(RolTransaccion).where(RolTransaccion.rol_id == rol.id)
            )
            current_txs = current_tx_res.scalars().all()
            current_tx_ids = {rt.transaccion_id for rt in current_txs}
            desired_tx_ids = set(data.transaccion_ids)

            for rt in current_txs:
                if rt.transaccion_id not in desired_tx_ids:
                    await session.delete(rt)
            for tid in desired_tx_ids - current_tx_ids:
                session.add(RolTransaccion(rol_id=rol.id, transaccion_id=tid))

        await session.commit()
        return rol.id

    # ── Rol ↔ Transacción (usadas en PermisosRol) ───────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ACCESO_FUNC_ASIGNAR")])
    async def asignar_transaccion_rol(
        self,
        info: strawberry.Info,
        rol_id: uuid.UUID,
        transaccion_id: uuid.UUID,
    ) -> uuid.UUID:
        session = info.context.session
        existing = (await session.execute(
            select(RolTransaccion).where(
                RolTransaccion.rol_id == rol_id,
                RolTransaccion.transaccion_id == transaccion_id,
            )
        )).scalar_one_or_none()
        if existing:
            return existing.id
        rt = RolTransaccion(rol_id=rol_id, transaccion_id=transaccion_id, eliminado=False, fecha_creacion=datetime.utcnow())
        session.add(rt)
        await session.commit()
        return rt.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ACCESO_FUNC_REVOCAR")])
    async def revocar_transaccion_rol(
        self,
        info: strawberry.Info,
        rol_id: uuid.UUID,
        transaccion_id: uuid.UUID,
    ) -> bool:
        session = info.context.session
        res = await session.execute(
            select(RolTransaccion).where(
                RolTransaccion.rol_id == rol_id,
                RolTransaccion.transaccion_id == transaccion_id,
            )
        )
        rt = res.scalar_one_or_none()
        if rt:
            await session.delete(rt)
            await session.commit()
        return True

    # ── Usuario ↔ Rol ────────────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ACCESO_ROL_ASIGNAR")])
    async def asignar_rol_usuario(
        self,
        info: strawberry.Info,
        usuario_id: uuid.UUID,
        rol_id: uuid.UUID,
        agrupacion_id: Optional[uuid.UUID] = None,
    ) -> uuid.UUID:
        session = info.context.session
        existing = (await session.execute(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_id == rol_id,
            )
        )).scalar_one_or_none()
        if existing:
            return existing.id
        ur = UsuarioRol(
            usuario_id=usuario_id,
            rol_id=rol_id,
            agrupacion_id=agrupacion_id,
            eliminado=False,
            fecha_creacion=datetime.utcnow(),
        )
        session.add(ur)
        await session.commit()
        return ur.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ACCESO_ROL_ELIMINAR")])
    async def eliminar_rol(
        self,
        info: strawberry.Info,
        id: uuid.UUID,
    ) -> bool:
        """Elimina un rol, rechazando roles de sistema."""
        session = info.context.session
        res = await session.execute(select(Rol).where(Rol.id == id, Rol.eliminado == False))
        rol = res.scalar_one_or_none()
        if rol is None:
            raise ValueError("Rol no encontrado")
        if rol.sistema:
            raise ValueError(f"El rol «{rol.nombre}» es de sistema y no se puede eliminar")

        await session.execute(sa_delete(Rol).where(Rol.id == id))
        await session.commit()
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("ACCESO_ROL_REVOCAR")])
    async def revocar_rol_usuario(
        self,
        info: strawberry.Info,
        usuario_id: uuid.UUID,
        rol_id: uuid.UUID,
    ) -> bool:
        session = info.context.session
        res = await session.execute(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_id == rol_id,
            )
        )
        ur = res.scalar_one_or_none()
        if ur:
            await session.delete(ur)
            await session.commit()
        return True
