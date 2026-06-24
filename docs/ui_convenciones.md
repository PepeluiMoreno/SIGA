# Convenciones de UI — SIGA frontend

Sistema de diseño compartido. El objetivo es que **todas las vistas sigan el
mismo layout y reutilicen las mismas primitivas** (DRY). Lo que sigue es el
patrón canónico; al migrar una vista, ajústala a esto.

## Tipografía

Fuente: **Plus Jakarta Sans** (variable, autoalojada vía `@fontsource-variable`,
sin CDN externo por privacidad). Se aplica globalmente desde `--font-main` y
`tailwind.config.js`. No hace falta declararla por componente.

## Layout de vista

Toda vista se envuelve en `AppLayout` (el shell con barra lateral + cabecera).
Aporta título, subtítulo, icono y zonas de acciones/pie; garantiza cabecera y
ritmo consistentes. Dentro, el contenido se organiza con `AppFieldset` y la
clase `page-body`.

```vue
<AppLayout title="Miembros" subtitle="142 activos" icon="👥">
  <template #actions>
    <AppButton :icon="PlusIcon" @click="alta">Nuevo</AppButton>
  </template>

  <div class="page-body">
    <AppFieldset title="Filtros" cols="3">
      <AppFormField label="Nombre"><AppInput v-model="f.nombre" width="md" /></AppFormField>
      <AppFormField label="Localidad"><AppInput v-model="f.localidad" width="md" /></AppFormField>
      <AppFormField label="CP"><AppInput v-model="f.cp" width="xs" /></AppFormField>
    </AppFieldset>

    <div class="card p-0"><!-- tabla --></div>
  </div>
</AppLayout>
```

## Campos y grupos

- **Grupos enmarcados:** `AppFieldset` (borde + título + grid opcional). Sustituye
  los `<div class="bg-white border …">` sueltos.
- **Campo:** `AppFormField` aporta label, ayuda, error y accesibilidad (ids,
  `aria-describedby`, `aria-invalid`). Envuelve el control dentro.
- **Controles:** `AppInput`, `AppSelect`, `AppTextarea`. Ya enmarcados y
  tematizados; nada de clases sueltas repetidas.

### Anchura proporcional al contenido

No todo es `w-full`. El control declara su ancho según lo que se espera escribir:

| `width` | Uso típico                |
|---------|---------------------------|
| `xs`    | CP, año, número           |
| `sm`    | fecha, DNI, teléfono      |
| `md`    | nombre, email corto       |
| `lg`    | email largo, asunto       |
| `full`  | ocupa la celda (defecto)  |

```vue
<AppFormField label="Código postal"><AppInput v-model="cp" width="xs" /></AppFormField>
```

## Modales: solo para advertencias

- **Formularios / alta / edición / detalle / acciones con campos →** `AppDrawer`
  (panel lateral). Nunca un modal centrado.
- **Advertencias y confirmaciones sí/no →** `ConfirmModal` / `ConfirmActionModal`
  (vía el composable `useConfirm`) o `BaseModal` para avisos puntuales.

## Estados

- Cargando → `EstadoCarga` (con roles ARIA).
- Lista/resultado vacío → `EstadoVacio`.
- Guía "configura filtros y busca" → `EstadoPendiente`.
- Error → `ErrorAlert`.

## Overlays accesibles

`BaseModal` y `AppDrawer` integran `useFocusTrap`: atrapan el foco, lo devuelven
al cerrar y bloquean el scroll de fondo. No hay que gestionar el foco a mano.

## Building blocks CSS (cuando no haya primitiva)

Definidos en `style.css` (`@layer components`): `.card`, `.fieldset`,
`.fieldset-legend`, `.field-label`, `.field-help`, `.field-error`, `.control`,
`.w-field-xs|sm|md|lg`, `.page-body`. Además, todo `input/select/textarea` crudo
recibe un enmarcado base coherente y tematizado (`@layer base`).

## Importación

```js
import {
  AppLayout, AppFieldset, AppFormField, AppFormGrid,
  AppInput, AppSelect, AppTextarea, AppButton, AppDrawer,
  EstadoCarga, EstadoVacio, ErrorAlert,
} from '@/components/common'
```
