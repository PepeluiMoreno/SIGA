# Scripts de Volcado MySQL → PostgreSQL

Scripts para migrar datos desde la base de datos MySQL legacy a PostgreSQL.

## Requisitos

### Variables de entorno (.env)

```env
# MySQL (base de datos legacy)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_DATABASE=europalaica_db

# PostgreSQL (destino)
DATABASE_URL=postgresql+asyncpg://usuario:password@localhost:5432/siga
```

### Dependencias Python

```bash
pip install aiomysql asyncpg sqlalchemy[asyncio]
```

## Orden de Ejecución

| # | Script | Descripción | Fuente |
|---|--------|-------------|--------|
| 1 | `1_crear_catalogos_base.py` | Crear catálogos básicos (tipos, estados) | PostgreSQL |
| 2 | `2_importar_geografico.py` | Países, provincias, municipios | MySQL* |
| 3 | `3_importar_agrupaciones.py` | Agrupaciones territoriales | MySQL* |
| 3b | `3b_establecer_jerarquia.py` | Jerarquía de agrupaciones | PostgreSQL |
| 4 | `4_importar_miembros.py` | Miembros (miembros) con encriptación | MySQL |
| 5 | `5_importar_importes_cuota.py` | Catálogo de importes de cuota | MySQL |
| 6 | `6_importar_cuotas_anuales.py` | Historial de cuotas anuales | MySQL |
| 7 | `7_importar_financiero.py` | Donaciones, remesas, órdenes de cobro | MySQL |
| 8 | `8_validar_importacion.py` | Validación de integridad | PostgreSQL |

\* Los scripts 2 y 3 actualmente usan SQLDumpParser (archivo .sql). Para usar MySQL directo, ver sección "Migración pendiente".

## Uso

### Ejecutar volcado completo

```bash
python -m app.scripts.dump.ejecutar_volcado_completo
```

### Ejecutar desde un script específico

```bash
# Comenzar desde el script 4
python -m app.scripts.dump.ejecutar_volcado_completo --desde 4

# Ejecutar solo del 4 al 6
python -m app.scripts.dump.ejecutar_volcado_completo --desde 4 --hasta 6
```

### Ejecutar un script individual

```bash
# Solo el script 7
python -m app.scripts.dump.ejecutar_volcado_completo --solo 7

# O directamente
python -m app.scripts.dump.7_importar_financiero
```

## Estadísticas de la Última Migración

| Entidad | Importados | Omitidos | Notas |
|---------|------------|----------|-------|
| Agrupaciones | 55 | - | Con jerarquía provincial |
| Miembros | 2,273 | - | DNIs e IBANs encriptados |
| Importes cuota | 19 | - | Por ejercicio y tipo |
| Cuotas anuales | 20,174 | 887 | 95.8% de cobertura |
| Conceptos donación | 4 | - | - |
| Donaciones | 2,154 | 122 | Sin fecha válida |
| Remesas SEPA | 18 | - | - |
| Órdenes cobro | 6,677 | 233 | Sin miembro/cuota/remesa |

## Campos del Formulario de Alta

El modelo Miembro cubre todos los campos del formulario de alta:

- ✅ Datos personales: nombre, apellidos, sexo, fecha nacimiento
- ✅ Documento: tipo, número, país
- ✅ Contacto: email, teléfono móvil, teléfono fijo
- ✅ Domicilio: dirección, CP, localidad, país
- ✅ Profesión y estudios
- ✅ Datos bancarios: IBAN (encriptado)
- ✅ Agrupación territorial
- ✅ Observaciones

## Migración Pendiente

Los scripts 2 y 3 aún usan `SQLDumpParser` que lee de archivo .sql.
Para convertirlos a MySQL directo:

1. Cambiar import de `sql_dump_parser` a `.mysql_helper`
2. Reemplazar `parser.extraer_inserts('TABLA')` por queries MySQL
3. Usar `async with get_mysql_connection() as conn:`

## Notas Técnicas

### Tabla temp_id_mapping

Se usa para relacionar IDs antiguos (MySQL) con nuevos UUIDs (PostgreSQL):

```sql
CREATE TABLE temp_id_mapping (
    tabla VARCHAR(50) NOT NULL,
    old_id INTEGER NOT NULL,
    new_uuid UUID,
    PRIMARY KEY (tabla, old_id)
);
```

### Encriptación

Los campos sensibles (DNI, IBAN) se encriptan con el servicio de encriptación:
- `app.infrastructure.services.encriptacion_service`

### Fallback de Agrupación

Las cuotas usan fallback a agrupación provincial cuando la original no existe.
