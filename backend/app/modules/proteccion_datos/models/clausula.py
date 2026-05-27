"""Cláusulas informativas versionadas (art. 13 / 14 RGPD).

Catálogo de textos informativos que se muestran al interesado en el
momento de la recogida del dato (alta de socio, formulario de
voluntariado, donaciones, contacto web…). Cada cambio crea una nueva
versión; las versiones antiguas se conservan para auditoría —prueba de
qué texto vio cada persona cuando consintió—.
"""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Text, Boolean, Date, Integer, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import BaseModel


# Códigos canónicos — se referencian desde formularios públicos y desde
# Consentimiento.codigo_clausula. Añadir aquí (y al seeding) cuando aparezca
# un nuevo punto de recogida.
CODIGOS_CLAUSULA = (
    'ALTA_SOCIO',
    'ALTA_VOLUNTARIADO',
    'DONACION',
    'CONTACTO_WEB',
    'COMUNICACIONES_INFORMATIVAS',
    'CESION_IMAGEN',
    'DATOS_SALUD',
)


class ClausulaInformativa(BaseModel):
    __tablename__ = 'rgpd_clausulas_informativas'
    __table_args__ = (
        UniqueConstraint('codigo', 'version', name='uq_clausulas_codigo_version'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    vigente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    fecha_vigencia_desde: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vigencia_hasta: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    finalidad_corta: Mapped[str] = mapped_column(
        String(300), nullable=False,
        comment='Resumen de una línea para listas y selectores'
    )
    texto: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment='Texto informativo completo (markdown)'
    )

    def __repr__(self) -> str:
        return f"<ClausulaInformativa(codigo='{self.codigo}', v={self.version}, vigente={self.vigente})>"
