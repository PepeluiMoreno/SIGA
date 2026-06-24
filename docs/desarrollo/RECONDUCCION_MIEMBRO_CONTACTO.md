# Reconducción `Miembro` → `Contacto` — mapa y plan

> Decisión tomada: **retirar el modelo `Miembro`**; toda la identidad viva pasa a
> `Contacto`; `miembros_legacy` queda solo como histórico. Catálogos ORM por UUID,
> sin códigos de negocio inventados.

## 1. Dónde vive ahora cada cosa (mapa de campos)

| Concepto en `Miembro` (viejo) | Nuevo hogar |
|---|---|
| Identidad (nombre, apellidos, sexo, doc, dirección, tel, email, foto, agrupacion_id, `activo`) | `Contacto` (mismas columnas; `contacto.id == miembro.id`) |
| Datos RGPD (solicita_supresion, fecha_limite_retencion, datos_anonimizados…) | `Contacto` |
| `tipo_miembro_id` | `Membresia.tipo_miembro_id` (subtipo de `Participacion`) |
| Cuota: `cuota_mensual`, `incremento_cuota`, `iban`, `swift_bic`, `referencia_pago`, `forma_pago_id`, `motivo_reduccion_id`, `motivo_baja_id`, `es_socio_honor` | `Socio` (satélite de `Vinculacion` SOCIO) |
| `estado` socio (activo/suspendido/baja) | `Socio.estado_socio` y/o `Vinculacion.estado` |
| `es_voluntario` | Existencia de `Vinculacion` tipo VOLUNTARIO (+ satélite `Voluntario`) |
| Voluntariado (disponibilidad, profesion, intereses, puede_conducir…) | `Voluntario` (satélite) |
| Habilidades/competencias/formación/documentos (`MiembroHabilidad`, `MiembroSkill`, `MiembroCompetencia`, `FormacionMiembro`, `DocumentoMiembro`) | Mismos modelos, FK `miembro_id` → ahora apunta a `contactos` (la migración ya re-apuntó la FK; el código repunta la relación a `Contacto`) |

## 2. Reconducción por fichero

### 2a. Mecánico (relación de identidad → `Contacto`; bajo riesgo)
Modelos de otros módulos cuyo `relationship('Miembro')` es una referencia a una
persona (no semántica de membresía). Repuntar a `Contacto` y `ForeignKey('miembros.id')`
→ `ForeignKey('contactos.id')`:

- `actividades/models/grupo.py` (coordinador, MiembroGrupo.miembro), `actividad.py`,
  `tarea.py`, `campana.py`
- `secretaria/models/acta.py` (presidente, secretario), `reunion.py`, `convenio.py`
- `economico/models/cuotas.py`, `recibos.py`, `cuentas_anuales.py`, `cobro/pago.py`,
  `cobro/suscripcion.py`, `justificantes_gasto.py`
- `acceso/services/ambito_territorial.py`, `repositories.py`,
  `core/comunicacion/services/destinatario_resolver.py`

### 2b. Requiere lógica nueva (NO mecánico)
- **`economico/services/cuota_service.py` (FISCAL)** — hoy genera cuotas contando
  `Miembro` por `TipoMiembro` y aplicando `tipo_miembro.motivo_reduccion_id` con
  override `Miembro.motivo_reduccion_id`. En el modelo nuevo la cuota vive en
  `Socio` (`cuota_mensual`, `motivo_reduccion_id`) y el tipo en `Membresia`. ⚠️
  **Decisión fiscal pendiente** (ver §3).
- **`graphql/membresia_resolvers.py`** — `MiembroCreateInput/UpdateInput` y
  `Miembro(**kwargs)`. Alta/edición debe crear `Contacto` + `Vinculacion` +
  satélite `Socio`/`Voluntario` (y `Membresia` si se usa `tipo_miembro`). Listado
  de voluntarios: de `Miembro.es_voluntario` → `Vinculacion` VOLUNTARIO.
- **`economico/services/{donacion,remesa,presupuesto,justificante_gasto,modelo_182}_service.py`**
  — `donaciones.miembro_id` ya es `contacto_id`; `select(Miembro)` → `select(Contacto)`.
  Modelo 182 (donantes IRPF) usa identidad → `Contacto` directo.
- **`secretaria/services/libro_socios_service.py`** — “libro de socios” → recorrer
  `Vinculacion` SOCIO + `Socio`, no `Miembro`.

### 2c. Scripts (fase final)
`app/scripts/seeding/*` y `app/scripts/importacion/*` crean `Miembro`. Con el
modelo retirado deben crear `Contacto` (+ vinculaciones/satélites). 24 ficheros.

## 3. Decisión fiscal pendiente (bloquea cuota_service)

La generación de cuotas anuales: ¿se calcula a partir del **`TipoMiembro`** (lo que
exige poblar `Membresia.tipo_miembro_id` para los socios existentes — la migración
hoy NO lo hace) o a partir de **`Socio.cuota_mensual`** ya por socio (importe
directo, sin pasar por tipo)? La respuesta define cómo se reescribe el servicio y
si hace falta un paso de migración que cree `Membresia` para los socios.
