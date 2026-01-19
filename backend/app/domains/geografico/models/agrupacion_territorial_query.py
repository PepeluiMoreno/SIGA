"""
Vista alternativa: AgrupacionTerritorial como query wrapper.

Esta opción no crea una vista materializada real,
sino que usa un modelo que mapea a una subquery.
"""

from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.domains.organizaciones.models import Organizacion, TipoOrganizacion


class AgrupacionTerritorialQuery:
    """
    Helper para queries de agrupaciones territoriales.

    Proporciona métodos convenientes para trabajar con agrupaciones
    sin necesidad de filtrar manualmente por tipo.
    """

    @staticmethod
    def get_base_query():
        """
        Devuelve el query base para agrupaciones territoriales.

        Filtra organizaciones de categoria INTERNA.
        """
        return (
            select(Organizacion)
            .join(TipoOrganizacion, Organizacion.tipo_id == TipoOrganizacion.id)
            .where(
                TipoOrganizacion.categoria == 'INTERNA',
                Organizacion.eliminado == False
            )
        )

    @staticmethod
    def get_by_tipo(tipo: str):
        """
        Filtra agrupaciones por tipo (ESTATAL, AUTONOMICA, PROVINCIAL, LOCAL).

        Args:
            tipo: Tipo de agrupación

        Returns:
            Query filtrado
        """
        return (
            AgrupacionTerritorialQuery.get_base_query()
            .where(Organizacion.ambito == tipo)
        )

    @staticmethod
    def get_activas():
        """Devuelve query de agrupaciones activas."""
        return (
            AgrupacionTerritorialQuery.get_base_query()
            .where(Organizacion.activo == True)
        )

    @staticmethod
    def get_por_provincia(provincia_id):
        """Filtra agrupaciones de una provincia."""
        return (
            AgrupacionTerritorialQuery.get_base_query()
            .where(Organizacion.provincia_id == provincia_id)
        )

    @staticmethod
    def get_jerarquia_completa():
        """
        Devuelve todas las agrupaciones ordenadas jerárquicamente.

        Primero estatales, luego autonómicas, provinciales y locales.
        """
        return (
            AgrupacionTerritorialQuery.get_base_query()
            .order_by(
                Organizacion.nivel,
                Organizacion.nombre
            )
        )

# Uso en código:
#
# from app.domains.geografico.models.agrupacion_territorial_query import AgrupacionTerritorialQuery
#
# # Obtener todas las agrupaciones activas
# result = await session.execute(AgrupacionTerritorialQuery.get_activas())
# agrupaciones = result.scalars().all()
#
# # Obtener agrupaciones autonómicas
# result = await session.execute(AgrupacionTerritorialQuery.get_by_tipo('AUTONOMICA'))
# autonomicas = result.scalars().all()
