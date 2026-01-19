"""Modelos de voluntariado, competencias y formación."""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Boolean, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class CategoriaCompetencia(BaseModel):
    """Categorías de competencias."""
    __tablename__ = 'categorias_competencia'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    competencias = relationship('Competencia', back_populates='categoria', lazy='selectin')

    def __repr__(self) -> str:
        return f"<CategoriaCompetencia(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Competencia(BaseModel):
    """Competencias de voluntarios."""
    __tablename__ = 'competencias'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    categoria_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('categorias_competencia.id'), nullable=False, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    categoria = relationship('CategoriaCompetencia', back_populates='competencias', lazy='selectin')
    miembros_competencia = relationship('MiembroCompetencia', back_populates='competencia', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Competencia(codigo='{self.codigo}', nombre='{self.nombre}')>"


class NivelCompetencia(BaseModel):
    """Niveles de competencia (básico, intermedio, avanzado, experto)."""
    __tablename__ = 'niveles_competencia'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    miembros_competencia = relationship('MiembroCompetencia', back_populates='nivel', lazy='selectin')

    def __repr__(self) -> str:
        return f"<NivelCompetencia(codigo='{self.codigo}', nombre='{self.nombre}')>"


class MiembroCompetencia(BaseModel):
    """Competencias de un miembro específico."""
    __tablename__ = 'miembros_competencia'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a Miembro
    competencia_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('competencias.id'), nullable=False, index=True)
    nivel_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('niveles_competencia.id'), nullable=False, index=True)

    verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_verificacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    competencia = relationship('Competencia', back_populates='miembros_competencia', lazy='selectin')
    nivel = relationship('NivelCompetencia', back_populates='miembros_competencia', lazy='selectin')

    def __repr__(self) -> str:
        return f"<MiembroCompetencia(miembro_id='{self.miembro_id}', competencia_id='{self.competencia_id}')>"


class TipoDocumentoVoluntario(BaseModel):
    """Tipos de documentos para voluntarios."""
    __tablename__ = 'tipos_documento_voluntario'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requiere_caducidad: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    documentos = relationship('DocumentoMiembro', back_populates='tipo_documento', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoDocumentoVoluntario(codigo='{self.codigo}', nombre='{self.nombre}')>"


class DocumentoMiembro(BaseModel):
    """Documento de un miembro voluntario."""
    __tablename__ = 'documentos_miembro'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a Miembro
    tipo_documento_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_documento_voluntario.id'), nullable=False, index=True)

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Archivo
    archivo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    archivo_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    archivo_tipo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    archivo_tamano: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    fecha_subida: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fecha_caducidad: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    tipo_documento = relationship('TipoDocumentoVoluntario', back_populates='documentos', lazy='selectin')

    def __repr__(self) -> str:
        return f"<DocumentoMiembro(nombre='{self.nombre}', miembro_id='{self.miembro_id}')>"

    def esta_caducado(self) -> bool:
        """Verifica si el documento ha caducado."""
        if self.fecha_caducidad is None:
            return False
        return self.fecha_caducidad < date.today()


class TipoFormacion(BaseModel):
    """Tipos de formación para voluntarios."""
    __tablename__ = 'tipos_formacion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    formaciones = relationship('FormacionMiembro', back_populates='tipo_formacion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoFormacion(codigo='{self.codigo}', nombre='{self.nombre}')>"


class FormacionMiembro(BaseModel):
    """Formación recibida por un miembro."""
    __tablename__ = 'formaciones_miembro'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)  # FK a Miembro
    tipo_formacion_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_formacion.id'), nullable=False, index=True)

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    institucion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    horas: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    certificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    competencias_adquiridas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    es_interna: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Formación interna de la organización

    # Relaciones
    tipo_formacion = relationship('TipoFormacion', back_populates='formaciones', lazy='selectin')

    def __repr__(self) -> str:
        return f"<FormacionMiembro(titulo='{self.titulo}', miembro_id='{self.miembro_id}')>"
