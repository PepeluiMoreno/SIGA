"""Histórico de mensajes de email enviados desde la aplicación.

MVP del módulo de Comunicación: cada envío de la app (p.ej. "Enviar mensaje" a una
selección de contactos) se registra aquí para trazabilidad y consulta posterior.
No es un cliente de correo (no recibe): solo el histórico de lo enviado por SMTP.
Ver project_modulo_comunicacion.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Uuid, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.base_model import BaseModel


class MensajeEnviado(BaseModel):
    """Un mensaje de email enviado desde la app (a uno o varios destinatarios)."""
    __tablename__ = "mensajes_enviados"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Quién lo envió (usuario de la app) y cuándo.
    remitente_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True
    )
    enviado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    asunto: Mapped[str] = mapped_column(String(500), nullable=False)
    cuerpo_html: Mapped[str] = mapped_column(Text, nullable=False)

    # Destinatarios como listas de emails serializadas (coma), para trazabilidad.
    para: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cco: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Resultado del envío.
    enviados: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errores: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # errores serializados (\n)

    def __repr__(self) -> str:
        return f"<MensajeEnviado(asunto='{self.asunto}', enviados={self.enviados}/{self.total})>"
