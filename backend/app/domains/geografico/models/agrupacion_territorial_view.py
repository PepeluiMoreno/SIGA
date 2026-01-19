"""
Vista materializada de Agrupaciones Territoriales.

Esta es una vista congelada (materialized view) que filtra organizaciones
de tipo INTERNA (agrupaciones territoriales de Europa Laica).

Permite mantener compatibilidad con código legacy mientras migramos
al modelo unificado Organizacion.
"""

import uuid
from typing import Optional, List

from sqlalchemy import String, Integer, Uuid, Text, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

from ....infrastructure.base_model import Base  # No heredar de BaseModel, es una vista


class AgrupacionTerritorial(Base):
    """
    Vista materializada de agrupaciones territoriales.

    Esta es una vista de solo lectura que mapea directamente
    a la tabla organizaciones filtrada por tipo INTERNA.

    NO usar para inserts/updates, usar el modelo Organizacion directamente.
    """
    __tablename__ = 'vista_agrupaciones_territoriales'
    __table_args__ = {'info': {'is_view': True}}  # Metadata para indicar que es vista

    # Campos mapeados desde organizaciones
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)

    # Identificación
    codigo: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    nombre: Mapped[str] = mapped_column(String(200), index=True)
    nombre_corto: Mapped[Optional[str]] = mapped_column(String(100))

    # Tipo (siempre será uno de los tipos INTERNA)
    tipo: Mapped[str] = mapped_column(String(50), index=True)  # ESTATAL, AUTONOMICA, PROVINCIAL, LOCAL

    # Jerarquía
    agrupacion_padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)
    nivel: Mapped[int] = mapped_column(Integer)

    # Ubicación
    pais_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    provincia_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)
    municipio_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    direccion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    # Contacto
    email: Mapped[Optional[str]] = mapped_column(String(255))
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    web: Mapped[Optional[str]] = mapped_column(String(255))

    # Información adicional
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Integer, index=True)

    # Relaciones (se mapean igual que en un modelo normal)
    @declared_attr
    def pais(cls):
        return relationship('Pais', foreign_keys=[cls.pais_id], lazy='selectin')

    @declared_attr
    def provincia(cls):
        return relationship('Provincia', foreign_keys=[cls.provincia_id], lazy='selectin')

    @declared_attr
    def municipio(cls):
        return relationship('Municipio', foreign_keys=[cls.municipio_id], lazy='selectin')

    @declared_attr
    def direccion(cls):
        return relationship('Direccion', foreign_keys=[cls.direccion_id], lazy='selectin')

    # Jerarquía (self-referencing)
    @declared_attr
    def agrupacion_padre(cls):
        return relationship(
            'AgrupacionTerritorial',
            remote_side=[cls.id],
            foreign_keys=[cls.agrupacion_padre_id],
            backref='agrupaciones_hijas',
            lazy='selectin'
        )

    def __repr__(self) -> str:
        return f"<AgrupacionTerritorial(codigo='{self.codigo}', nombre='{self.nombre}', tipo='{self.tipo}')>"

    @property
    def telefono_principal(self) -> Optional[str]:
        """Devuelve el teléfono."""
        return self.telefono

    @classmethod
    def crear_vista_materializada(cls, engine):
        """
        Crea la vista materializada en PostgreSQL.

        Debe ejecutarse después de crear las tablas base.
        """
        from sqlalchemy import text

        sql = text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS vista_agrupaciones_territoriales AS
        SELECT
            o.id,
            o.codigo,
            o.nombre,
            o.nombre_corto,
            CASE
                WHEN t.codigo = 'AGRUP_ESTATAL' THEN 'ESTATAL'
                WHEN t.codigo = 'AGRUP_INTERNACIONAL' THEN 'INTERNACIONAL'
                WHEN t.codigo = 'AGRUP_AUTONOMICA' THEN 'AUTONOMICA'
                WHEN t.codigo = 'AGRUP_PROVINCIAL' THEN 'PROVINCIAL'
                WHEN t.codigo = 'AGRUP_LOCAL' THEN 'LOCAL'
                ELSE o.ambito
            END as tipo,
            o.organizacion_padre_id as agrupacion_padre_id,
            o.nivel,
            o.pais_id,
            o.provincia_id,
            o.municipio_id,
            o.direccion_id,
            o.email,
            COALESCE(o.telefono_movil, o.telefono_fijo) as telefono,
            o.web,
            o.descripcion,
            o.activo
        FROM organizaciones o
        INNER JOIN tipos_organizacion t ON o.tipo_id = t.id
        WHERE t.categoria = 'INTERNA'
          AND o.eliminado = FALSE;

        -- Crear índices en la vista materializada
        CREATE UNIQUE INDEX IF NOT EXISTS idx_vista_agrup_id ON vista_agrupaciones_territoriales(id);
        CREATE INDEX IF NOT EXISTS idx_vista_agrup_codigo ON vista_agrupaciones_territoriales(codigo);
        CREATE INDEX IF NOT EXISTS idx_vista_agrup_tipo ON vista_agrupaciones_territoriales(tipo);
        CREATE INDEX IF NOT EXISTS idx_vista_agrup_padre ON vista_agrupaciones_territoriales(agrupacion_padre_id);
        CREATE INDEX IF NOT EXISTS idx_vista_agrup_provincia ON vista_agrupaciones_territoriales(provincia_id);
        CREATE INDEX IF NOT EXISTS idx_vista_agrup_activo ON vista_agrupaciones_territoriales(activo);
        """)

        with engine.connect() as conn:
            conn.execute(sql)
            conn.commit()

    @classmethod
    def refrescar_vista(cls, session):
        """
        Refresca la vista materializada con los datos actuales.

        Debe llamarse después de cambios en organizaciones.
        """
        from sqlalchemy import text

        session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY vista_agrupaciones_territoriales"))
        session.commit()
