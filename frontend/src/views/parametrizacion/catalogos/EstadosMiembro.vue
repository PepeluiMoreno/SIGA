<template>
  <CatalogoGenerico
    titulo="Situaciones"
    subtitulo="Situaciones por las que pasa un miembro"
    nombre-singular="Situación"
    icono="📊"
    query-name="estadosMiembro"
    :query-string="GET_ESTADOS_MIEMBRO"
    :mutation-create="CREATE_ESTADO_MIEMBRO"
    :mutation-update="UPDATE_ESTADO_MIEMBRO"
    :mutation-delete="DELETE_ESTADO_MIEMBRO"
    :columnas="columnas"
    :campos="campos"
    order-by="orden"
  />
</template>

<script setup>
import CatalogoGenerico from '@/components/parametrizacion/CatalogoGenerico.vue'
import { GET_ESTADOS_MIEMBRO, CREATE_ESTADO_MIEMBRO, UPDATE_ESTADO_MIEMBRO, DELETE_ESTADO_MIEMBRO } from '@/graphql/queries/catalogos.js'

const columnas = [
  { key: 'orden', label: 'Orden' },
  { key: 'nombre', label: 'Nombre' },
  { key: 'descripcion', label: 'Descripción', type: 'multiline' },
  { key: 'activo', label: 'En uso', type: 'checkbox' },
]

const campos = [
  { name: 'nombre', label: 'Nombre', type: 'text', required: true, maxLength: 100 },
  { name: 'descripcion', label: 'Descripción', type: 'textarea' },
  { name: 'color', label: 'Color', type: 'color', default: '#6C757D' },
  { name: 'orden', label: 'Orden', type: 'number', default: 0 },
  { name: 'activo', label: 'En uso', type: 'checkbox', default: true },
]
</script>
