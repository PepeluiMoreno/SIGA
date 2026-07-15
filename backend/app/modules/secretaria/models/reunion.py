"""Modelos de reuniones, orden del día, acuerdos y votaciones.

Cubre la gestión de Asambleas Generales y reuniones de Junta Directiva
según la Ley Orgánica 1/2002 de asociaciones.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
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

    # Órgano de gobierno que se reúne. FK al catálogo REAL de tipos de órgano
    # (`tipos_organo`, módulo acceso), no un string libre: es el mismo órgano que
    # configura la gobernanza, para que un acuerdo sepa quién lo adoptó.
    tipo_organo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('tipos_organo.id', ondelete='RESTRICT'),
        nullable=False, index=True,
    )

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
    tipo_organo = relationship('TipoOrgano', lazy='selectin')

    def __repr__(self) -> str:
        return f"<TipoReunion(nombre='{self.nombre}', tipo_organo_id='{self.tipo_organo_id}')>"


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
    # El órgano CONCRETO que se reúne (p. ej. «la Junta Directiva de Madrid»), con
    # su composición real. Es quien adopta los acuerdos: sin esto, un acuerdo no
    # sabe quién lo tomó. Nullable durante la transición (reuniones sin órgano
    # instanciado); el objetivo es que siempre esté informado.
    organo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('organos.id', ondelete='RESTRICT'), nullable=True, index=True,
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
    plataforma_telematica: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True,
        comment='Texto libre (legacy). Cuando hay plataforma_telematica_id se prefiere este último.'
    )
    plataforma_telematica_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('sec_plataformas_telematicas.id'), nullable=True, index=True,
    )
    datos_conexion_telematica: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment='JSON con valores de los campos definidos por la plataforma (URL, sala, password…)'
    )

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
    estado_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('estados_reunion.id'), nullable=True, index=True
    )
    # Código de máquina denormalizado para queries de lógica sin JOIN
    estado_codigo: Mapped[str] = mapped_column(
        String(30), nullable=False, default='CONVOCADA', index=True
    )

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Actividad generada automáticamente al convocar (para integración contable/presupuestaria)
    actividad_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('actividades.id'), nullable=True,
        comment="Actividad creada automáticamente al convocar — permite presupuestar y contabilizar gastos"
    )

    # Relaciones
    tipo_reunion = relationship('TipoReunion', back_populates='reuniones', lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', lazy='selectin')
    organo = relationship('Organo', lazy='selectin')
    asistentes = relationship('AsistenteReunionSecretaria', back_populates='reunion', lazy='selectin')
    puntos_orden_dia = relationship(
        'PuntoOrdenDia', back_populates='reunion',
        lazy='selectin', order_by='PuntoOrdenDia.orden'
    )
    acta = relationship('Acta', foreign_keys='Acta.reunion_id', back_populates='reunion', uselist=False, lazy='selectin')
    actividad = relationship('Actividad', foreign_keys=[actividad_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<Reunion(tipo='{self.tipo_reunion_id}', fecha='{self.fecha_celebracion}', estado='{self.estado_codigo}')>"

    @property
    def quorum_asistencia(self) -> Optional[float]:
        """Porcentaje de asistencia sobre el total de socios."""
        if self.socios_totales and self.socios_totales > 0:
            presentes = (self.socios_presentes or 0) + (self.socios_representados or 0)
            return round(presentes / self.socios_totales * 100, 2)
        return None


class AsistenteReunionSecretaria(BaseModel):
    """Registro de asistencia de un miembro a una reunión."""
    __tablename__ = 'sec_asistentes_reunion'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    reunion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_reuniones.id', ondelete='CASCADE'), nullable=False, index=True
    )
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('contactos.id'), nullable=False, index=True
    )

    # Forma de asistencia
    tipo_asistencia: Mapped[str] = mapped_column(
        String(20), nullable=False, default='PRESENCIAL'
    )  # PRESENCIAL | TELEMATICA | REPRESENTADO | EXCUSADO

    # Si asiste representado
    representado_por_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('contactos.id'), nullable=True
    )

    # Cargo que ostenta en la reunión (si es órgano directivo)
    cargo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relaciones
    reunion = relationship('Reunion', back_populates='asistentes')
    miembro = relationship('Contacto', foreign_keys=[miembro_id], lazy='selectin')
    representado_por = relationship('Contacto', foreign_keys=[representado_por_id], lazy='selectin')

    def __repr__(self) -> str:
        return f"<AsistenteReunionSecretaria(reunion_id='{self.reunion_id}', miembro_id='{self.miembro_id}')>"


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

    # QUÉ es este acuerdo (nombramiento, cese, aprobación de cuentas…). Sin esto, un
    # acuerdo es solo texto libre y la máquina no puede darle efecto: no sabe que
    # «se nombra Tesorera a Ana» ES un nombramiento. Nullable: hay acuerdos que no
    # producen efecto alguno (declarativos, informativos).
    tipo_acuerdo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('sec_tipos_acuerdo.id', ondelete='RESTRICT'),
        nullable=True, index=True,
    )

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
        Uuid, ForeignKey('contactos.id'), nullable=True
    )
    fecha_limite_ejecucion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado_ejecucion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('estados_ejecucion_acuerdo.id'), nullable=True, index=True
    )
    estado_ejecucion_codigo: Mapped[str] = mapped_column(
        String(30), nullable=False, default='PENDIENTE', index=True
    )

    observaciones_ejecucion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    punto_orden_dia = relationship('PuntoOrdenDia', back_populates='acuerdos')
    votacion = relationship('VotacionAcuerdo', back_populates='acuerdo', uselist=False, lazy='selectin')
    responsable = relationship('Contacto', foreign_keys=[responsable_id], lazy='selectin')
    certificados = relationship('CertificadoAcuerdo', back_populates='acuerdo', lazy='selectin')
    tipo_acuerdo = relationship('TipoAcuerdo', lazy='selectin')
    # Payload del acuerdo de nombramiento (a quién, para qué cargo…). 1:1, presente
    # solo si el tipo de acuerdo es NOMBRAMIENTO/CESE.
    nombramiento = relationship(
        'AcuerdoNombramiento', back_populates='acuerdo', uselist=False, lazy='selectin',
        cascade='all, delete-orphan',
    )
    # Payload del acuerdo de aprobación de presupuesto de campaña. 1:1, presente solo
    # si el tipo de acuerdo es APROBACION_PRESUPUESTO.
    presupuesto_campania = relationship(
        'AcuerdoPresupuestoCampania', back_populates='acuerdo', uselist=False, lazy='selectin',
        cascade='all, delete-orphan',
    )

    @property
    def es_aprobado(self) -> bool:
        """Un acuerdo solo produce efectos si fue APROBADO."""
        return self.resultado == 'APROBADO'

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


class TipoAcuerdo(InmutableMixin, BaseModel):
    """Catálogo: QUÉ clase de acuerdo es, y por tanto qué efecto produce.

    Sin esto, un acuerdo es solo texto libre: nadie puede saber que «se nombra
    Tesorera a Ana» ES un nombramiento y debe generar un mandato.

    `produce_efecto` distingue los acuerdos que la máquina puede **ejecutar**
    (NOMBRAMIENTO, CESE…) de los meramente declarativos (aprobar un informe).
    """

    __tablename__ = 'sec_tipos_acuerdo'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    codigo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # True si el acuerdo, una vez aprobado, se puede EJECUTAR y transformar algo.
    produce_efecto: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<TipoAcuerdo(codigo='{self.codigo}')>"


class AcuerdoNombramiento(BaseModel):
    """Payload estructurado de un acuerdo de NOMBRAMIENTO o CESE.

    El acuerdo genérico solo tiene texto; aquí vive lo que la máquina necesita para
    **ejecutarlo**: a quién se nombra, para qué cargo, en qué agrupación y desde
    cuándo. Es una tabla satélite (1:1) para no ensuciar `sec_acuerdos` con campos
    nullable de un tipo concreto de acuerdo.

    Al ejecutarse produce el `HistorialNombramiento` (el mandato), que a su vez
    deriva los `UsuarioRol` vía `CargoRol`. Ver GOBERNANZA.md.
    """

    __tablename__ = 'sec_acuerdos_nombramiento'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    acuerdo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_acuerdos.id', ondelete='CASCADE'),
        nullable=False, unique=True, index=True,
    )

    # A quién se nombra (o cesa) y para qué cargo.
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('contactos.id', ondelete='RESTRICT'), nullable=False, index=True,
    )
    cargo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('cargos.id', ondelete='RESTRICT'), nullable=False, index=True,
    )
    # Territorio donde ejerce. NULL = cargo global (sin ámbito territorial).
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('unidades_organizativas.id', ondelete='RESTRICT'),
        nullable=True, index=True,
    )

    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Se rellena al EJECUTAR el acuerdo: el mandato que produjo. Cierra el círculo
    # (y evita ejecutarlo dos veces).
    nombramiento_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('historial_nombramientos.id', ondelete='SET NULL'),
        nullable=True, index=True,
    )

    # Relaciones
    acuerdo = relationship('Acuerdo', back_populates='nombramiento')
    miembro = relationship('Contacto', foreign_keys=[miembro_id], lazy='selectin')
    cargo = relationship('Cargo', foreign_keys=[cargo_id], lazy='selectin')
    agrupacion = relationship('UnidadOrganizativa', foreign_keys=[agrupacion_id], lazy='selectin')

    @property
    def ya_ejecutado(self) -> bool:
        return self.nombramiento_id is not None

    def __repr__(self) -> str:
        return f"<AcuerdoNombramiento(miembro={self.miembro_id}, cargo={self.cargo_id})>"


class AcuerdoPresupuestoCampania(BaseModel):
    """Payload estructurado de un acuerdo de APROBACION_PRESUPUESTO de campaña.

    El acuerdo genérico solo tiene texto; aquí vive lo que la máquina necesita para
    **ejecutarlo**: qué campaña, cuánto se reserva y contra qué partida del presupuesto
    anual. Tabla satélite (1:1), como `AcuerdoNombramiento`.

    Al ejecutarse produce un `CompromisoPresupuestario` (la reserva) y marca la campaña
    como aprobada. El `compromiso_id` se rellena al ejecutar: cierra el círculo y evita
    reservar dos veces (idempotencia), igual que `nombramiento_id` en los nombramientos.
    """

    __tablename__ = 'sec_acuerdos_presupuesto_campania'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    acuerdo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('sec_acuerdos.id', ondelete='CASCADE'),
        nullable=False, unique=True, index=True,
    )

    campania_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('campanias.id', ondelete='RESTRICT'), nullable=False, index=True,
    )
    # Partida del presupuesto anual contra la que se reservan los fondos.
    partida_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('partidas_presupuestarias.id', ondelete='RESTRICT'),
        nullable=False, index=True,
    )
    importe: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Se rellena al EJECUTAR: el compromiso que produjo la reserva. Idempotencia.
    compromiso_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey('compromisos_presupuestarios.id', ondelete='SET NULL'),
        nullable=True, index=True,
    )

    # Relaciones
    acuerdo = relationship('Acuerdo', back_populates='presupuesto_campania')
    campania = relationship('Campania', foreign_keys=[campania_id], lazy='selectin')
    partida = relationship('PartidaPresupuestaria', foreign_keys=[partida_id], lazy='selectin')

    @property
    def ya_ejecutado(self) -> bool:
        return self.compromiso_id is not None

    def __repr__(self) -> str:
        return f"<AcuerdoPresupuestoCampania(campania={self.campania_id}, importe={self.importe})>"
