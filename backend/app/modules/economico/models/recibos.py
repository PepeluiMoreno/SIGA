"""Modelo Recibo: justificante numerado del cobro de cuotas y otros conceptos.

El recibo es el documento formal numerado correlativamente (REC-YYYY-NNNNN)
que justifica un cobro. Da soporte a:
- Cuotas ordinarias (cuota anual de socio)
- Cuotas extraordinarias (derramas, congresales, formación...)
- Reenvíos tras fallido SEPA (con SeqTp=FRST en la remesa)

Cumplimiento: Código de Comercio art. 25; PCESFL 2013 norma 1ª (imagen fiel).
"""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Uuid, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class Recibo(BaseModel):
    """Recibo numerado emitido a un miembro como justificante de cobro."""
    __tablename__ = "recibos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Numeración correlativa REC-YYYY-NNNNN
    numero_recibo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Tipo: CUOTA_ORDINARIA | EXTRAORDINARIA | REENVIO
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="CUOTA_ORDINARIA")
    concepto: Mapped[str] = mapped_column(String(300), nullable=False)

    # Destinatario y vinculaciones
    vinculacion_socio_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("vinculaciones.id"), nullable=False, index=True)
    cuota_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("cuotas_anuales.id", ondelete="SET NULL"), nullable=True, index=True
    )
    orden_cobro_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("ordenes_cobro.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Agrupación territorial responsable (D2.3 — prefija el número de recibo)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("unidades_organizativas.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Importes
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    importe_pagado: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)

    # Estado: EMITIDO | COBRADO | FALLIDO | ANULADO
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="EMITIDO", index=True)

    # Modo de cobro: SEPA | TRANSFERENCIA | MANUAL | EFECTIVO | TARJETA
    modo_cobro: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Fechas
    fecha_emision: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_cobro: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Trazabilidad del aviso al socio cuando el recibo queda FALLIDO (D4.3)
    fecha_aviso_fallido: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    plantilla_email_aviso_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("plantillas_email.id", ondelete="SET NULL"), nullable=True
    )

    # Relaciones
    vinculacion_socio = relationship("Vinculacion", foreign_keys=[vinculacion_socio_id], lazy="selectin")
    cuota = relationship("CuotaAnual", foreign_keys=[cuota_id], lazy="selectin")
    orden_cobro = relationship("OrdenCobro", foreign_keys=[orden_cobro_id], lazy="selectin")
    plantilla_email_aviso = relationship("PlantillaEmail", foreign_keys=[plantilla_email_aviso_id], lazy="selectin")
    agrupacion = relationship("UnidadOrganizativa", foreign_keys=[agrupacion_id], lazy="selectin")

    def __repr__(self) -> str:
        return f"<Recibo(numero='{self.numero_recibo}', estado='{self.estado}', importe={self.importe})>"

    @property
    def importe_pendiente(self) -> Decimal:
        return self.importe - self.importe_pagado

    @property
    def esta_cobrado(self) -> bool:
        return self.estado == "COBRADO"
