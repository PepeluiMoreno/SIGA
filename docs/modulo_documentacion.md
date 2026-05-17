# Módulo de Documentación SIGA

> Módulo transversal (como comunicación interna). Planificación y diseño.  
> Última actualización: 2026-05-15

---

## Propósito

Gestionar los documentos que genera o recibe la organización: archivos de texto, XML, JSON
y cualquier formato que represente una pieza de información completa y tratable como un todo.

El módulo **no almacena el contenido de los archivos** (sería un DMS completo). Gestiona:
- La **tipología** y el **ciclo de vida** de los documentos.
- Los **metadatos** (quién lo generó, cuándo, qué entidades están vinculadas).
- El **estado** del documento (borrador, emitido, archivado, anulado).
- Las **referencias** a la ubicación real del archivo (ruta local, URL externa, adjunto).

---

## Tipología de documentos

### Categorías principales

| Categoría | Ejemplos |
|---|---|
| **Actas y resoluciones** | Acta de asamblea, acta de junta directiva, resolución de junta |
| **Financiero-contable** | Factura emitida, factura recibida, albarán, nota de gastos, liquidación de gastos |
| **Cobros y pagos** | Remesa de recibos (XML SEPA), orden de cobro, recibo individual |
| **Contratos y convenios** | Convenio de colaboración, contrato de voluntariado, acuerdo marco |
| **Comunicaciones formales** | Carta oficial, escrito a administración, solicitud de subvención |
| **Informes y memorias** | Memoria anual de actividades, informe de campaña, memoria económica |
| **Certificados** | Certificado de pertenencia, certificado de voluntariado, certificado fiscal |
| **Formularios** | Hoja de inscripción, formulario SEPA, formulario de baja |
| **Exportaciones de datos** | Exportación XML/JSON de miembros, backup de datos |

### Modelo conceptual: `TipoDocumento`

```python
class TipoDocumento(Base):
    __tablename__ = 'tipos_documento'

    id: UUID
    nombre: str                   # "Acta de asamblea", "Factura emitida"…
    categoria: str                # acta | financiero | cobro | contrato | informe | certificado | otro
    descripcion: str | None
    formato_esperado: str | None  # pdf | xml | json | docx | cualquiera
    plantilla_id: UUID | None     # FK plantillas_documento (si existe plantilla)
    activo: bool = True
    requiere_firma: bool = False   # si el documento necesita firma digital/física
    sistema: bool = False          # generado automáticamente por el sistema (ej. remesa SEPA)
```

---

## Modelo de datos principal: `Documento`

```python
class Documento(Base):
    __tablename__ = 'documentos'

    id: UUID
    tipo_id: UUID                 # FK tipos_documento
    titulo: str                   # título descriptivo
    descripcion: str | None
    estado: str = 'borrador'      # borrador | emitido | firmado | archivado | anulado
    numero_referencia: str | None # numeración interna (ej. FACT-2025-0042)
    fecha_documento: date         # fecha del documento (no de creación en sistema)
    fecha_creacion: datetime      # automático
    creado_por_id: UUID | None    # FK usuarios

    # Archivo
    ruta_archivo: str | None      # ruta en sistema de ficheros o URL
    nombre_archivo: str | None    # nombre original del archivo
    formato: str | None           # pdf, xml, json, docx…
    tamano_bytes: int | None

    # Vínculos (polimórficos optativos)
    campania_id: UUID | None      # FK campanias
    actividad_id: UUID | None     # FK actividades
    miembro_id: UUID | None       # FK miembros
    remesa_id: UUID | None        # FK remesas
    # … añadir según necesidad

    # Metadatos extra (JSON libre para propiedades específicas por tipo)
    metadatos: dict | None        # JSONB
```

---

## Plantillas de documentos: `PlantillaDocumento`

Permite definir plantillas para documentos generables automáticamente.

```python
class PlantillaDocumento(Base):
    __tablename__ = 'plantillas_documento'

    id: UUID
    nombre: str
    tipo_id: UUID                 # FK tipos_documento
    contenido: str                # texto con {{variables}} Jinja2
    formato_salida: str           # pdf | docx | html | txt
    activo: bool = True
    variables: list[str]          # lista de variables disponibles en la plantilla
```

Ejemplos de plantillas:
- Certificado de voluntariado → variables: `{{ nombre }}`, `{{ horas }}`, `{{ campania }}`
- Acta de asamblea → variables: `{{ fecha }}`, `{{ asistentes }}`, `{{ acuerdos }}`
- Carta oficial → variables: `{{ destinatario }}`, `{{ asunto }}`, `{{ cuerpo }}`

---

## Generación automática

Documentos que el sistema puede generar automáticamente:

| Documento | Disparador | Datos fuente |
|---|---|---|
| Remesa SEPA (XML ISO 20022) | Botón en módulo económico | ordenes_cobro del período |
| Informe de campaña (PDF) | Cierre de campaña | campania + actividades + participantes |
| Memoria anual (PDF) | Botón en `/memoria-anual` | campanias + actividades del ejercicio |
| Certificado de voluntariado | Solicitud desde ficha miembro | miembro + aportaciones_horas |
| Recibo de cuota (PDF) | Cobro de cuota | cuota_anual + miembro |

---

## Permisos previstos (transacciones)

| Código | Descripción |
|---|---|
| `DOC_LIST` | Listar documentos |
| `DOC_VIEW` | Ver detalle y descargar |
| `DOC_CREATE` | Crear / subir documento |
| `DOC_EDIT` | Editar metadatos |
| `DOC_DELETE` | Eliminar / archivar documento |
| `DOC_GENERATE` | Generar documento desde plantilla |
| `TPL_MANAGE` | Gestionar plantillas de documentos |

---

## Rutas previstas

```
/documentos              → ListaDocumentos.vue
/documentos/nuevo        → NuevoDocumento.vue (subir o generar)
/documentos/:id          → DetalleDocumento.vue
/plantillas              → ListaPlantillas.vue
/plantillas/:id          → EditorPlantilla.vue
```

---

## Decisiones de diseño pendientes

- [ ] ¿Almacenamos los archivos en la BD (bytea) o solo la ruta? → Recomendación: ruta + hash, archivos en volumen Docker o S3-compatible.
- [ ] Motor de PDF: WeasyPrint (Python, HTML→PDF), ReportLab o un servicio externo.
- [ ] ¿Firma digital? → Fuera de alcance inicial; se puede añadir con campo `firmado: bool` y `firma_hash`.
- [ ] ¿Numeración automática por tipo? → Sí: `TipoDocumento.formato_numeracion` (ej. `FACT-{YYYY}-{NNNN}`).
- [ ] Vínculos polimórficos: tabla de vínculos vs columnas FK nulas → FK nulas más sencillo para empezar.

---

## Orden de implementación sugerido

1. **Modelo DB** — `TipoDocumento`, `Documento` (sin `PlantillaDocumento`)
2. **Seeding** — tipos de documento básicos (actas, facturas, informes…)
3. **GraphQL** — CRUD básico de documentos
4. **Frontend** — `ListaDocumentos.vue`, `DetalleDocumento.vue`
5. **Generación PDF** — integrar WeasyPrint; primero con Memoria Anual (ya existe la vista frontend)
6. **Plantillas** — `PlantillaDocumento` + editor Jinja2
7. **Certificados** — generación desde ficha de miembro

---

## Notas de implementación

- Seguir el patrón de módulo transversal: carpeta `backend/app/modules/documentacion/`.
- Todas las rutas llevan `CAMP_LIST` o `DOC_LIST` como permiso mínimo.
- El módulo de Memoria Anual (`/memoria-anual`) ya está construido en frontend; conectarlo
  al generador PDF cuando esté disponible añadiendo un endpoint REST `GET /api/memoria-anual/{anio}/pdf`.
- No usar la palabra "skill" en ningún lugar del módulo.
