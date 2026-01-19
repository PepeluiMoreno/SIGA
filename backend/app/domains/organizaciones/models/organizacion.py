"""
Modelo unificado de Organizaciones (internas y externas).

Este modelo unifica:
- Agrupaciones territoriales (internas de Europa Laica)
- Asociaciones colaboradoras (externas: ONGs, sindicatos, etc.)
"""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Numeric, Text, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel
from ....infrastructure.mixins import ContactoCompletoMixin
from ....infrastructure.mixins.sistema_mixin import CatalogoMixin


class TipoOrganizacion(BaseModel, CatalogoMixin):
    """
    Tipos de organizaciones (catálogo protegido del sistema).

    Incluye tanto agrupaciones territoriales de Europa Laica
    como asociaciones externas colaboradoras.

    Los tipos del sistema (AGRUP_ESTATAL, ASOC_ONG, etc.) están
    protegidos y no pueden ser eliminados.

    Hereda de CatalogoMixin:
    - codigo (String, unique, required)
    - nombre (String, required)
    - descripcion (String, optional)
    - orden (Integer, default 0)
    - activo (Boolean, default True)
    - es_sistema (Boolean, default False) - Marca registros protegidos
    """
    __tablename__ = 'tipos_organizacion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Los siguientes campos vienen de CatalogoMixin:
    # - codigo, nombre, descripcion, orden, activo, es_sistema

    # Categoría principal
    categoria: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # INTERNA, EXTERNA

    # Permite jerarquía (para agrupaciones territoriales)
    permite_jerarquia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Para convenios (solo asociaciones externas)
    permite_convenios: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relaciones
    organizaciones = relationship('Organizacion', back_populates='tipo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoOrganizacion(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Organizacion(BaseModel, ContactoCompletoMixin):
    """
    Modelo unificado de organizaciones internas y externas.

    Representa:
    - Agrupaciones territoriales de Europa Laica (internas)
    - Asociaciones colaboradoras externas (ONGs, sindicatos, etc.)

    Hereda de ContactoCompletoMixin para datos de contacto.
    """
    __tablename__ = 'organizaciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Tipo de organización
    tipo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('tipos_organizacion.id'),
        nullable=False,
        index=True
    )

    # Identificación básica
    codigo: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    nombre_corto: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    siglas: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)

    # Datos legales
    cif_nif: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    registro_oficial: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    numero_registro: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fecha_constitucion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Jerarquía (solo para agrupaciones territoriales internas)
    organizacion_padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey('organizaciones.id'),
        nullable=True,
        index=True
    )
    nivel: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Ámbito territorial
    ambito: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default='LOCAL',
        index=True
    )  # LOCAL, PROVINCIAL, AUTONOMICA, ESTATAL, INTERNACIONAL

    # Los campos de ubicación y contacto vienen de ContactoCompletoMixin:
    # - pais_id, provincia_id, municipio_id, direccion_id
    # - email, telefono_fijo, telefono_movil, web
    # - persona_contacto_nombre, persona_contacto_cargo
    # - persona_contacto_email, persona_contacto_telefono

    # Información adicional
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actividades_principales: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    numero_socios: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Estado
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    fecha_alta: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False)
    fecha_baja: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    motivo_baja: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Valoración (para asociaciones externas)
    valoracion: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    tipo = relationship('TipoOrganizacion', back_populates='organizaciones', lazy='selectin')
    pais = relationship('Pais', lazy='selectin')
    provincia = relationship('Provincia', lazy='selectin')
    municipio = relationship('Municipio', lazy='selectin')
    direccion = relationship('Direccion', lazy='selectin')

    # Jerarquía (para agrupaciones territoriales)
    organizacion_padre = relationship(
        'Organizacion',
        remote_side=[id],
        back_populates='organizaciones_hijas',
        lazy='selectin'
    )
    organizaciones_hijas: Mapped[List["Organizacion"]] = relationship(
        'Organizacion',
        back_populates='organizacion_padre',
        lazy='selectin'
    )

    # Convenios (para asociaciones externas)
    convenios = relationship('Convenio', back_populates='organizacion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Organizacion(nombre='{self.nombre}', tipo='{self.tipo_id}', ambito='{self.ambito}')>"

    @property
    def es_agrupacion_territorial(self) -> bool:
        """Verifica si es una agrupación territorial interna."""
        return self.tipo and self.tipo.categoria == 'INTERNA'

    @property
    def es_asociacion_externa(self) -> bool:
        """Verifica si es una asociación externa."""
        return self.tipo and self.tipo.categoria == 'EXTERNA'

    @property
    def tiene_convenio_vigente(self) -> bool:
        """Verifica si tiene algún convenio vigente."""
        if not self.convenios:
            return False
        return any(conv.esta_vigente for conv in self.convenios)


class EstadoConvenio(BaseModel):
    """Estados de convenios de colaboración."""
    __tablename__ = 'estados_convenio'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    convenios = relationship('Convenio', back_populates='estado', lazy='selectin')

    def __repr__(self) -> str:
        return f"<EstadoConvenio(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Convenio(BaseModel):
    """
    Convenios de colaboración con organizaciones externas.

    Incluye acuerdos, protocolos, convenios marco, etc.
    """
    __tablename__ = 'convenios'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Organización (asociación externa)
    organizacion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('organizaciones.id'),
        nullable=False,
        index=True
    )

    # Identificación del convenio
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default='CONVENIO'
    )  # CONVENIO, ACUERDO, PROTOCOLO, MEMORANDUM

    # Fechas
    fecha_firma: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    renovable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Contenido
    objeto: Mapped[str] = mapped_column(Text, nullable=False)
    compromisos_organizacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    compromisos_propios: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    beneficios: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Aspectos económicos
    tiene_aportacion_economica: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    importe_aportacion: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    periodicidad_aportacion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Documentación
    documento_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    anexos_urls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Responsables
    responsable_organizacion_propia: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    responsable_organizacion_externa: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Estado
    estado_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('estados_convenio.id'),
        nullable=False,
        index=True
    )

    # Información adicional
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relaciones
    organizacion = relationship('Organizacion', back_populates='convenios', lazy='selectin')
    estado = relationship('EstadoConvenio', back_populates='convenios', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Convenio(codigo='{self.codigo}', nombre='{self.nombre}')>"

    @property
    def esta_vigente(self) -> bool:
        """Verifica si el convenio está vigente basado en fechas."""
        hoy = date.today()
        if hoy < self.fecha_inicio:
            return False
        if self.fecha_fin and hoy > self.fecha_fin:
            return False
        return True

    @property
    def dias_hasta_vencimiento(self) -> Optional[int]:
        """Calcula los días hasta el vencimiento del convenio."""
        if not self.fecha_fin:
            return None
        dias = (self.fecha_fin - date.today()).days
        return dias if dias > 0 else 0
