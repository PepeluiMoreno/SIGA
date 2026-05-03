"""Sincroniza los catálogos declarados en código con la base de datos.

Se ejecuta una vez al arrancar la aplicación (lifespan de FastAPI).
Usa upsert para que sea idempotente: no destruye asignaciones existentes,
solo añade o actualiza las definiciones del catálogo.
"""

from __future__ import annotations

import logging
from typing import Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.transaccion import Transaccion
from ..models.funcionalidad import Funcionalidad, FuncionalidadTransaccion, FlujoAprobacion
from ..models.rol import Rol
from .registry import ModuleCatalog

logger = logging.getLogger(__name__)


class CatalogSyncService:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def sync(self) -> None:
        await self._sync_transacciones()
        await self._sync_funcionalidades()
        await self._sync_flujos()
        await self.session.commit()
        logger.info("Catálogo sincronizado correctamente")

    # ------------------------------------------------------------------
    # Transacciones
    # ------------------------------------------------------------------

    async def _sync_transacciones(self) -> None:
        for defn in ModuleCatalog.get_transacciones():
            result = await self.session.execute(
                select(Transaccion).where(Transaccion.codigo == defn.codigo)
            )
            obj = result.scalar_one_or_none()
            if obj is None:
                obj = Transaccion(
                    id=uuid.uuid4(),
                    codigo=defn.codigo,
                    nombre=defn.nombre,
                    descripcion=defn.descripcion,
                    tipo=defn.tipo,
                    modulo=defn.codigo.split("_")[0].lower(),
                    activa=True,
                    sistema=defn.sistema,
                )
                self.session.add(obj)
                logger.debug("Transaccion creada: %s", defn.codigo)
            else:
                obj.nombre = defn.nombre
                obj.descripcion = defn.descripcion
                obj.sistema = defn.sistema

    # ------------------------------------------------------------------
    # Funcionalidades y sus transacciones
    # ------------------------------------------------------------------

    async def _sync_funcionalidades(self) -> None:
        for defn in ModuleCatalog.get_funcionalidades():
            result = await self.session.execute(
                select(Funcionalidad).where(Funcionalidad.codigo == defn.codigo)
            )
            obj = result.scalar_one_or_none()
            if obj is None:
                obj = Funcionalidad(
                    id=uuid.uuid4(),
                    codigo=defn.codigo,
                    nombre=defn.nombre,
                    descripcion=defn.descripcion,
                    modulo=defn.modulo,
                    activa=True,
                    sistema=defn.sistema,
                )
                self.session.add(obj)
                logger.debug("Funcionalidad creada: %s", defn.codigo)
            else:
                obj.nombre = defn.nombre
                obj.descripcion = defn.descripcion
                obj.sistema = defn.sistema

            await self.session.flush()
            await self._sync_funcionalidad_transacciones(obj, defn)

    async def _sync_funcionalidad_transacciones(
        self, func_obj: Funcionalidad, defn
    ) -> None:
        for ft_defn in defn.transacciones:
            t_result = await self.session.execute(
                select(Transaccion).where(Transaccion.codigo == ft_defn.transaccion_codigo)
            )
            transaccion = t_result.scalar_one_or_none()
            if transaccion is None:
                logger.warning(
                    "Transaccion '%s' no encontrada para funcionalidad '%s'",
                    ft_defn.transaccion_codigo,
                    func_obj.codigo,
                )
                continue

            existing = await self.session.execute(
                select(FuncionalidadTransaccion).where(
                    FuncionalidadTransaccion.funcionalidad_id == func_obj.id,
                    FuncionalidadTransaccion.transaccion_id == transaccion.id,
                )
            )
            if existing.scalar_one_or_none() is None:
                self.session.add(FuncionalidadTransaccion(
                    id=uuid.uuid4(),
                    funcionalidad_id=func_obj.id,
                    transaccion_id=transaccion.id,
                    ambito=ft_defn.ambito,
                ))

    # ------------------------------------------------------------------
    # Flujos de aprobación
    # ------------------------------------------------------------------

    async def _sync_flujos(self) -> None:
        for defn in ModuleCatalog.get_flujos():
            result = await self.session.execute(
                select(FlujoAprobacion).where(FlujoAprobacion.codigo == defn.codigo)
            )
            obj = result.scalar_one_or_none()

            t_inicio = await self._get_transaccion(defn.transaccion_inicio_codigo)
            t_aprobacion = await self._get_transaccion(defn.transaccion_aprobacion_codigo)
            rol_aprobador = await self._get_rol(defn.rol_aprobador_codigo)
            t_rechazo: Optional[Transaccion] = None
            if defn.transaccion_rechazo_codigo:
                t_rechazo = await self._get_transaccion(defn.transaccion_rechazo_codigo)

            if not (t_inicio and t_aprobacion and rol_aprobador):
                logger.warning("FlujoAprobacion '%s' omitido: faltan referencias", defn.codigo)
                continue

            if obj is None:
                obj = FlujoAprobacion(
                    id=uuid.uuid4(),
                    codigo=defn.codigo,
                    nombre=defn.nombre,
                    descripcion=defn.descripcion,
                    transaccion_inicio_id=t_inicio.id,
                    transaccion_aprobacion_id=t_aprobacion.id,
                    transaccion_rechazo_id=t_rechazo.id if t_rechazo else None,
                    rol_aprobador_id=rol_aprobador.id,
                    entidad=defn.entidad,
                    activo=True,
                    sistema=defn.sistema,
                )
                self.session.add(obj)
                logger.debug("FlujoAprobacion creado: %s", defn.codigo)
            else:
                obj.nombre = defn.nombre
                obj.descripcion = defn.descripcion
                obj.sistema = defn.sistema

    async def _get_transaccion(self, codigo: str) -> Optional[Transaccion]:
        result = await self.session.execute(
            select(Transaccion).where(Transaccion.codigo == codigo)
        )
        return result.scalar_one_or_none()

    async def _get_rol(self, codigo: str) -> Optional[Rol]:
        result = await self.session.execute(
            select(Rol).where(Rol.codigo == codigo)
        )
        return result.scalar_one_or_none()
