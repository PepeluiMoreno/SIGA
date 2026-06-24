// Queries GraphQL para el módulo económico
// IMPORTANTE: Strawberry usa camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID
// Strawchemy no usa limit/offset, usa filtros automáticos generados

// Query para obtener cuotas anuales
export const GET_CUOTAS_ANUALES = `
  query CuotasAnuales {
    cuotasAnuales {
      id
      ejercicio
      importe
      importePagado
      fechaPago
      modoIngreso
      miembro {
        id
        nombre
        apellido1
        apellido2
      }
      estado {
        id
        nombre
        color
      }
      agrupacion {
        id
        nombre
      }
      fechaCreacion
    }
  }
`

// Query para obtener cuotas por miembro
export const GET_CUOTAS_BY_MIEMBRO = `
  query CuotasByMiembro($vinculacionSocioId: UUID!) {
    cuotasAnuales(filter: {vinculacionSocioId: {eq: $vinculacionSocioId}}) {
      id
      ejercicio
      importe
      importePagado
      fechaPago
      modoIngreso
      estado {
        id
        nombre
        color
      }
    }
  }
`

// Query para obtener donaciones
export const GET_DONACIONES = `
  query Donaciones {
    donaciones {
      id
      fecha
      importe
      gastos
      donanteNombre
      donanteDni
      donanteEmail
      donanteTelefono
      tipo
      caracter
      descripcionEspecie
      valoracion
      documentoValoracion
      modoIngreso
      referenciaPago
      numeroCertificado
      fechaCertificado
      concepto {
        id
        nombre
      }
      estado {
        id
        nombre
        color
      }
      certificadoEmitido
      anonima
      observaciones
      fechaCreacion
    }
  }
`

// ── Donaciones (flujo 6) — mutations + queries ────────────────────────────

export const REGISTRAR_DONACION = `
  mutation RegistrarDonacion(
    $importe: Float!
    $fechaDonacion: Date!
    $tipo: String!
    $caracter: String!
    $miembroId: UUID
    $donanteNombre: String
    $donanteDni: String
    $donanteEmail: String
    $donanteTelefono: String
    $conceptoId: UUID
    $campaniaId: UUID
    $modoIngreso: String
    $referenciaPago: String
    $descripcionEspecie: String
    $valoracion: Float
    $documentoValoracion: String
    $anonima: Boolean!
    $observaciones: String
    $cobrarInmediato: Boolean!
    $cuentaBancariaId: UUID
  ) {
    registrarDonacion(
      importe: $importe
      fechaDonacion: $fechaDonacion
      tipo: $tipo
      caracter: $caracter
      contactoId: $miembroId
      donanteNombre: $donanteNombre
      donanteDni: $donanteDni
      donanteEmail: $donanteEmail
      donanteTelefono: $donanteTelefono
      conceptoId: $conceptoId
      campaniaId: $campaniaId
      modoIngreso: $modoIngreso
      referenciaPago: $referenciaPago
      descripcionEspecie: $descripcionEspecie
      valoracion: $valoracion
      documentoValoracion: $documentoValoracion
      anonima: $anonima
      observaciones: $observaciones
      cobrarInmediato: $cobrarInmediato
      cuentaBancariaId: $cuentaBancariaId
    )
  }
`

export const MARCAR_DONACION_COBRADA = `
  mutation MarcarDonacionCobrada(
    $donacionId: UUID!
    $cuentaBancariaId: UUID
    $fechaCobro: Date
  ) {
    marcarDonacionCobrada(
      donacionId: $donacionId
      cuentaBancariaId: $cuentaBancariaId
      fechaCobro: $fechaCobro
    )
  }
`

export const ANULAR_DONACION = `
  mutation AnularDonacion($donacionId: UUID!, $motivo: String) {
    anularDonacion(donacionId: $donacionId, motivo: $motivo)
  }
`

export const LISTAR_DONACIONES_CERTIFICABLES = `
  mutation DonacionesCertificables($ejercicio: Int!) {
    listarDonacionesCertificables(ejercicio: $ejercicio) {
      nif
      nombre
      tipo
      total
      nDonaciones
      donacionIds
      todasCertificadas
    }
  }
`

export const EMITIR_CERTIFICADO_DONACION_ANUAL = `
  mutation EmitirCertificadoDonacionAnual(
    $ejercicio: Int!
    $nifDonante: String!
    $tipo: String!
  ) {
    emitirCertificadoDonacionAnual(
      ejercicio: $ejercicio
      nifDonante: $nifDonante
      tipo: $tipo
    ) {
      numero
      pdfBase64
    }
  }
`

// Query para obtener conceptos de donación
export const GET_DONACION_CONCEPTOS = `
  query DonacionConceptos {
    donacionConceptos {
      id
      nombre
      descripcion
      activo
    }
  }
`

// Query para obtener remesas
export const GET_REMESAS = `
  query Remesas {
    remesas {
      id
      referencia
      fechaCreacion
      fechaEnvio
      fechaCobro
      importeTotal
      gastos
      numOrdenes
      estado {
        id
        nombre
        color
      }
      archivoSepa
      observaciones
    }
  }
`

// Query para obtener órdenes de cobro
export const GET_ORDENES_COBRO = `
  query OrdenesCobro {
    ordenesCobro {
      id
      importe
      fechaProcesamiento
      remesa {
        id
        referencia
      }
      cuota {
        id
        ejercicio
        miembro {
          id
          nombre
          apellido1
        }
      }
      estado {
        id
        nombre
      }
    }
  }
`

// Query para importes de cuota por año
export const GET_IMPORTES_CUOTA = `
  query ImportesCuotaAnio {
    importesCuotaAnio {
      id
      ejercicio
      importe
      nombreCuota
      observaciones
      tipoMiembro {
        id
        nombre
      }
      activo
    }
  }
`

// Query para estados financieros (catálogos)
export const GET_ESTADOS_CUOTA = `
  query EstadosCuota {
    estadosCuota {
      id
      nombre
      descripcion
      color
      orden
      activo
    }
  }
`

export const GET_ESTADOS_DONACION = `
  query EstadosDonacion {
    estadosDonacion {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const GET_ESTADOS_REMESA = `
  query EstadosRemesa {
    estadosRemesa {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const GET_ESTADOS_ORDEN_COBRO = `
  query EstadosOrdenCobro {
    estadosOrdenCobro {
      id
      nombre
      descripcion
      activo
    }
  }
`

// ─── Flujo 4: Liquidación de remesa ─────────────────────────────────────────

export const GET_REMESA_DETALLE = `
  query RemesaDetalle($id: UUID!) {
    remesas(filter: { id: { eq: $id } }) {
      id
      referencia
      fechaCreacion
      fechaEnvio
      fechaCobro
      importeTotal
      numOrdenes
      tipoRemesa
      seqTipo
      concepto
      remesaOrigenId
      estado { id nombre color }
      ordenes {
        id
        nseq
        importe
        iban
        referenciaMandato
        fechaProcesamiento
        codigoRechazo
        motivoRechazo
        fechaRechazo
        estado { id nombre }
        cuota {
          id
          ejercicio
          miembro { id nombre apellido1 apellido2 }
        }
      }
    }
  }
`

export const PREVISUALIZAR_LIQUIDACION_REMESA = `
  mutation PrevisualizarLiquidacionRemesa(
    $remesaId: UUID!,
    $tipoFichero: String!,
    $ficheroB64: String,
    $fallidosManual: [FallidoBancoInput!]
  ) {
    previsualizarLiquidacionRemesa(
      remesaId: $remesaId,
      tipoFichero: $tipoFichero,
      ficheroB64: $ficheroB64,
      fallidosManual: $fallidosManual
    ) {
      remesaReferencia
      cobradas { ordenId endToEndId importe miembroNombre }
      fallidas { ordenId endToEndId codigo motivo fecha importe }
      noEmparejadas { endToEndId motivo }
      totales { nCobradas nFallidas importeCobrado }
    }
  }
`

export const LIQUIDAR_REMESA = `
  mutation LiquidarRemesa(
    $remesaId: UUID!,
    $cuentaBancariaId: UUID!,
    $fechaLiquidacion: Date!,
    $cobradas: [UUID!]!,
    $fallidas: [FallidoBancoInput!]
  ) {
    liquidarRemesa(
      remesaId: $remesaId,
      cuentaBancariaId: $cuentaBancariaId,
      fechaLiquidacion: $fechaLiquidacion,
      cobradas: $cobradas,
      fallidas: $fallidas
    ) {
      nCobradas
      nFallidas
      importeCobrado
      apunteId
      asientoId
      remesaEstado
    }
  }
`

export const GENERAR_REMESA_REENVIO = `
  mutation GenerarRemesaReenvio($remesaOrigenId: UUID!, $fechaCobro: Date!, $observaciones: String) {
    generarRemesaFallidos(
      remesaOrigenId: $remesaOrigenId,
      fechaCobro: $fechaCobro,
      observaciones: $observaciones
    )
  }
`

// ─── Pantalla 5.4: comunicación a socios con recibo fallido ────────────────

export const GET_RECIBOS_FALLIDOS = `
  query RecibosFallidos {
    recibos(filter: { estado: { eq: "FALLIDO" } }) {
      id
      numeroRecibo
      ejercicio
      importe
      observaciones
      fechaEmision
      fechaAvisoFallido
      miembro { id nombre apellido1 apellido2 email }
    }
  }
`

export const GET_PLANTILLAS_EMAIL_ECONOMICO = `
  query PlantillasEmailEconomico {
    plantillasEmail(filter: {
      activo: { eq: true },
      modulo: { in: ["economico", "tesoreria"] }
    }) {
      id
      codigo
      nombre
      asunto
      variablesDisponibles
    }
  }
`

export const COMUNICAR_RECIBOS_FALLIDOS = `
  mutation ComunicarRecibosFallidos($reciboIds: [UUID!]!, $plantillaEmailId: UUID!) {
    comunicarRecibosFallidos(reciboIds: $reciboIds, plantillaEmailId: $plantillaEmailId)
  }
`

// ─── Flujo 2 — Emisión de recibos ───────────────────────────────────────────

export const GET_RECIBOS = `
  query Recibos {
    recibos {
      id
      numeroRecibo
      ejercicio
      tipo
      concepto
      importe
      importePagado
      estado
      modoCobro
      fechaEmision
      fechaVencimiento
      fechaCobro
      observaciones
      miembro { id nombre apellido1 apellido2 email }
      cuota { id ejercicio }
    }
  }
`

export const EMITIR_RECIBOS_LOTE = `
  mutation EmitirRecibosLote(
    $ejercicio: Int!, $tipo: String, $concepto: String,
    $vinculacionSocioIds: [UUID!], $agrupacionId: UUID, $fechaVencimiento: Date
  ) {
    emitirRecibosLote(
      ejercicio: $ejercicio, tipo: $tipo, concepto: $concepto,
      vinculacionSocioIds: $vinculacionSocioIds, agrupacionId: $agrupacionId, fechaVencimiento: $fechaVencimiento
    )
  }
`

export const MARCAR_RECIBO_COBRADO = `
  mutation MarcarReciboCobrado(
    $reciboId: UUID!, $cuentaBancariaId: UUID, $importeCobrado: Float, $fechaCobro: Date,
    $modoCobro: String, $ordenCobroId: UUID, $referencia: String, $observaciones: String
  ) {
    marcarReciboCobrado(
      reciboId: $reciboId, cuentaBancariaId: $cuentaBancariaId,
      importeCobrado: $importeCobrado, fechaCobro: $fechaCobro,
      modoCobro: $modoCobro, ordenCobroId: $ordenCobroId,
      referencia: $referencia, observaciones: $observaciones
    )
  }
`

export const GET_CUENTAS_BANCARIAS_ACTIVAS = `
  query CuentasBancariasActivas {
    cuentasBancarias {
      id nombre iban activa
      bicSwift bancoNombre titular saldoActual saldoConciliado
    }
  }
`

// Último extracto importado por cuenta — para la tarjeta de info en Conciliación.
export const GET_ULTIMO_EXTRACTO_POR_CUENTA = `
  query UltimoExtractoPorCuenta($cuentaId: UUID!) {
    extractosBancarios(filter: { cuentaBancariaId: { eq: $cuentaId } }) {
      id fecha importe concepto referencia conciliado fechaCreacion
    }
  }
`

// ─── Flujo 7 — Justificantes de gasto ───────────────────────────────────────

// Campos de un justificante de gasto — compartidos entre la query global y la
// filtrada por socio para no duplicar la selección.
const JUSTIFICANTE_FIELDS = `
  id
  numeroJustificante
  ejercicio
  estado
  concepto
  importe
  fechaGasto
  fechaPresentacion
  fechaAceptacion
  fechaAprobacion
  fechaPago
  modoPago
  motivoRechazo
  archivoFactura
  observaciones
  miembro { id nombre apellido1 apellido2 }
  aceptador { id nombre apellido1 apellido2 }
  aprobador { id nombre apellido1 apellido2 }
  presentadoPorTesorero { id nombre apellido1 apellido2 }
  actividad { id nombre responsableId }
  agrupacion { id nombre nombreCorto }
  cuentaBancaria { id nombre }
  cuentaContable { id codigo nombre }
  lineas { id concepto importe fechaGasto observaciones }
  documentos { id nombreArchivo url mimeType tamanoBytes }
`

// Todos los justificantes (vista de gestión — tesorería).
export const GET_JUSTIFICANTES = `
  query Justificantes {
    justificantesGasto { ${JUSTIFICANTE_FIELDS} }
  }
`

// Justificantes de un socio concreto (panel personal — Mis Datos).
export const GET_JUSTIFICANTES_DE_MIEMBRO = `
  query JustificantesMiembro($miembroId: UUID!) {
    justificantesGasto(filter: { miembroId: { eq: $miembroId } }) { ${JUSTIFICANTE_FIELDS} }
  }
`

export const GET_ACTIVIDADES_PARA_GASTO = `
  query ActividadesParaGasto {
    actividades(filter: { eliminado: { eq: false } }) {
      id
      nombre
      caracter
      responsableId
      campaniaId
      esRecurrente
      padreId
      campania { id nombre estado { id codigo nombre } }
    }
  }
`

export const GET_CUENTAS_GASTO = `
  query CuentasGasto {
    cuentasContables(filter: {
      tipo: { eq: "GASTO" }, permiteAsiento: { eq: true }, activa: { eq: true }
    }) {
      id codigo nombre
    }
  }
`

export const GET_MIEMBROS_PARA_GASTO = `
  query MiembrosParaGasto {
    miembros: socios(activo: true) {
      id nombre apellido1 apellido2 numeroDocumento
    }
  }
`

// Miembros elegibles para imputar a una actividad (los del grupo de la actividad
// si es de campaña, o todos los activos si es permanente/sin grupo).
export const GET_MIEMBROS_ELEGIBLES_JUSTIFICANTE = `
  query MiembrosElegiblesJustificante($actividadId: UUID!) {
    miembrosElegiblesParaJustificante(actividadId: $actividadId) {
      id nombre apellido1 apellido2 email
    }
  }
`

// ─── Flujo 8 — Conciliación bancaria ────────────────────────────────────────

export const GET_APUNTES_PARA_CONCILIAR = `
  query ApuntesParaConciliar($cuentaId: UUID!) {
    apuntesCaja(filter: {
      cuentaBancariaId: { eq: $cuentaId },
      conciliado: { eq: false }
    }) {
      id fecha importe tipo concepto referenciaExterna conciliado
    }
  }
`

export const GET_EXTRACTOS_PARA_CONCILIAR = `
  query ExtractosParaConciliar($cuentaId: UUID!) {
    extractosBancarios(filter: {
      cuentaBancariaId: { eq: $cuentaId },
      conciliado: { eq: false }
    }) {
      id fecha importe concepto referencia conciliado
    }
  }
`

export const CONCILIAR_APUNTE_CON_EXTRACTO = `
  mutation ConciliarApunteConExtracto($apunteId: UUID!, $extractoId: UUID!) {
    conciliarApunteConExtracto(apunteId: $apunteId, extractoId: $extractoId)
  }
`

export const ROMPER_CONCILIACION = `
  mutation RomperConciliacion($conciliacionId: UUID!) {
    romperConciliacion(conciliacionId: $conciliacionId)
  }
`

export const IMPORTAR_EXTRACTO_NORMA43 = `
  mutation ImportarExtractoNorma43($cuentaId: UUID!, $archivoB64: String!) {
    importarExtractoNorma43(cuentaId: $cuentaId, archivoB64: $archivoB64)
  }
`

export const IMPORTAR_EXTRACTO_CSV = `
  mutation ImportarExtractoCsv($cuentaId: UUID!, $lineasJson: String!) {
    importarExtractoCsv(cuentaId: $cuentaId, lineasJson: $lineasJson)
  }
`

export const GET_OPENBANKING_ACTIVO = `
  query OpenbankingActivo {
    parametrosOrganizacion { openbankingActivo }
  }
`

// ─── Flujo 9 — Cierre de ejercicio ──────────────────────────────────────────

export const GET_ESTADO_CIERRE = `
  query EstadoCierre($ejercicio: Int!) {
    estadoCierre(ejercicio: $ejercicio) {
      ejercicio todosConfirmados numBorradores balanceCuadra
      totalDebe totalHaber regularizacionHecha cierreHecho aperturaSiguienteHecha
      conciliacionCompleta numApuntesSinConciliar
    }
  }
`

export const GET_BALANCE_PCESFL = `
  query BalancePcesfl($ejercicio: Int!, $fechaFin: Date) {
    balancePcesfl(ejercicio: $ejercicio, fechaFin: $fechaFin) {
      ejercicio
      activoNoCorriente activoCorriente patrimonioNeto pasivoNoCorriente pasivoCorriente
      totalActivo totalPatrimonioNeto totalPasivoNoCorriente totalPasivoCorriente
      totalPasivoYPn diferencia cuadra
    }
  }
`

export const GET_CUENTA_RESULTADOS = `
  query CuentaResultados($ejercicio: Int!, $fechaFin: Date) {
    cuentaResultados(ejercicio: $ejercicio, fechaFin: $fechaFin) {
      ejercicio
      ingresosActividadPropia gastosActividadPropia excedenteActividadPropia
      ingresosMercantil gastosMercantil excedenteMercantil
      ingresosFinancieros gastosFinancieros resultadoFinanciero
      excedenteAntesImpuestos impuestoSobreBeneficios excedenteEjercicio
    }
  }
`

export const GET_LIBRO_DIARIO_CSV = `
  query LibroDiarioCsv($ejercicio: Int!, $organizacionNombre: String) {
    libroDiarioCsv(ejercicio: $ejercicio, organizacionNombre: $organizacionNombre)
  }
`

export const GENERAR_ASIENTO_REGULARIZACION = `
  mutation GenerarAsientoRegularizacion($ejercicio: Int!) {
    generarAsientoRegularizacion(ejercicio: $ejercicio)
  }
`

export const GENERAR_ASIENTO_CIERRE = `
  mutation GenerarAsientoCierre($ejercicio: Int!) {
    generarAsientoCierre(ejercicio: $ejercicio)
  }
`

export const GENERAR_ASIENTO_APERTURA = `
  mutation GenerarAsientoApertura($ejercicioNuevo: Int!) {
    generarAsientoApertura(ejercicioNuevo: $ejercicioNuevo)
  }
`

// ─── Flujo 10 — Cuentas Anuales ──────────────────────────────────────────────

export const GET_CUENTAS_ANUALES = `
  query CuentasAnuales {
    cuentasAnuales {
      id ejercicio estado excedente
      fechaAprobacion aprobadoPorId actaReferencia
      fechaDeposito archivoAcuseRecibo
      memoria balancePcesfl cuentaResultados observaciones
    }
  }
`

export const GET_CCAA_POR_EJERCICIO = `
  query CuentasAnualesPorEjercicio($ejercicio: Int!) {
    cuentasAnualesPorEjercicio(ejercicio: $ejercicio) {
      id ejercicio estado excedente
      fechaAprobacion aprobadoPorId actaReferencia
      fechaDeposito archivoAcuseRecibo
      memoria balancePcesfl cuentaResultados observaciones
    }
  }
`

export const GENERAR_CCAA = `
  mutation GenerarCuentasAnuales($ejercicio: Int!) {
    generarCuentasAnuales(ejercicio: $ejercicio)
  }
`

export const ACTUALIZAR_MEMORIA_CCAA = `
  mutation ActualizarMemoriaCcaa($ccaaId: UUID!, $apartado: String!, $texto: String!) {
    actualizarMemoriaCcaa(ccaaId: $ccaaId, apartado: $apartado, texto: $texto)
  }
`

export const APROBAR_CCAA = `
  mutation AprobarCuentasAnuales(
    $ccaaId: UUID!, $aprobadoPorId: UUID!,
    $actaReferencia: String!, $fechaAprobacion: Date
  ) {
    aprobarCuentasAnuales(
      ccaaId: $ccaaId, aprobadoPorId: $aprobadoPorId,
      actaReferencia: $actaReferencia, fechaAprobacion: $fechaAprobacion
    )
  }
`

export const MARCAR_CCAA_DEPOSITADAS = `
  mutation MarcarCcaaDepositadas(
    $ccaaId: UUID!, $fechaDeposito: Date, $archivoAcuseRecibo: String
  ) {
    marcarCcaaDepositadas(
      ccaaId: $ccaaId, fechaDeposito: $fechaDeposito, archivoAcuseRecibo: $archivoAcuseRecibo
    )
  }
`

export const REABRIR_CCAA = `
  mutation ReabrirCuentasAnuales($ccaaId: UUID!, $motivo: String!) {
    reabrirCuentasAnuales(ccaaId: $ccaaId, motivo: $motivo)
  }
`

export const EXPORTAR_CCAA_PDF = `
  mutation ExportarCcaaPdf($ccaaId: UUID!, $organizacionNombre: String) {
    exportarCcaaPdf(ccaaId: $ccaaId, organizacionNombre: $organizacionNombre)
  }
`

// ─── Flujo 11 — Modelo 182 ──────────────────────────────────────────────────

export const GET_AGREGADO_182 = `
  query AgregadoModelo182($ejercicio: Int!) {
    agregadoModelo182(ejercicio: $ejercicio) {
      ejercicio nIncluidos nExcluidos importeTotal
      incluidos { nif nombre tipo clave importe nDonaciones }
      excluidos { donacionId fecha importe nif motivo }
    }
  }
`

export const GET_PRESENTACIONES_182 = `
  query PresentacionesModelo182 {
    presentacionesModelo182 {
      id ejercicio fechaEnvio codigoAeat nDonantes importeTotal archivoAcuse observaciones
    }
  }
`

export const DESCARGAR_FICHERO_AEAT_182 = `
  mutation DescargarFicheroAeat182(
    $ejercicio: Int!, $declaranteNif: String!, $declaranteNombre: String!
  ) {
    descargarFicheroAeat182(
      ejercicio: $ejercicio, declaranteNif: $declaranteNif, declaranteNombre: $declaranteNombre
    )
  }
`

export const DESCARGAR_PDF_RESUMEN_182 = `
  mutation DescargarPdfResumen182($ejercicio: Int!, $organizacionNombre: String) {
    descargarPdfResumen182(ejercicio: $ejercicio, organizacionNombre: $organizacionNombre)
  }
`

export const REGISTRAR_PRESENTACION_182 = `
  mutation RegistrarPresentacion182(
    $ejercicio: Int!, $fechaEnvio: Date!,
    $codigoAeat: String, $archivoAcuse: String, $observaciones: String
  ) {
    registrarPresentacion182(
      ejercicio: $ejercicio, fechaEnvio: $fechaEnvio,
      codigoAeat: $codigoAeat, archivoAcuse: $archivoAcuse, observaciones: $observaciones
    )
  }
`

export const PRESENTAR_JUSTIFICANTE = `
  mutation PresentarJustificante(
    $miembroId: UUID!, $actividadId: UUID!,
    $lineas: [LineaJustificanteInput!]!,
    $partidaActividadId: UUID, $agrupacionId: UUID,
    $observaciones: String, $ejercicio: Int,
    $presentadoPorTesoreroId: UUID
  ) {
    presentarJustificanteGasto(
      miembroId: $miembroId, actividadId: $actividadId,
      lineas: $lineas,
      partidaActividadId: $partidaActividadId, agrupacionId: $agrupacionId,
      observaciones: $observaciones, ejercicio: $ejercicio,
      presentadoPorTesoreroId: $presentadoPorTesoreroId
    )
  }
`

export const ACEPTAR_JUSTIFICANTE = `
  mutation AceptarJustificante($justificanteId: UUID!, $aceptadorId: UUID!) {
    aceptarJustificanteGasto(justificanteId: $justificanteId, aceptadorId: $aceptadorId)
  }
`

export const APROBAR_JUSTIFICANTE = `
  mutation AprobarJustificante($justificanteId: UUID!, $aprobadorId: UUID!) {
    aprobarJustificanteGasto(justificanteId: $justificanteId, aprobadorId: $aprobadorId)
  }
`

export const RECHAZAR_JUSTIFICANTE = `
  mutation RechazarJustificante($justificanteId: UUID!, $aprobadorId: UUID!, $motivo: String!) {
    rechazarJustificanteGasto(justificanteId: $justificanteId, aprobadorId: $aprobadorId, motivo: $motivo)
  }
`

export const PAGAR_JUSTIFICANTE = `
  mutation PagarJustificante(
    $justificanteId: UUID!, $cuentaBancariaId: UUID!,
    $modoPago: String, $fechaPago: Date, $referencia: String,
    $cuentaContableId: UUID
  ) {
    pagarJustificanteGasto(
      justificanteId: $justificanteId, cuentaBancariaId: $cuentaBancariaId,
      modoPago: $modoPago, fechaPago: $fechaPago, referencia: $referencia,
      cuentaContableId: $cuentaContableId
    )
  }
`

export const ANULAR_JUSTIFICANTE = `
  mutation AnularJustificante($justificanteId: UUID!, $motivo: String) {
    anularJustificanteGasto(justificanteId: $justificanteId, motivo: $motivo)
  }
`

export const ANULAR_RECIBO = `
  mutation AnularRecibo($reciboId: UUID!, $motivo: String) {
    anularRecibo(reciboId: $reciboId, motivo: $motivo)
  }
`

export const DESCARGAR_RECIBO_PDF = `
  mutation DescargarReciboPdf($reciboId: UUID!) {
    descargarReciboPdf(reciboId: $reciboId)
  }
`

export const ENVIAR_RECIBO_EMAIL = `
  mutation EnviarReciboEmail($reciboId: UUID!, $plantillaEmailId: UUID!) {
    enviarReciboEmail(reciboId: $reciboId, plantillaEmailId: $plantillaEmailId)
  }
`

// ─── Flujo 1 — Establecimiento de cuotas del ejercicio ──────────────────────

export const GET_MOTIVOS_REDUCCION = `
  query MotivosReduccion {
    motivosReduccionCuota {
      id
      codigo
      nombre
      descripcion
      porcentajeReduccion
      excluyeCuota
      orden
      activo
    }
  }
`

export const CREATE_MOTIVO_REDUCCION = `
  mutation CrearMotivoReduccion(
    $codigo: String!, $nombre: String!, $porcentajeReduccion: Float!,
    $descripcion: String, $orden: Int, $activo: Boolean
  ) {
    crearMotivoReduccion(
      codigo: $codigo, nombre: $nombre, porcentajeReduccion: $porcentajeReduccion,
      descripcion: $descripcion, orden: $orden, activo: $activo
    )
  }
`

export const UPDATE_MOTIVO_REDUCCION = `
  mutation ActualizarMotivoReduccion(
    $id: UUID!, $codigo: String, $nombre: String, $porcentajeReduccion: Float,
    $descripcion: String, $orden: Int, $activo: Boolean
  ) {
    actualizarMotivoReduccion(
      id: $id, codigo: $codigo, nombre: $nombre, porcentajeReduccion: $porcentajeReduccion,
      descripcion: $descripcion, orden: $orden, activo: $activo
    )
  }
`

export const MOTIVO_TIENE_RECIBOS = `
  query MotivoTieneRecibos($motivoId: UUID!) {
    motivoTieneRecibos(motivoId: $motivoId)
  }
`

export const GET_CONFIG_CUOTA_EJERCICIO = `
  query ConfigCuotaEjercicio($ejercicio: Int!) {
    importesCuotaAnio(filter: {
      ejercicio: { eq: $ejercicio },
      codigoCuota: { eq: "BASE" }
    }) {
      id ejercicio importe nombreCuota observaciones activo
    }
  }
`

export const CONFIGURAR_CUOTA_EJERCICIO = `
  mutation ConfigurarCuotaEjercicio(
    $ejercicio: Int!,
    $importeBase: Float!,
    $clonarDe: Int,
    $observaciones: String
  ) {
    configurarCuotaEjercicio(
      ejercicio: $ejercicio,
      importeBase: $importeBase,
      clonarDe: $clonarDe,
      observaciones: $observaciones
    )
  }
`

export const ELIMINAR_CUOTA_EJERCICIO = `
  mutation EliminarCuotaEjercicio($ejercicio: Int!) {
    eliminarCuotaEjercicio(ejercicio: $ejercicio)
  }
`

export const GET_HISTORIAL_CUOTAS = `
  query HistorialCuotas {
    importesCuotaAnio(filter: { codigoCuota: { eq: "BASE" } }) {
      id ejercicio importe nombreCuota observaciones activo
    }
  }
`

export const PREVISUALIZAR_GENERACION_CUOTAS = `
  mutation PrevisualizarGeneracionCuotas($ejercicio: Int!) {
    previsualizarGeneracionCuotas(ejercicio: $ejercicio) {
      ejercicio
      importeBase
      nGenerables
      nExcluidos
      nExistentes
      totalEsperado
      desglose {
        tipoMiembroId
        tipoMiembroNombre
        motivoCodigo
        motivoPorcentaje
        nMiembros
        importeUnitario
        total
        excluido
      }
    }
  }
`

export const GENERAR_CUOTAS_INDIVIDUALES = `
  mutation GenerarCuotasIndividuales($ejercicio: Int!, $fechaVencimiento: Date) {
    generarCuotasIndividuales(ejercicio: $ejercicio, fechaVencimiento: $fechaVencimiento) {
      ejercicio
      nCreadas
      nOmitidasExistentes
      nOmitidasExcluidas
      totalImporte
    }
  }
`
