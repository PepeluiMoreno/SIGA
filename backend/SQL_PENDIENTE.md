# SQL acumulado — pendiente de alembic upgrade

Aplicar cuando termine el lote. Instrucciones:
```
docker exec -it siga-backend alembic upgrade head
docker restart siga-backend
```

---

## Lote 1: Tareas con habilidad + Actividades con ubicación completa y duración

### tareas — nuevas columnas
```sql
ALTER TABLE tareas
  ADD COLUMN IF NOT EXISTS habilidad_id UUID REFERENCES habilidades(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS nivel_habilidad_id UUID REFERENCES niveles_habilidad(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_tareas_habilidad_id ON tareas(habilidad_id);
CREATE INDEX IF NOT EXISTS ix_tareas_nivel_habilidad_id ON tareas(nivel_habilidad_id);
```

### actividades — nuevas columnas
```sql
ALTER TABLE actividades
  ADD COLUMN IF NOT EXISTS duracion_horas NUMERIC(6,2),
  ADD COLUMN IF NOT EXISTS duracion_dias INTEGER,
  ADD COLUMN IF NOT EXISTS localidad VARCHAR(150),
  ADD COLUMN IF NOT EXISTS provincia VARCHAR(100);
```
