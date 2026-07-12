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
from app.modules.acceso.models.organo import (
    TipoOrgano,
    NivelOrgano,
    NivelOrganoCargo,
    Organo,
    OrganoCargo,
)
from app.modules.core.geografico.direccion import UnidadOrganizativa
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


@strawberry.input
class CargoOrdenInput:
    """Un cargo dentro de la composición de un órgano, con su orden protocolario."""
    cargo_id: uuid.UUID
    orden_protocolario: int = 0


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
        hard: bool = False,
    ) -> bool:
        """Elimina un rol, rechazando roles de sistema.

        - `hard=False` (por defecto): **soft-delete** (a la papelera): marca
          `eliminado` y desactiva; recuperable.
        - `hard=True`: **borrado definitivo**. Solo se permite sobre un rol que
          ya está en la papelera: el borrado lógico precede siempre al físico.
          Limpia las asignaciones propias (usuarios, funcionalidades,
          transacciones) y borra la fila.
        """
        session = info.context.session
        res = await session.execute(select(Rol).where(Rol.id == id))
        rol = res.scalar_one_or_none()
        if rol is None:
            raise ValueError("Rol no encontrado")
        if rol.sistema:
            raise ValueError(f"El rol «{rol.nombre}» es de sistema y no se puede eliminar")

        if not hard:
            if rol.eliminado:
                raise ValueError(f"El rol «{rol.nombre}» ya está en la papelera")
            rol.soft_delete(getattr(info.context.user, "id", None))
            rol.activo = False
            await session.commit()
            return True

        # Hard-delete: exige que el rol ya esté en la papelera.
        if not rol.eliminado:
            raise ValueError(
                f"El rol «{rol.nombre}» debe enviarse a la papelera antes de "
                "borrarlo definitivamente"
            )

        await session.execute(sa_delete(UsuarioRol).where(UsuarioRol.rol_id == id))
        await session.execute(sa_delete(RolFuncionalidad).where(RolFuncionalidad.rol_id == id))
        await session.execute(sa_delete(RolTransaccion).where(RolTransaccion.rol_id == id))
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

    # ── Configuración: el modelo organizativo de cada NIVEL ──────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("CFG_CONFIGURACION_EDITAR")])
    async def establecer_composicion_nivel_organo(
        self,
        info: strawberry.Info,
        nivel_organo_id: uuid.UUID,
        cargos: List[CargoOrdenInput],
    ) -> bool:
        """Reemplaza la composición-plantilla del órgano de un nivel, de una vez.

        Borra las filas `niveles_organos_cargos` de ese `NivelOrgano` y las recrea
        con los cargos y el orden dados. El input autogenerado de strawchemy no
        incluye las FKs (`nivel_organo_id`/`cargo_id`), de ahí este resolver manual.
        """
        session = info.context.session
        await session.execute(
            sa_delete(NivelOrganoCargo).where(
                NivelOrganoCargo.nivel_organo_id == nivel_organo_id
            )
        )
        for c in cargos:
            session.add(NivelOrganoCargo(
                nivel_organo_id=nivel_organo_id,
                cargo_id=c.cargo_id,
                orden_protocolario=c.orden_protocolario,
            ))
        await session.commit()
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("CFG_CONFIGURACION_EDITAR")])
    async def establecer_organos_de_nivel(
        self,
        info: strawberry.Info,
        nivel_id: uuid.UUID,
        tipo_organo_ids: List[uuid.UUID],
    ) -> bool:
        """Fija qué órganos tiene un nivel territorial.

        Reemplaza el conjunto de `NivelOrgano` del nivel: borra los que ya no están
        y crea los nuevos. Los que se mantienen NO se tocan, para no perder su
        composición (`NivelOrganoCargo`).
        """
        session = info.context.session

        actuales = (await session.execute(
            select(NivelOrgano).where(NivelOrgano.nivel_id == nivel_id)
        )).scalars().all()

        deseados = set(tipo_organo_ids)
        existentes = {no.tipo_organo_id for no in actuales}

        for no in actuales:
            if no.tipo_organo_id not in deseados:
                await session.delete(no)   # cascade borra su composición

        for tid in deseados - existentes:
            session.add(NivelOrgano(nivel_id=nivel_id, tipo_organo_id=tid, activo=True))

        await session.commit()
        return True

    # ── Órganos de una agrupación ────────────────────────────────────────────
    @strawberry.mutation(permission_classes=[RequireTransaction("CFG_CONFIGURACION_EDITAR")])
    async def crear_organo_en_agrupacion(
        self,
        info: strawberry.Info,
        tipo_organo_id: uuid.UUID,
        agrupacion_id: uuid.UUID,
        nombre: Optional[str] = None,
        fecha_constitucion: Optional[str] = None,
    ) -> uuid.UUID:
        """Crea un órgano en una agrupación, copiando la composición-plantilla de su NIVEL.

        La plantilla vive en el nivel territorial de la agrupación (`NivelOrgano` /
        `NivelOrganoCargo`): es el punto de partida, y la composición real
        (`OrganoCargo`) queda copiada y ajustable por esa agrupación.
        Los tipos de composición PLENO (asamblea) no llevan cargos. Si el nivel no
        tiene ese órgano configurado, el órgano se crea sin composición.
        """
        from datetime import date as _date
        session = info.context.session

        tipo = (await session.execute(
            select(TipoOrgano).where(TipoOrgano.id == tipo_organo_id)
        )).scalar_one_or_none()
        if tipo is None:
            raise ValueError("Tipo de órgano no encontrado")

        agrupacion = (await session.execute(
            select(UnidadOrganizativa).where(UnidadOrganizativa.id == agrupacion_id)
        )).scalar_one_or_none()
        if agrupacion is None:
            raise ValueError("Agrupación no encontrada")

        organo = Organo(
            tipo_organo_id=tipo_organo_id,
            agrupacion_id=agrupacion_id,
            nombre=(nombre or tipo.nombre),
            fecha_constitucion=(
                _date.fromisoformat(fecha_constitucion) if fecha_constitucion else _date.today()
            ),
            activo=True,
        )
        session.add(organo)
        await session.flush()   # necesitamos organo.id

        # Copiar la plantilla del NIVEL de la agrupación (solo si se compone por CARGOS).
        # `UnidadOrganizativa.tipo_id` es su nivel organizativo.
        if tipo.composicion.value == "CARGOS" and agrupacion.tipo_id is not None:
            nivel_organo = (await session.execute(
                select(NivelOrgano).where(
                    NivelOrgano.nivel_id == agrupacion.tipo_id,
                    NivelOrgano.tipo_organo_id == tipo_organo_id,
                )
            )).scalars().first()
            if nivel_organo is not None:
                plantilla = (await session.execute(
                    select(NivelOrganoCargo).where(
                        NivelOrganoCargo.nivel_organo_id == nivel_organo.id
                    ).order_by(NivelOrganoCargo.orden_protocolario)
                )).scalars().all()
                for nc in plantilla:
                    session.add(OrganoCargo(
                        organo_id=organo.id,
                        cargo_id=nc.cargo_id,
                        orden_protocolario=nc.orden_protocolario,
                    ))

        await session.commit()
        return organo.id

    @strawberry.mutation(permission_classes=[RequireTransaction("CFG_CONFIGURACION_EDITAR")])
    async def establecer_composicion_de_organo(
        self,
        info: strawberry.Info,
        organo_id: uuid.UUID,
        cargos: List[CargoOrdenInput],
    ) -> bool:
        """Reemplaza la composición REAL de un órgano concreto (la de una agrupación)."""
        session = info.context.session
        await session.execute(
            sa_delete(OrganoCargo).where(OrganoCargo.organo_id == organo_id)
        )
        for c in cargos:
            session.add(OrganoCargo(
                organo_id=organo_id,
                cargo_id=c.cargo_id,
                orden_protocolario=c.orden_protocolario,
            ))
        await session.commit()
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("CFG_CONFIGURACION_EDITAR")])
    async def replicar_organos_en_agrupacion(
        self,
        info: strawberry.Info,
        agrupacion_origen_id: uuid.UUID,
        agrupacion_destino_id: uuid.UUID,
    ) -> int:
        """Replica los órganos (y su composición) de una agrupación en otra.

        Pensado para el modelo territorial DISTRIBUIDO: al crear una agrupación hija
        no se hereda nada en silencio; se pregunta al usuario y, si acepta, se llama
        aquí. Omite los tipos de órgano que la agrupación destino ya tenga.
        Devuelve cuántos órganos se crearon.
        """
        from datetime import date as _date
        session = info.context.session

        origen = (await session.execute(
            select(Organo).where(
                Organo.agrupacion_id == agrupacion_origen_id,
                Organo.eliminado == False,  # noqa: E712
            )
        )).scalars().all()

        ya_tiene = {
            o.tipo_organo_id for o in (await session.execute(
                select(Organo).where(
                    Organo.agrupacion_id == agrupacion_destino_id,
                    Organo.eliminado == False,  # noqa: E712
                )
            )).scalars().all()
        }

        creados = 0
        for o in origen:
            if o.tipo_organo_id in ya_tiene:
                continue
            nuevo = Organo(
                tipo_organo_id=o.tipo_organo_id,
                agrupacion_id=agrupacion_destino_id,
                nombre=o.nombre,
                fecha_constitucion=_date.today(),
                activo=True,
            )
            session.add(nuevo)
            await session.flush()

            comp = (await session.execute(
                select(OrganoCargo).where(OrganoCargo.organo_id == o.id)
            )).scalars().all()
            for oc in comp:
                session.add(OrganoCargo(
                    organo_id=nuevo.id,
                    cargo_id=oc.cargo_id,
                    orden_protocolario=oc.orden_protocolario,
                ))
            creados += 1

        await session.commit()
        return creados
