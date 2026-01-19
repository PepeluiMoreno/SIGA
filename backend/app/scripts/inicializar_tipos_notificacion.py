"""Script para inicializar los tipos de notificación del sistema."""

import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..domains.notificaciones.models import TipoNotificacion


# Tipos de notificación por defecto
TIPOS_NOTIFICACION = [
    # SISTEMA
    {
        'codigo': 'BIENVENIDA',
        'nombre': 'Bienvenida al Sistema',
        'descripcion': 'Notificación de bienvenida para nuevos usuarios',
        'categoria': 'SISTEMA',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': False,
        'permite_inapp': True,
        'prioridad': 'NORMAL',
        'requiere_accion': False,
        'template_asunto': 'Bienvenido a AIEL',
        'template_cuerpo': 'Hola {nombre}, bienvenido al sistema AIEL.',
        'icono': 'user-plus',
        'color': 'primary',
    },
    {
        'codigo': 'CAMBIO_CONTRASENA',
        'nombre': 'Cambio de Contraseña',
        'descripcion': 'Notificación cuando se cambia la contraseña',
        'categoria': 'SISTEMA',
        'permite_email': True,
        'permite_sms': True,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'ALTA',
        'requiere_accion': False,
        'template_asunto': 'Contraseña Modificada',
        'template_cuerpo': 'Tu contraseña ha sido modificada exitosamente.',
        'icono': 'lock',
        'color': 'warning',
    },
    {
        'codigo': 'LOGIN_SOSPECHOSO',
        'nombre': 'Login Sospechoso',
        'descripcion': 'Alerta de inicio de sesión desde ubicación no habitual',
        'categoria': 'SISTEMA',
        'permite_email': True,
        'permite_sms': True,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'URGENTE',
        'requiere_accion': True,
        'template_asunto': 'Inicio de Sesión Detectado',
        'template_cuerpo': 'Se detectó un inicio de sesión desde {ubicacion}. Si no fuiste tú, cambia tu contraseña inmediatamente.',
        'icono': 'alert-triangle',
        'color': 'danger',
    },

    # FINANCIERO
    {
        'codigo': 'CUOTA_COBRADA',
        'nombre': 'Cuota Cobrada',
        'descripcion': 'Confirmación de cobro de cuota anual',
        'categoria': 'FINANCIERO',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'NORMAL',
        'requiere_accion': False,
        'template_asunto': 'Cuota Cobrada - {ejercicio}',
        'template_cuerpo': 'Tu cuota de {importe}€ para el ejercicio {ejercicio} ha sido cobrada correctamente.',
        'icono': 'check-circle',
        'color': 'success',
    },
    {
        'codigo': 'CUOTA_IMPAGADA',
        'nombre': 'Cuota Impagada',
        'descripcion': 'Notificación de fallo en el cobro de cuota',
        'categoria': 'FINANCIERO',
        'permite_email': True,
        'permite_sms': True,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'ALTA',
        'requiere_accion': True,
        'template_asunto': 'Error en Cobro de Cuota',
        'template_cuerpo': 'No se pudo cobrar tu cuota de {importe}€. Por favor, actualiza tu método de pago.',
        'icono': 'x-circle',
        'color': 'danger',
    },
    {
        'codigo': 'CUOTA_PROXIMA',
        'nombre': 'Cuota Próxima',
        'descripcion': 'Recordatorio de próximo cobro de cuota',
        'categoria': 'FINANCIERO',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'NORMAL',
        'requiere_accion': False,
        'template_asunto': 'Próximo Cobro de Cuota',
        'template_cuerpo': 'Se cobrará tu cuota de {importe}€ el día {fecha}.',
        'icono': 'calendar',
        'color': 'info',
    },
    {
        'codigo': 'DONACION_RECIBIDA',
        'nombre': 'Donación Recibida',
        'descripcion': 'Confirmación de recepción de donación',
        'categoria': 'FINANCIERO',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'NORMAL',
        'requiere_accion': False,
        'template_asunto': 'Donación Recibida',
        'template_cuerpo': 'Hemos recibido tu donación de {importe}€. ¡Muchas gracias!',
        'icono': 'heart',
        'color': 'success',
    },
    {
        'codigo': 'CERTIFICADO_DONACION',
        'nombre': 'Certificado de Donación',
        'descripcion': 'Certificado fiscal de donaciones disponible',
        'categoria': 'FINANCIERO',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'NORMAL',
        'requiere_accion': True,
        'template_asunto': 'Certificado de Donaciones {ejercicio}',
        'template_cuerpo': 'Tu certificado de donaciones del ejercicio {ejercicio} está disponible para descarga.',
        'icono': 'file-text',
        'color': 'info',
    },

    # CAMPAÑA
    {
        'codigo': 'CAMPANA_INICIADA',
        'nombre': 'Campaña Iniciada',
        'descripcion': 'Notificación de inicio de nueva campaña',
        'categoria': 'CAMPANA',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'NORMAL',
        'requiere_accion': False,
        'template_asunto': 'Nueva Campaña: {nombre_campana}',
        'template_cuerpo': 'Se ha iniciado la campaña "{nombre_campana}".',
        'icono': 'megaphone',
        'color': 'primary',
    },
    {
        'codigo': 'CAMPANA_FINALIZADA',
        'nombre': 'Campaña Finalizada',
        'descripcion': 'Notificación de finalización de campaña',
        'categoria': 'CAMPANA',
        'permite_email': False,
        'permite_sms': False,
        'permite_push': False,
        'permite_inapp': True,
        'prioridad': 'BAJA',
        'requiere_accion': False,
        'icono': 'check',
        'color': 'success',
    },
    {
        'codigo': 'INVITACION_EVENTO',
        'nombre': 'Invitación a Evento',
        'descripcion': 'Invitación a participar en evento',
        'categoria': 'CAMPANA',
        'permite_email': True,
        'permite_sms': True,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'ALTA',
        'requiere_accion': True,
        'template_asunto': 'Invitación: {nombre_evento}',
        'template_cuerpo': 'Estás invitado al evento "{nombre_evento}" el día {fecha}.',
        'template_sms': 'Invitación a {nombre_evento} el {fecha}. Confirma tu asistencia.',
        'icono': 'calendar-check',
        'color': 'primary',
    },

    # TAREA
    {
        'codigo': 'TAREA_ASIGNADA',
        'nombre': 'Tarea Asignada',
        'descripcion': 'Nueva tarea asignada al usuario',
        'categoria': 'TAREA',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'NORMAL',
        'requiere_accion': True,
        'template_asunto': 'Nueva Tarea Asignada',
        'template_cuerpo': 'Se te ha asignado la tarea "{titulo_tarea}".',
        'icono': 'clipboard',
        'color': 'info',
    },
    {
        'codigo': 'TAREA_VENCIMIENTO',
        'nombre': 'Tarea por Vencer',
        'descripcion': 'Recordatorio de tarea próxima a vencer',
        'categoria': 'TAREA',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'ALTA',
        'requiere_accion': True,
        'template_asunto': 'Tarea por Vencer',
        'template_cuerpo': 'La tarea "{titulo_tarea}" vence el {fecha_vencimiento}.',
        'icono': 'clock',
        'color': 'warning',
    },
    {
        'codigo': 'TAREA_COMPLETADA',
        'nombre': 'Tarea Completada',
        'descripcion': 'Confirmación de tarea completada',
        'categoria': 'TAREA',
        'permite_email': False,
        'permite_sms': False,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'BAJA',
        'requiere_accion': False,
        'icono': 'check-circle',
        'color': 'success',
    },

    # MIEMBRO
    {
        'codigo': 'NUEVO_MIEMBRO',
        'nombre': 'Nuevo Miembro',
        'descripcion': 'Notificación de alta de nuevo miembro',
        'categoria': 'MIEMBRO',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': False,
        'permite_inapp': True,
        'prioridad': 'BAJA',
        'requiere_accion': False,
        'template_asunto': 'Nuevo Miembro Registrado',
        'template_cuerpo': 'Se ha registrado un nuevo miembro: {nombre_miembro}.',
        'icono': 'user-plus',
        'color': 'success',
    },
    {
        'codigo': 'BAJA_MIEMBRO',
        'nombre': 'Baja de Miembro',
        'descripcion': 'Notificación de baja de miembro',
        'categoria': 'MIEMBRO',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': False,
        'permite_inapp': True,
        'prioridad': 'NORMAL',
        'requiere_accion': False,
        'template_asunto': 'Baja de Miembro',
        'template_cuerpo': 'El miembro {nombre_miembro} ha causado baja.',
        'icono': 'user-minus',
        'color': 'warning',
    },
    {
        'codigo': 'DATOS_ACTUALIZADOS',
        'nombre': 'Datos Actualizados',
        'descripcion': 'Confirmación de actualización de datos personales',
        'categoria': 'MIEMBRO',
        'permite_email': True,
        'permite_sms': False,
        'permite_push': True,
        'permite_inapp': True,
        'prioridad': 'NORMAL',
        'requiere_accion': False,
        'template_asunto': 'Datos Actualizados',
        'template_cuerpo': 'Tus datos personales han sido actualizados correctamente.',
        'icono': 'edit',
        'color': 'info',
    },
]


async def inicializar_tipos_notificacion(session: AsyncSession) -> None:
    """Inicializa los tipos de notificación del sistema."""
    print("\n=== Inicializando Tipos de Notificación ===\n")

    count_creados = 0
    count_existentes = 0

    for tipo_data in TIPOS_NOTIFICACION:
        result = await session.execute(
            select(TipoNotificacion).where(TipoNotificacion.codigo == tipo_data['codigo'])
        )
        existe = result.scalar_one_or_none()

        if not existe:
            tipo = TipoNotificacion(
                id=uuid.uuid4(),
                **tipo_data
            )
            session.add(tipo)
            print(f"  * Tipo creado: {tipo_data['codigo']} - {tipo_data['nombre']}")
            count_creados += 1
        else:
            print(f"  - Tipo ya existe: {tipo_data['codigo']}")
            count_existentes += 1

    await session.commit()

    print(f"\n=== Tipos de notificación inicializados ===")
    print(f"Creados: {count_creados} | Existentes: {count_existentes} | Total: {len(TIPOS_NOTIFICACION)}\n")


# Función main para ejecutar el script directamente
async def main():
    """Función principal para ejecutar el script."""
    from ..infrastructure.database import get_session

    async with get_session() as session:
        await inicializar_tipos_notificacion(session)


if __name__ == "__main__":
    asyncio.run(main())
