# Informe de Migración de Datos

## Sistema de Gestión Integral de Asociados (SIGA)

**Fecha de migración:** Enero 2026
**Base de datos origen:** MySQL (europalaica_com)
**Base de datos destino:** PostgreSQL (Supabase)
**Versión del sistema:** 1.0.0

---

## 1. Resumen Ejecutivo

Se ha completado satisfactoriamente la migración de datos desde el sistema legacy MySQL hacia la nueva arquitectura PostgreSQL basada en Domain-Driven Design (DDD). El proceso incluyó transformaciones de datos, normalización de estructuras, encriptación de datos sensibles y cumplimiento normativo RGPD.

---

## 2. Procedimiento de Migración

### 2.1 Arquitectura de Scripts

La migración se organizó en scripts secuenciales numerados:

| Script | Descripción | Dependencias |
|--------|-------------|--------------|
| `1_crear_catalogos_base.py` | Crea catálogos maestros (tipos, estados) | Ninguna |
| `2_importar_geografico.py` | Importa países y provincias | Script 1 |
| `3_importar_agrupaciones.py` | Importa agrupaciones territoriales | Script 2 |
| `3b_establecer_jerarquia_agrupaciones.py` | Establece relaciones padre-hijo | Script 3 |
| `4_importar_miembros.py` | Importa miembros (miembros) | Script 3b |
| `5_importar_importes_cuota.py` | Importa tarifas de cuotas por año | Script 1 |
| `6_importar_cuotas_anuales.py` | Importa cuotas de miembros | Scripts 4, 5 |
| `7_importar_financiero_complementario.py` | Importa donaciones, remesas, órdenes | Script 6 |
| `8_actualizar_bajas_legacy.py` | Actualiza datos de bajas históricas | Script 4 |
| `8_validar_importacion.py` | Valida integridad de datos | Todos |

### 2.2 Métodos de Importación

Se implementaron múltiples estrategias según el volumen de datos:

1. **Inserción directa**: Para catálogos y registros pequeños
2. **Batch inserts**: Para miembros y cuotas (lotes de 100-1000 registros)
3. **CSV + COPY**: Variante optimizada para grandes volúmenes

### 2.3 Herramientas Desarrolladas

- **`sql_dump_parser.py`**: Parser de dumps SQL de phpMyAdmin
- **`mysql_helper.py`**: Context manager para conexiones MySQL
- **`ejecutar_importacion_completa.py`**: Orquestador automático
- **`ejecutar_importacion_interactiva.py`**: Orquestador con confirmación paso a paso

---

## 3. Mapeo de Tablas

### 3.1 Tablas Geográficas

| MySQL | PostgreSQL | Transformaciones |
|-------|------------|------------------|
| `PAIS` | `paises` | Normalización códigos ISO |
| `PROVINCIA` | `provincias` | FK a país, comunidad autónoma |
| `AGRUPACIONTERRITORIAL` | `agrupaciones_territoriales` | Jerarquía (Estatal→Autonómica→Provincial) |

### 3.2 Tablas de Miembros

| MySQL | PostgreSQL | Transformaciones |
|-------|------------|------------------|
| `MIEMBRO` | `miembros` | Encriptación DNI/IBAN, normalización nombres |
| `MIEMBROELIMINADO5ANIOS` | `miembros` | Marcados como `datos_anonimizados=true` |
| `miembroSFALLECIDOS` | `miembros` | `motivo_baja_id=FALLECIMIENTO` |
| `miembro` (campo SIMPATIZANTE) | `tipo_miembro_id` | SIMPATIZANTE si `SIMPATIZANTE=1` |

### 3.3 Tablas Financieras

| MySQL | PostgreSQL | Transformaciones |
|-------|------------|------------------|
| `CUOTAANIOmiembro` | `cuotas_anuales` | Estado calculado, modo ingreso mapeado |
| `IMPORTEDESCUOTAANIO` | `importes_cuota_anio` | Replicado por tipo de miembro |
| `DONACION` | `donaciones` | Asociación con campañas por concepto |
| `DONACIONCONCEPTOS` | `donaciones_conceptos` | Códigos truncados a 20 caracteres |
| `REMESAS_SEPAXML` | `remesas` | Referencias de archivos SEPA |
| `ORDENES_COBRO` | `ordenes_cobro` | Vinculación con remesas y cuotas |

---

## 4. Estadísticas de Migración

### 4.1 Registros Importados (Estimados)

| Entidad | Registros | Notas |
|---------|-----------|-------|
| Países | ~250 | Catálogo ISO completo |
| Provincias | ~52 | España + extranjero |
| Agrupaciones Territoriales | ~60+ | Jerarquía de 3 niveles |
| Miembros | ~5,000+ | Incluye histórico de bajas |
| Cuotas Anuales | ~50,000+ | Múltiples ejercicios |
| Importes Cuota | ~100+ | Por ejercicio × tipo |
| Conceptos Donación | ~10+ | Catálogo normalizado |
| Donaciones | ~1,000+ | Con asociación a campañas |
| Remesas SEPA | ~200+ | Archivos XML históricos |
| Órdenes de Cobro | ~30,000+ | Vinculadas a remesas |

### 4.2 Registros de Bajas Legacy

| Categoría | Registros | Tratamiento |
|-----------|-----------|-------------|
| Miembros fallecidos | 43 | `motivo_baja_id=FALLECIMIENTO` |
| Eliminados +5 años | 604 | `datos_anonimizados=true` |
| Con fecha límite retención | 1,082 | Calculado `fecha_baja + 6 años` |
| Límite ya expirado | 439 | Candidatos a anonimización |

---

## 5. Transformaciones de Datos

### 5.1 Encriptación

Los siguientes campos se encriptan en reposo usando AES-256:

- `numero_documento` (DNI/NIE/Pasaporte)
- `iban` (datos bancarios)

### 5.2 Normalización de Nombres

```
'JOSE LUIS' → 'Jose Luis'
'GARCÍA LÓPEZ' → 'García López'
```

### 5.3 Prioridad de Teléfonos

1. Móvil → `telefono`
2. Fijo casa → `telefono2`
3. Fijo trabajo → (descartado si hay móvil y fijo casa)

### 5.4 Mapeo de Estados de Cuota

| MySQL (ESTADOCUOTA) | PostgreSQL |
|---------------------|------------|
| `ABONADA` | `PAGADA` |
| `NOABONADA` | `PENDIENTE` |
| `DEVUELTA` | `DEVUELTA` |
| Sin pagar + > 0 pagado | `PARCIAL` |

### 5.5 Mapeo de Modos de Ingreso

| MySQL (MODOINGRESO) | PostgreSQL |
|---------------------|------------|
| `DOMICILIACIONBANCARIA` | `SEPA` |
| `INGRESOENBANCO` | `TRANSFERENCIA` |
| `EFECTIVOENPROVINCIA` | `EFECTIVO` |
| Otros | `OTRO` |

### 5.6 Asociación Donaciones-Campañas

| Concepto MySQL | Campaña |
|----------------|---------|
| `COSTAS-MEDALLA-VIRGEN-MERITO-POLICIAL` | `CAMP-MEDALLA-POLICIAL` |
| `GASTOS-JUDICIALES` | `CAMP-FONDO-JUDICIAL` |
| `VIII-CONGRESO-AILP-MADRID-2022` | `CAMP-CONGRESO-AILP-2022` |

---

## 6. Incidencias y Resoluciones

### 6.1 Incidencias Técnicas

| Incidencia | Causa | Resolución |
|------------|-------|------------|
| Error asyncpg AmbiguousParameterError | Parámetros en CASE SQL | Mover lógica CASE a Python |
| Truncamiento VARCHAR(500) | Campo observaciones muy largo | No concatenar observaciones largas |
| Timeout en importaciones grandes | Consultas sin límite | Implementar fetchmany con batches |
| Duplicados de email | Datos legacy inconsistentes | Permitir duplicados (no es UNIQUE) |

### 6.2 Datos Omitidos

| Tipo | Cantidad | Motivo |
|------|----------|--------|
| Donaciones sin fecha | Variable | `FECHAINGRESO` nulo o inválido |
| Órdenes sin miembro | Variable | `CODmiembro` no encontrado en mapeo |
| Órdenes sin remesa | Variable | Referencia SEPA no encontrada |
| Órdenes sin cuota | Variable | Cuota del ejercicio no existe |

### 6.3 Advertencias

- **Emails duplicados**: Se detectaron miembros con el mismo email. Se permitió para preservar datos históricos.
- **Miembros sin agrupación**: Algunos miembros activos no tienen agrupación asignada.
- **Cuotas sin agrupación**: Algunas cuotas antiguas no tienen agrupación vinculada.

---

## 7. Cumplimiento Normativo

### 7.1 RGPD (Reglamento General de Protección de Datos)

**Implementación del derecho de supresión (Art. 17):**

1. Campos añadidos al modelo `Miembro`:
   - `solicita_supresion_datos`: Indica solicitud de borrado
   - `fecha_solicitud_supresion`: Fecha de la solicitud
   - `fecha_limite_retencion`: Calculado como `fecha_baja + 6 años`
   - `datos_anonimizados`: Indica si ya fue anonimizado
   - `fecha_anonimizacion`: Fecha de ejecución de anonimización

2. **Proceso de anonimización diferida**:
   - Microservicio Docker: `services/rgpd-anonimizer/`
   - Ejecuta a las 3 AM diariamente (configurable)
   - Conserva referencias para registros contables
   - Anonimiza: nombre, DNI, email, teléfono, dirección, IBAN

### 7.2 PGC ESFL (Plan General de Contabilidad para ESFL)

**Retención de documentación contable 6 años:**

- Los datos financieros (cuotas, donaciones) se preservan íntegramente
- El miembro anonimizado mantiene su UUID para referencias FK
- Los registros de auditoría (`fecha_creacion`, `fecha_modificacion`) se conservan

### 7.3 Motivos de Baja Estructurados

| Código | Nombre | Requiere Documentación |
|--------|--------|------------------------|
| `VOLUNTARIA` | Baja voluntaria | No |
| `IMPAGO` | Baja por impago | No |
| `FALLECIMIENTO` | Fallecimiento | Sí (certificado defunción) |
| `EXPULSION` | Expulsión | Sí (acta disciplinaria) |

---

## 8. Migraciones de Base de Datos

### 8.1 Migraciones Alembic Ejecutadas

1. `019f010cd755` - Migración inicial DDD
2. `04ede766081e` - Todos los modelos de dominio
3. `32a0dc295063` - Campos profesión, nivel estudios
4. `ce6205f5e089` - Campo estado_id en miembros
5. `564207c255eb` - FK campaña en actividades
6. `5c2912c2f427` - Eliminar tabla acciones_campania
7. `8c6072307fac` - Server defaults en BaseModel
8. `c5c4f3434510` - Organizaciones y vista materializada
9. `1706f7b803ae` - Campo observaciones en miembros
10. `cf92a2404011` - Aumentar longitud numero_documento (255)
11. `70f5a36b7a69` - Campo sexo en miembros
12. `0e023bd10912` - Firmante, FirmaCampania y relación campaña-donación
13. `34e1d423d0c9` - Vista materializada segmentación
14. `e45d75d6204a` - Motivos de baja y campos RGPD

---

## 9. Verificación Post-Migración

### 9.1 Script de Validación

El script `8_validar_importacion.py` verifica:

- ✓ Totales MySQL vs PostgreSQL (tolerancia 90%)
- ✓ Integridad referencial (FK válidas)
- ✓ Datos huérfanos (registros sin padre)
- ✓ Lógica de negocio (estados coherentes)
- ✓ Duplicados de email (advertencia)

### 9.2 Consultas de Verificación Manual

```sql
-- Contar miembros por estado
SELECT em.codigo, COUNT(*)
FROM miembros m
JOIN estados_miembro em ON m.estado_id = em.id
GROUP BY em.codigo;

-- Verificar campos RGPD
SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE datos_anonimizados) as anonimizados,
    COUNT(*) FILTER (WHERE fecha_limite_retencion IS NOT NULL) as con_limite,
    COUNT(*) FILTER (WHERE fecha_limite_retencion < CURRENT_DATE) as limite_expirado
FROM miembros;

-- Cuotas por estado
SELECT ec.codigo, COUNT(*)
FROM cuotas_anuales ca
JOIN estados_cuota ec ON ca.estado_id = ec.id
GROUP BY ec.codigo;
```

---

## 10. Recomendaciones Post-Migración

1. **Ejecutar validación**: `python -m app.scripts.importacion.8_validar_importacion`
2. **Revisar advertencias**: Especialmente miembros sin agrupación
3. **Activar scheduler RGPD**: `docker-compose up -d rgpd-scheduler`
4. **Refrescar vistas materializadas**: Se hace automáticamente tras anonimización
5. **Backup inicial**: Realizar backup completo antes de producción

---

## 11. Anexos

### A. Estructura de Directorios

```
backend/app/scripts/importacion/
├── 1_crear_catalogos_base.py
├── 2_importar_geografico.py
├── 3_importar_agrupaciones.py
├── 3b_establecer_jerarquia_agrupaciones.py
├── 4_importar_miembros.py
├── 4_importar_miembros_csv.py      # Variante optimizada
├── 4_importar_miembros_mysql.py    # Conexión directa MySQL
├── 5_importar_importes_cuota.py
├── 6_importar_cuotas_anuales.py
├── 6_importar_cuotas_anuales_csv.py
├── 7_importar_financiero_complementario.py
├── 8_actualizar_bajas_legacy.py
├── 8_validar_importacion.py
├── ejecutar_importacion_completa.py
├── ejecutar_importacion_interactiva.py
├── sql_dump_parser.py
├── mysql_helper.py
└── __init__.py

services/rgpd-anonimizer/
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

### B. Variables de Entorno Requeridas

```bash
# Base de datos PostgreSQL (Supabase)
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx

# Base de datos MySQL (solo para importación)
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=xxx
MYSQL_DATABASE=europalaica_com

# Encriptación
ENCRYPTION_KEY=xxx  # AES-256 key

# RGPD Anonimizer
SCHEDULE_HOUR=3
SCHEDULE_MINUTE=0
```

---

**Documento generado automáticamente**
**SIGA - Sistema de Gestión Integral de Asociados**
