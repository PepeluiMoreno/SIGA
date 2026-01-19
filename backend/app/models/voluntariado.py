from datetime import date, datetime
from sqlalchemy import String, ForeignKey, DateTime, Date, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class CategoriaCompetencia(Base):
    """Categorías de competencias: TECNICA, IDIOMAS, COMUNICACION, etc."""
    __tablename__ = "categoria_competencia"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(String(500))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Competencia(Base):
    """Competencias/Skills disponibles (RF-VC001)."""
    __tablename__ = "competencia"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(String(500))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categoria_competencia.id"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relaciones
    categoria: Mapped["CategoriaCompetencia"] = relationship()


class NivelCompetencia(Base):
    """Niveles de dominio: BASICO, INTERMEDIO, AVANZADO, EXPERTO."""
    __tablename__ = "nivel_competencia"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(50))
    orden: Mapped[int] = mapped_column(Integer, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class MiembroCompetencia(Base):
    """Competencias de un miembro (RF-VC001)."""
    __tablename__ = "miembro_competencia"

    # Clave primaria compuesta
    miembro_id: Mapped[int] = mapped_column(ForeignKey("miembro.id"), primary_key=True)
    competencia_id: Mapped[int] = mapped_column(ForeignKey("competencia.id"), primary_key=True)

    nivel_id: Mapped[int] = mapped_column(ForeignKey("nivel_competencia.id"))

    # Verificación
    verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_verificacion: Mapped[date | None] = mapped_column(Date)
    verificado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))

    # Observaciones
    observaciones: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    miembro: Mapped["Miembro"] = relationship(back_populates="competencias")
    competencia: Mapped["Competencia"] = relationship()
    nivel: Mapped["NivelCompetencia"] = relationship()
    verificado_por: Mapped["Usuario | None"] = relationship()


class TipoDocumento(Base):
    """Tipos de documento: CV, CERTIFICADO, AUTORIZACION, FOTO, etc."""
    __tablename__ = "tipo_documento_voluntario"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(String(500))
    requiere_caducidad: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class DocumentoMiembro(Base):
    """Documentos de un miembro: CV, certificados, etc. (RF-VC004)."""
    __tablename__ = "documento_miembro"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    miembro_id: Mapped[int] = mapped_column(ForeignKey("miembro.id"))
    tipo_documento_id: Mapped[int] = mapped_column(ForeignKey("tipo_documento_voluntario.id"))

    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)

    # Archivo
    archivo_url: Mapped[str] = mapped_column(String(500))
    archivo_nombre: Mapped[str] = mapped_column(String(255))
    archivo_tipo: Mapped[str | None] = mapped_column(String(50))  # MIME type
    archivo_tamano: Mapped[int | None]  # bytes

    # Fechas
    fecha_subida: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecha_caducidad: Mapped[date | None] = mapped_column(Date)

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Auditoría
    subido_por_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))

    # Relaciones
    miembro: Mapped["Miembro"] = relationship(back_populates="documentos")
    tipo_documento: Mapped["TipoDocumento"] = relationship()
    subido_por: Mapped["Usuario"] = relationship()


class TipoFormacion(Base):
    """Tipos de formación: CURSO, TALLER, CERTIFICACION, TITULO, etc."""
    __tablename__ = "tipo_formacion"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class FormacionMiembro(Base):
    """Formación recibida por un miembro (RF-VC004)."""
    __tablename__ = "formacion_miembro"

   id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    miembro_id: Mapped[int] = mapped_column(ForeignKey("miembro.id"))
    tipo_formacion_id: Mapped[int] = mapped_column(ForeignKey("tipo_formacion.id"))

    titulo: Mapped[str] = mapped_column(String(300))
    institucion: Mapped[str | None] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)

    # Fechas
    fecha_inicio: Mapped[date | None] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date)

    # Duración
    horas: Mapped[int | None]

    # Certificación
    certificado: Mapped[bool] = mapped_column(Boolean, default=False)
    documento_id: Mapped[int | None] = mapped_column(ForeignKey("documento_miembro.id"))

    # Competencias relacionadas
    competencias_adquiridas: Mapped[str | None] = mapped_column(Text)  # JSON o lista separada por comas

    # Organizado internamente?
    es_interna: Mapped[bool] = mapped_column(Boolean, default=False)  # Formación de la ONG

    # Relaciones
    miembro: Mapped["Miembro"] = relationship(back_populates="formaciones")
    tipo_formacion: Mapped["TipoFormacion"] = relationship()
    documento: Mapped["DocumentoMiembro | None"] = relationship()


# Imports para evitar circular imports
from .miembro import Miembro  # noqa: E402,F401
from .usuario import Usuario  # noqa: E402,F401
