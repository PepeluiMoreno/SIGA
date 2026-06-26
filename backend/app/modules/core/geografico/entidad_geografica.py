"""Entidades geográficas: jerarquía territorial única y recursiva.

Una sola tabla recursiva (`padre_id`) para toda la división territorial, con el
**tipo** tomado del catálogo `AmbitoGeografico` (País/CCAA/Provincia/Municipio…),
de modo que admite cualquier distribución variopinta (comarca, concello,
parroquia…) sin hardcodear el nombre del nivel. Se puebla desde el recurso
consolidado «España - Geografía jerárquica (INE)» de OpenDataManager.
"""
import uuid
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.base_model import BaseModel


class EntidadGeografica(BaseModel):
    __tablename__ = 'entidades_geograficas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Clave de enlace ÚNICA, prefijada por tipo (ES / CA## / PR## / MU#####).
    # Necesaria porque los códigos INE de CCAA y provincia son ambos de 2 dígitos
    # y colisionan (CCAA 01=Andalucía vs provincia 01=Álava). Es la clave de
    # importación idempotente desde ODM.
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    # Código natural del INE (2 díg. CCAA/provincia, 5 díg. municipio). No único entre niveles.
    codigo_ine: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)

    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    ruta: Mapped[Optional[str]] = mapped_column(String(400), nullable=True)
    nivel: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('entidades_geograficas.id', ondelete='CASCADE'),
        nullable=True, index=True
    )
    # 'tipo' del nodo (País/CCAA/Provincia/Municipio…) = catálogo de ámbitos geográficos.
    ambito_geografico_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('ambitos_geograficos.id', ondelete='SET NULL'),
        nullable=True, index=True
    )

    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)

    padre = relationship(
        'EntidadGeografica', remote_side=[id], back_populates='hijos', lazy='selectin'
    )
    hijos = relationship(
        'EntidadGeografica', back_populates='padre', lazy='noload',
        cascade='all, delete-orphan'
    )
    ambito_geografico = relationship('AmbitoGeografico', lazy='selectin')

    def __repr__(self) -> str:
        return f"<EntidadGeografica(codigo='{self.codigo}', nombre='{self.nombre}')>"
