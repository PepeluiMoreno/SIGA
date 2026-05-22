<template>
  <CatalogoGenerico
    titulo="Tipos de miembro"
    subtitulo="Configuración de tipos de miembro"
    nombre-singular="Tipo de miembro"
    icono="👤"
    query-name="tiposMiembro"
    :query-string="GET_TIPOS_MIEMBRO_CON_MOTIVO"
    :mutation-create="CREATE_TIPO_MIEMBRO"
    :mutation-update="UPDATE_TIPO_MIEMBRO"
    :mutation-delete="DELETE_TIPO_MIEMBRO"
    :columnas="columnas"
    :campos="campos"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CatalogoGenerico from '@/components/parametrizacion/CatalogoGenerico.vue'
import { CREATE_TIPO_MIEMBRO, UPDATE_TIPO_MIEMBRO, DELETE_TIPO_MIEMBRO } from '@/graphql/queries/catalogos.js'
import { GET_MOTIVOS_REDUCCION } from '@/graphql/queries/economico.js'
import { useGraphQL } from '@/composables/useGraphQL'

// Query ampliada: incluye motivo_reduccion (Flujo 1, D1.2)
const GET_TIPOS_MIEMBRO_CON_MOTIVO = `
  query TiposMiembroConMotivo {
    tiposMiembro {
      id
      nombre
      descripcion
      requiereCuota
      puedeVotar
      orden
      activo
      motivoReduccionId
      motivoReduccion { id codigo nombre porcentajeReduccion }
    }
  }
`

const { query } = useGraphQL()

// Carga inicial de los motivos para alimentar el selector
const motivosOptions = ref([{ value: '', label: '— Sin reducción (paga cuota base) —' }])

const cargarMotivos = async () => {
  const data = await query(GET_MOTIVOS_REDUCCION)
  const opts = (data.motivosReduccionCuota || [])
    .filter(m => m.activo)
    .sort((a, b) => a.orden - b.orden)
    .map(m => ({
      value: m.id,
      label: `${m.codigo} — ${m.nombre} (-${m.porcentajeReduccion}%)${m.porcentajeReduccion >= 100 ? ' [excluido]' : ''}`,
    }))
  motivosOptions.value = [{ value: null, label: '— Sin reducción (paga cuota base) —' }, ...opts]
  // Mutar la entrada del campo `motivoReduccionId` para que CatalogoGenerico la vea
  campoMotivo.options = motivosOptions.value
}

const columnas = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'descripcion', label: 'Descripción', type: 'multiline' },
  { key: 'requiereCuota', label: 'Requiere Cuota', type: 'checkbox' },
  { key: 'puedeVotar', label: 'Puede Votar', type: 'checkbox' },
  // Mostramos el motivo asociado en la tabla
  {
    key: 'motivoReduccion',
    label: 'Motivo reducción',
    formatter: (v) => v ? `${v.codigo} (-${v.porcentajeReduccion}%)` : '—',
  },
  { key: 'activo', label: 'En uso', type: 'checkbox' },
]

// Definimos el campo motivo como objeto reactivo para mutar `options` tras la carga async
const campoMotivo = {
  name: 'motivoReduccionId',
  label: 'Motivo de reducción por defecto (Flujo 1 — D1.2)',
  type: 'select',
  options: motivosOptions.value,
}

const campos = [
  { name: 'nombre', label: 'Nombre', type: 'text', required: true, maxLength: 100 },
  { name: 'descripcion', label: 'Descripción', type: 'textarea' },
  { name: 'requiereCuota', label: 'Requiere Cuota', type: 'checkbox', default: true },
  { name: 'puedeVotar', label: 'Puede Votar', type: 'checkbox', default: false },
  campoMotivo,
  { name: 'activo', label: 'En uso', type: 'checkbox', default: true },
]

onMounted(cargarMotivos)
</script>
