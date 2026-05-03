1. Entidades principales
Miembro

Persona registrada en la asociación con derechos completos.

Atributos relevantes:

Identidad y datos personales
Habilidades
Estado (pendiente, admitido, rechazado)
Fecha de solicitud
Fecha de ingreso

Relaciones:

Pertenece a una agrupación territorial (histórica)
Tiene una cuota
Realiza contribuciones económicas
Participa en campañas
Puede convertirse en voluntario
Puede ser gestionado por usuarios con rol autorizado
Voluntario

Entidad que representa la capacidad operativa de una persona para colaborar.

Características:

Puede ser un miembro o una persona externa
Tiene disponibilidad declarada

Atributos:

Calendario de disponibilidad (días y franjas horarias)

Relaciones:

Participa en campañas
Ejecuta tareas
Registra horas de trabajo
Agrupación Territorial

Unidad organizativa de la asociación.

Atributos:

Identificación
Nombre
Configuración (feature_flag de uso)

Relaciones:

Tiene miembros
Tiene voluntarios asociados indirectamente
Tiene una junta directiva
Define asignaciones de cargos a roles
Mantiene histórico de miembros que han pertenecido
Junta Directiva

Estructura organizativa fija dentro de cada agrupación.

Composición (entidades dependientes o roles estructurales):

Presidente
Vicepresidente
Secretario
Tesorero

Relaciones:

Asociada a una agrupación territorial
Cada cargo está ocupado por un miembro
Cada cargo se mapea a uno o varios roles de aplicación
Cargo

Posición dentro de la junta directiva.

Relaciones:

Pertenece a una junta directiva
Está ocupado por un miembro
Se asocia a roles (mapping configurable)
Rol

Representa capacidades funcionales dentro de la aplicación.

Relaciones:

Se asigna a cargos (a nivel territorial o central)
Agrupa funciones (permisos)
Función (Transacción)

Unidad mínima de permiso dentro del sistema.

Ejemplos:

Asignación de recursos
Gestión de campañas
Contratación
Gestión de militancia

Relaciones:

Pertenece a uno o varios roles
Cuota

Condiciones económicas del miembro.

Atributos:

Importe
Tipo (ordinaria, reducida, exenta)
Porcentaje de reducción
Mínimos aplicables
Forma de pago

Relaciones:

Asociada a un miembro
Genera contribuciones económicas
Contribución Económica

Registro de pagos realizados por un miembro.

Tipos:

Cuotas ordinarias
Cuotas extraordinarias
Donaciones

Relaciones:

Pertenece a un miembro
Campaña

Entidad organizativa de actividad política/social.

Relaciones:

Tiene tareas
Tiene participantes (miembros/voluntarios)
Tarea

Unidad de trabajo dentro de una campaña.

Atributos:

Descripción
Recursos asignados (presupuesto, horas, etc.)

Relaciones:

Pertenece a una campaña
Es ejecutada por voluntarios
Participación

Entidad intermedia entre voluntario (o miembro) y campaña.

Atributos:

Horas dedicadas

Relaciones:

Vincula voluntario con campaña
Vincula con tareas ejecutadas
Historial de Agrupación

Registro de pertenencia de un miembro a agrupaciones.

Atributos:

Fecha inicio
Fecha fin

Relaciones:

Vincula miembro con agrupación territorial
Solicitud de Admisión

Entidad que modela el proceso de alta.

Atributos:

Estado (pendiente, aceptada, rechazada)
Fecha de solicitud
Fecha de resolución

Relaciones:

Asociada a un candidato (futuro miembro)
Evaluada por un coordinador
Notificación

Registro de comunicaciones del sistema.

Relaciones:

Asociada a eventos (alta, traslado, validación)
Destinatarios: miembros con roles (coordinadores, junta, etc.)
2. Relaciones clave (resumen)
Un miembro pertenece a una o varias agrupaciones territoriales (con historial)
Un miembro puede ser voluntario, pero un voluntario no necesariamente es miembro
Un voluntario define un calendario de disponibilidad
Una agrupación territorial tiene una junta directiva
Cada cargo de la junta está ocupado por un miembro
Cada cargo se asocia a uno o varios roles
Cada rol agrupa varias funciones
Un miembro tiene una cuota
Un miembro genera múltiples contribuciones económicas
Un voluntario participa en campañas mediante tareas
La participación registra horas dedicadas
Existe un histórico de pertenencia a agrupaciones
El alta de miembro se gestiona mediante solicitudes de admisión
Los cambios relevantes generan notificaciones
3. Consideraciones estructurales
Separación clara entre identidad (miembro) y capacidad operativa (voluntario)
Sistema de permisos basado en:
Cargo → Rol → Función
Configuración multinivel:
Nivel central
Nivel agrupación territorial
Historización obligatoria en:
Pertenencia a agrupaciones
Participación en campañas
Contribuciones económicas
Existencia de reglas de negocio parametrizadas:
Cuotas mínimas
Exenciones
Delegación operativa:
Usuarios con rol pueden gestionar datos de terceros

Este modelo describe un sistema con separación entre estructura organizativa, permisos, actividad y economía, con trazabilidad completa de la vida del miembro dentro de la organización.