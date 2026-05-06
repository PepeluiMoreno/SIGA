"""Servicio orquestador del módulo de acceso.

Cubre el ciclo completo:
  - Creación de usuarios con credenciales
  - Constitución y gestión de juntas directivas
  - Asignación/revocación de nombramientos (rol organizacional) con propagación de permisos
  - Emisión de eventos de dominio para invalidación de la PermissionMatrix

Nota: Los cargos son directamente roles de tipo ORGANIZACION.
UsuarioRol ES el nombramiento activo; HistorialNombramiento traza los cambios.
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
from ...membresia.models.junta import JuntaDirectiva
from ...membresia.models.historial_nombramiento import HistorialNombramiento
from ...acceso.models.usuario import Usuario, UsuarioRol
from ...acceso.models.rol import TipoRol

logger = logging.getLogger(__name__)


class AccesoService:
    """Orquesta operaciones de acceso: usuarios, juntas y nombramientos."""

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
    # Nombramientos (cargo = rol organizacional)
    # ------------------------------------------------------------------

    async def asignar_nombramiento(
        self,
        usuario_id: UUID,
        rol_id: UUID,
        fecha_inicio: date,
        agrupacion_id: Optional[UUID] = None,
        motivo: Optional[str] = None,
        tipo_origen: Optional[str] = None,
    ) -> UsuarioRol:
        """Asigna un cargo (rol organizacional) a un usuario/miembro.

        - Crea UsuarioRol activo (el nombramiento vigente).
        - Registra en HistorialNombramiento.
        - Emite CargoAssigned.

        Args:
            rol_id: El rol de tipo ORGANIZACION que se asigna.
            agrupacion_id: Ámbito territorial del nombramiento.
            tipo_origen: 'JUNTA', 'MANUAL', 'MIGRACION', 'SEED'.

        Raises:
            ValueError: si el usuario ya tiene este rol activo en el mismo ámbito.
        """
        # Validar que no exista ya activo
        result = await self.session.execute(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_id == rol_id,
                UsuarioRol.agrupacion_id == agrupacion_id,
                UsuarioRol.activo == True,
                UsuarioRol.eliminado == False,
            )
        )
        if result.scalars().first():
            raise ValueError(
                f"El usuario ya tiene el rol {rol_id} en ámbito {agrupacion_id}"
            )

        usuario_rol = UsuarioRol(
            usuario_id=usuario_id,
            rol_id=rol_id,
            agrupacion_id=agrupacion_id,
            activo=True,
        )
        self.session.add(usuario_rol)
        await self.session.flush()

        # Historial
        historial = HistorialNombramiento(
            miembro_id=usuario_id,
            rol_id=rol_id,
            agrupacion_id=agrupacion_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=None,
            tipo_origen=tipo_origen,
            motivo=motivo,
        )
        self.session.add(historial)

        await self.session.flush()

        await event_bus.publish(
            CargoAssigned(
                usuario_id=str(usuario_id),
                cargo_codigo=str(rol_id),
                agrupacion_id=str(agrupacion_id) if agrupacion_id else None,
            )
        )

        return usuario_rol

    async def revocar_nombramiento(
        self,
        usuario_id: UUID,
        rol_id: UUID,
        fecha_fin: date,
        motivo: Optional[str] = None,
        agrupacion_id: Optional[UUID] = None,
    ) -> UsuarioRol:
        """Revoca un nombramiento (cargo) activo.

        - Desactiva UsuarioRol.
        - Cierra la entrada en HistorialNombramiento.
        - Emite CargoRevoked.

        Raises:
            ValueError: si el nombramiento no existe o ya está inactivo.
        """
        result = await self.session.execute(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_id == rol_id,
                UsuarioRol.agrupacion_id == agrupacion_id,
                UsuarioRol.eliminado == False,
                UsuarioRol.activo == True,
            )
        )
        usuario_rol = result.scalars().first()
        if not usuario_rol:
            raise ValueError("No existe un nombramiento activo con estos parámetros")

        usuario_rol.activo = False
        self.session.add(usuario_rol)

        # Cerrar historial
        hist_result = await self.session.execute(
            select(HistorialNombramiento).where(
                HistorialNombramiento.miembro_id == usuario_id,
                HistorialNombramiento.rol_id == rol_id,
                HistorialNombramiento.agrupacion_id == agrupacion_id,
                HistorialNombramiento.fecha_fin == None,
                HistorialNombramiento.eliminado == False,
            )
        )
        historial = hist_result.scalars().first()
        if historial:
            historial.fecha_fin = fecha_fin
            historial.motivo = motivo
            self.session.add(historial)
        else:
            historial = HistorialNombramiento(
                miembro_id=usuario_id,
                rol_id=rol_id,
                agrupacion_id=agrupacion_id,
                fecha_inicio=fecha_fin,
                fecha_fin=fecha_fin,
                motivo=motivo,
                tipo_origen='RESCISION',
            )
            self.session.add(historial)

        await self.session.flush()

        await event_bus.publish(
            CargoRevoked(
                usuario_id=str(usuario_id),
                cargo_codigo=str(rol_id),
                agrupacion_id=str(agrupacion_id) if agrupacion_id else None,
            )
        )

        return usuario_rol

    async def obtener_nombramientos_activos(
        self,
        usuario_id: Optional[UUID] = None,
        rol_id: Optional[UUID] = None,
        agrupacion_id: Optional[UUID] = None,
    ) -> list[UsuarioRol]:
        """Consulta los nombramientos (roles organizacionales) activos."""
        conditions = [
            UsuarioRol.activo == True,
            UsuarioRol.eliminado == False,
        ]
        if usuario_id:
            conditions.append(UsuarioRol.usuario_id == usuario_id)
        if rol_id:
            conditions.append(UsuarioRol.rol_id == rol_id)
        if agrupacion_id:
            conditions.append(UsuarioRol.agrupacion_id == agrupacion_id)

        result = await self.session.execute(
            select(UsuarioRol)
            .join(UsuarioRol.rol)
            .where(and_(*conditions))
            .order_by(UsuarioRol.fecha_creacion)
        )
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    async def _get_agrupacion_junta(self, junta_id: UUID) -> Optional[UUID]:
        result = await self.session.execute(
            select(JuntaDirectiva.agrupacion_id).where(JuntaDirectiva.id == junta_id)
        )
        row = result.first()
        return row[0] if row else None
