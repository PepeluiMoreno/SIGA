# Descentralización — el modelo matrioska

> **Estado: acuerdo de dominio, para implementar.** Fija cómo se comporta la aplicación
> según el grado de descentralización de la organización. El *cómo* del reparto RBAC y la
> unificación de cargos en BD se planifican aparte; aquí va el *qué* y el *porqué*.
> Complementa `MOTOR_TERRITORIAL.md` (que acota el ámbito) y `GOBERNANZA.md` (cargos y roles).

## 1. El principio

La aplicación es **la misma en cada nivel territorial, a escala menor**. Cada agrupación es
una organización completa dentro de otra: una matrioska.

**Todas las funcionalidades existen en todos los niveles.** Lo único que cambia es el
**ámbito** sobre el que se ejercen. No hay "funciones centrales" frente a "funciones
locales" — hay las mismas funciones, cada una en su muñeca. Ese acotamiento por ámbito ya
está construido: es el motor territorial. La descentralización no añade ni quita funciones;
decide **quién las ejerce y dónde**.

## 2. La descentralización es por materia

Una organización no es "centralizada" o "descentralizada" en bloque: lo es **materia a
materia**. Cada materia de gobierno tiene un flag homogéneo "¿distribuida hacia abajo?":

| Materia | Flag | Si `true` (distribuida) | Si `false` (retenida) |
|---|---|---|---|
| Presidencia | `presidencia_distribuida` | hay **presidente electo** en el territorio | la asume el **coordinador** |
| Secretaría | `secretaria_distribuida` | hay **secretario electo** | la asume el responsable del territorio |
| Tesorería | `tesoreria_distribuida` | hay **tesorero electo** | la asume el responsable del territorio |
| Campañas | `campanas_distribuida` | la agrupación **diseña, presupuesta, dota y ejecuta** sus campañas | las campañas son competencia del **nivel central** |

El antiguo `org.multiterritorial` **se jubila**: era un interruptor de bloque que estos
flags sustituyen con precisión. Una organización es descentralizada en la medida en que
distribuya materias; con todas a `false`, es de facto centralizada.

> **⚠️ Campañas — flag creado, distribución NO habilitada aún.** El flag
> `campanas_distribuida` existe (default `false`) para dejar el modelo completo, pero el
> ciclo de campaña **no está maduro ni a nivel central**: presupuestar carece de flujo de
> aprobación real, **reservar fondos no existe** (el vínculo campaña→partida presupuestaria
> es un UUID suelto sin FK ni servicio que lo ejecute) y el reclutamiento de voluntarios
> vive desacoplado en el módulo Grupos. Distribuir ahora replicaría por territorio una
> función que aún no funciona en ningún sitio. La distribución de campañas queda **reservada
> al centro hasta cerrar esos tres huecos** (ver `GOBERNANZA.md` / pendientes de campañas).

## 3. Presidente y coordinador son el mismo puesto

Cada agrupación tiene **un** máximo responsable de su muñeca. Cómo se le llega a él depende
de si la presidencia está distribuida:

- **`presidencia_distribuida = true`** → lo **elige** una junta local: se llama **presidente**.
- **`presidencia_distribuida = false`** → lo **designa** el nivel superior: se llama
  **coordinador**.

**No son dos cargos distintos: son dos nombres del mismo puesto** según se llegue a él por
elección o por nombramiento. Donde hay presidente electo, no existe además un coordinador;
el presidente de la agrupación *es* el coordinador de ese territorio.

> **Nota de implementación pendiente:** hoy `cargos` tiene dos filas separadas (`Presidente`
> y `Coordinador/a territorial`). Unificarlas es coherente con este modelo, pero es una
> decisión de modelado que se planifica aparte (ver §6).

## 4. La regla, en una línea

> El responsable de cada agrupación ejerce en su ámbito **toda materia que no esté
> distribuida hacia abajo**. Cada materia distribuida la ejerce su cargo electo.

Aplicada materia a materia:

| | `distribuida = true` | `distribuida = false` |
|---|---|---|
| Presidencia | presidente electo la ejerce | el coordinador la ejerce |
| Secretaría | secretario electo la ejerce | el responsable del territorio la ejerce |
| Tesorería | tesorero electo la ejerce | el responsable del territorio la ejerce |

Todo, **en su ámbito territorial** — lo garantiza el motor, no la configuración.

### Ejemplos

- **Todo centralizado** (las tres a `false`): cada territorio tiene un coordinador designado
  que ejerce presidencia, secretaría y tesorería de su ámbito. No hay cargos electos locales.
- **Todo distribuido** (las tres a `true`): cada territorio tiene junta electa completa
  (presidente + secretario + tesorero). El presidente es el responsable del territorio.
- **Mixto frecuente** — presidencia y secretaría distribuidas, **caja central**
  (`tesoreria_distribuida = false`): el territorio se autogobierna y lleva sus actas, pero el
  dinero lo maneja el nivel superior. El presidente electo NO toca tesorería.

## 5. Los cargos electos (donde su materia está distribuida)

- **Tesorero** — toda la rama económica; **nadie más toca el dinero** (separación de
  funciones: quien autoriza no paga). Existe solo si `tesoreria_distribuida = true`.
- **Secretario** — padrón, altas de socio, actas, libro de socios, contactos. Existe solo si
  `secretaria_distribuida = true`.
- **Presidente / coordinador** — el responsable del territorio (§3). Ejerce presidencia
  siempre, y además cada materia no distribuida. Aprueba altas de socio. Sobre el dinero:
  solo si la tesorería está retenida (no distribuida) y por tanto recae en él.
- **Vicepresidente** — suple al presidente.
- **Vocal (base)** — solo actividades; esqueleto para vocalías **a medida** ("Vocal de
  Comunicación", "Vocal de Formación") sin tocar código.

## 6. Cómo se sostiene técnicamente

La cadena de autorización es:

```
USUARIO ──▶ CARGO ──▶ ROL ──▶ FUNCIONALIDAD ──▶ TRANSACCIÓN
        nombramiento   cargos_roles   roles_funcionalidades   ft
```

- Los **roles** son de granularidad alta: grupos pequeños de funcionalidades afines (un
  "flujo de trabajo": padrón, tesorería, actas…). Permite componer cargos a medida.
- Un **cargo** es una combinación de roles-flujo. Los tradicionales se preestablecen por
  *seeding*; los "a medida" se componen desde configuración.
- El **responsable del territorio** compone su paquete según los tres flags: presidencia
  siempre, más cada materia no distribuida.
- Regla de oro: **los roles se asignan a cargos, no a usuarios**. El usuario recibe su rol al
  ocupar un cargo, con el territorio del nombramiento.

El grado de descentralización se resuelve **en el momento del seeding**. Consecuencia:
cambiar cualquiera de los flags exige re-derivar los permisos del responsable
(re-ejecutar el seed) para que surta efecto. Si en el futuro se requiere efecto instantáneo,
la evaluación del flag se mueve al motor de autorización sin rehacer el reparto.

## 7. Estado y pendientes

- Acuerdo de dominio: **cerrado** (este documento).
- **Implementación pendiente**, en orden de decisión:
  1. **Unificar `Presidente` y `Coordinador/a territorial`** en un único cargo (decisión de
     modelado; planificar aparte).
  2. **Jubilar `org.multiterritorial`** y crear los flags homogéneos
     (`presidencia_distribuida`, `secretaria_distribuida`, `tesoreria_distribuida`,
     `campanas_distribuida`).
  3. **Seed de reparto** de funcionalidades a cargos (roles-flujo + composición condicional
     por flags), enganchado en el lifespan tras la sincronización del catálogo.
- **Campañas**: el flag `campanas_distribuida` se crea ya (default `false`) para dejar el
  modelo completo, pero **su distribución no se habilita** hasta madurar el ciclo central
  (§2): presupuesto con aprobación real, reserva de fondos (FK + servicio ejecutable) y
  reclutamiento integrado en la vista de campaña. Hoy hay ~7 transacciones `CAMPANA_*`
  huérfanas y un `FLUJO_PRESUPUESTO_CAMPANA` que es dead code (apunta a una entidad
  inexistente).
- La cadena RBAC hoy está construida pero **desconectada** en el tramo ROL→FUNCIONALIDAD:
  los roles de cargo están vacíos, por lo que ocupar un cargo aún no habilita nada. En
  particular, **nadie puede aprobar altas de socio** pese a que la mutación existe.
