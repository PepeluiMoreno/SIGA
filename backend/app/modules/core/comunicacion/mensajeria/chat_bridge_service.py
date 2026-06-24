"""Servicio puente entre SIGA y ejabberd (mensajería interna).

Responsabilidad: mantener la sala XMPP de un grupo de trabajo sincronizada con su
membresía en SIGA. Es la pieza que aporta el valor (vínculo automático). NO
almacena mensajes; solo el vínculo (`CanalChat`) y la propagación a ejabberd.

Reglas:
  - La membresía del canal SE DERIVA de SIGA, no se gestiona a mano.
  - El JID del usuario es su email (el UUID es PK interna y no se usa como id externo).
  - Toda operación contra ejabberd registra estado_sync en CanalChat para reintento.

Pendiente de verificación (ver docs/DISENO_CHAT_INTERNO.md §7): comandos exactos de
la API de ejabberd y emisión de token de login del usuario.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.acceso.models.usuario import Usuario
from app.modules.actividades.models.grupo import GrupoTrabajo, MiembroGrupo
from .models import CanalChat, OrigenCanal, EstadoSync
from .ejabberd_client import EjabberdClient, EjabberdConfig, EjabberdError

logger = logging.getLogger(__name__)


class ChatDesactivado(Exception):
    """El módulo de chat no está activado (feature flag chat.activo apagado)."""

# Claves de configuración de SIGA (Parámetros Generales) para el chat.
_CFG_KEYS = {
    "activo": "chat.activo",
    "api_url": "chat.ejabberd_api_url",
    "admin_token": "chat.ejabberd_admin_token",
    "dominio": "chat.xmpp_dominio",
    "muc_servicio": "chat.muc_servicio",
}


class ChatBridgeService:
    """Sincroniza grupos de trabajo de SIGA con salas MUC de ejabberd."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._client: Optional[EjabberdClient] = None

    # ── Configuración / cliente ──────────────────────────────────────────

    async def chat_activo(self) -> bool:
        """Feature flag: el módulo de chat solo opera si chat.activo es verdadero.

        Si está desactivado, el módulo queda inerte: no crea canales ni habla con
        ejabberd. La clave vive en la tabla de configuración de SIGA.
        """
        from app.modules.configuracion.models.configuracion import Configuracion
        r = await self.session.execute(
            select(Configuracion).where(Configuracion.clave == _CFG_KEYS["activo"])
        )
        cfg = r.scalar_one_or_none()
        if cfg is None or cfg.valor is None:
            return False
        return str(cfg.valor).strip().lower() in ("1", "true", "si", "sí", "on")

    async def _cargar_config(self) -> EjabberdConfig:
        from app.modules.configuracion.models.configuracion import Configuracion
        r = await self.session.execute(
            select(Configuracion).where(Configuracion.clave.in_(list(_CFG_KEYS.values())))
        )
        valores = {c.clave: (c.valor or "") for c in r.scalars().all()}
        return EjabberdConfig(
            api_url=valores.get(_CFG_KEYS["api_url"], ""),
            admin_token=valores.get(_CFG_KEYS["admin_token"], ""),
            dominio=valores.get(_CFG_KEYS["dominio"], ""),
            muc_servicio=valores.get(_CFG_KEYS["muc_servicio"], ""),
        )

    async def _get_client(self) -> EjabberdClient:
        if self._client is None:
            self._client = EjabberdClient(await self._cargar_config())
        return self._client

    # ── Derivaciones ─────────────────────────────────────────────────────

    @staticmethod
    def _nombre_sala_grupo(grupo_id: uuid.UUID) -> str:
        """Parte local del JID de la sala. Estable y opaca."""
        return f"grupo-{grupo_id}"

    @staticmethod
    def _nombre_sala_unidad(unidad_id: uuid.UUID) -> str:
        """Parte local del JID de la sala de una unidad organizativa."""
        return f"unidad-{unidad_id}"

    def _jid_usuario(self, usuario: Usuario, dominio: str) -> Optional[str]:
        """JID del usuario = su email. El UUID no se usa como id externo."""
        if not usuario.email:
            return None
        return f"{usuario.email}"  # email ya es 'local@dominio'; ejabberd usa el JID completo

    async def _usuarios_del_grupo(self, grupo_id: uuid.UUID) -> list[Usuario]:
        """Usuarios activos cuyos miembros pertenecen (activos) al grupo."""
        r = await self.session.execute(
            select(Usuario)
            .join(MiembroGrupo, MiembroGrupo.miembro_id == Usuario.contacto_id)
            .where(
                MiembroGrupo.grupo_id == grupo_id,
                MiembroGrupo.activo == True,        # noqa: E712
                MiembroGrupo.eliminado == False,    # noqa: E712
                Usuario.activo == True,             # noqa: E712
                Usuario.eliminado == False,         # noqa: E712
            )
        )
        return list(r.scalars().all())

    async def _usuarios_cargo_unidad(self, unidad_id: uuid.UUID) -> list[Usuario]:
        """Usuarios que ocupan ALGÚN cargo vigente en la unidad organizativa.

        El canal de una unidad es para cargos/responsables (no para todos los
        miembros, que pueden ser cientos). Fuente: vista v_nombramientos_vigentes
        (la misma que usa el DestinatarioResolver), filtrada por la agrupación.
        """
        from app.modules.membresia.models.nombramiento_vigente import NombramientoVigente
        sub = (
            select(NombramientoVigente.miembro_id)
            .where(NombramientoVigente.agrupacion_id == unidad_id)
        )
        r = await self.session.execute(
            select(Usuario).where(
                Usuario.contacto_id.in_(sub),
                Usuario.activo == True,        # noqa: E712
                Usuario.eliminado == False,    # noqa: E712
            )
        )
        return list(r.scalars().all())

    # ── API del puente ───────────────────────────────────────────────────

    async def asegurar_canal_grupo(self, grupo: GrupoTrabajo) -> CanalChat:
        """Crea (si no existe) el vínculo CanalChat para un grupo y su sala MUC.

        Idempotente: si ya existe el CanalChat, lo devuelve. La creación de la sala
        en ejabberd se intenta y el resultado queda en estado_sync.
        """
        existente = await self._canal_de(OrigenCanal.GRUPO_TRABAJO, grupo.id)
        if existente is not None:
            return existente
        if not await self.chat_activo():
            raise ChatDesactivado()

        cfg = await self._cargar_config()
        nombre_sala = self._nombre_sala_grupo(grupo.id)
        jid = f"{nombre_sala}@{cfg.muc_servicio}" if cfg.muc_servicio else nombre_sala

        canal = CanalChat(
            id=uuid.uuid4(),
            origen=OrigenCanal.GRUPO_TRABAJO,
            origen_id=grupo.id,
            sala_jid=jid,
            nombre=grupo.nombre,
            estado_sync=EstadoSync.PENDIENTE,
        )
        self.session.add(canal)
        await self.session.commit()
        await self.session.refresh(canal)

        await self._crear_sala_remota(canal, nombre_sala)
        return canal

    async def sincronizar_membresia_grupo(self, grupo_id: uuid.UUID) -> None:
        """Propaga a ejabberd la membresía actual del grupo (altas y bajas).

        Da de alta (afiliación 'member') a los usuarios actuales del grupo. Las
        bajas se gestionan en `quitar_miembro`. Este método reconcilia el alta.
        """
        canal = await self._canal_de(OrigenCanal.GRUPO_TRABAJO, grupo_id)
        if canal is None:
            logger.warning("sincronizar_membresia_grupo: no hay canal para grupo %s", grupo_id)
            return
        cfg = await self._cargar_config()
        nombre_sala = self._nombre_sala_grupo(grupo_id)
        usuarios = await self._usuarios_del_grupo(grupo_id)

        try:
            client = await self._get_client()
            for u in usuarios:
                jid = self._jid_usuario(u, cfg.dominio)
                if jid:
                    await client.set_afiliacion(nombre_sala, jid, "member")
            await self._marcar_sync(canal, EstadoSync.OK)
        except EjabberdError as exc:
            await self._marcar_sync(canal, EstadoSync.ERROR, str(exc))

    async def asegurar_canal_unidad(
        self, unidad_id: uuid.UUID, nombre: Optional[str] = None
    ) -> CanalChat:
        """Crea (si no existe) el canal de una unidad organizativa y su sala MUC.

        El canal es para los cargos/responsables de la unidad. Idempotente.
        """
        existente = await self._canal_de(OrigenCanal.UNIDAD_ORGANIZATIVA, unidad_id)
        if existente is not None:
            return existente
        if not await self.chat_activo():
            raise ChatDesactivado()

        cfg = await self._cargar_config()
        nombre_sala = self._nombre_sala_unidad(unidad_id)
        jid = f"{nombre_sala}@{cfg.muc_servicio}" if cfg.muc_servicio else nombre_sala

        canal = CanalChat(
            id=uuid.uuid4(),
            origen=OrigenCanal.UNIDAD_ORGANIZATIVA,
            origen_id=unidad_id,
            sala_jid=jid,
            nombre=nombre,
            estado_sync=EstadoSync.PENDIENTE,
        )
        self.session.add(canal)
        await self.session.commit()
        await self.session.refresh(canal)

        await self._crear_sala_remota(canal, nombre_sala)
        return canal

    async def sincronizar_membresia_unidad(self, unidad_id: uuid.UUID) -> None:
        """Propaga a ejabberd los cargos vigentes de la unidad como miembros del canal."""
        canal = await self._canal_de(OrigenCanal.UNIDAD_ORGANIZATIVA, unidad_id)
        if canal is None:
            logger.warning("sincronizar_membresia_unidad: no hay canal para unidad %s", unidad_id)
            return
        cfg = await self._cargar_config()
        nombre_sala = self._nombre_sala_unidad(unidad_id)
        usuarios = await self._usuarios_cargo_unidad(unidad_id)

        try:
            client = await self._get_client()
            for u in usuarios:
                jid = self._jid_usuario(u, cfg.dominio)
                if jid:
                    await client.set_afiliacion(nombre_sala, jid, "member")
            await self._marcar_sync(canal, EstadoSync.OK)
        except EjabberdError as exc:
            await self._marcar_sync(canal, EstadoSync.ERROR, str(exc))

    async def anadir_miembro(self, grupo_id: uuid.UUID, usuario: Usuario) -> None:
        canal = await self._canal_de(OrigenCanal.GRUPO_TRABAJO, grupo_id)
        if canal is None:
            return
        cfg = await self._cargar_config()
        jid = self._jid_usuario(usuario, cfg.dominio)
        if not jid:
            return
        try:
            client = await self._get_client()
            await client.set_afiliacion(self._nombre_sala_grupo(grupo_id), jid, "member")
            await self._marcar_sync(canal, EstadoSync.OK)
        except EjabberdError as exc:
            await self._marcar_sync(canal, EstadoSync.ERROR, str(exc))

    async def quitar_miembro(self, grupo_id: uuid.UUID, usuario: Usuario) -> None:
        canal = await self._canal_de(OrigenCanal.GRUPO_TRABAJO, grupo_id)
        if canal is None:
            return
        cfg = await self._cargar_config()
        jid = self._jid_usuario(usuario, cfg.dominio)
        if not jid:
            return
        try:
            client = await self._get_client()
            # 'none' retira la afiliación → pierde acceso a la sala members_only.
            await client.set_afiliacion(self._nombre_sala_grupo(grupo_id), jid, "none")
            await self._marcar_sync(canal, EstadoSync.OK)
        except EjabberdError as exc:
            await self._marcar_sync(canal, EstadoSync.ERROR, str(exc))

    async def archivar_canal_grupo(self, grupo_id: uuid.UUID) -> None:
        """El grupo terminó: marca el canal como archivado. La sala se conserva
        en ejabberd como histórico (no se destruye)."""
        canal = await self._canal_de(OrigenCanal.GRUPO_TRABAJO, grupo_id)
        if canal is None:
            return
        canal.fecha_archivado = datetime.utcnow()
        await self.session.commit()

    # ── Consulta / reintento (para la capa GraphQL) ──────────────────────

    async def mis_canales(self, usuario: Usuario) -> list[CanalChat]:
        """Canales del usuario: los de sus grupos de trabajo y los de las unidades
        donde ocupa un cargo vigente. Derivado de SIGA, no de ejabberd.
        """
        if usuario.contacto_id is None:
            return []
        from app.modules.membresia.models.nombramiento_vigente import NombramientoVigente

        # Grupos de trabajo activos del miembro.
        sub_grupos = (
            select(MiembroGrupo.grupo_id)
            .where(
                MiembroGrupo.miembro_id == usuario.contacto_id,
                MiembroGrupo.activo == True,      # noqa: E712
                MiembroGrupo.eliminado == False,  # noqa: E712
            )
        )
        # Unidades donde el miembro tiene cargo vigente.
        sub_unidades = (
            select(NombramientoVigente.agrupacion_id)
            .where(NombramientoVigente.miembro_id == usuario.contacto_id)
        )
        from sqlalchemy import or_, and_
        r = await self.session.execute(
            select(CanalChat).where(
                CanalChat.eliminado == False,  # noqa: E712
                or_(
                    and_(
                        CanalChat.origen == OrigenCanal.GRUPO_TRABAJO,
                        CanalChat.origen_id.in_(sub_grupos),
                    ),
                    and_(
                        CanalChat.origen == OrigenCanal.UNIDAD_ORGANIZATIVA,
                        CanalChat.origen_id.in_(sub_unidades),
                    ),
                ),
            )
        )
        return list(r.scalars().all())

    async def reintentar_sync(self, canal_id: uuid.UUID) -> Optional[CanalChat]:
        """Reintenta la sincronización de un canal en estado ERROR.

        Reaplica creación de sala + membresía. Devuelve el canal con su nuevo
        estado_sync, o None si no existe.
        """
        r = await self.session.execute(
            select(CanalChat).where(
                CanalChat.id == canal_id,
                CanalChat.eliminado == False,  # noqa: E712
            )
        )
        canal = r.scalar_one_or_none()
        if canal is None:
            return None
        if canal.origen == OrigenCanal.GRUPO_TRABAJO:
            nombre_sala = self._nombre_sala_grupo(canal.origen_id)
            await self._crear_sala_remota(canal, nombre_sala)
            await self.sincronizar_membresia_grupo(canal.origen_id)
        elif canal.origen == OrigenCanal.UNIDAD_ORGANIZATIVA:
            nombre_sala = self._nombre_sala_unidad(canal.origen_id)
            await self._crear_sala_remota(canal, nombre_sala)
            await self.sincronizar_membresia_unidad(canal.origen_id)
        await self.session.refresh(canal)
        return canal

    # ── Internos ─────────────────────────────────────────────────────────

    async def _crear_sala_remota(self, canal: CanalChat, nombre_sala: str) -> None:
        try:
            client = await self._get_client()
            await client.crear_sala(nombre_sala, persistente=True)
            await self._marcar_sync(canal, EstadoSync.OK)
        except EjabberdError as exc:
            await self._marcar_sync(canal, EstadoSync.ERROR, str(exc))

    async def _canal_de(self, origen: OrigenCanal, origen_id: uuid.UUID) -> Optional[CanalChat]:
        r = await self.session.execute(
            select(CanalChat).where(
                CanalChat.origen == origen,
                CanalChat.origen_id == origen_id,
                CanalChat.eliminado == False,  # noqa: E712
            )
        )
        return r.scalar_one_or_none()

    async def _marcar_sync(self, canal: CanalChat, estado: EstadoSync, error: Optional[str] = None) -> None:
        canal.estado_sync = estado
        canal.ultimo_sync = datetime.utcnow()
        canal.ultimo_error = error
        await self.session.commit()
