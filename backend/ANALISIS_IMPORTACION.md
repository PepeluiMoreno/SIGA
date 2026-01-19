# Análisis del Dump MySQL de Europa Laica

## Información General
- **Archivo**: `europalaica_com_2026_01_01 apertura de año.sql`
- **Tamaño**: 16.8 MB
- **Base de datos origen**: MySQL/MariaDB (`europalaica_com`)
- **Fecha dump**: 2026-01-01
- **Servidor**: MariaDB 10.3.39
- **Total de tablas**: 46

## Tablas Principales y Mapeo a Nuevo Modelo

### 1. Datos Geográficos
| Tabla Origen | Tabla Destino | Notas |
|-------------|---------------|-------|
| `PAIS` | `paises` | Mapeo directo |
| `PROVINCIA` | `provincias` | Mapeo directo |
| `CCAA` | provincias (parcial) | Comunidades autónomas → provincias |

### 2. Agrupaciones Territoriales
| Tabla Origen | Tabla Destino | Notas |
|-------------|---------------|-------|
| `AGRUPACIONTERRITORIAL` | `agrupaciones_territoriales` | Principal |
| `AGRUPACIONTERRITORIAL_estatal_y_internacional` | `agrupaciones_territoriales` | Merge con principal |

**Campos clave en origen**:
- `CODAGRUPACION` (varchar 8) → mapear a código único
- `NOMAGRUPACION` → nombre
- `AMBITO` (estatal/autonomico/provincial/local) → tipo
- `ESTADO` (activa/inactiva/baja) → calcular estado
- `CUENTAAGRUPIBAN1`, `CUENTAAGRUPIBAN2` → datos bancarios (encriptar)

### 3. Miembros/Socios
| Tabla Origen | Tabla Destino | Notas |
|-------------|---------------|-------|
| `MIEMBRO` | `miembros` | Principal - contiene socios y simpatizantes |
| `SOCIO` | `miembros` (filtro tipo) | Posible redundancia |
| `SIMPATIZANTE` | `miembros` (filtro tipo) | Posible redundancia |
| `MIEMBROELIMINADO5ANIOS` | miembros (con fecha_baja) | Histórico de bajas |
| `SOCIOSFALLECIDOS` | miembros (motivo_baja) | Fallecidos |

**Campos clave en MIEMBRO**:
- `CODUSER` (int) → NO usar como UUID, generar nuevo
- `TIPOMIEMBRO` (socio/simpatizante) → `tipos_miembro`
- `NUMDOCUMENTOMIEMBRO` → numero_documento (encriptar)
- `TIPODOCUMENTOMIEMBRO` → tipo_documento
- `APE1`, `APE2`, `NOM` → apellido1, apellido2, nombre
- `EMAIL` → email
- `CODPAISDOM` → pais_domicilio_id (buscar en paises)
- `CODPROV` (int) → provincia_id (buscar en provincias)
- `DIRECCION`, `CP`, `LOCALIDAD` → datos de contacto
- `COLABORA` → observaciones_voluntariado

### 4. Cuotas y Finanzas
| Tabla Origen | Tabla Destino | Notas |
|-------------|---------------|-------|
| `CUOTAANIOSOCIO` | `cuotas_anuales` | Cuotas por año y socio |
| `IMPORTEDESCUOTAANIO` | `importes_cuota_anio` | Importes de cuota por año |
| `ORDENES_COBRO` | `ordenes_cobro` | Órdenes de cobro |
| `REMESAS_SEPAXML` | `remesas` | Remesas SEPA |
| `DONACION` | `donaciones` | Donaciones |
| `DONACIONCONCEPTOS` | `donacion_conceptos` | Conceptos de donación |

**Tablas históricas de órdenes** (consolidar en ordenes_cobro):
- `ORDEN_COBRO_2013`
- `ORDEN_COBRO_2014_05_19`
- `ORDEN_COBRO_2015_05_01`
- ...

### 5. Usuarios y Roles (Sistema)
| Tabla Origen | Tabla Destino | Notas |
|-------------|---------------|-------|
| `USUARIO` | `usuarios` | Usuarios del sistema |
| `ROL` | NO MAPEAR | Sustituido por `usuario_roles` |
| `ROLTIENEFUNCION` | NO MAPEAR | Sistema de permisos nuevo |
| `USUARIOTIENEROL` | NO MAPEAR | Relación roles nueva |
| `FUNCION` | NO MAPEAR | Permisos rediseñados |

### 6. Áreas de Gestión (NO IMPLEMENTADO EN NUEVO MODELO)
Estas tablas NO tienen equivalente directo en el nuevo modelo DDD:
- `AREAGESTION`
- `AREAGESTIONAGRUPACIONESCOORD`
- `COORDINAAREAGESTIONAGRUP`

**Decisión**: Posiblemente reemplazado por grupos de trabajo o estructura de campañas.

### 7. Tablas de Control/Temporales (NO IMPORTAR)
- `CONTROLES` → logs/auditoría
- `CONTROLMODOAPLICACION` → config de aplicación vieja
- `ERRORES` → logs
- `EXCELANDALUCIA`, `EXCELESTATAL`, `EXCELTODOS` → exports temporales
- `CONFIRMAREMAILALTAGESTOR` → proceso de confirmación obsoleto
- `SOCIOSCONFIRMAR` → proceso de confirmación obsoleto
- `CODIGOSBIC` → catálogo bancario (posiblemente obsoleto)
- `PAGOGASTOS_borrar` → tabla temporal
- `Donacion_Medalla_PayPal_Sant_EXP_puntoD_2019_10_03_Final` → export temporal

## Estrategia de Importación

### Fase 1: Catálogos y Maestros (OBLIGATORIO PRIMERO)
1. **Países** (`PAIS` → `paises`)
   - Mapear códigos ISO
   - Mantener activos

2. **Provincias** (`PROVINCIA` → `provincias`)
   - Relacionar con países importados (buscar por código ISO)
   - Generar UUIDs nuevos

3. **Tipos de Miembro** (generar desde valores únicos de `TIPOMIEMBRO`)
   - Crear tipos: "socio", "simpatizante", "colaborador"
   - Asignar propiedades (requiere_cuota, puede_votar)

4. **Estados de Cuota** (generar catálogo)
   - PENDIENTE, PAGADA, VENCIDA, EXENTA

### Fase 2: Agrupaciones Territoriales
1. Merge de `AGRUPACIONTERRITORIAL` + `AGRUPACIONTERRITORIAL_estatal_y_internacional`
2. Mapear `AMBITO` → `tipo`
3. Relacionar con provincias (por código provincia en dirección)
4. **ENCRIPTAR** IBANs antes de guardar

### Fase 3: Miembros
1. Consolidar `MIEMBRO`, `SOCIO`, `SIMPATIZANTE`
2. Generar UUIDs nuevos (NO usar CODUSER)
3. Relacionar con:
   - tipo_miembro_id (buscar por código)
   - provincia_id (buscar por CODPROV)
   - pais_documento_id (buscar por CODPAISDOC)
   - pais_domicilio_id (buscar por CODPAISDOM)
   - agrupacion_id (buscar por CODAGRUPACION → código)
4. **ENCRIPTAR** datos sensibles:
   - numero_documento
   - iban (si existe)
5. Mapear campos voluntariado:
   - `COLABORA` → observaciones_voluntariado, intereses
6. Procesar eliminados:
   - `MIEMBROELIMINADO5ANIOS` → fecha_baja + motivo_baja
   - `SOCIOSFALLECIDOS` → fecha_baja + motivo_baja="Fallecido"

### Fase 4: Cuotas y Finanzas
1. **Importes de cuota por año** (`IMPORTEDESCUOTAANIO` → `importes_cuota_anio`)
2. **Cuotas anuales** (`CUOTAANIOSOCIO` → `cuotas_anuales`)
   - Relacionar con miembro_id (por CODUSER → buscar miembro)
   - Calcular estado_id basado en datos de pago
3. **Donaciones** (`DONACION` → `donaciones`)
4. **Conceptos de donación** (`DONACIONCONCEPTOS` → `donacion_conceptos`)
5. **Remesas SEPA** (`REMESAS_SEPAXML` → `remesas`)
6. **Órdenes de cobro** (consolidar todas las tablas `ORDEN_COBRO_*`)

### Fase 5: Usuarios del Sistema
1. Importar `USUARIO` → `usuarios`
2. **NO importar roles** (rediseñar permisos manualmente)
3. Generar contraseñas temporales
4. Forzar cambio de contraseña en primer login

## Consideraciones Técnicas

### Conversión de IDs
- **Origen**: MySQL con `int` auto-increment
- **Destino**: PostgreSQL con `uuid`
- **Estrategia**:
  - Crear tabla temporal de mapeo `old_id → new_uuid`
  - Usar durante importación para FKs
  - Eliminar al finalizar

### Encriptación
Campos que DEBEN encriptarse:
- `miembros.numero_documento`
- `miembros.iban`
- `agrupaciones_territoriales.cuenta_iban1`
- `agrupaciones_territoriales.cuenta_iban2`

Usar `EncriptacionService` del infrastructure.

### Datos Calculados vs Almacenados
- **Estados**: NO importar directamente, calcular con `@property`
  - Estado miembro: calcular por fecha_baja
  - Estado cuota: calcular por fechas de pago
  - Estado campaña: calcular por fechas inicio/fin

### Validaciones Durante Importación
1. **Integridad referencial**: Validar que todas las FKs existen
2. **Emails duplicados**: Detectar y reportar
3. **Documentos duplicados**: Detectar y reportar
4. **IBANs inválidos**: Validar formato antes de encriptar

## Scripts a Crear

### 1. `importar_geografico.py`
- Lee `PAIS`, `PROVINCIA`
- Crea registros en PostgreSQL
- Retorna mapeo `codigo → uuid`

### 2. `importar_agrupaciones.py`
- Lee `AGRUPACIONTERRITORIAL`
- Encripta IBANs
- Relaciona con provincias
- Retorna mapeo `CODAGRUPACION → uuid`

### 3. `importar_miembros.py`
- Lee `MIEMBRO` + consolidar otras tablas
- Encripta datos sensibles
- Relaciona con catálogos
- Maneja bajas y fallecidos
- Retorna mapeo `CODUSER → uuid`

### 4. `importar_financiero.py`
- Lee todas las tablas financieras
- Relaciona con miembros importados
- Calcula estados

### 5. `importar_usuarios.py`
- Lee `USUARIO`
- Genera contraseñas temporales
- Crear admin inicial

## Orden de Ejecución

```bash
# 1. Crear base de datos limpia
alembic upgrade head

# 2. Importar catálogos
python -m app.scripts.importar_geografico

# 3. Crear tipos y estados
python -m app.scripts.crear_catalogos_iniciales

# 4. Importar agrupaciones
python -m app.scripts.importar_agrupaciones

# 5. Importar miembros (el más complejo)
python -m app.scripts.importar_miembros

# 6. Importar finanzas
python -m app.scripts.importar_financiero

# 7. Importar usuarios sistema
python -m app.scripts.importar_usuarios

# 8. Validar integridad
python -m app.scripts.validar_importacion
```

## Métricas Esperadas

Basado en el tamaño del dump (16.8 MB), estimaciones:
- **Países**: ~200 registros
- **Provincias**: ~100 registros (principalmente España)
- **Agrupaciones**: ~80 registros
- **Miembros**: ~10,000-50,000 registros (núcleo del dump)
- **Cuotas**: ~50,000-200,000 registros
- **Órdenes de cobro**: ~1,000-5,000 registros
- **Donaciones**: ~500-2,000 registros

## Notas Finales

1. **Backup obligatorio**: Antes de cualquier importación, backup de PostgreSQL
2. **Modo transaccional**: Toda importación en transacción (rollback si falla)
3. **Logging detallado**: Log de cada registro importado para auditoría
4. **Reporte de errores**: CSV con registros que fallaron
5. **Validación post-importación**: Queries de verificación de counts y relaciones
