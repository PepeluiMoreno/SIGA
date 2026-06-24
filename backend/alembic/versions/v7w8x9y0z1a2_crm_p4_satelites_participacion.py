"""CRM paso 4: enganchar los satélites de dominio a Participacion.

firmas_campania, donaciones y sec_convenios son satélites 1:1 de Participacion
(via participacion_id). En una BD migrada en sitio hay que crear una Participacion
del tipo correspondiente por cada fila existente y enlazarla.

Revision ID: v7w8x9y0z1a2
Revises: u6v7w8x9y0z1
Create Date: 2026-06-24 15:00:00.000000
"""
from alembic import op

revision = 'v7w8x9y0z1a2'
down_revision = 'u6v7w8x9y0z1'
branch_labels = None
depends_on = None


def _wire_satellite(table: str, tipo: str, contacto_col: str, not_null: bool) -> None:
    """Crea una Participacion(tipo) por fila con contacto y enlaza participacion_id."""
    op.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS participacion_id UUID")
    op.execute(f"""
        DO $$
        DECLARE r record; pid uuid;
        BEGIN
            FOR r IN SELECT id, {contacto_col} AS cid, fecha_creacion
                     FROM {table}
                     WHERE {contacto_col} IS NOT NULL AND participacion_id IS NULL LOOP
                pid := gen_random_uuid();
                INSERT INTO participaciones (id, contacto_id, tipo, fecha, estado, eliminado, fecha_creacion)
                VALUES (pid, r.cid, '{tipo}', COALESCE(r.fecha_creacion, NOW()),
                        'registrada', FALSE, COALESCE(r.fecha_creacion, NOW()));
                UPDATE {table} SET participacion_id = pid WHERE id = r.id;
            END LOOP;
        END $$;
    """)
    op.execute(
        f"CREATE UNIQUE INDEX IF NOT EXISTS ux_{table}_participacion "
        f"ON {table}(participacion_id)"
    )
    op.execute(
        f"ALTER TABLE {table} ADD CONSTRAINT fk_{table}_participacion "
        f"FOREIGN KEY (participacion_id) REFERENCES participaciones(id) ON DELETE CASCADE"
    )
    if not_null:
        op.execute(f"ALTER TABLE {table} ALTER COLUMN participacion_id SET NOT NULL")


def upgrade() -> None:
    # firmas_campania: contacto_id NOT NULL -> participacion_id NOT NULL.
    _wire_satellite('firmas_campania', 'FIRMA', 'contacto_id', not_null=True)
    # donaciones: contacto_id nullable (donación anónima/sin contacto) -> nullable.
    _wire_satellite('donaciones', 'DONACION', 'contacto_id', not_null=False)

    # sec_convenios: la contraparte era texto libre (entidad_contraparte/
    # nif_contraparte); ahora es un Contacto PERSONA_JURIDICA. Materializar el
    # Contacto (deduplicando por CIF) y enlazar contraparte_id antes de engancharlo.
    op.execute("ALTER TABLE sec_convenios ADD COLUMN IF NOT EXISTS contraparte_id UUID")
    op.execute("""
        DO $$
        DECLARE r record; cid uuid;
        BEGIN
            FOR r IN SELECT id, entidad_contraparte, nif_contraparte
                     FROM sec_convenios
                     WHERE contraparte_id IS NULL
                       AND COALESCE(NULLIF(entidad_contraparte, ''), NULLIF(nif_contraparte, '')) IS NOT NULL
            LOOP
                cid := NULL;
                IF NULLIF(r.nif_contraparte, '') IS NOT NULL THEN
                    SELECT id INTO cid FROM contactos
                    WHERE cif = r.nif_contraparte AND tipo = 'PERSONA_JURIDICA' LIMIT 1;
                END IF;
                IF cid IS NULL THEN
                    cid := gen_random_uuid();
                    INSERT INTO contactos (id, tipo, nombre, razon_social, cif, activo, eliminado,
                                           solicita_supresion_datos, datos_anonimizados, fecha_creacion)
                    VALUES (cid, 'PERSONA_JURIDICA',
                            COALESCE(NULLIF(r.entidad_contraparte, ''), 'Entidad'),
                            NULLIF(r.entidad_contraparte, ''), NULLIF(r.nif_contraparte, ''),
                            TRUE, FALSE, FALSE, FALSE, NOW());
                END IF;
                UPDATE sec_convenios SET contraparte_id = cid WHERE id = r.id;
            END LOOP;
        END $$;
    """)
    op.execute(
        "ALTER TABLE sec_convenios ADD CONSTRAINT fk_sec_convenios_contraparte "
        "FOREIGN KEY (contraparte_id) REFERENCES contactos(id) ON DELETE SET NULL"
    )
    op.execute("ALTER TABLE sec_convenios DROP COLUMN IF EXISTS entidad_contraparte")
    op.execute("ALTER TABLE sec_convenios DROP COLUMN IF EXISTS nif_contraparte")

    _wire_satellite('sec_convenios', 'CONVENIO', 'contraparte_id', not_null=False)


def downgrade() -> None:
    for table, tipo in [('firmas_campania', 'FIRMA'), ('donaciones', 'DONACION'),
                        ('sec_convenios', 'CONVENIO')]:
        op.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS fk_{table}_participacion")
        op.execute(f"DROP INDEX IF EXISTS ux_{table}_participacion")
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS participacion_id")
        op.execute(f"DELETE FROM participaciones WHERE tipo = '{tipo}'")
