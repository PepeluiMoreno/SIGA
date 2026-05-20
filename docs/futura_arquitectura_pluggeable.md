Una arquitectura “pluggeable” bien diseñada no es un monolito con carpetas “plugins/”. Es un núcleo pequeño, estable y fuertemente desacoplado alrededor de contratos explícitos.

Con tu stack, el mayor riesgo es que:

SQLAlchemy acabe acoplándolo todo al modelo de datos.
Strawberry/Stawchemy conviertan el esquema GraphQL en algo rígido.
Alembic se vuelva inmantenible con migraciones cruzadas.
Vue/Vite terminen con imports directos entre módulos.

La clave es diseñar:

un core mínimo,
un sistema de capacidades,
y un runtime de composición.
1. Separar “core” de “features”

La arquitectura correcta es:

core/
plugins/
runtime/
Core

El core NO contiene negocio concreto.

Solo:

autenticación/autorización
eventos
registro de plugins
configuración
DI/container
DB/session management
lifecycle hooks
capacidades compartidas
GraphQL base
API contracts
UI shell

El core debe poder arrancar sin plugins.

Si no puede, has fallado.

2. Un plugin no es “código”

Un plugin es:

capacidad + contrato + lifecycle

Ejemplo:

“facturación”
“CRM”
“inventario”
“notificaciones”

Nunca:

“utils”
“helpers”
“services”

Eso son librerías, no plugins.

3. Cada plugin debe ser vertical

No separar por capas globales tipo:

models/
services/
graphql/

Eso destruye el desacoplamiento.

Mejor:

plugins/
  billing/
    models/
    graphql/
    services/
    migrations/
    frontend/
    permissions/
    events/

Cada plugin contiene TODO lo suyo.

Arquitectura modular vertical.

4. Contratos explícitos

El núcleo no debe conocer implementaciones.

Solo interfaces/capacidades.

Ejemplo conceptual:

NotificationProvider
StorageProvider
AuthProvider
SearchProvider

El plugin registra implementaciones.

El core consume contratos.

Nunca imports directos entre plugins.

5. Sistema de registro

Necesitas un registry central.

Conceptualmente:

PluginManifest
PluginLoader
CapabilityRegistry
HookRegistry

El manifiesto define:

nombre
versión
dependencias
migrations
rutas GraphQL
assets frontend
hooks
permisos
configuración

Piensa en algo parecido a:

VSCode extensions
Django apps
Odoo modules
Kubernetes operators
6. SQLAlchemy: el error clásico

El error:
tener un único Base.

Eso genera:

dependencias circulares
migraciones imposibles
coupling brutal

Mejor:

metadata compartida
modelos aislados por plugin

Cada plugin registra sus modelos.

El runtime compone el metadata final.

7. Alembic: probablemente la parte más difícil

El problema real de sistemas pluggeables no es GraphQL.

Son las migraciones.

Necesitas:

Opción A — Migraciones por plugin

Cada plugin:

plugins/foo/migrations/

Ventajas:

aislamiento
activación/desactivación limpia

Inconvenientes:

coordinación compleja
Opción B — Monorepo migration stream

Más simple operacionalmente.

El runtime descubre modelos y genera migraciones globales.

Más mantenible para equipos pequeños.

Recomendación real:

< 10 plugins → migraciones globales
ecosistema/extensiones externas → migraciones por plugin
8. Evitar FKs cruzadas entre plugins

Esto es crítico.

Si:

billing -> users
crm -> users
inventory -> billing

Has perdido modularidad.

Mejor:

IDs externos
eventos
read models
relaciones lógicas

Los plugins deben comunicarse por:

eventos
APIs internas
contratos

No por joins arbitrarios.

9. Arquitectura orientada a eventos

Imprescindible.

Los plugins no deben llamarse directamente.

Usa:

domain events
pub/sub interno
async signals

Ejemplo:

UserCreated
InvoicePaid
ProductReserved

Entonces:

CRM escucha
Analytics escucha
Notifications escucha

Sin coupling.

10. Strawberry GraphQL

GraphQL modular encaja muy bien con plugins.

Cada plugin aporta:

types
queries
mutations
subscriptions

El runtime compone el schema final.

La clave:
el core no conoce los schemas concretos.

11. Strawchemy

Aquí debes tener cuidado.

La autogeneración excesiva:

acelera al inicio
destruye diseño a escala

Úsalo:

CRUD internos
admin tooling
backoffice

No para:

dominio complejo
workflows
reglas críticas

La API pública debe diseñarse manualmente.

12. Backend runtime

Necesitas lifecycle hooks.

Ejemplo conceptual:

on_install
on_enable
on_disable
on_startup
on_shutdown

Y capacidades:

registrar rutas
registrar eventos
registrar permisos
registrar jobs
registrar cron tasks
registrar menú frontend
13. Frontend pluggeable (Vue/Vite)

Aquí suele hacerse muy mal.

La solución NO es:
“importar componentes dinámicamente”.

Necesitas un:

Frontend Shell

El shell provee:

layout
router
auth
stores
theme
navegación
slots/extensiones

Los plugins registran:

rutas
vistas
widgets
menús
panels
acciones

Como:

VSCode
Grafana
Home Assistant
Kibana
14. Microfrontends: normalmente NO

No uses microfrontends salvo:

equipos enormes
despliegues independientes reales
organizaciones complejas

En la mayoría de casos:

complican build
rompen DX
duplican dependencias
degradan rendimiento

Mejor:

monorepo modular
carga dinámica
chunks por plugin
15. Vite encaja muy bien

Porque permite:

code splitting
dynamic imports
lazy loading
plugin manifests

La UI puede descubrir módulos en runtime.

16. Permisos desacoplados

No hardcodear permisos.

Cada plugin registra:

scopes
roles
capabilities

Ejemplo:

billing.invoice.read
billing.invoice.write
crm.contact.delete
17. Configuración multi-tenant

Si el sistema crecerá:
haz esto desde el principio.

Porque luego es casi imposible.

Separar:

configuración global
configuración plugin
configuración tenant
18. Observabilidad desde el núcleo

Cada plugin debe heredar:

logging estructurado
tracing
métricas
audit trail

Centralizados.

19. El mayor error arquitectónico

Intentar que los plugins puedan hacer “de todo”.

Eso mata estabilidad.

Debes limitar:

superficies públicas
hooks
capacidades

Un buen sistema pluggeable es:

restrictivo
opinionado
estable

No “flexible”.

20. Arquitectura recomendada para tu stack
Backend
FastAPI
  + Strawberry
  + SQLAlchemy 2
  + Alembic
  + Plugin Runtime
  + Event Bus
Plugins

Cada plugin:

manifest
models
graphql
services
events
permissions
migrations
tasks
frontend
Frontend
Vue 3
Pinia
Vue Router
Plugin Shell
Dynamic Route Registry
Dynamic Menus
21. Patrón arquitectónico ideal

La combinación más robusta aquí suele ser:

Modular Monolith + Event Driven

NO microservicios al inicio.

Porque:

SQLAlchemy
GraphQL
Alembic
permisos
transacciones

se vuelven muchísimo más complejos distribuidos.

Un modular monolith bien hecho puede durar años.

22. Filosofía correcta

El objetivo NO es:
“poder instalar plugins”.

El objetivo es:

que el núcleo sobreviva al crecimiento del dominio

Eso cambia completamente las decisiones de diseño.

https://github.com/PepeluiMoreno/SIGA  como lo convertirias a pluggeable?

No puedo inspeccionar correctamente el repositorio porque el buscador web no ha devuelto el contenido del proyecto, solo resultados genéricos de GitHub. Necesitaría al menos:

estructura de carpetas,
stack exacto,
organización de modelos/API/frontend,
y cómo están acoplados los módulos hoy.

El enlace del repo es:
SIGA en GitHub

Aun así, viendo el stack que mencionaste antes, te diría que la migración a arquitectura pluggeable probablemente debería hacerse en 4 fases, no de golpe.

Lo primero: NO empezar por plugins

Error típico:
“voy a crear un loader dinámico”.

No.

Primero debes:

modularizar el monolito

Si el monolito no está modularizado:

los plugins solo serán imports dinámicos del caos existente.
Lo que probablemente haría con SIGA
Fase 1 — Descubrir bounded contexts

Buscaría:

qué partes del sistema pueden vivir aisladas

Normalmente aparecen módulos como:

auth
usuarios
expedientes
documentos
workflow
notificaciones
auditoría
permisos
reporting
inventario
facturación

Y entonces:

convertiría cada dominio en un módulo vertical
La estructura objetivo

Probablemente algo así:

backend/
  core/
  runtime/
  plugins/

frontend/
  shell/
  plugins/
Backend
Core

Muy pequeño.

core/
  db/
  auth/
  events/
  permissions/
  config/
  graphql/
  plugin_api/
  observability/

Nada de negocio.

Runtime

Esto es lo importante.

runtime/
  loader/
  registry/
  schema/
  lifecycle/

Responsabilidades:

descubrir plugins
resolver dependencias
montar schemas GraphQL
registrar eventos
registrar modelos
cargar frontend manifests
Plugins

Cada módulo aislado:

plugins/
  expedientes/
  documentos/
  auditoria/

Y dentro:

plugin.py
manifest.py
models/
graphql/
services/
events/
permissions/
migrations/
frontend/
Lo más importante:
eliminar imports laterales

Esto suele ser el cáncer del monolito.

Ejemplo malo:

expedientes -> usuarios
usuarios -> auditoria
auditoria -> documentos

Eso impide pluginización.

La dependencia correcta debe ser:

plugins -> core

Nunca:

plugin -> plugin
Comunicación entre plugins

Solo:

eventos
contratos
interfaces registradas

Nunca:

imports directos
acceso arbitrario a modelos SQLAlchemy
joins cruzados
SQLAlchemy

Aquí seguramente tengas uno de los mayores problemas.

Probablemente ahora tengas:

un único Base
modelos globales
relaciones cruzadas

Yo haría:

Paso 1

Separar metadata por plugin.

Paso 2

Eliminar relaciones ORM cruzadas.

Paso 3

Cambiar:

relationship()

por:

foreign ids + services

cuando atraviesen dominios.

GraphQL

Con Strawberry esto encaja muy bien.

Cada plugin:

expone sus types
queries
mutations
subscriptions

El runtime:

compone el schema final
Pero cuidado con Strawchemy

No dejaría que:

modelo SQLAlchemy == API pública

Porque:

mata encapsulación
acopla frontend a DB
rompe versionado

Strawchemy:
sí para CRUD interno.

No para lógica de negocio importante.

Frontend

Aquí suele haber muchísimo acoplamiento oculto.

Lo correcto sería:

convertir Vue en un shell
El shell frontend

Debe contener:

auth
router base
layout
navegación
permisos
stores globales
theme
i18n

Y nada más.

Cada plugin frontend
plugins/
  expedientes/
    routes/
    views/
    stores/
    widgets/
    menus/
El router debe ser dinámico

Cada plugin registra:

routes
menus
dashboard widgets
actions
permissions
Muy importante:
NO microfrontends

Para SIGA probablemente sería un desastre.

Mejor:

monorepo
chunks dinámicos
lazy loading
manifests
Permisos

Cada plugin define:

expedientes.read
expedientes.write
expedientes.delete

El core:

registra
resuelve
aplica
Eventos

Aquí está la verdadera desacoplación.

Ejemplo:

ExpedienteCreado
DocumentoFirmado
UsuarioBloqueado

Plugins escuchan eventos.

No se llaman directamente.

Alembic

Yo NO haría inicialmente:

migrations por plugin

Complica muchísimo.

Haría:

stream global de migraciones

Hasta que:

haya terceros desarrollando plugins
o despliegues independientes
El cambio más importante

Pasar de:

aplicación con módulos

a:

runtime que compone capacidades

Eso es el salto conceptual real.

Cómo lo haría técnicamente
Etapa 1

Modularizar carpetas.

Etapa 2

Eliminar imports cruzados.

Etapa 3

Introducir event bus.

Etapa 4

Introducir plugin manifests.

Etapa 5

Carga dinámica de schemas/routes/frontend.

Etapa 6

Permitir enable/disable plugins.

Lo que NO intentaría al principio
hot reload de plugins
plugins externos arbitrarios
marketplace
aislamiento tipo microkernel
sandboxing
multi-version plugin support

Eso viene muchísimo después.

Arquitectura final que probablemente buscaría
Backend
Modular Monolith
+ Event Driven
+ Plugin Runtime
Frontend
Shell SPA
+ Dynamic Modules
+ Capability Registry
Y el punto crítico real

Si SIGA ya tiene:

imports circulares,
modelos compartidos,
lógica mezclada en resolvers,
stores globales enormes,
permisos hardcodeados,

entonces el trabajo no es “añadir plugins”.

Es:

rediseñar fronteras del dominio

Y eso suele ser el 80% del esfuerzo.