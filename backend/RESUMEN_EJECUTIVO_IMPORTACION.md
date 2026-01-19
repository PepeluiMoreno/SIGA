# Resumen Ejecutivo - Importación de Datos AIEL

## ✅ Estado Actual

### Modelos Completados
- ✅ 70+ modelos implementados en arquitectura DDD
- ✅ Todos con UUID como primary key
- ✅ Todas las ForeignKeys usando UUID (no códigos de negocio)
- ✅ Estados calculados con `@property` (no almacenados)
- ✅ Migraciones aplicadas y base de datos actualizada

### Cambios Recientes Aplicados
1. **Modelo Miembro**: Añadidos campos `profesion` y `nivel_estudios` (solo para voluntarios)
2. **Modelo ImporteCuotaAnio**: Modificado para soportar cuotas por tipo de miembro y ejercicio
3. **Modelo CuotaAnual**: Añadido `gastos_gestion`, FK a ImporteCuotaAnio, relaciones activadas

## 📊 Tipos de Miembro

Un miembro puede tener distintas características según su tipo:

| Tipo | requiere_cuota | puede_votar | Observaciones |
|------|---------------|-------------|---------------|
| **Miembro con cuota** | true | true | Paga cuota anual |
| **Voluntario** | false | false | No paga cuota, solo colabora |
| **Simpatizante** | false | false | Apoya sin colaborar activamente |
| **Administrador** | - | - | Usuario del sistema (especial) |

**IMPORTANTE**: El campo `es_voluntario` es independiente del tipo:
- Un miembro con cuota puede ser voluntario (`es_voluntario=true`)
- Un voluntario puro no paga cuota (`requiere_cuota=false`, `es_voluntario=true`)

## 🔄 Sistema de Cuotas Implementado

### Antes (MySQL)
```
IMPORTEDESCUOTAANIO: ejercicio + importe (único por año)
```

### Ahora (PostgreSQL)
```python
ImporteCuotaAnio:
  - ejercicio: int
  - tipo_miembro_id: UUID
  - importe: Decimal
  - nombre_cuota: str  # "General", "Estudiante", "Parado"
  - activo: bool
  - observaciones: text
```

### Beneficios
1. **Cuotas diferenciadas**: Cada tipo de miembro tiene su cuota (ej: 50€, 25€, 20€)
2. **Histórico automático**: Cada cambio crea nuevo registro
3. **Trazabilidad**: `CuotaAnual.importe_cuota_anio_id` enlaza con definición original

## 🗺️ Decisiones de Mapeo CRÍTICAS Confirmadas

### 1. Teléfonos (3 campos → 2)
```
Prioridad: móvil > fijo casa > fijo trabajo
- telefono ← TELMOVIL (si existe) o TELFIJOCASA
- telefono2 ← el que quedó libre
```

### 2. Profesión y Estudios
```
Solo se rellenan si es_voluntario=true:
- profesion ← PROFESION
- nivel_estudios ← ESTUDIOS
```

### 3. Agrupación del miembro
```
Inferir de última cuota en CUOTAANIOSOCIO:
- agrupacion_id ← buscar por CODAGRUPACION del año más reciente
```

### 4. Provincia de agrupación
```
Inferir del código postal:
1. Buscar provincia que contenga ese CP
2. Fallback: buscar por nombre localidad
```

### 5. Importes de cuota
```
importe ← IMPORTECUOTAANIOSOCIO (debe pagar)
importe_pagado ← IMPORTECUOTAANIOPAGADA (pagado real)
gastos_gestion ← IMPORTEGASTOSABONOCUOTA
```

### 6. Estados de cuota
```
ABONADA → PAGADA
PENDIENTE-COBRO → PENDIENTE
ABONADA-PARTE → PENDIENTE (con importe_pagado < importe)
NOABONADA-DEVUELTA → VENCIDA
NOABONADA-ERROR-CUENTA → PENDIENTE
BAJA-SOCIO → EXENTA
OTROS → PENDIENTE
```

## 🔒 Datos a ENCRIPTAR (Obligatorio)

Usar `EncriptacionService` antes de guardar:
1. `miembros.numero_documento`
2. `agrupaciones_territoriales.cuenta_iban1`
3. `agrupaciones_territoriales.cuenta_iban2`
4. Cualquier IBAN en tablas financieras

## 📁 Tablas MySQL → PostgreSQL

### Geográfico
- `PAIS` → `paises`
- `PROVINCIA` → `provincias`
- `CCAA` → (merge con provincias si necesario)

### Agrupaciones
- `AGRUPACIONTERRITORIAL` → `agrupaciones_territoriales`
- `AGRUPACIONTERRITORIAL_estatal_y_internacional` → (merge con anterior)

### Miembros
- `MIEMBRO` → `miembros` (principal)
- `SOCIO` → (verificar si es duplicado de MIEMBRO)
- `SIMPATIZANTE` → (verificar si es duplicado de MIEMBRO)
- `MIEMBROELIMINADO5ANIOS` → `miembros` (con fecha_baja)
- `SOCIOSFALLECIDOS` → `miembros` (motivo_baja="Fallecido")

### Cuotas
- `IMPORTEDESCUOTAANIO` → `importes_cuota_anio` (con tipo_miembro_id)
- `CUOTAANIOSOCIO` → `cuotas_anuales`

### Finanzas
- `DONACION` → `donaciones`
- `DONACIONCONCEPTOS` → `donacion_conceptos`
- `REMESAS_SEPAXML` → `remesas`
- `ORDENES_COBRO` + todas las `ORDEN_COBRO_20XX` → `ordenes_cobro`

### Sistema
- `USUARIO` → `usuarios`
- `ROL`, `FUNCION`, `ROLTIENEFUNCION`, `USUARIOTIENEROL` → NO IMPORTAR (rediseño)

### Ignorar (temporales/obsoletas)
- `CONTROLES`, `ERRORES` → logs
- `EXCELANDALUCIA`, `EXCELESTATAL`, `EXCELTODOS` → exports temp
- `CONFIRMAREMAILALTAGESTOR`, `SOCIOSCONFIRMAR` → procesos obsoletos
- `CODIGOSBIC` → catálogo bancario obsoleto
- `PAGOGASTOS_borrar`, `Donacion_Medalla_PayPal...` → tablas temp

## 🔢 Estrategia de IDs

### Problema
- **MySQL**: int auto-increment
- **PostgreSQL**: UUID

### Solución
1. Crear tabla temporal de mapeo durante importación:
   ```sql
   CREATE TEMP TABLE id_mapping (
     tabla varchar(50),
     old_id int,
     new_uuid uuid,
     PRIMARY KEY (tabla, old_id)
   );
   ```

2. Usar para resolver FKs:
   ```python
   # Ejemplo:
   old_coduser = 123
   new_uuid = mapeo['miembro'][old_coduser]
   ```

3. Eliminar tabla al finalizar

## 📋 Orden de Importación (CRÍTICO)

```
1. Catálogos base (NO tienen FK externas)
   ├── PAIS → paises
   ├── PROVINCIA → provincias
   ├── Crear tipos_miembro (socio, voluntario, simpatizante)
   └── Crear estados (cuota, campaña, tarea, etc.)

2. Agrupaciones (FK: pais, provincia)
   └── AGRUPACIONTERRITORIAL → agrupaciones_territoriales

3. Importes de cuota base (FK: tipo_miembro)
   └── IMPORTEDESCUOTAANIO → importes_cuota_anio

4. Miembros (FK: tipo_miembro, pais, provincia, agrupacion)
   └── MIEMBRO → miembros

5. Cuotas anuales (FK: miembro, agrupacion, estado, importe_cuota_anio)
   └── CUOTAANIOSOCIO → cuotas_anuales

6. Finanzas (FK: miembro, agrupacion, cuota)
   ├── DONACIONCONCEPTOS → donacion_conceptos
   ├── DONACION → donaciones
   ├── REMESAS_SEPAXML → remesas
   └── ORDENES_COBRO → ordenes_cobro

7. Usuarios sistema (FK: miembro opcional)
   └── USUARIO → usuarios
```

## 🎯 Scripts a Crear

### Fase 1: Preparación
```bash
1. crear_catalogos_base.py
   - Crear tipos_miembro: socio, voluntario, simpatizante
   - Crear estados_cuota: PENDIENTE, PAGADA, VENCIDA, EXENTA
   - Crear estados de otros dominios
```

### Fase 2: Geográfico
```bash
2. importar_geografico.py
   - Leer PAIS, PROVINCIA del dump MySQL
   - Crear en PostgreSQL
   - Retornar mapeo codigo → UUID
```

### Fase 3: Organizativo
```bash
3. importar_agrupaciones.py
   - Leer AGRUPACIONTERRITORIAL
   - Encriptar IBANs
   - Inferir provincia_id por CP
   - Retornar mapeo CODAGRUPACION → UUID
```

### Fase 4: Cuotas Base
```bash
4. importar_importes_cuota.py
   - Leer IMPORTEDESCUOTAANIO
   - Por cada ejercicio, crear registro por tipo_miembro
   - Mismo importe para todos inicialmente
   - Retornar mapeo (ejercicio, tipo) → UUID
```

### Fase 5: Miembros (COMPLEJO)
```bash
5. importar_miembros.py
   - Leer MIEMBRO, consolidar con otras tablas
   - Encriptar numero_documento
   - Mapear TIPOMIEMBRO → tipo_miembro_id
   - Inferir agrupacion_id de CUOTAANIOSOCIO
   - Inferir fecha_alta, fecha_baja
   - Marcar es_voluntario si COLABORA tiene datos
   - Priorizar teléfonos: móvil > casa > trabajo
   - Retornar mapeo CODUSER → UUID
```

### Fase 6: Cuotas Anuales
```bash
6. importar_cuotas_anuales.py
   - Leer CUOTAANIOSOCIO
   - Relacionar con miembro, agrupacion, estado
   - Mapear ESTADOCUOTA → estado_id
   - Convertir MODOINGRESO → modo_ingreso (enum)
   - Validar fechas '0000-00-00' → NULL
```

### Fase 7: Finanzas
```bash
7. importar_donaciones.py
   - Leer DONACIONCONCEPTOS, DONACION

8. importar_remesas.py
   - Leer REMESAS_SEPAXML

9. importar_ordenes_cobro.py
   - Consolidar todas las ORDEN_COBRO_20XX
   - Relacionar con cuotas_anuales
```

### Fase 8: Validación
```bash
10. validar_importacion.py
    - Verificar counts totales
    - Verificar integridad referencial
    - Detectar datos huérfanos
    - Generar reporte CSV con resumen
```

## 📊 Métricas Estimadas

Basado en dump de 16.8 MB:

| Tabla | Registros Estimados |
|-------|---------------------|
| Países | ~200 |
| Provincias | ~100 |
| Agrupaciones | ~80 |
| **Miembros** | **10,000 - 50,000** |
| Tipos Miembro | 4 |
| Estados Cuota | 4 |
| Importes Cuota | ~60 (15 años × 4 tipos) |
| **Cuotas Anuales** | **50,000 - 200,000** |
| Donaciones | ~500 - 2,000 |
| Remesas | ~100 - 500 |
| Órdenes Cobro | ~1,000 - 5,000 |

## ⚠️ Riesgos y Mitigaciones

### Riesgo 1: Datos duplicados MIEMBRO/SOCIO/SIMPATIZANTE
**Mitigación**: Verificar con query si CODUSER se repite, usar MIEMBRO como fuente única

### Riesgo 2: Fechas inválidas '0000-00-00'
**Mitigación**: Convertir a NULL, log de conversiones

### Riesgo 3: Provincias no encontradas por CP
**Mitigación**: Fallback a búsqueda por nombre, log de fallbacks

### Riesgo 4: Agrupación no encontrada para miembro
**Mitigación**: Permitir NULL, reportar en log, revisar manualmente

### Riesgo 5: Documentos duplicados
**Mitigación**: Constraint unique, detectar en pre-validación, reportar conflictos

## 🚀 Próximo Paso Inmediato

Crear `1_crear_catalogos_base.py` para inicializar tipos y estados básicos.
