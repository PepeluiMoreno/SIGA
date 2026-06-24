import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGraphQL } from './useGraphQL'
import { useConfirm } from './useConfirm'
import {
  GET_MIEMBRO_BY_ID,
  GET_AGRUPACIONES,
  GET_ESTADOS_MIEMBRO,
  GET_MOTIVOS_BAJA,
  GET_TIPOS_MIEMBRO,
  GET_FORMAS_PAGO,
  CREATE_MIEMBRO,
  UPDATE_MIEMBRO,
} from '@/graphql/queries/miembros.js'
import { GET_PAISES, GET_PROVINCIAS, GET_NIVELES_ESTUDIOS, GET_NIVELES_HABILIDAD } from '@/graphql/queries/catalogos.js'
import { GET_MOTIVOS_REDUCCION } from '@/graphql/queries/economico.js'

export function useMiembro() {
  const router = useRouter()
  const { query, mutation } = useGraphQL()
  const loading = ref(false)
  const error = ref(null)
  const lastLoadedId = ref(null)
  const isCreateMode = ref(false)
  const catalogos = ref({
    tiposMiembro: [],
    estadosMiembro: [],
    motivosBaja: [],
    agrupaciones: [],
    paises: [],
    provincias: [],
    formasPago: [],
    nivelesEstudios: [],
    nivelesHabilidad: [],
    motivosReduccion: [],
  })
  const miembro = ref(createEmptyMiembro())

  const loadCatalogos = async () => {
    try {
      const alpha = (a, b) => a.nombre.localeCompare(b.nombre, 'es')

      const tiposData = await query(GET_TIPOS_MIEMBRO)
      catalogos.value.tiposMiembro = (tiposData?.tiposMiembro || []).sort(alpha)

      const estadosData = await query(GET_ESTADOS_MIEMBRO)
      catalogos.value.estadosMiembro = (estadosData?.estadosMiembro || []).sort(alpha)

      const motivosData = await query(GET_MOTIVOS_BAJA)
      catalogos.value.motivosBaja = (motivosData?.motivosBaja || []).sort(alpha)

      const agrupacionesData = await query(GET_AGRUPACIONES)
      catalogos.value.agrupaciones = agrupacionesData?.unidadesOrganizativas || []

      const paisesData = await query(GET_PAISES)
      const paises = (paisesData?.paises || []).filter(p => p.activo)
      const espana = paises.find(p => p.codigo === 'ES')
      const resto = paises.filter(p => p.codigo !== 'ES').sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
      catalogos.value.paises = espana ? [espana, ...resto] : resto

      const provinciasData = await query(GET_PROVINCIAS)
      catalogos.value.provincias = (provinciasData?.provincias || []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))

      const formasPagoData = await query(GET_FORMAS_PAGO)
      catalogos.value.formasPago = formasPagoData?.formasPago || []

      const nivelesEstData = await query(GET_NIVELES_ESTUDIOS)
      catalogos.value.nivelesEstudios = (nivelesEstData?.nivelesEstudios || []).sort((a, b) => a.orden - b.orden)

      const nivelesHabData = await query(GET_NIVELES_HABILIDAD)
      catalogos.value.nivelesHabilidad = (nivelesHabData?.nivelesHabilidad || []).sort((a, b) => a.orden - b.orden)

      const motivosRedData = await query(GET_MOTIVOS_REDUCCION)
      catalogos.value.motivosReduccion = (motivosRedData?.motivosReduccionCuota || [])
        .filter(m => m.activo).sort((a, b) => (a.orden ?? 0) - (b.orden ?? 0))
    } catch (err) {
      console.error('Error loading member catalogs:', err)
      error.value = err.message || 'Error al cargar catálogos de militancia'
    }
  }

  const fetchMiembro = async (id) => {
    loading.value = true
    error.value = null
    try {
      const data = await query(GET_MIEMBRO_BY_ID, { id })
      if (data?.miembros && data.miembros.length > 0) {
        miembro.value = data.miembros[0]
        lastLoadedId.value = id
      } else {
        error.value = 'Miembro no encontrado'
      }
    } catch (err) {
      console.error('Error fetching miembro:', err)
      error.value = err.message || 'Error al cargar miembro'
    } finally {
      loading.value = false
    }
  }

  const saveMiembro = async () => {
    loading.value = true
    error.value = null
    try {
      if (isCreateMode.value) {
        const data = buildCreatePayload(miembro.value)
        const result = await mutation(CREATE_MIEMBRO, { data })
        return result?.crearMiembro
      } else {
        const data = buildUpdatePayload(miembro.value)
        await mutation(UPDATE_MIEMBRO, { data })
        if (lastLoadedId.value) {
          await fetchMiembro(lastLoadedId.value)
        }
      }
    } catch (err) {
      console.error('Error saving miembro:', err)
      error.value = err.message || 'Error al guardar miembro'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createMiembro = async () => {
    loading.value = true
    error.value = null
    try {
      const data = buildCreatePayload(miembro.value)
      const result = await mutation(CREATE_MIEMBRO, { data })
      return result?.crearMiembro
    } catch (err) {
      console.error('Error creating miembro:', err)
      error.value = err.message || 'Error al crear miembro'
      throw err
    } finally {
      loading.value = false
    }
  }

  const resetMiembro = () => {
    miembro.value = createEmptyMiembro()
    isCreateMode.value = true
    lastLoadedId.value = null
    error.value = null
  }

  const ELIMINAR_MIEMBRO = `
    mutation EliminarMiembro($id: UUID!) {
      eliminarContactos(filter: { id: { eq: $id } }) { id }
    }
  `

  const deleteMiembro = async (id) => {
    const ok = await useConfirm()({
      titulo: 'Eliminar miembro',
      mensaje: '¿Estás seguro de que quieres eliminar este miembro? Esta acción no se puede deshacer.',
      variante: 'critica',
      etiquetaConfirmar: 'Eliminar',
    })
    if (!ok) return

    loading.value = true
    try {
      await mutation(ELIMINAR_MIEMBRO, { id })
      router.push('/miembros')
    } catch (err) {
      console.error('Error deleting miembro:', err)
      error.value = err.message || 'Error al eliminar miembro'
    } finally {
      loading.value = false
    }
  }

  const nombreCompleto = computed(() => {
    const { nombre, apellido1, apellido2 } = miembro.value
    return [nombre, apellido1, apellido2].filter(Boolean).join(' ')
  })

  return {
    miembro,
    catalogos,
    loading,
    error,
    isCreateMode,
    nombreCompleto,
    loadCatalogos,
    fetchMiembro,
    saveMiembro,
    createMiembro,
    resetMiembro,
    deleteMiembro
  }
}

function createEmptyMiembro() {
  const hoy = new Date().toISOString().slice(0, 10)
  return {
    id: null,
    tipoMiembroId: null,
    motivoReduccionId: null,
    estadoId: null,
    motivoBajaId: null,
    agrupacionId: null,
    paisDocumentoId: null,
    paisDomicilioId: null,
    paisNacimientoId: null,
    provinciaId: null,
    nombre: '',
    apellido1: '',
    apellido2: '',
    sexo: '',
    fechaNacimiento: null,
    email: '',
    telefono: '',
    telefono2: '',
    tipoDocumento: '',
    numeroDocumento: '',
    tipoMiembro: null,
    estado: null,
    motivoBajaRel: null,
    motivoBajaTexto: '',
    agrupacion: null,
    fechaAlta: hoy,
    fechaBaja: null,
    direccion: '',
    codigoPostal: '',
    localidad: '',
    provincia: null,
    paisDomicilio: null,
    iban: '',
    swiftBic: '',
    referenciaPago: '',
    formaPagoId: null,
    esSocioHonor: false,
    esVoluntario: false,
    disponibilidad: '',
    horasDisponiblesSemana: null,
    profesion: '',
    nivelEstudiosId: null,
    intereses: '',
    observaciones: '',
    experienciaVoluntariado: '',
    observacionesVoluntariado: '',
    puedeConducir: false,
    vehiculoPropio: false,
    disponibilidadViajar: false,
    solicitaSupresionDatos: false,
    fechaSolicitudSupresion: null,
    fechaLimiteRetencion: null,
    datosAnonimizados: false,
    fechaAnonimizacion: null,
    activo: true,
  }
}

function nullIfEmpty(value) {
  return value === '' || value === undefined ? null : value
}

function normalizeText(value) {
  if (value === undefined || value === null) return null
  const trimmed = String(value).trim()
  return trimmed === '' ? null : trimmed
}

function buildCreatePayload(miembro) {
  return {
    nombre: miembro.nombre?.trim() || '',
    apellido1: miembro.apellido1?.trim() || '',
    apellido2: normalizeText(miembro.apellido2),
    sexo: normalizeText(miembro.sexo),
    fechaNacimiento: nullIfEmpty(miembro.fechaNacimiento),
    tipoMiembroId: miembro.tipoMiembroId,
    motivoReduccionId: nullIfEmpty(miembro.motivoReduccionId),
    estadoId: miembro.estadoId,
    tipoDocumento: normalizeText(miembro.tipoDocumento),
    numeroDocumento: normalizeText(miembro.numeroDocumento),
    paisDocumentoId: nullIfEmpty(miembro.paisDocumentoId),
    paisNacimientoId: nullIfEmpty(miembro.paisNacimientoId),
    direccion: normalizeText(miembro.direccion),
    codigoPostal: normalizeText(miembro.codigoPostal),
    localidad: normalizeText(miembro.localidad),
    provinciaId: nullIfEmpty(miembro.provinciaId),
    paisDomicilioId: nullIfEmpty(miembro.paisDomicilioId),
    telefono: normalizeText(miembro.telefono),
    telefono2: normalizeText(miembro.telefono2),
    email: normalizeText(miembro.email),
    agrupacionId: nullIfEmpty(miembro.agrupacionId),

    iban: normalizeText(miembro.iban),
    swiftBic: normalizeText(miembro.swiftBic),
    referenciaPago: normalizeText(miembro.referenciaPago),
    formaPagoId: nullIfEmpty(miembro.formaPagoId),
    esSocioHonor: Boolean(miembro.esSocioHonor),
    fechaAlta: nullIfEmpty(miembro.fechaAlta),
    fechaBaja: nullIfEmpty(miembro.fechaBaja),
    motivoBajaId: nullIfEmpty(miembro.motivoBajaId),
    motivoBajaTexto: normalizeText(miembro.motivoBajaTexto),
    observaciones: normalizeText(miembro.observaciones),
    solicitaSupresionDatos: Boolean(miembro.solicitaSupresionDatos),
    fechaSolicitudSupresion: nullIfEmpty(miembro.fechaSolicitudSupresion),
    fechaLimiteRetencion: nullIfEmpty(miembro.fechaLimiteRetencion),
    datosAnonimizados: Boolean(miembro.datosAnonimizados),
    fechaAnonimizacion: nullIfEmpty(miembro.fechaAnonimizacion),
    activo: Boolean(miembro.activo),
    esVoluntario: Boolean(miembro.esVoluntario),
    disponibilidad: normalizeText(miembro.disponibilidad),
    horasDisponiblesSemana: miembro.horasDisponiblesSemana === '' ? null : miembro.horasDisponiblesSemana,
    profesion: normalizeText(miembro.profesion),
    nivelEstudiosId: nullIfEmpty(miembro.nivelEstudiosId),
    experienciaVoluntariado: normalizeText(miembro.experienciaVoluntariado),
    intereses: normalizeText(miembro.intereses),
    observacionesVoluntariado: normalizeText(miembro.observacionesVoluntariado),
    puedeConducir: Boolean(miembro.puedeConducir),
    vehiculoPropio: Boolean(miembro.vehiculoPropio),
    disponibilidadViajar: Boolean(miembro.disponibilidadViajar),
  }
}

function buildUpdatePayload(miembro) {
  return {
    id: miembro.id,
    nombre: miembro.nombre?.trim() || '',
    apellido1: miembro.apellido1?.trim() || '',
    apellido2: normalizeText(miembro.apellido2),
    sexo: normalizeText(miembro.sexo),
    fechaNacimiento: nullIfEmpty(miembro.fechaNacimiento),
    tipoMiembroId: miembro.tipoMiembroId,
    motivoReduccionId: nullIfEmpty(miembro.motivoReduccionId),
    estadoId: miembro.estadoId,
    tipoDocumento: normalizeText(miembro.tipoDocumento),
    numeroDocumento: normalizeText(miembro.numeroDocumento),
    paisDocumentoId: nullIfEmpty(miembro.paisDocumentoId),
    paisNacimientoId: nullIfEmpty(miembro.paisNacimientoId),
    direccion: normalizeText(miembro.direccion),
    codigoPostal: normalizeText(miembro.codigoPostal),
    localidad: normalizeText(miembro.localidad),
    provinciaId: nullIfEmpty(miembro.provinciaId),
    paisDomicilioId: nullIfEmpty(miembro.paisDomicilioId),
    telefono: normalizeText(miembro.telefono),
    telefono2: normalizeText(miembro.telefono2),
    email: normalizeText(miembro.email),
    agrupacionId: nullIfEmpty(miembro.agrupacionId),

    iban: normalizeText(miembro.iban),
    swiftBic: normalizeText(miembro.swiftBic),
    referenciaPago: normalizeText(miembro.referenciaPago),
    formaPagoId: nullIfEmpty(miembro.formaPagoId),
    esSocioHonor: Boolean(miembro.esSocioHonor),
    fechaAlta: nullIfEmpty(miembro.fechaAlta),
    fechaBaja: nullIfEmpty(miembro.fechaBaja),
    motivoBajaId: nullIfEmpty(miembro.motivoBajaId),
    motivoBajaTexto: normalizeText(miembro.motivoBajaTexto),
    observaciones: normalizeText(miembro.observaciones),
    solicitaSupresionDatos: Boolean(miembro.solicitaSupresionDatos),
    fechaSolicitudSupresion: nullIfEmpty(miembro.fechaSolicitudSupresion),
    fechaLimiteRetencion: nullIfEmpty(miembro.fechaLimiteRetencion),
    datosAnonimizados: Boolean(miembro.datosAnonimizados),
    fechaAnonimizacion: nullIfEmpty(miembro.fechaAnonimizacion),
    activo: Boolean(miembro.activo),
    esVoluntario: Boolean(miembro.esVoluntario),
    disponibilidad: normalizeText(miembro.disponibilidad),
    horasDisponiblesSemana: miembro.horasDisponiblesSemana === '' ? null : miembro.horasDisponiblesSemana,
    profesion: normalizeText(miembro.profesion),
    nivelEstudiosId: nullIfEmpty(miembro.nivelEstudiosId),
    experienciaVoluntariado: normalizeText(miembro.experienciaVoluntariado),
    intereses: normalizeText(miembro.intereses),
    observacionesVoluntariado: normalizeText(miembro.observacionesVoluntariado),
    puedeConducir: Boolean(miembro.puedeConducir),
    vehiculoPropio: Boolean(miembro.vehiculoPropio),
    disponibilidadViajar: Boolean(miembro.disponibilidadViajar),
  }
}
