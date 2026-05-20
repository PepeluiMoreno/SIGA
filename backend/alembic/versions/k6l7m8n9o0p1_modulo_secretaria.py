"""Módulo de Secretaría: reuniones, actas, libro de socios y convenios.

Revision ID: k6l7m8n9o0p1
Revises: j5k6l7m8n9o0
Create Date: 2026-05-20 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'k6l7m8n9o0p1'
down_revision = 'j5k6l7m8n9o0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # sec_tipos_reunion                                                    #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_tipos_reunion',
        sa.Column('id',                             sa.Uuid(),      nullable=False),
        sa.Column('nombre',                         sa.String(100), nullable=False),
        sa.Column('descripcion',                    sa.String(500), nullable=True),
        sa.Column('organo',                         sa.String(50),  nullable=False),
        sa.Column('quorum_primera_convocatoria',    sa.Integer(),   nullable=True),
        sa.Column('quorum_segunda_convocatoria',    sa.Integer(),   nullable=True),
        sa.Column('antelacion_minima_dias',         sa.Integer(),   nullable=False, server_default='15'),
        sa.Column('activo',                         sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('orden',                          sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('es_inmutable',                   sa.Boolean(),   nullable=False, server_default='false'),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sec_tipos_reunion_activo', 'sec_tipos_reunion', ['activo'])

    # ------------------------------------------------------------------ #
    # sec_reuniones                                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_reuniones',
        sa.Column('id',                         sa.Uuid(),      nullable=False),
        sa.Column('tipo_reunion_id',             sa.Uuid(),      sa.ForeignKey('sec_tipos_reunion.id'), nullable=False),
        sa.Column('agrupacion_id',               sa.Uuid(),      sa.ForeignKey('unidades_organizativas.id'), nullable=True),
        sa.Column('numero_convocatoria',         sa.Integer(),   nullable=False),
        sa.Column('anio',                        sa.Integer(),   nullable=False),
        sa.Column('fecha_convocatoria',          sa.Date(),      nullable=False),
        sa.Column('fecha_celebracion',           sa.DateTime(),  nullable=True),
        sa.Column('lugar',                       sa.String(300), nullable=True),
        sa.Column('es_telematica',               sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('plataforma_telematica',       sa.String(200), nullable=True),
        sa.Column('tiene_segunda_convocatoria',  sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('fecha_segunda_convocatoria',  sa.DateTime(),  nullable=True),
        sa.Column('convocatoria_utilizada',      sa.Integer(),   nullable=True),
        sa.Column('socios_totales',              sa.Integer(),   nullable=True),
        sa.Column('socios_presentes',            sa.Integer(),   nullable=True),
        sa.Column('socios_representados',        sa.Integer(),   nullable=True),
        sa.Column('hay_quorum',                  sa.Boolean(),   nullable=True),
        sa.Column('estado',                      sa.String(30),  nullable=False, server_default='CONVOCADA'),
        sa.Column('observaciones',               sa.Text(),      nullable=True),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sec_reuniones_tipo_reunion_id', 'sec_reuniones', ['tipo_reunion_id'])
    op.create_index('ix_sec_reuniones_agrupacion_id',   'sec_reuniones', ['agrupacion_id'])
    op.create_index('ix_sec_reuniones_anio',            'sec_reuniones', ['anio'])
    op.create_index('ix_sec_reuniones_estado',          'sec_reuniones', ['estado'])
    op.create_index('ix_sec_reuniones_eliminado',       'sec_reuniones', ['eliminado'])

    # ------------------------------------------------------------------ #
    # sec_asistentes_reunion                                               #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_asistentes_reunion',
        sa.Column('id',                   sa.Uuid(),     nullable=False),
        sa.Column('reunion_id',           sa.Uuid(),     sa.ForeignKey('sec_reuniones.id', ondelete='CASCADE'), nullable=False),
        sa.Column('miembro_id',           sa.Uuid(),     sa.ForeignKey('miembros.id'), nullable=False),
        sa.Column('tipo_asistencia',      sa.String(20), nullable=False, server_default='PRESENCIAL'),
        sa.Column('representado_por_id',  sa.Uuid(),     sa.ForeignKey('miembros.id'), nullable=True),
        sa.Column('cargo',                sa.String(100), nullable=True),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sec_asistentes_reunion_id',  'sec_asistentes_reunion', ['reunion_id'])
    op.create_index('ix_sec_asistentes_miembro_id',  'sec_asistentes_reunion', ['miembro_id'])

    # ------------------------------------------------------------------ #
    # sec_puntos_orden_dia                                                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_puntos_orden_dia',
        sa.Column('id',          sa.Uuid(),      nullable=False),
        sa.Column('reunion_id',  sa.Uuid(),      sa.ForeignKey('sec_reuniones.id', ondelete='CASCADE'), nullable=False),
        sa.Column('orden',       sa.Integer(),   nullable=False),
        sa.Column('titulo',      sa.String(300), nullable=False),
        sa.Column('descripcion', sa.Text(),      nullable=True),
        sa.Column('tipo',        sa.String(30),  nullable=False, server_default='ORDINARIO'),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sec_puntos_orden_dia_reunion_id', 'sec_puntos_orden_dia', ['reunion_id'])

    # ------------------------------------------------------------------ #
    # sec_acuerdos                                                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_acuerdos',
        sa.Column('id',                    sa.Uuid(),     nullable=False),
        sa.Column('punto_orden_dia_id',    sa.Uuid(),     sa.ForeignKey('sec_puntos_orden_dia.id', ondelete='CASCADE'), nullable=False),
        sa.Column('numero',                sa.Integer(),  nullable=False),
        sa.Column('descripcion',           sa.Text(),     nullable=False),
        sa.Column('tipo_mayoria',          sa.String(30), nullable=False, server_default='SIMPLE'),
        sa.Column('resultado',             sa.String(20), nullable=True),
        sa.Column('responsable_id',        sa.Uuid(),     sa.ForeignKey('miembros.id'), nullable=True),
        sa.Column('fecha_limite_ejecucion',sa.Date(),     nullable=True),
        sa.Column('estado_ejecucion',      sa.String(20), nullable=False, server_default='PENDIENTE'),
        sa.Column('observaciones_ejecucion', sa.Text(),   nullable=True),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sec_acuerdos_punto_orden_dia_id', 'sec_acuerdos', ['punto_orden_dia_id'])
    op.create_index('ix_sec_acuerdos_estado_ejecucion',   'sec_acuerdos', ['estado_ejecucion'])

    # ------------------------------------------------------------------ #
    # sec_votaciones_acuerdo                                               #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_votaciones_acuerdo',
        sa.Column('id',                  sa.Uuid(),    nullable=False),
        sa.Column('acuerdo_id',          sa.Uuid(),    sa.ForeignKey('sec_acuerdos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('votos_favor',         sa.Integer(), nullable=False, server_default='0'),
        sa.Column('votos_contra',        sa.Integer(), nullable=False, server_default='0'),
        sa.Column('abstenciones',        sa.Integer(), nullable=False, server_default='0'),
        sa.Column('votos_nulos',         sa.Integer(), nullable=False, server_default='0'),
        sa.Column('es_votacion_secreta', sa.Boolean(), nullable=False, server_default='false'),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('acuerdo_id'),
    )
    op.create_index('ix_sec_votaciones_acuerdo_id', 'sec_votaciones_acuerdo', ['acuerdo_id'])

    # ------------------------------------------------------------------ #
    # sec_actas                                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_actas',
        sa.Column('id',                    sa.Uuid(),     nullable=False),
        sa.Column('reunion_id',            sa.Uuid(),     sa.ForeignKey('sec_reuniones.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('numero',                sa.Integer(),  nullable=False),
        sa.Column('anio',                  sa.Integer(),  nullable=False),
        sa.Column('texto_acta',            sa.Text(),     nullable=True),
        sa.Column('estado',                sa.String(20), nullable=False, server_default='BORRADOR'),
        sa.Column('fecha_aprobacion',      sa.Date(),     nullable=True),
        sa.Column('reunion_aprobacion_id', sa.Uuid(),     sa.ForeignKey('sec_reuniones.id'), nullable=True),
        sa.Column('secretario_id',         sa.Uuid(),     sa.ForeignKey('miembros.id'), nullable=True),
        sa.Column('presidente_id',         sa.Uuid(),     sa.ForeignKey('miembros.id'), nullable=True),
        sa.Column('fecha_firma',           sa.DateTime(), nullable=True),
        sa.Column('ruta_pdf',              sa.String(500), nullable=True),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reunion_id'),
    )
    op.create_index('ix_sec_actas_anio',    'sec_actas', ['anio'])
    op.create_index('ix_sec_actas_estado',  'sec_actas', ['estado'])

    # ------------------------------------------------------------------ #
    # sec_certificados_acuerdo                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_certificados_acuerdo',
        sa.Column('id',                  sa.Uuid(),      nullable=False),
        sa.Column('acta_id',             sa.Uuid(),      sa.ForeignKey('sec_actas.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('acuerdo_id',          sa.Uuid(),      sa.ForeignKey('sec_acuerdos.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('numero_certificado',  sa.String(50),  nullable=False),
        sa.Column('fecha_emision',       sa.Date(),      nullable=False),
        sa.Column('destinatario',        sa.String(300), nullable=True),
        sa.Column('proposito',           sa.String(500), nullable=True),
        sa.Column('texto_certificado',   sa.Text(),      nullable=False),
        sa.Column('secretario_id',       sa.Uuid(),      sa.ForeignKey('miembros.id'), nullable=True),
        sa.Column('presidente_id',       sa.Uuid(),      sa.ForeignKey('miembros.id'), nullable=True),
        sa.Column('ruta_pdf',            sa.String(500), nullable=True),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_certificado'),
    )
    op.create_index('ix_sec_certificados_acta_id',    'sec_certificados_acuerdo', ['acta_id'])
    op.create_index('ix_sec_certificados_acuerdo_id', 'sec_certificados_acuerdo', ['acuerdo_id'])

    # ------------------------------------------------------------------ #
    # sec_libro_socios_snapshots                                           #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_libro_socios_snapshots',
        sa.Column('id',                    sa.Uuid(),      nullable=False),
        sa.Column('fecha_corte',           sa.Date(),      nullable=False),
        sa.Column('fecha_generacion',      sa.DateTime(),  nullable=False),
        sa.Column('total_socios_activos',  sa.Integer(),   nullable=False),
        sa.Column('total_socios_baja',     sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('total_socios_historico',sa.Integer(),   nullable=False),
        sa.Column('motivo',                sa.String(200), nullable=True),
        sa.Column('ruta_pdf',              sa.String(500), nullable=True),
        sa.Column('hash_pdf',              sa.String(64),  nullable=True),
        sa.Column('observaciones',         sa.Text(),      nullable=True),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sec_libro_socios_fecha_corte', 'sec_libro_socios_snapshots', ['fecha_corte'])

    # ------------------------------------------------------------------ #
    # sec_tipos_convenio                                                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_tipos_convenio',
        sa.Column('id',          sa.Uuid(),      nullable=False),
        sa.Column('nombre',      sa.String(100), nullable=False),
        sa.Column('descripcion', sa.String(500), nullable=True),
        sa.Column('activo',      sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('es_inmutable',sa.Boolean(),   nullable=False, server_default='false'),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ------------------------------------------------------------------ #
    # sec_convenios                                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_convenios',
        sa.Column('id',                         sa.Uuid(),      nullable=False),
        sa.Column('tipo_convenio_id',           sa.Uuid(),      sa.ForeignKey('sec_tipos_convenio.id'), nullable=False),
        sa.Column('referencia',                 sa.String(100), nullable=False),
        sa.Column('titulo',                     sa.String(300), nullable=False),
        sa.Column('entidad_contraparte',        sa.String(300), nullable=False),
        sa.Column('cif_contraparte',            sa.String(20),  nullable=True),
        sa.Column('fecha_firma',                sa.Date(),      nullable=False),
        sa.Column('fecha_inicio',               sa.Date(),      nullable=False),
        sa.Column('fecha_fin',                  sa.Date(),      nullable=True),
        sa.Column('renovacion_automatica',      sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('dias_preaviso_no_renovacion',sa.Integer(),   nullable=True),
        sa.Column('estado',                     sa.String(20),  nullable=False, server_default='VIGENTE'),
        sa.Column('objeto',                     sa.Text(),      nullable=True),
        sa.Column('obligaciones_asociacion',    sa.Text(),      nullable=True),
        sa.Column('obligaciones_contraparte',   sa.Text(),      nullable=True),
        sa.Column('firmante_id',                sa.Uuid(),      sa.ForeignKey('miembros.id'), nullable=True),
        sa.Column('acuerdo_autorizacion_id',    sa.Uuid(),      sa.ForeignKey('sec_acuerdos.id'), nullable=True),
        sa.Column('ruta_documento',             sa.String(500), nullable=True),
        sa.Column('observaciones',              sa.Text(),      nullable=True),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('referencia'),
    )
    op.create_index('ix_sec_convenios_tipo_id', 'sec_convenios', ['tipo_convenio_id'])
    op.create_index('ix_sec_convenios_estado',  'sec_convenios', ['estado'])

    # ------------------------------------------------------------------ #
    # sec_delegaciones_firma                                               #
    # ------------------------------------------------------------------ #
    op.create_table(
        'sec_delegaciones_firma',
        sa.Column('id',                      sa.Uuid(),    nullable=False),
        sa.Column('delegante_id',            sa.Uuid(),    sa.ForeignKey('miembros.id'), nullable=False),
        sa.Column('delegado_id',             sa.Uuid(),    sa.ForeignKey('miembros.id'), nullable=False),
        sa.Column('descripcion_actos',       sa.Text(),    nullable=False),
        sa.Column('limite_importe',          sa.Numeric(12, 2), nullable=True),
        sa.Column('fecha_inicio',            sa.Date(),    nullable=False),
        sa.Column('fecha_fin',               sa.Date(),    nullable=True),
        sa.Column('activa',                  sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('acuerdo_autorizacion_id', sa.Uuid(),    sa.ForeignKey('sec_acuerdos.id'), nullable=True),
        sa.Column('observaciones',           sa.Text(),    nullable=True),
        # Auditoría
        sa.Column('fecha_creacion',     sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_modificacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_eliminacion',  sa.DateTime(), nullable=True),
        sa.Column('eliminado',          sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('creado_por_id',      sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('modificado_por_id',  sa.Uuid(),     sa.ForeignKey('usuarios.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sec_delegaciones_delegante_id', 'sec_delegaciones_firma', ['delegante_id'])
    op.create_index('ix_sec_delegaciones_delegado_id',  'sec_delegaciones_firma', ['delegado_id'])
    op.create_index('ix_sec_delegaciones_activa',       'sec_delegaciones_firma', ['activa'])


def downgrade() -> None:
    op.drop_table('sec_delegaciones_firma')
    op.drop_table('sec_convenios')
    op.drop_table('sec_tipos_convenio')
    op.drop_table('sec_libro_socios_snapshots')
    op.drop_table('sec_certificados_acuerdo')
    op.drop_table('sec_actas')
    op.drop_table('sec_votaciones_acuerdo')
    op.drop_table('sec_acuerdos')
    op.drop_table('sec_puntos_orden_dia')
    op.drop_table('sec_asistentes_reunion')
    op.drop_table('sec_reuniones')
    op.drop_table('sec_tipos_reunion')
