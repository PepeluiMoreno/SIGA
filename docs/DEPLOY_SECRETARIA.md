# Instrucciones de despliegue — Secretaría + Presidencia

**Rama:** `feature/modulo-secretaria`  
**Merge destino:** `master`  
**Commits:** 10  
**Última actualización:** 2026-05-20

---

## 1. Merge a master

```bash
git checkout master
git pull origin master
git merge --no-ff feature/modulo-secretaria
git push origin master
```

---

## 2. Migraciones de base de datos

Dos migraciones encadenadas. Un solo comando las aplica ambas:

```bash
cd backend
alembic upgrade head
```

### Migración 1 — `k6l7m8n9o0p1` — Estructura del módulo

**Encadena sobre:** `j5k6l7m8n9o0`

Crea 12 tablas nuevas con prefijo `sec_`:

| Tabla | Descripción |
|---|---|
| `sec_tipos_reunion` | Catálogo de tipos (Asamblea, Junta, Comisión…) |
| `sec_reuniones` | Reuniones convocadas y celebradas |
| `sec_asistentes_reunion` | Registro de asistencia por reunión |
| `sec_puntos_orden_dia` | Puntos del orden del día |
| `sec_acuerdos` | Acuerdos adoptados con resultado de votación |
| `sec_votaciones_acuerdo` | Detalle de votos por acuerdo |
| `sec_actas` | Libro de actas (numeración correlativa por tipo y año) |
| `sec_certificados_acuerdo` | Certificados emitidos a terceros (`CERT-AAAA-NNN`) |
| `sec_libro_socios_snapshots` | Historial de generaciones del Libro de Socios |
| `sec_tipos_convenio` | Catálogo de tipos de convenio |
| `sec_convenios` | Convenios firmados con terceros (`CONV-AAAA-NNN`) |
| `sec_delegaciones_firma` | Poderes y delegaciones de representación |

### Migración 2 — `l7m8n9o0p1q2` — Estados al catálogo

**Encadena sobre:** `k6l7m8n9o0p1`

Crea 3 tablas de estado en el sistema de configuración:

| Tabla | Máquina de estados |
|---|---|
| `estados_reunion` | CONVOCADA → CELEBRADA → ACTA_BORRADOR → ACTA_APROBADA \| CANCELADA |
| `estados_acta` | BORRADOR → APROBADA → FIRMADA |
| `estados_ejecucion_acuerdo` | PENDIENTE → EN_CURSO → COMPLETADO \| ARCHIVADO |

Modifica 3 tablas existentes (añade FK + código denormalizado, elimina columna string):

| Tabla | Añade | Elimina |
|---|---|---|
| `sec_reuniones` | `estado_id`, `estado_codigo` | `estado` |
| `sec_actas` | `estado_id`, `estado_codigo` | `estado` |
| `sec_acuerdos` | `estado_ejecucion_id`, `estado_ejecucion_codigo` | `estado_ejecucion` |

> **Diseño dual FK + código:** cada entidad guarda el UUID del estado (para `EstadoBadge` dinámico y JOINs) y el código de máquina (para lógica de negocio sin JOIN). Consistente con el resto del sistema.

### Rollback si fuera necesario

```bash
alembic downgrade k6l7m8n9o0p1   # deshace solo la migración 2
alembic downgrade j5k6l7m8n9o0   # deshace ambas
```

---

## 3. Seeds de datos iniciales

Idempotentes: ejecutar múltiples veces no duplica registros.

Se activan automáticamente en el arranque vía `inicializar_sistema.py`. Si el sistema ya está corriendo:

```bash
cd backend
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.scripts.inicializar_estados import inicializar_estados
from app.scripts.seeding.seed_secretaria import seed_secretaria

async def run():
    async with AsyncSessionLocal() as session:
        await inicializar_estados(session)
        await seed_secretaria(session)

asyncio.run(run())
"
```

### Datos insertados

**`inicializar_estados`** — 12 registros nuevos en 3 tablas:

| Tabla | Registros |
|---|---|
| `estados_reunion` | Convocada, Celebrada, Acta borrador, Acta aprobada, Cancelada |
| `estados_acta` | Borrador, Aprobada, Firmada |
| `estados_ejecucion_acuerdo` | Pendiente, En curso, Completado, Archivado |

**`seed_secretaria`** — 9 registros nuevos en 2 tablas:

| Tabla | Registros |
|---|---|
| `sec_tipos_reunion` | Asamblea General Ordinaria, Asamblea General Extraordinaria, Junta Directiva, Comisión de Trabajo |
| `sec_tipos_convenio` | Convenio de colaboración, Acuerdo de patrocinio, Adhesión a red, Contrato de servicios, Protocolo de actuación |

---

## 4. Rutas frontend

### Módulo Presidencia

| Ruta | Vista | Acceso |
|---|---|---|
| `/presidencia` | Cuadro de mando ejecutivo | Cualquier usuario autenticado |
| `/presidencia/acuerdos` | Seguimiento de acuerdos (vista ejecutiva) | Cualquier usuario autenticado |
| `/presidencia/mandatos` | Mandatos y cargos vigentes | Cualquier usuario autenticado |

La sección **Presidencia** aparece en el sidebar antes de Secretaría, visible para todos los usuarios autenticados. El cuadro de mando solo muestra datos a los que el usuario tiene acceso según sus permisos en los módulos de origen.

### Módulo Secretaría

| Ruta | Vista | Permiso requerido |
|---|---|---|
| `/secretaria/reuniones` | Convocatoria y gestión de reuniones | `SEC_REUNION_LISTAR` |
| `/secretaria/acuerdos` | Seguimiento de acuerdos | `SEC_ACUERDO_LISTAR` |
| `/secretaria/actas` | Libro de actas | `SEC_ACTA_LISTAR` |
| `/secretaria/libro-socios` | Libro de Socios (Ley 1/2002) | `SEC_LIBRO_SOCIOS_CONSULTAR` |
| `/secretaria/convenios` | Convenios y delegaciones de firma | `SEC_CONVENIO_LISTAR` |

La sección **Secretaría** aparece entre Presidencia y Ayuda. Se oculta si el usuario no tiene ningún permiso `SEC_*`.

---

## 5. Permisos a asignar en roles

22 transacciones nuevas, solo en secretaría. Asignar en **Administración → Roles → [rol] → Permisos**:

| Funcionalidad | Rol sugerido |
|---|---|
| `GESTION_REUNIONES` — convocar, celebrar, registrar asistencia, cancelar, acuerdos y seguimiento | Secretario/a |
| `GESTION_ACTAS` — redactar, aprobar, firmar, exportar | Secretario/a |
| `CERTIFICADOS_ACUERDOS` — emitir y listar | Secretario/a |
| `LIBRO_SOCIOS` — generar y consultar | Secretario/a, Presidente/a |
| `CONVENIOS_INSTITUCIONALES` — convenios y delegaciones | Presidente/a, Junta Directiva |

Presidencia no tiene permisos propios: agrega datos de secretaría y membresía con los permisos ya existentes.

---

## 6. API GraphQL nueva

### Secretaría — Queries

| Query | Parámetros |
|---|---|
| `tiposReunion` | — |
| `reuniones` | `anio`, `tipoReunionId`, `estadoCodigo` |
| `acuerdosPendientes` | `agrupacionId` |
| `actas` | `anio`, `estadoCodigo` |
| `actasPendientesAprobacion` | — |
| `certificadosAcuerdo` | `actaId`, `anio` |
| `libroSociosSnapshots` | — |
| `convenios` | `estado`, `proximosAVencerDias` |
| `delegacionesFirma` | `activasSolo` |

### Secretaría — Mutations

| Mutation | Descripción |
|---|---|
| `convocarReunion(data)` | Crea convocatoria con numeración automática |
| `registrarCelebracionReunion(data)` | Registra datos y calcula quórum |
| `cancelarReunion(reunionId, motivo)` | Cancela una reunión convocada |
| `registrarAcuerdo(data)` | Crea acuerdo + votación en una transacción |
| `actualizarSeguimientoAcuerdo(data)` | Actualiza estado de ejecución |
| `crearActaBorrador(data)` | Numeración correlativa por tipo y año |
| `aprobarActa(actaId, fechaAprobacion)` | Aprueba el borrador |
| `firmarActa(actaId, secretarioId, presidenteId)` | Registra la firma |
| `emitirCertificadoAcuerdo(data)` | Referencia automática `CERT-AAAA-NNN` |
| `generarLibroSocios(fechaCorte, motivo)` | Snapshot del censo con hash de integridad |
| `registrarConvenio(data)` | Referencia automática `CONV-AAAA-NNN` |
| `cambiarEstadoConvenio(convenioId, nuevoEstado)` | Cambia estado del convenio |
| `crearDelegacionFirma(data)` | Nueva delegación de representación |
| `revocarDelegacionFirma(delegacionId)` | Revoca una delegación activa |

---

## 7. Componente nuevo reutilizable

**`SelectorMiembro.vue`** — selector con búsqueda filtrada en local, disponible en `src/components/common/`. Acepta props `modelValue` (UUID), `miembros` (array), `placeholder` y `disabled`. Emite `update:modelValue` y `select`. Se puede usar en cualquier formulario del proyecto que necesite elegir un miembro.

---

## 8. Archivos de la rama

### Backend — nuevos (17 archivos)

```
app/modules/secretaria/__init__.py
app/modules/secretaria/catalog.py
app/modules/secretaria/models/__init__.py
app/modules/secretaria/models/reunion.py
app/modules/secretaria/models/acta.py
app/modules/secretaria/models/libro_socios.py
app/modules/secretaria/models/convenio.py
app/modules/secretaria/services/__init__.py
app/modules/secretaria/services/reunion_service.py
app/modules/secretaria/services/acta_service.py
app/modules/secretaria/services/libro_socios_service.py
app/modules/secretaria/services/convenio_service.py
app/graphql/secretaria_resolvers.py
app/scripts/seeding/seed_secretaria.py
alembic/versions/k6l7m8n9o0p1_modulo_secretaria.py
alembic/versions/l7m8n9o0p1q2_estados_secretaria.py
```

### Backend — modificados (6 archivos)

```
app/modules/configuracion/models/estados.py     + EstadoReunion, EstadoActa, EstadoEjecucionAcuerdo
app/modules/configuracion/models/__init__.py    registro de los 3 nuevos modelos
app/modules/__init__.py                         registro de todos los modelos de secretaría
app/graphql/schema_simple.py                    + SecretariaQuery en Query
app/graphql/mutations.py                        + SecretariaResolverMutation en Mutation
app/scripts/inicializar_estados.py              + seeds de los 3 estados de secretaría
app/scripts/inicializar_sistema.py              + llamada a seed_secretaria
```

### Frontend — nuevos (11 archivos)

```
src/components/common/SelectorMiembro.vue
src/graphql/queries/secretaria.js
src/graphql/queries/presidencia.js
src/modules/secretaria/views/Reuniones.vue
src/modules/secretaria/views/Acuerdos.vue
src/modules/secretaria/views/Actas.vue
src/modules/secretaria/views/LibroSocios.vue
src/modules/secretaria/views/Convenios.vue
src/modules/presidencia/views/Dashboard.vue
src/modules/presidencia/views/Mandatos.vue
src/modules/presidencia/views/SeguimientoAcuerdos.vue
```

### Frontend — modificados (3 archivos)

```
src/router/index.js           8 rutas nuevas (/presidencia/*, /secretaria/*)
src/components/common/AppLayout.vue   secciones Presidencia y Secretaría en sidebar
src/views/Ayuda.vue           bloques de documentación de ambos módulos
```

---

## 9. Deuda técnica conocida

| Item | Impacto | Módulo |
|---|---|---|
| `cargarAcuerdosActa()` en Actas.vue es un stub vacío — el selector de acuerdo en el certificado no lista acuerdos hasta que exista una query directa por `actaId` | Menor — se puede emitir certificado igualmente escribiendo el texto manualmente | Secretaría |
| `LibroSociosService.generar_snapshot()` cuenta miembros sin filtrar por estado activo — pendiente de conectar con la lógica de estados de membresía | Menor — los conteos son aproximados hasta que se conecte | Secretaría |
| Exportación a PDF — `ruta_pdf` existe en modelo pero la generación no está implementada | Sin impacto funcional — los documentos se gestionan fuera del sistema por ahora | Secretaría |
| El módulo de presidencia no tiene permisos propios — visible para cualquier autenticado | Aceptable para esta versión — se puede granular en sprint posterior | Presidencia |
