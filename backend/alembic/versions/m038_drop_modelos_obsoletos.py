"""m038: eliminar modelos obsoletos (eventos, actividades, propuestas, plan JTI, tareas_grupo)

Revision ID: m038
Revises: m037
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa

revision = 'm038'
down_revision = 'm037'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Orden: hijos primero, luego padres ────────────────────────────────────

    # 1. KPIs
    op.drop_table('mediciones_kpi')
    op.drop_table('kpis_actividad')
    op.drop_table('kpis')
    op.drop_table('tipos_kpi')

    # 2. Dependientes de eventos
    op.drop_table('tareas_evento')
    op.drop_table('gastos_evento')
    op.drop_table('materiales_evento')
    op.drop_table('grupos_evento')
    op.drop_table('participantes_evento')

    # 3. Dependientes de actividades
    op.drop_table('tareas_actividad')
    op.drop_table('recursos_actividad')
    op.drop_table('grupos_actividad')
    op.drop_table('participantes_actividad')

    # 4. Tareas de grupo (reemplazadas por tabla unificada tareas)
    op.drop_table('tareas_grupo')

    # 5. Dependientes de propuestas
    op.drop_table('tareas_propuesta')
    op.drop_table('recursos_propuesta')
    op.drop_table('grupos_propuesta')

    # 6. Quitar plan_id de campanias antes de eliminar plan_actividades
    with op.batch_alter_table('campanias') as batch_op:
        batch_op.drop_constraint('fk_campanias_plan_id', type_='foreignkey')
        batch_op.drop_column('plan_id')

    # 7. Tablas principales obsoletas
    op.drop_table('eventos')
    op.drop_table('actividades')
    op.drop_table('propuestas_actividad')
    op.drop_table('plan_actividades')

    # 8. Catálogos obsoletos
    op.drop_table('tipos_evento')
    op.drop_table('estados_evento')
    op.drop_table('tipos_actividad')
    op.drop_table('estados_actividad')
    op.drop_table('estados_propuesta')
    op.drop_table('tipos_recurso')


def downgrade() -> None:
    # No se proporciona downgrade — la restauración requeriría recrear toda la estructura antigua.
    raise NotImplementedError("Downgrade de m038 no soportado")
