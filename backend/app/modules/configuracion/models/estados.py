"""Modelos de estados para las distintas entidades del sistema."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Text, DateTime, Uuid, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel, InmutableMixin


class EstadoBase(InmutableMixin, BaseModel):
    """Clase base abstracta para todos los estados."""
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    es_inicial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    es_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(nombre='{self.nombre}')>"


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


class EstadoAccion(EstadoBase):
    """Estados para acciones (unidad operativa)."""
    __tablename__ = 'estados_accion'

    # propuesta | aprobada | en_preparacion | en_curso | finalizada | cancelada


class EstadoActividad(EstadoBase):
    """Estados para actividades (legacy — mantenida por compatibilidad)."""
    __tablename__ = 'estados_actividad'


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


class EstadoNotificacion(EstadoBase):
    """Estados para notificaciones."""
    __tablename__ = 'estados_notificacion'

    # Posibles estados:
    # PENDIENTE: Notificación creada pero no enviada
    # ENVIADA: Notificación enviada al canal correspondiente
    # LEIDA: Notificación leída por el usuario
    # ERROR: Error al enviar la notificación



class EstadoReunion(EstadoBase):
    """Estados para reuniones de órganos de gobierno."""
    __tablename__ = 'estados_reunion'

    # CONVOCADA → CELEBRADA → ACTA_BORRADOR → ACTA_APROBADA (final)
    # CANCELADA (final)
    codigo: Mapped[str] = mapped_column(String(30), nullable=False, unique=True,
        comment="Código de máquina: CONVOCADA, CELEBRADA, ACTA_BORRADOR, ACTA_APROBADA, CANCELADA")


class EstadoActa(EstadoBase):
    """Estados para actas de reuniones."""
    __tablename__ = 'estados_acta'

    # BORRADOR → APROBADA → FIRMADA (final)
    codigo: Mapped[str] = mapped_column(String(30), nullable=False, unique=True,
        comment="Código de máquina: BORRADOR, APROBADA, FIRMADA")


class EstadoEjecucionAcuerdo(EstadoBase):
    """Estados de ejecución para acuerdos adoptados en reuniones."""
    __tablename__ = 'estados_ejecucion_acuerdo'

    # PENDIENTE → EN_CURSO → COMPLETADO (final) | ARCHIVADO (final)
    codigo: Mapped[str] = mapped_column(String(30), nullable=False, unique=True,
        comment="Código de máquina: PENDIENTE, EN_CURSO, COMPLETADO, ARCHIVADO")

class HistorialEstado(BaseModel):
    """Registro genérico de cambios de estado de cualquier entidad.

    Usa UUIDs para referenciar estados en lugar de códigos literales.
    El campo estado_tabla indica la tabla de estados correspondiente.
    """
    __tablename__ = 'historial_estados'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    entidad_tipo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # Nombre de la clase (ej: 'cuotaanual')
    entidad_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # UUID de la entidad
    estado_tabla: Mapped[str] = mapped_column(String(50), nullable=False)  # Tabla de estados (ej: 'estados_cuota')
    estado_anterior_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)  # UUID del estado anterior
    estado_nuevo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)  # UUID del nuevo estado
    motivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_cambio: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('usuarios.id'), nullable=True)

    # Relación con usuario que realizó el cambio
    usuario = relationship('Usuario', foreign_keys=[usuario_id], lazy='selectin')

    def __repr__(self) -> str:
        return (f"<HistorialEstado(entidad='{self.entidad_tipo}:{self.entidad_id}', "
                f"{self.estado_anterior_id} -> {self.estado_nuevo_id})>")
