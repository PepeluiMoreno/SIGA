# Scripts de Importación MySQL → PostgreSQL

Este directorio contiene todos los scripts necesarios para importar los datos históricos desde el dump MySQL de Europa Laica al nuevo sistema PostgreSQL con arquitectura DDD.

## 📋 Índice

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración](#configuración)
3. [Orden de Ejecución](#orden-de-ejecución)
4. [Descripción de Scripts](#descripción-de-scripts)
5. [Decisiones de Mapeo](#decisiones-de-mapeo)
6. [Troubleshooting](#troubleshooting)

## 🔧 Requisitos Previos

### Software Necesario

- Python 3.11+
- PostgreSQL 15+ (base de datos destino)
- MySQL/MariaDB (para leer el dump)
- Dependencias Python:
  ```bash
  pip install pymysql sqlalchemy asyncpg cryptography
  ```

### Archivos Necesarios

- Dump MySQL: `data/europalaica_com_2026_01_01 apertura de año.sql`
- Variables de entorno configuradas en `.env`:
  ```bash
  DATABASE_URL=postgresql+asyncpg://user:password@localhost/SIGA
  ENCRYPTION_KEY=<tu_clave_fernet>
  ```

### Base de Datos

1. **Crear base de datos PostgreSQL limpia**:
   ```bash
   createdb SIGA
   ```

2. **Ejecutar migraciones de Alembic**:
   ```bash
   alembic upgrade head
   ```

3. **Importar dump MySQL** (si no está ya cargado):
   ```bash
   mysql -u root -p europalaica_com < data/europalaica_com_2026_01_01\ apertura\ de\ año.sql
   ```

## ⚙️ Configuración

### Configurar Credenciales MySQL

Cada script tiene una constante `MYSQL_CONFIG` al inicio. Ajustarla según tu entorno:

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'tu_password',  # CAMBIAR ESTO
    'database': 'europalaica_com',
    'charset': 'utf8mb4'
}
```

### Generar Clave de Encriptación

Si no tienes `ENCRYPTION_KEY` en tu `.env`:

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Copiar esta clave al .env
```

## 🚀 Orden de Ejecución

### Opción 1: Ejecutar Todo Automáticamente (Recomendado)

```bash
cd backend
python -m app.scripts.importacion.ejecutar_importacion_completa
```

Este script ejecutará todos los pasos en orden y se detendrá si hay errores.

### Opción 2: Ejecutar Scripts Individualmente

```bash
# Paso 1: Crear catálogos base (OBLIGATORIO PRIMERO)
python -m app.scripts.importacion.1_crear_catalogos_base

# Paso 2: Importar datos geográficos
python -m app.scripts.importacion.2_importar_geografico

# Paso 3: Importar agrupaciones territoriales
python -m app.scripts.importacion.3_importar_agrupaciones

# Paso 4: Importar miembros (el más complejo)
python -m app.scripts.importacion.4_importar_miembros

# Paso 5: Importar importes de cuota por año
python -m app.scripts.importacion.5_importar_importes_cuota

# Paso 6: Importar cuotas anuales
python -m app.scripts.importacion.6_importar_cuotas_anuales

# Paso 7: Importar datos financieros complementarios
python -m app.scripts.importacion.7_importar_financiero_complementario

# Paso 8: Validar importación
python -m app.scripts.importacion.8_validar_importacion
```

## 📄 Descripción de Scripts

### 1. `1_crear_catalogos_base.py`

**Propósito**: Inicializa los catálogos necesarios para las importaciones posteriores.

**Crea**:
- `tipos_miembro`: miembro, SIMPATIZANTE, VOLUNTARIO, COLABORADOR
- `estados_cuota`: PENDIENTE, PAGADA, PARCIAL, VENCIDA, EXENTA, CANCELADA
- `estados_campania`: BORRADOR, PLANIFICADA, ACTIVA, SUSPENDIDA, FINALIZADA, CANCELADA
- `estados_actividad`: PROPUESTA, APROBADA, PROGRAMADA, EN_CURSO, COMPLETADA, CANCELADA
- `estados_participante`: INVITADO, ACTIVO, INACTIVO, RETIRADO

**Output**: Imprime UUIDs generados para cada catálogo.

### 2. `2_importar_geografico.py`

**Propósito**: Importa países y provincias.

**Tablas MySQL → PostgreSQL**:
- `PAIS` → `paises`
- `PROVINCIA` → `provincias`

**Genera**: Tabla temporal `temp_id_mapping` con mapeo `old_id → new_uuid`.

**Características**:
- Valida códigos ISO de países
- Relaciona provincias con países
- Maneja duplicados por código ISO

### 3. `3_importar_agrupaciones.py`

**Propósito**: Importa agrupaciones territoriales.

**Tablas MySQL → PostgreSQL**:
- `AGRUPACIONTERRITORIAL` → `agrupaciones_territoriales`
- `AGRUPACIONTERRITORIAL_estatal_y_internacional` → `agrupaciones_territoriales` (merge)

**Características**:
- **Encripta IBANs** antes de almacenarlos
- Mapea `AMBITO` → `tipo` (ESTATAL, AUTONOMICA, PROVINCIAL, LOCAL)
- Relaciona con provincias por `CODPROV`
- Calcula `activo` basado en `ESTADO` de MySQL

### 4. `4_importar_miembros.py`

**Propósito**: Importa miembros (el script más complejo).

**Tablas MySQL → PostgreSQL**:
- `MIEMBRO` → `miembros`
- `MIEMBROELIMINADO5ANIOS` → `miembros` (con fecha_baja)
- `miembroSFALLECIDOS` → `miembros` (con motivo_baja='Fallecido')

**Decisiones de Mapeo Implementadas**:

1. **Teléfonos** (Decisión 1):
   - Prioridad: móvil > fijo_casa > fijo_trabajo
   - `telefono` = primer disponible
   - `telefono2` = segundo disponible

2. **Profesión/Estudios** (Decisión 2):
   - Solo se llenan si `es_voluntario=True`
   - Van en sección de voluntariado

3. **Agrupación** (Decisión 3):
   - Se infiere de la última cuota en `CUOTAANIOmiembro`

4. **Provincia** (Decisión 4):
   - Se infiere por código postal (2 primeros dígitos)
   - Fallback a `CODPROV` directo

5. **Tipo de Miembro**:
   - Mapea `TIPOMIEMBRO` → `tipo_miembro_id`
   - Soporta: miembro, simpatizante, voluntario

**Características**:
- **Encripta DNI/NIE e IBANs**
- Detecta voluntarios por campo `COLABORA`
- Maneja bajas y fallecidos
- Genera UUIDs nuevos (no usa `CODUSER` directamente)

### 5. `5_importar_importes_cuota.py`

**Propósito**: Importa importes de cuota por año y tipo de miembro.

**Tablas MySQL → PostgreSQL**:
- `IMPORTEDESCUOTAANIO` → `importes_cuota_anio`

**Características**:
- Genera un registro por cada combinación `(ejercicio, tipo_miembro)`
- En MySQL solo hay un importe por año, se replica para cada tipo con cuota
- Permite ajustes especiales (ej: reducir cuota para simpatizantes)

### 6. `6_importar_cuotas_anuales.py`

**Propósito**: Importa cuotas anuales de miembros.

**Tablas MySQL → PostgreSQL**:
- `CUOTAANIOmiembro` → `cuotas_anuales`

**Características**:
- Relaciona miembros con cuotas por ejercicio
- Calcula `estado_id` basado en importes y fechas:
  - `PAGADA`: importe_pagado >= importe
  - `PARCIAL`: 0 < importe_pagado < importe
  - `VENCIDA`: importe_pagado == 0 y fecha_vencimiento pasada
  - `PENDIENTE`: importe_pagado == 0 y fecha_vencimiento futura
- Mapea `modo_ingreso`: SEPA, TRANSFERENCIA, PAYPAL, EFECTIVO, TARJETA
- Relaciona con `importe_cuota_anio_id` para trazabilidad

### 7. `7_importar_financiero_complementario.py`

**Propósito**: Importa datos financieros adicionales.

**Tablas MySQL → PostgreSQL**:
- `DONACIONCONCEPTOS` → `donacion_conceptos`
- `DONACION` → `donaciones`
- `REMESAS_SEPAXML` → `remesas`
- `ORDENES_COBRO` + tablas históricas → `ordenes_cobro`

**Características**:
- Consolida todas las tablas `ORDEN_COBRO_*` históricas
- Relaciona donaciones con miembros y conceptos
- Relaciona órdenes de cobro con cuotas

### 8. `8_validar_importacion.py`

**Propósito**: Valida la integridad de la importación.

**Validaciones**:
- ✅ Totales: Compara counts MySQL vs PostgreSQL
- ✅ Integridad referencial: Verifica FKs no nulos
- ✅ Datos huérfanos: Detecta registros sin relaciones
- ✅ Lógica de negocio: Valida estados calculados
- ✅ Duplicados: Detecta emails repetidos

**Output**: Reporte con errores críticos y advertencias.

## 🗺️ Decisiones de Mapeo

### Resumen de Decisiones Confirmadas

| # | Decisión | Implementación |
|---|----------|----------------|
| 1 | Prioridad de teléfonos | móvil > fijo_casa > fijo_trabajo |
| 2 | Profesión/estudios | Solo si `es_voluntario=True` |
| 3 | Agrupación | Inferida de última cuota |
| 4 | Provincia | Por código postal (2 dígitos) |
| 5 | Importe de cuota | Mapeo confirmado |
| 6 | Estados | Mapeo confirmado |

Ver documentos completos:
- [`DECISIONES_MAPEO_CONFIRMADAS.md`](../../DECISIONES_MAPEO_CONFIRMADAS.md)
- [`MAPEO_CAMPOS_DETALLADO.md`](../../MAPEO_CAMPOS_DETALLADO.md)

## 🛠️ Troubleshooting

### Error: "Connection refused" (MySQL)

**Solución**: Verificar que MySQL esté corriendo y las credenciales sean correctas.

```bash
mysql -u root -p -e "SELECT 1"
```

### Error: "Tabla no existe"

**Solución**: Verificar que el dump MySQL esté completamente importado.

```bash
mysql -u root -p europalaica_com -e "SHOW TABLES"
```

### Error: "ENCRYPTION_KEY not found"

**Solución**: Generar y configurar la clave en `.env`:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### Error: "IntegrityError: FK constraint"

**Solución**: Verificar que los scripts se ejecuten en orden. Si ya ejecutaste algunos scripts parcialmente, considera limpiar la BD:

```sql
-- PostgreSQL
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

Luego re-ejecutar migraciones y scripts desde el principio.

### Advertencia: "Miembros sin agrupación"

**Esperado**: Algunos miembros históricos pueden no tener agrupación asignada. No es crítico.

### Advertencia: "Emails duplicados"

**Esperado**: Datos históricos pueden contener duplicados. Revisar manualmente si es necesario.

## 📊 Métricas Esperadas

Basado en el dump de 16.8 MB:

| Entidad | Estimado |
|---------|----------|
| Países | ~200 |
| Provincias | ~100 |
| Agrupaciones | ~80 |
| Miembros | 10,000-50,000 |
| Cuotas | 50,000-200,000 |
| Donaciones | 500-2,000 |
| Remesas | 100-500 |

## 🔒 Seguridad

### Datos Encriptados

Los siguientes campos se encriptan usando `EncriptacionService`:

- `miembros.numero_documento` (DNI/NIE/Pasaporte)
- `miembros.iban`
- `agrupaciones_territoriales.cuenta_iban1`
- `agrupaciones_territoriales.cuenta_iban2`

### Tabla Temporal

La tabla `temp_id_mapping` contiene el mapeo de IDs antiguos a UUIDs nuevos. Se puede eliminar después de la importación:

```sql
DROP TABLE IF EXISTS temp_id_mapping;
```

## 📝 Notas Finales

1. **Backup obligatorio**: Hacer backup de PostgreSQL antes de ejecutar.
2. **Modo transaccional**: Toda importación usa transacciones (rollback automático si falla).
3. **Logging detallado**: Todos los scripts imprimen progreso en tiempo real.
4. **Idempotencia**: Los scripts verifican duplicados antes de insertar (pueden re-ejecutarse).
5. **Validación post-importación**: SIEMPRE ejecutar el script de validación al final.

## 📞 Soporte

Si encuentras problemas durante la importación:

1. Revisa los logs de cada script
2. Ejecuta el validador para identificar problemas
3. Consulta los documentos de mapeo para entender las decisiones
4. Si persiste el error, reporta con el stack trace completo

---

**Última actualización**: 2026-01-19
**Versión**: 1.0
**Autor**: Claude Code (Anthropic)
