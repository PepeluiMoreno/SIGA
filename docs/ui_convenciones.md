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

Lo que sigue es el layout de una vista **de formulario o detalle**. Las vistas
**de lista** tienen su propio patrón — `fluid` + `FilterRail` + `ResponsiveTable`
— descrito en la sección siguiente; no uses este.

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

## Vista de lista (patrón canónico)

Referencia viva: `modules/membresia/views/ListaContactos.vue` y `ListaMiembros.vue`.

Toda vista que liste registros se monta así:

```vue
<AppLayout title="Contactos" subtitle="…" fluid>
  <template #actions><!-- acción principal: Nuevo --></template>

  <div class="flex flex-col lg:flex-row gap-4 items-start">
    <FilterRail storage-key="contactos">
      <FilterBar vertical v-model="filters" v-model:search="searchQuery" :fields="filterFields" @clear="limpiar" />
    </FilterRail>

    <div class="flex-1 min-w-0 w-full">
      <ResponsiveTable :columnas="columnas" :filas="filasFiltradas" />
    </div>
  </div>
</AppLayout>
```

Reglas, todas ellas con su porqué:

- **`fluid` es obligatorio.** Sin él, `AppLayout` centra el contenido en
  `lg:w-3/4 lg:mx-auto` y deja un hueco enorme a la derecha de la tabla.
- **Los filtros van en `FilterRail`** (raíl lateral colapsable, recuerda su
  estado por `storage-key`), conteniendo un `FilterBar vertical`. No se usa
  `AppFieldset` para filtrar en una lista: eso es para formularios.
- **La tabla es `ResponsiveTable`**, nunca un `<table>` a mano. Da vista de
  tarjetas en móvil, ordenación por columna y **paginación** gratis (25 filas por
  página; el control solo aparece si hay más de una página). No la desactives
  (`porPagina="0"`) salvo que la tabla no sea una lista plana (p. ej. un árbol de
  acordeón), y en ese caso deja constancia de por qué.
  - **Excepción — vistas árbol.** `ListaMiembros` (agrupación→socios),
    `ListaTransacciones` (módulo→funcionalidad→transacción) y `ListaAcciones`
    (acordeón por campaña) NO son listas planas: son jerarquías con
    expandir/colapsar, y su valor está en ver la estructura. No usan
    `ResponsiveTable` ni paginan; es deliberado, no una tarea pendiente.
- **La columna de acciones lleva cabecera «Acciones»** (la pone `ResponsiveTable`
  por defecto en la columna `esAcciones`) y sus **iconos son siempre visibles**:
  color base `text-slate-500`/`text-gray-500`, no `-400`; el hover solo aporta el
  color de énfasis. El componente `RowActions` ya lo cumple: úsalo. El icono de
  «ver» es el ojo (`EyeIcon`) y **navega a la página de detalle** (no abre panel).
- **Activar/desactivar un registro = toggle deslizante** en su propia columna
  (verde=activo, gris=inactivo), no un botón que aparece/desaparece. Muestra el
  estado *y* lo alterna. Referencia: columna «Activo» de `ListaRoles.vue`. Si hay
  una acción inversa (activar), su mutación debe existir: un desactivar sin
  reactivar deja el registro atrapado.
- **El filtrado es en cliente**, sobre un `computed`. Las queries de strawchemy
  no aceptan `limit`/`offset`: se trae el conjunto y se filtra en la vista.
- **La carga de datos va en `onActivated`, no en `onMounted`** (ver abajo).

### Denominaciones configurables (no literales)

Textos que el usuario puede renombrar en Configuración **no se escriben literales**;
salen del store `useOrgConfigStore`:

- Denominación de la membresía: `orgConfig.miembro`/`Miembro` (singular) y
  `miembros`/`Miembros` (plural). Las mayúsculas son getters ya capitalizados.
- Órgano de gobierno: `orgConfig.organoGobierno`/`OrganoGobierno` (y `…Pl`).

Aplícalo en **títulos de columna, botones, subtítulos y mensajes**. Ejemplo: la
1ª columna de `ListaUsuarios` es `orgConfig.Miembro`, no «Miembro».

**Etiquetas de tipo de vinculación**: algunas derivan de la denominación, no son
fijas. El tipo `SOCIO` se muestra con `orgConfig.Miembro`; `SOCIO_ASPIRANTE` como
`${Miembro} aspirante`. Usa el helper `nombreTipoVinculacion(codigo, orgConfig,
nombreBD)` (en `utils/tipoVinculacion.js`) allí donde pintes el tipo; el `codigo`
es la clave estable, la etiqueta se calcula.

### Filtros: checkboxes, no desplegables

Un filtro con **pocas opciones se pinta entero, con checkboxes**. El desplegable
se reserva para listas largas (agrupaciones, municipios…), donde no caben.

El motivo no es estético: **los filtros son un OR**. Un `<select>` de selección
única impide expresar «activos *o* suspendidos»; con checkboxes marcas las dos.
Y verlas todas a la vez, sin desplegar, te dice de un vistazo qué puedes
combinar. Si el filtro admite varios valores, su control debe permitir marcar
varios.

**Filtro por agrupación/territorio = buscador de texto, no desplegable.** Para
elegir una agrupación (lista larga y jerárquica) se usa `SelectorAgrupacion`
(escribes «Sevilla» y filtra), colocado en el slot `#filters-prefix` del
`FilterBar` con `v-model="filters.agrupacion"`. El filtrado toma ese id y aplica
el subárbol (descendientes). No un `<select>` con las agrupaciones aplanadas.

## Vistas cacheadas: `onActivated`, nunca `onMounted`

Las vistas de lista están dentro de un `<keep-alive>` en `App.vue`, para
conservar scroll y filtros al ir y volver de un detalle. Eso tiene dos
consecuencias que **hay que respetar o la vista queda sutilmente rota**:

1. **La vista debe declarar su nombre**, o `keep-alive` no la reconoce y no la
   cachea (el `:include` casa contra el `name` del componente, y `<script setup>`
   no lo infiere):

   ```js
   defineOptions({ name: 'ListaContactos' })
   ```

   El nombre debe coincidir con el del `:include` en `App.vue`. Al crear una
   vista de lista nueva, añádela allí.

2. **Los datos se cargan en `onActivated`.** Un componente cacheado se monta una
   sola vez, así que `onMounted` no vuelve a correr: al regresar de un formulario
   verías la lista sin el registro que acabas de crear.

   ```js
   onActivated(cargar)
   ```

   Si la carga tiene orden (p. ej. los datos dependen de un catálogo), encadena
   dentro del mismo `onActivated` con `await`.

Una vista de lista **carga sus datos al entrar**. No hay listas que esperen a que
el usuario pulse «Buscar»: los filtros refinan lo ya mostrado.

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

## Ver el detalle de una entidad: página con ruta

**La ficha de una entidad (ver/editar un socio, contacto, agrupación, usuario…)
es una PÁGINA propia con ruta** (`AppLayout`), del tipo `/miembros/:id`, no un
drawer ni un modal. Referencia: `DetalleMiembro.vue`, `DetalleContacto.vue`,
`DetalleAgrupacion.vue` — todas son páginas. La acción «ver» de la fila **navega**
a esa ruta; no abre un panel. Un usuario tiene su `DetalleUsuario` en `/usuarios/:id`.

**Una vista de detalle carga en `onMounted`, NO en `onActivated`.** Al revés que
las listas: los detalles **no** están en el `keep-alive` de `App.vue`, así que se
montan y desmontan en cada visita. `onActivated` solo se dispara para componentes
dentro de keep-alive; en una vista de detalle **nunca correría** y la página
quedaría en blanco. `onActivated` es solo para las listas cacheadas.

## Modales y drawers: para acciones cortas, no para fichas

- **Formularios cortos / alta rápida / acciones con pocos campos →** `AppDrawer`
  (panel lateral). Nunca un modal centrado. **No** lo uses para *ver la ficha* de
  una entidad: eso es una página (ver arriba).
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
