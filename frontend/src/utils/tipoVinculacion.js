// Etiqueta mostrada de un tipo de vinculación.
//
// Algunos tipos NO tienen nombre fijo: derivan de la denominación configurable de
// la membresía (parámetro general). El caso canónico es SOCIO, cuya etiqueta ES la
// denominación singular: si la organización llama «asociado» a sus miembros, el
// tipo SOCIO debe mostrarse «Asociado», no «Socio». SOCIO_ASPIRANTE compone sobre
// esa misma base. El resto de tipos (Voluntario, Donante…) usan su nombre de BD.
//
// El `codigo` es la clave estable; lo que se calcula es solo la etiqueta.
//
// Uso:
//   import { useOrgConfigStore } from '@/stores/orgConfig'
//   const orgConfig = useOrgConfigStore()
//   nombreTipoVinculacion('SOCIO', orgConfig)              // → 'Socio' / 'Asociado' / …
//   nombreTipoVinculacion(tv.codigo, orgConfig, tv.nombre) // objeto con codigo+nombre

export function nombreTipoVinculacion(codigo, orgConfig, nombreBD = null) {
  switch (codigo) {
    case 'SOCIO':
      return orgConfig.Miembro
    case 'SOCIO_ASPIRANTE':
      return `${orgConfig.Miembro} aspirante`
    default:
      // Tipos con nombre fijo: el de BD si se conoce; si no, el propio código.
      return nombreBD ?? codigo ?? '—'
  }
}
