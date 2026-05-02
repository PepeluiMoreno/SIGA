# domains/financiero/models/tesoreria.py

from sqlalchemy import Column, Integer, Date, Numeric, String, Enum, Boolean
from app.infrastructure.base_model import Base
import enum


class TipoMovimiento(enum.Enum):
    INGRESO = "INGRESO"
    GASTO = "GASTO"
    TRANSFERENCIA = "TRANSFERENCIA"


class EstadoMovimiento(enum.Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    CONCILIADO = "CONCILIADO"


class MovimientoEconomico(Base):
    __tablename__ = "fin_movimiento"

    id = Column(Integer, primary_key=True)

    fecha = Column(Date, nullable=False)
    importe = Column(Numeric(12, 2), nullable=False)
    concepto = Column(String, nullable=False)

    tipo = Column(Enum(TipoMovimiento), nullable=False)
    estado = Column(Enum(EstadoMovimiento), default=EstadoMovimiento.PENDIENTE)

    actividad_id = Column(Integer, nullable=True)
    miembro_id = Column(Integer, nullable=True)

    origen = Column(String, nullable=False)  # CUOTA, DONACION, REMESA, MANUAL
    referencia_externa = Column(String, nullable=True)

    conciliado = Column(Boolean, default=False)
