# Modo debug de UI

## Objetivo

El modo debug de UI permite diagnosticar incidencias funcionales del frontend en staging o en otros entornos compartidos sin depender de DevTools del navegador.

La idea no es sustituir el trabajo de desarrollo local, sino ofrecer una capa de observabilidad ligera para detectar rápidamente:

- errores JavaScript capturados en cliente,
- errores de red o GraphQL,
- fallos de navegación del router,
- discrepancias entre el estado de sesión y la ruta actual,
- problemas de configuración como endpoints mal construidos.

## Activación

El modo debug puede activarse de dos maneras:

- añadiendo `?debug=1` a la URL,
- definiendo `VITE_DEBUG_UI=true` en el build del frontend.

Si no se cumple ninguna de esas condiciones, el panel permanece desactivado.

## Comportamiento

Cuando está activo, la aplicación muestra un panel fijo en la parte superior con fondo amarillo. El panel está pensado para ser visible, plegable y seguro.

El panel muestra:

- estado del modo debug,
- ruta actual,
- endpoint GraphQL efectivo,
- si existe token de sesión en `localStorage`,
- últimos eventos del frontend,
- errores recientes de tipo `graphql`, `router`, `window.error` y `unhandledrejection`.

Además, incluye:

- botón para expandir o contraer,
- botón para limpiar eventos,
- botón para copiar el diagnóstico resumido al portapapeles.

## Fuentes de eventos

El modo debug recoge información de estas fuentes:

- `window.onerror`,
- `window.unhandledrejection`,
- navegación del router (`beforeEach`, `afterEach`, `onError`),
- peticiones GraphQL centralizadas mediante el cliente compartido.

## Seguridad

El panel está orientado a depuración funcional, no a volcado de secretos.

Por diseño:

- no muestra contraseñas,
- no muestra tokens completos,
- redacciona claves sensibles como `password`, `token`, `authorization`, `jwt` o `secret`,
- limita el historial a un número pequeño de eventos recientes.

## Casos de uso

Este modo es especialmente útil para:

- diagnosticar errores de login cuando la UI muestra mensajes genéricos,
- verificar si la URL efectiva de GraphQL es correcta,
- comprobar si una navegación posterior al login falla,
- copiar un resumen técnico para reportar incidencias sin abrir DevTools.

## Uso recomendado

- Activarlo en staging cuando haya una incidencia reproducible.
- Desactivarlo en el uso normal.
- Conservar los eventos mínimos y redactados.
- Evitar ampliar el panel con datos sensibles o dumps completos de respuestas.
