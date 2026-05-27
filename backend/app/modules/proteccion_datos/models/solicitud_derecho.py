"""Solicitudes de ejercicio de derechos ARSULIPO (art. 15-22 RGPD).

Flujo unificado para que el interesado ejerza sus derechos:
Acceso, Rectificación, Supresión, Limitación, Portabilidad, Oposición y
decisiones automatizadas. Plazo legal de respuesta: 1 mes, prorrogable a
3 (art. 12.3 RGPD).
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, Date, DateTime, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel


TIPOS_DERECHO = (
    'ACCESO',                 # art. 15
    'RECTIFICACION',          # art. 16
    'SUPRESION',              # art. 17 ("derecho al olvido")
    'LIMITACION',             # art. 18
    'PORTABILIDAD',           # art. 20
    'OPOSICION',              # art. 21
    'DECISION_AUTOMATIZADA',  # art. 22
)

ESTADOS_SOLICITUD = (
    'PRESENTADA',
    'EN_TRAMITE',
    'PRORROGADA',
    'RESUELTA',
    'DENEGADA',
)

CANALES_PRESENTACION = ('WEB', 'EMAIL', 'PAPEL', 'PRESENCIAL', 'CORREO_POSTAL')


class SolicitudDerechoRGPD(BaseModel):
    __tablename__ = 'rgpd_solicitudes_derechos'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo_interno: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True, index=True,
        comment='Código legible para referenciar la solicitud (ej. ARS-2026-0001)'
    )

    tipo: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default='PRESENTADA', index=True
    )

    # Solicitante
    miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id', ondelete='SET NULL'), nullable=True, index=True
    )
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True, index=True
    )
    nombre_solicitante: Mapped[str] = mapped_column(String(200), nullable=False)
    documento_solicitante: Mapped[Optional[str]] = mapped_column(
        String(40), nullable=True,
        comment='DNI/NIE/Pasaporte que acompaña la solicitud (acreditación de identidad)'
    )
    email_solicitante: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    telefono_solicitante: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    canal_presentacion: Mapped[str] = mapped_column(String(30), nullable=False, default='EMAIL')
    fecha_presentacion: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_limite_respuesta: Mapped[date] = mapped_column(
        Date, nullable=False,
        comment='Calculada al alta: fecha_presentacion + 1 mes'
    )
    prorrogada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_limite_prorroga: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True,
        comment='Si se prorroga: fecha_presentacion + 3 meses, y se debe motivar'
    )
    motivo_prorroga: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    descripcion_solicitud: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    fecha_resolucion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolucion: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Resolución motivada notificada al interesado'
    )
    documento_resolucion_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tramitada_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True
    )

    def __repr__(self) -> str:
        return f"<SolicitudDerechoRGPD(codigo='{self.codigo_interno}', tipo='{self.tipo}', estado='{self.estado}')>"
