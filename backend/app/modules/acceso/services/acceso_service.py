"""Servicio orquestador del módulo de acceso.

Cubre el ciclo completo:
  - Creación de usuarios con credenciales
  - Constitución y gestión de juntas directivas
  - Asignación/revocación de cargos con propagación automática de roles
  - Emisión de eventos de dominio para invalidación de la PermissionMatrix

Nota sobre roles automáticos: al asignar un cargo, los UsuarioRol creados
se identifican por (usuario_id, rol_id, agrupacion_id). Al revocar, se eliminan
lógicamente SOLO si el usuario no tiene asignación manual posterior al mismo rol.
Si se necesita trazar el origen exacto, añadir `origen_cargo_junta_id` a UsuarioRol.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.security import hash_password
from ....core.events import event_bus, CargoAssigned, CargoRevoked, JuntaReconfigured
from ...membresia.models.junta import (
    JuntaDirectiva,
    CargoJunta,
    HistorialCargoJunta,
    TipoCargoRol,
)
from ...membresia.models.tipo_cargo import TipoCargo
from ..models.usuario import Usuario, UsuarioRol

logger = logging.getLogger(__name__)


class AccesoService:
    """Orquesta operaciones de acceso: usuarios, juntas y cargos."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Usuarios
    # ------------------------------------------------------------------

    async def crear_usuario(
        self,
        email: str,
        password: str,
        activo: bool = True,
    ) -> Usuario:
        """Crea un nuevo usuario del sistema con password hasheado.

        Raises:
            ValueError: si ya existe un usuario con ese email.
        """
        result = await self.session.execute(
            select(Usuario).where(Usuario.email == email)
        )
        if result.scalars().first():
            raise ValueError(f"Ya existe un usuario con email '{email}'")

        usuario = Usuario(
            email=email,
            password_hash=hash_password(password),
            activo=activo,
        )
        self.session.add(usuario)
        await self.session.flush()
        return usuario

    # ------------------------------------------------------------------
    # Juntas directivas
    # ------------------------------------------------------------------

    async def constituir_junta(
        self,
        agrupacion_id: UUID,
        nombre: str,
        fecha_constitucion: date,
        observaciones: Optional[str] = None,
    ) -> JuntaDirectiva:
        """Constituye una nueva junta directiva para una agrupación.

        Desactiva la junta activa anterior (si existe) y la nueva queda activa.
        Emite JuntaReconfigured para que la PermissionMatrix se reconstruya.
        """
        # Desactivar junta activa anterior
        await self.session.execute(
            update(JuntaDirectiva)
            .where(
                JuntaDirectiva.agrupacion_id == agrupacion_id,
                JuntaDirectiva.activa == True,
                JuntaDirectiva.eliminado == False,
            )
            .values(activa=False, fecha_disolucion=fecha_constitucion)
        )

        junta = JuntaDirectiva(
            agrupacion_id=agrupacion_id,
            nombre=nombre,
            fecha_constitucion=fecha_constitucion,
            activa=True,
            observaciones=observaciones,
        )
        self.session.add(junta)
        await self.session.flush()

        await event_bus.publish(JuntaReconfigured(agrupacion_id=str(agrupacion_id)))
        return junta

    async def obtener_junta_activa(self, agrupacion_id: UUID) -> Optional[JuntaDirectiva]:
        """Devuelve la junta directiva activa de una agrupación, o None."""
        result = await self.session.execute(
            select(JuntaDirectiva).where(
                JuntaDirectiva.agrupacion_id == agrupacion_id,
                JuntaDirectiva.activa == True,
                JuntaDirectiva.eliminado == False,
            )
        )
        return result.scalars().first()

    # ------------------------------------------------------------------
    # Cargos
    # ------------------------------------------------------------------

    async def asignar_cargo(
        self,
        junta_id: UUID,
        miembro_id: UUID,
        tipo_cargo_id: UUID,
        fecha_inicio: date,
        posicion: int = 0,
        usuario_id: Optional[UUID] = None,
    ) -> CargoJunta:
        """Asigna un cargo a un miembro en una junta directiva.

        - Crea CargoJunta con la posición indicada.
        - Registra en HistorialCargoJunta.
        - Si se proporciona usuario_id, crea UsuarioRol para cada rol
          definido en TipoCargoRol (roles automáticos del cargo).
        - Emite CargoAssigned → PermissionMatrix rebuild.

        Args:
            posicion: 0 para cargos únicos (PRESIDENTE, TESORERO…),
                      1/2/3 para vocalías adicionales.

        Raises:
            ValueError: si el cargo (junta_id, tipo_cargo_id, posicion) ya existe.
        """
        # Validar unicidad
        result = await self.session.execute(
            select(CargoJunta).where(
                CargoJunta.junta_id == junta_id,
                CargoJunta.tipo_cargo_id == tipo_cargo_id,
                CargoJunta.posicion == posicion,
                CargoJunta.eliminado == False,
            )
        )
        if result.scalars().first():
            raise ValueError(
                f"Ya existe un cargo para tipo_cargo_id={tipo_cargo_id} "
                f"posicion={posicion} en esta junta"
            )

        cargo = CargoJunta(
            junta_id=junta_id,
            miembro_id=miembro_id,
            tipo_cargo_id=tipo_cargo_id,
            posicion=posicion,
            fecha_inicio=fecha_inicio,
            activo=True,
        )
        self.session.add(cargo)
        await self.session.flush()

        # Historial
        historial = HistorialCargoJunta(
            junta_id=junta_id,
            tipo_cargo_id=tipo_cargo_id,
            miembro_id=miembro_id,
            posicion=posicion,
            fecha_inicio=fecha_inicio,
        )
        self.session.add(historial)

        # Roles automáticos
        agrupacion_id: Optional[UUID] = None
        if usuario_id:
            agrupacion_id = await self._get_agrupacion_junta(junta_id)
            await self._asignar_roles_automaticos(
                usuario_id=usuario_id,
                tipo_cargo_id=tipo_cargo_id,
                agrupacion_id=agrupacion_id,
            )

        await self.session.flush()

        tipo_cargo = await self._get_tipo_cargo(tipo_cargo_id)
        await event_bus.publish(
            CargoAssigned(
                usuario_id=str(usuario_id) if usuario_id else "",
                cargo_codigo=tipo_cargo.codigo if tipo_cargo else str(tipo_cargo_id),
                agrupacion_id=str(agrupacion_id) if agrupacion_id else None,
            )
        )

        return cargo

    async def revocar_cargo(
        self,
        cargo_junta_id: UUID,
        fecha_fin: date,
        motivo: Optional[str] = None,
        usuario_id: Optional[UUID] = None,
    ) -> CargoJunta:
        """Revoca un cargo activo en una junta.

        - Cierra CargoJunta (activo=False, fecha_fin).
        - Cierra la entrada en HistorialCargoJunta.
        - Si se proporciona usuario_id, desactiva los UsuarioRol automáticos
          derivados de este cargo.
        - Emite CargoRevoked → PermissionMatrix rebuild.

        Raises:
            ValueError: si el cargo no existe o ya está inactivo.
        """
        result = await self.session.execute(
            select(CargoJunta).where(
                CargoJunta.id == cargo_junta_id,
                CargoJunta.eliminado == False,
            )
        )
        cargo = result.scalars().first()
        if not cargo:
            raise ValueError(f"CargoJunta {cargo_junta_id} no encontrado")
        if not cargo.activo:
            raise ValueError(f"CargoJunta {cargo_junta_id} ya está inactivo")

        cargo.activo = False
        cargo.fecha_fin = fecha_fin
        self.session.add(cargo)

        # Cerrar entrada en historial
        await self._cerrar_historial_cargo(
            junta_id=cargo.junta_id,
            tipo_cargo_id=cargo.tipo_cargo_id,
            miembro_id=cargo.miembro_id,
            posicion=cargo.posicion,
            fecha_fin=fecha_fin,
            motivo=motivo,
        )

        # Revocar roles automáticos
        agrupacion_id: Optional[UUID] = None
        if usuario_id:
            agrupacion_id = await self._get_agrupacion_junta(cargo.junta_id)
            await self._revocar_roles_automaticos(
                usuario_id=usuario_id,
                tipo_cargo_id=cargo.tipo_cargo_id,
                agrupacion_id=agrupacion_id,
            )

        await self.session.flush()

        tipo_cargo = await self._get_tipo_cargo(cargo.tipo_cargo_id)
        await event_bus.publish(
            CargoRevoked(
                usuario_id=str(usuario_id) if usuario_id else "",
                cargo_codigo=tipo_cargo.codigo if tipo_cargo else str(cargo.tipo_cargo_id),
                agrupacion_id=str(agrupacion_id) if agrupacion_id else None,
            )
        )

        return cargo

    async def siguiente_posicion_vocal(
        self, junta_id: UUID, tipo_cargo_id: UUID
    ) -> int:
        """Calcula la siguiente posición disponible para un cargo multiple (ej: VOCAL).

        Devuelve 1 si no hay vocales, 2 si hay uno, etc.
        """
        result = await self.session.execute(
            select(CargoJunta.posicion).where(
                CargoJunta.junta_id == junta_id,
                CargoJunta.tipo_cargo_id == tipo_cargo_id,
                CargoJunta.activo == True,
                CargoJunta.eliminado == False,
            )
        )
        posiciones = [row[0] for row in result.all()]
        if not posiciones:
            return 1
        return max(posiciones) + 1

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    async def _get_tipo_cargo(self, tipo_cargo_id: UUID) -> Optional[TipoCargo]:
        result = await self.session.execute(
            select(TipoCargo).where(TipoCargo.id == tipo_cargo_id)
        )
        return result.scalars().first()

    async def _get_agrupacion_junta(self, junta_id: UUID) -> Optional[UUID]:
        result = await self.session.execute(
            select(JuntaDirectiva.agrupacion_id).where(JuntaDirectiva.id == junta_id)
        )
        row = result.first()
        return row[0] if row else None

    async def _asignar_roles_automaticos(
        self,
        usuario_id: UUID,
        tipo_cargo_id: UUID,
        agrupacion_id: Optional[UUID],
    ) -> None:
        """Crea UsuarioRol para cada rol en TipoCargoRol del cargo."""
        result = await self.session.execute(
            select(TipoCargoRol).where(TipoCargoRol.tipo_cargo_id == tipo_cargo_id)
        )
        tipo_cargo_roles = result.scalars().all()

        for tcr in tipo_cargo_roles:
            # Evitar duplicados
            exists = await self.session.execute(
                select(UsuarioRol).where(
                    and_(
                        UsuarioRol.usuario_id == usuario_id,
                        UsuarioRol.rol_id == tcr.rol_id,
                        UsuarioRol.agrupacion_id == agrupacion_id,
                        UsuarioRol.eliminado == False,
                    )
                )
            )
            if exists.scalars().first():
                continue

            usuario_rol = UsuarioRol(
                usuario_id=usuario_id,
                rol_id=tcr.rol_id,
                agrupacion_id=agrupacion_id,
                activo=True,
            )
            self.session.add(usuario_rol)
            logger.debug(
                "Rol automático asignado: usuario=%s rol=%s agrupacion=%s",
                usuario_id, tcr.rol_id, agrupacion_id,
            )

    async def _revocar_roles_automaticos(
        self,
        usuario_id: UUID,
        tipo_cargo_id: UUID,
        agrupacion_id: Optional[UUID],
    ) -> None:
        """Desactiva los UsuarioRol que corresponden a los roles automáticos del cargo."""
        result = await self.session.execute(
            select(TipoCargoRol).where(TipoCargoRol.tipo_cargo_id == tipo_cargo_id)
        )
        tipo_cargo_roles = result.scalars().all()

        for tcr in tipo_cargo_roles:
            await self.session.execute(
                update(UsuarioRol)
                .where(
                    and_(
                        UsuarioRol.usuario_id == usuario_id,
                        UsuarioRol.rol_id == tcr.rol_id,
                        UsuarioRol.agrupacion_id == agrupacion_id,
                        UsuarioRol.activo == True,
                        UsuarioRol.eliminado == False,
                    )
                )
                .values(activo=False)
            )
            logger.debug(
                "Rol automático revocado: usuario=%s rol=%s agrupacion=%s",
                usuario_id, tcr.rol_id, agrupacion_id,
            )

    async def _cerrar_historial_cargo(
        self,
        junta_id: UUID,
        tipo_cargo_id: UUID,
        miembro_id: UUID,
        posicion: int,
        fecha_fin: date,
        motivo: Optional[str],
    ) -> None:
        """Cierra la entrada abierta en historial o crea un registro de cierre."""
        result = await self.session.execute(
            select(HistorialCargoJunta).where(
                and_(
                    HistorialCargoJunta.junta_id == junta_id,
                    HistorialCargoJunta.tipo_cargo_id == tipo_cargo_id,
                    HistorialCargoJunta.miembro_id == miembro_id,
                    HistorialCargoJunta.posicion == posicion,
                    HistorialCargoJunta.fecha_fin == None,
                    HistorialCargoJunta.eliminado == False,
                )
            )
        )
        historial = result.scalars().first()
        if historial:
            historial.fecha_fin = fecha_fin
            historial.motivo_cambio = motivo
            self.session.add(historial)
        else:
            # Si no existe entrada abierta, crear registro de cierre
            self.session.add(
                HistorialCargoJunta(
                    junta_id=junta_id,
                    tipo_cargo_id=tipo_cargo_id,
                    miembro_id=miembro_id,
                    posicion=posicion,
                    fecha_inicio=fecha_fin,
                    fecha_fin=fecha_fin,
                    motivo_cambio=motivo,
                )
            )
