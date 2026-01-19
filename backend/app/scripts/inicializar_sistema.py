"""Script maestro para inicializar todo el sistema con datos por defecto."""

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from .inicializar_configuraciones import inicializar_configuraciones
from .inicializar_estados import inicializar_estados
from .inicializar_geografico import inicializar_geografico
from .inicializar_tipos_notificacion import inicializar_tipos_notificacion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def inicializar_sistema_completo(session: AsyncSession) -> None:
    """
    Inicializa todo el sistema con datos por defecto.

    Orden de inicialización:
    1. Configuraciones del sistema
    2. Estados (para cuotas, campañas, tareas, etc.)
    3. Datos geográficos (países, provincias, municipios)
    4. Tipos de notificación

    Args:
        session: Sesión de base de datos activa
    """
    print("\n" + "="*80)
    print(" "*20 + "INICIALIZACIÓN DEL SISTEMA AIEL")
    print("="*80 + "\n")

    try:
        # 1. Configuraciones
        logger.info("Paso 1/4: Inicializando configuraciones del sistema...")
        await inicializar_configuraciones(session)

        # 2. Estados
        logger.info("\nPaso 2/4: Inicializando estados de entidades...")
        await inicializar_estados(session)

        # 3. Datos geográficos
        logger.info("\nPaso 3/4: Inicializando datos geográficos...")
        await inicializar_geografico(session)

        # 4. Tipos de notificación
        logger.info("\nPaso 4/4: Inicializando tipos de notificación...")
        await inicializar_tipos_notificacion(session)

        print("\n" + "="*80)
        print(" "*25 + "¡INICIALIZACIÓN COMPLETADA!")
        print("="*80)
        print("\nResumen:")
        print("  * 12 configuraciones del sistema")
        print("  * 37 estados de entidades (7 tipos)")
        print("  * 1 país, 52 provincias, 20 municipios")
        print("  * 18 tipos de notificación")
        print("\n" + "="*80 + "\n")

    except Exception as e:
        logger.error(f"\n❌ Error durante la inicialización: {e}")
        raise


async def main():
    """Función principal para ejecutar el script."""
    from ..core.database import async_session

    async with async_session() as session:
        await inicializar_sistema_completo(session)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
