<template>
  <CatalogoGenerico
    titulo="Estados de Cuota"
    subtitulo="Estados del ciclo de cobro de cuotas"
    nombre-singular="Estado de Cuota"
    icono="💰"
    query-name="estadosCuota"
    :query-string="GET_ESTADOS_CUOTA"
    :mutation-create="CREATE_ESTADO_CUOTA"
    :mutation-update="UPDATE_ESTADO_CUOTA"
    :mutation-delete="DELETE_ESTADO_CUOTA"
    :columnas="columnas"
    :campos="campos"
    order-by="orden"
  />
</template>

<script setup>
import CatalogoGenerico from '@/components/parametrizacion/CatalogoGenerico.vue'
import { GET_ESTADOS_CUOTA, CREATE_ESTADO_CUOTA, UPDATE_ESTADO_CUOTA, DELETE_ESTADO_CUOTA } from '@/graphql/queries/catalogos.js'

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
