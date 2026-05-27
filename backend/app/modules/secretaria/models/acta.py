"""Modelos de actas y certificados de acuerdos.

El Acta es el documento oficial de cada reunión. El CertificadoAcuerdo
es el extracto que se emite a terceros (bancos, registros, organismos).
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Boolean, Uuid, ForeignKey, Date, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class Acta(BaseModel):
    """Acta oficial de una reunión.

    Numeración correlativa por tipo de órgano y año.
    Estado: BORRADOR → APROBADA → FIRMADA
    """
    __tablename__ = 'sec_actas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    reunion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_reuniones.id', ondelete='RESTRICT'),
        nullable=False, unique=True, index=True
    )

    # Numeración
    numero: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Número correlativo por tipo de órgano y año"
    )
    anio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Contenido
    texto_acta: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Texto completo del acta (puede generarse desde los datos estructurados)"
    )

    # Aprobación — estado por catálogo `estados_acta` + snapshot del código
    estado_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('estados_acta.id'), nullable=True, index=True,
    )
    estado_codigo: Mapped[str] = mapped_column(
        String(30), nullable=False, default='BORRADOR', index=True,
        comment='BORRADOR | APROBADA | FIRMADA (snapshot del catálogo)',
    )
    fecha_aprobacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    reunion_aprobacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('sec_reuniones.id'), nullable=True,
        comment="Reunión en la que se aprobó esta acta (normalmente la siguiente)"
    )

    # Firmantes
    secretario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True
    )
    presidente_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True
    )
    fecha_firma: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Documento generado
    ruta_pdf: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relaciones
    reunion = relationship('Reunion', foreign_keys=[reunion_id], back_populates='acta')
    reunion_aprobacion = relationship('Reunion', foreign_keys=[reunion_aprobacion_id])
    secretario = relationship('Miembro', foreign_keys=[secretario_id], lazy='selectin')
    presidente = relationship('Miembro', foreign_keys=[presidente_id], lazy='selectin')
    certificados = relationship('CertificadoAcuerdo', back_populates='acta', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Acta(numero={self.numero}, anio={self.anio}, estado='{self.estado_codigo}')>"


class CertificadoAcuerdo(BaseModel):
    """Certificado de un acuerdo concreto emitido a terceros.

    El secretario extrae un acuerdo del acta y lo certifica
    para presentarlo ante bancos, registros u organismos públicos.
    """
    __tablename__ = 'sec_certificados_acuerdo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    acta_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_actas.id', ondelete='RESTRICT'),
        nullable=False, index=True
    )
    acuerdo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_acuerdos.id', ondelete='RESTRICT'),
        nullable=False, index=True
    )

    # Número de certificado (correlativo independiente)
    numero_certificado: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True,
        comment="Ej: CERT-2025-042"
    )

    fecha_emision: Mapped[date] = mapped_column(Date, nullable=False)

    # Destinatario
    destinatario: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    proposito: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Texto certificado (copia literal del acuerdo con fórmulas legales)
    texto_certificado: Mapped[str] = mapped_column(Text, nullable=False)

    # Firmantes
    secretario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True
    )
    presidente_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True
    )

    ruta_pdf: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relaciones
    acta = relationship('Acta', back_populates='certificados')
    acuerdo = relationship('Acuerdo', back_populates='certificados')
    secretario = relationship('Miembro', foreign_keys=[secretario_id], lazy='selectin')
    presidente = relationship('Miembro', foreign_keys=[presidente_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<CertificadoAcuerdo(numero='{self.numero_certificado}')>"
