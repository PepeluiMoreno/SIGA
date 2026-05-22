"""Tests del servicio de tesorería."""
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.modules.economico.models.tesoreria import (
    CuentaBancaria, ApunteCaja, TipoApunte, ConciliacionBancaria
)
from app.modules.economico.services.tesoreria_service import TesoreriaService


@pytest.fixture
def mock_session():
    """Sesión SQLAlchemy simulada."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def service(mock_session):
    return TesoreriaService(mock_session)


# ─── Tests de cuentas bancarias ──────────────────────────────────────────────

class TestCuentaBancaria:
    async def test_crear_cuenta_bancaria_ok(self, service, mock_session):
        """Crear una cuenta bancaria nueva."""
        # IBAN no existente
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        cuenta = await service.crear_cuenta_bancaria(
            nombre="Cuenta principal",
            iban="ES7620770024003102575766",
            banco_nombre="CaixaBank",
        )

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()

    async def test_crear_cuenta_iban_duplicado_falla(self, service, mock_session):
        """Crear una cuenta con IBAN ya existente debe fallar."""
        cuenta_existente = MagicMock(spec=CuentaBancaria)
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = cuenta_existente
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="ya existe"):
            await service.crear_cuenta_bancaria(
                nombre="Cuenta duplicada",
                iban="ES7620770024003102575766",
            )

    async def test_listar_cuentas_activas_por_defecto(self, service, mock_session):
        """Listar cuentas debe devolver solo las activas por defecto."""
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        cuentas = await service.listar_cuentas_bancarias(activas_solo=True)
        assert isinstance(cuentas, list)


# ─── Tests de apuntes de caja ────────────────────────────────────────────────

class TestApunteCaja:
    async def _cuenta_activa(self, mock_session):
        cuenta = MagicMock(spec=CuentaBancaria)
        cuenta.id = uuid4()
        cuenta.activa = True
        cuenta.saldo_actual = Decimal('1000.00')
        mock_result_cuenta = AsyncMock()
        mock_result_cuenta.scalars.return_value.first.return_value = cuenta
        mock_session.execute = AsyncMock(return_value=mock_result_cuenta)
        return cuenta

    async def test_registrar_ingreso_actualiza_saldo(self, service, mock_session):
        """Registrar un ingreso debe incrementar el saldo."""
        cuenta = await self._cuenta_activa(mock_session)
        saldo_inicial = cuenta.saldo_actual

        await service.registrar_apunte(
            cuenta_id=cuenta.id,
            fecha=date.today(),
            importe=Decimal('500.00'),
            tipo=TipoApunte.INGRESO,
            concepto="Cuota socio",
        )

        assert cuenta.saldo_actual == saldo_inicial + Decimal('500.00')

    async def test_registrar_gasto_reduce_saldo(self, service, mock_session):
        """Registrar un gasto debe reducir el saldo."""
        cuenta = await self._cuenta_activa(mock_session)
        saldo_inicial = cuenta.saldo_actual

        await service.registrar_apunte(
            cuenta_id=cuenta.id,
            fecha=date.today(),
            importe=Decimal('200.00'),
            tipo=TipoApunte.GASTO,
            concepto="Compra material",
        )

        assert cuenta.saldo_actual == saldo_inicial - Decimal('200.00')

    async def test_importe_negativo_falla(self, service, mock_session):
        """Registrar importe negativo debe lanzar ValueError."""
        cuenta = await self._cuenta_activa(mock_session)

        with pytest.raises(ValueError):
            await service.registrar_apunte(
                cuenta_id=cuenta.id,
                fecha=date.today(),
                importe=Decimal('-100.00'),
                tipo=TipoApunte.INGRESO,
                concepto="Importe negativo",
            )

    async def test_cuenta_inactiva_falla(self, service, mock_session):
        """No se puede registrar en una cuenta inactiva."""
        cuenta = MagicMock(spec=CuentaBancaria)
        cuenta.activa = False
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = cuenta
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="inactiva"):
            await service.registrar_apunte(
                cuenta_id=cuenta.id,
                fecha=date.today(),
                importe=Decimal('100.00'),
                tipo=TipoApunte.INGRESO,
                concepto="Test",
            )

    async def test_marcar_apunte_conciliado(self, service, mock_session):
        """Marcar un apunte como conciliado actualiza el flag."""
        apunte = MagicMock(spec=ApunteCaja)
        apunte.conciliado = False
        mock_result = AsyncMock()
        mock_result.scalars.return_value.first.return_value = apunte
        mock_session.execute = AsyncMock(return_value=mock_result)

        await service.marcar_apunte_conciliado(uuid4(), date.today())

        assert apunte.conciliado is True
        mock_session.commit.assert_awaited_once()

    async def test_saldo_total_suma_cuentas_activas(self, service, mock_session):
        """obtener_saldo_total suma los saldos de cuentas activas."""
        mock_result = AsyncMock()
        mock_result.scalar.return_value = Decimal('2500.00')
        mock_session.execute = AsyncMock(return_value=mock_result)

        total = await service.obtener_saldo_total()
        assert total == Decimal('2500.00')
