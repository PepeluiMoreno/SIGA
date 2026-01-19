"""Servicio de caché con soporte para Redis y fallback en memoria."""

import os
import json
import pickle
import hashlib
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache en memoria como fallback
_memory_cache = {}
_memory_cache_ttl = {}


class CacheService:
    """Servicio de caché con soporte para Redis y fallback en memoria."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self._redis_available = False

        if redis_url:
            self._setup_redis(redis_url)

    def _setup_redis(self, redis_url: str) -> None:
        """Configura conexión a Redis."""
        try:
            import redis
            self.redis_client = redis.from_url(redis_url)
            # Test connection
            self.redis_client.ping()
            self._redis_available = True
            logger.info("Redis conectado exitosamente")
        except ImportError:
            logger.warning("Redis no está instalado, usando caché en memoria")
        except Exception as e:
            logger.error(f"Error conectando a Redis: {e}")
            logger.warning("Usando caché en memoria como fallback")

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor del caché."""
        try:
            if self._redis_available:
                value = self.redis_client.get(key)
                if value is not None:
                    try:
                        return pickle.loads(value)
                    except Exception:
                        return value.decode('utf-8')
                return default

            # Fallback a memoria
            return self._get_from_memory(key, default)

        except Exception as e:
            logger.error(f"Error obteniendo caché para {key}: {e}")
            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Guarda un valor en caché."""
        try:
            if self._redis_available:
                serialized_value = pickle.dumps(value)
                if ttl:
                    return self.redis_client.setex(key, ttl, serialized_value)
                else:
                    return self.redis_client.set(key, serialized_value)

            # Fallback a memoria
            return self._set_in_memory(key, value, ttl)

        except Exception as e:
            logger.error(f"Error guardando en caché para {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Elimina una clave del caché."""
        try:
            if self._redis_available:
                return bool(self.redis_client.delete(key))

            # Fallback a memoria
            return self._delete_from_memory(key)

        except Exception as e:
            logger.error(f"Error eliminando caché para {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Verifica si una clave existe en el caché."""
        try:
            if self._redis_available:
                return bool(self.redis_client.exists(key))

            # Fallback a memoria
            return self._exists_in_memory(key)

        except Exception as e:
            logger.error(f"Error verificando existencia de {key}: {e}")
            return False

    def flush_all(self) -> bool:
        """Limpia todo el caché."""
        try:
            if self._redis_available:
                return self.redis_client.flushdb()

            # Fallback a memoria
            return self._flush_memory()

        except Exception as e:
            logger.error(f"Error limpiando caché: {e}")
            return False

    def get_ttl(self, key: str) -> int:
        """Obtiene el tiempo de vida restante de una clave."""
        try:
            if self._redis_available:
                return self.redis_client.ttl(key)

            # Fallback a memoria
            return self._get_ttl_from_memory(key)

        except Exception as e:
            logger.error(f"Error obteniendo TTL para {key}: {e}")
            return -1

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Incrementa un contador en el caché."""
        try:
            if self._redis_available:
                return self.redis_client.incr(key, amount)

            # Fallback a memoria
            return self._increment_in_memory(key, amount)

        except Exception as e:
            logger.error(f"Error incrementando {key}: {e}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrementa un contador en el caché."""
        try:
            if self._redis_available:
                return self.redis_client.decr(key, amount)

            # Fallback a memoria
            return self._decrement_in_memory(key, amount)

        except Exception as e:
            logger.error(f"Error decrementando {key}: {e}")
            return None

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Obtiene múltiples valores del caché."""
        resultados = {}

        try:
            if self._redis_available:
                values = self.redis_client.mget(keys)
                for key, value in zip(keys, values):
                    if value is not None:
                        try:
                            resultados[key] = pickle.loads(value)
                        except Exception:
                            resultados[key] = value.decode('utf-8')
                return resultados

            # Fallback a memoria
            for key in keys:
                resultados[key] = self.get(key)
            return resultados

        except Exception as e:
            logger.error(f"Error obteniendo múltiples valores del caché: {e}")
            return {key: None for key in keys}

    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Guarda múltiples valores en el caché."""
        try:
            if self._redis_available:
                # Serializar valores
                serialized_mapping = {}
                for key, value in mapping.items():
                    serialized_mapping[key] = pickle.dumps(value)

                if ttl:
                    # Usar pipeline para TTL
                    pipe = self.redis_client.pipeline()
                    pipe.mset(serialized_mapping)
                    for key in mapping.keys():
                        pipe.expire(key, ttl)
                    pipe.execute()
                else:
                    self.redis_client.mset(serialized_mapping)
                return True

            # Fallback a memoria
            for key, value in mapping.items():
                self._set_in_memory(key, value, ttl)
            return True

        except Exception as e:
            logger.error(f"Error guardando múltiples valores en caché: {e}")
            return False

    # Métodos de caché en memoria (fallback)
    def _get_from_memory(self, key: str, default: Any = None) -> Any:
        """Obtiene valor del caché en memoria."""
        if key in _memory_cache_ttl:
            if datetime.utcnow() > _memory_cache_ttl[key]:
                # Expirado
                del _memory_cache[key]
                del _memory_cache_ttl[key]
                return default

        return _memory_cache.get(key, default)

    def _set_in_memory(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Guarda valor en caché en memoria."""
        _memory_cache[key] = value

        if ttl:
            _memory_cache_ttl[key] = datetime.utcnow() + timedelta(seconds=ttl)
        elif key in _memory_cache_ttl:
            del _memory_cache_ttl[key]

        return True

    def _delete_from_memory(self, key: str) -> bool:
        """Elimina valor del caché en memoria."""
        if key in _memory_cache:
            del _memory_cache[key]
            if key in _memory_cache_ttl:
                del _memory_cache_ttl[key]
            return True
        return False

    def _exists_in_memory(self, key: str) -> bool:
        """Verifica existencia en caché en memoria."""
        return key in _memory_cache

    def _flush_memory(self) -> bool:
        """Limpia caché en memoria."""
        _memory_cache.clear()
        _memory_cache_ttl.clear()
        return True

    def _get_ttl_from_memory(self, key: str) -> int:
        """Obtiene TTL de caché en memoria."""
        if key not in _memory_cache_ttl:
            return -1

        tiempo_restante = (_memory_cache_ttl[key] - datetime.utcnow()).total_seconds()
        return max(0, int(tiempo_restante))

    def _increment_in_memory(self, key: str, amount: int = 1) -> int:
        """Incrementa contador en caché en memoria."""
        if key not in _memory_cache:
            _memory_cache[key] = 0

        if isinstance(_memory_cache[key], (int, float)):
            _memory_cache[key] += amount
            return int(_memory_cache[key])

        return 0

    def _decrement_in_memory(self, key: str, amount: int = 1) -> int:
        """Decrementa contador en caché en memoria."""
        return self._increment_in_memory(key, -amount)


# Funciones helper para generar keys de caché
def generar_cache_key(prefix: str, *args) -> str:
    """Genera una clave de caché única a partir de parámetros."""
    parts = [prefix]
    for arg in args:
        if isinstance(arg, (dict, list)):
            # Serializar objetos complejos
            parts.append(hashlib.md5(json.dumps(arg, sort_keys=True).encode()).hexdigest())
        else:
            parts.append(str(arg))
    return ":".join(parts)


def generar_cache_key_modelo(modelo_clase, id_objeto: str, version: Optional[str] = None) -> str:
    """Genera clave de caché para un modelo."""
    key_parts = ["model", modelo_clase.__name__, str(id_objeto)]
    if version:
        key_parts.append(version)
    return ":".join(key_parts)


# Singleton global
_cache_service = None


def get_cache_service(redis_url: Optional[str] = None) -> CacheService:
    """Factory para obtener el servicio de caché (singleton)."""
    global _cache_service
    if _cache_service is None:
        # Intentar obtener URL de Redis de variables de entorno
        if not redis_url:
            redis_url = os.getenv('REDIS_URL')
        _cache_service = CacheService(redis_url)
    return _cache_service
