"""Órganos de gobierno: catálogo de tipos, modelo por NIVEL, e instancias.

Modelo de gobernanza (ver docs/arquitectura/GOBERNANZA.md). Distingue con nitidez
lo que es **configuración** (el modelo organizativo) de lo que es **poblamiento**
(las instancias reales de cada agrupación):

CONFIGURACIÓN — se define por NIVEL territorial, no por agrupación concreta:
- `TipoOrgano`      — catálogo puro de tipos (Junta Directiva, Asamblea, Comisión).
                      Declara su modo de composición: CARGOS (junta, comisión) o
                      PLENO (asamblea: su membresía es el pleno de socios con voto).
                      NO lleva composición: la misma «Junta Directiva» se compone
                      distinto en una Delegación que en un Grupo Local.
- `NivelOrgano`     — qué órganos tiene un NIVEL («el nivel Delegación tiene una
                      Junta Directiva y una Asamblea»).
- `NivelOrganoCargo`— composición de ese órgano EN ESE NIVEL: qué cargos lo forman
                      y en qué orden protocolario. El orden vive aquí, no en
                      `Rol.nivel` (que pasa a ser autoridad pura).

POBLAMIENTO — instancias reales, se ven en la ficha de la agrupación:
- `Organo`          — el órgano concreto de una agrupación («la Junta de Madrid»),
                      con su periodo. Generaliza la antigua `JuntaDirectiva`.
- `OrganoCargo`     — su composición real, inicializada desde el modelo del nivel y
                      ajustable por esa agrupación.

El cargo es genérico; el territorio lo instancia el mandato
(`HistorialNombramiento.agrupacion_id`), no el órgano ni el cargo.
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

    organos: Mapped[List["Organo"]] = relationship(
        back_populates="tipo_organo", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<TipoOrgano('{self.nombre}', {self.composicion.value})>"


# ── CONFIGURACIÓN: el modelo organizativo de cada NIVEL ──────────────────────

class NivelOrgano(BaseModel):
    """Un órgano que corresponde a un NIVEL territorial.

    «El nivel *Delegación* tiene una Junta Directiva y una Asamblea». Es
    configuración, no poblamiento: no habla de agrupaciones concretas. Al crear una
    agrupación de ese nivel se instancian sus órganos con esta composición.
    """

    __tablename__ = "niveles_organos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    nivel_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("niveles_organizativos.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    tipo_organo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("tipos_organo.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tipo_organo: Mapped["TipoOrgano"] = relationship(lazy="selectin")
    composicion: Mapped[List["NivelOrganoCargo"]] = relationship(
        back_populates="nivel_organo", lazy="selectin", cascade="all, delete-orphan",
        order_by="NivelOrganoCargo.orden_protocolario",
    )

    def __repr__(self) -> str:
        return f"<NivelOrgano(nivel={self.nivel_id}, tipo={self.tipo_organo_id})>"


class NivelOrganoCargo(BaseModel):
    """Composición del órgano de un nivel: qué cargos lo forman, con su orden.

    La misma «Junta Directiva» puede componerse distinto en una Delegación que en un
    Grupo Local; por eso la composición cuelga del NIVEL, no del tipo.
    """

    __tablename__ = "niveles_organos_cargos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    nivel_organo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("niveles_organos.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    cargo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cargos.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    # Orden protocolario dentro del órgano (0 = primero). Antes vivía —mal— en Rol.nivel.
    orden_protocolario: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    nivel_organo: Mapped["NivelOrgano"] = relationship(back_populates="composicion", lazy="selectin")
    cargo: Mapped["Cargo"] = relationship(lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<NivelOrganoCargo(nivel_organo={self.nivel_organo_id}, cargo={self.cargo_id}, orden={self.orden_protocolario})>"


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
