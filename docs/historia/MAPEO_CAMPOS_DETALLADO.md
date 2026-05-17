# Mapeo Detallado de Campos MySQL → PostgreSQL

## TABLA: MIEMBRO → miembros

| Campo MySQL | Tipo MySQL | Campo PostgreSQL | Tipo PostgreSQL | Transformación | Notas/Ambigüedades |
|------------|------------|------------------|-----------------|----------------|-------------------|
| `CODUSER` | `int(10)` | NO MAPEAR DIRECTAMENTE | - | Generar nuevo UUID | ⚠️ **ID antiguo**: Guardar en tabla temporal para FKs |
| `CODPAISDOC` | `char(2)` | `pais_documento_id` | `uuid` | Buscar país por código ISO | ✅ OK |
| `TIPOMIEMBRO` | `varchar(50)` | `tipo_miembro_id` | `uuid` | Buscar tipo por código  | ⚠️ **Valores encontrados**: "miembro", "simpatizante", "administrador" |
| `NUMDOCUMENTOMIEMBRO` | `varchar(255)` | `numero_documento` | `varchar(50)` | **ENCRIPTAR** antes de guardar | 🔒 **CRÍTICO**: Usar EncriptacionService |
| `TIPODOCUMENTOMIEMBRO` | `varchar(30)` | `tipo_documento` | `varchar(20)` | Mapear directo | ⚠️ **Valores**: "NIF", "NIE", "Otros", "Pasaporte" |
| `APE1` | `varchar(255)` | `apellido1` | `varchar(100)` | Truncar si >100 chars | ✅ OK |
| `APE2` | `varchar(255)` | `apellido2` | `varchar(100)` | Truncar si >100 chars, NULL si vacío | ✅ OK |
| `NOM` | `varchar(255)` | `nombre` | `varchar(100)` | Truncar si >100 chars | ✅ OK |
| `SEXO` | `char(1)` | **NO MAPEAR** | - | Ignorar | ⚠️ **Decisión**: No almacenar sexo en nuevo modelo |
| `FECHANAC` | `date` | `fecha_nacimiento` | `date` | Mapear directo, NULL si '0000-00-00' | ⚠️ **Validar**: Fechas '0000-00-00' → NULL |
| `TELFIJOCASA` | `varchar(14)` | `telefono` | `varchar(20)` | Priorizar sobre TELFIJOTRABAJO | ⚠️ **Ambigüedad**: ¿Cuál teléfono priorizar? |
| `TELFIJOTRABAJO` | `varchar(14)` | `telefono2` | `varchar(20)` | Si TELFIJOCASA existe | ✅ OK |
| `TELMOVIL` | `varchar(14)` | `telefono` o `telefono2` | `varchar(20)` | Priorizar móvil si fijos vacíos | ⚠️ **Lógica**: Priorizar móvil > fijo casa > fijo trabajo |
| `PROFESION` | `varchar(255)` | **NO MAPEAR** | - | Ignorar o guardar en observaciones | ⚠️ **Decisión**: ¿Añadir campo profesion al modelo? |
| `ESTUDIOS` | `varchar(255)` | **NO MAPEAR** | - | Ignorar o guardar en observaciones | ⚠️ **Decisión**: ¿Añadir campo estudios al modelo? |
| `EMAIL` | `varchar(255)` | `email` | `varchar(200)` | Truncar si >200, validar formato | ✅ OK |
| `EMAILERROR` | `varchar(20)` | **NO MAPEAR** | - | Ignorar (log de emails con error) | ✅ OK |
| `INFORMACIONEMAIL` | `char(2)` | **NO MAPEAR** | - | Ignorar (preferencia comunicación) | ⚠️ **Pregunta**: ¿Crear PreferenciaNotificacion? |
| `INFORMACIONCARTAS` | `char(2)` | **NO MAPEAR** | - | Ignorar (preferencia comunicación) | ⚠️ **Pregunta**: ¿Crear PreferenciaNotificacion? |
| `COLABORA` | `varchar(255)` | `intereses` + `observaciones_voluntariado` | `varchar(1000)` | Parsear y distribuir | ⚠️ **Ambigüedad**: Contiene texto libre sobre colaboración |
| `CODPAISDOM` | `char(2)` | `pais_domicilio_id` | `uuid` | Buscar país por código ISO | ⚠️ **Valor especial**: '--' para "Estatal" → NULL |
| `DIRECCION` | `varchar(255)` | `direccion` | `varchar(500)` | Mapear directo | ✅ OK |
| `CP` | `varchar(100)` | `codigo_postal` | `varchar(20)` | Truncar si >20 | ✅ OK |
| `LOCALIDAD` | `varchar(255)` | `localidad` | `varchar(200)` | Truncar si >200 | ✅ OK |
| `CODPROV` | `int(10)` | `provincia_id` | `uuid` | Buscar provincia por código antiguo | ⚠️ **CRÍTICO**: Crear mapeo CODPROV → provincia UUID |
| `NOMPROVINCIA` | `varchar(255)` | **NO MAPEAR** | - | Redundante (viene de FK provincia) | ✅ OK |
| `ARCHIVOFIRMAPD` | `varchar(255)` | **NO MAPEAR** | - | Archivo físico, guardar path en observaciones | ⚠️ **Pregunta**: ¿Migrar archivos a nuevo storage? |
| `PATH_ARCHIVO_FIRMAS` | `varchar(4096)` | **NO MAPEAR** | - | Path antiguo, obsoleto | ✅ OK |
| `COMENTARIOmiembro` | `varchar(500)` | **NO MAPEAR** | - | Merge con OBSERVACIONES | ✅ OK |
| `OBSERVACIONES` | `varchar(2000)` | `observaciones_voluntariado` | `varchar(1000)` | Concatenar con COMENTARIOmiembro | ⚠️ **Ambigüedad**: Mezcla observaciones gestor + voluntariado |
| **IBAN** (de otras tablas) | - | `iban` | `varchar(500)` | **ENCRIPTAR** antes de guardar | 🔒 **CRÍTICO**: Buscar en tablas de órdenes de cobro |
| - | - | `agrupacion_id` | `uuid` | Buscar en CUOTAANIOmiembro.CODAGRUPACION | ⚠️ **Lógica**: Tomar agrupación del año más reciente |
| - | - | `fecha_alta` | `date` | Tomar año mínimo de CUOTAANIOmiembro | ⚠️ **Inferir**: No hay campo explícito de fecha alta |
| - | - | `fecha_baja` | `date` | NULL para activos | ⚠️ **Lógica**: Si EMAILERROR='BAJA' → buscar última cuota |
| - | - | `motivo_baja` | `varchar(500)` | NULL o texto de OBSERVACIONES | ⚠️ **Inferir**: No hay campo explícito |
| - | - | `activo` | `boolean` | Calcular: fecha_baja IS NULL | ✅ Calculado |
| - | - | `es_voluntario` | `boolean` | Inferir de COLABORA | ⚠️ **Heurística**: Si COLABORA no NULL → true |

### ⚠️ AMBIGÜEDADES Y DECISIONES CRÍTICAS - MIEMBRO

1. **Teléfonos múltiples**:
   - Origen: 3 campos (fijo casa, fijo trabajo, móvil)
   - Destino: 2 campos (telefono, telefono2)
   - **Propuesta**: Prioridad móvil > fijo casa > fijo trabajo
   - **¿Estás de acuerdo?**

2. **Profesión y Estudios**:
   - Origen: 2 campos con datos
   - Destino: No existen en modelo actual
   - **Opciones**:
     - A) Ignorar estos datos
     - B) Añadir campos al modelo Miembro
     - C) Guardar en observaciones_voluntariado
   - **¿Qué prefieres?**

3. **Preferencias de comunicación** (INFORMACIONEMAIL, INFORMACIONCARTAS):
   - Origen: Flags SI/NO para email y cartas
   - Destino: Modelo PreferenciaNotificacion existe
   - **Propuesta**: Crear registros en PreferenciaNotificacion por cada miembro
   - **¿Estás de acuerdo?**

4. **Campo COLABORA**:
   - Origen: Texto libre como "formacion", "actividades", "otros"
   - Destino: `intereses` + `observaciones_voluntariado`
   - **Propuesta**:
     - Si contiene palabras clave → `intereses`
     - Resto → `observaciones_voluntariado`
     - Marcar `es_voluntario=true`
   - **¿Estás de acuerdo?**

5. **Archivos de firma LOPD**:
   - Origen: Path y nombre de archivo en servidor viejo
   - **Opciones**:
     - A) Ignorar (obsoleto)
     - B) Guardar referencia en observaciones
     - C) Migrar archivos físicos a nuevo storage
   - **¿Qué prefieres?**

6. **Agrupación del miembro**:
   - Origen: No hay FK directo en MIEMBRO
   - Se debe inferir de CUOTAANIOmiembro.CODAGRUPACION
   - **Propuesta**: Tomar agrupación de la cuota del año más reciente
   - **¿Estás de acuerdo?**

7. **Fecha de alta**:
   - Origen: No existe campo explícito
   - **Propuesta**: Inferir del año mínimo en CUOTAANIOmiembro → 01/01/YYYY
   - **¿Estás de acuerdo?**

8. **Fecha y motivo de baja**:
   - Origen: Solo marcador EMAILERROR='BAJA'
   - **Propuesta**:
     - Si 'BAJA' → buscar último año con cuota
     - fecha_baja = 31/12/último_año
     - motivo_baja = texto de OBSERVACIONES si menciona "baja"
   - **¿Estás de acuerdo?**

---

## TABLA: AGRUPACIONTERRITORIAL → agrupaciones_territoriales

| Campo MySQL | Tipo MySQL | Campo PostgreSQL | Tipo PostgreSQL | Transformación | Notas/Ambigüedades |
|------------|------------|------------------|-----------------|----------------|-------------------|
| `CODAGRUPACION` | `varchar(8)` | **NO MAPEAR A ID** | - | Guardar como `codigo` | ⚠️ **CRÍTICO**: Mantener código antiguo para referencias |
| - | - | `id` | `uuid` | Generar nuevo UUID | ✅ OK |
| - | - | `codigo` | `varchar(50)` | Copiar de CODAGRUPACION | ✅ Mantener código original |
| `NOMAGRUPACION` | `varchar(255)` | `nombre` | `varchar(200)` | Truncar si >200 | ✅ OK |
| `CIF` | `varchar(10)` | **NO MAPEAR** | - | Ignorar (dato fiscal antiguo) | ⚠️ **Pregunta**: ¿Añadir campo CIF al modelo? |
| `GESTIONCUOTAS` | `varchar(50)` | **NO MAPEAR** | - | Ignorar (lógica de negocio obsoleta) | ✅ OK |
| `TITULARCUENTASBANCOS` | `varchar(255)` | **NO MAPEAR** | - | Ignorar (dato bancario antiguo) | ✅ OK |
| `CUENTAAGRUPIBAN1` | `varchar(24)` | `cuenta_iban1` | `varchar(34)` | **ENCRIPTAR** antes de guardar | 🔒 **CRÍTICO**: Usar EncriptacionService |
| `NOMBREIBAN1` | `varchar(255)` | `nombre_iban1` | `varchar(255)` | Mapear directo | ✅ OK |
| `CUENTAAGRUPIBAN2` | `varchar(24)` | `cuenta_iban2` | `varchar(34)` | **ENCRIPTAR** si no vacío | 🔒 **CRÍTICO**: Usar EncriptacionService |
| `NOMBREIBAN2` | `varchar(255)` | `nombre_iban2` | `varchar(255)` | Mapear directo si IBAN2 existe | ✅ OK |
| `TELFIJOTRABAJO` | `varchar(11)` | `telefono_fijo` | `varchar(20)` | Mapear directo | ✅ OK |
| `TELMOV` | `varchar(11)` | `telefono_movil` | `varchar(20)` | Mapear directo | ✅ OK |
| `WEB` | `varchar(255)` | `web` | `varchar(500)` | Validar formato URL | ✅ OK |
| `EMAIL` | `varchar(255)` | `email` | `varchar(200)` | Truncar si >200, validar | ✅ OK |
| `EMAILCOORD` | `varchar(255)` | `email_coordinador` | `varchar(200)` | Mapear directo | ✅ OK |
| `EMAILSECRETARIO` | `varchar(255)` | `email_secretario` | `varchar(200)` | Mapear directo | ✅ OK |
| `EMAILTESORERO` | `varchar(255)` | `email_tesorero` | `varchar(200)` | Mapear directo | ✅ OK |
| `AMBITO` | `varchar(255)` | `tipo` | `varchar(50)` | Mapear valores | ⚠️ **Valores**: estatal/autonomico/provincial/local/municipal/barrio |
| `ESTADO` | `varchar(20)` | **NO MAPEAR** | - | Calcular con @property | ⚠️ **Valores**: activa/inactiva/baja/absorvida |
| `CODPAISDOM` | `char(2)` | `pais_domicilio_id` | `uuid` | Buscar país por código | ⚠️ **Valor especial**: '--' → NULL |
| `DIRECCION` | `varchar(255)` | `direccion` | `varchar(500)` | Mapear directo | ✅ OK |
| `CP` | `varchar(100)` | `codigo_postal` | `varchar(20)` | Truncar si >20 | ✅ OK |
| `LOCALIDAD` | `varchar(255)` | `localidad` | `varchar(200)` | Truncar si >200 | ✅ OK |
| `OBSERVACIONES` | `varchar(255)` | `observaciones` | `text` | Mapear directo | ✅ OK |
| - | - | `provincia_id` | `uuid` | Inferir de CP o LOCALIDAD | ⚠️ **CRÍTICO**: Lógica de inferencia compleja |
| - | - | `activo` | `boolean` | true si ESTADO='activa' | ✅ Calculado |

### ⚠️ AMBIGÜEDADES Y DECISIONES CRÍTICAS - AGRUPACION

1. **CIF (identificación fiscal)**:
   - Origen: Existe en datos
   - Destino: No existe en modelo
   - **Pregunta**: ¿Añadir campo CIF al modelo AgrupacionTerritorial?
   - **Uso**: Puede ser necesario para facturación/fiscal

2. **Provincia de la agrupación**:
   - Origen: No hay FK directo a provincia
   - **Propuesta lógica inferencia**:
     - A) Extraer código provincia del CODAGRUPACION (ej: "00118000" → 18=Granada)
     - B) Buscar provincia por código postal
     - C) Buscar provincia por nombre de localidad
   - **¿Cuál método prefieres o combinación?**

3. **Estado de agrupación**:
   - Origen: Campo ESTADO con valores: activa/inactiva/baja/absorvida
   - Destino: Solo campo booleano `activo`
   - **Pregunta**: ¿Crear tabla EstadoAgrupacion con estos 4 estados?
   - **O simplificar**: activa→true, resto→false

4. **Valor especial CODPAISDOM='--'**:
   - Origen: Usado para "Estatal e Internacional"
   - **Propuesta**: Mapear a NULL (sin país asignado)
   - **¿Estás de acuerdo?**

---

## TABLA: CUOTAANIOmiembro → cuotas_anuales

| Campo MySQL | Tipo MySQL | Campo PostgreSQL | Tipo PostgreSQL | Transformación | Notas/Ambigüedades |
|------------|------------|------------------|-----------------|----------------|-------------------|
| `ANIOCUOTA` | `varchar(4)` | `ejercicio` | `integer` | Convertir a int | ✅ OK |
| `CODmiembro` | `int(10)` | `miembro_id` | `uuid` | Buscar miembro por CODUSER→UUID | ⚠️ **CRÍTICO**: Usar tabla mapeo temporal |
| `CODCUOTA` | `varchar(100)` | **NO MAPEAR** | - | Ignorar (tipo de cuota antiguo) | ⚠️ **Pregunta**: ¿Necesitamos tipos de cuota? |
| `CODAGRUPACION` | `varchar(8)` | `agrupacion_id` | `uuid` | Buscar agrupación por código | ⚠️ **CRÍTICO**: Usar tabla mapeo |
| `IMPORTECUOTAANIOEL` | `decimal(10,2)` | `importe_cuota` | `decimal(10,2)` | Mapear directo | ✅ OK |
| `NOMBRECUOTA` | `varchar(255)` | **NO MAPEAR** | - | Redundante | ✅ OK |
| `IMPORTECUOTAANIOmiembro` | `decimal(10,2)` | `importe_pagado` | `decimal(10,2)` | Usar como importe esperado | ⚠️ **Ambigüedad**: ¿Es lo esperado o lo pagado? |
| `IMPORTECUOTAANIOPAGADA` | `decimal(10,2)` | `importe_pagado` | `decimal(10,2)` | Mapear directo | ✅ Este es el pagado real |
| `IMPORTEGASTOSABONOCUOTA` | `decimal(10,2)` | `gastos_gestion` | `decimal(10,2)` | Mapear directo | ✅ OK |
| `FECHAPAGO` | `datetime` | `fecha_pago` | `datetime` | Mapear, NULL si '0000-00-00' | ⚠️ **Validar**: Fechas inválidas |
| `FECHAANOTACION` | `datetime` | **NO MAPEAR** | - | Usar created_at del modelo | ✅ OK |
| `MODOINGRESO` | `varchar(255)` | `forma_pago` | `varchar(50)` | Mapear valores | ⚠️ **Valores**: DOMICILIADA/METALICO/TRANSFERENCIA/CHEQUE/TARJETA |
| `CUENTAPAGO` | `varchar(34)` | `cuenta_pago` | `varchar(34)` | Mapear directo | ✅ OK |
| `ESTADOCUOTA` | `varchar(50)` | `estado_id` | `uuid` | Buscar estado por código | ⚠️ **Valores**: ABONADA/PENDIENTE-COBRO/ABONADA-PARTE/etc |
| `ORDENARCOBROBANCO` | `varchar(255)` | **NO MAPEAR** | - | Obsoleto | ✅ OK |
| `OBSERVACIONES` | `varchar(2000)` | `observaciones` | `text` | Mapear directo | ✅ OK |
| `NOMARCHIVOSEPAXML` | `varchar(255)` | `remesa_id` | `uuid` | Buscar remesa por nombre archivo | ⚠️ **CRÍTICO**: Crear FK a remesas |

### ⚠️ AMBIGÜEDADES Y DECISIONES CRÍTICAS - CUOTA

1. **Tipos de cuota** (CODCUOTA, NOMBRECUOTA):
   - Origen: Valores como "General", "Estudiante", etc.
   - Destino: No existe modelo TipoCuota
   - **Pregunta**: ¿Crear tabla tipos_cuota o ignorar?
   - **Alternativa**: Guardar en observaciones

2. **Importe de cuota - AMBIGÜEDAD CRÍTICA**:
   - `IMPORTECUOTAANIOEL`: "Cuota del miembro para ese año"
   - `IMPORTECUOTAANIOmiembro`: "Cuota que abonará" (≥ IMPORTECUOTAANIOEL)
   - `IMPORTECUOTAANIOPAGADA`: "Lo que ha pagado hasta la fecha"
   - **Propuesta mapeo**:
     - `importe_cuota` ← IMPORTECUOTAANIOEL (lo que DEBE)
     - `importe_pagado` ← IMPORTECUOTAANIOPAGADA (lo pagado REAL)
   - **¿Estás de acuerdo?**

3. **Estados de cuota**:
   - Origen: Valores string (ABONADA, PENDIENTE-COBRO, ABONADA-PARTE, etc.)
   - Destino: FK a tabla estados_cuota
   - **Mapeo propuesto**:
     - ABONADA → PAGADA
     - PENDIENTE-COBRO → PENDIENTE
     - ABONADA-PARTE → PENDIENTE (parcial)
     - NOABONADA-DEVUELTA → VENCIDA
     - NOABONADA-ERROR-CUENTA → PENDIENTE
     - BAJA-miembro → EXENTA
   - **¿Estás de acuerdo con este mapeo?**

4. **Relación con remesas**:
   - Origen: Campo NOMARCHIVOSEPAXML con nombre de archivo
   - Destino: FK `remesa_id`
   - **Propuesta**: Crear tabla REMESAS_SEPAXML primero, luego relacionar
   - **¿Estás de acuerdo?**

---

## TABLA: PAIS → paises

| Campo MySQL | Tipo MySQL | Campo PostgreSQL | Tipo PostgreSQL | Transformación | Notas |
|------------|------------|------------------|-----------------|----------------|-------|
| Estructura pendiente de extraer | - | - | - | - | Necesito ver CREATE TABLE |

---

## TABLA: PROVINCIA → provincias

| Campo MySQL | Tipo MySQL | Campo PostgreSQL | Tipo PostgreSQL | Transformación | Notas |
|------------|------------|------------------|-----------------|----------------|-------|
| Estructura pendiente de extraer | - | - | - | - | Necesito ver CREATE TABLE |

---

## RESUMEN DE DECISIONES PENDIENTES

### 🔴 CRÍTICAS (Bloqueantes)

1. **Prioridad teléfonos en MIEMBRO**: ¿móvil > fijo casa > fijo trabajo?
2. **Profesión y Estudios**: ¿Añadir campos al modelo o ignorar?
3. **Agrupación del miembro**: ¿Inferir de última cuota?
4. **Provincia de agrupación**: ¿Método de inferencia?
5. **Importe de cuota**: ¿Confirmar mapeo propuesto?
6. **Estados de cuota**: ¿Confirmar mapeo de valores?

### 🟡 IMPORTANTES (No bloqueantes)

7. **CIF de agrupación**: ¿Añadir campo al modelo?
8. **Preferencias de comunicación**: ¿Crear PreferenciaNotificacion?
9. **Archivos LOPD**: ¿Migrar, referenciar o ignorar?
10. **Tipos de cuota**: ¿Crear tabla o ignorar?
11. **Estado de agrupación**: ¿Tabla completa o boolean?

### 🟢 OPCIONALES (Mejoras)

12. **Campo COLABORA**: ¿Parsing inteligente o directo?
13. **Fecha de baja**: ¿Método de inferencia propuesto OK?

---

## PRÓXIMOS PASOS

Una vez respondas las decisiones pendientes, completaré:
- Tablas PAIS y PROVINCIA
- Tabla DONACION → donaciones
- Tabla REMESAS_SEPAXML → remesas
- Tabla ORDENES_COBRO → ordenes_cobro
- Tabla USUARIO → usuarios
