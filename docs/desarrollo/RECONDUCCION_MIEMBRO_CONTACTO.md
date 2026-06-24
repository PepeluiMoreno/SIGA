# Reconducción `Miembro` → `Contacto` — mapa y plan

> Decisión tomada: **retirar el modelo `Miembro`**; toda la identidad viva pasa a
> `Contacto`; `miembros_legacy` queda solo como histórico. Catálogos ORM por UUID,
> sin códigos de negocio inventados.

## 0. ESTADO: refactor completado. La app arranca y migra; seeding adaptado.

- Modelo `Miembro` retirado; identidad viva = `Contacto`. App boota (mappers +
  esquema GraphQL + `main.py`), migra a `head`, `alembic check` sin error fatal.
- **Seeding/importación (pipeline canónico `app/scripts/importacion/`)** adaptado al
  modelo nuevo y validado contra el esquema migrado:
  - `1_crear_catalogos_base`: crea además los `TipoVinculacion` (SOCIO, VOLUNTARIO,
    …) con su `codigo`, que la importación necesita.
  - `4_importar_miembros`: por cada miembro legacy crea Contacto +
    Participacion(MEMBRESIA)+Membresia + Vinculacion(SOCIO)+Socio (IBAN) y, si es
    voluntario, Vinculacion(VOLUNTARIO)+Voluntario. Encripta DNI en Contacto e IBAN
    en Socio. Guarda en `temp_id_mapping` los mapeos `MIEMBRO` (→contacto) y
    `VINCULACION_SOCIO` (→vinculación de socio).
  - `6_importar_cuotas_anuales`: cuotas cuelgan de `vinculacion_socio_id`; el tipo
    sale de `membresias`, la provincia de `contactos`.
  - `7_importar_financiero_complementario`: donante = Contacto (find-or-create por
    documento); recibos/órdenes enlazan cuota vía `vinculacion_socio_id`.
  - `seeding/seed_tipos_vinculacion`: alineado al modelo nuevo (codigo + ambito +
    requiere_satelite; ya no usa `requiere_entidad`).
  - Pendiente menor: scripts de seeding demo (`seed_demo_*`, `seed_miembros`,
    `seed_mock_socios`, `bootstrap.py`, pipeline `dump/`) — secundarios, no usados
    por la importación real; reescribir si se necesitan para demos.
  - Aviso de datos: `Contacto` no tiene campo de observaciones libres; los
    comentarios/estudios legacy (COMENTARIOmiembro/OBSERVACIONES/ESTUDIOS) no tienen
    destino directo en el import.

## TODO (post-refactor, pedido por el usuario)

> Averiguar si está implementado el flujo de **envío del correo de validación de
> email** tras la **aprobación de la membresía** de un contacto por parte del
> **coordinador de su ámbito territorial** (o, en su defecto, la coordinación o
> secretaría del ámbito superior). Si no existe, diseñarlo/implementarlo.

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

## 2.4 Paso final (ÚNICO bloque pendiente — big-bang acoplado)

Todo el código de servicios está reconducido y la rama ARRANCA (imports +
mappers en verde) con `Miembro` aún presente. Lo único que queda es un bloque
acoplado que hay que hacer de una vez y validar con `build` del esquema GraphQL,
porque a medias rompe el arranque:

**Decisión tomada (alta de socio):** `crear_miembro` crea SIEMPRE
`Contacto` + `Vinculacion(SOCIO)` + `Socio` + `Participacion(MEMBRESIA)` +
`Membresia(tipo_miembro)`. Si `es_voluntario=True`, además
`Vinculacion(VOLUNTARIO)` + `Voluntario`. Input plano `MiembroCreateInput` se
reparte internamente:
- Contacto: nombre/apellidos/sexo/doc/dirección/tel/email/agrupacion_id/RGPD/activo/(tipo='PERSONA_FISICA').
- Socio: iban, swift_bic, referencia_pago, forma_pago_id, es_honor(=es_socio_honor), motivo_reduccion_id, motivo_baja_id/texto, estado_socio.
- Vinculacion(SOCIO): fecha_inicio=fecha_alta, fecha_fin=fecha_baja, estado, agrupacion_id, tipo_vinculacion_id(SOCIO).
- Membresia: tipo_miembro_id, numero_socio.
- Voluntario: disponibilidad, horas_disponibles_semana, profesion, nivel_estudios_id, experiencia/intereses/observaciones_voluntariado, puede_conducir, vehiculo_propio, disponibilidad_viajar.

**Tareas del bloque (en este orden, un commit):**
1. `graphql/types_auto.py`: crear `ContactoType` (`strawchemy.type(Contacto)`) con
   overrides nullable de sus relaciones (agrupacion, provincia, paises,
   representante_legal, nivel_estudios…); sustituir TODAS las refs
   `Optional['MiembroType']` → `Optional['ContactoType']`; borrar `MiembroType`,
   `MiembroSegmentacionType` y el import de `Miembro`/`MiembroSegmentacion`.
2. `graphql/inputs_auto.py`: revisar inputs de Miembro (si los hay).
3. `graphql/membresia_resolvers.py`: reescribir CRUD con un helper de fan-out
   (`_alta_socio`), devolver `ContactoType`, `_fetch` sobre `Contacto`; reescribir
   `_campos_perfil_faltantes`/`_publicar_perfil_incompleto`,
   `gestionar_perfil_voluntario` (→ satélite Voluntario), `actualizar_miembro`,
   `anonimizar_miembro`, `exportar_miembros_xlsx`, `voluntarios_en_ambito`
   (→ Vinculacion VOLUNTARIO), habilidades (MiembroHabilidad.miembro_id = contacto id).
4. `graphql/papelera_resolvers.py`: `restaurar_miembro` sobre `Contacto`/`ContactoType`
   (ya preparado; revertido para no romper boot).
5. `acceso/services/acceso_service.py`: `crear_usuario(miembro_id=…)` →
   `contacto_id` (Usuario ya migrado a `contacto_id`); revisar líneas 67/178/250.
6. Retirar `Miembro`: quitar reversos de catálogos
   (`TipoMiembro.miembros`, `EstadoMiembro.miembros`, `MotivoBaja.miembros`,
   `NivelEstudios.miembros`), eliminar la clase y sus relaciones en `miembro.py`,
   y limpiar `membresia/models/__init__.py` (quitar `Miembro`, `MiembroSegmentacion`),
   `app/models/__init__.py`, `modules/__init__.py`. Conservar `TipoMiembro`.
7. `python -c "import app.graphql.schema"` (o build strawberry) en verde +
   `configure_mappers()`.
8. Scripts (≈15): `seeding/*`, `importacion/*`, `dump/*`, `bootstrap.py` crean
   `Miembro`; reescribir a `Contacto`+vinculaciones. NO bloquean el arranque (no se
   importan en boot) → última subfase.

## 2.5 Progreso (estado a 2026-06-24)

**Migraciones (capa de datos): COMPLETAS y verificadas en PostgreSQL 16 real.**
p1→p2→p3→p4 crean todo el esquema nuevo, clasifican por datos reales, redirigen
FKs, enganchan satélites a Participacion, pueblan Membresía por socio y hacen el
split de actividades. (Ver `REFACTOR_CRM_ESTADO.md`.)

**Modelos: reconducidos.** Relaciones de identidad → Contacto; cuotas/recibos/
pagos/suscripciones → `vinculacion_socio_id` (Party-Role). Mappers en verde.

**Servicios reconducidos (✅):**
- `economico/cuota_service` — genera/previsualiza/recalcula por Vinculacion SOCIO
  activa; tipo vía Membresía; motivo vía Socio/TipoMiembro.
- `economico/donacion_service` — donante = Contacto (find-or-create por NIF).
- `economico/modelo_182_service`, `economico/tesoreria_service` — donante/socio
  vía Contacto / vinculacion_socio.contacto.
- `secretaria/libro_socios_service`, `economico/presupuesto_service` — cuentan por
  Vinculacion SOCIO (no por todos los contactos).

**PENDIENTE de reconducir (importan aún la clase `Miembro`):**
- Servicios: `economico/remesa_service` (SEPA: recibo→vinculacion_socio→socio.iban/
  contacto), `economico/justificante_gasto_service`, `acceso/ambito_territorial`
  (usa `Participacion.miembro_id` eliminado → vía asistencias/participacion),
  `acceso/repositories`, `core/comunicacion/destinatario_resolver`,
  `actividades/campania_service_p1` (audiencia → Contacto/Vinculacion).
- Resolvers GraphQL: `membresia_resolvers` (alta/edición debe crear Contacto+
  Vinculacion+satélites en vez de `Miembro(**kwargs)` — rewrite grande),
  `economico_mutations`, `papelera_resolvers`, `types_auto`/`inputs_auto`
  (MiembroType → ContactoType).
- **Retirar la clase `Miembro`**: quitar reversos de catálogos
  (`TipoMiembro.miembros`, `EstadoMiembro.miembros`, `MotivoBaja.miembros`,
  `NivelEstudios.miembros`), eliminar la clase y sus relaciones, y limpiar
  `membresia/models/__init__`, `app/models/__init__`, `modules/__init__`.
  ⚠️ Acoplado: estos reversos `lazy='selectin'` apuntan a la tabla renombrada y
  rompen cualquier query sobre los catálogos hasta retirarlos.
- Scripts (≈15): `app/scripts/seeding/*`, `app/scripts/importacion/*`,
  `app/scripts/dump/*`, `bootstrap.py` — crean `Miembro`; deben crear `Contacto`
  (+vinculaciones/satélites). Fase final; no bloquean el arranque (no se importan
  en boot).

## 3. Decisión fiscal pendiente (bloquea cuota_service)

La generación de cuotas anuales: ¿se calcula a partir del **`TipoMiembro`** (lo que
exige poblar `Membresia.tipo_miembro_id` para los socios existentes — la migración
hoy NO lo hace) o a partir de **`Socio.cuota_mensual`** ya por socio (importe
directo, sin pasar por tipo)? La respuesta define cómo se reescribe el servicio y
si hace falta un paso de migración que cree `Membresia` para los socios.
