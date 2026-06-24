"""Justificante de Gastos: solicitud de reembolso o rendición de cuenta de un miembro.

Un miembro presenta un justificante (con factura/ticket adjunto) por un gasto
realizado en nombre de la organización. Debe imputarse OBLIGATORIAMENTE a una
actividad (campaña, permanente o puntual).

Flujo de estados:
    PRESENTADO → APROBADO → PAGADO
              ↘ RECHAZADO (con motivo)
              ↘ ANULADO

Cumplimiento:
- LGT art. 106 + RD 1619/2012 — conservación de facturas
- LO 8/2007 (partidos) / Ley 50/2002 (fundaciones) — imputación a actividad
- Control interno PCESFL norma 1ª — segregación: presenta uno, autoriza otro
"""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Uuid, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class JustificanteGasto(BaseModel):
    """Justificante de gastos presentado por un miembro e imputado a actividad."""
    __tablename__ = "justificantes_gasto"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Numeración correlativa
    numero_justificante: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    ejercicio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Quién presenta (miembro)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("contactos.id"), nullable=False, index=True)

    # Imputación obligatoria a actividad; opcionalmente a una partida concreta de la actividad
    actividad_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("actividades.id"), nullable=False, index=True
    )
    partida_actividad_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("partidas_presupuesto_actividad.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    # Tesorería delegada
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("unidades_organizativas.id"), nullable=True, index=True
    )

    # Concepto e importe (resumen/cabecera; el detalle real va en `lineas`).
    # `importe` se mantiene como suma agregada de líneas para queries rápidas.
    # `concepto` puede ser el de la línea principal o un resumen como "Varios (3)".
    concepto: Mapped[str] = mapped_column(String(300), nullable=False)
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Fechas
    fecha_gasto: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_presentacion: Mapped[date] = mapped_column(Date, nullable=False)

    # Estado del flujo: PRESENTADO | APROBADO | RECHAZADO | PAGADO | ANULADO
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PRESENTADO", index=True)

    # Aceptación intermedia por el responsable de la actividad (D7.5)
    aceptado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("contactos.id"), nullable=True, index=True
    )
    fecha_aceptacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Autorización final (tesorero que aprueba/rechaza)
    aprobado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("contactos.id"), nullable=True, index=True
    )
    fecha_aprobacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Adjunto factura/ticket (D7.2) — opcional, almacenamiento simple por path
    archivo_factura: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # D7.7: categoría de gasto (cuenta contable del grupo 6) — obligatorio para nuevos
    cuenta_contable_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("cuentas_contables.id"), nullable=True, index=True
    )

    # D7.6: si lo presenta el tesorero en nombre de un socio (atajo)
    presentado_en_nombre_de_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("contactos.id"), nullable=True, index=True
    )

    # Pago
    apunte_caja_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("apuntes_caja.id", ondelete="SET NULL"), nullable=True, index=True
    )
    cuenta_bancaria_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("cuentas_bancarias.id"), nullable=True, index=True
    )
    modo_pago: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    fecha_pago: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    miembro = relationship("Contacto", foreign_keys=[miembro_id], lazy="selectin")
    aceptador = relationship("Contacto", foreign_keys=[aceptado_por_id], lazy="selectin")
    aprobador = relationship("Contacto", foreign_keys=[aprobado_por_id], lazy="selectin")
    actividad = relationship("Actividad", foreign_keys=[actividad_id], lazy="selectin")
    partida_actividad = relationship(
        "PartidaPresupuestoActividad", foreign_keys=[partida_actividad_id], lazy="selectin"
    )
    agrupacion = relationship("UnidadOrganizativa", foreign_keys=[agrupacion_id], lazy="selectin")
    cuenta_bancaria = relationship(
        "CuentaBancaria", foreign_keys=[cuenta_bancaria_id], lazy="selectin"
    )
    apunte_caja = relationship("ApunteCaja", foreign_keys=[apunte_caja_id], lazy="selectin")
    cuenta_contable = relationship("CuentaContable", foreign_keys=[cuenta_contable_id], lazy="selectin")
    presentado_por_tesorero = relationship("Contacto", foreign_keys=[presentado_en_nombre_de_id], lazy="selectin")

    def __repr__(self) -> str:
        return f"<JustificanteGasto(numero='{self.numero_justificante}', estado='{self.estado}', importe={self.importe})>"

    @property
    def esta_pagado(self) -> bool:
        return self.estado == "PAGADO"

    @property
    def puede_aceptarse(self) -> bool:
        """D7.5: el responsable de la actividad acepta cuando está PRESENTADO."""
        return self.estado == "PRESENTADO"

    @property
    def puede_aprobarse(self) -> bool:
        """D7.1: el tesorero aprueba cuando ya ha sido ACEPTADO por el responsable."""
        return self.estado == "ACEPTADO"

    @property
    def puede_pagarse(self) -> bool:
        return self.estado == "APROBADO"

    @property
    def puede_anularse_presentador(self) -> bool:
        """Solo el propio presentador puede retirarlo mientras esté PRESENTADO."""
        return self.estado == "PRESENTADO"

    # Líneas de detalle (un justificante puede tener varios conceptos referidos a la misma actividad)
    lineas = relationship(
        "JustificanteGastoLinea",
        back_populates="justificante",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="JustificanteGastoLinea.fecha_gasto.desc()",
    )

    # Documentos probatorios (facturas, tickets, fotos…)
    documentos = relationship(
        "JustificanteGastoDocumento",
        back_populates="justificante",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class JustificanteGastoLinea(BaseModel):
    """Línea individual de gasto dentro de un justificante.

    Un justificante representa un conjunto de gastos del mismo socio en la misma
    actividad. Cada `JustificanteGastoLinea` es uno de esos gastos concretos
    (un ticket, una factura, una dieta). El importe total del justificante es la
    suma de los importes de sus líneas.
    """
    __tablename__ = "justificantes_gasto_linea"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    justificante_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("justificantes_gasto.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    concepto: Mapped[str] = mapped_column(String(300), nullable=False)
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_gasto: Mapped[date] = mapped_column(Date, nullable=False)

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    justificante = relationship(
        "JustificanteGasto", foreign_keys=[justificante_id], back_populates="lineas",
    )

    def __repr__(self) -> str:
        return f"<JustificanteGastoLinea(importe={self.importe}, concepto='{self.concepto[:30]}')>"


class JustificanteGastoDocumento(BaseModel):
    """Documento probatorio adjunto a un justificante (factura, ticket, foto).

    Almacenamiento en disco del servidor bajo `/uploads/justificantes/{id}/`. Cuando
    se integre OCR (mini-ciclo aparte), `ocr_texto` y `ocr_datos` se rellenarán al
    subir y servirán para precargar líneas o anotar datos del documento.
    """
    __tablename__ = "justificantes_gasto_documento"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    justificante_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("justificantes_gasto.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)  # ruta/URL pública
    mime_type: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    tamano_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # OCR: opcional, alimentado en mini-ciclo posterior con pytesseract
    ocr_texto: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Datos extraídos por heurísticas (NIF emisor, fecha, importe…) — JSON serializado
    ocr_datos_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    justificante = relationship(
        "JustificanteGasto", foreign_keys=[justificante_id], back_populates="documentos",
    )

    def __repr__(self) -> str:
        return f"<JustificanteGastoDocumento(nombre='{self.nombre_archivo}')>"
