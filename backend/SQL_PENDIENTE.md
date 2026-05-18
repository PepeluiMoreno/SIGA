# SQL acumulado — pendiente de alembic upgrade

Aplicar cuando termine el lote. Instrucciones:
```
docker exec -it siga_dev_backend alembic upgrade head
docker restart siga_dev_backend
```

---

## Lote 1: APLICADO directamente — 2026-05-17

```sql
-- tareas — nuevas columnas
ALTER TABLE tareas
  ADD COLUMN IF NOT EXISTS habilidad_id UUID REFERENCES habilidades(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS nivel_habilidad_id UUID REFERENCES niveles_habilidad(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_tareas_habilidad_id ON tareas(habilidad_id);
CREATE INDEX IF NOT EXISTS ix_tareas_nivel_habilidad_id ON tareas(nivel_habilidad_id);

-- actividades — nuevas columnas
ALTER TABLE actividades
  ADD COLUMN IF NOT EXISTS duracion_horas NUMERIC(6,2),
  ADD COLUMN IF NOT EXISTS duracion_dias INTEGER,
  ADD COLUMN IF NOT EXISTS localidad VARCHAR(150),
  ADD COLUMN IF NOT EXISTS provincia VARCHAR(100);
```

> Aplicado directamente con docker exec siga_dev_db psql. Pendiente de reflejar
> en una migración Alembic formal para producción.

---

## Lote 2: Ámbito Geográfico — pendiente de aplicar

```sql
-- Catálogo de ámbitos geográficos (Nacional, CCAA, Provincia, Comarca, Municipio…)
CREATE TABLE IF NOT EXISTS ambitos_geograficos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(100) NOT NULL UNIQUE,
  descripcion TEXT,
  granularidad INTEGER NOT NULL DEFAULT 50,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en TIMESTAMPTZ DEFAULT now(),
  modificado_en TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_ambitos_geograficos_granularidad ON ambitos_geograficos(granularidad);
CREATE INDEX IF NOT EXISTS ix_ambitos_geograficos_activo ON ambitos_geograficos(activo);

-- Datos iniciales: ámbitos estándar para España
INSERT INTO ambitos_geograficos (nombre, descripcion, granularidad) VALUES
  ('Supranacional', 'Ámbito por encima del Estado (UE, internacional)', 5),
  ('Nacional',      'Ámbito estatal completo',                          10),
  ('CCAA',          'Comunidad Autónoma',                               20),
  ('Provincia',     'Provincia o territorio equivalente',               30),
  ('Comarca',       'Agrupación de municipios / comarca',               40),
  ('Municipio',     'Municipio o ciudad',                               50),
  ('Local',         'Barrio, distrito o entidad subnunicipal',          60)
ON CONFLICT (nombre) DO NOTHING;

-- FK en niveles_organizativos → ambitos_geograficos
ALTER TABLE niveles_organizativos
  ADD COLUMN IF NOT EXISTS ambito_geografico_id UUID
    REFERENCES ambitos_geograficos(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_niveles_organizativos_ambito_geografico_id
  ON niveles_organizativos(ambito_geografico_id);

-- Asignación inicial según los niveles ya existentes
-- (ajustar al nombre real de cada nivel si difiere)
UPDATE niveles_organizativos SET ambito_geografico_id = (
  SELECT id FROM ambitos_geograficos WHERE nombre = 'Nacional'
) WHERE nombre ILIKE '%sede central%' OR nivel = 1;

UPDATE niveles_organizativos SET ambito_geografico_id = (
  SELECT id FROM ambitos_geograficos WHERE nombre = 'CCAA'
) WHERE nombre ILIKE '%agrupaci%territorial%' OR nivel = 2;

UPDATE niveles_organizativos SET ambito_geografico_id = (
  SELECT id FROM ambitos_geograficos WHERE nombre = 'Provincia'
) WHERE nombre ILIKE '%grupo local%' OR nivel = 3;
```

> **Instrucciones**: ejecutar con `docker exec -it siga_dev_db psql -U siga -d siga`
> y después `docker restart siga_dev_backend`.
