
# Instrucciones — rama feature/reglas-recibos-paypal

## 1. Subir la rama al repositorio remoto

```bash
cd SIGA

# Opción A — si tienes el repo clonado con la rama anterior ya pusheada:
git checkout feature/reglas-recibos-paypal  # o crearla desde feature/tesoreria-contabilidad
git am reglas_recibos_paypal.patch
git push origin feature/reglas-recibos-paypal

# Opción B — aplicar el patch sobre la rama anterior:
git checkout feature/tesoreria-contabilidad
git checkout -b feature/reglas-recibos-paypal
git am reglas_recibos_paypal.patch
git push origin feature/reglas-recibos-paypal
```

## 2. Migración (solo Feature A — reglas_contables)

```bash
alembic upgrade b1c2d3e4f5a6
```

## 3. Seeds (ejecutar tras la migración)

```python
# En el script de inicialización del sistema:
from app.scripts.seeding.reglas_contables_default import cargar_reglas_contables
await cargar_reglas_contables(session)
```

Esto carga 9 reglas por defecto (CUOTA/DONACION/REMESA/PAGO → cuentas PCESFL).

## 4. Dependencias Python nuevas

```bash
pip install weasyprint   # Recibos PDF
pip install httpx        # Ya debería estar para FastAPI
```

WeasyPrint requiere librerías del sistema operativo en producción:
```bash
# Ubuntu/Debian
apt-get install libpango-1.0-0 libpangoft2-1.0-0 libcairo2
```

## 5. Variables de entorno — PayPal

Añadir al `.env`:
```
PAYPAL_CLIENT_ID=AXxxxxxxxxxxxx
PAYPAL_CLIENT_SECRET=EXxxxxxxxxxxxx
PAYPAL_MODE=sandbox           # sandbox en desarrollo, live en producción
PAYPAL_WEBHOOK_ID=WHxxxxxx    # ID del webhook creado en PayPal Dashboard
```

Para el frontend (en `.env` de Vue):
```
VITE_PAYPAL_CLIENT_ID=AXxxxxxxxxxxxx
```

## 6. Configurar webhook en PayPal Dashboard

1. Ir a https://developer.paypal.com/dashboard/
2. Apps & Credentials → tu app → Webhooks
3. Añadir URL: `https://tu-dominio.com/api/paypal/webhook`
4. Eventos: PAYMENT.CAPTURE.COMPLETED, PAYMENT.CAPTURE.DENIED,
   PAYMENT.CAPTURE.REVERSED, BILLING.SUBSCRIPTION.CANCELLED
5. Copiar el Webhook ID al .env como PAYPAL_WEBHOOK_ID

## 7. Usar PayPalButton en Vue

```vue
<PayPalButton
  :importe="cuota.importe"
  concepto="Cuota de socio 2026"
  :cuota-id="cuota.id"
  :miembro-id="miembro.id"
  :cuenta-bancaria-id="cuentaPrincipalId"
  :client-id="$env.VITE_PAYPAL_CLIENT_ID"
  @pago-completado="onPagoCompletado"
/>
```

## 8. Recibos PDF — endpoints

```
GET /api/recibos/cuota/{cuota_id}    → PDF recibo cuota anual
GET /api/recibos/apunte/{apunte_id}  → PDF justificante de movimiento
```

Ejemplo de enlace en Vue:
```vue
<a :href="`/api/recibos/cuota/${cuota.id}`" target="_blank">
  Descargar recibo PDF
</a>
```

## 9. Reglas contables — administración

Ruta: `/reglas-contables`

Permite crear/editar/desactivar reglas sin modificar código. El RegistroContable
consulta la BD primero; si no hay reglas activas, usa el mapa hardcodeado de fallback.

## Resumen de archivos nuevos

| Archivo | Descripción |
|---------|-------------|
| `models/contabilidad/regla_contable.py` | Modelo ReglaContable |
| `services/reglas_contables_service.py` | CRUD + resolver_cuentas |
| `services/registro_contable.py` | Actualizado: BD + fallback |
| `scripts/seeding/reglas_contables_default.py` | Seed 9 reglas PCESFL |
| `alembic/.../b1c2d3e4f5a6_add_reglas_contables.py` | Migración |
| `services/pdf/recibo_service.py` | Generación HTML→PDF |
| `api/recibos.py` | Endpoints REST PDF |
| `api/paypal.py` | Endpoints REST PayPal |
| `services/paypal_service.py` | Cliente PayPal REST v2 |
| `components/paypal/PayPalButton.vue` | Botón PayPal SDK |
| `views/financiero/ReglasContables.vue` | Admin de reglas |
