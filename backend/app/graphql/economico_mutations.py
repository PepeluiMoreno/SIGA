"""Mutations GraphQL financieras con lógica de negocio compleja.

Complementan las mutations CRUD automáticas de strawchemy con operaciones
que requieren lógica de servicio: confirmar asientos, conciliar apuntes,
generar balances, registrar apuntes con lógica contable automática.
"""
import strawberry
from datetime import date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select

from ..modules.economico.services.tesoreria_service import TesoreriaService
from ..modules.economico.services.contabilidad_service import ContabilidadService
from ..modules.economico.services.registro_contable import RegistroContable
from ..modules.economico.services.remesa_service import RemesaService
from ..modules.economico.services.recibo_service import ReciboService
from ..modules.economico.services.justificante_gasto_service import JustificanteGastoService
from ..modules.economico.services.donacion_service import DonacionService
from ..modules.economico.models.tesoreria import TipoApunte, OrigenApunte, MetodoConciliacion
from ..modules.economico.models.contabilidad import TipoAsientoContable
from .permissions import RequireTransaction


@strawberry.input
class FallidoBancoInput:
    """Una orden de cobro fallida importada del banco."""
    orden_id: UUID
    codigo: str
    motivo: Optional[str] = None
    fecha: Optional[date] = None


@strawberry.input
class LineaJustificanteInput:
    """Línea individual de gasto dentro de un justificante (Flujo 7).

    Varias líneas pueden agruparse bajo un mismo justificante si todas se
    refieren a la misma actividad.
    """
    concepto: str
    importe: float
    fecha_gasto: date
    observaciones: Optional[str] = None


# ─── Types para la liquidación de remesa (Flujo 4) ──────────────────────────

@strawberry.type
class PreviewOrdenCobradaType:
    orden_id: UUID
    end_to_end_id: str
    importe: float
    miembro_nombre: str


@strawberry.type
class PreviewOrdenFallidaType:
    orden_id: UUID
    end_to_end_id: str
    codigo: str
    motivo: str
    fecha: Optional[str] = None  # ISO date
    importe: float


@strawberry.type
class PreviewSinEmparejarType:
    end_to_end_id: str
    motivo: str


@strawberry.type
class PreviewTotalesType:
    n_cobradas: int
    n_fallidas: int
    importe_cobrado: float


@strawberry.type
class PreviewLiquidacionType:
    """Previsualización del resultado de aplicar un fichero del banco a una remesa."""
    remesa_referencia: str
    cobradas: list[PreviewOrdenCobradaType]
    fallidas: list[PreviewOrdenFallidaType]
    no_emparejadas: list[PreviewSinEmparejarType]
    totales: PreviewTotalesType


@strawberry.type
class ResultadoLiquidacionType:
    """Resumen del resultado de aplicar liquidar_remesa."""
    n_cobradas: int
    n_fallidas: int
    importe_cobrado: float
    apunte_id: Optional[UUID] = None
    asiento_id: Optional[UUID] = None
    remesa_estado: Optional[str] = None


# ─── Types para Flujo 1 — Establecimiento de cuotas ──────────────────────────

@strawberry.type
class DesgloseTipoMiembroType:
    tipo_miembro_id: UUID
    tipo_miembro_nombre: str
    motivo_codigo: Optional[str] = None
    motivo_porcentaje: float = 0.0
    n_miembros: int = 0
    importe_unitario: float = 0.0
    total: float = 0.0
    excluido: bool = False


@strawberry.type
class PreviewGeneracionCuotasType:
    ejercicio: int
    importe_base: float
    desglose: list[DesgloseTipoMiembroType]
    n_generables: int
    n_excluidos: int
    n_existentes: int
    total_esperado: float


@strawberry.type
class ResultadoGeneracionCuotasType:
    ejercicio: int
    n_creadas: int
    n_omitidas_existentes: int
    n_omitidas_excluidas: int
    total_importe: float


# ─── Types para Flujo 3 — Previsualización de remesa ────────────────────────

@strawberry.type
class CuotaPreviewType:
    """Una cuota previsualizada (incluida o excluida) antes de generar la remesa."""
    cuota_id: UUID
    miembro_id: UUID
    miembro_nombre: str
    importe_pendiente: float
    motivo_exclusion: str  # vacío si está incluida


@strawberry.type
class OrdinariaExistenteType:
    id: UUID
    referencia: str


@strawberry.type
class PreviewRemesaType:
    """Previsualización de qué se incluiría en una remesa ORDINARIA (D3.3, sin persistir)."""
    ejercicio: int
    n_incluidas: int
    n_excluidas: int
    importe_total: float
    incluidas: list[CuotaPreviewType]
    excluidas: list[CuotaPreviewType]
    ordinaria_existente: Optional[OrdinariaExistenteType] = None


@strawberry.type
class CertificableDonacionType:
    """Donante con donaciones certificables del ejercicio (agregado por NIF + tipo)."""
    nif: str
    nombre: str
    tipo: str  # DINERARIA | ESPECIE
    total: float
    n_donaciones: int
    donacion_ids: list[str]
    todas_certificadas: bool


@strawberry.type
class CertificadoEmitidoType:
    numero: str
    pdf_base64: str


@strawberry.type
class EconomicoFlujosMutation:
    """Mutations del módulo Económico con lógica de negocio (no solo CRUD).

    Agrupa todas las operaciones de los 11 flujos: cuotas, recibos, remesas, liquidación,
    cobro manual, donaciones, justificantes, conciliación, cierre, CCAA, Modelo 182.
    """

    # ─── Tesorería ────────────────────────────────────────────────────────────

    @strawberry.mutation
    async def registrar_apunte_caja(
        self,
        info: strawberry.Info,
        cuenta_id: UUID,
        fecha: date,
        importe: float,
        tipo: str,
        concepto: str,
        origen: Optional[str] = None,
        entidad_origen_tipo: Optional[str] = None,
        entidad_origen_id: Optional[UUID] = None,
        referencia_externa: Optional[str] = None,
        observaciones: Optional[str] = None,
        actividad_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
    ) -> str:
        """Registra un apunte de caja y, si está en versión COMPLETA, genera el asiento contable.

        `actividad_id` / `campania_id`: opcionales, permiten imputar el apunte a una
        actividad o campaña para el balance económico de la Memoria anual (flujo 10).
        """
        session = info.context.session
        service = TesoreriaService(session)

        tipo_apunte = TipoApunte(tipo)
        origen_apunte = OrigenApunte(origen) if origen else None

        # Validación de la imputación: aplica tanto a GASTO como a INGRESO.
        # Las plantillas recurrentes no son imputables; las campañas cerradas tampoco.
        if actividad_id is not None:
            from app.modules.actividades.models.actividad import Actividad
            from app.modules.actividades.models.campana import Campania
            from sqlalchemy import select as _select
            r = await session.execute(_select(Actividad).where(Actividad.id == actividad_id))
            actividad = r.scalars().first()
            if not actividad:
                raise ValueError(f"Actividad {actividad_id} no encontrada.")
            if actividad.caracter == "RECURRENTE" and actividad.padre_id is None:
                raise ValueError(
                    "No se puede imputar a una plantilla recurrente. "
                    "Elige una instancia concreta."
                )
            if actividad.campania_id:
                rc = await session.execute(_select(Campania).where(Campania.id == actividad.campania_id))
                camp = rc.scalars().first()
                if camp and camp.esta_cerrada:
                    raise ValueError(
                        f"La campaña «{camp.nombre}» está cerrada y no admite nuevos gastos/ingresos."
                    )
                # Coherencia: si la actividad tiene campania_id, el campania_id del apunte se
                # deriva siempre de ella (frontend ya lo hace, lo refuerza el backend).
                campania_id = actividad.campania_id

        apunte = await service.registrar_apunte(
            cuenta_id=cuenta_id,
            fecha=fecha,
            importe=Decimal(str(importe)),
            tipo=tipo_apunte,
            concepto=concepto,
            origen=origen_apunte,
            entidad_origen_tipo=entidad_origen_tipo,
            entidad_origen_id=entidad_origen_id,
            referencia_externa=referencia_externa,
            observaciones=observaciones,
            actividad_id=actividad_id,
            campania_id=campania_id,
        )

        registro = RegistroContable(session)
        await registro.generar_asiento_para_apunte(apunte)

        return str(apunte.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_CONCILIAR_APUNTE")])
    async def marcar_apunte_conciliado(
        self,
        info: strawberry.Info,
        apunte_id: UUID,
        fecha_conciliacion: Optional[date] = None,
    ) -> bool:
        session = info.context.session
        service = TesoreriaService(session)
        await service.marcar_apunte_conciliado(apunte_id, fecha_conciliacion)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_CONCILIAR_APUNTE")])
    async def desmarcar_apunte_conciliado(
        self, info: strawberry.Info, apunte_id: UUID,
    ) -> bool:
        """Revierte la conciliación manual de un apunte."""
        service = TesoreriaService(info.context.session)
        await service.desmarcar_apunte_conciliado(apunte_id)
        return True

    @strawberry.mutation
    async def actualizar_metadatos_apunte_caja(
        self,
        info: strawberry.Info,
        apunte_id: UUID,
        concepto: Optional[str] = None,
        observaciones: Optional[str] = None,
        actividad_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
        limpiar_actividad: bool = False,
    ) -> str:
        """Edita metadatos no contables del apunte (concepto, observaciones, imputación).
        Para cambiar importe/fecha/tipo hay que anular y crear uno nuevo.
        """
        session = info.context.session

        # Validar imputación: plantillas no imputables; campaña cerrada bloquea.
        if actividad_id is not None and not limpiar_actividad:
            from app.modules.actividades.models.actividad import Actividad
            from app.modules.actividades.models.campana import Campania
            from sqlalchemy import select as _select
            r = await session.execute(_select(Actividad).where(Actividad.id == actividad_id))
            actividad = r.scalars().first()
            if not actividad:
                raise ValueError(f"Actividad {actividad_id} no encontrada.")
            if actividad.caracter == "RECURRENTE" and actividad.padre_id is None:
                raise ValueError(
                    "No se puede imputar a una plantilla recurrente. Elige una instancia."
                )
            if actividad.campania_id:
                rc = await session.execute(_select(Campania).where(Campania.id == actividad.campania_id))
                camp = rc.scalars().first()
                if camp and camp.esta_cerrada:
                    raise ValueError(
                        f"La campaña «{camp.nombre}» está cerrada y no admite imputación."
                    )
                campania_id = actividad.campania_id

        service = TesoreriaService(session)
        apunte = await service.actualizar_metadatos_apunte(
            apunte_id,
            concepto=concepto,
            observaciones=observaciones,
            actividad_id=actividad_id,
            campania_id=campania_id,
            limpiar_actividad=limpiar_actividad,
        )
        return str(apunte.id)

    @strawberry.mutation
    async def anular_apunte_caja(
        self, info: strawberry.Info, apunte_id: UUID, motivo: str,
    ) -> str:
        """Anula un apunte generando un contraapunte con importe inverso.
        Devuelve el id del contraapunte creado.
        """
        service = TesoreriaService(info.context.session)
        contra = await service.anular_apunte(apunte_id, motivo)
        return str(contra.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_CONCILIAR_APUNTE")])
    async def conciliar_apunte_con_extracto(
        self,
        info: strawberry.Info,
        apunte_id: UUID,
        extracto_id: UUID,
        metodo: str = "MANUAL",
    ) -> str:
        session = info.context.session
        service = TesoreriaService(session)
        usuario_id = getattr(info.context.user, 'id', None)
        conciliacion = await service.conciliar_apunte_con_extracto(
            apunte_id=apunte_id,
            extracto_id=extracto_id,
            metodo=MetodoConciliacion(metodo),
            usuario_id=usuario_id,
        )
        return str(conciliacion.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_CONFIRMAR_PERIODO")])
    async def confirmar_conciliacion_periodo(
        self, info: strawberry.Info, conciliacion_id: UUID
    ) -> bool:
        session = info.context.session
        service = TesoreriaService(session)
        await service.confirmar_conciliacion_periodo(conciliacion_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_IMPORTAR_EXTRACTO")])
    async def importar_extracto_norma43(
        self, info: strawberry.Info, cuenta_id: UUID, archivo_b64: str
    ) -> int:
        """D8.1: parsea un fichero Norma 43 AEB (codificado base64) y carga las
        líneas en `ExtractoBancario`. Devuelve el número de líneas importadas.
        Evita duplicar líneas ya existentes con misma fecha/importe/referencia."""
        import base64
        session = info.context.session
        service = TesoreriaService(session)
        contenido = base64.b64decode(archivo_b64)
        lineas = TesoreriaService.parse_norma43(contenido)
        extractos = await service.importar_extracto(cuenta_id=cuenta_id, lineas=lineas)
        return len(extractos)

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_IMPORTAR_EXTRACTO")])
    async def importar_extracto_csv(
        self,
        info: strawberry.Info,
        cuenta_id: UUID,
        lineas_json: str,
    ) -> int:
        """D8.1: importa líneas de extracto desde CSV ya parseado en el cliente.
        `lineas_json` es un JSON string con [{fecha, importe, concepto, referencia}].
        Devuelve el número de líneas creadas."""
        import json
        session = info.context.session
        service = TesoreriaService(session)
        try:
            lineas = json.loads(lineas_json)
        except Exception as e:
            raise ValueError(f"CSV no parseable: {e}")
        if not isinstance(lineas, list):
            raise ValueError("Las líneas deben ser una lista JSON.")
        extractos = await service.importar_extracto(cuenta_id=cuenta_id, lineas=lineas)
        return len(extractos)

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_CONCILIAR_APUNTE")])
    async def romper_conciliacion(
        self, info: strawberry.Info, conciliacion_id: UUID
    ) -> bool:
        """A5 — Deshace un emparejamiento previo si el período no está cerrado."""
        session = info.context.session
        service = TesoreriaService(session)
        await service.romper_conciliacion(conciliacion_id)
        return True

    # ─── Contabilidad ─────────────────────────────────────────────────────────

    @strawberry.mutation
    async def confirmar_asiento_contable(
        self, info: strawberry.Info, asiento_id: UUID
    ) -> bool:
        """Confirma un asiento BORRADOR. Falla si debe ≠ haber."""
        session = info.context.session
        service = ContabilidadService(session)
        await service.confirmar_asiento(asiento_id)
        return True

    @strawberry.mutation
    async def anular_asiento_contable(
        self, info: strawberry.Info, asiento_id: UUID
    ) -> bool:
        session = info.context.session
        service = ContabilidadService(session)
        await service.anular_asiento(asiento_id)
        return True

    # ─── Liquidación automática ────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_PROCESS")])
    async def previsualizar_liquidacion_remesa(
        self,
        info: strawberry.Info,
        remesa_id: UUID,
        tipo_fichero: str,                          # "pain002" | "camt054" | "manual"
        fichero_b64: Optional[str] = None,          # contenido del XML en base64
        fallidos_manual: Optional[list[FallidoBancoInput]] = None,
    ) -> PreviewLiquidacionType:
        """Empareja el fichero del banco (pain.002, camt.054 o lista manual) con
        las órdenes de la remesa SIN persistir nada. Devuelve la propuesta para
        que el tesorero confirme con `liquidar_remesa`. (Flujo 4 — A2)"""
        import base64
        session = info.context.session
        service = RemesaService(session)

        contenido = base64.b64decode(fichero_b64) if fichero_b64 else None
        fallidos_dict = None
        if fallidos_manual:
            fallidos_dict = [
                {
                    "orden_id": f.orden_id,
                    "codigo": f.codigo,
                    "motivo": f.motivo or "",
                    "fecha": f.fecha.isoformat() if f.fecha else None,
                }
                for f in fallidos_manual
            ]

        preview = await service.previsualizar_liquidacion(
            remesa_id=remesa_id,
            tipo_fichero=tipo_fichero,
            contenido=contenido,
            fallidos_manual=fallidos_dict,
        )
        return PreviewLiquidacionType(
            remesa_referencia=preview["remesa_referencia"],
            cobradas=[PreviewOrdenCobradaType(**c) for c in preview["cobradas"]],
            fallidas=[PreviewOrdenFallidaType(**f) for f in preview["fallidas"]],
            no_emparejadas=[PreviewSinEmparejarType(**n) for n in preview["no_emparejadas"]],
            totales=PreviewTotalesType(**preview["totales"]),
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_PROCESS")])
    async def liquidar_remesa(
        self,
        info: strawberry.Info,
        remesa_id: UUID,
        cuenta_bancaria_id: UUID,
        fecha_liquidacion: date,
        cobradas: list[UUID],
        fallidas: Optional[list[FallidoBancoInput]] = None,
    ) -> ResultadoLiquidacionType:
        """Aplica el resultado del banco a la remesa: marca órdenes cobradas/fallidas,
        actualiza cuotas y recibos, crea ApunteCaja por el bruto + asiento contable.
        Atómico: si algo falla, rollback. (Flujo 4 — A3)"""
        session = info.context.session
        service = RemesaService(session)
        fallidas_dict = [
            {
                "orden_id": f.orden_id,
                "codigo": f.codigo,
                "motivo": f.motivo or "",
                "fecha": f.fecha.isoformat() if f.fecha else None,
            }
            for f in (fallidas or [])
        ]
        res = await service.liquidar_remesa(
            remesa_id=remesa_id,
            fecha_liquidacion=fecha_liquidacion,
            cuenta_bancaria_id=cuenta_bancaria_id,
            cobradas=cobradas,
            fallidas=fallidas_dict,
        )
        return ResultadoLiquidacionType(
            n_cobradas=res["n_cobradas"],
            n_fallidas=res["n_fallidas"],
            importe_cobrado=res["importe_cobrado"],
            apunte_id=UUID(res["apunte_id"]) if res["apunte_id"] else None,
            asiento_id=UUID(res["asiento_id"]) if res["asiento_id"] else None,
            remesa_estado=res["remesa_estado"],
        )

    @strawberry.mutation
    async def registrar_pago_cuota_manual(
        self,
        info: strawberry.Info,
        cuota_id: UUID,
        cuenta_bancaria_id: UUID,
        importe: float,
        modo_ingreso: str,
        fecha_pago: Optional[date] = None,
        referencia: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> str:
        """Registra un pago manual de cuota, actualiza su estado y genera
        ApunteCaja (+ asiento contable si modo COMPLETA).
        Devuelve el ID del ApunteCaja generado."""
        session = info.context.session
        service = TesoreriaService(session)
        apunte = await service.registrar_pago_cuota_manual(
            cuota_id=cuota_id,
            cuenta_bancaria_id=cuenta_bancaria_id,
            importe=Decimal(str(importe)),
            modo_ingreso=modo_ingreso,
            fecha_pago=fecha_pago,
            referencia=referencia,
            observaciones=observaciones,
        )
        return str(apunte.id)

    # ─── Generación de remesas SEPA ────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_CREATE")])
    async def generar_remesa_sepa(
        self,
        info: strawberry.Info,
        ejercicio: int,
        fecha_cobro: date,
        agrupacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
    ) -> str:
        """Genera una remesa SEPA en estado Borrador con todas las cuotas pendientes
        del ejercicio (filtradas por agrupación si se indica).
        Devuelve el ID de la remesa creada."""
        session = info.context.session
        service = RemesaService(session)
        remesa = await service.generar_remesa(
            ejercicio=ejercicio,
            fecha_cobro=fecha_cobro,
            agrupacion_id=agrupacion_id,
            observaciones=observaciones,
        )
        return str(remesa.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_SEND")])
    async def marcar_remesa_enviada(
        self,
        info: strawberry.Info,
        remesa_id: UUID,
    ) -> bool:
        """Marca la remesa como Enviada al banco."""
        session = info.context.session
        service = RemesaService(session)
        await service.marcar_enviada(remesa_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_CREATE")])
    async def generar_remesa_extraordinaria(
        self,
        info: strawberry.Info,
        ejercicio: int,
        fecha_cobro: date,
        concepto: str,
        miembro_ids: List[UUID],
        importe_por_miembro: float,
        agrupacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
    ) -> str:
        """Genera una remesa extraordinaria (derrama, cuota especial) con concepto e
        importe libre. SeqTp=OOFF por defecto (cargo único)."""
        session = info.context.session
        service = RemesaService(session)
        remesa = await service.generar_remesa_extraordinaria(
            ejercicio=ejercicio,
            fecha_cobro=fecha_cobro,
            concepto=concepto,
            miembro_ids=miembro_ids,
            importe_por_miembro=Decimal(str(importe_por_miembro)),
            agrupacion_id=agrupacion_id,
            observaciones=observaciones,
        )
        return str(remesa.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_RESEND")])
    async def generar_remesa_fallidos(
        self,
        info: strawberry.Info,
        remesa_origen_id: UUID,
        fecha_cobro: date,
        observaciones: Optional[str] = None,
    ) -> str:
        """Genera una remesa de reenvío con las órdenes fallidas de una remesa anterior.
        SeqTp=FRST (norma SEPA EPC131-08 tras fallido)."""
        session = info.context.session
        service = RemesaService(session)
        remesa = await service.generar_remesa_fallidos(
            remesa_origen_id=remesa_origen_id,
            fecha_cobro=fecha_cobro,
            observaciones=observaciones,
        )
        return str(remesa.id)

    # ─── Flujo 3 — Previsualización / Anulación / XML ─────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_PREVIEW")])
    async def previsualizar_remesa(
        self,
        info: strawberry.Info,
        ejercicio: int,
        agrupacion_id: Optional[UUID] = None,
    ) -> PreviewRemesaType:
        """Previsualiza qué cuotas se incluirían en una remesa ORDINARIA sin
        crearla, aplicando los filtros del flujo 3 (D3.3 + D3.4) y detectando
        si ya existe una ordinaria activa del ejercicio (D3.2)."""
        session = info.context.session
        service = RemesaService(session)
        preview = await service.previsualizar_remesa(
            ejercicio=ejercicio,
            agrupacion_id=agrupacion_id,
        )

        def _linea(c: dict) -> CuotaPreviewType:
            return CuotaPreviewType(
                cuota_id=UUID(c["cuota_id"]),
                miembro_id=UUID(c["miembro_id"]),
                miembro_nombre=c["miembro_nombre"],
                importe_pendiente=c["importe_pendiente"],
                motivo_exclusion=c["motivo_exclusion"],
            )

        ord_ex = preview.get("ordinaria_existente")
        return PreviewRemesaType(
            ejercicio=preview["ejercicio"],
            n_incluidas=preview["n_incluidas"],
            n_excluidas=preview["n_excluidas"],
            importe_total=preview["importe_total"],
            incluidas=[_linea(c) for c in preview["incluidas"]],
            excluidas=[_linea(c) for c in preview["excluidas"]],
            ordinaria_existente=(
                OrdinariaExistenteType(id=UUID(ord_ex["id"]), referencia=ord_ex["referencia"])
                if ord_ex else None
            ),
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_ANULAR")])
    async def anular_remesa(
        self,
        info: strawberry.Info,
        remesa_id: UUID,
    ) -> bool:
        """Anula una remesa Borrador/Generada/Enviada (no procesada). Libera
        las cuotas y anula los recibos asociados. (Flujo 3 — A8.)"""
        session = info.context.session
        service = RemesaService(session)
        await service.anular_remesa(remesa_id=remesa_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_XML")])
    async def generar_xml_sepa(
        self,
        info: strawberry.Info,
        remesa_id: UUID,
    ) -> str:
        """Genera el XML SEPA Pain.008 de la remesa y lo devuelve codificado
        en base64. Los datos del acreedor se leen de Parámetros Generales
        (configuraciones grupo SEPA) — D3.5."""
        import base64
        session = info.context.session
        service = RemesaService(session)
        xml_bytes = await service.generar_xml_sepa(remesa_id=remesa_id)
        return base64.b64encode(xml_bytes).decode("ascii")

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_FAIL_NOTIFY")])
    async def comunicar_recibos_fallidos(
        self,
        info: strawberry.Info,
        recibo_ids: List[UUID],
        plantilla_email_id: UUID,
    ) -> int:
        """Marca un lote de recibos FALLIDO como notificados al socio usando
        la plantilla indicada. Devuelve el nº de recibos procesados.

        Flujo 4 — pantalla 5.4. El envío real de email se delega al módulo de
        Comunicación Interna (queda como TODO de integración). Por ahora solo
        marca trazabilidad: fecha_aviso_fallido = hoy, plantilla_email_aviso_id.
        """
        from datetime import date as _date
        from sqlalchemy import select, update
        from app.modules.economico.models.recibos import Recibo

        session = info.context.session
        if not recibo_ids:
            return 0
        r = await session.execute(
            update(Recibo)
            .where(Recibo.id.in_(recibo_ids))
            .where(Recibo.estado == "FALLIDO")
            .values(
                fecha_aviso_fallido=_date.today(),
                plantilla_email_aviso_id=plantilla_email_id,
            )
        )
        await session.commit()
        return r.rowcount or 0

    @strawberry.mutation
    async def importar_fallidos_banco(
        self,
        info: strawberry.Info,
        remesa_id: UUID,
        fallidos: List[FallidoBancoInput],
    ) -> int:
        """Marca las órdenes indicadas como fallidas con código SEPA y motivo.
        Devuelve el número de órdenes marcadas."""
        session = info.context.session
        service = RemesaService(session)
        fallidos_dict = [
            {
                "orden_id": f.orden_id,
                "codigo": f.codigo,
                "motivo": f.motivo or "",
                "fecha": f.fecha,
            }
            for f in fallidos
        ]
        return await service.importar_fallidos_banco(remesa_id, fallidos_dict)

    # ─── Recibos ──────────────────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_EMIT_LOTE")])
    async def emitir_recibos_lote(
        self,
        info: strawberry.Info,
        ejercicio: int,
        tipo: str = "CUOTA_ORDINARIA",
        concepto: Optional[str] = None,
        miembro_ids: Optional[List[UUID]] = None,
        agrupacion_id: Optional[UUID] = None,
        fecha_vencimiento: Optional[date] = None,
    ) -> int:
        """Emite un lote de recibos numerados (REC-YYYY-NNNNN) para las cuotas
        pendientes del ejercicio. Devuelve el número de recibos emitidos."""
        session = info.context.session
        service = ReciboService(session)
        recibos = await service.emitir_lote(
            ejercicio=ejercicio,
            tipo=tipo,
            concepto=concepto,
            miembro_ids=miembro_ids,
            agrupacion_id=agrupacion_id,
            fecha_vencimiento=fecha_vencimiento,
        )
        return len(recibos)

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_EMIT_LOTE")])
    async def emitir_recibo_individual(
        self,
        info: strawberry.Info,
        ejercicio: int,
        miembro_id: UUID,
        concepto: str,
        importe: float,
        tipo: str = "EXTRAORDINARIA",
        cuota_id: Optional[UUID] = None,
        fecha_vencimiento: Optional[date] = None,
        observaciones: Optional[str] = None,
    ) -> str:
        """Emite un recibo individual. Devuelve el ID del recibo."""
        session = info.context.session
        service = ReciboService(session)
        recibo = await service.emitir_recibo_individual(
            ejercicio=ejercicio,
            miembro_id=miembro_id,
            concepto=concepto,
            importe=Decimal(str(importe)),
            tipo=tipo,
            cuota_id=cuota_id,
            fecha_vencimiento=fecha_vencimiento,
            observaciones=observaciones,
        )
        return str(recibo.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_MARCAR_COBRADO")])
    async def marcar_recibo_cobrado(
        self,
        info: strawberry.Info,
        recibo_id: UUID,
        cuenta_bancaria_id: Optional[UUID] = None,
        importe_cobrado: Optional[float] = None,
        fecha_cobro: Optional[date] = None,
        modo_cobro: Optional[str] = None,
        orden_cobro_id: Optional[UUID] = None,
        referencia: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> bool:
        """D5.1: cobro manual de recibo. Si se indica `cuenta_bancaria_id` y NO
        viene de una remesa (`orden_cobro_id` vacío), orquesta la cadena
        completa: recibo → cuota → ApunteCaja → asiento contable. Una sola
        transacción."""
        session = info.context.session
        service = ReciboService(session)
        await service.marcar_cobrado(
            recibo_id=recibo_id,
            importe_cobrado=Decimal(str(importe_cobrado)) if importe_cobrado is not None else None,
            fecha_cobro=fecha_cobro,
            modo_cobro=modo_cobro,
            orden_cobro_id=orden_cobro_id,
            cuenta_bancaria_id=cuenta_bancaria_id,
            referencia=referencia,
            observaciones=observaciones,
        )
        return True

    @strawberry.mutation
    async def marcar_recibo_fallido(
        self,
        info: strawberry.Info,
        recibo_id: UUID,
        codigo_sepa: str,
        motivo: Optional[str] = None,
    ) -> bool:
        session = info.context.session
        service = ReciboService(session)
        await service.marcar_fallido(recibo_id, codigo_sepa, motivo)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_ANULAR")])
    async def anular_recibo(
        self,
        info: strawberry.Info,
        recibo_id: UUID,
        motivo: Optional[str] = None,
    ) -> bool:
        session = info.context.session
        service = ReciboService(session)
        await service.anular_recibo(recibo_id, motivo)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_DESCARGAR_PDF")])
    async def descargar_recibo_pdf(
        self,
        info: strawberry.Info,
        recibo_id: UUID,
    ) -> str:
        """Genera el PDF del recibo y lo devuelve codificado en base64.

        TODO: requiere `reportlab` para producir PDF real. Mientras no esté
        instalado en el contenedor, devuelve un texto plano descriptivo
        codificado en base64 (placeholder funcional para que la UI no rompa).
        """
        import base64
        from sqlalchemy import select as _select
        from app.modules.economico.models.recibos import Recibo

        session = info.context.session
        r = await session.execute(_select(Recibo).where(Recibo.id == recibo_id))
        recibo = r.scalars().first()
        if not recibo:
            raise ValueError(f"Recibo {recibo_id} no encontrado")

        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A5
            from io import BytesIO
            buf = BytesIO()
            c = canvas.Canvas(buf, pagesize=A5)
            w, h = A5
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20, h - 30, f"Recibo {recibo.numero_recibo}")
            c.setFont("Helvetica", 9)
            y = h - 60
            for label, value in [
                ("Ejercicio", str(recibo.ejercicio)),
                ("Concepto", recibo.concepto or ""),
                ("Importe", f"{recibo.importe:.2f} €"),
                ("Estado", recibo.estado),
                ("Modo cobro", recibo.modo_cobro or "—"),
                ("Fecha emisión", recibo.fecha_emision.isoformat() if recibo.fecha_emision else "—"),
                ("Fecha cobro", recibo.fecha_cobro.isoformat() if recibo.fecha_cobro else "—"),
            ]:
                c.drawString(20, y, f"{label}: {value}")
                y -= 15
            c.showPage()
            c.save()
            return base64.b64encode(buf.getvalue()).decode("ascii")
        except ImportError:
            placeholder = (
                f"RECIBO {recibo.numero_recibo}\n"
                f"Ejercicio: {recibo.ejercicio}\n"
                f"Concepto: {recibo.concepto}\n"
                f"Importe: {recibo.importe:.2f} EUR\n"
                f"Estado: {recibo.estado}\n"
                f"(PDF no disponible: falta instalar reportlab en el backend)"
            )
            return base64.b64encode(placeholder.encode("utf-8")).decode("ascii")

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_ENVIAR_EMAIL")])
    async def enviar_recibo_email(
        self,
        info: strawberry.Info,
        recibo_id: UUID,
        plantilla_email_id: UUID,
    ) -> bool:
        """Registra la intención de enviar el recibo al socio con la plantilla
        indicada. El envío real se delega al módulo de Comunicación Interna
        (TODO de integración). Marca trazabilidad: fecha_aviso_fallido en el
        recibo si procediera. Devuelve true si la solicitud queda registrada.
        """
        from sqlalchemy import select as _select
        from datetime import date as _date
        from app.modules.economico.models.recibos import Recibo

        session = info.context.session
        r = await session.execute(_select(Recibo).where(Recibo.id == recibo_id))
        recibo = r.scalars().first()
        if not recibo:
            raise ValueError(f"Recibo {recibo_id} no encontrado")

        # Por ahora solo registramos la intención (sin envío real).
        # Cuando se complete la integración con comunicación_interna se invoca aquí.
        obs_prev = recibo.observaciones or ""
        sufijo = f"[{_date.today().isoformat()}] Email solicitado (plantilla {plantilla_email_id})"
        recibo.observaciones = f"{obs_prev}\n{sufijo}".strip()
        session.add(recibo)
        await session.commit()
        return True

    # ─── Justificantes de Gasto (flujo 7) ──────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_PRESENTAR")])
    async def presentar_justificante_gasto(
        self,
        info: strawberry.Info,
        miembro_id: UUID,
        actividad_id: UUID,
        lineas: list[LineaJustificanteInput],
        partida_actividad_id: Optional[UUID] = None,
        agrupacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
        ejercicio: Optional[int] = None,
        presentado_por_tesorero_id: Optional[UUID] = None,
    ) -> str:
        """A1 — Presentar justificante con UNA O MÁS líneas referidas a la misma actividad.

        - D7.2: el presentador NO indica cuenta contable. Se resuelve al pagar
          (cuenta_contable_default del tipo de actividad o decisión del tesorero).
        - D7.4: agrupación derivada de la actividad si no se pasa.
        - D7.6: si el usuario tiene `JUST_APROBAR` y rellena `presentado_por_tesorero_id`,
          el justificante nace ACEPTADO.
        """
        session = info.context.session
        if presentado_por_tesorero_id is not None:
            if not await info.context.check_permission("JUST_APROBAR"):
                raise PermissionError(
                    "Solo el tesorero puede presentar justificantes en nombre de otros socios."
                )
        if not lineas:
            raise ValueError("Debe haber al menos una línea de gasto.")
        lineas_norm: list[dict] = [{
            "concepto": l.concepto,
            "importe": Decimal(str(l.importe)),
            "fecha_gasto": l.fecha_gasto,
            "observaciones": l.observaciones,
        } for l in lineas]
        service = JustificanteGastoService(session)
        j = await service.presentar(
            miembro_id=miembro_id,
            actividad_id=actividad_id,
            lineas=lineas_norm,
            partida_actividad_id=partida_actividad_id,
            agrupacion_id=agrupacion_id,
            observaciones=observaciones,
            ejercicio=ejercicio,
            presentado_por_tesorero_id=presentado_por_tesorero_id,
        )
        return str(j.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_ACEPTAR")])
    async def aceptar_justificante_gasto(
        self,
        info: strawberry.Info,
        justificante_id: UUID,
        aceptador_id: UUID,
    ) -> bool:
        """A3 — Aceptación intermedia por el responsable de la actividad (D7.5).
        El servicio valida que aceptador_id == actividad.responsable_id."""
        session = info.context.session
        service = JustificanteGastoService(session)
        await service.aceptar(justificante_id, aceptador_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_APROBAR")])
    async def aprobar_justificante_gasto(
        self,
        info: strawberry.Info,
        justificante_id: UUID,
        aprobador_id: UUID,
    ) -> bool:
        """A5 — El tesorero aprueba un justificante ya ACEPTADO por el responsable (D7.1)."""
        session = info.context.session
        service = JustificanteGastoService(session)
        await service.aprobar(justificante_id, aprobador_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_APROBAR")])
    async def rechazar_justificante_gasto(
        self,
        info: strawberry.Info,
        justificante_id: UUID,
        aprobador_id: UUID,
        motivo: str,
    ) -> bool:
        """A4/A6 — Rechazo. Puede dispararlo el responsable (PRESENTADO) o el tesorero (ACEPTADO)."""
        session = info.context.session
        service = JustificanteGastoService(session)
        await service.rechazar(justificante_id, aprobador_id, motivo)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_PAGAR")])
    async def pagar_justificante_gasto(
        self,
        info: strawberry.Info,
        justificante_id: UUID,
        cuenta_bancaria_id: UUID,
        modo_pago: str = "TRANSFERENCIA",
        fecha_pago: Optional[date] = None,
        referencia: Optional[str] = None,
        cuenta_contable_id: Optional[UUID] = None,
    ) -> str:
        """A7 — Registra el pago del justificante APROBADO. Crea ApunteCaja (GASTO)
        + asiento contable. Devuelve el ID del ApunteCaja.

        `cuenta_contable_id` opcional: si se omite, se resuelve por la cuenta_contable_default
        del tipo de actividad. Si tampoco está, error pidiendo que se indique.
        """
        session = info.context.session
        service = JustificanteGastoService(session)
        apunte = await service.pagar(
            justificante_id=justificante_id,
            cuenta_bancaria_id=cuenta_bancaria_id,
            modo_pago=modo_pago,
            fecha_pago=fecha_pago,
            referencia=referencia,
            cuenta_contable_id=cuenta_contable_id,
        )
        return str(apunte.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_PRESENTAR")])
    async def anular_justificante_gasto(
        self,
        info: strawberry.Info,
        justificante_id: UUID,
        motivo: Optional[str] = None,
    ) -> bool:
        session = info.context.session
        service = JustificanteGastoService(session)
        await service.anular(justificante_id, motivo)
        return True

    # ─── Solicitud de reducción de cuota ──────────────────────────────────────

    @strawberry.mutation
    async def presentar_solicitud_reduccion_cuota(
        self,
        info: strawberry.Info,
        miembro_id: UUID,
        motivo_reduccion_id: UUID,
        texto_solicitud: Optional[str] = None,
        ejercicio: Optional[int] = None,
    ) -> str:
        """El socio solicita que se le aplique una reducción de cuota.

        Nace en estado PRESENTADA. El documento acreditativo (paro, jubilación…)
        se sube aparte vía REST. Devuelve el id de la solicitud creada.
        """
        from ..modules.economico.models.cuotas import SolicitudReduccionCuota
        session = info.context.session
        anio = ejercicio or date.today().year
        existe = await session.execute(
            select(SolicitudReduccionCuota).where(
                SolicitudReduccionCuota.miembro_id == miembro_id,
                SolicitudReduccionCuota.ejercicio == anio,
                SolicitudReduccionCuota.estado == "PRESENTADA",
                SolicitudReduccionCuota.eliminado == False,
            )
        )
        if existe.scalar_one_or_none():
            raise ValueError("Ya hay una solicitud de reducción pendiente para este ejercicio.")
        sol = SolicitudReduccionCuota(
            miembro_id=miembro_id,
            motivo_reduccion_id=motivo_reduccion_id,
            ejercicio=anio,
            estado="PRESENTADA",
            texto_solicitud=texto_solicitud,
            fecha_presentacion=date.today(),
        )
        session.add(sol)
        await session.commit()
        return str(sol.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_EXEMPT")])
    async def aprobar_solicitud_reduccion_cuota(
        self,
        info: strawberry.Info,
        solicitud_id: UUID,
        resuelto_por_id: UUID,
    ) -> bool:
        """El tesorero aprueba la solicitud: fija el motivo de reducción individual
        del miembro (cuotas futuras) y recalcula la CuotaAnual del ejercicio en
        curso si existe y está impagada."""
        from ..modules.economico.models.cuotas import (
            SolicitudReduccionCuota, CuotaAnual, MotivoReduccionCuota, ImporteCuotaAnio,
        )
        from ..modules.membresia.models.miembro import Miembro
        session = info.context.session
        sol = await session.get(SolicitudReduccionCuota, solicitud_id)
        if not sol:
            raise ValueError("Solicitud no encontrada.")
        if sol.estado != "PRESENTADA":
            raise ValueError(f"La solicitud no está pendiente (estado actual: {sol.estado}).")
        sol.estado = "APROBADA"
        sol.resuelto_por_id = resuelto_por_id
        sol.fecha_resolucion = date.today()

        # Cuotas futuras: motivo de reducción individual del miembro
        miembro = await session.get(Miembro, sol.miembro_id)
        if miembro:
            miembro.motivo_reduccion_id = sol.motivo_reduccion_id

        # Ejercicio en curso: recalcular la CuotaAnual si existe e impagada
        motivo = await session.get(MotivoReduccionCuota, sol.motivo_reduccion_id)
        res = await session.execute(
            select(CuotaAnual).where(
                CuotaAnual.miembro_id == sol.miembro_id,
                CuotaAnual.ejercicio == sol.ejercicio,
                CuotaAnual.eliminado == False,
            )
        )
        cuota = res.scalar_one_or_none()
        if cuota and motivo and cuota.importe_pagado == Decimal("0.00"):
            cuota.motivo_reduccion_id = motivo.id
            if cuota.importe_cuota_anio_id:
                base = await session.get(ImporteCuotaAnio, cuota.importe_cuota_anio_id)
                if base:
                    cuota.importe = motivo.aplicar_a(base.importe)
        await session.commit()
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_EXEMPT")])
    async def rechazar_solicitud_reduccion_cuota(
        self,
        info: strawberry.Info,
        solicitud_id: UUID,
        resuelto_por_id: UUID,
        motivo: str,
    ) -> bool:
        """El tesorero rechaza la solicitud, indicando el motivo."""
        from ..modules.economico.models.cuotas import SolicitudReduccionCuota
        session = info.context.session
        sol = await session.get(SolicitudReduccionCuota, solicitud_id)
        if not sol:
            raise ValueError("Solicitud no encontrada.")
        if sol.estado != "PRESENTADA":
            raise ValueError(f"La solicitud no está pendiente (estado actual: {sol.estado}).")
        sol.estado = "RECHAZADA"
        sol.resuelto_por_id = resuelto_por_id
        sol.fecha_resolucion = date.today()
        sol.motivo_rechazo = motivo
        await session.commit()
        return True

    @strawberry.mutation
    async def anular_solicitud_reduccion_cuota(
        self,
        info: strawberry.Info,
        solicitud_id: UUID,
    ) -> bool:
        """El solicitante retira su solicitud mientras siga PRESENTADA."""
        from ..modules.economico.models.cuotas import SolicitudReduccionCuota
        session = info.context.session
        sol = await session.get(SolicitudReduccionCuota, solicitud_id)
        if not sol:
            raise ValueError("Solicitud no encontrada.")
        if sol.estado != "PRESENTADA":
            raise ValueError("Solo puede anularse una solicitud aún pendiente.")
        sol.estado = "ANULADA"
        await session.commit()
        return True

    # ─── Incremento voluntario de cuota ───────────────────────────────────────

    @strawberry.mutation
    async def modificar_incremento_cuota(
        self,
        info: strawberry.Info,
        miembro_id: UUID,
        incremento: Decimal,
        observaciones: Optional[str] = None,
    ) -> bool:
        """El socio decide pagar de más sobre su cuota base (incremento voluntario).

        Cantidad fija en € que se sumará al generar las cuotas. No requiere
        aprobación: solo se graba en el socio. Si hay una CuotaAnual del ejercicio
        en curso aún impagada, se recalcula para reflejar el cambio al momento.
        """
        from ..modules.economico.models.cuotas import (
            CuotaAnual, MotivoReduccionCuota, ImporteCuotaAnio,
        )
        from ..modules.membresia.models.miembro import Miembro
        session = info.context.session
        if incremento < Decimal("0.00"):
            raise ValueError("El incremento no puede ser negativo.")
        miembro = await session.get(Miembro, miembro_id)
        if not miembro:
            raise ValueError("Miembro no encontrado.")
        miembro.incremento_cuota = incremento
        miembro.incremento_cuota_obs = (observaciones or "").strip() or None

        # Recalcular la CuotaAnual del ejercicio en curso si existe e impagada
        anio = date.today().year
        res = await session.execute(
            select(CuotaAnual).where(
                CuotaAnual.miembro_id == miembro_id,
                CuotaAnual.ejercicio == anio,
                CuotaAnual.eliminado == False,
            )
        )
        cuota = res.scalar_one_or_none()
        if cuota and cuota.importe_pagado == Decimal("0.00") and cuota.importe_cuota_anio_id:
            base = await session.get(ImporteCuotaAnio, cuota.importe_cuota_anio_id)
            if base:
                motivo = None
                if cuota.motivo_reduccion_id:
                    motivo = await session.get(MotivoReduccionCuota, cuota.motivo_reduccion_id)
                base_efectiva = motivo.aplicar_a(base.importe) if motivo else base.importe
                cuota.importe = base_efectiva + incremento
        await session.commit()
        return True

    # ─── Flujo 1: Establecimiento de cuotas del ejercicio ─────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_EJERCICIO_CONFIG")])
    async def configurar_cuota_ejercicio(
        self,
        info: strawberry.Info,
        ejercicio: int,
        importe_base: float,
        clonar_de: Optional[int] = None,
        observaciones: Optional[str] = None,
    ) -> UUID:
        """Crea o actualiza la configuración de cuota base del ejercicio (D1.3 paso 1).
        Devuelve el id del ImporteCuotaAnio (registro BASE)."""
        from ..modules.economico.services.cuota_service import CuotaService
        session = info.context.session
        service = CuotaService(session)
        cfg = await service.configurar_ejercicio(
            ejercicio=ejercicio,
            importe_base=Decimal(str(importe_base)),
            clonar_de=clonar_de,
            observaciones=observaciones,
        )
        return cfg.id

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_GENERATE")])
    async def previsualizar_generacion_cuotas(
        self,
        info: strawberry.Info,
        ejercicio: int,
    ) -> PreviewGeneracionCuotasType:
        """Calcula nº miembros y total esperado por tipo antes de generar (A5)."""
        from ..modules.economico.services.cuota_service import CuotaService
        session = info.context.session
        service = CuotaService(session)
        p = await service.previsualizar_generacion(ejercicio)
        return PreviewGeneracionCuotasType(
            ejercicio=p["ejercicio"],
            importe_base=p["importe_base"],
            desglose=[DesgloseTipoMiembroType(**d) for d in p["desglose"]],
            n_generables=p["n_generables"],
            n_excluidos=p["n_excluidos"],
            n_existentes=p["n_existentes"],
            total_esperado=p["total_esperado"],
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_GENERATE")])
    async def generar_cuotas_individuales(
        self,
        info: strawberry.Info,
        ejercicio: int,
        fecha_vencimiento: Optional[date] = None,
    ) -> ResultadoGeneracionCuotasType:
        """Crea CuotaAnual para cada miembro activo (A6). Idempotente."""
        from ..modules.economico.services.cuota_service import CuotaService
        session = info.context.session
        service = CuotaService(session)
        r = await service.generar_cuotas_individuales(ejercicio, fecha_vencimiento)
        return ResultadoGeneracionCuotasType(**r)

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_GENERATE")])
    async def recalcular_cuota(
        self,
        info: strawberry.Info,
        cuota_id: UUID,
    ) -> UUID:
        """Recalcula el importe de una cuota Pendiente con la configuración actual (A7)."""
        from ..modules.economico.services.cuota_service import CuotaService
        session = info.context.session
        service = CuotaService(session)
        c = await service.recalcular_cuota(cuota_id)
        return c.id

    # ─── Flujo 1 — Catálogo de motivos de reducción (D1.5 + D1.6) ─────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_MOTIVO_REDUC_MGMT")])
    async def crear_motivo_reduccion(
        self,
        info: strawberry.Info,
        codigo: str,
        nombre: str,
        porcentaje_reduccion: float,
        descripcion: Optional[str] = None,
        orden: Optional[int] = 0,
        activo: Optional[bool] = True,
    ) -> UUID:
        """Crea un nuevo motivo en el catálogo. Permiso: TESORERO_CENTRAL (D1.6)."""
        from ..modules.economico.models.cuotas import MotivoReduccionCuota
        from decimal import Decimal
        import uuid
        if porcentaje_reduccion < 0 or porcentaje_reduccion > 100:
            raise ValueError("porcentaje_reduccion debe estar entre 0 y 100")
        session = info.context.session
        motivo = MotivoReduccionCuota(
            id=uuid.uuid4(),
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            porcentaje_reduccion=Decimal(str(porcentaje_reduccion)),
            orden=orden or 0,
            activo=activo if activo is not None else True,
        )
        session.add(motivo)
        await session.commit()
        await session.refresh(motivo)
        return motivo.id

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_MOTIVO_REDUC_MGMT")])
    async def actualizar_motivo_reduccion(
        self,
        info: strawberry.Info,
        id: UUID,
        codigo: Optional[str] = None,
        nombre: Optional[str] = None,
        porcentaje_reduccion: Optional[float] = None,
        descripcion: Optional[str] = None,
        orden: Optional[int] = None,
        activo: Optional[bool] = None,
    ) -> UUID:
        """Actualiza un motivo. D1.5: si el motivo ya tiene cuotas con recibo
        emitido/cobrado/fallido/anulado, el `porcentaje_reduccion` queda
        congelado y no se puede cambiar (los demás campos sí).
        Permiso: TESORERO_CENTRAL (D1.6)."""
        from ..modules.economico.models.cuotas import MotivoReduccionCuota
        from ..modules.economico.services.cuota_service import CuotaService
        from decimal import Decimal
        from sqlalchemy import select as _select
        session = info.context.session
        r = await session.execute(_select(MotivoReduccionCuota).where(MotivoReduccionCuota.id == id))
        motivo = r.scalars().first()
        if not motivo:
            raise ValueError(f"Motivo {id} no encontrado")

        # D1.5: porcentaje congelado si hay recibos
        if porcentaje_reduccion is not None:
            nuevo_pct = Decimal(str(porcentaje_reduccion))
            if nuevo_pct != motivo.porcentaje_reduccion:
                service = CuotaService(session)
                if await service.motivo_tiene_recibos(motivo.id):
                    raise ValueError(
                        "No se puede modificar el porcentaje de un motivo que ya tiene cuotas "
                        "con recibo emitido. Anula primero las cuotas afectadas (D1.5)."
                    )
                if nuevo_pct < 0 or nuevo_pct > 100:
                    raise ValueError("porcentaje_reduccion debe estar entre 0 y 100")
                motivo.porcentaje_reduccion = nuevo_pct

        if codigo is not None: motivo.codigo = codigo
        if nombre is not None: motivo.nombre = nombre
        if descripcion is not None: motivo.descripcion = descripcion
        if orden is not None: motivo.orden = orden
        if activo is not None: motivo.activo = activo

        await session.commit()
        return motivo.id

    # ─── Donaciones (flujo 6) ──────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("DON_CREATE")])
    async def registrar_donacion(
        self,
        info: strawberry.Info,
        importe: float,
        fecha_donacion: date,
        tipo: str = "DINERARIA",
        caracter: str = "PUNTUAL",
        miembro_id: Optional[UUID] = None,
        donante_nombre: Optional[str] = None,
        donante_dni: Optional[str] = None,
        donante_email: Optional[str] = None,
        donante_telefono: Optional[str] = None,
        concepto_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
        modo_ingreso: Optional[str] = None,
        referencia_pago: Optional[str] = None,
        descripcion_especie: Optional[str] = None,
        valoracion: Optional[float] = None,
        documento_valoracion: Optional[str] = None,
        anonima: bool = False,
        observaciones: Optional[str] = None,
        agrupacion_id: Optional[UUID] = None,
        cobrar_inmediato: bool = False,
        cuenta_bancaria_id: Optional[UUID] = None,
    ) -> str:
        """A1 — Registra una donación. Si `cobrar_inmediato=True` ejecuta A2 en el acto."""
        session = info.context.session
        service = DonacionService(session)
        donacion = await service.registrar(
            importe=Decimal(str(importe)),
            fecha_donacion=fecha_donacion,
            tipo=tipo,
            caracter=caracter,
            miembro_id=miembro_id,
            donante_nombre=donante_nombre,
            donante_dni=donante_dni,
            donante_email=donante_email,
            donante_telefono=donante_telefono,
            concepto_id=concepto_id,
            campania_id=campania_id,
            modo_ingreso=modo_ingreso,
            referencia_pago=referencia_pago,
            descripcion_especie=descripcion_especie,
            valoracion=Decimal(str(valoracion)) if valoracion is not None else None,
            documento_valoracion=documento_valoracion,
            anonima=anonima,
            observaciones=observaciones,
            agrupacion_id=agrupacion_id,
            cobrar_inmediato=cobrar_inmediato,
            cuenta_bancaria_id=cuenta_bancaria_id,
        )
        return str(donacion.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("DON_CREATE")])
    async def marcar_donacion_cobrada(
        self,
        info: strawberry.Info,
        donacion_id: UUID,
        cuenta_bancaria_id: Optional[UUID] = None,
        fecha_cobro: Optional[date] = None,
    ) -> str:
        """A2 — Pasa REGISTRADA → COBRADA y genera ApunteCaja + asiento (D6.2)."""
        session = info.context.session
        service = DonacionService(session)
        donacion = await service.marcar_cobrada(
            donacion_id=donacion_id,
            cuenta_bancaria_id=cuenta_bancaria_id,
            fecha_cobro=fecha_cobro,
        )
        return str(donacion.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("DON_CREATE")])
    async def anular_donacion(
        self,
        info: strawberry.Info,
        donacion_id: UUID,
        motivo: Optional[str] = None,
    ) -> str:
        """A4 — Anula una donación. Revierte el asiento si lo tenía."""
        session = info.context.session
        service = DonacionService(session)
        donacion = await service.anular(donacion_id=donacion_id, motivo=motivo)
        return str(donacion.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("DON_CERT")])
    async def emitir_certificado_donacion_anual(
        self,
        info: strawberry.Info,
        ejercicio: int,
        nif_donante: str,
        tipo: str,  # DINERARIA | ESPECIE (D6.6)
    ) -> CertificadoEmitidoType:
        """A3 — Emite el certificado anual del donante para el ejercicio y tipo dados.
        Lee los datos de la organización (nombre + NIF) de la configuración global."""
        import base64
        from sqlalchemy import select as _select
        from app.modules.configuracion.models.configuracion import Configuracion

        session = info.context.session

        # Leer datos de la organización desde configuraciones
        async def _cfg(clave: str, default: str = "") -> str:
            r = await session.execute(_select(Configuracion).where(Configuracion.clave == clave))
            row = r.scalars().first()
            return (row.valor if row and row.valor else default) or default

        organizacion_nombre = (
            await _cfg("organizacion.nombre")
            or await _cfg("org.nombre")
            or "Asociación"
        )
        organizacion_nif = (
            await _cfg("organizacion.nif")
            or await _cfg("org.nif")
            or "—"
        )

        service = DonacionService(session)
        numero, pdf_bytes = await service.emitir_certificado_anual(
            ejercicio=ejercicio,
            nif_donante=nif_donante,
            tipo=tipo,
            organizacion_nombre=organizacion_nombre,
            organizacion_nif=organizacion_nif,
        )
        return CertificadoEmitidoType(
            numero=numero,
            pdf_base64=base64.b64encode(pdf_bytes).decode("ascii"),
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("DON_CERT")])
    async def listar_donaciones_certificables(
        self,
        info: strawberry.Info,
        ejercicio: int,
    ) -> list[CertificableDonacionType]:
        """A6 — Lista los donantes con donaciones COBRADAS no certificadas del ejercicio,
        agrupadas por NIF + tipo (D6.3, D6.6)."""
        session = info.context.session
        service = DonacionService(session)
        items = await service.listar_certificables_por_ejercicio(ejercicio)
        return [
            CertificableDonacionType(
                nif=item["nif"],
                nombre=item["nombre"],
                tipo=item["tipo"],
                total=float(item["total"]),
                n_donaciones=item["n"],
                donacion_ids=item["donacion_ids"],
                todas_certificadas=item["todas_certificadas"],
            )
            for item in items
        ]
