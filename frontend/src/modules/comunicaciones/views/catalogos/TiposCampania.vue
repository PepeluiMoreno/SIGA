<template>
  <CatalogoGenerico
    titulo="Tipos de campaña"
    subtitulo="Clasificación de las campañas de la organización"
    nombre-singular="Tipo de campaña"
    icono="📣"
    query-name="tiposCampania"
    :query-string="GET_TIPOS_CAMPANIA"
    :mutation-create="CREATE_TIPO_CAMPANIA"
    :mutation-update="UPDATE_TIPO_CAMPANIA"
    :mutation-delete="DELETE_TIPO_CAMPANIA"
    :columnas="columnas"
    :campos="campos"
  />
</template>

<script setup>
import CatalogoGenerico from '@/components/parametrizacion/CatalogoGenerico.vue'
import {
  GET_TIPOS_CAMPANIA,
  CREATE_TIPO_CAMPANIA,
  UPDATE_TIPO_CAMPANIA,
  DELETE_TIPO_CAMPANIA,
} from '@/modules/comunicaciones/graphql/queries.js'

const columnas = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'activo', label: 'Activo', type: 'checkbox', centered: true },
]

const campos = [
  { name: 'nombre', label: 'Nombre', type: 'text', required: true, maxLength: 100 },
  { name: 'activo', label: 'Activo', type: 'checkbox', default: true },
]
</script>
