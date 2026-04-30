"""Modelo de miembros (miembros) de la organización."""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ....infrastructure.base_model import BaseModel


# Constantes para segmentación
EDAD_JOVEN_LIMITE = 30  # Menores de 30 años se consideran jóvenes


class TipoMiembro(BaseModel):
    """Tipos de miembro (miembro, simpatizante, colaborador, etc.)."""
    __tablename__ = 'tipos_miembro'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Características del tipo
    requiere_cuota: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    puede_votar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    miembros = relationship('Miembro', back_populates='tipo_miembro', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoMiembro(nombre='{self.nombre}')>"


class Miembro(BaseModel):
    """Miembro (miembro) de la organización."""
    __tablename__ = 'miembros'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Datos personales
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    apellido1: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    apellido2: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sexo: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)  # H=Hombre, M=Mujer
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Tipo de miembro
    tipo_miembro_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('tipos_miembro.id'), nullable=False, index=True)

    # Estado del miembro (ciclo de vida)
    estado_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('estados_miembro.id'), nullable=False, index=True)

    # Documento de identidad
    tipo_documento: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # DNI, NIE, PASAPORTE
    numero_documento: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)  # Aumentado para datos encriptados
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

    # Cargo en la junta directiva (si aplica)
    cargo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('tipos_cargo.id'), nullable=True, index=True)

    # Datos bancarios (IBAN encriptado)
    iban: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Encriptado

    # Fechas de afiliación
    fecha_alta: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False, index=True)
    fecha_baja: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    motivo_baja_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('motivos_baja.id'), nullable=True, index=True)
    motivo_baja_texto: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Texto libre adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Observaciones generales (texto largo sin límite)

    # RGPD - Gestión de datos personales
    solicita_supresion_datos: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_solicitud_supresion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_limite_retencion: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)  # fecha_baja + 6 años
    datos_anonimizados: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    fecha_anonimizacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

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
    motivo_baja_rel = relationship('MotivoBaja', back_populates='miembros', lazy='selectin')
    agrupacion = relationship('AgrupacionTerritorial', lazy='selectin')
    cargo = relationship('TipoCargo', back_populates='miembros', lazy='selectin')
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

    @property
    def edad(self) -> Optional[int]:
        """Calcula la edad del miembro a partir de su fecha de nacimiento."""
        if not self.fecha_nacimiento:
            return None
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        # Ajustar si aún no ha cumplido años este año
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad

    @property
    def es_joven(self) -> bool:
        """Determina si el miembro es joven (menor de 30 años).

        Usado para segmentación de campañas dirigidas a jóvenes.
        Los jóvenes tienen cuota reducida de 5€.
        """
        edad = self.edad
        if edad is None:
            return False
        return edad < EDAD_JOVEN_LIMITE

    @property
    def es_simpatizante(self) -> bool:
        """Determina si el miembro es simpatizante (no paga cuota).

        Se determina por el tipo de membresía SIMPATIZANTE.
        Usado para segmentación de campañas.
        """
        if not self.tipo_miembro:
            return False
        return self.tipo_miembro.codigo == 'SIMPATIZANTE'

    @property
    def es_voluntario_disponible(self) -> bool:
        """Determina si el miembro es voluntario con disponibilidad para colaborar.

        Un voluntario disponible es aquel que:
        - Tiene es_voluntario=True
        - Está activo (sin fecha de baja)
        - Tiene alguna disponibilidad declarada

        Usado para segmentación de campañas que requieren voluntarios.
        """
        if not self.es_voluntario:
            return False
        if self.fecha_baja is not None:
            return False
        # Tiene alguna disponibilidad declarada
        return self.disponibilidad is not None or (self.horas_disponibles_semana or 0) > 0

    @property
    def es_junta_directiva(self) -> bool:
        """Determina si el miembro pertenece a la junta directiva.

        Un miembro pertenece a la junta directiva si tiene un cargo asignado.
        """
        return self.cargo_id is not None
