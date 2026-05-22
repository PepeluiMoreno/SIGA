"""Comunicación: codigo en estados_notificacion, seed de estados y vista v_nombramientos_vigentes.

Revision ID: c1a2b3d4e5f6
Revises: r3s4t5u6v7w8
Create Date: 2026-05-21 10:30:00.000000

Parte del módulo de comunicación dirigida por flujos de trabajo:
  - Añade la columna `codigo` a `estados_notificacion` (antes el seeder la usaba
    pero el modelo no la declaraba; deuda técnica que esta migración salda).
  - Siembra los 4 estados de notificación (PENDIENTE/ENVIADA/LEIDA/ERROR).
  - Crea la vista `v_nombramientos_vigentes` (hasta ahora solo en SQL_PENDIENTE.md),
    fuente de solo lectura para resolver cargos vigentes en el DestinatarioResolver.
"""
from alembic import op
import sqlalchemy as sa

revision = 'c1a2b3d4e5f6'
down_revision = 'r3s4t5u6v7w8'
branch_labels = None
depends_on = None


_ESTADOS = [
    ('PENDIENTE', 'Pendiente', 1, 'Notificación creada pero no enviada'),
    ('ENVIADA',   'Enviada',   2, 'Notificación enviada al canal correspondiente'),
    ('LEIDA',     'Leída',     3, 'Notificación leída por el usuario'),
    ('ERROR',     'Error',     4, 'Error al enviar la notificación'),
]


def upgrade() -> None:
    # 1) Columna `codigo` en estados_notificacion (nullable primero para poder
    #    rellenar las filas que pudieran existir; luego unique).
    op.add_column(
        'estados_notificacion',
        sa.Column('codigo', sa.String(length=30), nullable=True,
                  comment='Código de máquina: PENDIENTE, ENVIADA, LEIDA, ERROR'),
    )

    # 2) Seed idempotente de los estados. Inserta solo los que falten por código
    #    (match por nombre para filas preexistentes sembradas sin código).
    conn = op.get_bind()
    for codigo, nombre, orden, descripcion in _ESTADOS:
        # ¿existe ya por código?
        existe_cod = conn.execute(
            sa.text("SELECT 1 FROM estados_notificacion WHERE codigo = :c LIMIT 1"),
            {"c": codigo},
        ).first()
        if existe_cod:
            continue
        # ¿existe por nombre sin código? → completar el código
        fila = conn.execute(
            sa.text("SELECT id FROM estados_notificacion "
                    "WHERE nombre = :n AND codigo IS NULL LIMIT 1"),
            {"n": nombre},
        ).first()
        if fila:
            conn.execute(
                sa.text("UPDATE estados_notificacion SET codigo = :c WHERE id = :id"),
                {"c": codigo, "id": fila[0]},
            )
        else:
            conn.execute(
                sa.text(
                    "INSERT INTO estados_notificacion "
                    "(id, codigo, nombre, descripcion, orden, activo, es_inmutable, eliminado) "
                    "VALUES (gen_random_uuid(), :c, :n, :d, :o, true, false, false)"
                ),
                {"c": codigo, "n": nombre, "d": descripcion, "o": orden},
            )

    # 3) Ahora que todas las filas tienen código, imponer NOT NULL + UNIQUE.
    op.alter_column('estados_notificacion', 'codigo', nullable=False)
    op.create_unique_constraint(
        'uq_estados_notificacion_codigo', 'estados_notificacion', ['codigo']
    )

    # 4) Vista de nombramientos vigentes (idempotente).
    op.execute(
        """
        CREATE OR REPLACE VIEW v_nombramientos_vigentes AS
        SELECT id, miembro_id, cargo_id, agrupacion_id, fecha_inicio
        FROM historial_nombramientos
        WHERE estado = 'ACTIVO' AND fecha_fin IS NULL AND eliminado = false
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_nombramientos_vigentes")
    op.drop_constraint('uq_estados_notificacion_codigo', 'estados_notificacion', type_='unique')
    op.drop_column('estados_notificacion', 'codigo')
