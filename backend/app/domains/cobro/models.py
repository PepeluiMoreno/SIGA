from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


# -------------------------
# CATALOGOS
# -------------------------

class ProveedorPago(Base):
    __tablename__ = "proveedores_pago"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String, unique=True, nullable=False)  # PAYPAL, BIZUM...
    nombre = Column(String, nullable=False)
    activo = Column(Boolean, default=True)


class TipoPago(Base):
    __tablename__ = "tipos_pago"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String, unique=True, nullable=False)  # DONACION, SUSCRIPCION
    descripcion = Column(String, nullable=True)


class EstadoPago(Base):
    __tablename__ = "estados_pago"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String, unique=True, nullable=False)  # CREADO, COMPLETADO...
    es_final = Column(Boolean, default=False)


class EstadoSuscripcion(Base):
    __tablename__ = "estados_suscripcion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String, unique=True, nullable=False)
    es_final = Column(Boolean, default=False)


class TipoEventoPago(Base):
    __tablename__ = "tipos_evento_pago"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String, unique=True, nullable=False)


# -------------------------
# DOMINIO
# -------------------------

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    proveedor_id = Column(UUID(as_uuid=True), ForeignKey("proveedores_pago.id"))
    tipo_pago_id = Column(UUID(as_uuid=True), ForeignKey("tipos_pago.id"))
    estado_pago_id = Column(UUID(as_uuid=True), ForeignKey("estados_pago.id"))

    importe = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(3), default="EUR")

    email_pagador = Column(String, nullable=True)
    usuario_id = Column(UUID(as_uuid=True), nullable=True)

    id_externo_principal = Column(String, nullable=True)
    id_externo_secundario = Column(String, nullable=True)

    datos_externos = Column(JSON, nullable=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_completado = Column(DateTime, nullable=True)

    suscripcion_id = Column(UUID(as_uuid=True), ForeignKey("suscripciones.id"))

    proveedor = relationship("ProveedorPago")
    tipo_pago = relationship("TipoPago")
    estado_pago = relationship("EstadoPago")
    suscripcion = relationship("Suscripcion", back_populates="pagos")


class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    proveedor_id = Column(UUID(as_uuid=True), ForeignKey("proveedores_pago.id"))
    estado_id = Column(UUID(as_uuid=True), ForeignKey("estados_suscripcion.id"))

    usuario_id = Column(UUID(as_uuid=True), nullable=True)

    importe = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(3), default="EUR")

    id_externo = Column(String, nullable=False)

    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_proximo_cobro = Column(DateTime, nullable=True)

    proveedor = relationship("ProveedorPago")
    estado = relationship("EstadoSuscripcion")

    pagos = relationship("Pago", back_populates="suscripcion")


class EventoPago(Base):
    __tablename__ = "eventos_pago"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    pago_id = Column(UUID(as_uuid=True), ForeignKey("pagos.id"))

    proveedor_id = Column(UUID(as_uuid=True), ForeignKey("proveedores_pago.id"))
    tipo_evento_id = Column(UUID(as_uuid=True), ForeignKey("tipos_evento_pago.id"))

    id_evento_externo = Column(String, nullable=True)

    payload = Column(JSON, nullable=False)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)