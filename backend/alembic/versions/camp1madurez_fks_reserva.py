"""Campañas maduras: FK reales para reserva de fondos y vínculo de grupo

Tres FK que hasta ahora eran UUID sueltos, y que la maduración del ciclo de campaña
necesita como relaciones reales:

- `compromisos_presupuestarios.campania_id`  → `campanias.id`   (reserva de fondos)
- `compromisos_presupuestarios.actividad_id` → `actividades.id`
- `grupos_trabajo.campania_id`               → `campanias.id`   (vínculo canónico grupo↔campaña)

No hay datos que migrar (los compromisos solo existían en el seed demo, y los grupos con
campania_id apuntan a campañas reales); estas FK solo formalizan integridad referencial.

Revision ID: camp1madurez
Revises: act1terr2ag3
"""
from alembic import op


revision = "camp1madurez"
down_revision = "act1terr2ag3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "compromisos_presupuestarios_campania_id_fkey",
        "compromisos_presupuestarios", "campanias",
        ["campania_id"], ["id"],
    )
    op.create_foreign_key(
        "compromisos_presupuestarios_actividad_id_fkey",
        "compromisos_presupuestarios", "actividades",
        ["actividad_id"], ["id"],
    )
    op.create_foreign_key(
        "grupos_trabajo_campania_id_fkey",
        "grupos_trabajo", "campanias",
        ["campania_id"], ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("grupos_trabajo_campania_id_fkey", "grupos_trabajo", type_="foreignkey")
    op.drop_constraint("compromisos_presupuestarios_actividad_id_fkey", "compromisos_presupuestarios", type_="foreignkey")
    op.drop_constraint("compromisos_presupuestarios_campania_id_fkey", "compromisos_presupuestarios", type_="foreignkey")
