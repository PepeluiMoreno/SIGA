<template>
  <CatalogoGenerico
    titulo="Tipos de meta"
    subtitulo="Objetivos medibles que se pueden asignar a las campañas"
    nombre-singular="Tipo de meta"
    icono="🎯"
    query-name="tiposMetaCampania"
    :query-string="GET_ALL_TIPOS_META"
    :mutation-create="CREATE_TIPO_META"
    :mutation-update="UPDATE_TIPO_META"
    :mutation-delete="DELETE_TIPO_META"
    :columnas="columnas"
    :campos="campos"
  />
</template>

<script setup>
import CatalogoGenerico from '@/components/parametrizacion/CatalogoGenerico.vue'
import {
  GET_ALL_TIPOS_META,
  CREATE_TIPO_META,
  UPDATE_TIPO_META,
  DELETE_TIPO_META,
} from '@/modules/comunicaciones/graphql/queries.js'

const columnas = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'descripcion', label: 'Descripción', type: 'multiline' },
  { key: 'unidadMedida', label: 'Unidad de medida' },
  { key: 'activo', label: 'Activo', type: 'checkbox', centered: true },
]

const campos = [
  { name: 'nombre', label: 'Nombre', type: 'text', required: true, maxLength: 100 },
  { name: 'descripcion', label: 'Descripción', type: 'textarea' },
  { name: 'unidadMedida', label: 'Unidad de medida', type: 'text', required: true, maxLength: 30, placeholder: 'ej: €, personas, firmas' },
  { name: 'activo', label: 'Activo', type: 'checkbox', default: true },
]
</script>
