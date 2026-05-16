<template>
  <CatalogoGenerico
    titulo="Canales de difusión"
    subtitulo="Vías a través de las cuales se comunican y difunden las campañas"
    nombre-singular="Canal de difusión"
    icono="📡"
    query-name="tiposCanalDifusion"
    :query-string="GET_ALL_TIPOS_CANAL"
    :mutation-create="CREATE_TIPO_CANAL"
    :mutation-update="UPDATE_TIPO_CANAL"
    :mutation-delete="DELETE_TIPO_CANAL"
    :columnas="columnas"
    :campos="campos"
  />
</template>

<script setup>
import CatalogoGenerico from '@/components/parametrizacion/CatalogoGenerico.vue'
import {
  GET_ALL_TIPOS_CANAL,
  CREATE_TIPO_CANAL,
  UPDATE_TIPO_CANAL,
  DELETE_TIPO_CANAL,
} from '@/modules/comunicaciones/graphql/queries.js'

const columnas = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'descripcion', label: 'Descripción', type: 'multiline' },
  { key: 'activo', label: 'Activo', type: 'checkbox', centered: true },
]

const campos = [
  { name: 'nombre', label: 'Nombre', type: 'text', required: true, maxLength: 100 },
  { name: 'descripcion', label: 'Descripción', type: 'textarea' },
  { name: 'activo', label: 'Activo', type: 'checkbox', default: true },
]
</script>
