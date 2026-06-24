"""Vinculacion: el lazo tipado y vigente entre contacto y organización.

Estructura:
- Vinculacion: el registro del vínculo (quién, tipo, cuándo, estado)
- Socio: satélite cuando tipo = SOCIO (datos económicos)
- Voluntario: satélite cuando tipo = VOLUNTARIO (datos de voluntariado)
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import BaseModel

if TYPE_CHECKING:
    from .contacto import Contacto
    from .tipo_vinculacion import TipoVinculacion


class Vinculacion(BaseModel):
    """El lazo tipado y vigente entre una persona/empresa y la organización.
    
    Attributes:
        contacto_id: FK a Contacto (persona física o jurídica)
        tipo_vinculacion_id: FK a TipoVinculacion (qué tipo de vínculo)
        fecha_inicio: cuándo se otorgó
        fecha_fin: cuándo se cerró (NULL = vigente)
        estado: 'activa', 'inactiva', 'cerrada'
        agrupacion_id: para vínculos territoriales
    """

    __tablename__ = "vinculaciones"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Núcleo
    contacto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contactos.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    tipo_vinculacion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tipos_vinculacion.id"), nullable=False, index=True
    )

    # Vigencia
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    estado: Mapped[str] = mapped_column(
        String(50), default="activa", nullable=False, index=True
    )  # activa, inactiva, cerrada

    # Contexto territorial (si aplica)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("unidades_organizativas.id"), nullable=True
    )

    # Relaciones
    contacto: Mapped[Contacto] = relationship(
        back_populates="vinculaciones",
        lazy="selectin"
    )
    tipo_vinculacion: Mapped[TipoVinculacion] = relationship(
        back_populates="vinculaciones",
        lazy="selectin"
    )
    socio: Mapped[Optional[Socio]] = relationship(
        back_populates="vinculacion",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="Socio.vinculacion_id"
    )
    voluntario: Mapped[Optional[Voluntario]] = relationship(
        back_populates="vinculacion",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="Voluntario.vinculacion_id"
    )

    def __repr__(self) -> str:
        tipo = self.tipo_vinculacion.codigo if self.tipo_vinculacion else "?"
        fin = f", fin={self.fecha_fin}" if self.fecha_fin else ""
        return f"<Vinculacion(contacto={self.contacto_id}, tipo={tipo}{fin})>"

    @property
    def vigente(self) -> bool:
        """Retorna True si la vinculación está actualmente vigente."""
        return self.fecha_fin is None and self.estado == "activa" and not self.eliminado


class Socio(BaseModel):
    """Satélite de Vinculacion: datos específicos del vínculo de socio.
    
    Guarda los datos económicos y administrativos propios del rol socio:
    número de socio, cuota, IBAN, formas de pago, motivos de baja, etc.
    """

    __tablename__ = "socios"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # FK a Vinculacion (1:1)
    vinculacion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vinculaciones.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    # Identidad de socio
    numero_socio: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True, index=True)

    # Cuota
    cuota_mensual: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    incremento_cuota: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    incremento_cuota_obs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Datos bancarios
    iban: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    swift_bic: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    forma_pago_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("formas_pago.id"), nullable=True
    )

    # Estado y motivos
    estado_socio: Mapped[str] = mapped_column(
        String(50), default="activo", nullable=False, index=True
    )  # activo, suspendido, baja
    es_honor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    motivo_reduccion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("motivos_reduccion_cuota.id"), nullable=True
    )
    motivo_baja_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("motivos_baja.id"), nullable=True
    )
    motivo_baja_texto: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relación
    vinculacion: Mapped[Vinculacion] = relationship(
        back_populates="socio",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        num = self.numero_socio or "?"
        return f"<Socio(numero={num}, estado={self.estado_socio})>"


class Voluntario(BaseModel):
    """Satélite de Vinculacion: datos específicos del vínculo de voluntario.
    
    Guarda disponibilidad, habilidades, intereses, capacidades (conducir, viajar…).
    """

    __tablename__ = "voluntarios"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # FK a Vinculacion (1:1)
    vinculacion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vinculaciones.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    # Disponibilidad
    disponibilidad: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    horas_disponibles_semana: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Perfil profesional
    profesion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    nivel_estudios_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("niveles_estudios.id"), nullable=True
    )

    # Experiencia e intereses
    experiencia_voluntariado: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    intereses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observaciones_voluntariado: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Capacidades
    puede_conducir: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vehiculo_propio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disponibilidad_viajar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relación
    vinculacion: Mapped[Vinculacion] = relationship(
        back_populates="voluntario",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        horas = self.horas_disponibles_semana or "?"
        return f"<Voluntario(horas_semana={horas})>"
