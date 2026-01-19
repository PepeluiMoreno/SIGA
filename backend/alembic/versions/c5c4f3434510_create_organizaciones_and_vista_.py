"""create_organizaciones_and_vista_agrupaciones

Revision ID: c5c4f3434510
Revises: 8c6072307fac
Create Date: 2026-01-19 20:35:26.122412
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'c5c4f3434510'
down_revision: Union[str, None] = '8c6072307fac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear tabla tipos_organizacion
    op.create_table(
        'tipos_organizacion',
        sa.Column('id', sa.Uuid(), nullable=False),
        # Campos de CatalogoMixin
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.String(length=500), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('es_sistema', sa.Boolean(), nullable=False, server_default='false'),
        # Campos propios de TipoOrganizacion
        sa.Column('categoria', sa.String(length=50), nullable=False),
        sa.Column('permite_jerarquia', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('permite_convenios', sa.Boolean(), nullable=False, server_default='false'),

        # Campos de auditoria (BaseModel)
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('creado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo')
    )
    op.create_index('ix_tipos_organizacion_codigo', 'tipos_organizacion', ['codigo'])
    op.create_index('ix_tipos_organizacion_categoria', 'tipos_organizacion', ['categoria'])
    op.create_index('ix_tipos_organizacion_activo', 'tipos_organizacion', ['activo'])
    op.create_index('ix_tipos_organizacion_es_sistema', 'tipos_organizacion', ['es_sistema'])
    op.create_index('ix_tipos_organizacion_eliminado', 'tipos_organizacion', ['eliminado'])

    # Crear tabla organizaciones
    op.create_table(
        'organizaciones',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tipo_id', sa.Uuid(), sa.ForeignKey('tipos_organizacion.id'), nullable=False),

        # Identificación
        sa.Column('codigo', sa.String(length=20), nullable=True),
        sa.Column('nombre', sa.String(length=200), nullable=False),
        sa.Column('nombre_corto', sa.String(length=100), nullable=True),
        sa.Column('siglas', sa.String(length=20), nullable=True),

        # Datos legales
        sa.Column('cif_nif', sa.String(length=20), nullable=True),
        sa.Column('registro_oficial', sa.String(length=100), nullable=True),
        sa.Column('numero_registro', sa.String(length=50), nullable=True),
        sa.Column('fecha_constitucion', sa.Date(), nullable=True),

        # Jerarquia
        sa.Column('organizacion_padre_id', sa.Uuid(), sa.ForeignKey('organizaciones.id'), nullable=True),
        sa.Column('nivel', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('ambito', sa.String(length=50), nullable=False, server_default='LOCAL'),

        # Ubicacion (ContactoCompletoMixin)
        sa.Column('pais_id', sa.Uuid(), sa.ForeignKey('paises.id'), nullable=False),
        sa.Column('provincia_id', sa.Uuid(), sa.ForeignKey('provincias.id'), nullable=True),
        sa.Column('municipio_id', sa.Uuid(), sa.ForeignKey('municipios.id'), nullable=True),
        sa.Column('direccion_id', sa.Uuid(), sa.ForeignKey('direcciones.id'), nullable=True),

        # Contacto (ContactoCompletoMixin)
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('telefono_fijo', sa.String(length=20), nullable=True),
        sa.Column('telefono_movil', sa.String(length=20), nullable=True),
        sa.Column('web', sa.String(length=255), nullable=True),

        # Persona de contacto (ContactoCompletoMixin)
        sa.Column('persona_contacto_nombre', sa.String(length=200), nullable=True),
        sa.Column('persona_contacto_cargo', sa.String(length=100), nullable=True),
        sa.Column('persona_contacto_email', sa.String(length=255), nullable=True),
        sa.Column('persona_contacto_telefono', sa.String(length=20), nullable=True),

        # Informacion adicional
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('actividades_principales', sa.Text(), nullable=True),
        sa.Column('numero_socios', sa.Integer(), nullable=True),

        # Estado
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_alta', sa.Date(), server_default=sa.func.now(), nullable=False),
        sa.Column('fecha_baja', sa.Date(), nullable=True),
        sa.Column('motivo_baja', sa.Text(), nullable=True),

        # Valoracion
        sa.Column('valoracion', sa.Integer(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),

        # Campos de auditoria (BaseModel)
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
        sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('creado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo'),
        sa.UniqueConstraint('cif_nif')
    )

    # Indices en organizaciones
    op.create_index('ix_organizaciones_tipo_id', 'organizaciones', ['tipo_id'])
    op.create_index('ix_organizaciones_codigo', 'organizaciones', ['codigo'])
    op.create_index('ix_organizaciones_nombre', 'organizaciones', ['nombre'])
    op.create_index('ix_organizaciones_siglas', 'organizaciones', ['siglas'])
    op.create_index('ix_organizaciones_cif_nif', 'organizaciones', ['cif_nif'])
    op.create_index('ix_organizaciones_padre_id', 'organizaciones', ['organizacion_padre_id'])
    op.create_index('ix_organizaciones_ambito', 'organizaciones', ['ambito'])
    op.create_index('ix_organizaciones_pais_id', 'organizaciones', ['pais_id'])
    op.create_index('ix_organizaciones_provincia_id', 'organizaciones', ['provincia_id'])
    op.create_index('ix_organizaciones_email', 'organizaciones', ['email'])
    op.create_index('ix_organizaciones_activo', 'organizaciones', ['activo'])
    op.create_index('ix_organizaciones_eliminado', 'organizaciones', ['eliminado'])

    # NOTA: estados_convenio ya existe de migración anterior (colaboraciones domain)
    # No crear tabla estados_convenio - comentada para evitar conflicto
    # op.create_table(
    #     'estados_convenio',
    #     sa.Column('id', sa.Uuid(), nullable=False),
    #     sa.Column('codigo', sa.String(length=20), nullable=False),
    #     sa.Column('nombre', sa.String(length=100), nullable=False),
    #     sa.Column('descripcion', sa.Text(), nullable=True),
    #     sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
    #     sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
    #
    #     # Campos de auditoria
    #     sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    #     sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
    #     sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    #     sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
    #     sa.Column('creado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),
    #     sa.Column('modificado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),
    #
    #     sa.PrimaryKeyConstraint('id'),
    #     sa.UniqueConstraint('codigo')
    # )
    # op.create_index('ix_estados_convenio_codigo', 'estados_convenio', ['codigo'])
    # op.create_index('ix_estados_convenio_activo', 'estados_convenio', ['activo'])

    # NOTA: convenios también ya existe de migración anterior (colaboraciones domain)
    # No crear tabla convenios - comentada para evitar conflicto
    # op.create_table(
    #     'convenios',
    #     sa.Column('id', sa.Uuid(), nullable=False),
    #     sa.Column('organizacion_id', sa.Uuid(), sa.ForeignKey('organizaciones.id'), nullable=False),
    #     sa.Column('organizacion_colaboradora_id', sa.Uuid(), sa.ForeignKey('organizaciones.id'), nullable=True),
    #
    #     # Identificacion
    #     sa.Column('codigo', sa.String(length=50), nullable=False),
    #     sa.Column('nombre', sa.String(length=200), nullable=False),
    #     sa.Column('tipo', sa.String(length=50), nullable=False, server_default='CONVENIO'),
    #
    #     # Fechas
    #     sa.Column('fecha_firma', sa.Date(), nullable=False),
    #     sa.Column('fecha_inicio', sa.Date(), nullable=False),
    #     sa.Column('fecha_fin', sa.Date(), nullable=True),
    #     sa.Column('renovable', sa.Boolean(), nullable=False, server_default='false'),
    #
    #     # Contenido
    #     sa.Column('objeto', sa.Text(), nullable=False),
    #     sa.Column('compromisos_organizacion', sa.Text(), nullable=True),
    #     sa.Column('compromisos_propios', sa.Text(), nullable=True),
    #     sa.Column('beneficios', sa.Text(), nullable=True),
    #
    #     # Aspectos economicos
    #     sa.Column('tiene_aportacion_economica', sa.Boolean(), nullable=False, server_default='false'),
    #     sa.Column('importe_aportacion', sa.Numeric(10, 2), nullable=True),
    #     sa.Column('periodicidad_aportacion', sa.String(length=50), nullable=True),
    #
    #     # Documentacion
    #     sa.Column('documento_url', sa.String(length=500), nullable=True),
    #     sa.Column('anexos_urls', sa.Text(), nullable=True),
    #
    #     # Responsables
    #     sa.Column('responsable_organizacion_propia', sa.String(length=200), nullable=True),
    #     sa.Column('responsable_organizacion_externa', sa.String(length=200), nullable=True),
    #
    #     # Estado
    #     sa.Column('estado_id', sa.Uuid(), sa.ForeignKey('estados_convenio.id'), nullable=False),
    #     sa.Column('observaciones', sa.Text(), nullable=True),
    #     sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
    #
    #     # Campos de auditoria
    #     sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    #     sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
    #     sa.Column('fecha_eliminacion', sa.DateTime(), nullable=True),
    #     sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
    #     sa.Column('creado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),
    #     sa.Column('modificado_por_id', sa.Uuid(), sa.ForeignKey('usuarios.id'), nullable=True),
    #
    #     sa.PrimaryKeyConstraint('id'),
    #     sa.UniqueConstraint('codigo')
    # )
    # op.create_index('ix_convenios_organizacion_id', 'convenios', ['organizacion_id'])
    # op.create_index('ix_convenios_codigo', 'convenios', ['codigo'])
    # op.create_index('ix_convenios_fecha_firma', 'convenios', ['fecha_firma'])
    # op.create_index('ix_convenios_fecha_fin', 'convenios', ['fecha_fin'])
    # op.create_index('ix_convenios_estado_id', 'convenios', ['estado_id'])
    # op.create_index('ix_convenios_activo', 'convenios', ['activo'])

    # Crear vista materializada para agrupaciones territoriales
    op.execute("""
        CREATE MATERIALIZED VIEW vista_agrupaciones_territoriales AS
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
    """)

    # Crear indices en la vista materializada
    op.execute("CREATE UNIQUE INDEX idx_vista_agrup_id ON vista_agrupaciones_territoriales(id)")
    op.execute("CREATE INDEX idx_vista_agrup_codigo ON vista_agrupaciones_territoriales(codigo)")
    op.execute("CREATE INDEX idx_vista_agrup_tipo ON vista_agrupaciones_territoriales(tipo)")
    op.execute("CREATE INDEX idx_vista_agrup_padre ON vista_agrupaciones_territoriales(agrupacion_padre_id)")
    op.execute("CREATE INDEX idx_vista_agrup_provincia ON vista_agrupaciones_territoriales(provincia_id)")
    op.execute("CREATE INDEX idx_vista_agrup_activo ON vista_agrupaciones_territoriales(activo)")


def downgrade() -> None:
    # Eliminar vista materializada y sus indices
    op.execute("DROP MATERIALIZED VIEW IF EXISTS vista_agrupaciones_territoriales CASCADE")

    # Eliminar tablas en orden inverso
    # op.drop_table('convenios')  # No eliminar - tabla existe de migración anterior
    # op.drop_table('estados_convenio')  # No eliminar - tabla existe de migración anterior
    op.drop_table('organizaciones')
    op.drop_table('tipos_organizacion')
