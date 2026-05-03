# Módulo Cobro

Integración con pasarelas de pago externas (PayPal, Bizum, Stripe, TPV...).

## Responsabilidad

`cobro` es el **adaptador de entrada de dinero digital**. No gestiona la lógica de negocio de cuotas o donaciones — eso corresponde al subdominio `cuotas` y `donaciones` dentro de `financiero`.

Cuando un `Pago` pasa a estado `COMPLETADO`, genera un `MovimientoTesoreria` en tesorería.

## Entidades

- **ProveedorPago** — catálogo de pasarelas disponibles
- **Pago** — transacción registrada (ID externo, webhook, estado)
- **Suscripcion** — pago recurrente activo en una pasarela

## Transacciones

Prefijos: `PAY_*`
