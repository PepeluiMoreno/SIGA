"""
Mixin de datos de contacto reutilizable.

Este mixin proporciona campos de contacto estándar para:
- Organizaciones (agrupaciones territoriales, asociaciones)
- Miembros
- Voluntarios
- Cualquier entidad que necesite información de contacto
"""

import uuid
from typing import Optional

from sqlalchemy import String, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, declared_attr, relationship


class ContactoMixin:
    """
    Mixin que proporciona campos de contacto completos.

    Incluye:
    - Ubicación geográfica (país, provincia, municipio, dirección)
    - Datos de contacto (email, teléfonos, web)
    """

    # Ubicación geográfica
    @declared_attr
    def pais_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            Uuid,
            ForeignKey('paises.id'),
            nullable=False,
            index=True
        )

    @declared_attr
    def provincia_id(cls) -> Mapped[Optional[uuid.UUID]]:
        return mapped_column(
            Uuid,
            ForeignKey('provincias.id'),
            nullable=True,
            index=True
        )

    @declared_attr
    def municipio_id(cls) -> Mapped[Optional[uuid.UUID]]:
        return mapped_column(
            Uuid,
            ForeignKey('municipios.id'),
            nullable=True,
            index=True
        )

    @declared_attr
    def direccion_id(cls) -> Mapped[Optional[uuid.UUID]]:
        return mapped_column(
            Uuid,
            ForeignKey('direcciones.id'),
            nullable=True
        )

    # Datos de contacto
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    telefono_fijo: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    telefono_movil: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    web: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    # Relaciones (deben definirse en el modelo que usa el mixin)
    # pais = relationship('Pais', lazy='selectin')
    # provincia = relationship('Provincia', lazy='selectin')
    # municipio = relationship('Municipio', lazy='selectin')
    # direccion = relationship('Direccion', lazy='selectin')

    @property
    def telefono_principal(self) -> Optional[str]:
        """Devuelve el teléfono principal (móvil preferente, sino fijo)."""
        return self.telefono_movil or self.telefono_fijo

    @property
    def tiene_telefono(self) -> bool:
        """Verifica si tiene al menos un teléfono."""
        return bool(self.telefono_movil or self.telefono_fijo)

    @property
    def email_valido(self) -> bool:
        """Verifica si tiene un email válido (simplificado)."""
        if not self.email:
            return False
        return '@' in self.email and '.' in self.email.split('@')[1]


class ContactoCompletoMixin(ContactoMixin):
    """
    Extensión del ContactoMixin con datos de persona de contacto.

    Útil para organizaciones externas, proveedores, etc.
    donde necesitas los datos de una persona específica de contacto.
    """

    persona_contacto_nombre: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )

    persona_contacto_cargo: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    persona_contacto_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    persona_contacto_telefono: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    @property
    def tiene_persona_contacto(self) -> bool:
        """Verifica si tiene datos de persona de contacto."""
        return bool(
            self.persona_contacto_nombre or
            self.persona_contacto_email or
            self.persona_contacto_telefono
        )
