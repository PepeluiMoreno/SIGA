"""Catálogo de habilidades y competencias del sistema."""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Uuid, Boolean, UniqueConstraint, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class Skill(BaseModel):
    """Habilidad o competencia del catálogo."""
    __tablename__ = 'skills'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    categoria: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    miembro_skills: Mapped[list['MiembroSkill']] = relationship('MiembroSkill', back_populates='skill', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Skill(nombre='{self.nombre}', categoria='{self.categoria}')>"


class MiembroSkill(BaseModel):
    """Habilidad declarada o validada de un miembro."""
    __tablename__ = 'miembros_skills'
    __table_args__ = (
        UniqueConstraint('miembro_id', 'skill_id', name='uq_miembro_skill'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id', ondelete='CASCADE'), nullable=False, index=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('skills.id', ondelete='CASCADE'), nullable=False, index=True
    )

    nivel: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    validado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True
    )
    fecha_validacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    skill: Mapped['Skill'] = relationship('Skill', back_populates='miembro_skills', lazy='selectin')

    def __repr__(self) -> str:
        return f"<MiembroSkill(miembro={self.miembro_id}, skill={self.skill_id})>"
