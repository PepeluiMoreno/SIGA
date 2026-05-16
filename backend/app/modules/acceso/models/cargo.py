"""Catálogo de cargos orgánicos y su mapeo a roles de sistema."""

import uuid
from typing import Optional, List

from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.base_model import BaseModel


class Cargo(BaseModel):
    """Cargo orgánico de la organización (Director de Campaña, Coordinador, Secretario...).

    Un cargo es independiente del nivel territorial donde se ejerce.
    Si tipo_unidad_id es NULL, el cargo puede existir en cualquier nivel.
    La instanciación territorial ocurre en HistorialNombramiento.agrupacion_id.
    """
    __tablename__ = "cargos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Si NULL, el cargo existe en cualquier nivel organizativo
    tipo_unidad_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('niveles_organizativos.id', ondelete='SET NULL'),
        nullable=True, index=True
    )

    # Reglas de nombramiento
    puede_nominar_igual_nivel: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )
    requiere_aprobacion: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )
    # Qué cargo aprueba el nombramiento (NULL = coordinador del nivel superior)
    cargo_aprobador_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('cargos.id', ondelete='SET NULL'), nullable=True
    )

    # Límites
    max_simultaneos: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    duracion_maxima_meses: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    cargo_aprobador: Mapped[Optional["Cargo"]] = relationship(
        foreign_keys=[cargo_aprobador_id], remote_side="Cargo.id", lazy="selectin"
    )
    roles_sistema: Mapped[List["CargoRol"]] = relationship(
        back_populates="cargo", lazy="selectin", cascade="all, delete-orphan"
    )
    nombramientos: Mapped[List["HistorialNombramiento"]] = relationship(
        back_populates="cargo", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Cargo('{self.nombre}')>"


class CargoRol(BaseModel):
    """Mapeo entre un cargo orgánico y los roles de sistema que otorga."""
    __tablename__ = "cargos_roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cargo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('cargos.id', ondelete='CASCADE'), nullable=False, index=True
    )
    rol_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True
    )

    cargo: Mapped["Cargo"] = relationship(back_populates="roles_sistema", lazy="selectin")
    rol: Mapped["Rol"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<CargoRol(cargo='{self.cargo_id}', rol='{self.rol_id}')>"


from app.modules.acceso.models.rol import Rol  # noqa: E402,F401
from app.modules.membresia.models.historial_nombramiento import HistorialNombramiento  # noqa: E402,F401
