# domains/financiero/models/tesoreria_conciliacion.py

from sqlalchemy import Column, Integer, Date, Numeric, String, Boolean, ForeignKey
from app.infrastructure.base_model import Base


class ExtractoBancario(Base):
    __tablename__ = "fin_extracto"

    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    importe = Column(Numeric(12, 2), nullable=False)
    concepto = Column(String, nullable=True)

    referencia = Column(String, nullable=True)
    conciliado = Column(Boolean, default=False)


class Conciliacion(Base):
    __tablename__ = "fin_conciliacion"

    id = Column(Integer, primary_key=True)

    movimiento_id = Column(Integer, ForeignKey("fin_movimiento.id"))
    extracto_id = Column(Integer, ForeignKey("fin_extracto.id"))