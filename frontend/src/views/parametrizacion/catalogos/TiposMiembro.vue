<template>
  <CatalogoGenerico
    titulo="Tipos de miembro"
    subtitulo="Configuración de tipos de miembro"
    nombre-singular="Tipo de miembro"
    icono="👤"
    query-name="tiposMiembro"
    :query-string="GET_TIPOS_MIEMBRO"
    :mutation-create="CREATE_TIPO_MIEMBRO"
    :mutation-update="UPDATE_TIPO_MIEMBRO"
    :mutation-delete="DELETE_TIPO_MIEMBRO"
    :columnas="columnas"
    :campos="campos"
  />
</template>

<script setup>
import CatalogoGenerico from '@/components/parametrizacion/CatalogoGenerico.vue'
import { GET_TIPOS_MIEMBRO, CREATE_TIPO_MIEMBRO, UPDATE_TIPO_MIEMBRO, DELETE_TIPO_MIEMBRO } from '@/graphql/queries/catalogos.js'

const columnas = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'descripcion', label: 'Descripción', type: 'multiline' },
  { key: 'requiereCuota', label: 'Requiere Cuota', type: 'checkbox' },
  { key: 'puedeVotar', label: 'Puede Votar', type: 'checkbox' },
  { key: 'activo', label: 'En uso', type: 'checkbox' },
]

const campos = [
  { name: 'nombre', label: 'Nombre', type: 'text', required: true, maxLength: 100 },
  { name: 'descripcion', label: 'Descripción', type: 'textarea' },
  { name: 'requiereCuota', label: 'Requiere Cuota', type: 'checkbox', default: true },
  { name: 'puedeVotar', label: 'Puede Votar', type: 'checkbox', default: false },
  { name: 'activo', label: 'En uso', type: 'checkbox', default: true },
]
</script>
