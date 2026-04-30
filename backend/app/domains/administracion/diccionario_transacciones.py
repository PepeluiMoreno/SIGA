TRANSACCIONES_SOCIOS = {
    # Solicitudes de admisión
    'solicitudes.listar': {
        'codigo': 'SOL_LIST',
        'nombre': 'Listar solicitudes de admisión',
        'descripcion': 'Ver listado de solicitudes pendientes',
        'modulo': 'administracion_socios',
        'tipo': 'consulta'
    },
    'solicitudes.ver_detalle': {
        'codigo': 'SOL_VIEW',
        'nombre': 'Ver detalle de solicitud',
        'descripcion': 'Ver información completa de una solicitud',
        'modulo': 'administracion_socios',
        'tipo': 'consulta'
    },
    'solicitudes.crear': {
        'codigo': 'SOL_CREATE',
        'nombre': 'Crear solicitud de admisión',
        'descripcion': 'Registrar nueva solicitud (público/socio)',
        'modulo': 'administracion_socios',
        'tipo': 'escritura'
    },
    'solicitudes.aprobar': {
        'codigo': 'SOL_APPROVE',
        'nombre': 'Aprobar solicitud',
        'descripcion': 'Aprobar solicitud y generar socio',
        'modulo': 'administracion_socios',
        'tipo': 'aprobacion'
    },
    'solicitudes.rechazar': {
        'codigo': 'SOL_REJECT',
        'nombre': 'Rechazar solicitud',
        'descripcion': 'Rechazar solicitud de admisión',
        'modulo': 'administracion_socios',
        'tipo': 'aprobacion'
    },
    
    # Gestión de socios
    'socios.listar': {
        'codigo': 'SOC_LIST',
        'nombre': 'Listar socios',
        'descripcion': 'Ver listado de socios',
        'modulo': 'administracion_socios',
        'tipo': 'consulta'
    },
    'socios.ver_detalle': {
        'codigo': 'SOC_VIEW',
        'nombre': 'Ver detalle de socio',
        'descripcion': 'Ver información completa de un socio',
        'modulo': 'administracion_socios',
        'tipo': 'consulta'
    },
    'socios.crear': {
        'codigo': 'SOC_CREATE',
        'nombre': 'Crear socio manualmente',
        'descripcion': 'Alta directa sin solicitud',
        'modulo': 'administracion_socios',
        'tipo': 'escritura'
    },
    'socios.editar': {
        'codigo': 'SOC_EDIT',
        'nombre': 'Editar datos de socio',
        'descripcion': 'Modificar información del socio',
        'modulo': 'administracion_socios',
        'tipo': 'escritura'
    },
    'socios.dar_baja': {
        'codigo': 'SOC_DEACTIVATE',
        'nombre': 'Dar de baja socio',
        'descripcion': 'Baja temporal o definitiva',
        'modulo': 'administracion_socios',
        'tipo': 'critica'
    },
    'socios.reactivar': {
        'codigo': 'SOC_REACTIVATE',
        'nombre': 'Reactivar socio',
        'descripcion': 'Reactivar socio dado de baja',
        'modulo': 'administracion_socios',
        'tipo': 'escritura'
    },
    'socios.cambiar_tipo': {
        'codigo': 'SOC_CHANGE_TYPE',
        'nombre': 'Cambiar tipo de socio',
        'descripcion': 'Modificar tipo de socio',
        'modulo': 'administracion_socios',
        'tipo': 'escritura'
    },
    'socios.bloquear': {
        'codigo': 'SOC_BLOCK',
        'nombre': 'Bloquear/Suspender socio',
        'descripcion': 'Suspender temporalmente un socio',
        'modulo': 'administracion_socios',
        'tipo': 'critica'
    },
    'socios.exportar': {
        'codigo': 'SOC_EXPORT',
        'nombre': 'Exportar datos de socios',
        'descripcion': 'Exportar listados a Excel/CSV',
        'modulo': 'administracion_socios',
        'tipo': 'consulta'
    },
    
    # Tipos de socio
    'tipos_socio.gestionar': {
        'codigo': 'TIPOSOC_MANAGE',
        'nombre': 'Gestionar tipos de socio',
        'descripcion': 'Crear/editar/eliminar tipos de socio',
        'modulo': 'administracion_socios',
        'tipo': 'configuracion'
    },
}

# MÓDULO: TRASLADOS TERRITORIALES
TRANSACCIONES_TRASLADOS = {
    'traslados.solicitar': {
        'codigo': 'TRAS_REQUEST',
        'nombre': 'Solicitar traslado',
        'descripcion': 'Solicitar cambio de agrupación territorial',
        'modulo': 'traslados',
        'tipo': 'escritura'
    },
    'traslados.listar': {
        'codigo': 'TRAS_LIST',
        'nombre': 'Listar solicitudes de traslado',
        'descripcion': 'Ver solicitudes pendientes de aprobación',
        'modulo': 'traslados',
        'tipo': 'consulta'
    },
    'traslados.aprobar': {
        'codigo': 'TRAS_APPROVE',
        'nombre': 'Aprobar traslado',
        'descripcion': 'Aprobar solicitud de traslado',
        'modulo': 'traslados',
        'tipo': 'aprobacion'
    },
    'traslados.rechazar': {
        'codigo': 'TRAS_REJECT',
        'nombre': 'Rechazar traslado',
        'descripcion': 'Rechazar solicitud de traslado',
        'modulo': 'traslados',
        'tipo': 'aprobacion'
    },
    'traslados.cancelar': {
        'codigo': 'TRAS_CANCEL',
        'nombre': 'Cancelar traslado',
        'descripcion': 'Cancelar solicitud propia',
        'modulo': 'traslados',
        'tipo': 'escritura'
    },
}

# MÓDULO: TESORERÍA
TRANSACCIONES_TESORERIA = {
    # Cuotas
    'cuotas.listar': {
        'codigo': 'CUOT_LIST',
        'nombre': 'Listar cuotas',
        'descripcion': 'Ver listado de cuotas',
        'modulo': 'tesoreria',
        'tipo': 'consulta'
    },
    'cuotas.generar': {
        'codigo': 'CUOT_GENERATE',
        'nombre': 'Generar cuotas anuales',
        'descripcion': 'Crear cuotas para todos los socios',
        'modulo': 'tesoreria',
        'tipo': 'escritura'
    },
    'cuotas.registrar_pago': {
        'codigo': 'CUOT_PAY',
        'nombre': 'Registrar pago de cuota',
        'descripcion': 'Marcar cuota como pagada',
        'modulo': 'tesoreria',
        'tipo': 'escritura'
    },
    'cuotas.exentar': {
        'codigo': 'CUOT_EXEMPT',
        'nombre': 'Exentar cuota',
        'descripcion': 'Marcar cuota como exenta',
        'modulo': 'tesoreria',
        'tipo': 'critica'
    },
    'cuotas.anular': {
        'codigo': 'CUOT_CANCEL',
        'nombre': 'Anular cuota',
        'descripcion': 'Anular cuota generada',
        'modulo': 'tesoreria',
        'tipo': 'critica'
    },
    
    # Remesas SEPA
    'remesas.crear': {
        'codigo': 'REM_CREATE',
        'nombre': 'Crear remesa SEPA',
        'descripcion': 'Generar nueva remesa de cobros',
        'modulo': 'tesoreria',
        'tipo': 'escritura'
    },
    'remesas.generar_xml': {
        'codigo': 'REM_XML',
        'nombre': 'Generar XML SEPA',
        'descripcion': 'Crear archivo XML para banco',
        'modulo': 'tesoreria',
        'tipo': 'escritura'
    },
    'remesas.enviar': {
        'codigo': 'REM_SEND',
        'nombre': 'Enviar remesa al banco',
        'descripcion': 'Marcar remesa como enviada',
        'modulo': 'tesoreria',
        'tipo': 'critica'
    },
    'remesas.procesar_respuesta': {
        'codigo': 'REM_PROCESS',
        'nombre': 'Procesar respuesta banco',
        'descripcion': 'Registrar cobros y rechazos',
        'modulo': 'tesoreria',
        'tipo': 'escritura'
    },
    'remesas.listar': {
        'codigo': 'REM_LIST',
        'nombre': 'Listar remesas',
        'descripcion': 'Ver listado de remesas',
        'modulo': 'tesoreria',
        'tipo': 'consulta'
    },
    
    # Donaciones
    'donaciones.listar': {
        'codigo': 'DON_LIST',
        'nombre': 'Listar donaciones',
        'descripcion': 'Ver listado de donaciones',
        'modulo': 'tesoreria',
        'tipo': 'consulta'
    },
    'donaciones.registrar': {
        'codigo': 'DON_CREATE',
        'nombre': 'Registrar donación',
        'descripcion': 'Registrar nueva donación',
        'modulo': 'tesoreria',
        'tipo': 'escritura'
    },
    'donaciones.emitir_certificado': {
        'codigo': 'DON_CERT',
        'nombre': 'Emitir certificado fiscal',
        'descripcion': 'Generar certificado de donación',
        'modulo': 'tesoreria',
        'tipo': 'escritura'
    },
    
    # Informes financieros
    'informes_financieros.ver': {
        'codigo': 'FIN_REPORTS',
        'nombre': 'Ver informes financieros',
        'descripcion': 'Acceder a informes y estadísticas',
        'modulo': 'tesoreria',
        'tipo': 'consulta'
    },
    'informes_financieros.exportar': {
        'codigo': 'FIN_EXPORT',
        'nombre': 'Exportar informes financieros',
        'descripcion': 'Descargar informes en PDF/Excel',
        'modulo': 'tesoreria',
        'tipo': 'consulta'
    },
}

# MÓDULO: COMUNICACIONES
TRANSACCIONES_COMUNICACIONES = {
    'mensajes.listar': {
        'codigo': 'MSG_LIST',
        'nombre': 'Listar mensajes',
        'descripcion': 'Ver mensajes enviados/borradores',
        'modulo': 'comunicaciones',
        'tipo': 'consulta'
    },
    'mensajes.crear': {
        'codigo': 'MSG_CREATE',
        'nombre': 'Crear mensaje',
        'descripcion': 'Redactar nuevo mensaje',
        'modulo': 'comunicaciones',
        'tipo': 'escritura'
    },
    'mensajes.enviar_general': {
        'codigo': 'MSG_SEND_ALL',
        'nombre': 'Enviar a todos los socios',
        'descripcion': 'Envío masivo a nivel nacional',
        'modulo': 'comunicaciones',
        'tipo': 'critica'
    },
    'mensajes.enviar_territorial': {
        'codigo': 'MSG_SEND_TERR',
        'nombre': 'Enviar a agrupación territorial',
        'descripcion': 'Envío a socios de su ámbito',
        'modulo': 'comunicaciones',
        'tipo': 'escritura'
    },
    'mensajes.enviar_campana': {
        'codigo': 'MSG_SEND_CAMP',
        'nombre': 'Enviar a equipo de campaña',
        'descripcion': 'Envío a miembros de campaña',
        'modulo': 'comunicaciones',
        'tipo': 'escritura'
    },
    'mensajes.aprobar': {
        'codigo': 'MSG_APPROVE',
        'nombre': 'Aprobar mensaje',
        'descripcion': 'Aprobar mensaje para envío',
        'modulo': 'comunicaciones',
        'tipo': 'aprobacion'
    },
    'mensajes.rechazar': {
        'codigo': 'MSG_REJECT',
        'nombre': 'Rechazar mensaje',
        'descripcion': 'Rechazar mensaje pendiente',
        'modulo': 'comunicaciones',
        'tipo': 'aprobacion'
    },
    'mensajes.ver_estadisticas': {
        'codigo': 'MSG_STATS',
        'nombre': 'Ver estadísticas de mensajes',
        'descripcion': 'Ver aperturas, clicks, etc.',
        'modulo': 'comunicaciones',
        'tipo': 'consulta'
    },
    'plantillas.gestionar': {
        'codigo': 'TPL_MANAGE',
        'nombre': 'Gestionar plantillas',
        'descripcion': 'Crear/editar plantillas de email',
        'modulo': 'comunicaciones',
        'tipo': 'configuracion'
    },
}

# MÓDULO: CAMPAÑAS
TRANSACCIONES_CAMPANAS = {
    'campanas.listar': {
        'codigo': 'CAMP_LIST',
        'nombre': 'Listar campañas',
        'descripcion': 'Ver listado de campañas',
        'modulo': 'campanas',
        'tipo': 'consulta'
    },
    'campanas.ver_detalle': {
        'codigo': 'CAMP_VIEW',
        'nombre': 'Ver detalle de campaña',
        'descripcion': 'Ver información completa',
        'modulo': 'campanas',
        'tipo': 'consulta'
    },
    'campanas.crear': {
        'codigo': 'CAMP_CREATE',
        'nombre': 'Crear campaña',
        'descripcion': 'Crear nueva campaña',
        'modulo': 'campanas',
        'tipo': 'escritura'
    },
    'campanas.editar': {
        'codigo': 'CAMP_EDIT',
        'nombre': 'Editar campaña',
        'descripcion': 'Modificar campaña existente',
        'modulo': 'campanas',
        'tipo': 'escritura'
    },
    'campanas.activar': {
        'codigo': 'CAMP_ACTIVATE',
        'nombre': 'Activar campaña',
        'descripcion': 'Cambiar estado a activa',
        'modulo': 'campanas',
        'tipo': 'escritura'
    },
    'campanas.finalizar': {
        'codigo': 'CAMP_CLOSE',
        'nombre': 'Finalizar campaña',
        'descripcion': 'Cerrar campaña',
        'modulo': 'campanas',
        'tipo': 'escritura'
    },
    'campanas.cancelar': {
        'codigo': 'CAMP_CANCEL',
        'nombre': 'Cancelar campaña',
        'descripcion': 'Cancelar campaña planificada',
        'modulo': 'campanas',
        'tipo': 'critica'
    },
    
    # Participantes
    'participantes.inscribir': {
        'codigo': 'PART_ENROLL',
        'nombre': 'Inscribir participante',
        'descripcion': 'Añadir participante a campaña',
        'modulo': 'campanas',
        'tipo': 'escritura'
    },
    'participantes.dar_baja': {
        'codigo': 'PART_REMOVE',
        'nombre': 'Dar de baja participante',
        'descripcion': 'Eliminar participante de campaña',
        'modulo': 'campanas',
        'tipo': 'escritura'
    },
    'participantes.registrar_horas': {
        'codigo': 'PART_HOURS',
        'nombre': 'Registrar horas de voluntariado',
        'descripcion': 'Anotar horas trabajadas',
        'modulo': 'campanas',
        'tipo': 'escritura'
    },
}

# MÓDULO: EVENTOS
TRANSACCIONES_EVENTOS = {
    'eventos.listar': {
        'codigo': 'EVT_LIST',
        'nombre': 'Listar eventos',
        'descripcion': 'Ver listado de eventos',
        'modulo': 'eventos',
        'tipo': 'consulta'
    },
    'eventos.ver_detalle': {
        'codigo': 'EVT_VIEW',
        'nombre': 'Ver detalle de evento',
        'descripcion': 'Ver información del evento',
        'modulo': 'eventos',
        'tipo': 'consulta'
    },
    'eventos.crear': {
        'codigo': 'EVT_CREATE',
        'nombre': 'Crear evento',
        'descripcion': 'Organizar nuevo evento',
        'modulo': 'eventos',
        'tipo': 'escritura'
    },
    'eventos.editar': {
        'codigo': 'EVT_EDIT',
        'nombre': 'Editar evento',
        'descripcion': 'Modificar evento existente',
        'modulo': 'eventos',
        'tipo': 'escritura'
    },
    'eventos.cancelar': {
        'codigo': 'EVT_CANCEL',
        'nombre': 'Cancelar evento',
        'descripcion': 'Cancelar evento programado',
        'modulo': 'eventos',
        'tipo': 'critica'
    },
    'eventos.inscribirse': {
        'codigo': 'EVT_REGISTER',
        'nombre': 'Inscribirse en evento',
        'descripcion': 'Registrarse como asistente',
        'modulo': 'eventos',
        'tipo': 'escritura'
    },
    'eventos.gestionar_inscripciones': {
        'codigo': 'EVT_MANAGE_REG',
        'nombre': 'Gestionar inscripciones',
        'descripcion': 'Aprobar/rechazar inscripciones',
        'modulo': 'eventos',
        'tipo': 'escritura'
    },
    'eventos.registrar_asistencia': {
        'codigo': 'EVT_ATTENDANCE',
        'nombre': 'Registrar asistencia',
        'descripcion': 'Check-in de asistentes',
        'modulo': 'eventos',
        'tipo': 'escritura'
    },
}

# MÓDULO: VOLUNTARIADO
TRANSACCIONES_VOLUNTARIADO = {
    'voluntarios.listar': {
        'codigo': 'VOL_LIST',
        'nombre': 'Listar voluntarios',
        'descripcion': 'Ver listado de voluntarios',
        'modulo': 'voluntariado',
        'tipo': 'consulta'
    },
    'voluntarios.ver_perfil': {
        'codigo': 'VOL_VIEW',
        'nombre': 'Ver perfil de voluntario',
        'descripcion': 'Ver información completa',
        'modulo': 'voluntariado',
        'tipo': 'consulta'
    },
    'oportunidades.listar': {
        'codigo': 'OPP_LIST',
        'nombre': 'Listar oportunidades',
        'descripcion': 'Ver oportunidades disponibles',
        'modulo': 'voluntariado',
        'tipo': 'consulta'
    },
    'oportunidades.crear': {
        'codigo': 'OPP_CREATE',
        'nombre': 'Crear oportunidad',
        'descripcion': 'Publicar nueva oportunidad',
        'modulo': 'voluntariado',
        'tipo': 'escritura'
    },
    'oportunidades.postularse': {
        'codigo': 'OPP_APPLY',
        'nombre': 'Postularse a oportunidad',
        'descripcion': 'Solicitar participar',
        'modulo': 'voluntariado',
        'tipo': 'escritura'
    },
    'asignaciones.aprobar': {
        'codigo': 'ASG_APPROVE',
        'nombre': 'Aprobar asignación',
        'descripcion': 'Aceptar voluntario',
        'modulo': 'voluntariado',
        'tipo': 'aprobacion'
    },
    'competencias.gestionar': {
        'codigo': 'SKILL_MANAGE',
        'nombre': 'Gestionar competencias',
        'descripcion': 'Añadir/validar habilidades',
        'modulo': 'voluntariado',
        'tipo': 'escritura'
    },
}

# MÓDULO: EQUIPOS DE TRABAJO
TRANSACCIONES_EQUIPOS = {
    'equipos.listar': {
        'codigo': 'TEAM_LIST',
        'nombre': 'Listar equipos',
        'descripcion': 'Ver equipos de trabajo',
        'modulo': 'equipos',
        'tipo': 'consulta'
    },
    'equipos.ver_detalle': {
        'codigo': 'TEAM_VIEW',
        'nombre': 'Ver detalle de equipo',
        'descripcion': 'Ver información del equipo',
        'modulo': 'equipos',
        'tipo': 'consulta'
    },
    'equipos.crear': {
        'codigo': 'TEAM_CREATE',
        'nombre': 'Crear equipo',
        'descripcion': 'Crear nuevo equipo',
        'modulo': 'equipos',
        'tipo': 'escritura'
    },
    'equipos.editar': {
        'codigo': 'TEAM_EDIT',
        'nombre': 'Editar equipo',
        'descripcion': 'Modificar equipo existente',
        'modulo': 'equipos',
        'tipo': 'escritura'
    },
    'equipos.disolver': {
        'codigo': 'TEAM_DISSOLVE',
        'nombre': 'Disolver equipo',
        'descripcion': 'Eliminar equipo',
        'modulo': 'equipos',
        'tipo': 'critica'
    },
    'miembros.añadir': {
        'codigo': 'TMBR_ADD',
        'nombre': 'Añadir miembro',
        'descripcion': 'Incorporar miembro al equipo',
        'modulo': 'equipos',
        'tipo': 'escritura'
    },
    'miembros.remover': {
        'codigo': 'TMBR_REMOVE',
        'nombre': 'Remover miembro',
        'descripcion': 'Sacar miembro del equipo',
        'modulo': 'equipos',
        'tipo': 'escritura'
    },
    'tareas.crear': {
        'codigo': 'TASK_CREATE',
        'nombre': 'Crear tarea',
        'descripcion': 'Asignar nueva tarea',
        'modulo': 'equipos',
        'tipo': 'escritura'
    },
    'tareas.actualizar': {
        'codigo': 'TASK_UPDATE',
        'nombre': 'Actualizar tarea',
        'descripcion': 'Cambiar estado/asignación',
        'modulo': 'equipos',
        'tipo': 'escritura'
    },
    'reuniones.programar': {
        'codigo': 'MEET_SCHEDULE',
        'nombre': 'Programar reunión',
        'descripcion': 'Crear nueva reunión',
        'modulo': 'equipos',
        'tipo': 'escritura'
    },
}

# MÓDULO: AGRUPACIONES TERRITORIALES
TRANSACCIONES_AGRUPACIONES = {
    'agrupaciones.listar': {
        'codigo': 'AGR_LIST',
        'nombre': 'Listar agrupaciones',
        'descripcion': 'Ver estructura territorial',
        'modulo': 'agrupaciones',
        'tipo': 'consulta'
    },
    'agrupaciones.ver_detalle': {
        'codigo': 'AGR_VIEW',
        'nombre': 'Ver detalle de agrupación',
        'descripcion': 'Ver información completa',
        'modulo': 'agrupaciones',
        'tipo': 'consulta'
    },
    'agrupaciones.crear': {
        'codigo': 'AGR_CREATE',
        'nombre': 'Crear agrupación',
        'descripcion': 'Crear nueva delegación',
        'modulo': 'agrupaciones',
        'tipo': 'configuracion'
    },
    'agrupaciones.editar': {
        'codigo': 'AGR_EDIT',
        'nombre': 'Editar agrupación',
        'descripcion': 'Modificar datos de delegación',
        'modulo': 'agrupaciones',
        'tipo': 'configuracion'
    },
    'agrupaciones.desactivar': {
        'codigo': 'AGR_DEACTIVATE',
        'nombre': 'Desactivar agrupación',
        'descripcion': 'Cerrar delegación',
        'modulo': 'agrupaciones',
        'tipo': 'critica'
    },
    'cargos.asignar': {
        'codigo': 'POS_ASSIGN',
        'nombre': 'Asignar cargo',
        'descripcion': 'Nombrar coordinador/secretario/tesorero',
        'modulo': 'agrupaciones',
        'tipo': 'escritura'
    },
    'cargos.remover': {
        'codigo': 'POS_REMOVE',
        'nombre': 'Remover cargo',
        'descripcion': 'Cesar de cargo',
        'modulo': 'agrupaciones',
        'tipo': 'escritura'
    },
}

# MÓDULO: ADMINISTRACIÓN DEL SISTEMA
TRANSACCIONES_ADMINISTRACION = {
    'usuarios.listar': {
        'codigo': 'USR_LIST',
        'nombre': 'Listar usuarios',
        'descripcion': 'Ver usuarios del sistema',
        'modulo': 'administracion',
        'tipo': 'consulta'
    },
    'usuarios.crear': {
        'codigo': 'USR_CREATE',
        'nombre': 'Crear usuario',
        'descripcion': 'Crear acceso al sistema',
        'modulo': 'administracion',
        'tipo': 'critica'
    },
    'usuarios.editar': {
        'codigo': 'USR_EDIT',
        'nombre': 'Editar usuario',
        'descripcion': 'Modificar datos de usuario',
        'modulo': 'administracion',
        'tipo': 'escritura'
    },
    'usuarios.bloquear': {
        'codigo': 'USR_BLOCK',
        'nombre': 'Bloquear usuario',
        'descripcion': 'Suspender acceso',
        'modulo': 'administracion',
        'tipo': 'critica'
    },
    'usuarios.eliminar': {
        'codigo': 'USR_DELETE',
        'nombre': 'Eliminar usuario',
        'descripcion': 'Borrar usuario del sistema',
        'modulo': 'administracion',
        'tipo': 'critica'
    },
    
    'roles.listar': {
        'codigo': 'ROL_LIST',
        'nombre': 'Listar roles',
        'descripcion': 'Ver roles del sistema',
        'modulo': 'administracion',
        'tipo': 'consulta'
    },
    'roles.crear': {
        'codigo': 'ROL_CREATE',
        'nombre': 'Crear rol',
        'descripcion': 'Crear nuevo rol',
        'modulo': 'administracion',
        'tipo': 'configuracion'
    },
    'roles.editar': {
        'codigo': 'ROL_EDIT',
        'nombre': 'Editar rol',
        'descripcion': 'Modificar rol existente',
        'modulo': 'administracion',
        'tipo': 'configuracion'
    },
    'roles.eliminar': {
        'codigo': 'ROL_DELETE',
        'nombre': 'Eliminar rol',
        'descripcion': 'Borrar rol del sistema',
        'modulo': 'administracion',
        'tipo': 'critica'
    },
    
    'permisos.asignar_a_rol': {
        'codigo': 'PERM_ASSIGN',
        'nombre': 'Asignar permisos a rol',
        'descripcion': 'Configurar transacciones del rol',
        'modulo': 'administracion',
        'tipo': 'configuracion'
    },
    'permisos.revocar_de_rol': {
        'codigo': 'PERM_REVOKE',
        'nombre': 'Revocar permisos de rol',
        'descripcion': 'Quitar transacciones del rol',
        'modulo': 'administracion',
        'tipo': 'configuracion'
    },
    
    'usuarios_roles.asignar': {
        'codigo': 'USRROL_ASSIGN',
        'nombre': 'Asignar rol a usuario',
        'descripcion': 'Dar rol a un usuario',
        'modulo': 'administracion',
        'tipo': 'escritura'
    },
    'usuarios_roles.revocar': {
        'codigo': 'USRROL_REVOKE',
        'nombre': 'Revocar rol de usuario',
        'descripcion': 'Quitar rol a usuario',
        'modulo': 'administracion',
        'tipo': 'escritura'
    },
    
    'auditoria.consultar': {
        'codigo': 'AUD_VIEW',
        'nombre': 'Consultar auditoría',
        'descripcion': 'Ver logs de auditoría',
        'modulo': 'administracion',
        'tipo': 'consulta'
    },
    'auditoria.exportar': {
        'codigo': 'AUD_EXPORT',
        'nombre': 'Exportar auditoría',
        'descripcion': 'Descargar logs',
        'modulo': 'administracion',
        'tipo': 'consulta'
    },
    
    'configuracion.ver': {
        'codigo': 'CFG_VIEW',
        'nombre': 'Ver configuración',
        'descripcion': 'Ver parámetros del sistema',
        'modulo': 'administracion',
        'tipo': 'consulta'
    },
    'configuracion.editar': {
        'codigo': 'CFG_EDIT',
        'nombre': 'Editar configuración',
        'descripcion': 'Modificar parámetros',
        'modulo': 'administracion',
        'tipo': 'configuracion'
    },
}

# MÓDULO: INFORMES
TRANSACCIONES_INFORMES = {
    'informes.socios': {
        'codigo': 'RPT_MEMBERS',
        'nombre': 'Informes de socios',
        'descripcion': 'Estadísticas de socios',
        'modulo': 'informes',
        'tipo': 'consulta'
    },
    'informes.financieros': {
        'codigo': 'RPT_FINANCE',
        'nombre': 'Informes financieros',
        'descripcion': 'Estadísticas económicas',
        'modulo': 'informes',
        'tipo': 'consulta'
    },
    'informes.campanas': {
        'codigo': 'RPT_CAMPAIGNS',
        'nombre': 'Informes de campañas',
        'descripcion': 'Resultados de campañas',
        'modulo': 'informes',
        'tipo': 'consulta'
    },
    'informes.voluntariado': {
        'codigo': 'RPT_VOLUNTEERS',
        'nombre': 'Informes de voluntariado',
        'descripcion': 'Estadísticas de voluntarios',
        'modulo': 'informes',
        'tipo': 'consulta'
    },
    'informes.personalizados': {
        'codigo': 'RPT_CUSTOM',
        'nombre': 'Informes personalizados',
        'descripcion': 'Crear informes a medida',
        'modulo': 'informes',
        'tipo': 'consulta'
    },
    'dashboards.ejecutivo': {
        'codigo': 'DASH_EXEC',
        'nombre': 'Dashboard ejecutivo',
        'descripcion': 'Vista general de indicadores',
        'modulo': 'informes',
        'tipo': 'consulta'
    },
}