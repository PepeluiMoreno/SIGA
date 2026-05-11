/**
 * Devuelve el objeto de estilos inline para un badge usando el color del catálogo.
 * @param {string|null} color  Hex del catálogo (p.ej. "#22c55e")
 * @param {string} fallback    Color por defecto si no hay color en catálogo
 */
export function badgeStyle(color, fallback = '#9333ea') {
  const c = color || fallback
  return {
    backgroundColor: c + '1a',   // ~10 % opacidad
    color:           c,
    borderColor:     c + '4d',   // ~30 % opacidad
  }
}

/**
 * Estilo sólido para bandas/barras de color (cabeceras, bordes laterales, etc.)
 */
export function bandStyle(color, fallback = '#9333ea') {
  return { backgroundColor: color || fallback }
}
