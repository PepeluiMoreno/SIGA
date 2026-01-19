"""Modelo de miembros (socios) de la organización."""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class TipoMiembro(BaseModel):
    """Tipos de miembro (socio, simpatizante, colaborador, etc.)."""
    __tablename__ = 'tipos_miembro'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Características del tipo
    requiere_cuota: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    puede_votar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    miembros = relationship('Miembro', back_populates='tipo_miembro', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoMiembro(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Miembro(BaseModel):
    """Miembro (socio) de la organización."""
    __tablename__ = 'miembros'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Datos personales
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    apellido1: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    apellido2: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Tipo de miembro
    tipo_miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_miembro.id'), nullable=False, index=True)

    # Estado del miembro (ciclo de vida)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_miembro.id'), nullable=False, index=True)

    # Documento de identidad
    tipo_documento: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # DNI, NIE, PASAPORTE
    numero_documento: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    pais_documento_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('paises.id'), nullable=True)

    # Datos de contacto (se moverá a modelo Direccion)
    direccion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    codigo_postal: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    localidad: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    provincia_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('provincias.id'), nullable=True, index=True)
    pais_domicilio_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('paises.id'), nullable=True, index=True)

    telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    telefono2: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)

    # Pertenencia organizativa
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('agrupaciones_territoriales.id'), nullable=True, index=True)

    # Datos bancarios (IBAN encriptado)
    iban: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Encriptado

    # Fechas de afiliación
    fecha_alta: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False, index=True)
    fecha_baja: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    motivo_baja: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Voluntariado
    es_voluntario: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    disponibilidad: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # COMPLETA, FINES_SEMANA, TARDES, etc.
    horas_disponibles_semana: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    profesion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    nivel_estudios: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    experiencia_voluntariado: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    intereses: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    observaciones_voluntariado: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Movilidad
    puede_conducir: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vehiculo_propio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disponibilidad_viajar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relaciones
    tipo_miembro = relationship('TipoMiembro', back_populates='miembros', lazy='selectin')
    estado = relationship('EstadoMiembro', lazy='selectin')
    agrupacion = relationship('AgrupacionTerritorial', lazy='selectin')
    pais_documento = relationship('Pais', foreign_keys=[pais_documento_id], lazy='selectin')
    pais_domicilio = relationship('Pais', foreign_keys=[pais_domicilio_id], lazy='selectin')
    provincia = relationship('Provincia', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Miembro(nombre='{self.nombre} {self.apellido1}', tipo='{self.tipo_miembro_id}')>"

    @property
    def nombre_completo(self) -> str:
        """Devuelve el nombre completo del miembro."""
        if self.apellido2:
            return f"{self.nombre} {self.apellido1} {self.apellido2}"
        return f"{self.nombre} {self.apellido1}"

    @property
    def es_miembro_activo(self) -> bool:
        """Determina si el miembro está activo.

        Un miembro se considera activo si:
        - No tiene fecha de baja (fecha_baja es None)
        - Es voluntario (es_voluntario=True)
        - Tiene sus habilidades informadas (profesion, nivel_estudios, intereses)
        """
        if self.fecha_baja is not None:
            return False

        if not self.es_voluntario:
            return False

        # Verificar que tenga al menos algunos campos de habilidades informados
        tiene_habilidades = (
            (self.profesion is not None and self.profesion.strip() != "") or
            (self.nivel_estudios is not None and self.nivel_estudios.strip() != "") or
            (self.intereses is not None and self.intereses.strip() != "")
        )

        return tiene_habilidades
