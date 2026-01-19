"""Modelos de asociaciones y convenios de colaboración."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoAsociacion(BaseModel):
    """Tipos de asociaciones con las que se colabora."""
    __tablename__ = 'tipos_asociacion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    asociaciones = relationship('Asociacion', back_populates='tipo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoAsociacion(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Asociacion(BaseModel):
    """
    Asociaciones con las que se tienen relaciones de colaboración.

    Incluye ONGs, asociaciones culturales, deportivas, vecinales,
    sindicatos, organizaciones empresariales, etc.
    """
    __tablename__ = 'asociaciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Identificación
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    nombre_corto: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    siglas: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)

    # Tipo de asociación
    tipo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('tipos_asociacion.id'),
        nullable=False,
        index=True
    )

    # Datos legales
    cif_nif: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    registro_oficial: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    numero_registro: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fecha_constitucion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Ubicación
    direccion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey('direcciones.id'),
        nullable=True
    )
    provincia_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey('provincias.id'),
        nullable=True,
        index=True
    )
    ambito: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default='LOCAL'
    )  # LOCAL, PROVINCIAL, AUTONOMICO, ESTATAL, INTERNACIONAL

    # Datos de contacto
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    web: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Persona de contacto
    persona_contacto_nombre: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    persona_contacto_cargo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    persona_contacto_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    persona_contacto_telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Información adicional
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actividades_principales: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    numero_socios: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    fecha_alta: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False)
    fecha_baja: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    motivo_baja: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Valoración de la relación
    valoracion: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 estrellas
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    tipo = relationship('TipoAsociacion', back_populates='asociaciones', lazy='selectin')
    direccion = relationship('Direccion', lazy='selectin')
    provincia = relationship('Provincia', lazy='selectin')
    convenios = relationship('Convenio', back_populates='asociacion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Asociacion(nombre='{self.nombre}', siglas='{self.siglas}')>"

    @property
    def tiene_convenio_vigente(self) -> bool:
        """Verifica si tiene algún convenio vigente basado en fechas."""
        if not self.convenios:
            return False
        return any(conv.esta_vigente for conv in self.convenios)


class EstadoConvenio(BaseModel):
    """Estados de convenios de colaboración."""
    __tablename__ = 'estados_convenio'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    convenios = relationship('Convenio', back_populates='estado', lazy='selectin')

    def __repr__(self) -> str:
        return f"<EstadoConvenio(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Convenio(BaseModel):
    """
    Convenios de colaboración con asociaciones.

    Incluye acuerdos, protocolos, convenios marco, etc.
    """
    __tablename__ = 'convenios'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Asociación
    asociacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('asociaciones.id'),
        nullable=False,
        index=True
    )

    # Identificación del convenio
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default='CONVENIO'
    )  # CONVENIO, ACUERDO, PROTOCOLO, MEMORANDUM

    # Fechas
    fecha_firma: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    renovable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Contenido
    objeto: Mapped[str] = mapped_column(Text, nullable=False)  # Objetivo del convenio
    compromisos_asociacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    compromisos_propios: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    beneficios: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Aspectos económicos
    tiene_aportacion_economica: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    importe_aportacion: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    periodicidad_aportacion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # MENSUAL, ANUAL, UNICA

    # Documentación
    documento_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    anexos_urls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array

    # Responsables
    responsable_organizacion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    responsable_asociacion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Estado
    estado_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('estados_convenio.id'),
        nullable=False,
        index=True
    )

    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    asociacion = relationship('Asociacion', back_populates='convenios', lazy='selectin')
    estado = relationship('EstadoConvenio', back_populates='convenios', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Convenio(codigo='{self.codigo}', nombre='{self.nombre}')>"

    @property
    def esta_vigente(self) -> bool:
        """Verifica si el convenio está vigente basado en fechas."""
        hoy = date.today()
        # Vigente si estamos entre fecha_inicio y fecha_fin (o sin fecha_fin)
        if hoy < self.fecha_inicio:
            return False
        if self.fecha_fin and hoy > self.fecha_fin:
            return False
        return True

    @property
    def dias_hasta_vencimiento(self) -> Optional[int]:
        """Calcula los días hasta el vencimiento del convenio."""
        if not self.fecha_fin:
            return None
        dias = (self.fecha_fin - date.today()).days
        return dias if dias > 0 else 0
