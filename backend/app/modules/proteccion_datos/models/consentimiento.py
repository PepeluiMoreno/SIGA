"""Consentimientos otorgados por interesados (art. 7 RGPD).

Cada consentimiento queda enlazado a la versión exacta de la cláusula
informativa que el interesado vio cuando consintió —prueba del
consentimiento art. 7.1—. Una retirada no borra el registro: se marca
con `estado = RETIRADO` y `fecha_retirada`.
"""

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel

if TYPE_CHECKING:
    from .clausula import ClausulaInformativa


ESTADOS_CONSENTIMIENTO = ('OTORGADO', 'RETIRADO')
CANALES_CONSENTIMIENTO = ('WEB', 'PAPEL', 'EMAIL', 'IMPORTACION', 'PRESENCIAL')


class Consentimiento(BaseModel):
    __tablename__ = 'rgpd_consentimientos'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Interesado: o miembro / usuario interno, o externo identificado por email
    miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('contactos.id', ondelete='SET NULL'), nullable=True, index=True
    )
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True, index=True
    )
    email_externo: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    nombre_externo: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    clausula_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('rgpd_clausulas_informativas.id'), nullable=False, index=True
    )

    estado: Mapped[str] = mapped_column(String(20), nullable=False, default='OTORGADO', index=True)
    fecha_otorgamiento: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_retirada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    canal: Mapped[str] = mapped_column(String(20), nullable=False, default='WEB')
    prueba: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Evidencia del consentimiento: IP, user-agent, ruta del PDF firmado, etc.'
    )

    clausula: Mapped['ClausulaInformativa'] = relationship('ClausulaInformativa', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Consentimiento(clausula={self.clausula_id}, estado='{self.estado}')>"
