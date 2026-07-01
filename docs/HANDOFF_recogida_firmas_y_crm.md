# Handoff — Recogida de firmas + alineación CRM (CiviCRM)

> **Rama**: `claude/mirage-mi-repo-siga-zcgyp1` (15 commits sobre `master`).
> **Estado**: plan completo al 100% + 4 fases extra de modelo CRM. Todo
> **commiteado y validado a sintaxis** (`py_compile`, `php -l`, `node`), pero
> **sin ejecutar** (el entorno de trabajo no tenía SQLAlchemy/Alembic/`node_modules`).
> Falta un pase de arranque real (migraciones + mappers + build front).
> **No hay PR abierto.**
>
> Documentos hermanos: `docs/REDISENO_FIRMAS_ACTIVIDAD.md` (rediseño firmas) y
> `docs/arquitectura/ACTIVIDAD_UNIDAD_ABC.md` (norte: Actividad = unidad ABC).

---

## 1. Qué hace esta rama (resumen)

1. **Recogida de firmas end-to-end**: un **plugin de WordPress** presenta el
   formulario público y lo reenvía al backend SIGA (`POST /api/publico/firmas`,
   doble opt-in, captcha, honeypot, rate-limit).
2. **Rediseño del modelo de firmas** hacia el patrón correcto: la firma es un
   **registro** (no un rol), anclado a una **Actividad** online con meta en firmas.
3. **Alineación del CRM con CiviCRM**: distinción **afiliación vs condición
   derivada**, modelo **Relationship** (contacto↔contacto), **satélite
   Contratado**, **etiquetas/Tags**, y **generalización de Grupos**.

## 2. Principio de modelo (la decisión de fondo)

- **Afiliación** = vínculo duradero con la organización, con estado → se
  **almacena** como `Vinculacion`. Solo son afiliaciones:
  **SOCIO, VOLUNTARIO, CONTRATADO (EMPLEADO), ORGANIZACION_AMIGA**.
- **Condición derivada** = "es firmante / participante / donante" = **tiene ≥1
  registro** de ese tipo (`Participacion` / `Donacion`). **No** se almacena como
  vínculo; se muestra como **badge** y se puede segmentar con **etiquetas**.
- **Relationship** = vínculo **contacto↔contacto** (representante legal, empleado
  de otra empresa, familiar…) → modelo `Relacion`, NO `Vinculacion`.
- **Acto** (`Participacion`) = evento discreto (FIRMA, DONACION, ASISTENCIA,
  MEMBRESIA, CONVENIO) con su satélite; puede otorgar/mantener una afiliación.

## 3. Cambios por área (con rutas)

### Backend — modelos nuevos / modificados
| Modelo | Ruta | Qué |
|---|---|---|
| `MetaActividad` | `backend/app/modules/actividades/models/campana.py` | meta por actividad (espejo de `MetaCampania`) |
| `FirmaCampania` | `campana.py` | **+`actividad_id`**; `campania_id`→nullable |
| `Actividad.metas` | `actividades/models/actividad.py` | relación a `MetaActividad` |
| `TipoGrupo.categoria` + `GrupoTrabajo.actividad_id` | `actividades/models/grupo.py` | grupo generalizado (territorial/orgánico/efímero) |
| `Relacion`, `TipoRelacion` | `membresia/models/relacion.py` | Relationship contacto↔contacto |
| `Contratado` | `membresia/models/vinculacion.py` | satélite de `Vinculacion(EMPLEADO)` |
| `Etiqueta`, `ContactoEtiqueta` | `membresia/models/etiqueta.py` | Tags de contacto |
| `app/core/documento.py` | — | validación NIF (DNI/NIE) reutilizable |

### Backend — migraciones (cadena, un solo head)
`vol1ext2anc3` *(ya en master)* →
`firm1act2meta3` → `grup1cat2act3` → `rel1model2civi3` → `contr1sat2rrhh3` → `tag1etiq2civi3`
(en `backend/alembic/versions/`). **Todas aditivas**; la única mutación de datos
es desactivar los tipos `FIRMANTE`/`SIMPATIZANTE` (reversible).

### Backend — servicios
- `firma_publica_service.py`: firma = `Participacion(FIRMA)`+`FirmaCampania`
  (sin vinculación); consentimiento por persona vía `Consentimiento`
  (`proteccion_datos`, cláusula `COMUNICACIONES_INFORMATIVAS`); dedup por NIF o,
  sin NIF (extranjero), por nombre+apellidos.
- `economico/services/donacion_service.py`: al registrar donación con donante,
  crea `Participacion(DONACION)` y enlaza `participacion_id`.

### Backend — GraphQL
- `types_auto.py`: `TipoRelacionType`, `RelacionType`, `ContratadoType`,
  `EtiquetaType`, `ContactoEtiquetaType`; `VinculacionType.contratado`.
- `inputs_auto.py`: inputs/filtros de `Relacion`/`TipoRelacion`/`Etiqueta`/`ContactoEtiqueta`.
- `mutations.py`: CRUD de relaciones, etiquetas y `etiquetar/desetiquetar_contacto`.
- `schema_simple.py`: queries `tiposRelacion`, `relaciones`, `etiquetas`, `contactosEtiquetas`.
- `comunicacion_resolvers.py`: `firmasVerificadasCampania(campaniaId)`.
- `membresia_resolvers.py`: `condicionesContacto(contactoId)` y batch
  `condicionesContactos(contactoIds)` (badges derivados sin N+1).

### Backend — seeds
- `seed_tipos_vinculacion.py`: fuera FIRMANTE/SIMPATIZANTE, dentro ORGANIZACION_AMIGA.
- `seed_tipos_relacion.py` (nuevo): tipos de relación (representante legal, apoderado,
  empleado de, junta, familiar, tutor). Registrado en `app/fixtures/__main__.py` y
  `seed_demo_staging.py`.

### Frontend (Vue)
- `modules/comunicaciones/views/DetalleCampania.vue`: panel "Recogida de firmas".
- `modules/membresia/views/DetalleContacto.vue`: badges derivados (ficha).
- `modules/membresia/views/ListaContactos.vue`: badges derivados (listado, batch).
- `graphql/queries/contactos.js`: `GET_CONDICIONES_CONTACTO(S)`.

### Plugin WordPress (`integrations/wordpress/siga-firmas/`, v1.4.0)
Formulario público con paleta de laicismo.org, **desplegable de actividades**
de firmas activas, **NIF opcional** (casilla "extranjero sin DNI/NIE") con
validación de letra de control en navegador y proxy PHP. Ver su `README.md`.

## 4. Cómo probar la rama (copia de la BD de master)

Las migraciones nuevas cuelgan de `vol1ext2anc3` (que **sí** está en master), así
que sobre una **copia** de la BD de master `alembic upgrade head` aplica solo el
delta aditivo, conservando datos. **No usar** `dev-up.sh resetdb` (borra el
volumen; la cadena está pensada para squash en BD vacía).

```bash
# 1) Dump de la BD de master (staging/prod)
deploy/backup_db.sh

# 2) Restaurar en la BD de DESARROLLO (copia)
gunzip -c backups/<dump>.sql.gz | \
  docker compose -f docker-compose.yml -f docker-compose.dev.yml \
    exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"

# 3) Arrancar esta rama (el backend hace 'alembic upgrade head')
git checkout claude/mirage-mi-repo-siga-zcgyp1
scripts/dev-up.sh
python -m app.fixtures            # seeds (incluye seed_tipos_relacion)

# 4) Verificar
deploy/post_deploy_check.sh
alembic downgrade vol1ext2anc3 && alembic upgrade head   # reversibilidad
```
Qué mirar: arranque sin errores de **mappers/strawchemy**, migraciones aplicadas,
GraphQL (`relaciones`, `etiquetas`, `condicionesContacto`), donación creando
`Participacion`, badges en ficha y listado, y el formulario del plugin.

## 5. Pendiente / deferido (con motivo, NO son cabos sueltos)

1. **Convenio → `Participacion`**: la contraparte del convenio no siempre es un
   `Contacto` (a veces string `entidad_contraparte`); decidir cómo materializarla
   antes de crear la `Participacion(CONVENIO)`.
2. **Backfill `Contacto.representante_legal_id` → `Relacion`**: migración de datos
   (crear relaciones `REPRESENTANTE_LEGAL` desde la columna existente; la columna
   puede quedarse por compatibilidad). Verificar en staging.
3. **Fusión territorial**: plegar `UnidadOrganizativa` bajo el `Grupo`
   generalizado repunta ~20 FKs `agrupacion_id` en 12 módulos → **fase propia**.
   La §7 ya deja el concepto unificado (`categoria` TERRITORIAL reservada).
4. **Satélite `Contratado`**: campos RRHH son un **esqueleto** (tipo_contrato,
   jornada, categoría, SS, salario…); afinar con el área de personal.
5. Estados **socio-aspirante→socio** y **voluntario-postulado→voluntario**
   (etapas de la vinculación) y **grupos inteligentes** (segmentación por consulta).

## 6. Mapa de commits (orden cronológico)

```
6b17b99 plugin WordPress de firmas
a2b0ad6 paleta laicismo.org
9b1ab06 endpoint público lista campañas
ec631d1 desplegable de campañas en el plugin
98f82af docs: spec rediseño firmas=Actividad
78024dc docs: Actividad como unidad ABC
5ce837c desplegable pasa a ACTIVIDADES (interim)
a08bf29 vista de campaña contempla firmas
96013ef (interim) firmante=vinculación FIRMANTE  ← revertido en 80dc6f2
80dc6f2 firma=registro, consentimiento persona, anclaje a actividad
ff9c6a6 grupos generalizados + NIF opcional plugin
5f56191 badges derivados (ficha)
a0f37e3 Relationship model + §5 taxonomía
f138738 Relacion GraphQL + Contratado + donación=acto + etiquetas
bf6a54a badges derivados (listado, batch) — §6 100%
```

## 7. Próximos pasos sugeridos (al retomar en VSCode)
1. Ejecutar el pase de la §4 (copia de master → upgrade → checks) y corregir lo
   que aparezca (mappers/FKs/reversibilidad).
2. Decidir el modelado de contraparte de **convenio** y cablear su `Participacion`.
3. Backfill de **representante legal** → `Relacion`.
4. Abrir el PR hacia `master` cuando el pase esté verde.
