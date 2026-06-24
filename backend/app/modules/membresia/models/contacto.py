"""Contacto: entidad que puede participar en la organización.

Puede ser PERSONA_FISICA o PERSONA_JURIDICA (empresa, ONG, etc.).
Single-table inheritance: una tabla, discriminador `tipo`, campos condicionales.

Cualquier contacto puede participar (firmar campañas, donar, hacer voluntariado, convenios…).
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.actividades.models.campana import FirmaCampania
    from .vinculacion import Vinculacion
    from .participacion import Participacion


class Contacto(BaseModel):
    """Persona física u jurídica que puede participar en la organización.
    
    Attributes:
        tipo: 'PERSONA_FISICA' o 'PERSONA_JURIDICA' (discriminador)
        
    Para PERSONA_FISICA:
        nombre, apellido1, apellido2, sexo, fecha_nacimiento, documento, profesion, estudios
        
    Para PERSONA_JURIDICA:
        razon_social, cif, actividad_principal, representante_legal_id (FK a PF)
        
    Comunes: dirección, contacto, RGPD, auditoría, vinculaciones, participaciones
    """

    __tablename__ = "contactos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Discriminador de tipo
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # PERSONA_FISICA | PERSONA_JURIDICA

    # ========== IDENTIDAD (PERSONA_FISICA o PERSONA_JURIDICA) ==========
    # Para PF: nombre + apellidos. Para PJ: razon_social.
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    apellido1: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    apellido2: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    razon_social: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # Para PJ

    # ========== DOCUMENTO DE IDENTIDAD ==========
    # Para PF: DNI/NIE/pasaporte. Para PJ: CIF.
    tipo_documento: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # DNI, NIE, PASAPORTE, CIF
    numero_documento: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    pais_documento_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("paises.id"), nullable=True
    )

    # ========== DATOS PERSONA FÍSICA ==========
    sexo: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)  # H, M
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    pais_nacimiento_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("paises.id"), nullable=True
    )
    profesion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    nivel_estudios_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("niveles_estudios.id"), nullable=True
    )

    # ========== DATOS PERSONA JURÍDICA ==========
    cif: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)  # CIF de la empresa
    tipo_entidad_juridica_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("tipos_entidad_juridica.id"), nullable=True, index=True
    )  # Forma jurídica: asociación, fundación, empresa, administración…
    actividad_principal: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    representante_legal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("contactos.id"), nullable=True, index=True
    )  # FK a otro Contacto (persona física)

    # ========== DOMICILIO (COMÚN) ==========
    direccion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    codigo_postal: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    localidad: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    provincia_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("provincias.id"), nullable=True
    )
    pais_domicilio_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("paises.id"), nullable=True
    )

    # ========== CONTACTO (COMÚN) ==========
    telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    telefono2: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)

    # ========== CONTEXTO ORGANIZATIVO ==========
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("unidades_organizativas.id"), nullable=True, index=True
    )
    foto_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ========== RGPD (COMÚN) ==========
    solicita_supresion_datos: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_solicitud_supresion: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    fecha_limite_retencion: Mapped[Optional[date]] = mapped_column(nullable=True)
    datos_anonimizados: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_anonimizacion: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # ========== ESTADO (COMÚN) ==========
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # ========== RELACIONES ==========
    # Personas jurídicas que tienen este contacto como representante legal
    contactos_donde_represento: Mapped[list[Contacto]] = relationship(
        back_populates="representante_legal",
        remote_side=[id],
        foreign_keys=[representante_legal_id],
        lazy="select"
    )
    representante_legal: Mapped[Optional[Contacto]] = relationship(
        back_populates="contactos_donde_represento",
        remote_side=[representante_legal_id],
        lazy="selectin"
    )

    vinculaciones: Mapped[list[Vinculacion]] = relationship(
        back_populates="contacto",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    participaciones: Mapped[list[Participacion]] = relationship(
        back_populates="contacto",
        cascade="all, delete-orphan",
        lazy="select"
    )
    firmas_campania: Mapped[list[FirmaCampania]] = relationship(
        back_populates="contacto",
        foreign_keys="FirmaCampania.contacto_id",
        lazy="select"
    )
    # PENDIENTE (fuera de este bundle): reconducir RGPD a Contacto. Los modelos
    # de proteccion_datos (Consentimiento, SolicitudDerechoRGPD) aún cuelgan de
    # miembros.id; cuando se reconduzcan a contacto_id se añadirán aquí las
    # relaciones inversas consentimientos_rgpd / solicitudes_derechos.

    def __repr__(self) -> str:
        if self.tipo == "PERSONA_FISICA":
            return f"<Contacto PF(nombre='{self.nombre}', email='{self.email}')>"
        else:
            return f"<Contacto PJ(razon_social='{self.razon_social}', cif='{self.cif}')>"

    @property
    def nombre_completo(self) -> str:
        """Retorna nombre completo (PF) o razón social (PJ)."""
        if self.tipo == "PERSONA_FISICA":
            partes = [self.nombre]
            if self.apellido1:
                partes.append(self.apellido1)
            if self.apellido2:
                partes.append(self.apellido2)
            return " ".join(partes)
        else:
            return self.razon_social or self.nombre

    @property
    def vinculaciones_vigentes(self) -> list[Vinculacion]:
        """Retorna vinculaciones actualmente vigentes (sin cierre)."""
        return [v for v in self.vinculaciones if v.fecha_fin is None and not v.eliminado]

    def tiene_vinculacion_tipo(self, codigo_tipo: str) -> bool:
        """Comprueba si tiene una vinculación vigente de un tipo dado."""
        return any(
            v.tipo_vinculacion.codigo == codigo_tipo
            for v in self.vinculaciones_vigentes
            if v.tipo_vinculacion
        )
