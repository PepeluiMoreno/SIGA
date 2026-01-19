"""Modelos de estados para las distintas entidades del sistema."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Text, DateTime, Uuid, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class EstadoBase(BaseModel):
    """Clase base abstracta para todos los estados."""
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    es_inicial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    es_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Para UI: 'primary', 'success', 'warning', 'danger'

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(codigo='{self.codigo}', nombre='{self.nombre}')>"


class EstadoCuota(EstadoBase):
    """Estados para cuotas anuales."""
    __tablename__ = 'estados_cuota'

    # Posibles estados:
    # PENDIENTE: Cuota creada pero no cobrada
    # COBRADA: Cuota cobrada exitosamente
    # IMPAGADA: Intento de cobro fallido
    # ANULADA: Cuota anulada/cancelada
    # EXENTA: Cuota exenta de pago


class EstadoCampania(EstadoBase):
    """Estados para campañas."""
    __tablename__ = 'estados_campania'

    # Posibles estados:
    # BORRADOR: Campaña en creación
    # PROGRAMADA: Campaña programada para envío
    # EN_CURSO: Campaña activa/enviándose
    # FINALIZADA: Campaña completada
    # CANCELADA: Campaña cancelada
    # PAUSADA: Campaña pausada temporalmente


class EstadoTarea(EstadoBase):
    """Estados para tareas."""
    __tablename__ = 'estados_tarea'

    # Posibles estados:
    # PENDIENTE: Tarea por hacer
    # EN_PROGRESO: Tarea en ejecución
    # COMPLETADA: Tarea finalizada
    # CANCELADA: Tarea cancelada
    # BLOQUEADA: Tarea bloqueada por dependencias


class EstadoActividad(EstadoBase):
    """Estados para actividades."""
    __tablename__ = 'estados_actividad'

    # Relaciones
    actividades = relationship('Actividad', back_populates='estado', lazy='selectin')

    # Posibles estados:
    # PROPUESTA: Actividad propuesta pendiente de aprobación
    # APROBADA: Actividad aprobada pendiente de programación
    # PROGRAMADA: Actividad programada con fecha definida
    # EN_CURSO: Actividad en ejecución
    # COMPLETADA: Actividad finalizada exitosamente
    # CANCELADA: Actividad cancelada


class EstadoParticipante(EstadoBase):
    """Estados para participantes en campañas."""
    __tablename__ = 'estados_participante'

    # Posibles estados:
    # INCLUIDO: Participante añadido a la campaña
    # ENVIADO: Comunicación enviada
    # ENTREGADO: Comunicación entregada
    # LEIDO: Comunicación leída/abierta
    # RESPONDIDO: Participante respondió
    # REBOTADO: Comunicación rebotada
    # EXCLUIDO: Participante excluido de la campaña


class EstadoOrdenCobro(EstadoBase):
    """Estados para órdenes de cobro."""
    __tablename__ = 'estados_orden_cobro'

    # Posibles estados:
    # PENDIENTE: Orden creada, pendiente de procesar
    # PROCESADA: Orden procesada, cobro realizado
    # FALLIDA: Cobro fallido
    # ANULADA: Orden anulada


class EstadoRemesa(EstadoBase):
    """Estados para remesas SEPA."""
    __tablename__ = 'estados_remesa'

    # Posibles estados:
    # BORRADOR: Remesa en creación
    # GENERADA: Remesa generada, pendiente de envío
    # ENVIADA: Remesa enviada al banco
    # PROCESADA: Remesa procesada por el banco
    # RECHAZADA: Remesa rechazada
    # PARCIAL: Remesa procesada parcialmente


class EstadoDonacion(EstadoBase):
    """Estados para donaciones."""
    __tablename__ = 'estados_donacion'

    # Posibles estados:
    # PENDIENTE: Donación prometida pero no recibida
    # RECIBIDA: Donación recibida
    # CERTIFICADA: Certificado de donación emitido
    # ANULADA: Donación anulada


class HistorialEstado(BaseModel):
    """Registro genérico de cambios de estado de cualquier entidad."""
    __tablename__ = 'historial_estados'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    entidad_tipo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # Nombre de la clase (ej: 'cuotaanual')
    entidad_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # UUID de la entidad
    estado_anterior_codigo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estado_nuevo_codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    motivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_cambio: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('usuarios.id'), nullable=True)

    # Relación con usuario que realizó el cambio
    usuario = relationship('Usuario', foreign_keys=[usuario_id], lazy='selectin')

    def __repr__(self) -> str:
        return (f"<HistorialEstado(entidad='{self.entidad_tipo}:{self.entidad_id}', "
                f"{self.estado_anterior_codigo} -> {self.estado_nuevo_codigo})>")
