from sqlalchemy.orm import Session
import uuid

from models import (
    ProveedorPago,
    TipoPago,
    EstadoPago,
    EstadoSuscripcion,
    TipoEventoPago,
)

def seed_cobro(session: Session):

    # -------------------------
    # PROVEEDORES
    # -------------------------
    paypal = ProveedorPago(
        id=uuid.uuid4(),
        codigo="PAYPAL",
        nombre="PayPal",
        activo=True,
    )

    bizum = ProveedorPago(
        id=uuid.uuid4(),
        codigo="BIZUM",
        nombre="Bizum",
        activo=True,
    )

    session.add_all([paypal, bizum])

    # -------------------------
    # TIPOS PAGO
    # -------------------------
    donacion = TipoPago(
        id=uuid.uuid4(),
        codigo="DONACION",
        descripcion="Pago puntual sin compromiso",
    )

    suscripcion = TipoPago(
        id=uuid.uuid4(),
        codigo="SUSCRIPCION",
        descripcion="Cuota periódica",
    )

    session.add_all([donacion, suscripcion])

    # -------------------------
    # ESTADOS PAGO
    # -------------------------
    estados_pago = [
        EstadoPago(id=uuid.uuid4(), codigo="CREADO", es_final=False),
        EstadoPago(id=uuid.uuid4(), codigo="PENDIENTE", es_final=False),
        EstadoPago(id=uuid.uuid4(), codigo="COMPLETADO", es_final=True),
        EstadoPago(id=uuid.uuid4(), codigo="FALLIDO", es_final=True),
        EstadoPago(id=uuid.uuid4(), codigo="REEMBOLSADO", es_final=True),
    ]

    session.add_all(estados_pago)

    # -------------------------
    # ESTADOS SUSCRIPCION
    # -------------------------
    estados_suscripcion = [
        EstadoSuscripcion(id=uuid.uuid4(), codigo="ACTIVA", es_final=False),
        EstadoSuscripcion(id=uuid.uuid4(), codigo="CANCELADA", es_final=True),
        EstadoSuscripcion(id=uuid.uuid4(), codigo="EXPIRADA", es_final=True),
    ]

    session.add_all(estados_suscripcion)

    # -------------------------
    # TIPOS EVENTO
    # -------------------------
    eventos = [
        TipoEventoPago(id=uuid.uuid4(), codigo="WEBHOOK"),
        TipoEventoPago(id=uuid.uuid4(), codigo="SISTEMA"),
        TipoEventoPago(id=uuid.uuid4(), codigo="REINTENTO"),
    ]

    session.add_all(eventos)

    session.commit()