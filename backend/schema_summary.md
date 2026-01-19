# Schema GraphQL AIEL - Resumen

## Estadísticas
- **Tamaño**: 86,107 caracteres
- **Total de tipos**: 232 tipos GraphQL
- **Total de queries**: 127 queries disponibles

## Dominios Implementados

### Core
- Usuarios y Roles
- Configuración (con validación y historial)
- Estados (Cuota, Campaña, Tarea, Participante, OrdenCobro, Remesa, Donación)
- Historial de Estados
- Seguridad (Sesión, Historial, IPs Bloqueadas, Intentos de Acceso)

### Geográfico
- Países
- Provincias
- Municipios
- Direcciones
- Agrupaciones Territoriales

### Notificaciones
- Tipos de Notificación
- Notificaciones
- Preferencias de Notificación

### Financiero
- Importes de Cuota por Año
- Cuotas Anuales
- Conceptos de Donación
- Donaciones
- Remesas
- Órdenes de Cobro
- Estados de Planificación
- Categorías de Partida
- Partidas Presupuestarias
- Planificación Anual

### Colaboraciones
- Asociaciones
- Tipos de Asociación
- Convenios
- Estados de Convenio

### Miembros
- Tipos de Miembro
- Miembros (Socios)

### Campañas
- Tipos de Campaña
- Campañas
- Roles de Participante
- Acciones de Campaña
- Participantes de Campaña

### Actividades
- Tipos de Actividad
- Estados de Actividad
- Estados de Propuesta
- Tipos de Recurso
- Tipos de KPI
- Propuestas de Actividad
- Tareas de Propuesta
- Recursos de Propuesta
- Grupos de Propuesta
- Actividades
- Tareas de Actividad
- Recursos de Actividad
- Grupos de Actividad
- Participantes de Actividad
- KPIs
- KPIs de Actividad
- Mediciones de KPI

### Grupos de Trabajo
- Tipos de Grupo
- Roles de Grupo
- Grupos de Trabajo
- Miembros de Grupo
- Tareas de Grupo
- Reuniones de Grupo
- Asistentes a Reunión

### Voluntariado
- Categorías de Competencia
- Competencias
- Niveles de Competencia
- Competencias de Miembro
- Tipos de Documento de Voluntario
- Documentos de Miembro
- Tipos de Formación
- Formación de Miembro

## Características Automáticas (Strawchemy)

Cada tipo incluye automáticamente:
- **Campos de agregación**: avg, count, max, min, stddev, sum, variance
- **Campos numéricos**: para operaciones matemáticas
- **Campos min/max**: para comparaciones
- **Filtros**: where, order_by, limit, offset
- **Relaciones**: eager loading con `lazy='selectin'`

## Uso

El schema está disponible en:
- **Endpoint**: `http://localhost:8000/graphql`
- **Archivo SDL**: `backend/schema.graphql`
- **GraphQL Playground**: Navegador web en el endpoint

## Ejemplo de Query

```graphql
query {
  miembros {
    id
    nombre
    apellido1
    email
    esVoluntario
    tipoMiembro {
      nombre
    }
    agrupacion {
      nombre
    }
  }
}
```
