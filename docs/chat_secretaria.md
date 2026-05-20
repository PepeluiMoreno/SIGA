Resumen funcional: módulo de secretaría para gestión de asociaciones

1. Ámbito del módulo
La secretaría es el núcleo administrativo y legal de la asociación. Gestiona tres grandes áreas:

Gobierno interno: órganos, cargos, reuniones y acuerdos
Registro de socios: altas, bajas, datos y cuotas
Documentación legal: libro de socios, actas, estatutos, comunicaciones con registros


2. Gestión de socios
Entidad de datos mínima
CampoDetalleNIF/NIE/PasaporteIdentificación fiscalNombre y apellidosO razón social si es entidadFecha de nacimientoPara control de socios menores si aplicaDirección postalPara notificaciones oficialesEmail + teléfonoComunicación habitualFecha de altaInicio de la relación asociativaNúmero de socioCorrelativo, inamovible aunque cause bajaTipo de socioOrdinario / fundador / honorífico / colaborador…EstadoActivo / baja voluntaria / baja por impago / fallecidoFecha de bajaY motivoCuota asignadaVinculada al tipo de socio o tramo
Flujo de alta
Solicitud de adhesión
      ↓
Revisión por Junta (si los estatutos lo exigen)
      ↓
Aprobación → asignación de número de socio
      ↓
Notificación al interesado
      ↓
Primera cuota generada
      ↓
Inscripción en el Libro de Socios
Bajas

Voluntaria: a petición del socio, efecto inmediato o al cierre del ejercicio según estatutos
Por impago: tras N cuotas impagadas, con notificación previa obligatoria
Por sanción: requiere expediente disciplinario y acuerdo de Junta
El número de socio nunca se reutiliza


3. Libro de Socios
Obligatorio por la Ley Orgánica 1/2002 de asociaciones. El módulo debe mantenerlo actualizado automáticamente y permitir:

Exportación en PDF oficial en cualquier momento
Histórico de todos los socios, incluidos los que causaron baja
Fecha y motivo de cada cambio de estado
Estar disponible para inspección por la autoridad registral


4. Órganos de gobierno
La mayoría de asociaciones tienen al menos:
ÓrganoComposición habitualAsamblea GeneralTodos los sociosJunta DirectivaPresidente, Vicepresidente, Secretario, Tesorero, Vocales
El módulo debe gestionar:

Cargos vigentes: quién ocupa cada cargo y desde cuándo
Mandatos: duración según estatutos, alerta de vencimiento próximo
Histórico de cargos: quién ocupó cada puesto en cada período
Incompatibilidades si los estatutos las establecen


5. Convocatorias y reuniones
Flujo de una reunión
Convocatoria (con antelación estatutaria mínima)
      ↓
Envío a los convocados (email + registro de envío)
      ↓
Celebración → quórum (ordinario / reforzado según el tipo de acuerdo)
      ↓
Desarrollo: orden del día, intervenciones relevantes, votaciones
      ↓
Acta borrador → revisión del Secretario
      ↓
Aprobación del acta (en la misma reunión o en la siguiente)
      ↓
Firma (Secretario + Presidente)
      ↓
Archivo en el Libro de Actas
Datos de cada reunión
CampoDetalleTipoAsamblea ordinaria / extraordinaria / Junta DirectivaCarácterPrimera / segunda convocatoriaFecha, hora y lugarO plataforma si es telemáticaConvocadosLista con registro de asistenciaQuórumCálculo automático según tipo de acuerdoOrden del díaPuntos numeradosAcuerdosVinculados a cada punto del orden del díaVotacionesA favor / en contra / abstenciones por acuerdoDocumentos adjuntosConvocatoria, informes previos, acta firmada
Tipos de quórum más habituales

Ordinario: mayoría simple de presentes/representados
Reforzado: mayoría absoluta de socios (modificación de estatutos, disolución…)
El módulo debe calcular automáticamente si hay quórum suficiente según el tipo de acuerdo


6. Libro de Actas
También obligatorio por la Ley 1/2002. El módulo debe:

Numerar las actas correlativamente por tipo de órgano
Generar el PDF con el formato correcto (lugar, fecha, asistentes, acuerdos, firmas)
Registrar la fecha de aprobación del acta
Permitir certificar acuerdos concretos (el Secretario extrae un certificado de un acuerdo específico para presentarlo ante terceros)


7. Certificados de acuerdos
Documento habitual que pide bancos, registros y organismos públicos. Debe generarse desde el módulo con:

Identificación del órgano y reunión
Transcripción literal del acuerdo certificado
Fecha de adopción y de aprobación del acta
Firma del Secretario con el visto bueno del Presidente


8. Comunicaciones con el Registro de Asociaciones
El módulo debe alertar y facilitar la documentación para:
HechoObligación registralModificación de estatutosInscripción en el RegistroCambio de Junta DirectivaComunicación en plazo (1 mes habitual)Cambio de domicilio socialComunicación al RegistroDisoluciónInscripción de la liquidación
No presenta telemáticamente (eso lo hace el usuario), pero genera los documentos necesarios.

9. Gestión documental mínima
DocumentoGenerado por el móduloLibro de Socios✅ Automático, siempre actualizadoLibro de Actas✅ Por reunión, con numeración correlativaConvocatorias✅ Con registro de envíoCertificados de acuerdo✅ A demandaCartas de baja/alta✅ Plantillas personalizablesEstatutos vigentes📎 Adjunto, con control de versiones

10. Cuotas de socios (intersección con tesorería)
La secretaría define, tesorería ejecuta:

El módulo de secretaría establece los tipos de cuota y a qué tipo de socio aplica
Genera la remesa de recibos (mensual/trimestral/anual)
Registra impagos y dispara el proceso de baja por impago
Emite el justificante de pago de cuota (distinto al certificado de donación)


11. Protección de datos (RGPD / LOPDGDD)
Obligatorio para cualquier asociación que trate datos de personas físicas:

Base legal del tratamiento: interés legítimo o ejecución de contrato asociativo
Registro de actividades de tratamiento (RAT) — el módulo debe exportarlo
Cláusula informativa en el formulario de alta
Derecho de supresión: baja del socio → anonimización de datos personales (pero conservando el número de socio y los datos fiscales el tiempo legalmente exigido)
Acceso restringido por roles (no todos los usuarios ven datos de otros socios)


12. Informes mínimos del módulo

Censo de socios activos por tipo y fecha de alta
Altas y bajas en el período: evolución del asociacionismo
Mandatos próximos a vencer: alertas para renovación de Junta
Reuniones pendientes de acta aprobada: control de tareas del Secretario
Socios con cuota impagada: para iniciar proceso de baja


13. Prioridad de implementación sugerida

CRUD de socios + Libro de Socios exportable
Gestión de cargos y mandatos
Convocatorias + registro de asistencia + quórum automático
Generación de actas y Libro de Actas
Certificados de acuerdos
Gestión de cuotas (integrada con tesorería)
Alertas registrales y de mandatos
Capa RGPD (anonimización, RAT, roles)


Conexiones con otros módulos
FunciónMódulo relacionadoCuotas e impagosTesoreríaDonaciones de sociosDonacionesSubvenciones aprobadas en JuntaSubvencionesComunicaciones masivasComunicaciones / CRMFirma electrónica de actasDocumentos