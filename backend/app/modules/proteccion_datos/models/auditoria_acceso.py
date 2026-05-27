"""Log de auditoría de accesos a datos personales (art. 5.2 — responsabilidad proactiva).

Registra quién accede a qué entidad con datos personales, cuándo y
desde dónde. Sirve para acreditar trazabilidad ante una inspección de
la AEPD y para investigar brechas. Es append-only: no se actualiza ni
se borra (la tabla no usa la auditoría estándar de BaseModel).
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, Uuid, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ....core.database import Base


TIPOS_ACCESO = ('LECTURA', 'ESCRITURA', 'EXPORT', 'ANONIMIZACION', 'BORRADO')


class AuditoriaAccesoDatos(Base):
    """Append-only. No hereda de BaseModel: no se modifica ni se borra."""
    __tablename__ = 'rgpd_auditoria_accesos'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    fecha_acceso: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )

    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True, index=True
    )
    usuario_email_snapshot: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True,
        comment='Email del usuario en el momento del acceso (por si luego se anonimiza)'
    )

    entidad: Mapped[str] = mapped_column(
        String(60), nullable=False, index=True,
        comment='Nombre lógico de la entidad accedida: miembro, donacion, usuario…'
    )
    entidad_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, index=True)
    tipo_acceso: Mapped[str] = mapped_column(
        String(20), nullable=False, default='LECTURA', index=True
    )

    campos_accedidos: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Lista CSV de campos sensibles consultados (opcional)'
    )
    motivo: Mapped[Optional[str]] = mapped_column(
        String(300), nullable=True,
        comment='Justificación del acceso si la acción lo requiere'
    )

    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Marca conveniencia para integridad: las filas no deben actualizarse
    immutable_marker: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<AuditoriaAccesoDatos(entidad='{self.entidad}', tipo='{self.tipo_acceso}', fecha={self.fecha_acceso})>"
