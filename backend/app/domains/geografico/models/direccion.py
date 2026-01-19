"""Modelos de datos geográficos, direcciones y agrupaciones territoriales."""

import uuid
from typing import Optional, List

from sqlalchemy import String, Integer, Uuid, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class Pais(BaseModel):
    """Modelo de países."""
    __tablename__ = 'paises'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(2), unique=True, nullable=False, index=True)  # ISO 3166-1 alpha-2
    codigo_iso3: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)  # ISO 3166-1 alpha-3
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    nombre_oficial: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    codigo_telefono: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # Ej: +34
    continente: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    activo: Mapped[bool] = mapped_column(Integer, default=True, nullable=False, index=True)

    # Relaciones
    provincias = relationship('Provincia', back_populates='pais', lazy='selectin')
    direcciones = relationship('Direccion', back_populates='pais', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Pais(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Provincia(BaseModel):
    """Modelo de provincias/estados."""
    __tablename__ = 'provincias'
    __table_args__ = (
        UniqueConstraint('pais_id', 'codigo', name='uq_provincia_pais_codigo'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    pais_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('paises.id'), nullable=False, index=True)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # Código provincial (ej: '28' para Madrid)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    activo: Mapped[bool] = mapped_column(Integer, default=True, nullable=False, index=True)

    # Relaciones
    pais = relationship('Pais', back_populates='provincias', lazy='selectin')
    municipios = relationship('Municipio', back_populates='provincia', lazy='selectin')
    direcciones = relationship('Direccion', back_populates='provincia', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Provincia(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Municipio(BaseModel):
    """Modelo de municipios/ciudades."""
    __tablename__ = 'municipios'
    __table_args__ = (
        UniqueConstraint('provincia_id', 'codigo', name='uq_municipio_provincia_codigo'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    provincia_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('provincias.id'), nullable=False, index=True)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # Código INE
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    codigo_postal: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # CP principal
    activo: Mapped[bool] = mapped_column(Integer, default=True, nullable=False, index=True)

    # Relaciones
    provincia = relationship('Provincia', back_populates='municipios', lazy='selectin')
    direcciones = relationship('Direccion', back_populates='municipio', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Municipio(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Direccion(BaseModel):
    """Modelo de direcciones completas."""
    __tablename__ = 'direcciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Tipo de dirección
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)  # PRINCIPAL, FISCAL, ENVIO, FACTURACION

    # Campos de dirección
    via_tipo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Calle, Avenida, Plaza, etc.
    via_nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    numero: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    piso: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    puerta: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    bloque: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    escalera: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    codigo_postal: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Referencias geográficas
    municipio_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('municipios.id'), nullable=True, index=True)
    provincia_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('provincias.id'), nullable=False, index=True)
    pais_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('paises.id'), nullable=False, index=True)

    # Campos adicionales
    localidad: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Para localidades no catalogadas
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    coordenadas_lat: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    coordenadas_lon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Validación
    validada: Mapped[bool] = mapped_column(Integer, default=False, nullable=False)
    fecha_validacion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relaciones
    pais = relationship('Pais', back_populates='direcciones', lazy='selectin')
    provincia = relationship('Provincia', back_populates='direcciones', lazy='selectin')
    municipio = relationship('Municipio', back_populates='direcciones', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Direccion(via='{self.via_nombre}', cp='{self.codigo_postal}')>"

    @property
    def direccion_completa(self) -> str:
        """Genera la dirección completa en formato texto."""
        partes = []

        # Tipo de vía y nombre
        if self.via_tipo:
            partes.append(f"{self.via_tipo} {self.via_nombre}")
        else:
            partes.append(self.via_nombre)

        # Número
        if self.numero:
            partes.append(f"nº {self.numero}")

        # Bloque, escalera, piso, puerta
        detalles = []
        if self.bloque:
            detalles.append(f"Bloque {self.bloque}")
        if self.escalera:
            detalles.append(f"Esc. {self.escalera}")
        if self.piso:
            detalles.append(f"{self.piso}º")
        if self.puerta:
            detalles.append(self.puerta)

        if detalles:
            partes.append(", ".join(detalles))

        # CP y localidad
        localidad_nombre = self.localidad
        if self.municipio:
            localidad_nombre = self.municipio.nombre

        if localidad_nombre:
            partes.append(f"{self.codigo_postal} {localidad_nombre}")
        else:
            partes.append(self.codigo_postal)

        # Provincia y país
        if self.provincia:
            partes.append(self.provincia.nombre)

        if self.pais and self.pais.codigo != 'ES':  # Solo incluir país si no es España
            partes.append(self.pais.nombre)

        return ", ".join(partes)

    @property
    def direccion_corta(self) -> str:
        """Genera una versión corta de la dirección."""
        partes = [self.via_nombre]

        if self.numero:
            partes.append(self.numero)

        if self.piso:
            partes.append(f"{self.piso}º")

        return " ".join(partes)


class AgrupacionTerritorial(BaseModel):
    """
    Agrupaciones territoriales de la organización política.

    Representa las estructuras organizativas territoriales como
    agrupaciones locales, provinciales, autonómicas, etc.
    """
    __tablename__ = 'agrupaciones_territoriales'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Identificación
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    nombre_corto: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Tipo de agrupación
    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # LOCAL, PROVINCIAL, AUTONOMICO, NACIONAL

    # Jerarquía
    agrupacion_padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey('agrupaciones_territoriales.id'),
        nullable=True,
        index=True
    )
    nivel: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1=Local, 2=Provincial, 3=Autonómico, 4=Nacional

    # Ubicación geográfica
    pais_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('paises.id'), nullable=False, index=True)
    provincia_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('provincias.id'), nullable=True, index=True)
    municipio_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('municipios.id'), nullable=True, index=True)
    direccion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('direcciones.id'), nullable=True)

    # Datos de contacto
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    web: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Información adicional
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Integer, default=True, nullable=False, index=True)

    # Relaciones
    pais = relationship('Pais', lazy='selectin')
    provincia = relationship('Provincia', lazy='selectin')
    municipio = relationship('Municipio', lazy='selectin')
    direccion = relationship('Direccion', lazy='selectin')

    # Relación jerárquica
    agrupacion_padre = relationship(
        'AgrupacionTerritorial',
        remote_side=[id],
        back_populates='agrupaciones_hijas',
        lazy='selectin'
    )
    agrupaciones_hijas: Mapped[List["AgrupacionTerritorial"]] = relationship(
        'AgrupacionTerritorial',
        back_populates='agrupacion_padre',
        lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<AgrupacionTerritorial(codigo='{self.codigo}', nombre='{self.nombre}', tipo='{self.tipo}')>"

    @property
    def nombre_completo(self) -> str:
        """Genera el nombre completo incluyendo la jerarquía."""
        if self.agrupacion_padre:
            return f"{self.nombre} ({self.agrupacion_padre.nombre})"
        return self.nombre

    @property
    def ruta_jerarquica(self) -> str:
        """Genera la ruta jerárquica completa."""
        ruta = [self.nombre]
        actual = self.agrupacion_padre

        while actual:
            ruta.insert(0, actual.nombre)
            actual = actual.agrupacion_padre

        return " > ".join(ruta)
