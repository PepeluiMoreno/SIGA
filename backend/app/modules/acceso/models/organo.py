"""Órganos de gobierno: tipo (catálogo + composición) e instancia por unidad.

Modelo de gobernanza (ver docs/arquitectura/GOBERNANZA.md):

- `TipoOrgano`   — catálogo configurable de tipos de órgano (Junta Directiva,
                   Asamblea General, Comisión…). Cada tipo declara su modo de
                   composición: por CARGOS (junta, comisión) o por PLENO (asamblea,
                   cuya membresía es el conjunto de socios con voto, sin cargos).
- `TipoOrganoCargo` — composición-plantilla de un tipo de órgano por CARGOS: qué
                   cargos lo forman y en qué orden protocolario. El orden vive aquí,
                   no en `Rol.nivel` (que pasa a ser autoridad pura).
- `Organo`       — instancia concreta de un tipo de órgano en una unidad, con su
                   periodo. Generaliza la antigua `JuntaDirectiva`.

El cargo es genérico y la composición cuelga del TIPO (plantilla reutilizable); el
territorio lo instancia el mandato (`HistorialNombramiento.agrupacion_id`), no el
órgano ni el cargo.
"""

import enum
import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.base_model import BaseModel


class ComposicionOrgano(str, enum.Enum):
    """Cómo se forma la membresía de un órgano.

    - CARGOS: el órgano se compone de cargos concretos (Junta Directiva: presidencia,
      secretaría, tesorería…). Tiene composición-plantilla (`TipoOrganoCargo`).
    - PLENO: órgano de composición abierta; su membresía es el pleno de socios con
      derecho a voto (Asamblea General). No tiene cargos ni plantilla; sus acuerdos
      se toman por quórum y votación.
    """

    CARGOS = "CARGOS"
    PLENO = "PLENO"


class TipoOrgano(BaseModel):
    """Tipo de órgano de gobierno (catálogo configurable)."""

    __tablename__ = "tipos_organo"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    nombre: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Denominación mostrada (configurable). Jubila `org.denominacion_organo_gobierno`.
    denominacion_singular: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    denominacion_plural: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    composicion: Mapped[ComposicionOrgano] = mapped_column(
        Enum(ComposicionOrgano, name="composicion_organo"),
        default=ComposicionOrgano.CARGOS,
        nullable=False,
    )

    # Protegido: los tipos sembrados por defecto no se borran (pero sí se editan).
    sistema: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Composición-plantilla (solo para composicion=CARGOS)
    composicion_cargos: Mapped[List["TipoOrganoCargo"]] = relationship(
        back_populates="tipo_organo", lazy="selectin", cascade="all, delete-orphan",
        order_by="TipoOrganoCargo.orden_protocolario",
    )
    organos: Mapped[List["Organo"]] = relationship(
        back_populates="tipo_organo", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<TipoOrgano('{self.nombre}', {self.composicion.value})>"


class TipoOrganoCargo(BaseModel):
    """Un cargo dentro de la composición de un tipo de órgano, con su orden protocolario."""

    __tablename__ = "tipos_organo_cargos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    tipo_organo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("tipos_organo.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    cargo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cargos.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    # Orden protocolario dentro del órgano (0 = primero). Antes vivía —mal— en Rol.nivel.
    orden_protocolario: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    tipo_organo: Mapped["TipoOrgano"] = relationship(back_populates="composicion_cargos", lazy="selectin")
    cargo: Mapped["Cargo"] = relationship(lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<TipoOrganoCargo(tipo={self.tipo_organo_id}, cargo={self.cargo_id}, orden={self.orden_protocolario})>"


class Organo(BaseModel):
    """Instancia de un órgano de gobierno en una unidad, con su periodo.

    Generaliza `JuntaDirectiva`: una junta directiva es un `Organo` cuyo
    `tipo_organo` es «Junta Directiva». Puede haber varias instancias en el tiempo
    (renovaciones), pero por convención solo una activa por (tipo, unidad).
    """

    __tablename__ = "organos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    tipo_organo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("tipos_organo.id", ondelete="RESTRICT"), nullable=False, index=True,
    )
    agrupacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("unidades_organizativas.id", ondelete="RESTRICT"), nullable=False, index=True,
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_constitucion: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_disolucion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tipo_organo: Mapped["TipoOrgano"] = relationship(back_populates="organos", lazy="selectin")
    agrupacion = relationship("UnidadOrganizativa", lazy="selectin")
    composicion: Mapped[List["OrganoCargo"]] = relationship(
        back_populates="organo", lazy="selectin", cascade="all, delete-orphan",
        order_by="OrganoCargo.orden_protocolario",
    )

    def __repr__(self) -> str:
        return f"<Organo(tipo={self.tipo_organo_id}, agrupacion={self.agrupacion_id}, activo={self.activo})>"


class OrganoCargo(BaseModel):
    """Composición REAL de un órgano concreto: qué cargos lo forman, con su orden.

    Se inicializa copiando la plantilla del tipo (`TipoOrganoCargo`) al crear el
    órgano, pero cada agrupación puede ajustarla después (añadir una vocalía,
    quitar un cargo…). La plantilla es el punto de partida, no una atadura.
    """

    __tablename__ = "organos_cargos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    organo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("organos.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    cargo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cargos.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    orden_protocolario: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    organo: Mapped["Organo"] = relationship(back_populates="composicion", lazy="selectin")
    cargo: Mapped["Cargo"] = relationship(lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<OrganoCargo(organo={self.organo_id}, cargo={self.cargo_id}, orden={self.orden_protocolario})>"
