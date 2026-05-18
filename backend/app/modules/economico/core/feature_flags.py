"""Feature flags del módulo económico.

El modo de contabilidad se lee del parámetro 'org.contabilidad_compleja'
almacenado en la tabla configuraciones (Parámetros Generales → Funcionalidades).
La función is_version_completa() acepta una sesión SQLAlchemy para consultar
la BD, con caché en proceso para evitar una query por cada apunte.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Caché en memoria (se invalida al guardar parámetros)
_cache: Optional[bool] = None


def invalidar_cache() -> None:
    """Llamar cuando se guarda el parámetro org.contabilidad_compleja."""
    global _cache
    _cache = None


async def is_version_completa(session: Optional[AsyncSession] = None) -> bool:
    """Devuelve True si la contabilidad de partida doble está activa.

    Lee 'org.contabilidad_compleja' de la tabla configuraciones.
    Si no existe el parámetro, devuelve False (modo simple por defecto).
    Usa caché en proceso; llamar invalidar_cache() tras guardar el parámetro.
    """
    global _cache
    if _cache is not None:
        return _cache

    if session is None:
        return False

    from app.modules.configuracion.models.configuracion import Configuracion
    result = await session.execute(
        select(Configuracion).where(Configuracion.clave == "org.contabilidad_compleja")
    )
    cfg = result.scalars().first()
    if cfg is None:
        _cache = False
    else:
        _cache = cfg.valor.lower() in ("true", "1", "yes", "si", "on")

    return _cache


def modulo_activo(nombre: str) -> bool:
    return True
