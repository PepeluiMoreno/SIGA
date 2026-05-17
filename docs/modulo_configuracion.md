# Módulo Configuración — estado y cambios pendientes

> **Workflow**: NO aplicar `alembic upgrade head` ni reiniciar backend por cada cambio.
> Acumular SQL y cambios de modelo aquí; ejecutar de una vez al cerrar el lote.

---

## Estado actual del modelo (2026-05-15)

### Tablas del módulo

| Tabla | Clase Python | Archivo | Descripción |
|---|---|---|---|
| `parametros_generales` | — | `catalog.py` / `models/` | Configuración global de la organización |
| catálogos generales | — | `catalog.py` | Tablas de referencia compartidas (países, provincias, etc.) |

El módulo de configuración incluye también los resolvers de configuración:
`backend/app/graphql/configuracion_resolvers.py`

### Parámetros generales editables desde UI

- Nombre, CIF, dirección, email de la organización
- SMTP: host, puerto, usuario (sin contraseña — las credenciales van en Docker/GitHub secrets)
- Integración Indico: URL, API key (pendiente)

---

## Pendientes de diseño

### 1. SMTP en Parámetros Generales

Los campos SMTP son editables desde la UI en la vista `ParametrosGenerales.vue`.
La contraseña SMTP **nunca** se almacena en la base de datos ni en archivos — va en secretos Docker/GitHub.
Ver memory: `project_smtp_config_parametros_generales.md`

### 2. Integración Indico (pendiente)

Estudiar API REST de Indico (docs.getindico.io/en/stable/api/) antes de implementar sincronización de eventos.
Los campos de configuración de Indico ya están añadidos en Parámetros Generales (URL + API key).
Ver memory: `project_indico_integration.md`

---

## Cambios pendientes de migrar

*(Vacío — acumular aquí cuando se acuerde el próximo lote)*

---

## Pasos para aplicar el lote

```bash
docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend alembic upgrade head
docker compose -f docker-compose.dev.yml --env-file .env.dev restart backend
```
