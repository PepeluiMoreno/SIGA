"""Resolvers custom para operaciones de negocio de tesorería y contabilidad."""
from __future__ import annotations

import base64
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

import strawberry
from sqlalchemy import select

from app.modules.economico.models.contabilidad import TipoCuentaContable, TipoAsientoContable
from app.modules.economico.models.cuotas import CuotaAnual
from app.modules.economico.models.tesoreria import TipoMovimientoTesoreria
from app.modules.economico.services.tesoreria_service import TesoreriaService
from app.modules.economico.services.contabilidad_service import ContabilidadService
from app.modules.economico.services.cierre_service import CierreEjercicioService
from app.modules.economico.services.pdf.libro_diario import generar_libro_diario_csv
from app.graphql.types_auto import CuotaAnualType
from app.graphql.permissions import RequireTransaction


# ---------------------------------------------------------------------------
# Tipos GraphQL para cierre contable PCESFL
# ---------------------------------------------------------------------------

@strawberry.type
class BalanceSeccionType:
    """Sección del balance con sus subsecciones (clave → importe)."""
    nombre: str
    subsecciones: strawberry.scalars.JSON  # dict[str, float]
    total: float


@strawberry.type
class BalancePcesflType:
    """Balance estructurado según PCESFL 2013."""
    ejercicio: int
    activo_no_corriente: strawberry.scalars.JSON
    activo_corriente: strawberry.scalars.JSON
    patrimonio_neto: strawberry.scalars.JSON
    pasivo_no_corriente: strawberry.scalars.JSON
    pasivo_corriente: strawberry.scalars.JSON
    total_activo: float
    total_patrimonio_neto: float
    total_pasivo_no_corriente: float
    total_pasivo_corriente: float
    total_pasivo_y_pn: float
    diferencia: float
    cuadra: bool


@strawberry.type
class CuentaResultadosType:
    """Cuenta de Resultados PCESFL — formato Excedente del ejercicio."""
    ejercicio: int
    ingresos_actividad_propia: float
    gastos_actividad_propia: float
    excedente_actividad_propia: float
    ingresos_mercantil: float
    gastos_mercantil: float
    excedente_mercantil: float
    ingresos_financieros: float
    gastos_financieros: float
    resultado_financiero: float
    excedente_antes_impuestos: float
    impuesto_sobre_beneficios: float
    excedente_ejercicio: float


@strawberry.type
class EstadoCierreType:
    """Checklist del estado del cierre del ejercicio."""
    ejercicio: int
    todos_confirmados: bool
    num_borradores: int
    balance_cuadra: bool
    total_debe: float
    total_haber: float
    regularizacion_hecha: bool
    cierre_hecho: bool
    apertura_siguiente_hecha: bool
    conciliacion_completa: bool = True
    num_apuntes_sin_conciliar: int = 0


@strawberry.type
class SaldoCuentaType:
    """Saldo neto (debe-haber) de una cuenta contable en un ejercicio."""
    codigo: str
    saldo: float


# Modelo 182 (Flujo 11)
@strawberry.type
class Modelo182DonanteType:
    nif: str
    nombre: str
    tipo: int  # 1=PF, 2=PJ
    clave: str = "A"  # A = dineraria, B = en especie (D11.4)
    importe: float
    n_donaciones: int


@strawberry.type
class Modelo182ExcluidoType:
    donacion_id: Optional[str] = None
    fecha: Optional[str] = None
    importe: float = 0.0
    nif: Optional[str] = None
    motivo: str = ""


@strawberry.type
class AgregadoModelo182Type:
    ejercicio: int
    n_incluidos: int
    n_excluidos: int
    importe_total: float
    incluidos: list[Modelo182DonanteType]
    excluidos: list[Modelo182ExcluidoType]


@strawberry.type
class Presentacion182Type:
    id: uuid.UUID
    ejercicio: int
    fecha_envio: date
    codigo_aeat: Optional[str] = None
    n_donantes: int
    importe_total: float
    archivo_acuse: Optional[str] = None
    observaciones: Optional[str] = None


# Cuentas Anuales (Flujo 10) — uses JSON fields for snapshots
@strawberry.type
class CuentasAnualesType:
    id: uuid.UUID
    ejercicio: int
    estado: str
    balance_pcesfl: strawberry.scalars.JSON
    cuenta_resultados: strawberry.scalars.JSON
    memoria: strawberry.scalars.JSON
    excedente: Optional[float] = None
    fecha_aprobacion: Optional[date] = None
    aprobado_por_id: Optional[uuid.UUID] = None
    acta_referencia: Optional[str] = None
    fecha_deposito: Optional[date] = None
    archivo_acuse_recibo: Optional[str] = None
    observaciones: Optional[str] = None


@strawberry.type
class LineaBalanceSumasSaldosType:
    """Una fila del balance de sumas y saldos (instantánea, sin persistir)."""
    codigo: str
    nombre: str
    tipo: str
    total_debe: float
    total_haber: float
    saldo: float


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

@strawberry.input
class CrearCuentaBancariaInput:
    nombre: str
    iban: str
    banco_nombre: str
    bic_swift: Optional[str] = None
    agrupacion_id: Optional[uuid.UUID] = None
    observaciones: Optional[str] = None


@strawberry.input
class CrearMovimientoTesoreriaInput:
    cuenta_id: uuid.UUID
    fecha: date
    importe: float
    tipo: str
    concepto: str
    referencia_externa: Optional[str] = None
    entidad_origen_tipo: Optional[str] = None
    entidad_origen_id: Optional[uuid.UUID] = None
    observaciones: Optional[str] = None


@strawberry.input
class CrearConciliacionBancariaInput:
    cuenta_id: uuid.UUID
    fecha_inicio: date
    fecha_fin: date
    saldo_inicial_extracto: float
    saldo_final_extracto: float


@strawberry.input
class CrearCuentaContableInput:
    codigo: str
    nombre: str
    tipo: str
    nivel: int
    padre_id: Optional[uuid.UUID] = None
    es_dotacion: bool = False
    descripcion: Optional[str] = None


@strawberry.input
class CrearAsientoContableInput:
    ejercicio: int
    numero_asiento: int
    fecha: date
    glosa: str
    tipo_asiento: str = "GESTION"
    observaciones: Optional[str] = None


@strawberry.input
class CrearApunteContableInput:
    asiento_id: uuid.UUID
    cuenta_id: uuid.UUID
    debe: float = 0.0
    haber: float = 0.0
    concepto: str = ""
    actividad_id: Optional[uuid.UUID] = None
    observaciones: Optional[str] = None


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

@strawberry.type
class MiembroElegibleType:
    """Miembro elegible para figurar como gastador en un justificante.

    Type ligero para no exponer toda la ficha del miembro al socio que rellena.
    """
    id: uuid.UUID
    nombre: str
    apellido1: str
    apellido2: Optional[str] = None
    email: Optional[str] = None


@strawberry.type
class AmbitoTesoreriaType:
    """Ámbito de tesorería del usuario que consulta.

    - ve_todas=True  → tesorero general / matriz: ve todas las solicitudes.
    - ve_todas=False → tesorero regional: solo las de socios cuya agrupación
      está en `agrupacion_ids` (esas agrupaciones y sus descendientes).
    """
    ve_todas: bool
    agrupacion_ids: list[uuid.UUID]


@strawberry.type
class EconomicoQuery:

    @strawberry.field
    async def ambito_tesoreria(self, info: strawberry.Info) -> AmbitoTesoreriaType:
        """Calcula qué solicitudes de reducción de cuota puede ver el usuario que
        consulta, según sus nombramientos de tesorero vigentes (vista
        v_nombramientos_vigentes → cargo → rol TESORERO).

        - Sin nombramiento de tesorero (admin / tesorero general) → ve todas.
        - Tesorero de la agrupación matriz o con cargo global → ve todas.
        - Tesorero regional → solo su agrupación y descendientes.
        """
        from app.modules.membresia.models.nombramiento_vigente import NombramientoVigente
        from app.modules.acceso.models.cargo import CargoRol
        from app.modules.acceso.models.rol import Rol
        from app.modules.core.geografico.direccion import UnidadOrganizativa

        session = info.context.session
        user = info.context.user
        if user is None or getattr(user, 'miembro_id', None) is None:
            return AmbitoTesoreriaType(ve_todas=False, agrupacion_ids=[])

        # Agrupaciones donde el usuario es tesorero vigente
        res = await session.execute(
            select(NombramientoVigente.agrupacion_id)
            .join(CargoRol, CargoRol.cargo_id == NombramientoVigente.cargo_id)
            .join(Rol, Rol.id == CargoRol.rol_id)
            .where(
                NombramientoVigente.miembro_id == user.miembro_id,
                Rol.codigo == 'TESORERO',
            )
        )
        agrupaciones = [row[0] for row in res.all()]

        # Sin nombramiento de tesorero: si ha llegado aquí tiene el permiso
        # (admin / tesorero general) → ve todas.
        if not agrupaciones:
            return AmbitoTesoreriaType(ve_todas=True, agrupacion_ids=[])

        # Cargo global (agrupación NULL) o tesorero de la matriz → ve todas
        matriz_id = await session.scalar(
            select(UnidadOrganizativa.id).where(UnidadOrganizativa.agrupacion_padre_id.is_(None))
        )
        if any(a is None for a in agrupaciones) or (matriz_id in agrupaciones):
            return AmbitoTesoreriaType(ve_todas=True, agrupacion_ids=[])

        # Tesorero regional: su(s) agrupación(es) + descendientes
        filas = (await session.execute(
            select(UnidadOrganizativa.id, UnidadOrganizativa.agrupacion_padre_id)
        )).all()
        hijos: dict = {}
        for uid_, padre in filas:
            hijos.setdefault(padre, []).append(uid_)
        visibles: set = set()
        pila = [a for a in agrupaciones if a is not None]
        while pila:
            a = pila.pop()
            if a in visibles:
                continue
            visibles.add(a)
            pila.extend(hijos.get(a, []))
        return AmbitoTesoreriaType(ve_todas=False, agrupacion_ids=list(visibles))

    @strawberry.field
    async def cuenta_por_codigo(self, info: strawberry.Info, codigo: str) -> Optional[uuid.UUID]:
        """Devuelve el id de la cuenta contable por su código contable."""
        service = ContabilidadService(info.context.session)
        cuenta = await service.obtener_cuenta_por_codigo(codigo)
        return cuenta.id if cuenta else None

    @strawberry.field(permission_classes=[RequireTransaction("ECO_JUSTIFICANTE_PRESENTAR")])
    async def miembros_elegibles_para_justificante(
        self, info: strawberry.Info, actividad_id: uuid.UUID,
    ) -> list[MiembroElegibleType]:
        """Lista de miembros que pueden figurar como gastador en un justificante
        imputado a la actividad indicada.

        - Actividad de campaña con grupo asignado: miembros del grupo (activos).
        - Actividad sin campaña o sin grupo: todos los miembros activos (fallback).
        """
        from app.modules.economico.services.justificante_gasto_service import JustificanteGastoService
        service = JustificanteGastoService(info.context.session)
        miembros = await service.miembros_elegibles_para_actividad(actividad_id)
        return [
            MiembroElegibleType(
                id=m.id, nombre=m.nombre,
                apellido1=m.apellido1, apellido2=m.apellido2,
                email=m.email,
            )
            for m in miembros
        ]

    @strawberry.field
    async def motivo_tiene_recibos(
        self,
        info: strawberry.Info,
        motivo_id: uuid.UUID,
    ) -> bool:
        """D1.5: ¿el motivo tiene cuotas asociadas con al menos un recibo emitido?
        Si es true, su porcentaje_reduccion queda congelado.
        """
        from app.modules.economico.services.cuota_service import CuotaService
        service = CuotaService(info.context.session)
        return await service.motivo_tiene_recibos(motivo_id)

    @strawberry.field
    async def cuenta_tiene_apuntes_confirmados(
        self,
        info: strawberry.Info,
        cuenta_id: uuid.UUID,
    ) -> bool:
        """¿La cuenta tiene apuntes en asientos CONFIRMADOS?

        Si lo tiene, no se debe permitir cambiar código, tipo, padre ni eliminarla
        (rompería la integridad contable). Solo renombrar y activar/desactivar.
        """
        service = ContabilidadService(info.context.session)
        return await service.tiene_apuntes_confirmados(cuenta_id)

    @strawberry.field
    async def saldo_cuenta(
        self,
        info: strawberry.Info,
        cuenta_id: uuid.UUID,
        ejercicio: Optional[int] = None,
        fecha_fin: Optional[date] = None,
    ) -> float:
        """Calcula el saldo de una cuenta contable."""
        service = ContabilidadService(info.context.session)
        saldo = await service.calcular_saldo_cuenta(cuenta_id, fecha_fin=fecha_fin, ejercicio=ejercicio)
        return float(saldo)

    @strawberry.field
    async def cuotas_por_miembro(
        self,
        info: strawberry.Info,
        miembro_id: uuid.UUID,
    ) -> list[CuotaAnualType]:
        """Devuelve el historial de cuotas de un miembro ordenadas por ejercicio descendente."""
        session = info.context.session
        stmt = (
            select(CuotaAnual)
            .where(CuotaAnual.miembro_id == miembro_id)
            .order_by(CuotaAnual.ejercicio.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    # ── Cierre contable PCESFL ──────────────────────────────────────────────

    @strawberry.field(permission_classes=[RequireTransaction("ECO_CIERRE_CONSULTAR")])
    async def balance_pcesfl(
        self,
        info: strawberry.Info,
        ejercicio: int,
        fecha_fin: Optional[date] = None,
    ) -> BalancePcesflType:
        """Balance del ejercicio estructurado según PCESFL 2013."""
        service = CierreEjercicioService(info.context.session)
        b = await service.calcular_balance_pcesfl(ejercicio, fecha_fin)
        totales = b["totales"]
        return BalancePcesflType(
            ejercicio=ejercicio,
            activo_no_corriente={k: float(v) for k, v in b["activo_no_corriente"].items()},
            activo_corriente={k: float(v) for k, v in b["activo_corriente"].items()},
            patrimonio_neto={k: float(v) for k, v in b["patrimonio_neto"].items()},
            pasivo_no_corriente={k: float(v) for k, v in b["pasivo_no_corriente"].items()},
            pasivo_corriente={k: float(v) for k, v in b["pasivo_corriente"].items()},
            total_activo=float(totales["total_activo"]),
            total_patrimonio_neto=float(totales["total_patrimonio_neto"]),
            total_pasivo_no_corriente=float(totales["total_pasivo_no_corriente"]),
            total_pasivo_corriente=float(totales["total_pasivo_corriente"]),
            total_pasivo_y_pn=float(totales["total_pasivo_y_pn"]),
            diferencia=float(totales["diferencia"]),
            cuadra=abs(totales["diferencia"]) < Decimal("0.01"),
        )

    @strawberry.field(permission_classes=[RequireTransaction("ECO_CIERRE_CONSULTAR")])
    async def cuenta_resultados(
        self,
        info: strawberry.Info,
        ejercicio: int,
        fecha_fin: Optional[date] = None,
    ) -> CuentaResultadosType:
        """Cuenta de Resultados del ejercicio en formato PCESFL (Excedente)."""
        service = CierreEjercicioService(info.context.session)
        r = await service.calcular_cuenta_resultados(ejercicio, fecha_fin)
        return CuentaResultadosType(
            ejercicio=ejercicio,
            ingresos_actividad_propia=float(r["ingresos_actividad_propia"]),
            gastos_actividad_propia=float(r["gastos_actividad_propia"]),
            excedente_actividad_propia=float(r["excedente_actividad_propia"]),
            ingresos_mercantil=float(r["ingresos_mercantil"]),
            gastos_mercantil=float(r["gastos_mercantil"]),
            excedente_mercantil=float(r["excedente_mercantil"]),
            ingresos_financieros=float(r["ingresos_financieros"]),
            gastos_financieros=float(r["gastos_financieros"]),
            resultado_financiero=float(r["resultado_financiero"]),
            excedente_antes_impuestos=float(r["excedente_antes_impuestos"]),
            impuesto_sobre_beneficios=float(r["impuesto_sobre_beneficios"]),
            excedente_ejercicio=float(r["excedente_ejercicio"]),
        )

    @strawberry.field(permission_classes=[RequireTransaction("ECO_CIERRE_CONSULTAR")])
    async def estado_cierre(
        self,
        info: strawberry.Info,
        ejercicio: int,
    ) -> EstadoCierreType:
        """Checklist del estado del cierre del ejercicio."""
        service = CierreEjercicioService(info.context.session)
        e = await service.verificar_estado_cierre(ejercicio)
        return EstadoCierreType(
            ejercicio=ejercicio,
            todos_confirmados=e["todos_confirmados"],
            num_borradores=e["num_borradores"],
            balance_cuadra=e["balance_cuadra"],
            total_debe=e["total_debe"],
            total_haber=e["total_haber"],
            regularizacion_hecha=e["regularizacion_hecha"],
            cierre_hecho=e["cierre_hecho"],
            apertura_siguiente_hecha=e["apertura_siguiente_hecha"],
            conciliacion_completa=e.get("conciliacion_completa", True),
            num_apuntes_sin_conciliar=e.get("num_apuntes_sin_conciliar", 0),
        )

    @strawberry.field
    async def balance_sumas_y_saldos(
        self,
        info: strawberry.Info,
        ejercicio: int,
        fecha_corte: Optional[date] = None,
        solo_con_saldo: bool = True,
    ) -> list[LineaBalanceSumasSaldosType]:
        """Balance de sumas y saldos del ejercicio a una fecha. No se persiste.

        Devuelve una fila por cuenta con total_debe, total_haber y saldo.
        Solo incluye asientos confirmados con fecha ≤ fecha_corte.
        Si solo_con_saldo=true (por defecto), omite cuentas sin movimientos.
        """
        service = ContabilidadService(info.context.session)
        filas = await service.calcular_balance_sumas_y_saldos(
            ejercicio=ejercicio,
            fecha_corte=fecha_corte,
            solo_con_saldo=solo_con_saldo,
        )
        return [
            LineaBalanceSumasSaldosType(
                codigo=f["codigo"],
                nombre=f["nombre"],
                tipo=f["tipo"],
                total_debe=float(f["total_debe"]),
                total_haber=float(f["total_haber"]),
                saldo=float(f["saldo"]),
            )
            for f in filas
        ]

    @strawberry.field
    async def saldos_cuentas(
        self,
        info: strawberry.Info,
        ejercicio: int,
        fecha_fin: Optional[date] = None,
    ) -> list[SaldoCuentaType]:
        """Saldos netos por código de cuenta para todas las cuentas con movimientos
        en el ejercicio. Solo cuenta asientos CONFIRMADOS."""
        service = CierreEjercicioService(info.context.session)
        saldos = await service.calcular_saldos_cuentas(ejercicio, fecha_fin)
        return [SaldoCuentaType(codigo=k, saldo=float(v)) for k, v in saldos.items()]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_CIERRE_CONSULTAR")])
    async def libro_diario_csv(
        self,
        info: strawberry.Info,
        ejercicio: int,
        organizacion_nombre: str = "Organización",
    ) -> str:
        """Genera el Libro Diario del ejercicio en formato CSV (UTF-8 BOM, separador `;`).
        Devuelve el CSV codificado en base64 listo para descargar desde el frontend."""
        contenido = await generar_libro_diario_csv(
            info.context.session, ejercicio, organizacion_nombre
        )
        return base64.b64encode(contenido).decode("ascii")

    # ── Cuentas Anuales (Flujo 10) ──────────────────────────────────────────

    @strawberry.field(permission_classes=[RequireTransaction("ECO_CUENTAS_ANUALES_LISTAR")])
    async def cuentas_anuales(self, info: strawberry.Info) -> list[CuentasAnualesType]:
        """Listado de Cuentas Anuales (todas las que existen, cualquier estado)."""
        from app.modules.economico.services.cuentas_anuales_service import CuentasAnualesService
        service = CuentasAnualesService(info.context.session)
        items = await service.listar()
        return [
            CuentasAnualesType(
                id=c.id,
                ejercicio=c.ejercicio,
                estado=c.estado,
                balance_pcesfl=c.balance_pcesfl or {},
                cuenta_resultados=c.cuenta_resultados or {},
                memoria=c.memoria or {},
                excedente=float(c.excedente) if c.excedente is not None else None,
                fecha_aprobacion=c.fecha_aprobacion,
                aprobado_por_id=c.aprobado_por_id,
                acta_referencia=c.acta_referencia,
                fecha_deposito=c.fecha_deposito,
                archivo_acuse_recibo=c.archivo_acuse_recibo,
                observaciones=c.observaciones,
            ) for c in items
        ]

    # ── Modelo 182 (Flujo 11) ───────────────────────────────────────────────

    @strawberry.field(permission_classes=[RequireTransaction("ECO_MODELO182_GENERAR")])
    async def agregado_modelo_182(
        self, info: strawberry.Info, ejercicio: int
    ) -> AgregadoModelo182Type:
        """A1 — Calcula el agregado anual del Modelo 182 (donantes incluibles +
        excluidos), sin persistirlo. D11.1, D11.2."""
        from app.modules.economico.services.modelo_182_service import Modelo182Service
        service = Modelo182Service(info.context.session)
        ag = await service.generar_agregado(ejercicio)
        return AgregadoModelo182Type(
            ejercicio=ag["ejercicio"],
            n_incluidos=ag["n_incluidos"],
            n_excluidos=ag["n_excluidos"],
            importe_total=ag["importe_total"],
            incluidos=[
                Modelo182DonanteType(
                    nif=e["nif"], nombre=e["nombre"], tipo=e["tipo"],
                    clave=e.get("clave") or "A",
                    importe=e["importe"], n_donaciones=e["n_donaciones"],
                ) for e in ag["incluidos"]
            ],
            excluidos=[
                Modelo182ExcluidoType(
                    donacion_id=x.get("donacion_id"),
                    fecha=x.get("fecha"),
                    importe=x.get("importe", 0.0),
                    nif=x.get("nif"),
                    motivo=x.get("motivo", ""),
                ) for x in ag["excluidos"]
            ],
        )

    @strawberry.field(permission_classes=[RequireTransaction("ECO_MODELO182_LISTAR")])
    async def presentaciones_modelo_182(
        self, info: strawberry.Info
    ) -> list[Presentacion182Type]:
        from app.modules.economico.services.modelo_182_service import Modelo182Service
        service = Modelo182Service(info.context.session)
        items = await service.listar_presentaciones()
        return [
            Presentacion182Type(
                id=p.id, ejercicio=p.ejercicio, fecha_envio=p.fecha_envio,
                codigo_aeat=p.codigo_aeat, n_donantes=p.n_donantes,
                importe_total=float(p.importe_total), archivo_acuse=p.archivo_acuse,
                observaciones=p.observaciones,
            ) for p in items
        ]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_CUENTAS_ANUALES_LISTAR")])
    async def cuentas_anuales_por_ejercicio(
        self, info: strawberry.Info, ejercicio: int
    ) -> Optional[CuentasAnualesType]:
        """Devuelve las CCAA del ejercicio indicado, o null si no existen."""
        from app.modules.economico.services.cuentas_anuales_service import CuentasAnualesService
        service = CuentasAnualesService(info.context.session)
        c = await service.obtener_por_ejercicio(ejercicio)
        if not c:
            return None
        return CuentasAnualesType(
            id=c.id,
            ejercicio=c.ejercicio,
            estado=c.estado,
            balance_pcesfl=c.balance_pcesfl or {},
            cuenta_resultados=c.cuenta_resultados or {},
            memoria=c.memoria or {},
            excedente=float(c.excedente) if c.excedente is not None else None,
            fecha_aprobacion=c.fecha_aprobacion,
            aprobado_por_id=c.aprobado_por_id,
            acta_referencia=c.acta_referencia,
            fecha_deposito=c.fecha_deposito,
            archivo_acuse_recibo=c.archivo_acuse_recibo,
            observaciones=c.observaciones,
        )


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------

@strawberry.type
class EconomicoMutation:

    # ── Tesorería ────────────────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CUENTA_CREAR")])
    async def crear_cuenta_bancaria(self, info: strawberry.Info, data: CrearCuentaBancariaInput) -> uuid.UUID:
        service = TesoreriaService(info.context.session)
        cuenta = await service.crear_cuenta_bancaria(
            nombre=data.nombre,
            iban=data.iban,
            banco_nombre=data.banco_nombre,
            bic_swift=data.bic_swift,
            agrupacion_id=data.agrupacion_id,
            observaciones=data.observaciones,
        )
        return cuenta.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_MOVIMIENTO_REGISTRAR")])
    async def crear_movimiento_tesoreria(self, info: strawberry.Info, data: CrearMovimientoTesoreriaInput) -> uuid.UUID:
        service = TesoreriaService(info.context.session)
        movimiento = await service.registrar_movimiento(
            cuenta_id=data.cuenta_id,
            fecha=data.fecha,
            importe=Decimal(str(data.importe)),
            tipo=TipoMovimientoTesoreria(data.tipo),
            concepto=data.concepto,
            referencia_externa=data.referencia_externa,
            entidad_origen_tipo=data.entidad_origen_tipo,
            entidad_origen_id=data.entidad_origen_id,
            observaciones=data.observaciones,
        )
        return movimiento.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CONCILIACION_REALIZAR")])
    async def marcar_movimiento_conciliado(
        self, info: strawberry.Info, movimiento_id: uuid.UUID, fecha_conciliacion: Optional[date] = None
    ) -> bool:
        service = TesoreriaService(info.context.session)
        await service.marcar_movimiento_conciliado(movimiento_id, fecha_conciliacion)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CONCILIACION_REALIZAR")])
    async def crear_conciliacion_bancaria(self, info: strawberry.Info, data: CrearConciliacionBancariaInput) -> uuid.UUID:
        service = TesoreriaService(info.context.session)
        conciliacion = await service.crear_conciliacion_bancaria(
            cuenta_id=data.cuenta_id,
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
            saldo_inicial_extracto=Decimal(str(data.saldo_inicial_extracto)),
            saldo_final_extracto=Decimal(str(data.saldo_final_extracto)),
        )
        return conciliacion.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CONCILIACION_REALIZAR")])
    async def confirmar_conciliacion(self, info: strawberry.Info, conciliacion_id: uuid.UUID) -> bool:
        service = TesoreriaService(info.context.session)
        await service.confirmar_conciliacion(conciliacion_id)
        return True

    # ── Contabilidad ─────────────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def crear_cuenta_contable(self, info: strawberry.Info, data: CrearCuentaContableInput) -> uuid.UUID:
        """Crea una cuenta del plan contable. Restringido al rol TESORERO de la organización matriz.
        El plan de cuentas es un activo único de la asociación; los tesoreros de agrupación no pueden alterarlo."""
        service = ContabilidadService(info.context.session)
        cuenta = await service.crear_cuenta_contable(
            codigo=data.codigo,
            nombre=data.nombre,
            tipo=TipoCuentaContable(data.tipo),
            nivel=data.nivel,
            padre_id=data.padre_id,
            es_dotacion=data.es_dotacion,
            descripcion=data.descripcion,
        )
        return cuenta.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def actualizar_cuenta_contable(
        self,
        info: strawberry.Info,
        id: uuid.UUID,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        activa: Optional[bool] = None,
        permite_asiento: Optional[bool] = None,
    ) -> uuid.UUID:
        """Actualiza una cuenta del plan contable (mismo permiso que crear)."""
        from sqlalchemy import select as _select
        from app.modules.economico.models.contabilidad import CuentaContable
        session = info.context.session
        r = await session.execute(_select(CuentaContable).where(CuentaContable.id == id))
        cuenta = r.scalars().first()
        if not cuenta:
            raise ValueError(f"Cuenta {id} no encontrada")
        if nombre is not None: cuenta.nombre = nombre
        if descripcion is not None: cuenta.descripcion = descripcion
        if activa is not None: cuenta.activa = activa
        if permite_asiento is not None: cuenta.permite_asiento = permite_asiento
        await session.commit()
        return cuenta.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def desactivar_cuenta_contable(self, info: strawberry.Info, id: uuid.UUID) -> bool:
        """Desactiva una cuenta del plan contable. No se elimina por integridad referencial
        con asientos históricos — se marca como inactiva."""
        from sqlalchemy import select as _select
        from app.modules.economico.models.contabilidad import CuentaContable
        session = info.context.session
        r = await session.execute(_select(CuentaContable).where(CuentaContable.id == id))
        cuenta = r.scalars().first()
        if not cuenta:
            raise ValueError(f"Cuenta {id} no encontrada")
        cuenta.activa = False
        await session.commit()
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ASIENTO_CREAR")])
    async def crear_asiento_contable(self, info: strawberry.Info, data: CrearAsientoContableInput) -> uuid.UUID:
        service = ContabilidadService(info.context.session)
        asiento = await service.crear_asiento(
            ejercicio=data.ejercicio,
            numero_asiento=data.numero_asiento,
            fecha=data.fecha,
            glosa=data.glosa,
            tipo_asiento=TipoAsientoContable(data.tipo_asiento),
            observaciones=data.observaciones,
        )
        return asiento.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ASIENTO_CREAR")])
    async def crear_apunte_contable(self, info: strawberry.Info, data: CrearApunteContableInput) -> uuid.UUID:
        service = ContabilidadService(info.context.session)
        apunte = await service.crear_apunte(
            asiento_id=data.asiento_id,
            cuenta_id=data.cuenta_id,
            debe=Decimal(str(data.debe)),
            haber=Decimal(str(data.haber)),
            concepto=data.concepto,
            actividad_id=data.actividad_id,
            observaciones=data.observaciones,
        )
        return apunte.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ASIENTO_APROBAR")])
    async def confirmar_asiento(self, info: strawberry.Info, asiento_id: uuid.UUID) -> bool:
        service = ContabilidadService(info.context.session)
        await service.confirmar_asiento(asiento_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ASIENTO_APROBAR")])
    async def anular_asiento(self, info: strawberry.Info, asiento_id: uuid.UUID) -> bool:
        service = ContabilidadService(info.context.session)
        await service.anular_asiento(asiento_id)
        return True

    # ── Cierre contable PCESFL (Flujo 9) ────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CIERRE_EJECUTAR")])
    async def generar_asiento_regularizacion(
        self, info: strawberry.Info, ejercicio: int
    ) -> uuid.UUID:
        """A1 — Asiento de regularización: salda cuentas grupo 6 y 7 contra la
        cuenta 129 (Excedente del ejercicio). D9.3: requiere todos los asientos
        del ejercicio en CONFIRMADO."""
        service = CierreEjercicioService(info.context.session)
        asiento = await service.generar_asiento_regularizacion(ejercicio)
        return asiento.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CIERRE_EJECUTAR")])
    async def generar_asiento_cierre(
        self, info: strawberry.Info, ejercicio: int
    ) -> uuid.UUID:
        """A2 — Asiento de cierre: salda balance completo. D8.4: requiere
        conciliación bancaria completa del ejercicio."""
        service = CierreEjercicioService(info.context.session)
        asiento = await service.generar_asiento_cierre(ejercicio)
        return asiento.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CIERRE_EJECUTAR")])
    async def generar_asiento_apertura(
        self, info: strawberry.Info, ejercicio_nuevo: int
    ) -> uuid.UUID:
        """A3 — Apertura del ejercicio nuevo invirtiendo el cierre del anterior."""
        service = CierreEjercicioService(info.context.session)
        asiento = await service.generar_asiento_apertura(ejercicio_nuevo)
        return asiento.id

    # ── Cuentas Anuales (Flujo 10) ──────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CUENTAS_ANUALES_GENERAR")])
    async def generar_cuentas_anuales(
        self, info: strawberry.Info, ejercicio: int
    ) -> uuid.UUID:
        """A1 — Crea las CCAA del ejercicio en BORRADOR con snapshot del balance
        y la cuenta de resultados. Requiere ejercicio CERRADO (flujo 9)."""
        from app.modules.economico.services.cuentas_anuales_service import CuentasAnualesService
        service = CuentasAnualesService(info.context.session)
        ccaa = await service.generar(ejercicio)
        return ccaa.id

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CUENTAS_ANUALES_GENERAR")])
    async def actualizar_memoria_ccaa(
        self, info: strawberry.Info, ccaa_id: uuid.UUID, apartado: str, texto: str
    ) -> bool:
        """A2 — Edita un apartado de la Memoria. Solo en estado BORRADOR."""
        from app.modules.economico.services.cuentas_anuales_service import CuentasAnualesService
        service = CuentasAnualesService(info.context.session)
        await service.actualizar_memoria(ccaa_id, apartado, texto)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CUENTAS_ANUALES_APROBAR")])
    async def aprobar_cuentas_anuales(
        self,
        info: strawberry.Info,
        ccaa_id: uuid.UUID,
        aprobado_por_id: uuid.UUID,
        acta_referencia: str,
        fecha_aprobacion: Optional[date] = None,
    ) -> bool:
        """A3 — Aprobación por junta (BORRADOR → APROBADAS)."""
        from app.modules.economico.services.cuentas_anuales_service import CuentasAnualesService
        service = CuentasAnualesService(info.context.session)
        await service.aprobar(ccaa_id, aprobado_por_id, acta_referencia, fecha_aprobacion)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CUENTAS_ANUALES_DEPOSITAR")])
    async def marcar_ccaa_depositadas(
        self,
        info: strawberry.Info,
        ccaa_id: uuid.UUID,
        fecha_deposito: Optional[date] = None,
        archivo_acuse_recibo: Optional[str] = None,
    ) -> bool:
        """A4 — APROBADAS → DEPOSITADAS, registrando fecha y acuse de recibo."""
        from app.modules.economico.services.cuentas_anuales_service import CuentasAnualesService
        service = CuentasAnualesService(info.context.session)
        await service.marcar_depositadas(ccaa_id, fecha_deposito, archivo_acuse_recibo)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CUENTAS_ANUALES_GENERAR")])
    async def reabrir_cuentas_anuales(
        self, info: strawberry.Info, ccaa_id: uuid.UUID, motivo: str
    ) -> bool:
        """A6 — Vuelve a BORRADOR (excepcional). Se requiere motivo justificado."""
        from app.modules.economico.services.cuentas_anuales_service import CuentasAnualesService
        service = CuentasAnualesService(info.context.session)
        await service.reabrir(ccaa_id, motivo)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_CUENTAS_ANUALES_LISTAR")])
    async def exportar_ccaa_pdf(
        self, info: strawberry.Info, ccaa_id: uuid.UUID,
        organizacion_nombre: str = "Organización",
    ) -> str:
        """A5 — Genera el PDF de las CCAA y lo devuelve en base64 (D10.4)."""
        import base64
        from app.modules.economico.services.cuentas_anuales_service import (
            CuentasAnualesService, generar_pdf_ccaa,
        )
        service = CuentasAnualesService(info.context.session)
        ccaa = await service.obtener(ccaa_id)
        if not ccaa:
            raise ValueError(f"CCAA {ccaa_id} no encontradas")
        pdf_bytes = generar_pdf_ccaa(ccaa, organizacion_nombre)
        return base64.b64encode(pdf_bytes).decode("ascii")

    # ── Modelo 182 (Flujo 11) ───────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_MODELO182_GENERAR")])
    async def descargar_fichero_aeat_182(
        self,
        info: strawberry.Info,
        ejercicio: int,
        declarante_nif: str,
        declarante_nombre: str,
    ) -> str:
        """A2 — Genera el fichero AEAT (TXT 250 chars, ISO-8859-1) en base64."""
        import base64
        from app.modules.economico.services.modelo_182_service import Modelo182Service
        service = Modelo182Service(info.context.session)
        contenido = await service.generar_fichero_aeat(ejercicio, declarante_nif, declarante_nombre)
        return base64.b64encode(contenido).decode("ascii")

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_MODELO182_GENERAR")])
    async def descargar_pdf_resumen_182(
        self,
        info: strawberry.Info,
        ejercicio: int,
        organizacion_nombre: str = "Organización",
    ) -> str:
        """A3 — PDF resumen con donantes incluidos y excluidos. Base64."""
        import base64
        from app.modules.economico.services.modelo_182_service import Modelo182Service
        service = Modelo182Service(info.context.session)
        pdf = await service.generar_pdf_resumen(ejercicio, organizacion_nombre)
        return base64.b64encode(pdf).decode("ascii")

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_MODELO182_REGISTRAR")])
    async def registrar_presentacion_182(
        self,
        info: strawberry.Info,
        ejercicio: int,
        fecha_envio: date,
        codigo_aeat: Optional[str] = None,
        archivo_acuse: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> uuid.UUID:
        """A4 — Registra la presentación a la AEAT con su acuse (D11.4)."""
        from app.modules.economico.services.modelo_182_service import Modelo182Service
        service = Modelo182Service(info.context.session)
        pres = await service.registrar_presentacion(
            ejercicio=ejercicio,
            fecha_envio=fecha_envio,
            codigo_aeat=codigo_aeat,
            archivo_acuse=archivo_acuse,
            observaciones=observaciones,
        )
        return pres.id
