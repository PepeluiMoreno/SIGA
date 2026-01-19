"""Mixins reutilizables para modelos."""

from .contacto_mixin import ContactoMixin, ContactoCompletoMixin
from .sistema_mixin import RegistroSistemaMixin, CatalogoMixin

__all__ = [
    "ContactoMixin",
    "ContactoCompletoMixin",
    "RegistroSistemaMixin",
    "CatalogoMixin",
]
