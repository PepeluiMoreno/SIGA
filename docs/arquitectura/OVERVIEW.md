# Visión General del Sistema

SIGA es un sistema integral de gestión para organizaciones sin ánimo de lucro.
Está diseñado con una arquitectura de dominios desacoplados, API GraphQL y frontend Vue 3.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 async |
| API | Strawberry GraphQL + strawchemy |
| Frontend | Vue 3, Tailwind CSS |
| Base de datos | PostgreSQL 17 |
| Autenticación | JWT con RBAC |
| Infraestructura | Docker, Traefik, GHCR, GitHub Actions |

## Estructura de dominios

```
backend/app/domains/
├── administracion/   ← usuarios, roles, auditoría, configuración
├── militancia/       ← miembros, agrupaciones, traslados, skills
├── actividades/      ← campañas, actividades, grupos de trabajo, eventos
├── financiero/       ← tesorería, contabilidad, cuotas, donaciones, remesas
├── cobro/            ← pasarelas de pago externas
├── grupos/           ← grupos de trabajo y voluntariado
├── core/             ← estados, configuración, modelos base
└── comunicacion/     ← mensajería interna
```

## Entorno de despliegue

- **Staging**: `siga.staging.europalaica.org`
- **Proxy**: Traefik v2.11 en `vps2.europalaica.org`
- **Imágenes**: `ghcr.io/pepeluimoreno/siga-backend` y `siga-frontend`
- **CI/CD**: GitHub Actions — push a `master` dispara build + deploy automático
- **Validación**: PR hacia `master` ejecuta CI de sintaxis, lint y build antes del merge

## Principios de diseño

- PKs UUID en todos los modelos
- `Mapped` / `mapped_column` — sin `Column()` legacy
- `Decimal` para importes, nunca `float`
- Estados como FK a tablas de catálogo cuando el flujo de trabajo depende de ellos
- Enums Python cuando la lógica es fija y no parametrizable
- Sin valores hardcodeados — secrets en GitHub, variables en `.env`
- Todos los modelos heredan de `BaseModel` (auditoría incluida)
- GraphQL generado automáticamente vía strawchemy
