"""Registro de Actividades de Tratamiento (RAT) — art. 30 RGPD.

Catálogo formal de las actividades de tratamiento de datos personales que
realiza la organización. Exportable como documento RAT ante la AEPD.

Por simplicidad evitamos catálogos satélite (bases jurídicas, categorías
de datos, categorías de interesados) y los modelamos como strings con
constantes en código; suelen ser estables y muy poco numerosos.
"""

import uuid
from datetime import date
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, Date, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel

if TYPE_CHECKING:
    from .encargado import EncargadoTratamiento


# Constantes — art. 6.1 RGPD
BASES_JURIDICAS = (
    'CONSENTIMIENTO',         # 6.1.a
    'EJECUCION_CONTRATO',     # 6.1.b
    'OBLIGACION_LEGAL',       # 6.1.c
    'INTERES_VITAL',          # 6.1.d
    'INTERES_PUBLICO',        # 6.1.e
    'INTERES_LEGITIMO',       # 6.1.f
)


class ActividadTratamiento(BaseModel):
    __tablename__ = 'rgpd_actividades_tratamiento'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    finalidad: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment='Para qué se tratan los datos (gestión de socios, cobro, comunicación…)'
    )

    base_juridica: Mapped[str] = mapped_column(
        String(40), nullable=False, index=True,
        comment='Una de BASES_JURIDICAS (art. 6.1 RGPD)'
    )
    base_juridica_detalle: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Artículo o norma concreta que sustenta la base jurídica'
    )

    categorias_interesados: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Lista (separada por comas o líneas) de categorías: socios, voluntarios, donantes…'
    )
    categorias_datos: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Lista de categorías de datos: identificativos, económicos, contacto…'
    )
    datos_sensibles: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True,
        comment='Trata categorías especiales del art. 9 RGPD (salud, religión, etc.)'
    )
    datos_sensibles_detalle: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    destinatarios_cesion: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Terceros a los que se ceden los datos (Hacienda, banco, federación…)'
    )

    transferencias_internacionales: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    transferencias_paises: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    transferencias_garantias: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Garantías aplicadas (cláusulas tipo, decisión adecuación, BCR…)'
    )

    plazo_conservacion: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Texto libre con plazo y norma que lo justifica'
    )
    medidas_seguridad: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='Resumen de medidas técnicas y organizativas'
    )

    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    fecha_alta_actividad: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_revision: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True,
        comment='Última revisión del registro (responsabilidad proactiva art. 5.2)'
    )

    encargados_rel: Mapped[List['ActividadTratamientoEncargado']] = relationship(
        'ActividadTratamientoEncargado', back_populates='actividad',
        cascade='all, delete-orphan', lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<ActividadTratamiento(nombre='{self.nombre}', base='{self.base_juridica}')>"


class ActividadTratamientoEncargado(BaseModel):
    """Relación N:M entre actividades de tratamiento y encargados (art. 30.1.e)."""
    __tablename__ = 'rgpd_actividades_encargados'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('rgpd_actividades_tratamiento.id', ondelete='CASCADE'),
        nullable=False, index=True
    )
    encargado_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('rgpd_encargados_tratamiento.id', ondelete='CASCADE'),
        nullable=False, index=True
    )

    actividad: Mapped['ActividadTratamiento'] = relationship(
        'ActividadTratamiento', back_populates='encargados_rel', lazy='selectin'
    )
    encargado: Mapped['EncargadoTratamiento'] = relationship(
        'EncargadoTratamiento', lazy='selectin'
    )
