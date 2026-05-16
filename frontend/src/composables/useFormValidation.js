import { reactive, computed } from 'vue'

/**
 * Composable de validación de formularios con errores inline por campo.
 *
 * rules: { campo: [fn(valor, formData) => string|null, ...] }
 * Cada validador devuelve un mensaje de error (string) o null si es válido.
 *
 * Uso:
 *   const { errors, validate, validateField, clearErrors } = useFormValidation({
 *     nombre: [required('El nombre es obligatorio')],
 *     email:  [required(), isEmail()],
 *     fechaFin: [requiredIf(form => form.modalidad !== 'permanente', 'Introduce la fecha de fin')],
 *   })
 */
export function useFormValidation(rules) {
  const errors = reactive({})

  function validateField(field, value, formData = {}) {
    const fieldRules = rules[field]
    if (!fieldRules?.length) { errors[field] = null; return true }
    for (const rule of fieldRules) {
      const msg = rule(value, formData)
      if (msg) { errors[field] = msg; return false }
    }
    errors[field] = null
    return true
  }

  function validate(formData) {
    let valid = true
    for (const field of Object.keys(rules)) {
      if (!validateField(field, formData[field], formData)) valid = false
    }
    return valid
  }

  function clearErrors() {
    for (const k of Object.keys(errors)) errors[k] = null
  }

  const hasErrors = computed(() => Object.values(errors).some(Boolean))

  return { errors, validate, validateField, clearErrors, hasErrors }
}

// ── Validadores reutilizables ─────────────────────────────────────────────────

export const required = (msg = 'Campo obligatorio') =>
  (v) => !v || (typeof v === 'string' && !v.trim()) ? msg : null

export const maxLength = (max, msg) =>
  (v) => v && String(v).length > max ? (msg ?? `Máximo ${max} caracteres`) : null

export const isUrl = (msg = 'URL no válida') => (v) => {
  if (!v) return null
  try { new URL(v); return null } catch { return msg }
}

export const isEmail = (msg = 'Email no válido') => (v) => {
  if (!v) return null
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? null : msg
}

export const minValue = (min, msg) =>
  (v) => v !== null && v !== '' && Number(v) < min ? (msg ?? `El valor mínimo es ${min}`) : null

export const requiredIf = (condFn, msg = 'Campo obligatorio') =>
  (v, form) => condFn(form) && (!v || (typeof v === 'string' && !v.trim())) ? msg : null
