modulo de donaciones en una aplicacion de gestion integral de asociaciones13:39Claude respondió: Resumen funcional: módulo de donaciones para gestión de asociacionesResumen funcional: módulo de donaciones para gestión de asociaciones

1. Entidad de datos mínima por donación
Cada registro de donación debe almacenar:
CampoDetalleDonanteNIF/NIE/CIF + nombre completo o razón socialImporteEn euros, con dos decimalesFechaDe recepción efectiva del dineroTipoDineraria / en especieForma de pagoTransferencia, domiciliación, efectivo, tarjeta…Referencia bancariaPara trazabilidad contableCarácterPuntual / recurrenteEstadoRecibida / certificada / anuladaEjercicio fiscalAño al que imputa (normalmente el de cobro)

2. Flujo básico de una donación
Entrada de donación
      ↓
Registro en el sistema (con todos los campos)
      ↓
Validación (importe > 0, donante identificado, forma de pago válida)
      ↓
Asiento contable automático (cuenta 730 o equivalente PGC-ESFL)
      ↓
Generación del certificado PDF (firmado/sellado)
      ↓
Envío al donante (email o descarga)
      ↓
Acumulación para el Modelo 182

3. Certificado de donación (campos obligatorios)
El PDF generado debe incluir obligatoriamente:

NIF + denominación de la asociación
NIF + nombre completo del donante
Importe y fecha
Tipo de donación (dineraria/especie) y forma de pago
Literal: "La entidad está acogida al régimen especial de la Ley 49/2002" (si aplica)
Literal: "La donación es irrevocable, pura y simple"
Número de certificado (para registro interno)
Firma/sello de la entidad


4. Modelo 182 — lo que el módulo debe acumular
El fichero que se presenta a Hacienda en enero requiere, por donante:

NIF donante + NIF entidad
Importe total donado en el ejercicio
Clave de tipo de donación (A=dineraria, B=especie, C=cuotas…)
Indicador de recurrencia (≥3 años con incremento → tipo reforzado)
Si tiene derecho a deducción autonómica adicional

El módulo debe agregar automáticamente por donante y ejercicio, y exportar en formato BOE (longitud fija) o al menos en CSV estructurado para importación en el programa de declaraciones.

5. Donaciones recurrentes

Domiciliaciones SEPA: el módulo debe gestionar el mandato SEPA (referencia única de mandato, fecha de firma, BIC/IBAN)
Generación automática de cargos periódicos (mensual, trimestral, anual)
Cada cargo genera su propio registro de donación con fecha real de cobro
Si un cargo rebota → estado "fallido", notificación interna, no se certifica


6. Donaciones en especie

Descripción del bien + valoración a precio de mercado
Documento de valoración adjunto (factura, tasación)
El certificado debe reflejar la valoración, no el importe monetario
No generan movimiento bancario, pero sí asiento contable


7. Contabilidad automática (PGC-ESFL)
Cada donación registrada debe provocar al menos:
DEBE                          HABER
570 Caja / 572 Banco    →    730 Subvenciones, donaciones y legados
Si la aplicación lleva contabilidad integrada, el asiento debe generarse automáticamente al confirmar la donación.

8. Informes mínimos del módulo

Libro de donaciones: listado cronológico con todos los campos
Resumen por donante y ejercicio: para preparar el 182 y para control interno
Donaciones pendientes de certificar: para no dejar donantes sin su justificante
Recurrentes activos/inactivos: control de mandatos SEPA vigentes
Comparativo interanual: evolución de ingresos por donaciones


9. Lo que el módulo NO debe gestionar (pero debe conectar)
FunciónMódulo responsableSocios y cuotasMódulo de socios (cuotas ≠ donaciones fiscalmente)Subvenciones públicasMódulo de subvenciones (régimen distinto)Presentación telemática del 182AEAT (el módulo exporta, no presenta)Firma electrónica del certificadoMódulo de documentos / certificados

Prioridad de implementación sugerida

CRUD de donaciones con validación de datos
Generación de certificado PDF
Agregación por donante/ejercicio + exportación para el 182
Donaciones recurrentes con gestión de mandatos SEPA
Integración contable automática
Informes y cuadro de mando