"""
Vista materializada de Miembros para Segmentación de Campañas.

Esta vista precalcula los campos de segmentación (es_joven, es_simpatizante,
es_voluntario_disponible) para permitir filtrados eficientes en campañas
sin necesidad de JOINs ni cálculos en tiempo real.

Se refresca periódicamente o tras cambios masivos en miembros.
"""

import uuid
from typing import Optional
from datetime import date

from sqlalchemy import String, Integer, Uuid, Boolean, Date, Text
from sqlalchemy.orm import Mapped, mapped_column

from ....infrastructure.base_model import Base  # No heredar de BaseModel, es una vista


class MiembroSegmentacion(Base):
    """
    Vista materializada para segmentación de miembros en campañas.

    Contiene campos precalculados para filtrar miembros por:
    - es_joven: Menores de 30 años
    - es_simpatizante: Tipo de membresía SIMPATIZANTE
    - es_voluntario_disponible: Voluntarios con disponibilidad declarada

    Esta es una vista de solo lectura.
    """
    __tablename__ = 'vista_miembros_segmentacion'
    __table_args__ = {'info': {'is_view': True}}

    # Identificación
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    apellido1: Mapped[str] = mapped_column(String(100))
    apellido2: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(200))

    # Datos para cálculo de edad
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date)
    edad: Mapped[Optional[int]] = mapped_column(Integer)

    # Tipo y estado (por nombre)
    tipo_miembro_nombre: Mapped[str] = mapped_column(String(100))
    estado_nombre: Mapped[str] = mapped_column(String(100))

    # Agrupación
    agrupacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    agrupacion_nombre: Mapped[Optional[str]] = mapped_column(String(200))

    # Campos de segmentación precalculados
    es_joven: Mapped[bool] = mapped_column(Boolean)
    es_simpatizante: Mapped[bool] = mapped_column(Boolean)
    es_voluntario_disponible: Mapped[bool] = mapped_column(Boolean)

    # Datos de voluntariado
    es_voluntario: Mapped[bool] = mapped_column(Boolean)
    disponibilidad: Mapped[Optional[str]] = mapped_column(String(50))

    # Fechas
    fecha_alta: Mapped[date] = mapped_column(Date)
    fecha_baja: Mapped[Optional[date]] = mapped_column(Date)

    def __repr__(self) -> str:
        return f"<MiembroSegmentacion(id='{self.id}', nombre='{self.nombre} {self.apellido1}')>"

    @classmethod
    def crear_vista_materializada(cls, engine):
        """
        Crea la vista materializada en PostgreSQL.

        Debe ejecutarse después de crear las tablas base.
        """
        from sqlalchemy import text

        sql = text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS vista_miembros_segmentacion AS
        SELECT
            m.id,
            m.nombre,
            m.apellido1,
            m.apellido2,
            m.email,
            m.fecha_nacimiento,
            -- Cálculo de edad
            CASE
                WHEN m.fecha_nacimiento IS NOT NULL THEN
                    EXTRACT(YEAR FROM age(CURRENT_DATE, m.fecha_nacimiento))::integer
                ELSE NULL
            END as edad,
            -- Tipo y estado
            tm.nombre as tipo_miembro_nombre,
            em.nombre as estado_nombre,
            -- Agrupación
            m.agrupacion_id,
            a.nombre as agrupacion_nombre,
            -- Segmentación: es_joven (menores de 30)
            CASE
                WHEN m.fecha_nacimiento IS NOT NULL
                     AND EXTRACT(YEAR FROM age(CURRENT_DATE, m.fecha_nacimiento)) < 30
                THEN true
                ELSE false
            END as es_joven,
            -- Segmentación: es_simpatizante
            CASE
                WHEN LOWER(tm.nombre) = 'simpatizante' THEN true
                ELSE false
            END as es_simpatizante,
            -- Segmentación: es_voluntario_disponible
            CASE
                WHEN m.es_voluntario = true
                     AND m.fecha_baja IS NULL
                     AND (m.disponibilidad IS NOT NULL OR COALESCE(m.horas_disponibles_semana, 0) > 0)
                THEN true
                ELSE false
            END as es_voluntario_disponible,
            -- Datos voluntariado
            m.es_voluntario,
            m.disponibilidad,
            -- Fechas
            m.fecha_alta,
            m.fecha_baja
        FROM miembros m
        INNER JOIN tipos_miembro tm ON m.tipo_miembro_id = tm.id
        INNER JOIN estados_miembro em ON m.estado_id = em.id
        LEFT JOIN vista_agrupaciones_territoriales a ON m.agrupacion_id = a.id
        WHERE m.eliminado = FALSE;

        -- Crear índices en la vista materializada
        CREATE UNIQUE INDEX IF NOT EXISTS idx_vista_miembro_seg_id
            ON vista_miembros_segmentacion(id);
        CREATE INDEX IF NOT EXISTS idx_vista_miembro_seg_es_joven
            ON vista_miembros_segmentacion(es_joven) WHERE es_joven = true;
        CREATE INDEX IF NOT EXISTS idx_vista_miembro_seg_es_simpatizante
            ON vista_miembros_segmentacion(es_simpatizante) WHERE es_simpatizante = true;
        CREATE INDEX IF NOT EXISTS idx_vista_miembro_seg_es_voluntario
            ON vista_miembros_segmentacion(es_voluntario_disponible) WHERE es_voluntario_disponible = true;
        CREATE INDEX IF NOT EXISTS idx_vista_miembro_seg_estado
            ON vista_miembros_segmentacion(estado_nombre);
        CREATE INDEX IF NOT EXISTS idx_vista_miembro_seg_agrupacion
            ON vista_miembros_segmentacion(agrupacion_id);
        CREATE INDEX IF NOT EXISTS idx_vista_miembro_seg_email
            ON vista_miembros_segmentacion(email) WHERE email IS NOT NULL;
        """)

        with engine.connect() as conn:
            conn.execute(sql)
            conn.commit()

    @classmethod
    def refrescar_vista(cls, session):
        """
        Refresca la vista materializada con los datos actuales.

        Debe llamarse después de cambios masivos en miembros
        o periódicamente (ej. cada noche).
        """
        from sqlalchemy import text

        session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY vista_miembros_segmentacion"))
        session.commit()

    @classmethod
    def eliminar_vista(cls, engine):
        """Elimina la vista materializada."""
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("DROP MATERIALIZED VIEW IF EXISTS vista_miembros_segmentacion CASCADE"))
            conn.commit()
