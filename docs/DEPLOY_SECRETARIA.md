# Instrucciones de despliegue — Módulo de Secretaría

**Rama:** `feature/modulo-secretaria`  
**Merge destino:** `master`  
**Commits de la rama:** 6 + 1 de estados (trabajo en curso)

---

## 1. Merge a master

```bash
git checkout master
git merge --no-ff feature/modulo-secretaria
git push origin master
```

---

## 2. Migraciones de base de datos

Hay **dos migraciones** que deben aplicarse en orden. Son consecutivas y encadenadas, por lo que `alembic upgrade head` las aplica ambas de una vez.

```bash
cd backend
alembic upgrade head
```

### Migración 1 — `k6l7m8n9o0p1` — Estructura del módulo

**Encadena sobre:** `j5k6l7m8n9o0` (última migración preexistente)

Crea **12 tablas nuevas** con prefijo `sec_`:

| Tabla | Descripción |
|---|---|
| `sec_tipos_reunion` | Catálogo de tipos (Asamblea, Junta, Comisión…) |
| `sec_reuniones` | Reuniones convocadas y celebradas |
| `sec_asistentes_reunion` | Registro de asistencia por reunión |
| `sec_puntos_orden_dia` | Puntos del orden del día |
| `sec_acuerdos` | Acuerdos adoptados con resultado de votación |
| `sec_votaciones_acuerdo` | Detalle de votos por acuerdo |
| `sec_actas` | Libro de actas (numeración correlativa) |
| `sec_certificados_acuerdo` | Certificados emitidos a terceros |
| `sec_libro_socios_snapshots` | Historial de generaciones del Libro de Socios |
| `sec_tipos_convenio` | Catálogo de tipos de convenio |
| `sec_convenios` | Convenios firmados con terceros |
| `sec_delegaciones_firma` | Poderes y delegaciones de representación |

### Migración 2 — `l7m8n9o0p1q2` — Estados al catálogo

**Encadena sobre:** `k6l7m8n9o0p1`

Crea **3 tablas de estado** en el sistema de configuración:

| Tabla | Estados |
|---|---|
| `estados_reunion` | CONVOCADA → CELEBRADA → ACTA_BORRADOR → ACTA_APROBADA / CANCELADA |
| `estados_acta` | BORRADOR → APROBADA → FIRMADA |
| `estados_ejecucion_acuerdo` | PENDIENTE → EN_CURSO → COMPLETADO / ARCHIVADO |

Y modifica **3 tablas existentes** para añadir FK + código denormalizado:

| Tabla | Columnas añadidas | Columnas eliminadas |
|---|---|---|
| `sec_reuniones` | `estado_id`, `estado_codigo` | `estado` |
| `sec_actas` | `estado_id`, `estado_codigo` | `estado` |
| `sec_acuerdos` | `estado_ejecucion_id`, `estado_ejecucion_codigo` | `estado_ejecucion` |

> **Nota sobre el diseño dual (FK + código):** Cada entidad guarda tanto el UUID de estado (para consultas con JOIN y `EstadoBadge` dinámico) como el código de máquina (para lógica de negocio sin JOIN). Esto es consistente con el patrón del resto del sistema.

### Rollback (si fuera necesario)

```bash
alembic downgrade k6l7m8n9o0p1   # deshace solo la migración 2
alembic downgrade j5k6l7m8n9o0   # deshace ambas migraciones
```

---

## 3. Seeds de datos iniciales

El seeding es **idempotente**: se puede ejecutar múltiples veces sin duplicar registros.

Se activa automáticamente en el arranque del sistema a través de `inicializar_sistema.py`. Si el sistema ya está arriba, ejecutar manualmente:

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

### Datos que se insertan

**`inicializar_estados`** (nuevo en esta rama):
- 5 estados de reunión con colores hex
- 3 estados de acta
- 4 estados de ejecución de acuerdo

**`seed_secretaria`**:
- 4 tipos de reunión: Asamblea General Ordinaria, Asamblea General Extraordinaria, Junta Directiva, Comisión de Trabajo
- 5 tipos de convenio: Colaboración, Patrocinio, Adhesión a red, Contrato de servicios, Protocolo de actuación

---

## 4. Rutas frontend disponibles

| Ruta | Vista | Permiso requerido |
|---|---|---|
| `/secretaria/reuniones` | Convocatoria y gestión de reuniones | `SEC_REUNION_LISTAR` |
| `/secretaria/acuerdos` | Seguimiento de acuerdos | `SEC_ACUERDO_LISTAR` |
| `/secretaria/actas` | Libro de actas | `SEC_ACTA_LISTAR` |
| `/secretaria/libro-socios` | Libro de Socios (Ley 1/2002) | `SEC_LIBRO_SOCIOS_CONSULTAR` |
| `/secretaria/convenios` | Convenios y delegaciones de firma | `SEC_CONVENIO_LISTAR` |

La sección **Secretaría** aparece en el sidebar entre Económico y Ayuda. Se oculta automáticamente si el usuario no tiene ninguno de los permisos `SEC_*`.

---

## 5. Permisos a asignar en roles

22 transacciones nuevas agrupadas en 5 funcionalidades. Asignar según rol:

| Funcionalidad | Transacciones | Rol sugerido |
|---|---|---|
| `GESTION_REUNIONES` | Listar, convocar, editar, registrar asistencia, cancelar reuniones + listar, crear, editar y hacer seguimiento de acuerdos | Secretario/a |
| `GESTION_ACTAS` | Listar, redactar, aprobar, firmar y exportar actas | Secretario/a |
| `CERTIFICADOS_ACUERDOS` | Emitir y listar certificados | Secretario/a |
| `LIBRO_SOCIOS` | Generar y consultar el Libro de Socios | Secretario/a, Presidente/a |
| `CONVENIOS_INSTITUCIONALES` | Gestionar convenios y delegaciones de firma | Presidente/a, Junta Directiva |

Para asignar desde la interfaz: **Administración → Roles → [rol] → Permisos**.

---

## 6. Queries y mutations GraphQL nuevas

### Queries
- `tiposReunion` — catálogo de tipos
- `reuniones(anio, tipoReunionId, estado)` — lista filtrada
- `acuerdosPendientes(agrupacionId)` — acuerdos sin completar
- `actas(anio, estado)` — libro de actas
- `actasPendientesAprobacion` — borradores pendientes
- `certificadosAcuerdo(actaId, anio)` — certificados emitidos
- `libroSociosSnapshots` — historial de generaciones
- `convenios(estado, proximosAVencerDias)` — convenios con filtro de vencimiento
- `delegacionesFirma(activasSolo)` — delegaciones de representación

### Mutations
- `convocarReunion(data)` — crea convocatoria con numeración automática
- `registrarCelebracionReunion(data)` — registra datos + calcula quórum
- `cancelarReunion(reunionId, motivo)`
- `registrarAcuerdo(data)` — crea acuerdo + votación en una transacción
- `actualizarSeguimientoAcuerdo(data)`
- `crearActaBorrador(data)` — numeración correlativa por tipo y año
- `aprobarActa(actaId, fechaAprobacion)`
- `firmarActa(actaId, secretarioId, presidenteId)`
- `emitirCertificadoAcuerdo(data)` — referencia automática `CERT-AAAA-NNN`
- `generarLibroSocios(fechaCorte, motivo)`
- `registrarConvenio(data)` — referencia automática `CONV-AAAA-NNN`
- `cambiarEstadoConvenio(convenioId, nuevoEstado)`
- `crearDelegacionFirma(data)`
- `revocarDelegacionFirma(delegacionId)`

---

## 7. Archivos modificados en esta rama

### Backend — nuevos
| Archivo | Descripción |
|---|---|
| `app/modules/secretaria/__init__.py` | Módulo |
| `app/modules/secretaria/catalog.py` | 22 transacciones, 5 funcionalidades |
| `app/modules/secretaria/models/reunion.py` | TipoReunion, Reunion, AsistenteReunion, PuntoOrdenDia, Acuerdo, VotacionAcuerdo |
| `app/modules/secretaria/models/acta.py` | Acta, CertificadoAcuerdo |
| `app/modules/secretaria/models/libro_socios.py` | LibroSociosSnapshot |
| `app/modules/secretaria/models/convenio.py` | TipoConvenio, Convenio, DelegacionFirma |
| `app/modules/secretaria/services/reunion_service.py` | ReunionService |
| `app/modules/secretaria/services/acta_service.py` | ActaService |
| `app/modules/secretaria/services/libro_socios_service.py` | LibroSociosService |
| `app/modules/secretaria/services/convenio_service.py` | ConvenioService |
| `app/graphql/secretaria_resolvers.py` | SecretariaQuery + SecretariaResolverMutation |
| `app/scripts/seeding/seed_secretaria.py` | Seed idempotente |
| `alembic/versions/k6l7m8n9o0p1_modulo_secretaria.py` | Migración 1 |
| `alembic/versions/l7m8n9o0p1q2_estados_secretaria.py` | Migración 2 |

### Backend — modificados
| Archivo | Cambio |
|---|---|
| `app/modules/configuracion/models/estados.py` | + EstadoReunion, EstadoActa, EstadoEjecucionAcuerdo |
| `app/modules/configuracion/models/__init__.py` | Registro de los 3 nuevos modelos |
| `app/modules/__init__.py` | Registro de todos los modelos de secretaría |
| `app/graphql/schema_simple.py` | + SecretariaQuery en Query |
| `app/graphql/mutations.py` | + SecretariaResolverMutation en Mutation |
| `app/scripts/inicializar_estados.py` | + seeds de los 3 estados de secretaría |
| `app/scripts/inicializar_sistema.py` | + llamada a seed_secretaria |

### Frontend — nuevos
| Archivo | Descripción |
|---|---|
| `src/modules/secretaria/views/Reuniones.vue` | Vista funcional completa |
| `src/modules/secretaria/views/Acuerdos.vue` | Vista funcional completa |
| `src/modules/secretaria/views/Actas.vue` | Vista funcional completa |
| `src/modules/secretaria/views/LibroSocios.vue` | Vista funcional completa |
| `src/modules/secretaria/views/Convenios.vue` | Vista funcional completa |
| `src/graphql/queries/secretaria.js` | Todas las queries y mutations |

### Frontend — modificados
| Archivo | Cambio |
|---|---|
| `src/router/index.js` | 5 rutas nuevas bajo `/secretaria/*` |
| `src/components/common/AppLayout.vue` | Sección Secretaría en sidebar |

---

## 8. Deuda técnica conocida (no bloquea el deploy)

- **Selector de firmantes en actas:** el modal de firma usa los IDs ya almacenados en el acta como placeholder. En producción habría que añadir un selector de miembro para secretario y presidente cuando no están preestablecidos.
- **Selector de acuerdo en certificados:** el modal de emitir certificado usa el ID del acta como placeholder para `acuerdo_id`. Pendiente añadir un selector que liste los acuerdos de esa acta.
- **Exportación a PDF:** `LibroSociosSnapshot.ruta_pdf`, `Acta.ruta_pdf` y `CertificadoAcuerdo.ruta_pdf` están en el modelo pero la generación de PDF no está implementada.
- **Conteo de socios activos en LibroSociosService:** el query de `generar_snapshot` cuenta todos los miembros no eliminados sin filtrar por estado activo (pendiente de conectar con la lógica de estados de membresía).
