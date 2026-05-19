"""Modelos de reuniones, orden del día, acuerdos y votaciones.

Cubre la gestión de Asambleas Generales y reuniones de Junta Directiva
según la Ley Orgánica 1/2002 de asociaciones.
"""

import uuid
from datetime import date, datetime
from typing import Optional
from enum import Enum

from sqlalchemy import (
    String, Boolean, Uuid, ForeignKey, Date, DateTime,
    Text, Integer, Numeric, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel, InmutableMixin


class TipoReunion(InmutableMixin, BaseModel):
    """Tipos de reunión: Asamblea General ordinaria/extraordinaria, Junta Directiva, etc."""
    __tablename__ = 'sec_tipos_reunion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Configuración legal
    organo: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ASAMBLEA_GENERAL | JUNTA_DIRECTIVA | COMISION

    # Quórum por defecto (puede sobreescribirse en cada reunión)
    quorum_primera_convocatoria: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="% mínimo de asistentes para quórum en primera convocatoria"
    )
    quorum_segunda_convocatoria: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="% mínimo en segunda convocatoria (0 = cualquier número)"
    )

    # Antelación mínima para convocatoria (en días)
    antelacion_minima_dias: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relaciones
    reuniones = relationship('Reunion', back_populates='tipo_reunion', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoReunion(nombre='{self.nombre}', organo='{self.organo}')>"


class Reunion(BaseModel):
    """Reunión de un órgano de gobierno.

    Cubre desde la convocatoria hasta la aprobación del acta.
    Estado: CONVOCADA → CELEBRADA → ACTA_BORRADOR → ACTA_APROBADA
    """
    __tablename__ = 'sec_reuniones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    tipo_reunion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_tipos_reunion.id'), nullable=False, index=True
    )
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('unidades_organizativas.id'), nullable=True, index=True,
        comment="Agrupación que celebra la reunión (null = organización central)"
    )

    # Convocatoria
    numero_convocatoria: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Número correlativo dentro del tipo de reunión y año"
    )
    anio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    fecha_convocatoria: Mapped[date] = mapped_column(Date, nullable=False)

    # Celebración
    fecha_celebracion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    lugar: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    es_telematica: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    plataforma_telematica: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Segunda convocatoria
    tiene_segunda_convocatoria: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_segunda_convocatoria: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    convocatoria_utilizada: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="1 o 2: qué convocatoria se utilizó finalmente"
    )

    # Quórum
    socios_totales: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    socios_presentes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    socios_representados: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hay_quorum: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Estado
    estado: Mapped[str] = mapped_column(
        String(30), nullable=False, default='CONVOCADA', index=True
    )  # CONVOCADA | CELEBRADA | ACTA_BORRADOR | ACTA_APROBADA | CANCELADA

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    tipo_reunion = relationship('TipoReunion', back_populates='reuniones', lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', lazy='selectin')
    asistentes = relationship('AsistenteReunion', back_populates='reunion', lazy='selectin')
    puntos_orden_dia = relationship(
        'PuntoOrdenDia', back_populates='reunion',
        lazy='selectin', order_by='PuntoOrdenDia.orden'
    )
    acta = relationship('Acta', back_populates='reunion', uselist=False, lazy='selectin')

    def __repr__(self) -> str:
        return f"<Reunion(tipo='{self.tipo_reunion_id}', fecha='{self.fecha_celebracion}', estado='{self.estado}')>"

    @property
    def quorum_asistencia(self) -> Optional[float]:
        """Porcentaje de asistencia sobre el total de socios."""
        if self.socios_totales and self.socios_totales > 0:
            presentes = (self.socios_presentes or 0) + (self.socios_representados or 0)
            return round(presentes / self.socios_totales * 100, 2)
        return None


class AsistenteReunion(BaseModel):
    """Registro de asistencia de un miembro a una reunión."""
    __tablename__ = 'sec_asistentes_reunion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    reunion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_reuniones.id', ondelete='CASCADE'), nullable=False, index=True
    )
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=False, index=True
    )

    # Forma de asistencia
    tipo_asistencia: Mapped[str] = mapped_column(
        String(20), nullable=False, default='PRESENCIAL'
    )  # PRESENCIAL | TELEMATICA | REPRESENTADO | EXCUSADO

    # Si asiste representado
    representado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True
    )

    # Cargo que ostenta en la reunión (si es órgano directivo)
    cargo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relaciones
    reunion = relationship('Reunion', back_populates='asistentes')
    miembro = relationship('Miembro', foreign_keys=[miembro_id], lazy='selectin')
    representado_por = relationship('Miembro', foreign_keys=[representado_por_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<AsistenteReunion(reunion_id='{self.reunion_id}', miembro_id='{self.miembro_id}')>"


class PuntoOrdenDia(BaseModel):
    """Punto del orden del día de una reunión."""
    __tablename__ = 'sec_puntos_orden_dia'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    reunion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_reuniones.id', ondelete='CASCADE'), nullable=False, index=True
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tipo de punto
    tipo: Mapped[str] = mapped_column(
        String(30), nullable=False, default='ORDINARIO'
    )  # ORDINARIO | RUEGOS_PREGUNTAS | INFORMATIVO

    # Relaciones
    reunion = relationship('Reunion', back_populates='puntos_orden_dia')
    acuerdos = relationship(
        'Acuerdo', back_populates='punto_orden_dia',
        lazy='selectin', order_by='Acuerdo.numero'
    )

    def __repr__(self) -> str:
        return f"<PuntoOrdenDia(orden={self.orden}, titulo='{self.titulo[:40]}')>"


class Acuerdo(BaseModel):
    """Acuerdo adoptado en un punto del orden del día.

    Cada acuerdo tiene su propio resultado de votación y puede
    generar un CertificadoAcuerdo independiente.
    """
    __tablename__ = 'sec_acuerdos'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    punto_orden_dia_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_puntos_orden_dia.id', ondelete='CASCADE'),
        nullable=False, index=True
    )
    numero: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Número de acuerdo dentro del punto"
    )

    # Contenido
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    # Tipo de mayoría requerida
    tipo_mayoria: Mapped[str] = mapped_column(
        String(30), nullable=False, default='SIMPLE'
    )  # SIMPLE | ABSOLUTA | DOS_TERCIOS | UNANIMIDAD

    # Resultado
    resultado: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # APROBADO | RECHAZADO | RETIRADO | APLAZADO

    # Seguimiento
    responsable_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('miembros.id'), nullable=True
    )
    fecha_limite_ejecucion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado_ejecucion: Mapped[str] = mapped_column(
        String(20), nullable=False, default='PENDIENTE', index=True
    )  # PENDIENTE | EN_CURSO | COMPLETADO | ARCHIVADO

    observaciones_ejecucion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    punto_orden_dia = relationship('PuntoOrdenDia', back_populates='acuerdos')
    votacion = relationship('VotacionAcuerdo', back_populates='acuerdo', uselist=False, lazy='selectin')
    responsable = relationship('Miembro', foreign_keys=[responsable_id], lazy='selectin')
    certificados = relationship('CertificadoAcuerdo', back_populates='acuerdo', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Acuerdo(numero={self.numero}, resultado='{self.resultado}')>"


class VotacionAcuerdo(BaseModel):
    """Resultado de la votación de un acuerdo."""
    __tablename__ = 'sec_votaciones_acuerdo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    acuerdo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_acuerdos.id', ondelete='CASCADE'),
        nullable=False, unique=True, index=True
    )

    votos_favor: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    votos_contra: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    abstenciones: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    votos_nulos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    es_votacion_secreta: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relaciones
    acuerdo = relationship('Acuerdo', back_populates='votacion')

    @property
    def total_votos(self) -> int:
        return self.votos_favor + self.votos_contra + self.abstenciones + self.votos_nulos

    def __repr__(self) -> str:
        return f"<VotacionAcuerdo(favor={self.votos_favor}, contra={self.votos_contra})>"
