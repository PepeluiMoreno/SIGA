# Plan de Desarrollo SIGA

Fuente única de verdad funcional: [Requisitos Funcionales](REQUISITOS_FUNCIONALES.md).

## Decisiones de partida

- **Stack backend**: Python + FastAPI + SQLAlchemy 2.0 + GraphQL (strawchemy)
- **Stack frontend**: Vue 3, una sola SPA con todos los módulos
- **Autenticación**: JWT con RBAC
- **Convenciones de modelo**: `Mapped[...] / mapped_column(...)`, PKs UUID, herencia de `BaseModel`
- **RBAC y auditoría**: capa transversal (middleware/dependencias GraphQL)
- **Entorno**: staging en `siga.staging.europalaica.org`, Traefik, imágenes en GHCR, CI/CD desde GitHub
- **Sin valores hardcodeados**: secrets en GitHub, docker-compose generado dinámicamente

## Fase 0a — Dockerización y CI/CD

Objetivo: validar UI en staging con pipeline reproducible.

- Tres contenedores: `siga-backend`, `siga-frontend`, `siga-db`
- Traefik labels: `/api` → backend, `/` → frontend
- GitHub Actions: build + push GHCR + deploy SSH en cada push a `master`
- CI de validación en PRs: sintaxis, lint, build

**Entregable**: `siga.staging.europalaica.org` con página Vue y `/api/health` desplegados desde CI/CD.

## Fase 0 — Capa transversal

1. Autenticación JWT (login, hash, emisión, validación, refresh)
2. RBAC middleware (comprueba permiso por código de transacción)
3. Audit middleware (registra quién ejecutó qué transacción)

## Módulo 1 — Administración

**Modelo**: Usuario, Rol, Transacción, UsuarioRol, RolTransacción, LogAuditoría, Configuración

**API**: login/logout, CRUD usuarios/roles, asignación transacciones, auditoría, configuración

**UI**: gestión de usuarios, roles, matriz rol×transacción, visor de auditoría

## Módulo 2 — Militancia

**Modelo**: Miembro, TipoMiembro, Skill, Disponibilidad, Participación, ConsentimientoRGPD

**API**: CRUD miembros, skills, disponibilidad, histórico, matching miembro↔tarea

**UI**: ficha de miembro, listados, calendario, skills, histórico

## Módulo 3 — Actividad

**Modelo**: Campaña, Actividad, Tarea, Asignación, GrupoTrabajo, MiembroGrupo, Evento

**API**: CRUD jerárquico Campaña→Actividad→Tarea, matching con Militancia, métricas

**UI**: planificador, timeline, grupos de trabajo, voluntariado, eventos

## Módulo 4 — Contable

**Modelo**: PlanCuentas, Ejercicio, AsientoContable, ApunteContable, ReglaContable

**API**: motor evento→regla→asiento, libro diario, balances, cierre de ejercicio

**UI**: libro diario, plan de cuentas, reglas, informes, asistente de cierre

## Tabla de módulos y transacciones

| Módulo | Prefijos |
|---|---|
| administracion | `USR_*`, `ROL_*`, `AUD_*`, `CFG_*`, `PERM_*` |
| militancia | `SOC_*`, `MBR_*`, `AGR_*`, `TRAS_*`, `SKILL_*`, `RGPD_*` |
| actividad | `CAMP_*`, `PART_*`, `TEAM_*`, `TASK_*`, `EVT_*`, `VOL_*` |
| contable | `CUOT_*`, `REM_*`, `DON_*`, `FIN_*`, `RPT_*` |
| comunicación | `MSG_*`, `TPL_*` |
