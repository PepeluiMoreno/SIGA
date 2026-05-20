"""Modelo de miembros (miembros) de la organización."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .nivel_estudios import NivelEstudios

from sqlalchemy import String, Integer, Uuid, ForeignKey, Date, Boolean, Text, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property

from ....infrastructure.base_model import BaseModel, InmutableMixin


# Constantes para segmentación
EDAD_JOVEN_LIMITE = 30  # Menores de 30 años se consideran jóvenes


class TipoMiembro(InmutableMixin, BaseModel):
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

    # Flujo 1 D1.2: motivo de reducción aplicado por defecto al generar CuotaAnual
    motivo_reduccion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('motivos_reduccion_cuota.id', ondelete='SET NULL'), nullable=True, index=True
    )

    # Relaciones
    miembros = relationship('Miembro', back_populates='tipo_miembro', lazy='selectin')
    motivo_reduccion = relationship(
        'MotivoReduccionCuota', foreign_keys=[motivo_reduccion_id], lazy='selectin'
    )

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
    pais_nacimiento_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('paises.id'), nullable=True)

    # Tipo de miembro (nullable: puede registrarse sin tipo y completarse después)
    tipo_miembro_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('tipos_miembro.id'), nullable=True, index=True)

    # Motivo de reducción individual (override del que trae el TipoMiembro)
    # Si está informado, prevalece sobre `tipo_miembro.motivo_reduccion_id` al calcular cuota.
    # Solo afecta a cuotas futuras (D1.5: porcentaje congelado si ya hay recibos emitidos).
    motivo_reduccion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('motivos_reduccion_cuota.id'), nullable=True, index=True
    )

    # Incremento voluntario de cuota: el socio decide pagar de más sobre la cuota
    # base. Cantidad fija en euros que se SUMA al importe al generar las cuotas.
    # No requiere aprobación (a diferencia de la reducción): solo se graba.
    incremento_cuota: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal('0.00'), server_default='0'
    )
    incremento_cuota_obs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Estado del miembro (nullable: puede registrarse sin estado y asignarse después)
    estado_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('estados_miembro.id'), nullable=True, index=True)

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
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('unidades_organizativas.id'), nullable=True, index=True)

    # Datos bancarios / pago
    iban: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    swift_bic: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    forma_pago_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('formas_pago.id'), nullable=True, index=True)

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
    es_socio_honor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Voluntariado
    es_voluntario: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    disponibilidad: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # COMPLETA, FINES_SEMANA, TARDES, etc.
    horas_disponibles_semana: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    profesion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    nivel_estudios_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('niveles_estudios.id', ondelete='SET NULL'), nullable=True, index=True
    )
    experiencia_voluntariado: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    intereses: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    observaciones_voluntariado: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Imagen de perfil
    foto_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Movilidad
    puede_conducir: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vehiculo_propio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disponibilidad_viajar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relaciones
    tipo_miembro = relationship('TipoMiembro', back_populates='miembros', lazy='selectin')
    motivo_reduccion = relationship(
        'MotivoReduccionCuota', foreign_keys=[motivo_reduccion_id], lazy='selectin'
    )
    estado = relationship('EstadoMiembro', lazy='selectin')
    usuario = relationship('Usuario', back_populates='miembro', foreign_keys='Usuario.miembro_id', uselist=False, lazy='selectin')
    motivo_baja_rel = relationship('MotivoBaja', back_populates='miembros', lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', lazy='selectin')
    pais_documento = relationship('Pais', foreign_keys=[pais_documento_id], lazy='selectin')
    pais_domicilio = relationship('Pais', foreign_keys=[pais_domicilio_id], lazy='selectin')
    pais_nacimiento = relationship('Pais', foreign_keys=[pais_nacimiento_id], lazy='selectin')
    provincia = relationship('Provincia', lazy='selectin')
    forma_pago = relationship('FormaPago', lazy='selectin')
    nivel_estudios_rel: Mapped[Optional['NivelEstudios']] = relationship(
        'NivelEstudios', back_populates='miembros', lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<Miembro(nombre='{self.nombre} {self.apellido1}', tipo='{self.tipo_miembro_id}')>"

    @validates('nombre', 'apellido1', 'apellido2')
    def _normalizar_nombre(self, key, value):
        if value is None:
            return value
        return value.strip().title()

    @property
    def tiene_acceso(self) -> bool:
        """True si el miembro tiene un usuario vinculado en el sistema."""
        return self.usuario is not None

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
        - Tiene sus habilidades informadas (profesion, nivel_estudios_id, intereses)
        """
        if self.fecha_baja is not None:
            return False

        if not self.es_voluntario:
            return False

        # Verificar que tenga al menos algunos campos de habilidades informados
        tiene_habilidades = (
            (self.profesion is not None and self.profesion.strip() != "") or
            (self.nivel_estudios_id is not None) or
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

        Se consulta via UsuarioRol con roles ORGANIZACION o HistorialNombramiento.
        Este property es solo informativo; la consulta real se hace por servicio.
        """
        return False  # Se resuelve via historial_nombramientos
