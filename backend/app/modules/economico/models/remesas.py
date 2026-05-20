"""Modelos relacionados con remesas SEPA y órdenes de cobro."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Uuid, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class Remesa(BaseModel):
    """Lote de cobros SEPA."""
    __tablename__ = "remesas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Identificación
    referencia: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    fecha_creacion: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False, index=True)
    fecha_envio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_cobro: Mapped[date] = mapped_column(Date, nullable=False)  # Fecha en la que se efectuará el cobro

    # Importes
    importe_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    gastos: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    num_ordenes: Mapped[int] = mapped_column(default=0, nullable=False)

    # Estado (FK a EstadoRemesa)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_remesa.id"), nullable=False, index=True)

    # Archivo SEPA
    archivo_sepa: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Path al archivo XML generado
    mensaje_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # ID del mensaje SEPA

    # Agrupación territorial (tesorería delegada)
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("unidades_organizativas.id"), nullable=True, index=True)

    # Tipo de remesa: ORDINARIA | EXTRAORDINARIA | REENVIO
    tipo_remesa: Mapped[str] = mapped_column(String(20), nullable=False, default="ORDINARIA", index=True)
    # Concepto libre — para extraordinarias y reenvíos
    concepto: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    # SEPA Sequence Type: FRST | RCUR | LAST | OOFF (norma EPC131-08)
    seq_tipo: Mapped[str] = mapped_column(String(4), nullable=False, default="RCUR")
    # Remesa origen (si es REENVIO, apunta a la remesa que tuvo los fallidos)
    remesa_origen_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("remesas.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    ordenes: Mapped[List["OrdenCobro"]] = relationship(back_populates="remesa", lazy="selectin")
    estado = relationship('EstadoRemesa', foreign_keys=[estado_id], lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', foreign_keys=[agrupacion_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<Remesa(referencia='{self.referencia}', estado_id='{self.estado_id}', importe={self.importe_total})>"

    @property
    def importe_neto(self) -> Decimal:
        """Calcula el importe neto después de gastos."""
        return self.importe_total - self.gastos

    def calcular_totales(self) -> None:
        """Recalcula los totales basándose en las órdenes."""
        if self.ordenes:
            self.importe_total = sum(orden.importe for orden in self.ordenes)
            self.num_ordenes = len(self.ordenes)

    def puede_enviarse(self) -> bool:
        """Verifica si la remesa puede enviarse al banco."""
        # TODO: Verificar estado_id contra estados 'BORRADOR' o 'GENERADA'
        return (
            # self.estado_id in [borrador_id, generada_id] and
            self.num_ordenes > 0 and
            self.archivo_sepa is not None
        )


class OrdenCobro(BaseModel):
    """Orden individual dentro de remesa SEPA."""
    __tablename__ = "ordenes_cobro"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    remesa_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("remesas.id"), nullable=False, index=True)
    cuota_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cuotas_anuales.id"), nullable=False, index=True)

    # Correlativo de la orden dentro de la remesa (D4.1):
    # forma el EndToEndId SEPA como f"{remesa.referencia}-{nseq:03d}"
    nseq: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    # Datos del cobro
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    referencia_mandato: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Referencia del mandato SEPA
    iban: Mapped[Optional[str]] = mapped_column(String(34), nullable=True)  # IBAN del miembro

    # Estado (FK a EstadoOrdenCobro)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_orden_cobro.id"), nullable=False, index=True)

    # Información de procesamiento
    fecha_procesamiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    codigo_rechazo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_rechazo: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relaciones
    remesa: Mapped["Remesa"] = relationship(back_populates="ordenes", lazy="selectin")
    cuota = relationship('CuotaAnual', foreign_keys=[cuota_id], back_populates='ordenes_cobro', lazy='selectin')
    estado = relationship('EstadoOrdenCobro', foreign_keys=[estado_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<OrdenCobro(cuota_id='{self.cuota_id}', importe={self.importe}, estado_id='{self.estado_id}')>"

    @property
    def end_to_end_id(self) -> str:
        """Identificador SEPA legible {referencia_remesa}-{nseq:03d} (D4.1).

        Requiere que la relación 'remesa' esté cargada (lazy='selectin' ya lo
        hace por defecto). Máx 35 caracteres (límite SEPA EndToEndIdentification).
        """
        ref = self.remesa.referencia if self.remesa else ""
        return f"{ref}-{self.nseq:03d}"

    @staticmethod
    def parse_end_to_end_id(value: str) -> tuple[str, int] | None:
        """Descompone un EndToEndId en (referencia_remesa, nseq). None si no encaja."""
        if not value or "-" not in value:
            return None
        ref, sep, nseq = value.rpartition("-")
        if not sep or not nseq.isdigit():
            return None
        return (ref, int(nseq))

    def marcar_procesada(self) -> None:
        """Marca la orden como procesada exitosamente."""
        # TODO: self.estado_id = # buscar estado 'PROCESADA'
        self.fecha_procesamiento = date.today()

    def marcar_fallida(self, codigo_rechazo: str, motivo: str, fecha_rechazo: Optional[date] = None) -> None:
        """Marca la orden como fallida con código SEPA y motivo."""
        # El estado_id lo cambia el servicio (necesita acceso a la sesión)
        self.fecha_procesamiento = date.today()
        self.fecha_rechazo = fecha_rechazo or date.today()
        self.codigo_rechazo = codigo_rechazo
        self.motivo_rechazo = motivo
