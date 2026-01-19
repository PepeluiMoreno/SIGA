"""Modelos relacionados con cuotas anuales."""

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, ForeignKey, Date, Numeric, Enum, Text, Uuid, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class ModoIngreso(PyEnum):
    """Modos de ingreso de pagos."""
    SEPA = "SEPA"
    TRANSFERENCIA = "TRANSFERENCIA"
    PAYPAL = "PAYPAL"
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"


class ImporteCuotaAnio(BaseModel):
    """Importe de cuota por tipo de miembro y año (ejercicio).

    Permite definir cuotas diferentes según el tipo de miembro (socio, simpatizante, etc.)
    y mantener un histórico de cuotas por ejercicio.
    """
    __tablename__ = "importes_cuota_anio"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tipo_miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tipos_miembro.id"), nullable=False, index=True)
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    nombre_cuota: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Ej: "General", "Estudiante", "Parado"
    activo: Mapped[bool] = mapped_column(Integer, default=True, nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relación
    tipo_miembro = relationship('TipoMiembro', lazy='selectin')

    def __repr__(self) -> str:
        return f"<ImporteCuotaAnio(ejercicio={self.ejercicio}, tipo_miembro_id='{self.tipo_miembro_id}', importe={self.importe})>"


class CuotaAnual(BaseModel):
    """Cuota anual de un miembro (socio).

    Representa la cuota asignada a un miembro para un ejercicio específico.
    Mantiene histórico de todas las cuotas (pagadas y pendientes).
    """
    __tablename__ = "cuotas_anuales"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("miembros.id"), nullable=False, index=True)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    agrupacion_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("agrupaciones_territoriales.id"), nullable=False, index=True)

    # Relación con el importe de cuota definido para el tipo de miembro
    importe_cuota_anio_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("importes_cuota_anio.id"), nullable=True, index=True)

    # Importes
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    importe_pagado: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    gastos_gestion: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)

    # Estado (FK a EstadoCuota)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_cuota.id"), nullable=False, index=True)

    # Modo de pago
    modo_ingreso: Mapped[Optional[str]] = mapped_column(Enum(ModoIngreso), nullable=True)

    # Fechas
    fecha_pago: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Número de transacción, etc.

    # Relaciones
    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')
    agrupacion = relationship('AgrupacionTerritorial', foreign_keys=[agrupacion_id], lazy='selectin')
    importe_cuota_anio = relationship('ImporteCuotaAnio', foreign_keys=[importe_cuota_anio_id], lazy='selectin')
    estado = relationship('EstadoCuota', foreign_keys=[estado_id], lazy='selectin')
    ordenes_cobro = relationship('OrdenCobro', back_populates='cuota', lazy='selectin')

    def __repr__(self) -> str:
        return f"<CuotaAnual(miembro_id='{self.miembro_id}', ejercicio={self.ejercicio}, estado_id='{self.estado_id}')>"

    @property
    def esta_pagada(self) -> bool:
        """Verifica si la cuota está completamente pagada."""
        return self.importe_pagado >= self.importe

    @property
    def saldo_pendiente(self) -> Decimal:
        """Calcula el saldo pendiente de pago."""
        return self.importe - self.importe_pagado

    def registrar_pago(
        self,
        importe_pago: Decimal,
        modo_ingreso: ModoIngreso,
        fecha_pago: Optional[date] = None,
        referencia: Optional[str] = None
    ) -> None:
        """Registra un pago para la cuota."""
        self.importe_pagado += importe_pago
        self.modo_ingreso = modo_ingreso.value
        self.fecha_pago = fecha_pago or date.today()

        if referencia:
            self.referencia_pago = referencia

        # TODO: Actualizar estado requiere consultar EstadoCuota por código
        # if self.esta_pagada:
        #     self.estado_id = # buscar estado COBRADA
        # elif self.importe_pagado > 0:
        #     self.estado_id = # buscar COBRADA_PARCIAL o COBRADA
