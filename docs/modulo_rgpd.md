# Módulo transversal de Protección de Datos (RGPD / LOPDGDD)

> Plan de trabajo. Documento vivo — se aborda cuando toque, tras cerrar los
> módulos en curso. Redactado 2026-05-20.

## 1. Propósito

SIGA trata datos personales de socios, voluntarios, donantes, usuarios y
terceros. Hoy el cumplimiento del RGPD está disperso (unos campos sueltos en la
ficha de socio) y es **manual**. Este módulo lo convierte en una capa
**transversal** que cualquier otro módulo (membresía, económico, actividades,
comunicación, documentación) consume, de modo que la protección de datos sea
*por diseño y por defecto* (art. 25 RGPD).

Marco legal: **Reglamento (UE) 2016/679 (RGPD)** y **Ley Orgánica 3/2018
(LOPDGDD)**.

## 2. Estado actual (ya implementado)

- Ficha de socio — panel "RGPD y privacidad":
  - `solicita_supresion_datos` + `fecha_solicitud_supresion`: el socio marca su
    solicitud de supresión desde *Mis datos*; la fecha se rellena sola.
  - `fecha_limite_retencion`: **calculada** (solo lectura) = fecha de baja + 6
    años (constante `ANIOS_RETENCION`).
  - Anonimización: mutación `anonimizar_miembro` — despoja al miembro de todos
    los datos identificativos (nombre, documento, contacto, dirección, IBAN,
    foto, observaciones) y conserva un registro "muñón" anonimizado. Solo sobre
    miembros de baja. Botón con confirmación, irreversible.
- Pendiente de elevar: todo lo demás de este documento.

## 3. Designación de responsables

Entidades y catálogos nuevos:

- **Responsable del tratamiento**: la organización (la asociación que instala
  SIGA). Datos identificativos, de contacto y registrales.
- **Delegado de Protección de Datos (DPD/DPO)**: opcional según art. 37 RGPD;
  obligatorio para algunas entidades. Persona o proveedor externo, con datos de
  contacto publicables.
- **Encargados del tratamiento**: proveedores que tratan datos por cuenta de la
  organización (hosting, pasarela de pago, email/SMTP, gestoría…). Cada uno con
  su **contrato de encargo** (art. 28 RGPD) registrado y fechado.
- **Personas autorizadas**: qué roles internos acceden a qué categorías de datos
  — se apoya en el RBAC existente (Transacciones/Roles).

## 4. Registro de Actividades de Tratamiento (RAT) — art. 30

Catálogo de **actividades de tratamiento**, cada una con:
- Finalidad (gestión de socios, cobro de cuotas, comunicación, voluntariado…).
- **Base jurídica** (art. 6 RGPD): ejecución de contrato, obligación legal,
  consentimiento, interés legítimo.
- Categorías de interesados y de datos (incluida la marca de **datos
  sensibles**, art. 9 — p. ej. salud para reducción de cuota).
- Encargados implicados.
- Plazo de conservación (enlaza con §6).
- Medidas de seguridad.

Exportable como documento RAT presentable ante la AEPD.

## 5. Derechos de los interesados (ARSULIPO)

Flujo unificado de ejercicio de derechos — **Acceso, Rectificación, Supresión,
Limitación, Portabilidad, Oposición** y decisiones automatizadas:

- Entidad `SolicitudDerechoRGPD`: interesado, tipo de derecho, fecha, estado
  (PRESENTADA → EN_TRÁMITE → RESUELTA / DENEGADA), resolución motivada.
- Plazo legal de respuesta: **1 mes** (prorrogable a 3). El sistema avisa.
- **Acceso / Portabilidad**: generación automática del volcado de datos del
  interesado (formato legible y estructurado).
- **Supresión**: ver §6 — resolución en dos fases.
- **Rectificación / Oposición / Limitación**: marcan el registro y restringen
  el tratamiento (p. ej. excluir de envíos).
- Modela el flujo formal que hoy es solo el check manual `solicita_supresion`.

## 6. Retención, bloqueo y supresión

El derecho de supresión (art. 17) **no es absoluto**: el art. 17.3.b) lo exceptúa
cuando hay obligación legal de conservar. Esto se resuelve con el **bloqueo de
datos** del art. 32 LOPDGDD.

### 6.1 Matriz de retención legal

| Dato | Norma | Plazo |
|---|---|---|
| Documentación contable y libros | Código de Comercio art. 30 | 6 años |
| Justificantes con efecto fiscal | Ley General Tributaria art. 66/70 | 4 años |
| Datos de socio sin obligación legal | RGPD — minimización | hasta baja + margen |
| Subvenciones públicas (si aplica) | normativa de la subvención | según convocatoria |

Configurable desde Parámetros Generales (hoy `ANIOS_RETENCION = 6` fijo).

### 6.2 Supresión en dos fases

1. **Inmediata** — al pedir supresión o causar baja: anonimización de los datos
   **personales identificativos** (lo que ya hace `anonimizar_miembro`).
2. **Diferida** — los **registros económicos** (cuotas, recibos, donaciones,
   apuntes, justificantes) no se borran: quedan **bloqueados** —conservados, de
   acceso restringido a jueces, tribunales y Administración tributaria— hasta
   vencer la retención legal. Cumplido el plazo, **purga definitiva**.

El "muñón" anonimizado del miembro se conserva como ancla referencial de esos
asientos. Una vez la persona es irreconocible, el asiento deja de ser dato
personal.

### 6.3 Purga automática

Job programado que, al vencer `fecha_limite_retencion`, elimina o anonimiza
definitivamente los registros bloqueados. Traza cada purga en el log de
auditoría.

## 7. Anonimización (ampliación)

- Extender más allá del miembro: usuario de acceso vinculado, contactos de
  comunicación, donantes no socios.
- Estrategia configurable: anonimización (irreversible, conserva estadística) vs.
  borrado completo, según la entidad y la base jurídica.

## 8. Consentimientos

- Entidad `Consentimiento`: interesado, finalidad, fecha, canal, texto/versión
  de la cláusula aceptada, estado (otorgado / retirado) y fecha de retirada.
- Prueba del consentimiento (art. 7.1): quién, cuándo, a qué versión.
- Casos: comunicaciones comerciales/informativas, cesión de imagen, tratamiento
  de datos de salud para reducción de cuota.

## 9. Brechas de seguridad

- Registro de **incidencias de seguridad**: detección, naturaleza, datos y
  personas afectadas, medidas.
- Asistente de **notificación a la AEPD en 72 h** (art. 33) y, si procede,
  comunicación a los afectados (art. 34).

## 10. Cláusulas informativas

- Catálogo de **textos informativos** versionados (art. 13/14): alta de socio,
  formulario de voluntariado, donaciones, formulario de contacto público.
- Se muestran en el punto de recogida del dato y se vinculan al consentimiento.

## 11. Seguridad de los datos

- Cifrado en reposo de identificadores sensibles (el `numero_documento` del
  miembro ya está dimensionado para dato cifrado — completar el cifrado real).
- **Log de auditoría** de accesos y cambios sobre datos personales: quién, qué,
  cuándo. Base para acreditar la *responsabilidad proactiva* (art. 5.2).
- Revisión del RBAC para que el acceso a datos personales y sensibles esté
  limitado por rol.

## 12. Integración transversal

| Módulo | Punto de contacto |
|---|---|
| Membresía | Ficha de socio, anonimización, solicitudes de derechos |
| Económico | Bloqueo y purga diferida de cuotas/recibos/donaciones |
| Comunicación interna | Respeta oposición/limitación; consentimiento de envíos |
| Documentación | Retención y purga de documentos con datos personales |
| Acceso (RBAC) | Personas autorizadas; log de auditoría |
| Configuración | Plazos de retención, datos del responsable y del DPD |

## 13. Fases de implementación sugeridas

1. **Catálogos base**: responsable, DPD, encargados, actividades de tratamiento
   (RAT). Datos del responsable a Parámetros Generales.
2. **Retención configurable + bloqueo + purga**: matriz de plazos, job de purga,
   formalizar el bloqueo de datos económicos.
3. **Flujo de derechos ARSULIPO**: entidad `SolicitudDerechoRGPD` y su gestión;
   sustituye el check manual de supresión.
4. **Consentimientos + cláusulas informativas** versionados.
5. **Brechas de seguridad** y asistente de notificación AEPD.
6. **Log de auditoría** de accesos a datos personales y cifrado en reposo.

## 14. Decisiones ya tomadas

- **D-RGPD.1** — La supresión se resuelve en dos fases: anonimización inmediata
  de datos personales + bloqueo y purga diferida de los datos económicos por
  obligación legal de conservación (art. 17.3.b RGPD, art. 32 LOPDGDD).
- **D-RGPD.2** — La anonimización conserva un registro "muñón" anonimizado del
  miembro como ancla de los asientos económicos; no se borra la fila.
- **D-RGPD.3** — `ANIOS_RETENCION = 6` (Código de Comercio); se hará
  configurable en Parámetros Generales.
