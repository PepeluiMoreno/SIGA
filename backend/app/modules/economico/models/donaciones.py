"""Modelos relacionados con donaciones."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, Date, Numeric, Boolean, Text, Uuid, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel
from .cuotas import ModoIngreso


class DonacionConcepto(BaseModel):
    """Conceptos de donación predefinidos."""
    __tablename__ = "donaciones_conceptos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    donaciones = relationship('Donacion', back_populates='concepto', lazy='selectin')

    def __repr__(self) -> str:
        return f"<DonacionConcepto(nombre='{self.nombre}')>"


class Donacion(BaseModel):
    """Satélite de Participacion: donación de un contacto.

    Reconducida al modelo Contacto/Participacion: el antiguo miembro_id pasa a
    contacto_id (FK real), y los campos de donante-externo desaparecen (un
    externo es ahora un Contacto creado al vuelo). Engancha a Participacion 1:1.
    """
    __tablename__ = "donaciones"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    participacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("participaciones.id", ondelete="CASCADE"),
        nullable=True, unique=True, index=True
    )
    contacto_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("contactos.id"), nullable=True, index=True
    )
    concepto_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("donaciones_conceptos.id"), nullable=True, index=True)
    campania_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)  # TODO: ForeignKey("campanias.id")

    # Tipo y carácter (D6.5)
    tipo: Mapped[str] = mapped_column(String(15), nullable=False, default="DINERARIA")
    caracter: Mapped[str] = mapped_column(String(15), nullable=False, default="PUNTUAL")

    # Donación en especie
    descripcion_especie: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    valoracion: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    documento_valoracion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Importes
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    gastos: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)

    # Información de pago
    fecha: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False, index=True)
    modo_ingreso: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cuenta_bancaria_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("cuentas_bancarias.id"), nullable=True, index=True
    )

    # Estado (FK a EstadoDonacion)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_donacion.id"), nullable=False, index=True)

    # Certificado fiscal
    certificado_emitido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_certificado: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    numero_certificado: Mapped[Optional[str]] = mapped_column(String(30), unique=True, nullable=True)

    # Contabilidad generada (D6.2)
    apunte_caja_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("apuntes_caja.id"), nullable=True, index=True
    )
    asiento_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("asientos_contables.id"), nullable=True, index=True
    )

    # Tesorería delegada
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("unidades_organizativas.id"), nullable=True, index=True
    )

    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    anonima: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relaciones
    contacto = relationship('Contacto', foreign_keys=[contacto_id], lazy='selectin')
    participacion = relationship('Participacion', back_populates='donacion', foreign_keys=[participacion_id], lazy='selectin')
    concepto = relationship('DonacionConcepto', back_populates='donaciones', lazy='selectin')
    # campania: pendiente de aplicar FK de SQL_PENDIENTE.md Lote 9
    estado = relationship('EstadoDonacion', foreign_keys=[estado_id], lazy='selectin')
    cuenta_bancaria = relationship('CuentaBancaria', foreign_keys=[cuenta_bancaria_id], lazy='selectin')
    apunte_caja = relationship('ApunteCaja', foreign_keys=[apunte_caja_id], lazy='selectin')
    asiento = relationship('AsientoContable', foreign_keys=[asiento_id], lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', foreign_keys=[agrupacion_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<Donacion(importe={self.importe}, fecha={self.fecha}, estado_id='{self.estado_id}')>"

    @property
    def importe_neto(self) -> Decimal:
        """Calcula el importe neto después de gastos."""
        return self.importe - self.gastos

    @property
    def es_deducible(self) -> bool:
        """Verifica si la donación es deducible fiscalmente."""
        # Deducible si está asociada a un contacto identificado y no es anónima
        return bool(self.contacto_id and not self.anonima)

    def emitir_certificado(self) -> None:
        """Marca la donación como certificada."""
        if not self.certificado_emitido:
            self.certificado_emitido = True
            self.fecha_certificado = date.today()
            # TODO: self.estado_id = # buscar estado 'CERTIFICADA'
