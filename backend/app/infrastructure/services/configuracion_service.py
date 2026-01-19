"""Servicio unificado de configuración con validación dinámica y caché."""

import json
import re
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ConfiguracionService:
    """Servicio para gestionar configuración con validación dinámica y caché."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._cache = {}  # Cache simple en memoria
        self._cache_ttl = {}  # TTL para cada entrada del cache

    async def get(self, clave: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración con cache."""
        # Verificar cache
        if self._esta_en_cache(clave):
            return self._cache[clave]

        try:
            from ...domains.core.models.configuracion import Configuracion

            result = await self.session.execute(
                select(Configuracion).where(
                    Configuracion.clave == clave.upper(),
                    Configuracion.eliminado == False
                )
            )
            config = result.scalar_one_or_none()

            if config:
                valor = config.get_valor()
                self._guardar_en_cache(clave, valor)
                return valor

            return default

        except Exception as e:
            logger.error(f"Error obteniendo configuración {clave}: {e}")
            return default

    async def set(self, clave: str, valor: Any, usuario_id: Optional[str] = None,
                  validar: bool = True) -> bool:
        """Establece un valor de configuración con validación opcional."""
        try:
            if validar:
                valor = await self._validar_valor(clave, valor)

            from ...domains.core.models.configuracion import Configuracion

            result = await self.session.execute(
                select(Configuracion).where(
                    Configuracion.clave == clave.upper(),
                    Configuracion.eliminado == False
                )
            )
            config = result.scalar_one_or_none()

            if not config:
                logger.warning(f"Configuración {clave} no encontrada")
                return False

            if not config.modificable:
                logger.warning(f"Configuración {clave} no es modificable")
                return False

            config.set_valor(valor)
            if usuario_id:
                config.modificado_por_id = usuario_id

            await self.session.commit()

            # Actualizar cache
            self._guardar_en_cache(clave, valor)

            logger.info(f"Configuración actualizada: {clave}")
            return True

        except Exception as e:
            logger.error(f"Error estableciendo configuración {clave}: {e}")
            await self.session.rollback()
            return False

    async def get_bool(self, clave: str, default: bool = False) -> bool:
        """Obtiene un valor booleano con validación."""
        valor = await self.get(clave, default)
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, str):
            return valor.lower() in ['true', '1', 'yes', 'si', 'on', 'enabled']
        return bool(valor) if valor is not None else default

    async def get_int(self, clave: str, default: int = 0) -> int:
        """Obtiene un valor entero con validación según reglas."""
        valor = await self.get(clave, default)
        try:
            int_val = int(valor) if valor is not None else default

            # Obtener reglas de validación
            reglas = await self._obtener_reglas_validacion(clave)
            if reglas:
                if reglas.min_valor is not None and int_val < reglas.min_valor:
                    return int(reglas.min_valor)
                if reglas.max_valor is not None and int_val > reglas.max_valor:
                    return int(reglas.max_valor)

            return int_val

        except (ValueError, TypeError):
            return default

    async def get_float(self, clave: str, default: float = 0.0) -> float:
        """Obtiene un valor float con validación según reglas."""
        valor = await self.get(clave, default)
        try:
            float_val = float(valor) if valor is not None else default

            # Obtener reglas de validación
            reglas = await self._obtener_reglas_validacion(clave)
            if reglas:
                if reglas.min_valor is not None and float_val < reglas.min_valor:
                    return reglas.min_valor
                if reglas.max_valor is not None and float_val > reglas.max_valor:
                    return reglas.max_valor
                if reglas.decimales is not None:
                    return round(float_val, reglas.decimales)

            return float_val

        except (ValueError, TypeError):
            return default

    async def get_string(self, clave: str, default: str = "") -> str:
        """Obtiene un string con validación según reglas."""
        valor = await self.get(clave, default)
        if not isinstance(valor, str):
            valor = str(valor) if valor is not None else default

        # Obtener reglas de validación
        reglas = await self._obtener_reglas_validacion(clave)
        if reglas:
            if reglas.max_longitud is not None and len(valor) > reglas.max_longitud:
                valor = valor[:reglas.max_longitud]
            if reglas.pattern_regex is not None:
                if not re.match(reglas.pattern_regex, valor):
                    return default

        return valor

    async def get_list(self, clave: str, default: List[Any] = None) -> List[Any]:
        """Obtiene una lista de valores."""
        if default is None:
            default = []

        valor = await self.get(clave, default)
        if isinstance(valor, list):
            return valor
        if isinstance(valor, str):
            try:
                return json.loads(valor)
            except json.JSONDecodeError:
                return default
        return default

    async def get_dict(self, clave: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obtiene un diccionario de valores."""
        if default is None:
            default = {}

        valor = await self.get(clave, default)
        if isinstance(valor, dict):
            return valor
        if isinstance(valor, str):
            try:
                return json.loads(valor)
            except json.JSONDecodeError:
                return default
        return default

    async def get_timedelta(self, clave: str, default: timedelta = None) -> timedelta:
        """Obtiene un timedelta desde segundos o string."""
        if default is None:
            default = timedelta(0)

        valor = await self.get(clave, default)

        if isinstance(valor, timedelta):
            return valor

        if isinstance(valor, (int, float)):
            return timedelta(seconds=valor)

        if isinstance(valor, str):
            # Formatos: "30d", "24h", "60m", "3600s"
            match = re.match(r'^(\d+)([dhms])$', valor.lower())
            if match:
                cantidad, unidad = int(match.group(1)), match.group(2)
                if unidad == 'd':
                    return timedelta(days=cantidad)
                elif unidad == 'h':
                    return timedelta(hours=cantidad)
                elif unidad == 'm':
                    return timedelta(minutes=cantidad)
                elif unidad == 's':
                    return timedelta(seconds=cantidad)

        return default

    async def get_grupo(self, grupo: str) -> Dict[str, Any]:
        """Obtiene todas las configuraciones de un grupo."""
        from ...domains.core.models.configuracion import Configuracion

        result = await self.session.execute(
            select(Configuracion).where(
                Configuracion.grupo == grupo,
                Configuracion.eliminado == False
            )
        )
        configs = result.scalars().all()

        return {config.clave: config.get_valor() for config in configs}

    async def crear_configuracion(self, clave: str, valor: Any, tipo_dato: str,
                                   descripcion: str = "", grupo: str = "general",
                                   modificable: bool = True, usuario_id: Optional[str] = None) -> bool:
        """Crea una nueva configuración."""
        try:
            from ...domains.core.models.configuracion import Configuracion

            # Verificar si ya existe
            result = await self.session.execute(
                select(Configuracion).where(
                    Configuracion.clave == clave.upper(),
                    Configuracion.eliminado == False
                )
            )
            existe = result.scalar_one_or_none()

            if existe:
                logger.warning(f"Configuración {clave} ya existe")
                return False

            import uuid

            config = Configuracion(
                id=uuid.uuid4(),
                clave=clave.upper(),
                valor=str(valor),
                tipo_dato=tipo_dato,
                descripcion=descripcion,
                grupo=grupo,
                modificable=modificable
            )

            if usuario_id:
                config.creado_por_id = usuario_id

            self.session.add(config)
            await self.session.commit()

            logger.info(f"Configuración creada: {clave}")
            return True

        except Exception as e:
            logger.error(f"Error creando configuración {clave}: {e}")
            await self.session.rollback()
            return False

    async def eliminar_configuracion(self, clave: str, usuario_id: Optional[str] = None) -> bool:
        """Elimina lógicamente una configuración."""
        try:
            from ...domains.core.models.configuracion import Configuracion

            result = await self.session.execute(
                select(Configuracion).where(
                    Configuracion.clave == clave.upper(),
                    Configuracion.eliminado == False
                )
            )
            config = result.scalar_one_or_none()

            if not config:
                return False

            # Usar el soft delete del BaseModel
            config.soft_delete(usuario_id)
            await self.session.commit()

            # Eliminar del cache
            if clave.upper() in self._cache:
                del self._cache[clave.upper()]
                del self._cache_ttl[clave.upper()]

            logger.info(f"Configuración eliminada: {clave}")
            return True

        except Exception as e:
            logger.error(f"Error eliminando configuración {clave}: {e}")
            await self.session.rollback()
            return False

    async def _validar_valor(self, clave: str, valor: Any) -> Any:
        """Valida el valor según las reglas almacenadas en BD."""
        reglas = await self._obtener_reglas_validacion(clave)
        if not reglas:
            return valor

        # Validación por tipo de dato
        if reglas.tipo_dato == 'email':
            if '@' not in str(valor):
                raise ValueError(f"Valor inválido para {clave}: debe ser un email válido")

        elif reglas.tipo_dato == 'url':
            # Validación básica de URL sin dependencia externa
            if not str(valor).startswith(('http://', 'https://')):
                raise ValueError(f"Valor inválido para {clave}: debe ser una URL válida")

        elif reglas.tipo_dato == 'porcentaje':
            float_val = float(valor)
            if float_val < 0 or float_val > 100:
                raise ValueError(f"Valor inválido para {clave}: debe ser un porcentaje entre 0 y 100")

        elif reglas.tipo_dato == 'moneda':
            # Validar código ISO de moneda
            if not re.match(r'^[A-Z]{3}$', str(valor).upper()):
                raise ValueError(f"Valor inválido para {clave}: debe ser un código ISO de moneda (EUR, USD, etc.)")

        elif reglas.pattern_regex is not None:
            if not re.match(reglas.pattern_regex, str(valor)):
                raise ValueError(f"Valor inválido para {clave}: no cumple con el patrón requerido")

        return valor

    async def _obtener_reglas_validacion(self, clave: str):
        """Obtiene las reglas de validación para una clave desde BD."""
        from ...domains.core.models.configuracion import ReglaValidacionConfig

        result = await self.session.execute(
            select(ReglaValidacionConfig).where(
                ReglaValidacionConfig.config_clave == clave.upper(),
                ReglaValidacionConfig.activa == True
            )
        )
        return result.scalar_one_or_none()

    def _esta_en_cache(self, clave: str) -> bool:
        """Verifica si una clave está en caché y no ha expirado."""
        if clave not in self._cache:
            return False

        if clave not in self._cache_ttl:
            return False

        # TTL de 5 minutos por defecto
        if datetime.utcnow() > self._cache_ttl[clave]:
            del self._cache[clave]
            del self._cache_ttl[clave]
            return False

        return True

    def _guardar_en_cache(self, clave: str, valor: Any):
        """Guarda un valor en caché."""
        self._cache[clave] = valor
        self._cache_ttl[clave] = datetime.utcnow() + timedelta(minutes=5)

    def limpiar_cache(self):
        """Limpia el caché de configuración."""
        self._cache.clear()
        self._cache_ttl.clear()
        logger.info("Caché de configuración limpiado")


# Nota: No usamos singleton global en async, se crea por request con dependency injection
