# MÓDULO DE COBROS CON PAYPAL

## 1. OBJETIVO

Implementar un submódulo de pagos que permita:

* Gestión de **donaciones puntuales**
* Gestión de **cuotas recurrentes anuales**
* Auditoría completa de todos los eventos
* Soporte para **usuarios autenticados y donaciones anónimas**
* Preparación para múltiples proveedores futuros

---

## 2. ALCANCE

Incluye:

* Integración con API de PayPal (Orders + Subscriptions)
* Procesamiento de webhooks
* Persistencia de pagos, suscripciones y eventos
* Generación de recibos
* Gestión de reembolsos
* API GraphQL (Strawberry)

Excluye:

* UI frontend (solo contratos)
* Integración con otros proveedores (aunque se prepara)

---

## 3. REQUISITOS FUNCIONALES

### 3.1 Donaciones

* Permitir donaciones con importe variable
* Permitir donaciones anónimas
* Redirigir al usuario a PayPal para completar el pago
* Registrar el pago solo tras confirmación por webhook
* Generar recibo tras pago completado
* Enviar notificación por email

---

### 3.2 Cuotas (Suscripciones)

* Permitir cuotas anuales con importe variable
* Requiere usuario autenticado
* Crear suscripción en PayPal
* Registrar activación mediante webhook
* Registrar cada cobro como un pago independiente
* Permitir cancelación de suscripción

---

### 3.3 Reembolsos

* Permitir reembolso total o parcial
* Solo sobre pagos completados
* Registrar operación en el sistema
* Sin automatismos

---

### 3.4 Consulta de información

* Listado de pagos del usuario
* Consulta de estado de pago
* Consulta de suscripción activa
* Histórico unificado con otros medios de pago

---

### 3.5 Auditoría

* Registrar todos los eventos de PayPal
* Persistir payload completo (json)
* Garantizar trazabilidad completa

---

## 4. REQUISITOS NO FUNCIONALES

### 4.1 Consistencia

* El estado del sistema se basa exclusivamente en webhooks
* El frontend no puede determinar estados de pago

---

### 4.2 Idempotencia

* Procesamiento de webhooks idempotente
* Eventos duplicados deben ser ignorados

---

### 4.3 Concurrencia

* Control mediante locking a nivel de fila
* Evitar condiciones de carrera

---

### 4.4 Seguridad

* Verificación obligatoria de firma de webhook
* Uso de HTTPS
* No exposición de identificadores externos

---

### 4.5 Auditoría

* No eliminación de eventos
* No sobrescritura sin registro histórico

---

## 5. MODELO DE DATOS

### 5.1 Pago

* id
* proveedor
* id_externo
* tipo (DONACION | SUSCRIPCION)
* importe
* moneda
* estado
* email_pagador
* usuario_id (nullable)
* referencia_interna
* fecha_creacion
* fecha_completado

---

### 5.2 Suscripcion

* id
* usuario_id
* proveedor
* id_externo
* importe
* moneda
* estado
* fecha_inicio
* fecha_proximo_cobro

---

### 5.3 EventoPago

* id
* pago_id (nullable)
* proveedor
* tipo_evento
* id_evento_externo
* payload
* fecha_creacion

---

### 5.4 Reembolso

* id
* pago_id
* importe
* motivo
* estado
* id_externo
* fecha_creacion

---

## 6. FLUJOS PRINCIPALES

### 6.1 Donación

1. Crear pago en estado CREADO
2. Redirigir a PayPal
3. Usuario completa pago
4. Recepción de webhook
5. Validación y procesamiento
6. Actualización a COMPLETADO
7. Generación de recibo y notificación

---

### 6.2 Suscripción

1. Crear suscripción en PayPal
2. Redirigir usuario
3. Webhook de activación
4. Creación de suscripción local
5. Webhook de cobro periódico
6. Creación de pago asociado

---

## 7. WEBHOOKS

### 7.1 Requisitos

* Endpoint dedicado
* Verificación de firma
* Procesamiento transaccional
* Persistencia previa al procesamiento

---

### 7.2 Eventos relevantes

* PAYMENT.CAPTURE.COMPLETED
* PAYMENT.CAPTURE.DENIED
* BILLING.SUBSCRIPTION.ACTIVATED
* BILLING.SUBSCRIPTION.CANCELLED
* PAYMENT.SALE.COMPLETED

---

## 8. API GRAPHQL

### Mutations

* crearDonacion
* crearSuscripcion
* cancelarSuscripcion
* reembolsarPago

---

### Queries

* pagos
* pago
* miSuscripcion

---

## 9. REGLAS DE NEGOCIO

* Un pago solo se marca como COMPLETADO mediante webhook
* No se permiten transiciones inversas
* Los importes no se modifican tras creación
* Los eventos son fuente de verdad

---

## 10. INTEGRACIÓN CON FRONTEND

* Redirección completa a PayPal
* Página de resultado propia
* Consulta de estado mediante API
* No uso de parámetros de retorno para lógica

---

## 11. EXTENSIBILIDAD

El sistema debe permitir:

* Añadir nuevos proveedores sin modificar lógica existente
* Mantener API GraphQL estable
* Reutilizar modelo de datos

---

## 12. TESTING

Debe cubrir:

* Transiciones de estado
* Idempotencia
* Webhooks simulados
* Concurrencia
* Constraints de base de datos

---

## 13. DESPLIEGUE

* Uso de entorno sandbox y producción
* Configuración de credenciales
* Registro de webhook en PayPal
* Validación end-to-end antes de producción

---

## 14. CRITERIOS DE ACEPTACIÓN

* Pago completado solo vía webhook
* No duplicidad de eventos
* Auditoría completa disponible
* Reembolsos funcionales
* Suscripciones activas correctamente reflejadas
* Sistema estable ante concurrencia

---

## 15. RIESGOS CONTROLADOS

* Eventos duplicados → mitigado por idempotencia
* Desorden de eventos → mitigado por modelo de estados
* Fallos de red → mitigado por reintentos
* Inconsistencias → mitigadas por auditoría

---

## 16. RESULTADO ESPERADO

Submódulo robusto, auditado, extensible y desacoplado del proveedor, capaz de gestionar pagos reales en producción sin dependencia del frontend ni inconsistencias de estado.
