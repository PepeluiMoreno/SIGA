"""Brechas de seguridad de datos personales (art. 33 / 34 RGPD).

El responsable tiene 72 h desde el conocimiento de la brecha para
notificarla a la AEPD (art. 33). Si supone alto riesgo para los derechos
y libertades de los afectados, debe comunicarla también a ellos sin
dilación indebida (art. 34).
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, Date, DateTime, Integer, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel


ORIGENES_BRECHA = (
    'CIBERATAQUE',
    'PERDIDA_DISPOSITIVO',
    'ROBO_DISPOSITIVO',
    'ENVIO_ERRONEO',
    'ERROR_HUMANO',
    'ACCESO_NO_AUTORIZADO',
    'FALLO_TECNICO',
    'OTROS',
)

SEVERIDADES = ('BAJA', 'MEDIA', 'ALTA', 'CRITICA')


class BrechaSeguridad(BaseModel):
    __tablename__ = 'rgpd_brechas_seguridad'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo_interno: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True, index=True,
        comment='Código legible (ej. BRE-2026-0001)'
    )

    fecha_deteccion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False,
        comment='Cuándo se tuvo conocimiento (inicio del cómputo de 72 h)'
    )
    fecha_ocurrencia: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True,
        comment='Fecha estimada de la brecha (si distinta de la detección)'
    )

    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    origen: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    severidad: Mapped[str] = mapped_column(String(20), nullable=False, default='MEDIA', index=True)

    datos_afectados: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Categorías de datos afectados (identificativos, contacto, salud, económicos…)'
    )
    personas_afectadas_num: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    datos_sensibles_afectados: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    medidas_inmediatas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    medidas_correctivas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Notificación a la AEPD (art. 33)
    notificada_aepd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    fecha_notificacion_aepd: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    referencia_aepd: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notificacion_aepd_documento_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    motivo_no_notificacion: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Si no se notifica: justificación de la improbabilidad de riesgo (art. 33.1)'
    )

    # Comunicación a los afectados (art. 34)
    comunicada_interesados: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_comunicacion_interesados: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    medio_comunicacion_interesados: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    cerrada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    fecha_cierre: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    detectada_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True
    )
    responsable_gestion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True
    )

    def __repr__(self) -> str:
        return f"<BrechaSeguridad(codigo='{self.codigo_interno}', severidad='{self.severidad}')>"
