<template>
  <CatalogoGenerico
    titulo="Motivos de Traslado"
    subtitulo="Razones para trasladar un socio de agrupación"
    nombre-singular="Motivo de Traslado"
    icono="🔀"
    query-name="motivosTraslado"
    :query-string="GET_MOTIVOS_TRASLADO"
    :mutation-create="CREATE_MOTIVO_TRASLADO"
    :mutation-update="UPDATE_MOTIVO_TRASLADO"
    :mutation-delete="DELETE_MOTIVO_TRASLADO"
    :columnas="columnas"
    :campos="campos"
  />
</template>

<script setup>
import CatalogoGenerico from '@/components/parametrizacion/CatalogoGenerico.vue'
import {
  GET_MOTIVOS_TRASLADO, CREATE_MOTIVO_TRASLADO, UPDATE_MOTIVO_TRASLADO, DELETE_MOTIVO_TRASLADO,
} from '@/graphql/queries/catalogos.js'

const columnas = [
  { key: 'codigo', label: 'Código' },
  { key: 'nombre', label: 'Nombre' },
  { key: 'descripcion', label: 'Descripción', type: 'multiline' },
  { key: 'orden', label: 'Orden', centered: true },
  { key: 'activo', label: 'En uso', type: 'checkbox' },
]

const campos = [
  { name: 'codigo', label: 'Código', type: 'text', required: true, maxLength: 50 },
  { name: 'nombre', label: 'Nombre', type: 'text', required: true, maxLength: 100 },
  { name: 'descripcion', label: 'Descripción', type: 'textarea' },
  { name: 'orden', label: 'Orden', type: 'number', default: 0 },
  { name: 'activo', label: 'En uso', type: 'checkbox', default: true },
]
</script>
