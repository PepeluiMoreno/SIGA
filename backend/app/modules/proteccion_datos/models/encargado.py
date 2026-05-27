"""Encargados del tratamiento (art. 28 RGPD).

Proveedores que tratan datos personales por cuenta del responsable
(hosting, pasarela de pago, email/SMTP, gestoría, mensajería…). Cada
encargado debe tener firmado un contrato de encargo conforme al art. 28.
"""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Text, Boolean, Date, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel


class EncargadoTratamiento(BaseModel):
    __tablename__ = 'rgpd_encargados_tratamiento'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    nif: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    servicio: Mapped[str] = mapped_column(
        String(300), nullable=False,
        comment='Servicio prestado: hosting, SMTP, pasarela de pago, gestoría…'
    )

    contacto_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contacto_telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pais_alojamiento: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment='País donde se alojan/tratan los datos (relevante para TID)'
    )
    transferencia_internacional: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment='True si hay transferencia internacional de datos (fuera del EEE)'
    )

    contrato_firmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contrato_fecha: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    contrato_documento_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    clausulas_tipo_aepd: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment='Usa cláusulas tipo aprobadas por la AEPD'
    )

    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<EncargadoTratamiento(nombre='{self.nombre}', servicio='{self.servicio}')>"
