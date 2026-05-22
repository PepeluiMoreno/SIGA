"""Tests del servicio de contabilidad."""
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.modules.economico.models.contabilidad import (
    CuentaContable, AsientoContable, ApunteContable,
    TipoCuentaContable, EstadoAsientoContable, TipoAsientoContable,
)
from app.modules.economico.services.contabilidad_service import ContabilidadService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def service(mock_session):
    return ContabilidadService(mock_session)


class TestPlanCuentas:
    async def test_crear_cuenta_codigo_unico(self, service, mock_session):
        """No se puede crear dos cuentas con el mismo código."""
        cuenta_existente = MagicMock(spec=CuentaContable)
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = cuenta_existente
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="ya existe"):
            await service.crear_cuenta_contable(
                codigo="572",
                nombre="Bancos",
                tipo=TipoCuentaContable.ACTIVO,
                nivel=3,
            )

    async def test_crear_cuenta_ok(self, service, mock_session):
        """Crear una cuenta nueva."""
        mock_result_vacio = AsyncMock()
        mock_result_vacio.scalars.return_value.first.return_value = None
        mock_result_max = AsyncMock()
        mock_result_max.scalar.return_value = None
        mock_session.execute = AsyncMock(side_effect=[mock_result_vacio])

        await service.crear_cuenta_contable(
            codigo="572",
            nombre="Bancos e instituciones de crédito",
            tipo=TipoCuentaContable.ACTIVO,
            nivel=3,
        )
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()


class TestAsientos:
    def _asiento_con_apuntes(self, cuadrado: bool = True):
        """Helper: asiento en BORRADOR con apuntes cuadrados o no."""
        asiento = MagicMock(spec=AsientoContable)
        asiento.estado = EstadoAsientoContable.BORRADOR
        asiento.esta_cuadrado = cuadrado

        if cuadrado:
            def confirmar():
                asiento.estado = EstadoAsientoContable.CONFIRMADO
            asiento.confirmar.side_effect = confirmar
        else:
            asiento.confirmar.side_effect = ValueError("El asiento no cuadra")

        return asiento

    async def test_confirmar_asiento_cuadrado_ok(self, service, mock_session):
        """Confirmar un asiento cuadrado cambia su estado a CONFIRMADO."""
        asiento = self._asiento_con_apuntes(cuadrado=True)
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = asiento
        mock_session.execute = AsyncMock(return_value=mock_result)

        await service.confirmar_asiento(uuid4())

        assert asiento.estado == EstadoAsientoContable.CONFIRMADO

    async def test_confirmar_asiento_no_cuadrado_falla(self, service, mock_session):
        """Confirmar un asiento que no cuadra debe lanzar ValueError."""
        asiento = self._asiento_con_apuntes(cuadrado=False)
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = asiento
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError):
            await service.confirmar_asiento(uuid4())

    async def test_anular_asiento_cambia_estado(self, service, mock_session):
        """Anular un asiento lo marca como ANULADO."""
        asiento = MagicMock(spec=AsientoContable)
        asiento.estado = EstadoAsientoContable.CONFIRMADO

        def anular():
            asiento.estado = EstadoAsientoContable.ANULADO
        asiento.anular.side_effect = anular

        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = asiento
        mock_session.execute = AsyncMock(return_value=mock_result)

        await service.anular_asiento(uuid4())

        assert asiento.estado == EstadoAsientoContable.ANULADO

    async def test_añadir_apunte_a_asiento_confirmado_falla(self, service, mock_session):
        """No se pueden añadir apuntes a un asiento ya confirmado."""
        asiento = MagicMock(spec=AsientoContable)
        asiento.estado = EstadoAsientoContable.CONFIRMADO

        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = asiento
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="BORRADOR"):
            await service.añadir_apunte(
                asiento_id=uuid4(),
                cuenta_id=uuid4(),
                debe=Decimal('100.00'),
            )

    async def test_apunte_con_debe_y_haber_falla(self, service, mock_session):
        """Un apunte no puede tener debe y haber a la vez."""
        asiento = MagicMock(spec=AsientoContable)
        asiento.estado = EstadoAsientoContable.BORRADOR
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = asiento
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="simultáneamente"):
            await service.añadir_apunte(
                asiento_id=uuid4(),
                cuenta_id=uuid4(),
                debe=Decimal('100.00'),
                haber=Decimal('50.00'),
            )

    async def test_siguiente_numero_asiento(self, service, mock_session):
        """El siguiente número de asiento incrementa el máximo existente."""
        mock_result = AsyncMock()
        mock_result.scalar.return_value = 42
        mock_session.execute = AsyncMock(return_value=mock_result)

        numero = await service.siguiente_numero_asiento(2026)
        assert numero == 43

    async def test_siguiente_numero_asiento_primer_asiento(self, service, mock_session):
        """Si no hay asientos en el ejercicio, el primer número es 1."""
        mock_result = AsyncMock()
        mock_result.scalar.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        numero = await service.siguiente_numero_asiento(2026)
        assert numero == 1
