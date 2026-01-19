"""Script para inicializar configuraciones por defecto del sistema."""

import uuid
import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import async_session
from ..domains.core.models.configuracion import Configuracion, ReglaValidacionConfig

logger = logging.getLogger(__name__)

# Configuraciones por defecto
CONFIGURACIONES_POR_DEFECTO = [
    # Finanzas
    {
        'clave': 'CUOTA_IMPORTE_DEFAULT',
        'valor': '50.0',
        'tipo_dato': 'float',
        'descripcion': 'Importe por defecto de la cuota anual',
        'grupo': 'finanzas',
        'orden': 1
    },
    {
        'clave': 'DIAS_VENCIMIENTO_CUOTA',
        'valor': '30',
        'tipo_dato': 'int',
        'descripcion': 'Días antes de considerar una cuota como vencida',
        'grupo': 'finanzas',
        'orden': 2
    },
    {
        'clave': 'MONEDA_PRINCIPAL',
        'valor': 'EUR',
        'tipo_dato': 'string',
        'descripcion': 'Moneda principal del sistema (EUR, USD, etc.)',
        'grupo': 'finanzas',
        'orden': 3
    },

    # Notificaciones
    {
        'clave': 'NOTIFICACIONES_EMAIL_ENABLED',
        'valor': 'true',
        'tipo_dato': 'bool',
        'descripcion': 'Activar envío de notificaciones por email',
        'grupo': 'notificaciones',
        'orden': 1
    },

    # Seguridad
    {
        'clave': 'MAX_INTENTOS_LOGIN',
        'valor': '5',
        'tipo_dato': 'int',
        'descripcion': 'Máximo número de intentos de login antes de bloquear',
        'grupo': 'seguridad',
        'orden': 1
    },
    {
        'clave': 'TIEMPO_BLOQUEO_MINUTOS',
        'valor': '30',
        'tipo_dato': 'int',
        'descripcion': 'Tiempo de bloqueo en minutos tras exceder intentos',
        'grupo': 'seguridad',
        'orden': 2
    },
    {
        'clave': 'CONTRASENA_LONGITUD_MINIMA',
        'valor': '8',
        'tipo_dato': 'int',
        'descripcion': 'Longitud mínima de la contraseña',
        'grupo': 'seguridad',
        'orden': 3
    },
    {
        'clave': 'CONTRASENA_REQUIERE_MAYUSCULAS',
        'valor': 'true',
        'tipo_dato': 'bool',
        'descripcion': 'La contraseña debe contener al menos una mayúscula',
        'grupo': 'seguridad',
        'orden': 4
    },
    {
        'clave': 'CONTRASENA_REQUIERE_MINUSCULAS',
        'valor': 'true',
        'tipo_dato': 'bool',
        'descripcion': 'La contraseña debe contener al menos una minúscula',
        'grupo': 'seguridad',
        'orden': 5
    },
    {
        'clave': 'CONTRASENA_REQUIERE_NUMEROS',
        'valor': 'true',
        'tipo_dato': 'bool',
        'descripcion': 'La contraseña debe contener al menos un número',
        'grupo': 'seguridad',
        'orden': 6
    },
    {
        'clave': 'CONTRASENA_REQUIERE_ESPECIALES',
        'valor': 'false',
        'tipo_dato': 'bool',
        'descripcion': 'La contraseña debe contener caracteres especiales',
        'grupo': 'seguridad',
        'orden': 7
    },
    {
        'clave': 'DURACION_SESION_MINUTOS',
        'valor': '1440',
        'tipo_dato': 'int',
        'descripcion': 'Duración de la sesión en minutos (24 horas por defecto)',
        'grupo': 'seguridad',
        'orden': 8
    },

    # Interfaz
    {
        'clave': 'FORMATO_FECHA',
        'valor': '%d/%m/%Y',
        'tipo_dato': 'string',
        'descripcion': 'Formato de fecha para la interfaz',
        'grupo': 'interfaz',
        'orden': 1
    },
    {
        'clave': 'IDIOMA_DEFAULT',
        'valor': 'es',
        'tipo_dato': 'string',
        'descripcion': 'Idioma por defecto del sistema',
        'grupo': 'interfaz',
        'orden': 2
    },
]

# Reglas de validación
REGLAS_VALIDACION = [
    {
        'config_clave': 'CUOTA_IMPORTE_DEFAULT',
        'tipo_dato': 'float',
        'min_valor': 0.0,
        'max_valor': 10000.0,
        'decimales': 2,
        'descripcion': 'Importe entre 0 y 10000 euros',
    },
    {
        'config_clave': 'DIAS_VENCIMIENTO_CUOTA',
        'tipo_dato': 'int',
        'min_valor': 1.0,
        'max_valor': 365.0,
        'descripcion': 'Entre 1 y 365 días',
    },
    {
        'config_clave': 'MAX_INTENTOS_LOGIN',
        'tipo_dato': 'int',
        'min_valor': 3.0,
        'max_valor': 10.0,
        'descripcion': 'Entre 3 y 10 intentos',
    },
    {
        'config_clave': 'DURACION_SESION_MINUTOS',
        'tipo_dato': 'int',
        'min_valor': 15.0,
        'max_valor': 10080.0,  # 7 días
        'descripcion': 'Entre 15 minutos y 7 días',
    },
    {
        'config_clave': 'MONEDA_PRINCIPAL',
        'tipo_dato': 'moneda',
        'pattern_regex': r'^[A-Z]{3}$',
        'descripcion': 'Código ISO de 3 letras',
        'mensaje_error': 'Debe ser un código ISO de moneda válido (EUR, USD, etc.)',
    },
]


async def inicializar_configuraciones(session: AsyncSession) -> None:
    """Inicializa las configuraciones por defecto si no existen."""
    logger.info("Iniciando carga de configuraciones por defecto...")

    creadas = 0
    for config_data in CONFIGURACIONES_POR_DEFECTO:
        # Verificar si ya existe
        result = await session.execute(
            select(Configuracion).where(
                Configuracion.clave == config_data['clave']
            )
        )
        existe = result.scalar_one_or_none()

        if not existe:
            config = Configuracion(
                id=uuid.uuid4(),
                **config_data
            )
            session.add(config)
            creadas += 1
            logger.info(f"Configuración creada: {config_data['clave']}")

    await session.commit()
    logger.info(f"Configuraciones inicializadas: {creadas} creadas")


async def inicializar_reglas_validacion(session: AsyncSession) -> None:
    """Inicializa las reglas de validación por defecto."""
    logger.info("Iniciando carga de reglas de validación...")

    creadas = 0
    for regla_data in REGLAS_VALIDACION:
        # Verificar si ya existe
        result = await session.execute(
            select(ReglaValidacionConfig).where(
                ReglaValidacionConfig.config_clave == regla_data['config_clave']
            )
        )
        existe = result.scalar_one_or_none()

        if not existe:
            regla = ReglaValidacionConfig(
                id=uuid.uuid4(),
                **regla_data
            )
            session.add(regla)
            creadas += 1
            logger.info(f"Regla de validación creada: {regla_data['config_clave']}")

    await session.commit()
    logger.info(f"Reglas de validación inicializadas: {creadas} creadas")


async def main():
    """Función principal."""
    logging.basicConfig(level=logging.INFO)
    logger.info("=== Inicialización de Configuraciones ===")

    async with async_session() as session:
        await inicializar_configuraciones(session)
        await inicializar_reglas_validacion(session)

    logger.info("=== Proceso completado exitosamente ===")


if __name__ == "__main__":
    asyncio.run(main())
