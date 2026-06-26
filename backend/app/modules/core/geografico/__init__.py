"""Modelos del dominio geográfico."""

from .nivel_organizativo import AmbitoGeografico, NivelOrganizativo, NaturalezaUnidad, VinculoUnidad
from .direccion import Pais, Provincia, Municipio, Direccion, UnidadOrganizativa
from .entidad_geografica import EntidadGeografica
from .unidad_organizativa_view import UnidadOrganizativaVista

__all__ = [
    'AmbitoGeografico',
    'NivelOrganizativo',
    'NaturalezaUnidad',
    'VinculoUnidad',
    'Pais',
    'Provincia',
    'Municipio',
    'Direccion',
    'UnidadOrganizativa',
    'EntidadGeografica',
]
