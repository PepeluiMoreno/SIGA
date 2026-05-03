MODULO DE MILITANCIA:

La aplicacion tendrá un feature_flag para distinguir cuando se va a manejar o no la extensión en agrupaciones_territoriales. 

Cada agrupación territorial tendrá una junta directiva con presidente, vicepresidente, secretario y tesorero como figuras fijas.  Y cada agrupacion tendra un mapa entre los cargos de la junta directiva y los roles de la aplicación.

Cada agrupacion territorial y tambien a nivel central se llevará un mapa que hace corresponder a los cargos, unos roles.

Por ejemplo:  presidente territorial:  diseño de campaña territorial, coordinación territorial de campaña estatal.

Y a los roles se les asignan funciones (trnasacciones):  por ejemplo al deseñador de campañas, se le dan los permisos para asignacion de recursos (presupuesto y horas de voluntariado, contratacion de servicios, alquiler de locales y equipamiento) 


Cada miembro que se ofrezca de colaborador declare su disponibilidad para trabajar. Y mantenga un calendario con un horario para señalar los días y tramos horarios en los que se puede contar con él. 

Un miembro que haya rellenado el calendario se convierte en voluntario, pero tambien puede haber voluntarios que no sean miembros (porque no pagan cuota, solo se registra el trabajo que hacen, no sus cuotas)

El miembro no solo mantiene sus datos personales, sus habilidades y su disponibilidad, sino puede consultar el histórico de las contribuciones tanto dinerarias (cuotas ordinarias, extraordinarias, donaciones) que ha hecho a la asociación como también el histórico de campañas en las que ha participado y con ello las tareas y el numero de horas dedicadas a esas tareas que ha ejecutado. 

El voluntario puede hacer lo mismo pero no verá historico de cuotas porque no las paga.


Hay que admitir que el usuario pueda modificar su cuota y la forma de pago de la misma, siempre dentro de unos límites mínimos. Se estableceran criterios de exención total o parcial de las cuotas. Por ejemplo: cuota joven (50%) mínimo 20€, situación de desempleo (80%), mínimo 10€.


Toda la información que puede mantener el usuario en la aplicación también puede ser introducida en su nombre, la persona al que se le asigne el rol adecuado en cada agrupacion territorial. Por ejemplo en "Cadiz Laica, el rol de gestión de la militancia se le asigna al secretario". Esta particularización de asignación de roles a cargos en las agrupaciones territoriales las tiene el presidente.


Hay que permitir que el miembro registre su traslado de una agrupación territorial a otra o que un coordinador de agrupación territorial pueda mover a un miembro, a petición de éste, de una agrupación a otra, notificando en ambos casos por la aplicación (si se impementa un modilo de comunicación interna) o por email, al coordinador de la agrupación de destino, tal circunstancia.

Consecuentemente habrá un histórico de las agrupaciones por las que ha pasado el miembro.

El flujo de registro y admisión de miembros consiste en los siguientes pasos:

1. El nuevo miembro rellena el formulario en la web y solicita su admisión.
2. El coordinador de la agrupación territorial en la que se registra, revisa la solicitud y la valida o la rechaza. Tanto en un caso como ptro  el miembro recibe un correo electrónico. 
3. En el caso de ser admitido, a través de un enlace en el correo de bienvenida, el miembro se confirma como tal y se anota ese dia como fecha de ingreso.  
4. La aplicación anuncia a la junta directiva y al coordinador de la agrupación territorial que el miembro ha sido confirmado.

ver /opt/docker/apps/SIGA/docs/modulos/administracion_usuarios_roles..md sobre indicaciones sobre sy implementacion

TODO: Sistema de eventos para reconstrucción automática de la Permission Matrix

Objetivo: mantener la PermissionMatrix en memoria coherente con cambios en roles, cargos, juntas y funcionalidades, sin recalcular permisos en cada request.



