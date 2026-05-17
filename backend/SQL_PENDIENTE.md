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
