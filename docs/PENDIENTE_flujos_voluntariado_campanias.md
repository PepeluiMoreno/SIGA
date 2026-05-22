# Trabajo pendiente — flujos de voluntariado y campañas

> Documento de anotación. Recoge flujos y funcionalidades **no implementados**
> detectados durante las sesiones de refactor de UI. NO son cambios de interfaz:
> requieren modelo de datos, resolvers y/o lógica de negocio nuevos. Abordar en
> sesiones dedicadas, no en las de UI.

## 1. Coordinadores de campaña: ver disponibilidad y habilidades de voluntarios

**Contexto.** En la ficha de miembro (`MiembroDetail.vue`, sección "Membresía y
participación") un voluntario registra: perfil (profesión, intereses, experiencia,
conducir/vehículo/viajar), habilidades (catálogo con nivel) y disponibilidad
(franjas horarias por día de la semana + horas/semana).

**Lo que falta.** Un coordinador de campaña, al formar los grupos de trabajo de una
actividad, necesita **consultar esa disponibilidad y esas habilidades de forma
agregada** para decidir a quién asignar. Hoy esos datos solo se ven entrando ficha
a ficha, y solo por quien tiene permiso sobre el miembro.

**Implica (no-UI):**
- Vista/consulta nueva: "buscar voluntarios por habilidad + disponibilidad +
  ámbito organizativo", probablemente con cruce de franjas horarias contra el
  horario de la actividad.
- Resolver/servicio que exponga disponibilidad y habilidades de los voluntarios de
  un ámbito a los roles de coordinación (RBAC nuevo: un coordinador no es
  necesariamente gestor del miembro).
- Posible modelo de "asignación a grupo de trabajo" que enlace
  voluntario ↔ grupo ↔ campaña/actividad.
- Decisión de privacidad: qué campos del voluntario ve un coordinador.

**Cuando se aborde**, la parte de UI podrá reutilizar componentes ya creados en las
sesiones de refactor (ResponsiveTable, FilterBar con AgrupacionCascada en modo
breadcrumb, AppDrawer).

## 2. (añadir aquí futuros flujos detectados)

## 2. Propuesta automática de voluntarios para una actividad

**Lo que falta.** Que la aplicación, dada una actividad con sus fechas/horario y sus
habilidades requeridas, **proponga automáticamente los voluntarios disponibles** que
encajan: cuya disponibilidad horaria (franjas por día de la semana) cubre las fechas
de la actividad y que poseen las habilidades necesarias.

**Implica (no-UI):**
- Modelo: las actividades necesitan declarar habilidades requeridas y un horario
  concreto (fechas + tramos) contra el que cruzar.
- Lógica de matching: intersección de franjas de disponibilidad del voluntario con
  el horario de la actividad + verificación de habilidades (con nivel mínimo).
  Posible puntuación/ranking de candidatos por grado de encaje.
- Resolver/servicio que exponga "voluntarios candidatos para la actividad X",
  respetando ámbito organizativo y RBAC de coordinación (ver punto 1).
- Relación con el punto 1 (consulta de disponibilidad/habilidades por coordinador):
  esto es la versión "push" (la app sugiere) de aquella consulta "pull" (el
  coordinador busca). Conviene diseñarlos juntos.

**Cuando se aborde**, la UI podrá reutilizar ResponsiveTable (lista de candidatos),
AppDrawer (ficha rápida del candidato) y los badges de estado ya existentes.

## 3. (añadir aquí futuros flujos detectados)
