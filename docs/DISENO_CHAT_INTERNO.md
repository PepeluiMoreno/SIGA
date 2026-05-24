# Mensajería interna (chat) — Diseño y decisiones

> Estado: **fase de diseño, no implementado.** Este documento recoge la decisión
> tomada y, sobre todo, lo que falta VERIFICAR antes de escribir código. La
> implementación es una sesión dedicada, condicionada a esas verificaciones.
>
> Nota de nombres: hablamos de **XMPP** (protocolo de chat: ejabberd, Conversations),
> no de XAMPP (paquete de servidor web). No confundir.

## 1. Problema que se resuelve

La organización usa hoy WhatsApp/Telegram para coordinarse. El problema no es la
calidad del chat (WhatsApp es buen chat), sino que está **desconectado de SIGA**:
los grupos se gestionan por duplicado y a mano. El valor buscado es un chat
**fuertemente vinculado a la estructura de SIGA**: al crear un grupo de trabajo o
una unidad organizativa, su canal de conversación existe solo; al entrar o salir
un miembro, entra o sale del canal automáticamente.

Requisitos declarados por el usuario:
- Sustituir WhatsApp/Telegram.
- **Vínculo fuerte** con la app (membresía del canal derivada de la de SIGA).
- **Fiable**, **trazable**, transferencia de **archivos sin pérdida** (poco frecuente).
- Uso principal **desde el móvil**.
- No depender de servicios fuera de la organización (VPN).

## 2. Alcance de canales

Dos orígenes desde el inicio:
- **Organizativos** (estructura permanente: unidades territoriales, órganos de
  gobierno). Membresía derivada de la estructura. Posible comportamiento de
  difusión (pocos emisores) en canales muy grandes — a decidir.
- **De actividad** (grupos de trabajo, temporales). Membresía dinámica; al
  terminar la actividad, el canal se **archiva** (histórico consultable), no se borra.

Común a ambos y núcleo del módulo: **la membresía del canal NO se gestiona a mano,
se deriva de otra entidad de SIGA** (unidad organizativa o grupo de trabajo).

## 3. Decisión de arquitectura

**Usar XMPP con servidor propio (ejabberd) dentro de la VPN + cliente Conversations
en el móvil + un PUENTE construido en SIGA.** No se construye un cliente de chat
propio (sería reescribir años de trabajo y, por las notificaciones push, obligaría
igualmente a salir de la VPN vía Google/Apple).

Motivo de elegir XMPP sobre "chat web propio dentro de SIGA": el uso es móvil, y un
chat web móvil no tiene notificaciones push fiables con la app cerrada → la gente
volvería a WhatsApp. Conversations (app nativa madura) resuelve eso de fábrica.

Coste aceptado conscientemente: operar un segundo sistema (ejabberd) y que la
**trazabilidad de los mensajes viva en ejabberd**, no nativa en SIGA (mitigable
copiando metadatos/índice a SIGA si se requiere auditoría desde la app — a decidir).

## 4. El puente SIGA ↔ ejabberd (lo que SÍ se construye)

Cuatro piezas:

1. **Sincronización de salas (núcleo, el valor).** Evento de dominio de SIGA
   (grupo creado, miembro añadido/quitado) → handler → llamada a la **API ReST de
   ejabberd** (autenticada con bearer token `ejabberd:admin`) para crear sala MUC y
   gestionar miembros. Encaja con el event bus existente (`app/core/events.py`).
   **Confirmado viable** por la doc de ejabberd (API ReST + OAuth, ver §6).
2. **Identidad del usuario** → ver §5 (la pieza delicada).
3. **Aprovisionamiento** de cuentas XMPP (alta/baja ligadas al alta/baja en SIGA).
4. **Onboarding en Conversations**: SIGA genera el acceso (p. ej. QR) para que el
   usuario configure la app sin teclear credenciales.

Librería para el puente: **slixmpp** (asyncio, como SIGA; viva, release 2026-05).
Para la API ReST basta un cliente HTTP con bearer token.

## 5. Identidad: principio rector

**El puente se engancha a la identidad YA RESUELTA por SIGA, con independencia del
`auth.modo` activo.** SIGA soporta UN modo de autenticación activo a la vez
(`auth.modo`: `LOCAL` con JWT propio, o `AUTHELIA` por forward-auth; el `Context`
en `app/core/context.py` ya abstrae ambos en un `user_id`). El chat **NO debe
vincularse a un modo concreto**: se vincula a "usuario autenticado en SIGA, sea
como sea". Así, cambiar de modo no rompe el chat. (Coherente con el principio de
no-acoplamiento del proyecto.)

Flujo: el usuario se autentica en SIGA (por el modo que sea) → SIGA, que tiene
token admin de ejabberd, **emite para ese usuario un token XMPP** (scope
`sasl_auth`, ver §6) → ese token llega a Conversations (vía QR). El usuario nunca
teclea una credencial XMPP.

Detalle dependiente del modo (no es atadura, es implementación del onboarding):
- **LOCAL**: directo — SIGA valida con su JWT y emite el token XMPP.
- **AUTHELIA**: Authelia es forward-auth HTTP; **no cubre XMPP nativo** (Conversations
  habla TCP directo, no pasa por el proxy HTTP). Por eso la emisión del token la
  hace SIGA (que sí está tras Authelia) y se entrega al móvil por QR.

## 6. Lo confirmado por la documentación de ejabberd (OAuth/API)

- ejabberd expone **API ReST** (`mod_http_api`) autenticable con **bearer token**
  OAuth 2.0 → SIGA puede administrar (crear salas, gestionar rosters/miembros).
  Token admin emitible con `oauth_issue_token ... ejabberd:admin`. **(Pieza 1: OK.)**
- Existe el scope **`sasl_auth`**: un token con ese scope permite **login XMPP vía
  SASL X-OAUTH2** en lugar de contraseña. Es la base del flujo de identidad de §5.
- El OAuth de ejabberd es **su propio** proveedor (autentica contra su base de
  usuarios), NO delega en Authelia. Por eso la identidad la orquesta SIGA, no ejabberd.

## 7. Verificaciones PENDIENTES (hacer ANTES de programar, con acceso real)

1. ¿Un token `sasl_auth` **emitido por el lado admin** (sin que el usuario teclee
   su contraseña en ejabberd) sirve para autenticar a ese usuario? ¿O el flujo
   `authorization_token` exige siempre que el usuario introduzca credenciales?
2. ¿**Conversations** (la app) soporta login por **token / QR** sin pedir contraseña
   XMPP? (Comportamiento del cliente móvil, no del servidor.)
3. Provisión de cuentas: ¿crear la cuenta XMPP por usuario vía API, con qué JID
   (¿basado en email? ¿en id de SIGA?), y cómo se da de baja.
4. Transferencia de archivos (HTTP File Upload, XEP-0363) en ejabberd dentro de la
   VPN: configuración y límites.
5. Notificaciones push de Conversations: confirmar si requieren el servicio de push
   de Conversations/Google y si eso es aceptable respecto al requisito de VPN
   (las push de móvil pasan necesariamente por Google/Apple — punto a aceptar o no).

> Estas verificaciones necesitan acceso a internet/documentación actual y, idealmente,
> un ejabberd de pruebas. No se pudieron hacer en la sesión de diseño.

## 8. Lo que NO se hace

- No se construye un cliente de chat propio (móvil ni web).
- No se ata el chat a un `auth.modo` concreto.
- No se duplica la mensajería en la BD de SIGA (salvo, opcionalmente, un índice de
  trazabilidad si se decide en §3).
- Fuera de fase inicial (según spec original): edición de mensajes, permisos
  avanzados por mensaje, reacciones, menciones.

## 9. Relación con el módulo de comunicación ya existente

Distinto del subsistema de **notificaciones dirigidas por procesos**
(`docs/MODULO_COMUNICACION.md`, ya implementado). Aquel es sistema→usuario; este es
usuario↔usuario. Pueden puentearse: un mensaje o mención podría generar una
notificación in-app, y el `DestinatarioResolver` podría reutilizarse para poblar la
membresía inicial de un canal (p. ej. "todos los de este grupo de trabajo").
