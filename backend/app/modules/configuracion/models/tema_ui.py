"""Catálogo de temas de interfaz de usuario."""
import uuid
from sqlalchemy import String, Boolean, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from ....infrastructure.base_model import BaseModel


class TemaUI(BaseModel):
    __tablename__ = "temas_ui"
    __table_args__ = (UniqueConstraint('slug', name='uq_temas_ui_slug'),)

    id:     Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str]       = mapped_column(String(60), nullable=False)
    slug:   Mapped[str]       = mapped_column(String(40), nullable=False, index=True)

    # Paleta de color primario (10 tonos)
    t50:  Mapped[str] = mapped_column(String(25), nullable=False)
    t100: Mapped[str] = mapped_column(String(25), nullable=False)
    t200: Mapped[str] = mapped_column(String(25), nullable=False)
    t300: Mapped[str] = mapped_column(String(25), nullable=False)
    t400: Mapped[str] = mapped_column(String(25), nullable=False)
    t500: Mapped[str] = mapped_column(String(25), nullable=False)
    t600: Mapped[str] = mapped_column(String(25), nullable=False)
    t700: Mapped[str] = mapped_column(String(25), nullable=False)
    t800: Mapped[str] = mapped_column(String(25), nullable=False)
    t900: Mapped[str] = mapped_column(String(25), nullable=False)

    # Colores estructurales
    sidebar:      Mapped[str] = mapped_column(String(50), nullable=False)  # fondo barra lateral
    topbar:       Mapped[str] = mapped_column(String(25), nullable=False)  # fondo cabecera
    page_bg:      Mapped[str] = mapped_column(String(25), nullable=False)  # fondo página
    card_bg:      Mapped[str] = mapped_column(String(25), nullable=False)  # fondo tarjetas/paneles
    text_main:    Mapped[str] = mapped_column(String(25), nullable=False)  # texto principal
    text_muted:   Mapped[str] = mapped_column(String(25), nullable=False)  # texto secundario
    border_color: Mapped[str] = mapped_column(String(25), nullable=False)  # color de bordes

    sistema: Mapped[bool] = mapped_column(Boolean, server_default='false', nullable=False)
    activo:  Mapped[bool] = mapped_column(Boolean, server_default='true',  nullable=False)
