# Despliegue del servidor de chat (ejabberd) — SIGA

> ⚠️ Material NO verificado contra un ejabberd real. Punto de partida basado en la
> documentación oficial. Validar en la fase de despliegue (ver
> `docs/DISENO_CHAT_INTERNO.md`, §6 y §7).

## Qué hay aquí
- `docker-compose.yml` — contenedor ejabberd para la VPN.
- `ejabberd.yml` — config mínima: API ReST + OAuth (para que SIGA administre),
  MUC (salas por grupo), MAM (historial), file upload y push.

## Antes de arrancar (obligatorio)
1. Cambiar `EJABBERD_ADMIN_PWD` y todos los secretos de ejemplo.
2. Montar certificados TLS reales en `./certs` (o ajustar `certfiles`).
3. Ajustar `siga.local` al dominio real, y `put_url` de `mod_http_upload` a una
   URL accesible por los clientes.
4. Si SIGA ya define una red Docker, usar `external: true` con su nombre.

## Arranque
```
docker compose up -d
docker compose logs -f ejabberd
```

## Conectar SIGA con ejabberd (el token admin)
SIGA administra ejabberd por la API ReST con un bearer token de scope
`ejabberd:admin`. Generarlo dentro del contenedor:

```
docker compose exec ejabberd \
  ejabberdctl oauth_issue_token admin@siga.local 31536000 ejabberd:admin
```

Copiar el token devuelto y configurarlo en SIGA (Parámetros Generales), junto al
resto de claves que lee el puente:

- `chat.ejabberd_api_url`     → `http://siga-ejabberd:5280/api`  (nombre del contenedor en la red)
- `chat.ejabberd_admin_token` → el token emitido
- `chat.xmpp_dominio`         → `siga.local`
- `chat.muc_servicio`         → `conference.siga.local`

## Verificaciones pendientes (no resueltas en diseño)
Ver §7 del diseño. En resumen, probar contra este contenedor:
1. Que el token admin permite `create_room` / `set_room_affiliation` vía `/api`.
2. El flujo de identidad del usuario (token `sasl_auth` / QR en el cliente).
3. File upload (XEP-0363) accesible desde los clientes.
4. Push al móvil (decisión de push sin Google: ver diseño).
