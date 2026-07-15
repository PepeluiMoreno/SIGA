"""Ejecución de acuerdos: el acuerdo produce sus efectos.

Este es el eslabón que da sentido a la gobernanza: **un nombramiento no nace de un
botón, nace de un acuerdo de un órgano, reflejado en un acta**.

Cadena completa (ver GOBERNANZA.md):

    Órgano se reúne → adopta un Acuerdo (APROBADO, con su payload)
        → se ejecuta → produce el Mandato (HistorialNombramiento)
            → deriva los UsuarioRol vía CargoRol, heredando el territorio

La trazabilidad queda cerrada por ambos extremos: el mandato apunta al acuerdo que
lo originó (`origen_id`), y el acuerdo apunta al mandato que produjo
(`AcuerdoNombramiento.nombramiento_id`, que además impide ejecutarlo dos veces).
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.reunion import (
    Acuerdo, AcuerdoNombramiento, AcuerdoPresupuestoCampania, PuntoOrdenDia, Reunion,
)
from ..models.acta import Acta
from ...acceso.models.cargo import CargoRol
from ...acceso.models.usuario import Usuario, UsuarioRol
from ...membresia.models.historial_nombramiento import HistorialNombramiento
from ...economico.services.reserva_service import ReservaService, ResultadoReserva

# `tipo_origen` del mandato: de dónde salió. Aquí, de un acuerdo de un órgano.
ORIGEN_ACUERDO = 'ACUERDO'


class AcuerdoEjecucionService:
    """Convierte acuerdos aprobados en hechos."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ejecutar_nombramiento(
        self,
        acuerdo_id: uuid.UUID,
        *,
        ejecutado_por_id: Optional[uuid.UUID] = None,
        exigir_acta_aprobada: bool = True,
    ) -> HistorialNombramiento:
        """Ejecuta un acuerdo de NOMBRAMIENTO: produce el mandato y deriva los roles.

        Validaciones (un acuerdo solo produce efectos si es válido):
          - el acuerdo existe y tiene payload de nombramiento;
          - fue APROBADO (un acuerdo rechazado no nombra a nadie);
          - su acta está aprobada (el acuerdo consta formalmente), salvo que se
            releve explícitamente;
          - no se ha ejecutado ya (idempotencia: no se nombra dos veces).
        """
        acuerdo = (await self.session.execute(
            select(Acuerdo).where(
                Acuerdo.id == acuerdo_id,
                Acuerdo.eliminado == False,  # noqa: E712
            )
        )).scalar_one_or_none()
        if acuerdo is None:
            raise ValueError("Acuerdo no encontrado")

        payload: Optional[AcuerdoNombramiento] = acuerdo.nombramiento
        if payload is None:
            raise ValueError(
                "El acuerdo no lleva datos de nombramiento (a quién, para qué cargo). "
                "Solo los acuerdos de tipo NOMBRAMIENTO/CESE se pueden ejecutar así."
            )

        if not acuerdo.es_aprobado:
            raise ValueError(
                f"El acuerdo no está aprobado (resultado: {acuerdo.resultado or '—'}). "
                "Un acuerdo no aprobado no produce efectos."
            )

        if payload.ya_ejecutado:
            raise ValueError("Este acuerdo ya se ejecutó: el nombramiento existe.")

        if exigir_acta_aprobada:
            await self._exigir_acta_aprobada(acuerdo)

        # ── El mandato ────────────────────────────────────────────────────────
        # Trazabilidad: queda escrito de qué acuerdo salió. Ahora se puede
        # responder «¿en qué acta consta que Fulano es tesorero?».
        mandato = HistorialNombramiento(
            miembro_id=payload.miembro_id,
            cargo_id=payload.cargo_id,          # cargo, NO rol (el rol se deriva)
            agrupacion_id=payload.agrupacion_id,
            fecha_inicio=payload.fecha_inicio,
            fecha_fin=payload.fecha_fin,
            estado='ACTIVO',
            aprobado_por_id=ejecutado_por_id,
            fecha_aprobacion=date.today(),
            tipo_origen=ORIGEN_ACUERDO,
            origen_id=acuerdo.id,
            motivo=f"Acuerdo nº {acuerdo.numero}",
        )
        self.session.add(mandato)
        await self.session.flush()   # necesitamos mandato.id

        # Cierra el círculo por el otro extremo (y bloquea una segunda ejecución).
        payload.nombramiento_id = mandato.id

        # ── Los roles se DERIVAN del cargo, no se asignan a mano ──────────────
        await self._derivar_roles(mandato, payload)

        return mandato

    async def ejecutar_cese(
        self,
        acuerdo_id: uuid.UUID,
        *,
        ejecutado_por_id: Optional[uuid.UUID] = None,
        exigir_acta_aprobada: bool = True,
    ) -> HistorialNombramiento:
        """Ejecuta un acuerdo de CESE: cierra el mandato y retira los roles derivados.

        Simétrico del nombramiento. El cese no borra el mandato —es historia, y debe
        constar— sino que lo **finaliza**: le pone `fecha_fin`, lo pasa a FINALIZADO
        y desactiva los `UsuarioRol` que derivaban de él (los permisos se van con el
        cargo, que es justo el sentido de derivarlos).

        El payload (`AcuerdoNombramiento`) identifica a quién se cesa y de qué cargo;
        se busca su mandato vigente.
        """
        acuerdo = (await self.session.execute(
            select(Acuerdo).where(
                Acuerdo.id == acuerdo_id,
                Acuerdo.eliminado == False,  # noqa: E712
            )
        )).scalar_one_or_none()
        if acuerdo is None:
            raise ValueError("Acuerdo no encontrado")

        payload: Optional[AcuerdoNombramiento] = acuerdo.nombramiento
        if payload is None:
            raise ValueError(
                "El acuerdo no lleva datos de cese (a quién se cesa, de qué cargo)."
            )
        if not acuerdo.es_aprobado:
            raise ValueError(
                f"El acuerdo no está aprobado (resultado: {acuerdo.resultado or '—'}). "
                "Un acuerdo no aprobado no produce efectos."
            )
        if payload.ya_ejecutado:
            raise ValueError("Este acuerdo ya se ejecutó.")
        if exigir_acta_aprobada:
            await self._exigir_acta_aprobada(acuerdo)

        # El mandato vigente de esa persona en ese cargo (y territorio).
        mandato = (await self.session.execute(
            select(HistorialNombramiento).where(
                HistorialNombramiento.miembro_id == payload.miembro_id,
                HistorialNombramiento.cargo_id == payload.cargo_id,
                HistorialNombramiento.agrupacion_id == payload.agrupacion_id,
                HistorialNombramiento.estado == 'ACTIVO',
                HistorialNombramiento.fecha_fin.is_(None),
                HistorialNombramiento.eliminado == False,  # noqa: E712
            )
        )).scalar_one_or_none()
        if mandato is None:
            raise ValueError(
                "No hay un mandato vigente de esa persona en ese cargo: nada que cesar."
            )

        # Cerrar el mandato. No se borra: es historia y debe constar.
        # Fecha de efecto del cese: `fecha_fin` si se indicó; si no, la `fecha_inicio`
        # del payload (en un acuerdo de CESE, esa fecha ES la de efecto); si tampoco,
        # hoy.
        mandato.fecha_fin = payload.fecha_fin or payload.fecha_inicio or date.today()
        mandato.estado = 'FINALIZADO'
        mandato.observaciones = (
            f"{mandato.observaciones + ' | ' if mandato.observaciones else ''}"
            f"Cesado por acuerdo nº {acuerdo.numero}"
        )

        # Retirar los roles que derivaban de ese mandato: el permiso se va con el cargo.
        roles_derivados = (await self.session.execute(
            select(UsuarioRol).where(
                UsuarioRol.nombramiento_id == mandato.id,
                UsuarioRol.activo == True,  # noqa: E712
            )
        )).scalars().all()
        for ur in roles_derivados:
            ur.activo = False

        payload.nombramiento_id = mandato.id   # traza qué mandato cerró (e impide repetir)
        return mandato

    async def ejecutar_aprobacion_presupuesto(
        self,
        acuerdo_id: uuid.UUID,
        *,
        ejecutado_por_id: Optional[uuid.UUID] = None,
        exigir_acta_aprobada: bool = True,
    ) -> ResultadoReserva:
        """Ejecuta un acuerdo de APROBACION_PRESUPUESTO: reserva fondos y aprueba la campaña.

        Mismas garantías que un nombramiento (el patrón de esta casa): el acuerdo debe
        existir con su payload, estar APROBADO, constar en acta aprobada y no haberse
        ejecutado ya. Al ejecutarse:
          - crea un `CompromisoPresupuestario` contra la partida anual (la reserva);
          - marca la campaña como aprobada (estado PROGRAMADA + auditoría);
          - cierra el círculo escribiendo `compromiso_id` en el payload (idempotencia).

        Sobregiro: si el importe excede el disponible de la partida, se reserva igualmente
        y el resultado lo indica (`sobregiro=True`) — política «avisa, no bloquea».
        """
        acuerdo = (await self.session.execute(
            select(Acuerdo).where(
                Acuerdo.id == acuerdo_id,
                Acuerdo.eliminado == False,  # noqa: E712
            )
        )).scalar_one_or_none()
        if acuerdo is None:
            raise ValueError("Acuerdo no encontrado")

        payload: Optional[AcuerdoPresupuestoCampania] = acuerdo.presupuesto_campania
        if payload is None:
            raise ValueError(
                "El acuerdo no lleva datos de presupuesto (campaña, importe, partida). "
                "Solo los acuerdos de tipo APROBACION_PRESUPUESTO se ejecutan así."
            )

        if not acuerdo.es_aprobado:
            raise ValueError(
                f"El acuerdo no está aprobado (resultado: {acuerdo.resultado or '—'}). "
                "Un acuerdo no aprobado no reserva fondos."
            )

        if payload.ya_ejecutado:
            raise ValueError("Este acuerdo ya se ejecutó: la reserva existe.")

        if exigir_acta_aprobada:
            await self._exigir_acta_aprobada(acuerdo)

        # ── La reserva ────────────────────────────────────────────────────────
        resultado = await ReservaService(self.session).reservar(
            partida_id=payload.partida_id,
            importe=payload.importe,
            campania_id=payload.campania_id,
            concepto=f"Presupuesto de campaña — acuerdo nº {acuerdo.numero}",
        )

        # Cierra el círculo (y bloquea una segunda ejecución).
        payload.compromiso_id = resultado.compromiso.id

        # ── La campaña queda aprobada ─────────────────────────────────────────
        await self._aprobar_campania(payload.campania_id, ejecutado_por_id)

        return resultado

    async def _aprobar_campania(
        self, campania_id: uuid.UUID, aprobado_por_id: Optional[uuid.UUID]
    ) -> None:
        """Marca la campaña como aprobada (estado PROGRAMADA + auditoría), en la misma
        transacción del acuerdo (no usa CampaniaService.aprobar, que comitea aparte)."""
        from ...actividades.models.campana import Campania
        from ...configuracion.models.estados import EstadoCampania

        campania = (await self.session.execute(
            select(Campania).where(Campania.id == campania_id)
        )).scalar_one_or_none()
        if campania is None:
            raise ValueError("La campaña del acuerdo no existe.")

        estado = (await self.session.execute(
            select(EstadoCampania).where(EstadoCampania.codigo == "PROGRAMADA")
        )).scalar_one_or_none()
        if estado is not None:
            campania.estado_id = estado.id
        campania.aprobado_por_id = aprobado_por_id
        campania.fecha_aprobacion = date.today()
        await self.session.flush()

    async def _exigir_acta_aprobada(self, acuerdo: Acuerdo) -> None:
        """Un acuerdo solo es ejecutable si consta en un acta aprobada."""
        reunion_id = (await self.session.execute(
            select(PuntoOrdenDia.reunion_id).where(PuntoOrdenDia.id == acuerdo.punto_orden_dia_id)
        )).scalar_one_or_none()
        if reunion_id is None:
            raise ValueError("El acuerdo no está ligado a ninguna reunión")

        acta = (await self.session.execute(
            select(Acta).where(
                Acta.reunion_id == reunion_id,
                Acta.eliminado == False,  # noqa: E712
            )
        )).scalar_one_or_none()

        if acta is None:
            raise ValueError(
                "La reunión no tiene acta. El acuerdo debe constar en un acta aprobada "
                "antes de producir efectos."
            )
        if acta.estado_codigo not in ('APROBADA', 'FIRMADA'):
            raise ValueError(
                f"El acta está en estado {acta.estado_codigo}: debe estar APROBADA "
                "para que sus acuerdos surtan efecto."
            )

    async def _derivar_roles(
        self,
        mandato: HistorialNombramiento,
        payload: AcuerdoNombramiento,
    ) -> None:
        """Crea los `UsuarioRol` que el cargo confiere, heredando el territorio.

        Regla de oro (GOBERNANZA.md): los roles NO se asignan a una cuenta a mano;
        se derivan del cargo vía `CargoRol`, y heredan el `agrupacion_id` del mandato
        (que restringe el permiso a ese subárbol territorial).

        Si la persona no tiene cuenta de usuario, no hay roles que derivar: el mandato
        existe igual (es un hecho de gobierno, no de acceso).
        """
        usuario = (await self.session.execute(
            select(Usuario).where(
                Usuario.contacto_id == payload.miembro_id,
                Usuario.eliminado == False,  # noqa: E712
            )
        )).scalar_one_or_none()
        if usuario is None:
            return   # sin cuenta, no hay acceso que conceder

        roles_del_cargo = (await self.session.execute(
            select(CargoRol).where(
                CargoRol.cargo_id == payload.cargo_id,
                CargoRol.eliminado == False,  # noqa: E712
            )
        )).scalars().all()

        for cr in roles_del_cargo:
            ya = (await self.session.execute(
                select(UsuarioRol).where(
                    UsuarioRol.usuario_id == usuario.id,
                    UsuarioRol.rol_id == cr.rol_id,
                    UsuarioRol.nombramiento_id == mandato.id,
                )
            )).scalar_one_or_none()
            if ya is not None:
                continue
            self.session.add(UsuarioRol(
                usuario_id=usuario.id,
                rol_id=cr.rol_id,
                agrupacion_id=mandato.agrupacion_id,   # el territorio se hereda
                nombramiento_id=mandato.id,            # trazabilidad del permiso
                activo=True,
            ))
