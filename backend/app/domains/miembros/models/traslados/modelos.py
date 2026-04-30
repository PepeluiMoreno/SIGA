from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class EstadoTraslado(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO_ORIGEN = "APROBADO_ORIGEN"
    APROBADO_DESTINO = "APROBADO_DESTINO"
    APROBADO = "APROBADO"
    RECHAZADO_ORIGEN = "RECHAZADO_ORIGEN"
    RECHAZADO_DESTINO = "RECHAZADO_DESTINO"
    EJECUTADO = "EJECUTADO"
    CANCELADO = "CANCELADO"


class SolicitudTraslado(Base):
    __tablename__ = "solicitudes_traslado"
    
    id = Column(Integer, primary_key=True)
    
    # Socio que solicita el traslado
    socio_id = Column(Integer, ForeignKey('socios.id'), nullable=False)
    
    # Agrupaciones
    agrupacion_origen_id = Column(Integer, ForeignKey('agrupaciones_territoriales.id'), nullable=False)
    agrupacion_destino_id = Column(Integer, ForeignKey('agrupaciones_territoriales.id'), nullable=False)
    
    # Motivo del traslado
    motivo = Column(Text, nullable=False)
    
    # Estado
    estado = Column(Enum(EstadoTraslado), default=EstadoTraslado.PENDIENTE)
    
    # Fechas
    fecha_solicitud = Column(DateTime, default=datetime.utcnow)
    fecha_efectiva_deseada = Column(Date)  # Cuándo quiere que sea efectivo el traslado
    
    # Aprobaciones
    aprobado_origen = Column(Boolean, default=False)
    fecha_aprobacion_origen = Column(DateTime)
    coordinador_origen_id = Column(Integer, ForeignKey('usuarios.id'))
    observaciones_origen = Column(Text)
    
    aprobado_destino = Column(Boolean, default=False)
    fecha_aprobacion_destino = Column(DateTime)
    coordinador_destino_id = Column(Integer, ForeignKey('usuarios.id'))
    observaciones_destino = Column(Text)
    
    # Rechazo
    motivo_rechazo = Column(Text)
    
    # Ejecución
    fecha_ejecucion = Column(DateTime)
    usuario_ejecutor_id = Column(Integer, ForeignKey('usuarios.id'))
    
    # Datos del traslado ejecutado
    numero_socio_anterior = Column(String(50))
    numero_socio_nuevo = Column(String(50))
    equipos_dados_baja = Column(Text)  # JSON con lista de equipos
    
    # Observaciones generales
    observaciones = Column(Text)
    
    # Control
    activo = Column(Boolean, default=True)
    
    # Relaciones
    socio = relationship("Socio", back_populates="solicitudes_traslado")
    agrupacion_origen = relationship("AgrupacionTerritorial", foreign_keys=[agrupacion_origen_id])
    agrupacion_destino = relationship("AgrupacionTerritorial", foreign_keys=[agrupacion_destino_id])
    coordinador_origen = relationship("Usuario", foreign_keys=[coordinador_origen_id])
    coordinador_destino = relationship("Usuario", foreign_keys=[coordinador_destino_id])
    usuario_ejecutor = relationship("Usuario", foreign_keys=[usuario_ejecutor_id])


# Actualizar modelo Socio para añadir relación
# En backend/app/modulos/administracion_socios/modelos.py
class Socio(Base):
    # ... campos existentes ...
    
    # Añadir:
    solicitudes_traslado = relationship("SolicitudTraslado", back_populates="socio")