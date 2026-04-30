# Plan de Desarrollo SIGA

Fuente única de verdad funcional: [REQUISITOS_FUNCIONALES.md](REQUISITOS_FUNCIONALES.md).

## Decisiones de partida

- **Stack backend**: Python + FastAPI + SQLAlchemy + GraphQL.
- **Stack frontend**: Vue 3, una sola SPA con todos los módulos.
- **Autenticación**: JWT.
- **Convenciones de modelo**: `Mapped[...] / mapped_column(...)`, PKs `Uuid`, herencia de `BaseModel`.
- **Granularidad por módulo**: fases gruesas — modelo de datos → API → UI → integración.
- **Entregable por módulo**: CRUD completo de sus entidades cubriendo los casos de uso del requisito.
- **Orden de módulos**: Administración → Militancia → Campañas → Contable.
- **RBAC y auditoría**: capa transversal de infraestructura (middleware/dependencias GraphQL), no responsabilidad explícita de cada resolver.
- **Entorno y despliegue**: ver [anexos/peculiraridades_entorno.md](anexos/peculiraridades_entorno.md). Resumen: staging en `vp2.europalaica.org`, expuesto en `siga.staging.europalaica.org` vía Traefik (`traefik_public`), imágenes en GHCR, CI/CD desde GitHub, sin valores hardcodeados (secrets de GitHub, docker-compose de producción generado dinámicamente en el despliegue).

## Fase 0a — Dockerización y CI/CD (antes que el código funcional)

Objetivo: poder validar UI en `siga.staging.europalaica.org` lo antes posible, con pipeline reproducible.

1. **Tres contenedores**:
   - `siga-backend`: FastAPI (uvicorn). Sin nginx delante: Traefik termina TLS y enruta.
   - `siga-frontend`: `nginx:alpine` sirviendo el bundle estático de Vue3.
   - `siga-db`: postgres, en red interna, no expuesto.
2. **Traefik labels**: `siga.staging.europalaica.org/api` → backend; `siga.staging.europalaica.org/` → frontend. Red `traefik_public` para los expuestos.
3. **GHCR + CI/CD**: workflow de GitHub Actions que construye y publica imágenes `ghcr.io/pepeluimoreno/siga-backend` y `ghcr.io/pepeluimoreno/siga-frontend` en cada push a `master`.
4. **Despliegue**: en `vp2.europalaica.org`, `docker-compose.yml` de producción generado dinámicamente desde plantilla + secrets de GitHub (DB password, JWT secret, etc.). Nada hardcodeado.
5. **Healthchecks** mínimos en cada servicio.

**Entregable Fase 0a**: `siga.staging.europalaica.org` sirviendo una página Vue3 vacía y un endpoint `/api/health` del backend, ambos desplegados desde CI/CD.

## Fase 0 — Capa transversal (cimientos)

Bloques previos al módulo 1 que sostienen todo lo demás.

1. **Autenticación JWT**: login, hash de contraseña, emisión y validación de tokens, refresh.
2. **RBAC middleware**: dependencia GraphQL que, leyendo el código de transacción asociado al resolver, comprueba que el usuario tiene permiso. Deniega en caso contrario.
3. **Audit middleware**: el mismo punto de entrada registra automáticamente quién ejecutó qué transacción, con qué resultado, sobre qué entidad.

**Entregable Fase 0**: un resolver de prueba protegido que pasa por auth → RBAC → audit, con tests.

## Módulo 1 — Administración

**Modelo**: Usuario, Rol, Transacción, UsuarioRol (con ámbito territorial), RolTransacción, LogAuditoría, configuración global.

**API**: login/logout, refresh de token, CRUD de usuarios, CRUD de roles, asignación de transacciones a roles, asignación de roles a usuarios (con ámbito), consulta de auditoría, lectura/escritura de configuración global.

**UI Vue 3**: pantallas de admin — gestión de usuarios, gestión de roles, matriz rol × transacción, visor de log de auditoría, configuración del sistema.

**Integración**: catálogo inicial de transacciones poblado en BD. (Los seeders se reescriben más adelante, no son prioritarios ahora.)

## Módulo 2 — Militancia

**Modelo**: miembro (identidad + estado), Tipomiembro, Skill y nivel por miembro, Disponibilidad (calendario), Participación (histórico), Preferencias, Consentimiento RGPD.

**API**: CRUD de miembros, gestión de skills, gestión de disponibilidad, histórico de participación, consultas de matching miembro ↔ tarea.

**UI Vue 3**: ficha de miembro, listados, calendario de disponibilidad, gestión de skills, vista de histórico.

**Integración**: vinculación miembro ↔ Usuario (módulo 1) cuando proceda; flujo de traslados territoriales.

## Módulo 3 — Campañas

**Modelo**: Campaign, Activity, Task, Assignment, dependencias entre actividades, estados (planificada / activa / bloqueada / finalizada).

**API**: CRUD jerárquico de la cadena Campaign → Activity → Task → Assignment, motor de matching automático contra Militancia, balanceo de carga, detección de conflictos, métricas (avance, desviación temporal, consumo de horas).

**UI Vue 3**: planificador de campaña, timeline, vista de asignaciones, dashboard de seguimiento.

**Integración**: consume Skills y Disponibilidad de Militancia; emite eventos al motor contable.

## Módulo 4 — Contable

**Modelo**: PlanCuentas, Ejercicio, Asiento (inmutable), DimensiónAnalítica (campaña, actividad, territorio, centro de coste), ReglaContable (evento → asiento), TipoOperación (caja vs devengo).

**API**: motor evento → regla → asiento, libro diario, balances, cierre de ejercicio, informes (básico de caja y avanzado PGC-ESFL bajo RD 1491/2011).

**UI Vue 3**: libro diario, plan de cuentas, configuración de reglas, informes, asistente de cierre.

**Integración**: consume eventos de Campañas y de tesorería existente; respeta inmutabilidad y trazabilidad.

## Lo que queda fuera de este plan (por ahora)

- Reescritura de seeders (`backend/scripts/seeding/*`, `backend/initial_data/*`).
- Decidir qué del código existente sirve. Esa evaluación se hace cuando empecemos la Fase 0, no antes.
