"""Modelos de convenios institucionales y delegaciones de firma.

Gestiona los acuerdos de colaboración firmados por la asociación
y los poderes/delegaciones de representación del Presidente.
"""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Boolean, Uuid, ForeignKey, Date, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel, InmutableMixin


class TipoConvenio(InmutableMixin, BaseModel):
    """Catálogo de tipos de convenio."""
    __tablename__ = 'sec_tipos_convenio'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    convenios = relationship('ConvenioInstitucional', back_populates='tipo_convenio', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoConvenio(nombre='{self.nombre}')>"


class ConvenioInstitucional(BaseModel):
    """ConvenioInstitucional o acuerdo firmado con una entidad externa.

    Incluye adhesiones a redes y plataformas, acuerdos de colaboración,
    contratos de servicios con obligaciones derivadas, etc.
    """
    __tablename__ = 'sec_convenios'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    tipo_convenio_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_tipos_convenio.id'), nullable=False, index=True
    )

    # Identificación
    referencia: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True,
        comment="Código interno: CONV-2025-001"
    )
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)

    # Contraparte
    entidad_contraparte: Mapped[str] = mapped_column(String(300), nullable=False)
    nif_contraparte: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Vigencia
    fecha_firma: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    renovacion_automatica: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dias_preaviso_no_renovacion: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Estado
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default='VIGENTE', index=True
    )  # VIGENTE | VENCIDO | RESCINDIDO | SUSPENDIDO

    # Contenido
    objeto: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    obligaciones_asociacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    obligaciones_contraparte: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Firmante por parte de la asociación
    firmante_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True
    )

    # Acuerdo de Junta que autoriza el convenio
    acuerdo_autorizacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('sec_acuerdos.id'), nullable=True
    )

    ruta_documento: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    tipo_convenio = relationship('TipoConvenio', back_populates='convenios', lazy='selectin')
    firmante = relationship('Miembro', foreign_keys=[firmante_id], lazy='selectin')
    acuerdo_autorizacion = relationship('Acuerdo', foreign_keys=[acuerdo_autorizacion_id])

    def __repr__(self) -> str:
        return f"<ConvenioInstitucional(referencia='{self.referencia}', estado='{self.estado}')>"


class DelegacionFirma(BaseModel):
    """Delegación de representación o poder de firma del Presidente.

    Registra quién está autorizado para actuar en nombre de la
    asociación, para qué actos y durante qué período.
    """
    __tablename__ = 'sec_delegaciones_firma'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Delegante (normalmente el Presidente)
    delegante_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=False, index=True
    )
    # Delegado
    delegado_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=False, index=True
    )

    # Alcance
    descripcion_actos: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Descripción de los actos para los que se delega"
    )
    limite_importe: Mapped[Optional[float]] = mapped_column(
        # Numeric(12, 2)
        # usando float por compatibilidad con el resto del proyecto
        nullable=True,
        comment="Límite económico de la delegación en euros (null = sin límite)"
    )

    # Vigencia
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Acuerdo de Junta que autoriza la delegación
    acuerdo_autorizacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('sec_acuerdos.id'), nullable=True
    )

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    delegante = relationship('Miembro', foreign_keys=[delegante_id], lazy='selectin')
    delegado = relationship('Miembro', foreign_keys=[delegado_id], lazy='selectin')
    acuerdo_autorizacion = relationship('Acuerdo', foreign_keys=[acuerdo_autorizacion_id])

    def __repr__(self) -> str:
        return f"<DelegacionFirma(delegado_id='{self.delegado_id}', activa={self.activa})>"
