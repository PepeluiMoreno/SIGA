"""Tests del puente de chat (ChatBridgeService).

Estrategia: sesión real sobre SQLite en memoria (datos y queries reales) y mock
SOLO del cliente ejabberd (lo externo, que aquí no existe). Así se prueba la
lógica de sincronización de verdad: derivación de miembros, registro de estado,
manejo de errores y reintento — los puntos que sostienen la fiabilidad pedida.

No requieren ejabberd real. Las verificaciones contra un ejabberd de verdad están
en docs/DISENO_CHAT_INTERNO.md §7 y son aparte.
"""
import datetime as dt
import uuid
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.schema import CreateTable

import app.modules  # registra todos los modelos / mappers
from app.core.database import Base
from app.modules.acceso.models.usuario import Usuario
from app.modules.membresia.models.miembro import Miembro
from app.modules.actividades.models.grupo import (
    GrupoTrabajo, MiembroGrupo, TipoGrupo, RolGrupo,
)
from app.modules.configuracion.models.configuracion import Configuracion
from app.modules.core.comunicacion.mensajeria.chat_bridge_service import ChatBridgeService
from app.modules.core.comunicacion.mensajeria.models import CanalChat, EstadoSync, OrigenCanal
from app.modules.core.comunicacion.mensajeria.ejabberd_client import EjabberdError


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
async def session():
    """Sesión SQLite en memoria con las tablas que compilan en SQLite."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    compat = []
    for t in Base.metadata.sorted_tables:
        try:
            str(CreateTable(t).compile(dialect=engine.dialect))
            compat.append(t)
        except Exception:
            pass
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=compat)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as s:
        yield s
    await engine.dispose()


@pytest.fixture
async def grupo_con_usuario(session):
    """Crea config de chat + un grupo con un usuario miembro. Devuelve (grupo, usuario)."""
    for k, v in [
        ("chat.ejabberd_api_url", "http://x/api"),
        ("chat.ejabberd_admin_token", "tok"),
        ("chat.xmpp_dominio", "siga.local"),
        ("chat.muc_servicio", "conference.siga.local"),
    ]:
        session.add(Configuracion(clave=k, valor=v))
    tg = TipoGrupo(id=uuid.uuid4(), nombre="T")
    rg = RolGrupo(id=uuid.uuid4(), nombre="R")
    session.add_all([tg, rg])
    await session.flush()
    hoy = dt.date.today()
    grupo = GrupoTrabajo(id=uuid.uuid4(), nombre="Grupo X", tipo_grupo_id=tg.id, activo=True)
    miembro = Miembro(id=uuid.uuid4(), nombre="Ana", apellido1="L", fecha_alta=hoy)
    usuario = Usuario(id=uuid.uuid4(), email="ana@siga.local", password_hash="x", miembro_id=miembro.id)
    session.add_all([grupo, miembro, usuario])
    await session.flush()
    session.add(MiembroGrupo(
        id=uuid.uuid4(), grupo_id=grupo.id, miembro_id=miembro.id, rol_grupo_id=rg.id,
        fecha_incorporacion=hoy, activo=True,
    ))
    await session.commit()
    return grupo, usuario


def _bridge_con_cliente(session, cliente):
    b = ChatBridgeService(session)
    b._client = cliente
    return b


# ── Camino feliz ─────────────────────────────────────────────────────────────

class TestCreacionCanal:
    async def test_crea_canal_con_jid_correcto(self, session, grupo_con_usuario):
        grupo, _ = grupo_con_usuario
        bridge = _bridge_con_cliente(session, AsyncMock())
        canal = await bridge.asegurar_canal_grupo(grupo)
        assert canal.origen == OrigenCanal.GRUPO_TRABAJO
        assert canal.origen_id == grupo.id
        assert canal.sala_jid == f"grupo-{grupo.id}@conference.siga.local"
        assert canal.estado_sync == EstadoSync.OK

    async def test_idempotente(self, session, grupo_con_usuario):
        grupo, _ = grupo_con_usuario
        bridge = _bridge_con_cliente(session, AsyncMock())
        c1 = await bridge.asegurar_canal_grupo(grupo)
        c2 = await bridge.asegurar_canal_grupo(grupo)
        assert c1.id == c2.id

    async def test_sincroniza_miembro_por_email(self, session, grupo_con_usuario):
        grupo, _ = grupo_con_usuario
        fake = AsyncMock()
        bridge = _bridge_con_cliente(session, fake)
        await bridge.asegurar_canal_grupo(grupo)
        await bridge.sincronizar_membresia_grupo(grupo.id)
        llamadas = [c.args for c in fake.set_afiliacion.await_args_list]
        assert any("ana@siga.local" in a and "member" in a for a in llamadas)


# ── Manejo de errores (fiabilidad) ───────────────────────────────────────────

class TestErrores:
    async def test_fallo_al_crear_sala_deja_estado_error(self, session, grupo_con_usuario):
        grupo, _ = grupo_con_usuario
        fake = AsyncMock()
        fake.crear_sala.side_effect = EjabberdError("ejabberd caído")
        bridge = _bridge_con_cliente(session, fake)
        canal = await bridge.asegurar_canal_grupo(grupo)
        # El canal se crea en SIGA igualmente, pero queda marcado ERROR para reintentar.
        assert canal.estado_sync == EstadoSync.ERROR
        assert canal.ultimo_error and "caído" in canal.ultimo_error

    async def test_fallo_en_sincronizacion_deja_estado_error(self, session, grupo_con_usuario):
        grupo, _ = grupo_con_usuario
        fake = AsyncMock()
        bridge = _bridge_con_cliente(session, fake)
        await bridge.asegurar_canal_grupo(grupo)        # OK
        fake.set_afiliacion.side_effect = EjabberdError("timeout")
        await bridge.sincronizar_membresia_grupo(grupo.id)
        canal = await bridge._canal_de(OrigenCanal.GRUPO_TRABAJO, grupo.id)
        assert canal.estado_sync == EstadoSync.ERROR

    async def test_reintento_recupera_estado_ok(self, session, grupo_con_usuario):
        grupo, _ = grupo_con_usuario
        fake = AsyncMock()
        fake.crear_sala.side_effect = EjabberdError("caído")
        bridge = _bridge_con_cliente(session, fake)
        canal = await bridge.asegurar_canal_grupo(grupo)
        assert canal.estado_sync == EstadoSync.ERROR
        # ejabberd vuelve: el reintento debe dejar OK.
        fake.crear_sala.side_effect = None
        fake.set_afiliacion.side_effect = None
        canal2 = await bridge.reintentar_sync(canal.id)
        assert canal2 is not None
        assert canal2.estado_sync == EstadoSync.OK


# ── Bajas y consulta ─────────────────────────────────────────────────────────

class TestMembresiaYConsulta:
    async def test_quitar_miembro_pide_afiliacion_none(self, session, grupo_con_usuario):
        grupo, usuario = grupo_con_usuario
        fake = AsyncMock()
        bridge = _bridge_con_cliente(session, fake)
        await bridge.asegurar_canal_grupo(grupo)
        await bridge.quitar_miembro(grupo.id, usuario)
        llamadas = [c.args for c in fake.set_afiliacion.await_args_list]
        assert any("ana@siga.local" in a and "none" in a for a in llamadas)

    async def test_mis_canales_devuelve_los_del_usuario(self, session, grupo_con_usuario):
        grupo, usuario = grupo_con_usuario
        bridge = _bridge_con_cliente(session, AsyncMock())
        await bridge.asegurar_canal_grupo(grupo)
        canales = await bridge.mis_canales(usuario)
        assert len(canales) == 1
        assert canales[0].origen_id == grupo.id

    async def test_archivar_marca_fecha(self, session, grupo_con_usuario):
        grupo, _ = grupo_con_usuario
        bridge = _bridge_con_cliente(session, AsyncMock())
        await bridge.asegurar_canal_grupo(grupo)
        await bridge.archivar_canal_grupo(grupo.id)
        canal = await bridge._canal_de(OrigenCanal.GRUPO_TRABAJO, grupo.id)
        assert canal.fecha_archivado is not None
