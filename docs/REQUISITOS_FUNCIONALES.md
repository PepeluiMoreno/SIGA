1. MÓDULO CONTABLE (CORE FINANCIERO)
1.1 Objetivo

Gestionar la realidad económica de la organización de forma trazable, auditable y conforme a normativa española, con soporte dual:

Contabilidad básica (caja)
Contabilidad avanzada (PGC-ESFL)

Marco:

Plan General de Contabilidad de Entidades Sin Fines Lucrativos
Real Decreto 1491/2011
1.2 Funcionalidad
Ingresos
Cuotas de miembros
Donaciones
Subvenciones
Ingresos extraordinarios
Gastos
Operativos
Campañas
Estructura
Servicios externos
1.3 Núcleo funcional
Libro diario (asientos inmutables)
Plan de cuentas configurable
Ejercicios contables
Dimensiones analíticas:
campaña
actividad
territorio
centro de coste
1.4 Motor contable

Evento → regla → asiento

eventos del sistema generan asientos
reglas parametrizables por tipo de asociación
1.5 Submódulos
1.5.1 Contabilidad básica
criterio de caja
sin devengo
informes simples
1.5.2 Contabilidad avanzada
devengo
amortizaciones
subvenciones imputadas
cierres formales
1.6 Requisitos clave
inmutabilidad contable
trazabilidad total
cierre por ejercicio
auditoría completa
2. MÓDULO DE ADMINISTRACIÓN
2.1 Objetivo

Controlar estructura, permisos, reglas y configuración global del sistema.

2.2 Funciones principales
Usuarios y roles
gestión de usuarios
roles dinámicos
permisos granulares (RBAC)
Organización
niveles:
estatal
territorial
asignación de usuarios a ámbitos
Catálogo de transacciones
definición de operaciones del sistema
vinculación a permisos
2.3 Seguridad
control de acceso por:
rol
territorio
ámbito funcional
auditoría de acciones administrativas
2.4 Configuración global
configuración contable activa
configuración de campañas
reglas de negocio
3. MÓDULO DE CAMPAÑAS (DISEÑO, PLANIFICACIÓN Y SEGUIMIENTO)
3.1 Objetivo

Gestionar proyectos operativos de la organización (campañas) con planificación, ejecución y evaluación.

3.2 Jerarquía
Campaign
Activity
Task
Assignment
3.3 Diseño de campaña
definición de objetivos
planificación temporal
definición de actividades
estimación de recursos
3.4 Actividades
bloques funcionales
planificación temporal
dependencias opcionales
3.5 Tareas
unidad mínima de ejecución
asociada a skill
estimación de horas
fecha objetivo
3.6 Asignación de colaboradores
basado en:
skills
disponibilidad
carga actual
3.7 Motor de planificación
matching automático
balanceo de carga
detección de conflictos
sugerencia de asignaciones
3.8 Seguimiento
estados:
planificada
activa
bloqueada
finalizada
métricas:
avance
desviación temporal
consumo de horas
3.9 Multi-ejercicio
campañas pueden cruzar ejercicios
seguimiento continuo sin corte contable
4. MÓDULO DE MILITANCIA (BASE DE DATOS SOCIAL Y OPERATIVA)
4.1 Objetivo

Gestionar el ciclo de vida de los miembros y su capacidad operativa dentro de la organización.

4.2 Datos de miembro
identidad
estado (activo, baja, suspensión)
territorio
historial de participación
4.3 Sistema de habilidades
catálogo de skills
nivel por miembro
validación de habilidades
4.4 Disponibilidad
calendario de horas disponibles
reservas
bloqueo por asignaciones
4.5 Participación operativa
asignación a tareas
histórico de contribución
carga acumulada
4.6 Preferencias
áreas de interés
disponibilidad voluntaria
restricciones
4.7 Matching interno
relación miembro ↔ tareas
basado en:
skill match
disponibilidad
carga actual
4.8 Privacidad y RGPD
consentimiento explícito
control de datos sensibles
trazabilidad de accesos