"""Seed: descripciones en lenguaje llano del plan de cuentas PCESFL 2013.

Asigna a cada cuenta una explicación breve y NO técnica, pensada para un tesorero
no profesional. Idempotente: actualiza solo si la descripción actual está vacía o
es genérica; sobrescribe siempre las cuentas listadas explícitamente aquí.

Uso (dentro del contenedor backend):
  docker exec siga_dev_backend python -m app.scripts.seeding.descripciones_cuentas
"""

import asyncio
from sqlalchemy import update

from app.core.database import async_session
from app.modules.economico.models.contabilidad import CuentaContable


# (codigo, descripcion)
DESCRIPCIONES: dict[str, str] = {
    # ─── Grupo 1: Financiación básica ───────────────────────────────────────
    "1":   "Patrimonio de la entidad: dinero aportado al constituirla, reservas acumuladas y deudas a más de un año.",
    "10":  "Dinero que los socios/fundadores aportan para iniciar la entidad. No se devuelve.",
    "100": "Aportación inicial de los socios fundadores. Se mantiene a lo largo de la vida de la entidad.",
    "11":  "Excedentes de años anteriores que la entidad decide no gastar y reservar para el futuro.",
    "110": "Reservas obligadas por los estatutos (porcentaje del excedente anual).",
    "119": "Otras reservas voluntarias acordadas por la asamblea.",
    "12":  "Ganancias o pérdidas de ejercicios anteriores pendientes de aplicar.",
    "120": "Excedente de años anteriores que aún no se ha asignado a reservas u otra finalidad.",
    "121": "Pérdidas acumuladas de años anteriores pendientes de compensar con excedentes futuros.",
    "129": "Ganancia o pérdida del año actual, una vez cerradas todas las cuentas. Si es positivo es \"excedente\"; si es negativo, déficit.",
    "13":  "Donaciones y subvenciones recibidas para fines plurianuales (no se imputan todas al año en que se reciben).",
    "130": "Subvenciones recibidas de administraciones públicas para inversiones a varios años.",
    "132": "Donaciones y herencias recibidas con destino al patrimonio (no al gasto del año).",
    "14":  "Cantidades reservadas por obligaciones futuras todavía no facturadas (litigios, indemnizaciones...).",
    "142": "Provisión por posibles responsabilidades legales o demandas.",
    "16":  "Préstamos y créditos bancarios a devolver en más de un año.",
    "160": "Préstamo bancario con plazo de devolución superior a 12 meses.",
    "17":  "Otras deudas a más de un año (no bancarias).",
    "170": "Deudas con plazo superior a 12 meses con proveedores o particulares.",
    "18":  "Fianzas y garantías que la entidad guarda y debe devolver a más de un año.",
    "180": "Fianzas recibidas (por ejemplo, alquileres) que se devolverán en más de un año.",

    # ─── Grupo 2: Activo no corriente (inversiones a largo plazo) ───────────
    "2":   "Bienes y derechos que la entidad usa por más de un año: locales, ordenadores, programas, vehículos, etc.",
    "20":  "Bienes inmateriales: software, marcas, patentes, licencias.",
    "200": "Gastos invertidos en investigación y desarrollo propios.",
    "201": "Concesiones administrativas (uso de espacios públicos, licencias).",
    "202": "Marcas, patentes y otros derechos de propiedad industrial.",
    "203": "Libros, publicaciones y archivos editados por la entidad.",
    "206": "Programas informáticos comprados o desarrollados.",
    "209": "Otros bienes inmateriales no incluidos arriba.",
    "21":  "Bienes físicos duraderos: edificios, mobiliario, equipos.",
    "210": "Terrenos propiedad de la entidad.",
    "211": "Edificios, locales y construcciones propias.",
    "213": "Maquinaria y equipos productivos.",
    "214": "Herramientas y utensilios.",
    "215": "Otras instalaciones fijas (electricidad, climatización...).",
    "216": "Mesas, sillas, estanterías y demás mobiliario.",
    "217": "Ordenadores, impresoras, servidores y similares.",
    "218": "Vehículos: coches, furgonetas, etc.",
    "219": "Otros equipos duraderos.",
    "23":  "Bienes en proceso de adquisición o construcción (aún no terminados).",
    "230": "Terrenos en obras de adaptación todavía no finalizadas.",
    "231": "Edificios u obras en construcción a fecha de cierre.",
    "28":  "Pérdida de valor acumulada por el uso/desgaste de los bienes duraderos. Resta del activo.",
    "280": "Pérdida acumulada de valor del software, marcas y demás bienes inmateriales.",
    "281": "Pérdida acumulada de valor de edificios, mobiliario y equipos.",
    "29":  "Pérdida puntual de valor por daños, obsolescencia o caída del mercado.",
    "290": "Pérdida puntual de valor en bienes inmateriales (programas obsoletos, etc.).",
    "291": "Pérdida puntual de valor en bienes físicos (locales, equipos dañados).",

    # ─── Grupo 3: Existencias ───────────────────────────────────────────────
    "3":   "Material y mercancía que la entidad almacena para vender, consumir o entregar.",
    "30":  "Productos comprados para revender (tienda, librería interna...).",
    "300": "Mercaderías en almacén pendientes de venta.",
    "32":  "Materiales que la entidad transforma para crear productos propios.",
    "320": "Materias primas en almacén.",
    "33":  "Material consumible usado en el día a día (papel, bolígrafos, tóner...).",
    "330": "Material de oficina y papelería en stock.",

    # ─── Grupo 4: Acreedores y deudores ─────────────────────────────────────
    "4":   "Personas, empresas y administraciones a las que la entidad debe (acreedores) o que le deben (deudores).",
    "40":  "Empresas a las que se compran bienes o servicios y que están pendientes de cobro por su parte.",
    "400": "Facturas de proveedores recibidas y pendientes de pago.",
    "401": "Pagarés o letras pendientes de pagar a proveedores.",
    "409": "Gastos del año cuyas facturas aún no han llegado pero se sabe que llegarán.",
    "41":  "Otros acreedores varios (no proveedores habituales): asesoría, profesionales puntuales...",
    "410": "Facturas pendientes de pago a personas que han prestado servicios (asesores, técnicos).",
    "411": "Pagarés/letras a pagar a estos acreedores no habituales.",
    "43":  "Personas o entidades que reciben actividades de la entidad y que aún no han pagado lo que les corresponde.",
    "430": "Usuarios o socios pendientes de pagar por servicios o actividades realizadas.",
    "431": "Pagarés/letras pendientes de cobrar a usuarios.",
    "436": "Estimación de cobros que probablemente se perderán (incobrables).",
    "44":  "Cuentas con patrocinadores, socios y otros relacionados con cobros pendientes.",
    "440": "Patrocinadores que han comprometido aportaciones pendientes de cobrar.",
    "441": "Cuotas de socios emitidas pero todavía no cobradas.",
    "46":  "Saldos con el personal: anticipos pagados o nóminas pendientes.",
    "460": "Anticipos de sueldo entregados al personal.",
    "465": "Sueldos del mes ya devengados pero aún sin pagar.",
    "47":  "Saldos con Hacienda y Seguridad Social: lo que se les debe o lo que ellos deben.",
    "470": "Devoluciones que Hacienda debe a la entidad.",
    "471": "Cantidades pendientes de devolución por parte de la Seguridad Social.",
    "472": "IVA pagado en compras, pendiente de compensar o recuperar.",
    "473": "Retenciones de IRPF e impuestos a cuenta pagados que se recuperarán al cierre fiscal.",
    "475": "Retenciones de IRPF practicadas a empleados/colaboradores pendientes de ingresar en Hacienda.",
    "476": "Cuotas de Seguridad Social retenidas pendientes de ingresar.",
    "477": "IVA cobrado a usuarios pendiente de ingresar en Hacienda.",
    "48":  "Cobros y pagos que corresponden a otro ejercicio (se imputan al año al que pertenecen, no al que se cobran/pagan).",
    "480": "Gastos pagados por adelantado (seguros, alquileres) que se imputarán al año siguiente.",
    "485": "Cobros recibidos por adelantado por servicios que aún no se han prestado.",

    # ─── Grupo 5: Cuentas financieras (corto plazo y tesorería) ─────────────
    "5":   "Dinero disponible (caja, bancos) y deudas/créditos a menos de un año.",
    "52":  "Préstamos y créditos a menos de un año.",
    "520": "Líneas de crédito bancario a devolver en menos de 12 meses.",
    "521": "Otras deudas a corto plazo con particulares o empresas.",
    "526": "Pagos pendientes a socios por excedentes acordados (raro en ESFL).",
    "55":  "Cuentas de paso y movimientos no bancarios pendientes de identificar.",
    "551": "Saldo con socios o administradores que ha entrado/salido provisionalmente.",
    "554": "Cobros que han entrado en cuenta pero aún no se ha identificado a quién corresponden.",
    "57":  "Dinero líquido disponible en caja o en cuentas bancarias.",
    "570": "Dinero en efectivo en la caja física de la entidad (euros).",
    "571": "Dinero en efectivo en moneda extranjera.",
    "572": "Saldo de las cuentas corrientes bancarias en euros (la principal cuenta del tesorero).",
    "573": "Saldo de cuentas bancarias en moneda extranjera.",
    "575": "Cobros enviados al banco pero aún no aplicados a la cuenta (remesas en tránsito).",
    "58":  "Bienes destinados a venderse rápidamente (no de uso continuado).",

    # ─── Grupo 6: Compras y gastos ──────────────────────────────────────────
    "6":   "Todo el dinero que sale de la entidad durante el año: compras, sueldos, suministros, impuestos.",
    "60":  "Compras realizadas (mercaderías, materiales).",
    "600": "Compras de productos para revender.",
    "601": "Compras de materias primas.",
    "602": "Compras de otros materiales (consumibles, repuestos).",
    "607": "Servicios subcontratados que forman parte del producto/servicio final.",
    "62":  "Gastos en servicios externos contratados a empresas o profesionales.",
    "620": "Gastos en investigación y desarrollo durante el ejercicio.",
    "621": "Alquileres de locales, equipos o vehículos.",
    "622": "Mantenimiento, reparaciones y conservación de bienes.",
    "623": "Honorarios de profesionales independientes (abogados, gestores, técnicos).",
    "624": "Transportes y mensajería pagados a terceros.",
    "625": "Primas de seguros (responsabilidad civil, locales, vehículos).",
    "626": "Comisiones y gastos bancarios (mantenimiento, transferencias, devoluciones).",
    "627": "Publicidad, anuncios, prensa, marketing.",
    "628": "Facturas de agua, luz, gas, teléfono e internet.",
    "629": "Otros servicios menores no clasificados en las cuentas anteriores.",
    "63":  "Impuestos pagados (excepto el de la renta de las personas físicas, que se retiene en 475).",
    "630": "Impuesto sobre el excedente del ejercicio (si la entidad está sujeta a Sociedades).",
    "631": "Otros tributos: IBI, tasas municipales, etc.",
    "64":  "Salarios, seguros sociales y demás coste del personal contratado.",
    "640": "Sueldos brutos pagados al personal (antes de retenciones).",
    "641": "Indemnizaciones por despido o terminación de contrato.",
    "642": "Cuota patronal de la Seguridad Social (lo que paga la entidad por cada trabajador).",
    "643": "Aportaciones a planes de pensiones de empleo (aportación definida).",
    "644": "Retribuciones al personal mediante acciones (poco habitual en ESFL).",
    "645": "Compromisos de pensiones de prestación definida.",
    "649": "Otros gastos sociales del personal: formación, regalos, ayudas, dietas no salariales.",
    "65":  "Otros gastos de gestión del día a día.",
    "650": "Cuotas, donaciones o cobros que ya no se podrán recuperar nunca (incobrables definitivos).",
    "651": "Pérdidas al vender o dar de baja un bien duradero por debajo de su valor en libros.",
    "659": "Otros gastos varios no clasificados arriba.",
    "66":  "Intereses, comisiones y otros gastos financieros.",
    "660": "Intereses de préstamos a largo plazo.",
    "661": "Intereses de bonos u obligaciones (raro en ESFL).",
    "662": "Intereses de deudas con personas físicas o entidades no bancarias.",
    "663": "Pérdida por cambio de valor en inversiones.",
    "664": "Intereses por aplazar pagos a proveedores.",
    "665": "Descuentos perdidos por no haber pagado a tiempo.",
    "666": "Pérdidas en venta de inversiones financieras.",
    "667": "Créditos prestados que resultan incobrables.",
    "668": "Pérdidas por diferencias de cambio en moneda extranjera.",
    "669": "Otros gastos financieros menores.",
    "67":  "Pérdidas por la venta de bienes duraderos por debajo de su valor en libros.",
    "671": "Pérdida al vender software, marcas u otros bienes inmateriales por menos de lo registrado.",
    "672": "Pérdida al vender edificios, vehículos o equipos por menos de lo registrado.",
    "68":  "Pérdida de valor del año por uso de los bienes duraderos (cargo del año a la amortización).",
    "680": "Amortización del año del software, marcas y otros bienes inmateriales.",
    "681": "Amortización del año de edificios, mobiliario y equipos.",
    "682": "Amortización del año de inversiones inmobiliarias.",
    "69":  "Pérdida estimada del año por bienes que han bajado de valor o cobros dudosos.",
    "690": "Estimación de pérdida en el inmovilizado inmaterial.",
    "691": "Estimación de pérdida en el inmovilizado material.",
    "694": "Estimación de cobros dudosos a usuarios.",

    # ─── Grupo 7: Ventas e ingresos ─────────────────────────────────────────
    "7":   "Todo el dinero que entra en la entidad durante el año: cuotas, donaciones, subvenciones, ventas.",
    "72":  "Ingresos generados por la actividad propia de la entidad (cuotas, formación, eventos).",
    "720": "Ingresos por venta de productos o servicios propios.",
    "721": "Cuotas pagadas por socios y afiliados (la principal fuente de ingresos en muchas ESFL).",
    "722": "Ingresos por cursos, talleres o formación que organiza la entidad.",
    "723": "Ingresos por venta de libros, revistas o publicaciones propias.",
    "724": "Ingresos por eventos, jornadas, conferencias y actos públicos.",
    "725": "Pagos de afiliados por servicios concretos (no por cuota general).",
    "73":  "Donaciones y herencias recibidas que se aplican al año.",
    "730": "Donaciones puntuales recibidas para gastos corrientes del ejercicio.",
    "731": "Parte del año que se aplica al excedente de subvenciones/donaciones de capital plurianuales.",
    "74":  "Subvenciones públicas y ayudas externas.",
    "740": "Subvenciones de administraciones públicas para gastos del año.",
    "741": "Subvenciones de entidades privadas o fundaciones para gastos del año.",
    "742": "Parte aplicable al año de subvenciones de capital recibidas para inversiones plurianuales.",
    "749": "Otros ingresos del día a día no clasificados arriba.",
    "75":  "Ingresos derivados de actividades secundarias (alquileres, cesiones, etc.).",
    "751": "Ingresos por alquilar locales o equipos propios.",
    "752": "Ingresos por ceder a terceros el uso de marcas o patentes propias.",
    "759": "Ingresos por servicios cobrados al personal (comedor, etc.).",
    "76":  "Intereses y dividendos cobrados por inversiones financieras.",
    "760": "Dividendos cobrados por participaciones en otras entidades.",
    "761": "Intereses cobrados por bonos u obligaciones que posee la entidad.",
    "762": "Intereses cobrados por préstamos concedidos a más de un año.",
    "763": "Intereses cobrados por préstamos concedidos a menos de un año.",
    "765": "Descuentos obtenidos por pagar a proveedores antes de tiempo.",
    "768": "Ganancias por diferencias de cambio en moneda extranjera.",
    "769": "Otros ingresos financieros menores.",
    "77":  "Beneficios por la venta de bienes duraderos (locales, vehículos, equipos).",
    "771": "Ganancia al vender software, marcas u otros bienes inmateriales.",
    "772": "Ganancia al vender edificios, vehículos o equipos.",
    "79":  "Reversión de provisiones y estimaciones de pérdida que finalmente no se materializaron.",
    "790": "Sobrante de provisiones de años anteriores que ya no son necesarias.",
    "794": "Recuperación de créditos a usuarios que parecían incobrables y finalmente se cobran.",
}


async def aplicar_descripciones() -> None:
    async with async_session() as session:
        actualizadas = 0
        for codigo, descripcion in DESCRIPCIONES.items():
            r = await session.execute(
                update(CuentaContable)
                .where(CuentaContable.codigo == codigo)
                .values(descripcion=descripcion)
            )
            if r.rowcount:
                actualizadas += r.rowcount
        await session.commit()
        print(f"✓ {actualizadas} cuentas actualizadas con descripción en lenguaje llano.")
        print(f"  Total con entrada en el diccionario: {len(DESCRIPCIONES)}")


if __name__ == "__main__":
    asyncio.run(aplicar_descripciones())
