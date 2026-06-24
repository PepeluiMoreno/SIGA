"""
Helper de queries para UnidadOrganizativa (estructura territorial interna).

Antes operaba sobre el modelo obsoleto Organizacion (categoria INTERNA).
Reconducido a UnidadOrganizativa, que es ahora la estructura territorial
canonica de la asociacion (incluidas delegaciones con personalidad juridica,
distinguidas por su vinculo FILIAL/FEDERADA).
"""

from sqlalchemy import select

from app.modules.core.geografico.direccion import UnidadOrganizativa


class UnidadOrganizativaQuery:
    """Helper para queries de agrupaciones territoriales."""

    @staticmethod
    def get_base_query():
        """Query base: unidades organizativas no eliminadas."""
        return select(UnidadOrganizativa).where(
            UnidadOrganizativa.eliminado == False  # noqa: E712
        )

    @staticmethod
    def get_activas():
        """Devuelve query de agrupaciones activas."""
        return UnidadOrganizativaQuery.get_base_query().where(
            UnidadOrganizativa.activo == True  # noqa: E712
        )

    @staticmethod
    def get_por_provincia(provincia_id):
        """Filtra agrupaciones de una provincia."""
        return UnidadOrganizativaQuery.get_base_query().where(
            UnidadOrganizativa.provincia_id == provincia_id
        )

    @staticmethod
    def get_jerarquia_completa():
        """Devuelve todas las agrupaciones ordenadas por nombre."""
        return UnidadOrganizativaQuery.get_base_query().order_by(
            UnidadOrganizativa.nombre
        )
