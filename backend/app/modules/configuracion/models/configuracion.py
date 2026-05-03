"""Modelos de configuración del sistema."""

import uuid
import json
from typing import Optional

from sqlalchemy import Uuid, String, Text, Boolean, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class Configuracion(BaseModel):
    """Tabla de configuración para parámetros del sistema."""
    __tablename__ = 'configuraciones'

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    clave: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_dato: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='string'
    )  # int, float, string, json, boolean
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    modificable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    grupo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default='general'
    )
    orden: Mapped[int] = mapped_column(Integer, default=0)

    # Relación inversa con historial
    historial = relationship("HistorialConfiguracion", back_populates="configuracion")

    def get_valor(self):
        """Obtiene el valor convertido al tipo correcto."""
        if self.tipo_dato == 'bool':
            return self.valor.lower() in ['true', '1', 'yes', 'si', 'on']
        elif self.tipo_dato == 'int':
            return int(self.valor)
        elif self.tipo_dato == 'float':
            return float(self.valor)
        elif self.tipo_dato == 'json':
            try:
                return json.loads(self.valor)
            except json.JSONDecodeError:
                return {}
        else:
            return self.valor

    def set_valor(self, valor):
        """Establece el valor convirtiendo al tipo string."""
        if self.tipo_dato == 'json':
            self.valor = json.dumps(valor)
        else:
            self.valor = str(valor)

    def __repr__(self):
        return f"<Configuracion(clave='{self.clave}', valor='{self.valor}', tipo='{self.tipo_dato}')>"


class ReglaValidacionConfig(BaseModel):
    """Reglas de validación para configuraciones específicas."""
    __tablename__ = 'reglas_validacion_config'

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    config_clave: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    tipo_dato: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # email, url, porcentaje, moneda, etc.
    min_valor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_valor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_longitud: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    decimales: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pattern_regex: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    valores_permitidos: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mensaje_error: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def get_valores_permitidos(self) -> list:
        """Obtiene la lista de valores permitidos."""
        try:
            return json.loads(self.valores_permitidos) if self.valores_permitidos else []
        except (json.JSONDecodeError, TypeError):
            return []


class HistorialConfiguracion(BaseModel):
    """Historial de cambios en configuraciones."""
    __tablename__ = 'historial_configuracion'

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    configuracion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('configuraciones.id'),
        nullable=False
    )
    valor_anterior: Mapped[str] = mapped_column(Text, nullable=False)
    valor_nuevo: Mapped[str] = mapped_column(Text, nullable=False)
    motivo_cambio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    configuracion = relationship("Configuracion", back_populates="historial")

    def __repr__(self):
        return f"<HistorialConfiguracion(config_id={self.configuracion_id})>"
