/**
 * Utilidades de fecha para formularios.
 */

/**
 * Fecha de HOY en formato ISO `YYYY-MM-DD` (el que esperan los <input type="date">
 * y los campos Date de GraphQL). Usa la hora local, no UTC, para que "hoy" sea el
 * día del usuario aunque esté cerca de medianoche.
 *
 * Regla del proyecto: en las vistas de ALTA de una entidad, la fecha de inicio se
 * precarga con hoy por defecto (ver feedback_fecha_inicio_hoy_por_defecto).
 */
export function hoyISO() {
  const d = new Date()
  const mes = String(d.getMonth() + 1).padStart(2, '0')
  const dia = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mes}-${dia}`
}
