"""Modelos relacionados con cuotas anuales."""

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, ForeignKey, Date, Numeric, Enum, Text, Uuid, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class ModoIngreso(PyEnum):
    """Modos de ingreso de pagos."""
    SEPA = "SEPA"
    TRANSFERENCIA = "TRANSFERENCIA"
    PAYPAL = "PAYPAL"
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"


class MotivoReduccionCuota(BaseModel):
    """Catálogo de motivos por los que se rebaja la cuota base (Flujo 1, D1.1).

    El importe efectivo se calcula como `importe_base × (1 − %reduccion/100)`.
    Si `porcentaje_reduccion >= 100`, los miembros con ese motivo quedan
    **excluidos del proceso** (D1.4): no se genera CuotaAnual para ellos.
    """
    __tablename__ = "motivos_reduccion_cuota"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    porcentaje_reduccion: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<MotivoReduccionCuota({self.codigo}: -{self.porcentaje_reduccion}%)>"

    @property
    def excluye_cuota(self) -> bool:
        """Regla D1.4: % >= 100 significa 'no se genera CuotaAnual'."""
        return self.porcentaje_reduccion >= Decimal("100.00")

    def aplicar_a(self, importe_base: Decimal) -> Decimal:
        """Devuelve el importe efectivo tras aplicar la reducción."""
        factor = (Decimal("100") - self.porcentaje_reduccion) / Decimal("100")
        return (importe_base * factor).quantize(Decimal("0.01"))


class ImporteCuotaAnio(BaseModel):
    """Importe de cuota por tipo de miembro y año (ejercicio).

    Permite definir cuotas diferentes según el tipo de miembro (miembro, simpatizante, etc.)
    y mantener un histórico de cuotas por ejercicio.
    """
    __tablename__ = "importes_cuota_anio"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    codigo_cuota: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # General, Joven, Parado, Honorario
    tipo_miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("tipos_miembro.id"), nullable=True, index=True)
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    nombre_cuota: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relación
    tipo_miembro = relationship('TipoMiembro', lazy='selectin')

    def __repr__(self) -> str:
        return f"<ImporteCuotaAnio(ejercicio={self.ejercicio}, tipo_miembro_id='{self.tipo_miembro_id}', importe={self.importe})>"


class CuotaAnual(BaseModel):
    """Cuota anual de un miembro (miembro).

    Representa la cuota asignada a un miembro para un ejercicio específico.
    Mantiene histórico de todas las cuotas (pagadas y pendientes).
    """
    __tablename__ = "cuotas_anuales"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("miembros.id"), nullable=False, index=True)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    agrupacion_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("unidades_organizativas.id"), nullable=False, index=True)

    # Relación con el importe de cuota definido para el tipo de miembro
    importe_cuota_anio_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("importes_cuota_anio.id"), nullable=True, index=True)
    codigo_cuota: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # tarifa aplicada: General, Joven, etc.

    # Importes
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    importe_pagado: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    gastos_gestion: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)

    # Estado (FK a EstadoCuota)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("estados_cuota.id"), nullable=False, index=True)

    # Modo de pago
    modo_ingreso: Mapped[Optional[ModoIngreso]] = mapped_column(Enum(ModoIngreso), nullable=True)

    # Fechas
    fecha_pago: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Número de transacción, etc.

    # Snapshot del motivo de reducción aplicado al generar la cuota (D1.1, D1.2)
    motivo_reduccion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('motivos_reduccion_cuota.id', ondelete='SET NULL'), nullable=True, index=True
    )

    # Relaciones
    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', foreign_keys=[agrupacion_id], lazy='selectin')
    importe_cuota_anio = relationship('ImporteCuotaAnio', foreign_keys=[importe_cuota_anio_id], lazy='selectin')
    estado = relationship('EstadoCuota', foreign_keys=[estado_id], lazy='selectin')
    ordenes_cobro = relationship('OrdenCobro', back_populates='cuota', lazy='selectin')
    motivo_reduccion = relationship('MotivoReduccionCuota', foreign_keys=[motivo_reduccion_id], lazy='selectin')
    # Apuntes de caja directamente vinculados (pagos manuales/directos).
    # Para pagos via remesa el enlace es indirecto: OrdenCobro → Remesa → ApunteCaja.
    apuntes_caja = relationship(
        'ApunteCaja',
        foreign_keys='ApunteCaja.cuota_id',
        lazy='selectin',
    )

    def __repr__(self) -> str:
        return f"<CuotaAnual(miembro_id='{self.miembro_id}', ejercicio={self.ejercicio}, estado_id='{self.estado_id}')>"

    @property
    def importe_pagado_real(self) -> Decimal:
        """Importe pagado derivado de apuntes de caja vinculados (fuente de verdad).

        Recorre los ApunteCaja directamente ligados a esta cuota (cuota_id).
        Falls back a importe_pagado (campo cache) si los apuntes no están cargados.
        """
        try:
            return sum(
                (a.importe for a in self.apuntes_caja if a.es_ingreso),
                Decimal("0.00"),
            )
        except Exception:
            return self.importe_pagado

    @property
    def esta_pagada(self) -> bool:
        """Verifica si la cuota está completamente pagada."""
        return self.importe_pagado >= self.importe

    @property
    def saldo_pendiente(self) -> Decimal:
        """Calcula el saldo pendiente de pago."""
        return self.importe - self.importe_pagado


class SolicitudReduccionCuota(BaseModel):
    """Solicitud de un miembro para que se le aplique una reduccion de cuota.

    El miembro NO fija su reduccion directamente: la solicita aportando un
    documento acreditativo (tarjeta de desempleo, carne de estudiante, etc.).
    El tesorero (local o general) la aprueba o rechaza.

    Flujo de estados (directo, sin paso intermedio):
        PRESENTADA -> APROBADA   (tesorero acepta; fija Miembro.motivo_reduccion_id)
                   -> RECHAZADA  (tesorero rechaza, con motivo)
                   -> ANULADA    (el propio socio la retira mientras este PRESENTADA)
    """
    __tablename__ = "solicitudes_reduccion_cuota"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Quien la presenta
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("miembros.id"), nullable=False, index=True
    )

    # Motivo de reduccion solicitado (del catalogo MotivoReduccionCuota)
    motivo_reduccion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("motivos_reduccion_cuota.id"), nullable=False, index=True
    )

    # Ejercicio para el que se solicita (por defecto, el del alta de la solicitud)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Estado del flujo: PRESENTADA | APROBADA | RECHAZADA | ANULADA
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PRESENTADA", index=True)

    # Texto explicativo del solicitante
    texto_solicitud: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    fecha_presentacion: Mapped[date] = mapped_column(Date, nullable=False)

    # Resolucion (tesorero)
    resuelto_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("miembros.id"), nullable=True, index=True
    )
    fecha_resolucion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    miembro = relationship("Miembro", foreign_keys=[miembro_id], lazy="selectin")
    motivo_reduccion = relationship("MotivoReduccionCuota", foreign_keys=[motivo_reduccion_id], lazy="selectin")
    resolutor = relationship("Miembro", foreign_keys=[resuelto_por_id], lazy="selectin")
    documentos = relationship(
        "SolicitudReduccionCuotaDocumento",
        back_populates="solicitud",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<SolicitudReduccionCuota(miembro_id={self.miembro_id}, estado={self.estado})>"

    @property
    def puede_resolverse(self) -> bool:
        """El tesorero solo aprueba/rechaza mientras este PRESENTADA."""
        return self.estado == "PRESENTADA"

    @property
    def puede_anularse(self) -> bool:
        """El solicitante solo puede retirarla mientras este PRESENTADA."""
        return self.estado == "PRESENTADA"


class SolicitudReduccionCuotaDocumento(BaseModel):
    """Documento acreditativo adjunto a una solicitud de reduccion de cuota."""
    __tablename__ = "solicitudes_reduccion_cuota_documento"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    solicitud_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("solicitudes_reduccion_cuota.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    tamano_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    solicitud = relationship(
        "SolicitudReduccionCuota", foreign_keys=[solicitud_id], back_populates="documentos",
    )

    def __repr__(self) -> str:
        return f"<SolicitudReduccionCuotaDocumento(nombre={self.nombre_archivo!r})>"
