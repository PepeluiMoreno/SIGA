# SIGA · Recogida de firmas (plugin de WordPress)

Plugin de WordPress que muestra un formulario para recoger los datos de
contacto de simpatizantes que firman una campaña y los reenvía al backend de
SIGA. **WordPress solo presenta el formulario**; SIGA es la fuente única de
datos, consentimiento y verificación (doble opt-in).

## Cómo encaja con el backend

El plugin consume los endpoints públicos que SIGA expone en
`backend/app/api/publico/firmas.py`:

```
POST /api/publico/firmas              → registra una firma (doble opt-in)
GET  /api/publico/firmas/actividades  → actividades de recogida de firmas activas
GET  /api/publico/firmas/contador/ID  → nº de firmas verificadas
```

El alta (`POST /api/publico/firmas`):

- Hace *upsert* del **Contacto** (persona física) por email y crea la
  **Participación** de tipo `FIRMA` con su satélite `FirmaCampania`.
- Envía un correo de **doble opt-in**: la firma no cuenta hasta que el
  simpatizante pulsa el enlace de confirmación.
- Se protege con **captcha server-side** (Cloudflare Turnstile o hCaptcha),
  **honeypot** y **rate-limit** por IP y por email.

El plugin no inventa esquema ni guarda datos personales en WordPress: solo
recoge el formulario y lo reenvía.

## Arquitectura del envío

```
Navegador  ──POST /wp-json/siga-firmas/v1/firmar──▶  WordPress (este plugin)
   (formulario + token de captcha + nonce)                    │
                                                              │ wp_remote_post
                                                              ▼  (+ X-Forwarded-For)
                                              SIGA  POST /api/publico/firmas
```

El navegador **no llama directamente a SIGA**: envía a un endpoint REST del
propio WordPress (mismo origen, con *nonce*) y WordPress reenvía la petición
server-side. Ventajas:

- **No depende de CORS**: el navegador habla siempre con su propio dominio.
- **Rate-limit correcto**: WordPress reenvía la **IP real** del visitante en la
  cabecera `X-Forwarded-For`, que es la que SIGA usa para limitar por IP.
- **El secreto del captcha nunca toca WordPress**: el widget usa solo la clave
  pública; la verificación la hace SIGA con su clave secreta.

## Instalación

1. Copia la carpeta `siga-firmas/` en `wp-content/plugins/` (o sube un ZIP de
   esa carpeta desde *Plugins → Añadir nuevo → Subir plugin*).
2. Actívalo en *Plugins*.
3. Ve a **Ajustes → SIGA Firmas** y rellena:
   - **URL del backend de SIGA** — p. ej. `https://api.tu-dominio.org` (sin
     barra final).
   - **Actividad de recogida de firmas** — se elige en un **desplegable** que el
     plugin rellena llamando a `GET /api/publico/firmas/actividades` (actividades
     de recogida de firmas web **activas**: iniciadas y no cerradas, cuya campaña
     incluye la recogida de firmas en su métrica). No hay que pegar UUIDs a mano.
     El botón *Actualizar actividades* refresca la lista (se cachea 5 minutos). Si
     el backend no responde, el campo cae a texto libre para no bloquearte.
   - **Proveedor de captcha** — `turnstile`, `hcaptcha` o `none` (solo
     desarrollo). Debe coincidir con `CAPTCHA_PROVIDER` del backend.
   - **Clave pública (site key) del captcha** — la clave *pública* del widget.
   - **URL de política de privacidad** — se enlaza en la casilla de aceptación.

## Uso

Inserta el formulario con el shortcode:

```
[siga_firmas]
```

Atributos opcionales:

| Atributo          | Por defecto                | Descripción                                       |
|-------------------|----------------------------|---------------------------------------------------|
| `actividad`       | (la de Ajustes)            | UUID de la actividad, para usar otra distinta.    |
| `titulo`          | `Firma la campaña`         | Título mostrado sobre el formulario.              |
| `boton`           | `Firmar`                   | Texto del botón de envío.                         |
| `pedir_cp`        | `1`                        | Mostrar el campo Código postal (`1`/`0`).         |
| `pedir_documento` | `0`                        | Mostrar Tipo + Número de documento (`1`/`0`).     |

Ejemplo con actividad concreta y pidiendo documento:

```
[siga_firmas actividad="3f6a2c10-1b2c-4d5e-8f90-0a1b2c3d4e5f" pedir_documento="1" titulo="Firma por la laicidad"]
```

## Campos del formulario → payload de SIGA

| Campo del formulario      | Campo en `FirmaPublicaIn` | Obligatorio |
|---------------------------|---------------------------|-------------|
| (actividad seleccionada)  | `actividad_id`            | Sí          |
| Nombre                    | `nombre`                  | Sí          |
| Apellidos                 | `apellidos`               | Sí          |
| Correo electrónico        | `email`                   | Sí          |
| Código postal             | `codigo_postal`           | No          |
| Tipo (DNI/NIE)            | `tipo_documento`          | Sí          |
| **DNI / NIE**             | `documento`               | **Sí**      |
| Acepto términos           | `acepta_terminos`         | Sí          |
| Quiero recibir info        | `acepta_comunicaciones`   | No          |
| (oculto, honeypot)        | `website`                 | —           |
| (widget captcha)          | `captcha_token`           | Según config|

> El campo `pais_id` de SIGA es un UUID y se omite en este formulario para no
> exigir un catálogo de países en WordPress. Si lo necesitas, puede añadirse
> como atributo fijo del shortcode en una versión posterior.

### NIF, desduplicación y firmante

El **DNI/NIE es obligatorio** y es la clave de identidad. El plugin valida la
letra de control **en el navegador y en el servidor** (proxy PHP), y SIGA la
vuelve a validar. Con ese NIF, SIGA:

- **desduplica** al firmante: una misma persona no se duplica aunque firme con
  emails distintos (se reutiliza su `Contacto`);
- le da la **vinculación `FIRMANTE`** (si no la tenía);
- guarda el **historial** de qué ha firmado (una `FirmaCampania` por campaña).

Solo se aceptan **DNI y NIE** (no pasaporte), porque la desduplicación es por NIF.

## Requisitos en el lado de SIGA

- El endpoint público está montado (lo está por defecto en `backend/main.py`).
- `CAPTCHA_PROVIDER` y `CAPTCHA_SECRET` configurados en el backend, acordes con
  el proveedor y la clave pública del plugin. En desarrollo puede usarse
  `CAPTCHA_PROVIDER=disabled` en SIGA y `none` en el plugin.
- La actividad de recogida de firmas existe, es **online** y está **activa**
  (iniciada y no cerrada); su campaña incluye la recogida de firmas en su
  métrica. Si no, SIGA responde `campania_no_disponible`.
- El `TipoVinculacion` **`FIRMANTE`** está sembrado (seed de vinculaciones); si
  no, SIGA registra la firma pero no asigna la vinculación (queda avisado en log).

Como el navegador habla solo con WordPress, **no hace falta** añadir el dominio
del WordPress a `FIRMAS_CORS_ORIGINS` del backend.

## Seguridad

- Nonce de WordPress en el endpoint REST (defensa CSRF).
- Honeypot (`website`) descartado en silencio si llega relleno.
- Captcha y rate-limit reales en SIGA.
- WordPress no almacena datos personales: solo reenvía.
