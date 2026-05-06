"""drop tablas obsoletas: tipos_cargo, cargos_junta, historial_cargos_junta, tipos_cargo_roles

Los roles de tipo ORGANIZACION son ahora los cargos.
CargoJunta, HistorialCargoJunta y TipoCargoRol se eliminan.
TipoCargo se mantiene como catalogo (ya no tiene relacion con miembros).

Revision ID: m011
Revises: m010
Create Date: 2026-05-06 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'm011'
down_revision: Union[str, None] = 'm010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop FK constraints first
    op.drop_constraint('fk_hist_nombramientos_rol', 'historial_nombramientos', type_='foreignkey')
    op.drop_constraint('historial_nombramientos_miembro_id_fkey', 'historial_nombramientos', type_='foreignkey')

    # Drop obsolete tables
    op.drop_table('cargos_junta')
    op.drop_table('historial_cargos_junta')
    op.drop_table('tipos_cargo_roles')

    # Recreate FK constraints with correct names
    op.create_foreign_key(
        'fk_hist_nombramientos_rol',
        'historial_nombramientos', 'roles',
        ['rol_id'], ['id'],
        ondelete='RESTRICT'
    )
    op.create_foreign_key(
        'historial_nombramientos_miembro_id_fkey',
        'historial_nombramientos', 'miembros',
        ['miembro_id'], ['id'],
        ondelete='RESTRICT'
    )


def downgrade() -> None:
    # Recreate obsolete tables
    op.drop_constraint('fk_hist_nombramientos_rol', 'historial_nombramientos', type_='foreignkey')
    op.drop_constraint('historial_nombramientos_miembro_id_fkey', 'historial_nombramientos', type_='foreignkey')

    op.create_table('tipos_cargo_roles',
        # columns would be recreated here if needed
    )
    op.create_table('historial_cargos_junta',
        # columns would be recreated here if needed
    )
    op.create_table('cargos_junta',
        # columns would be recreated here if needed
    )

    op.create_foreign_key('fk_hist_nombramientos_rol', 'historial_nombramientos', 'roles', ['rol_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key('historial_nombramientos_miembro_id_fkey', 'historial_nombramientos', 'miembros', ['miembro_id'], ['id'], ondelete='RESTRICT')
