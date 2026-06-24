"""Participacion: actos discretos que un contacto realiza en la organización.

Estructura joined-table: tabla base `Participacion` + satélites especializados.
Cada participación otorga/mantiene una vinculación del tipo correspondiente.

IMPORTANTE: los satélites NO se definen todos aquí. Solo la base y `Membresia`
(que no tiene tabla de dominio previa) viven en este fichero. Los demás satélites
son tablas de dominio ricas que ya existen y se reconducen en sus módulos:
  - firmas_campania       -> actividades/models/campana.py
  - donaciones            -> economico/models (rica: fiscal, contable, remesas)
  - convenios             -> secretaria/organizaciones
  - asistencias_actividad -> actividades/models/actividad.py

Todos enganchan a Participacion via participacion_id (1:1) y declaran su
back_populates correspondiente.

Tipos (discriminador `tipo`): FIRMA | DONACION | VOLUNTARIADO | MEMBRESIA | CONVENIO | ASISTENCIA
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.base_model import BaseModel

if TYPE_CHECKING:
    from .contacto import Contacto


class Participacion(BaseModel):
    """Base de participacion: acto discreto que otorga/mantiene una vinculacion.

    Cada tipo especializado cuelga como satelite 1:1 (en su modulo de dominio).
    """

    __tablename__ = "participaciones"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    contacto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contactos.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    fecha: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )
    estado: Mapped[str] = mapped_column(
        String(50), default="registrada", nullable=False, index=True
    )

    contacto: Mapped["Contacto"] = relationship(
        back_populates="participaciones", lazy="selectin"
    )

    # Satelites 1:1 (definidos en sus modulos de dominio).
    membresia: Mapped[Optional["Membresia"]] = relationship(
        "Membresia", back_populates="participacion", uselist=False,
        cascade="all, delete-orphan", lazy="selectin",
        foreign_keys="Membresia.participacion_id",
    )
    firma_campania: Mapped[Optional["FirmaCampania"]] = relationship(
        "FirmaCampania", back_populates="participacion", uselist=False,
        cascade="all, delete-orphan", lazy="selectin",
        foreign_keys="FirmaCampania.participacion_id",
    )
    donacion: Mapped[Optional["Donacion"]] = relationship(
        "Donacion", back_populates="participacion", uselist=False,
        cascade="all, delete-orphan", lazy="selectin",
        foreign_keys="Donacion.participacion_id",
    )
    convenio: Mapped[Optional["Convenio"]] = relationship(
        "Convenio", back_populates="participacion", uselist=False,
        cascade="all, delete-orphan", lazy="selectin",
        foreign_keys="Convenio.participacion_id",
    )
    asistencia_actividad: Mapped[Optional["AsistenciaActividad"]] = relationship(
        "AsistenciaActividad", back_populates="participacion", uselist=False,
        cascade="all, delete-orphan", lazy="selectin",
        foreign_keys="AsistenciaActividad.participacion_id",
    )

    def __repr__(self) -> str:
        return f"<Participacion(contacto={self.contacto_id}, tipo={self.tipo}, fecha={self.fecha})>"


class Membresia(BaseModel):
    """Especializacion: alta (o reafiliacion) de un contacto como socio.

    Es el ACTO de darse de alta. No confundir con el satelite `Socio` de la
    vinculacion (que guarda los datos vigentes de cuota, IBAN, etc.).
    Cada alta abre/reactiva la vinculacion de tipo SOCIO.
    """

    __tablename__ = "membresias"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    participacion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("participaciones.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )

    tipo_miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("tipos_miembro.id"), nullable=True
    )
    numero_socio: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, unique=True, index=True
    )

    participacion: Mapped["Participacion"] = relationship(
        back_populates="membresia", lazy="selectin"
    )
    tipo_miembro = relationship(
        "TipoMiembro", foreign_keys=[tipo_miembro_id], lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Membresia(participacion={self.participacion_id}, numero_socio={self.numero_socio})>"
