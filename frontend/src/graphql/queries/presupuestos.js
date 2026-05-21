// Queries y mutations GraphQL del módulo de presupuestos

export const GET_PLANIFICACIONES = `
  query Planificaciones {
    planificaciones {
      id ejercicio nombre descripcion objetivos estadoId fechaAprobacion
      presupuestoTotal presupuestoIngresos presupuestoGastos
      saldoPresupuestado gastosEjecutados porcentajeEjecucion controlDisponibilidad
    }
  }
`

export const GET_PLANIFICACION = `
  query Planificacion($planificacionId: UUID!) {
    planificacion(planificacionId: $planificacionId) {
      id ejercicio nombre descripcion objetivos estadoId fechaAprobacion
      presupuestoTotal presupuestoIngresos presupuestoGastos
      saldoPresupuestado gastosEjecutados porcentajeEjecucion controlDisponibilidad
    }
  }
`

export const GET_PARTIDAS = `
  query PartidasPresupuestarias($planificacionId: UUID!, $tipo: String) {
    partidasPresupuestarias(planificacionId: $planificacionId, tipo: $tipo) {
      id codigo nombre descripcion ejercicio tipo
      categoriaId actividadId campaniaId
      importePresupuestado importeComprometido importeEjecutado
      importeDisponible porcentajeEjecutado
      importeInicial importeModificaciones estaSobreejecutada estaAgotada
    }
  }
`

export const GET_INFORME_DESVIACIONES = `
  query InformeDesviaciones($planificacionId: UUID!) {
    informeDesviaciones(planificacionId: $planificacionId) {
      partidaId codigo nombre tipo
      presupuestado comprometido ejecutado disponible desviacion porcentajeEjecucion
    }
  }
`

export const CREAR_PLANIFICACION = `
  mutation CrearPlanificacion($data: CrearPlanificacionInput!) {
    crearPlanificacion(data: $data) { id ejercicio nombre estadoId }
  }
`

export const CREAR_PARTIDA = `
  mutation CrearPartida($data: CrearPartidaInput!) {
    crearPartida(data: $data) { id codigo nombre tipo importePresupuestado }
  }
`

export const ACTUALIZAR_PARTIDA = `
  mutation ActualizarPartida($data: ActualizarPartidaInput!) {
    actualizarPartida(data: $data) { id codigo nombre importePresupuestado }
  }
`

export const ELIMINAR_PARTIDA = `
  mutation EliminarPartida($partidaId: UUID!) {
    eliminarPartida(partidaId: $partidaId)
  }
`

export const PROPONER_PRESUPUESTO = `
  mutation ProponerPresupuesto($planificacionId: UUID!) {
    proponerPresupuesto(planificacionId: $planificacionId) { id estadoId }
  }
`

export const APROBAR_PRESUPUESTO = `
  mutation AprobarPresupuesto($planificacionId: UUID!) {
    aprobarPresupuesto(planificacionId: $planificacionId) { id estadoId fechaAprobacion }
  }
`

export const INICIAR_EJECUCION_PRESUPUESTO = `
  mutation IniciarEjecucion($planificacionId: UUID!) {
    iniciarEjecucionPresupuesto(planificacionId: $planificacionId) { id estadoId }
  }
`

export const CERRAR_PRESUPUESTO = `
  mutation CerrarPresupuesto($planificacionId: UUID!) {
    cerrarPresupuesto(planificacionId: $planificacionId) { id estadoId }
  }
`

export const DEVOLVER_A_BORRADOR = `
  mutation DevolverABorrador($planificacionId: UUID!) {
    devolverPresupuestoABorrador(planificacionId: $planificacionId) { id estadoId }
  }
`

export const GET_ESTADOS_PLANIFICACION = `
  query EstadosPlanificacion {
    estadosPlanificacion { id codigo nombre orden color esFinal }
  }
`

// ── FASE 2: modificaciones, alertas, control de disponibilidad ────────────────

export const GET_MODIFICACIONES = `
  query ModificacionesPresupuestarias($planificacionId: UUID!) {
    modificacionesPresupuestarias(planificacionId: $planificacionId) {
      id tipo partidaDestinoId partidaOrigenId importe fecha motivo
    }
  }
`

export const GET_ALERTAS = `
  query AlertasPresupuestarias($planificacionId: UUID!) {
    alertasPresupuestarias(planificacionId: $planificacionId) {
      partidaId codigo nombre tipoAlerta mensaje
    }
  }
`

export const REGISTRAR_MODIFICACION = `
  mutation RegistrarModificacion($data: RegistrarModificacionInput!) {
    registrarModificacionPresupuestaria(data: $data) {
      id tipo importe fecha motivo
    }
  }
`

export const ESTABLECER_CONTROL_DISPONIBILIDAD = `
  mutation EstablecerControl($planificacionId: UUID!, $activo: Boolean!) {
    establecerControlDisponibilidad(planificacionId: $planificacionId, activo: $activo) {
      id controlDisponibilidad
    }
  }
`
