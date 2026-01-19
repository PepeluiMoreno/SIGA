# Decisiones de Mapeo Confirmadas

## ✅ DECISIONES CRÍTICAS RESUELTAS

### 1. Prioridad de teléfonos en MIEMBRO
**Decisión**: Priorizar móvil > fijo casa > fijo trabajo
- `telefono` ← TELMOVIL (si existe) o TELFIJOCASA
- `telefono2` ← El que no se usó arriba

### 2. Profesión y Nivel de Estudios
**Decisión**: SÍ añadir campos al modelo Miembro, en sección voluntariado
- `profesion` ← PROFESION (MySQL)
- `nivel_estudios` ← ESTUDIOS (MySQL)
- **Contexto**: Solo se rellenan si `es_voluntario=true`

**IMPORTANTE**: Los tipos de miembro determinan sus características:
- **Miembro con cuota + Voluntario** (requiere_cuota=true, puede_votar=true, es_voluntario=true)
- **Miembro con cuota** (requiere_cuota=true, puede_votar=true, es_voluntario=false)
- **Voluntario** (requiere_cuota=false, puede_votar=false, es_voluntario=true)
- **Simpatizante** (requiere_cuota=false, puede_votar=false, es_voluntario=false)

Valores de TIPOMIEMBRO en MySQL: "socio", "simpatizante", "administrador", "voluntario"

### 3. Agrupación del miembro
**Decisión**: SÍ, inferir de última cuota
- Buscar en CUOTAANIOSOCIO el registro más reciente por CODSOCIO
- `agrupacion_id` ← Buscar UUID de agrupación por CODAGRUPACION

### 4. Provincia de agrupación
**Decisión**: Inferir del código postal (CP)
- Lógica: Buscar provincia que contenga ese CP en su rango
- Fallback: Buscar por nombre de localidad si CP no da resultado

### 5. Importe de cuota
**Decisión**: Confirmado mapeo propuesto
- `importe` ← IMPORTECUOTAANIOSOCIO (lo que DEBE pagar)
- `importe_pagado` ← IMPORTECUOTAANIOPAGADA (lo pagado REAL)
- `gastos_gestion` ← IMPORTEGASTOSABONOCUOTA

### 6. Estados de cuota
**Decisión**: Confirmado mapeo de valores
- ABONADA → PAGADA
- PENDIENTE-COBRO → PENDIENTE
- ABONADA-PARTE → PENDIENTE (con importe_pagado parcial)
- NOABONADA-DEVUELTA → VENCIDA
- NOABONADA-ERROR-CUENTA → PENDIENTE
- BAJA-SOCIO → EXENTA
- OTROS → PENDIENTE

---

## 🔄 CAMBIOS EN MODELOS REALIZADOS

### Modelo: Miembro
**Campos añadidos**:
```python
profesion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
nivel_estudios: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
```
- Ubicación: Sección voluntariado (líneas 83-84)
- Uso: Solo rellenar si `es_voluntario=true`

### Modelo: ImporteCuotaAnio
**Cambios realizados**:
1. **Añadido `tipo_miembro_id`**: Ahora las cuotas se definen POR TIPO DE MIEMBRO y ejercicio
2. **Añadido `nombre_cuota`**: Descriptivo (ej: "General", "Estudiante", "Parado")
3. **Añadido `observaciones`**: Notas sobre la cuota de ese tipo/ejercicio
4. **FK a TipoMiembro**: Relación con tipos_miembro

**Antes**:
```python
ejercicio: int (unique)
importe: Decimal
```

**Ahora**:
```python
ejercicio: int
tipo_miembro_id: UUID (FK)
importe: Decimal
nombre_cuota: str (opcional)
observaciones: text (opcional)
```

**Funcionalidad**:
- Permite cuotas diferenciadas por tipo (socio 50€, estudiante 25€, etc.)
- Mantiene histórico: cada cambio de cuota crea nuevo registro
- Constraint único: (ejercicio, tipo_miembro_id) para evitar duplicados por ejercicio

### Modelo: CuotaAnual
**Cambios realizados**:
1. **Añadido `importe_cuota_anio_id`**: FK a ImporteCuotaAnio (para trazabilidad)
2. **Añadido `gastos_gestion`**: Campo para IMPORTEGASTOSABONOCUOTA
3. **Activadas relaciones**: miembro, agrupacion, importe_cuota_anio, estado
4. **FK explícitos**: miembro_id y agrupacion_id ahora tienen ForeignKey

**Nueva estructura completa**:
```python
miembro_id: UUID (FK miembros)
ejercicio: int
agrupacion_id: UUID (FK agrupaciones_territoriales)
importe_cuota_anio_id: UUID (FK importes_cuota_anio, nullable)
importe: Decimal  # Lo que debe pagar
importe_pagado: Decimal  # Lo realmente pagado
gastos_gestion: Decimal  # Costes bancarios/PayPal
estado_id: UUID (FK estados_cuota)
modo_ingreso: Enum (SEPA/TRANSFERENCIA/PAYPAL/etc)
fecha_pago: date
fecha_vencimiento: date
observaciones: text
referencia_pago: str
```

---

## 📊 LÓGICA DE NEGOCIO IMPLEMENTADA

### Cuotas por Tipo de Miembro

**Escenario**: Europa Laica define cuotas anuales diferentes según el tipo de miembro.

**Ejemplo**:
```
Ejercicio 2025:
- Socio → 50.00 € (nombre_cuota: "General")
- Simpatizante → 30.00 € (nombre_cuota: "Apoyo")
- Estudiante → 25.00 € (nombre_cuota: "Reducida Estudiante")
- Parado → 20.00 € (nombre_cuota: "Reducida Desempleo")
```

**Histórico automático**:
- Si en 2026 cambia la cuota de socio a 55€ → nuevo registro
- Las cuotas de 2025 se mantienen inalteradas (histórico)

**Asignación de cuota a miembro**:
1. Se crea miembro con `tipo_miembro_id`
2. Al generar cuota para ejercicio X:
   - Se busca ImporteCuotaAnio donde ejercicio=X y tipo_miembro_id=miembro.tipo_miembro_id
   - Se crea CuotaAnual con:
     - importe ← ImporteCuotaAnio.importe
     - importe_cuota_anio_id ← ImporteCuotaAnio.id (trazabilidad)

---

## 🗂️ MAPEO FINAL CONFIRMADO

### MIEMBRO → miembros

| MySQL | PostgreSQL | Transformación | Notas |
|-------|-----------|----------------|-------|
| CODUSER | NO MAPEAR | Generar UUID nuevo | Guardar mapeo temporal CODUSER→UUID |
| TIPOMIEMBRO | tipo_miembro_id | Buscar UUID por código | "socio" / "simpatizante" / "administrador" |
| NUMDOCUMENTOMIEMBRO | numero_documento | **ENCRIPTAR** | Usar EncriptacionService |
| APE1, APE2, NOM | apellido1, apellido2, nombre | Directo | - |
| FECHANAC | fecha_nacimiento | NULL si '0000-00-00' | - |
| TELMOVIL / TELFIJOCASA / TELFIJOTRABAJO | telefono, telefono2 | Prioridad: móvil > casa > trabajo | - |
| PROFESION | profesion | Directo | Solo si es_voluntario |
| ESTUDIOS | nivel_estudios | Directo | Solo si es_voluntario |
| EMAIL | email | Validar formato | - |
| COLABORA | intereses + observaciones_voluntariado | Parsear | Marcar es_voluntario=true |
| CODPAISDOM | pais_domicilio_id | Buscar UUID por ISO | '--' → NULL |
| DIRECCION, CP, LOCALIDAD | direccion, codigo_postal, localidad | Directo | - |
| CODPROV | provincia_id | Buscar UUID por código | - |
| OBSERVACIONES + COMENTARIOSOCIO | observaciones_voluntariado | Concatenar | - |
| (de CUOTAANIOSOCIO) | agrupacion_id | Inferir de última cuota | - |
| (inferir) | fecha_alta | Año mínimo CUOTAANIOSOCIO | - |
| (EMAILERROR='BAJA') | fecha_baja, motivo_baja | Inferir | - |

### CUOTAANIOSOCIO → cuotas_anuales

| MySQL | PostgreSQL | Transformación | Notas |
|-------|-----------|----------------|-------|
| ANIOCUOTA | ejercicio | Convertir a int | - |
| CODSOCIO | miembro_id | Buscar UUID por CODUSER | Usar mapeo temporal |
| CODAGRUPACION | agrupacion_id | Buscar UUID por código | - |
| CODCUOTA + NOMBRECUOTA | importe_cuota_anio_id | Buscar por ejercicio+tipo | FK opcional (trazabilidad) |
| IMPORTECUOTAANIOSOCIO | importe | Directo | Lo que debe |
| IMPORTECUOTAANIOPAGADA | importe_pagado | Directo | Lo pagado real |
| IMPORTEGASTOSABONOCUOTA | gastos_gestion | Directo | - |
| ESTADOCUOTA | estado_id | Mapear valores | Ver tabla mapeo estados |
| MODOINGRESO | modo_ingreso | Enum | DOMICILIADA→SEPA, etc |
| FECHAPAGO | fecha_pago | NULL si '0000-00-00' | - |
| OBSERVACIONES | observaciones | Directo | - |
| NOMARCHIVOSEPAXML | remesa_id | Buscar por nombre | FK a remesas |

### IMPORTEDESCUOTAANIO → importes_cuota_anio

**NUEVA LÓGICA**: En MySQL solo hay importe por año. En PostgreSQL será por año + tipo de miembro.

**Transformación**:
1. Leer todos los registros de MySQL
2. Por cada ejercicio X con importe Y:
   - Obtener tipos de miembro existentes
   - Crear registro por cada tipo con mismo importe Y (inicialmente)
   - Nombre_cuota: "General" para todos inicialmente
3. Permitir ajuste manual posterior (estudiantes, parados, etc.)

---

## 🔐 CAMPOS A ENCRIPTAR (CRÍTICO)

1. **miembros.numero_documento**
2. **miembros.iban** (si se añade)
3. **agrupaciones_territoriales.cuenta_iban1**
4. **agrupaciones_territoriales.cuenta_iban2**

**Servicio**: `EncriptacionService.encriptar_iban()` / `encriptar_dni()`

---

## ✅ PRÓXIMOS PASOS

1. ✅ Actualizar modelo Miembro (profesion, nivel_estudios) - **HECHO**
2. ✅ Actualizar modelo ImporteCuotaAnio (tipo_miembro_id) - **HECHO**
3. ✅ Actualizar modelo CuotaAnual (gastos_gestion, FK mejorados) - **HECHO**
4. 🔄 Generar nueva migración Alembic
5. 🔄 Crear script importar_geografico.py
6. 🔄 Crear script importar_agrupaciones.py
7. 🔄 Crear script importar_cuotas_base.py
8. 🔄 Crear script importar_miembros.py (el más complejo)
9. 🔄 Crear script importar_cuotas_anuales.py
10. 🔄 Validar importación completa
