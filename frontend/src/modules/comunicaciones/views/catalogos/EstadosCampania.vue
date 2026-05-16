<template>
  <CatalogoGenerico
    titulo="Estados de campaña"
    subtitulo="Define el ciclo de vida y las transiciones de estado de las campañas"
    nombre-singular="Estado de campaña"
    icono="🔄"
    query-name="estadosCampania"
    :query-string="GET_ESTADOS_CAMPANIA"
    :mutation-create="CREATE_ESTADO_CAMPANIA"
    :mutation-update="UPDATE_ESTADO_CAMPANIA"
    :columnas="columnas"
    :campos="campos"
  />
</template>

<script setup>
import CatalogoGenerico from '@/components/parametrizacion/CatalogoGenerico.vue'
import {
  GET_ESTADOS_CAMPANIA,
  CREATE_ESTADO_CAMPANIA,
  UPDATE_ESTADO_CAMPANIA,
} from '@/modules/comunicaciones/graphql/queries.js'

const columnas = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'color', label: 'Color' },
  { key: 'orden', label: 'Orden', centered: true },
  { key: 'activo', label: 'Activo', type: 'checkbox', centered: true },
]

const campos = [
  { name: 'nombre', label: 'Nombre', type: 'text', required: true, maxLength: 100 },
  { name: 'color', label: 'Color (hex)', type: 'text', maxLength: 20 },
  { name: 'orden', label: 'Orden', type: 'number', default: 0 },
  { name: 'activo', label: 'Activo', type: 'checkbox', default: true },
]
</script>
