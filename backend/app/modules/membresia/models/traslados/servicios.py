from typing import List, Optional
from sqlalchemy import select, and_, or_
from datetime import datetime, date
import json

from app.core.database import get_session
from app.modulos.traslados.modelos import SolicitudTraslado, EstadoTraslado
from app.modulos.administracion_miembros.modelos import miembro
from app.modulos.equipos.modelos import MiembroEquipo, Equipo
from app.modulos.agrupaciones_territoriales.modelos import AgrupacionTerritorial
from app.modulos.comunicaciones.servicios import ServicioComunicaciones
from app.modulos.administracion_miembros.servicios import ServicioGestionmiembros


class ServicioTraslados:
    
    def __init__(self):
        self.servicio_comunicaciones = ServicioComunicaciones()
        self.servicio_miembros = ServicioGestionmiembros()
    
    async def crear_solicitud_traslado(
        self,
        miembro_id: int,
        agrupacion_destino_id: int,
        motivo: str,
        fecha_efectiva_deseada: Optional[date] = None
    ) -> SolicitudTraslado:
        """Crear nueva solicitud de traslado"""
        
        # Obtener miembro y validar
        miembro = await self.obtener_miembro(miembro_id)
        
        if miembro.estado != Estadomiembro.ACTIVO:
            raise ValueError("Solo pueden solicitar traslado los miembros activos")
        
        agrupacion_origen_id = miembro.agrupacion_territorial_id
        
        # Validar que no sea la misma agrupación
        if agrupacion_origen_id == agrupacion_destino_id:
            raise ValueError("No puedes trasladarte a la misma agrupación")
        
        # Validar que no tenga traslados pendientes
        traslado_pendiente = await self.tiene_traslado_pendiente(miembro_id)
        if traslado_pendiente:
            raise ValueError("Ya tienes una solicitud de traslado pendiente")
        
        # Crear solicitud
        solicitud = SolicitudTraslado(
            miembro_id=miembro_id,
            agrupacion_origen_id=agrupacion_origen_id,
            agrupacion_destino_id=agrupacion_destino_id,
            motivo=motivo,
            fecha_efectiva_deseada=fecha_efectiva_deseada or date.today(),
            estado=EstadoTraslado.PENDIENTE
        )
        
        async with get_session() as session:
            session.add(solicitud)
            await session.commit()
            await session.refresh(solicitud)
        
        # Notificar a coordinadores
        await self._notificar_nueva_solicitud(solicitud)
        
        return solicitud
    
    async def aprobar_traslado(
        self,
        solicitud_id: int,
        coordinador_id: int,
        observaciones: Optional[str] = None
    ) -> SolicitudTraslado:
        """Aprobar traslado (por coordinador de origen o destino)"""
        
        solicitud = await self.obtener_solicitud(solicitud_id)
        coordinador = await self.obtener_usuario(coordinador_id)
        
        # Determinar si es coordinador de origen o destino
        es_coordinador_origen = await self._es_coordinador_agrupacion(
            coordinador_id, 
            solicitud.agrupacion_origen_id
        )
        es_coordinador_destino = await self._es_coordinador_agrupacion(
            coordinador_id, 
            solicitud.agrupacion_destino_id
        )
        
        if not es_coordinador_origen and not es_coordinador_destino:
            raise PermissionError("No eres coordinador de ninguna de las agrupaciones involucradas")
        
        # Aprobar según corresponda
        if es_coordinador_origen:
            if solicitud.aprobado_origen:
                raise ValueError("Esta solicitud ya fue aprobada por el coordinador de origen")
            
            solicitud.aprobado_origen = True
            solicitud.fecha_aprobacion_origen = datetime.utcnow()
            solicitud.coordinador_origen_id = coordinador_id
            solicitud.observaciones_origen = observaciones
            solicitud.estado = EstadoTraslado.APROBADO_ORIGEN
        
        if es_coordinador_destino:
            if solicitud.aprobado_destino:
                raise ValueError("Esta solicitud ya fue aprobada por el coordinador de destino")
            
            solicitud.aprobado_destino = True
            solicitud.fecha_aprobacion_destino = datetime.utcnow()
            solicitud.coordinador_destino_id = coordinador_id
            solicitud.observaciones_destino = observaciones
            solicitud.estado = EstadoTraslado.APROBADO_DESTINO
        
        # Si ambos aprobaron, marcar como aprobado
        if solicitud.aprobado_origen and solicitud.aprobado_destino:
            solicitud.estado = EstadoTraslado.APROBADO
            
            # Ejecutar traslado automáticamente
            await self._ejecutar_traslado(solicitud)
        
        async with get_session() as session:
            session.add(solicitud)
            await session.commit()
            await session.refresh(solicitud)
        
        # Notificar
        await self._notificar_aprobacion(solicitud, es_coordinador_origen, es_coordinador_destino)
        
        return solicitud
    
    async def rechazar_traslado(
        self,
        solicitud_id: int,
        coordinador_id: int,
        motivo_rechazo: str
    ) -> SolicitudTraslado:
        """Rechazar traslado"""
        
        solicitud = await self.obtener_solicitud(solicitud_id)
        
        # Determinar si es coordinador de origen o destino
        es_coordinador_origen = await self._es_coordinador_agrupacion(
            coordinador_id, 
            solicitud.agrupacion_origen_id
        )
        es_coordinador_destino = await self._es_coordinador_agrupacion(
            coordinador_id, 
            solicitud.agrupacion_destino_id
        )
        
        if not es_coordinador_origen and not es_coordinador_destino:
            raise PermissionError("No tienes permisos para rechazar esta solicitud")
        
        # Marcar como rechazado
        if es_coordinador_origen:
            solicitud.estado = EstadoTraslado.RECHAZADO_ORIGEN
        else:
            solicitud.estado = EstadoTraslado.RECHAZADO_DESTINO
        
        solicitud.motivo_rechazo = motivo_rechazo
        
        async with get_session() as session:
            session.add(solicitud)
            await session.commit()
        
        # Notificar al miembro
        await self._notificar_rechazo(solicitud)
        
        return solicitud
    
    async def _ejecutar_traslado(self, solicitud: SolicitudTraslado):
        """Ejecutar el traslado una vez aprobado por ambos coordinadores"""
        
        miembro = solicitud.miembro
        
        # 1. Guardar datos anteriores
        solicitud.numero_miembro_anterior = miembro.numero_miembro
        
        # 2. Dar de baja de equipos territoriales de origen
        equipos_baja = await self._dar_baja_equipos_territoriales(
            miembro.id,
            solicitud.agrupacion_origen_id
        )
        solicitud.equipos_dados_baja = json.dumps([
            {'equipo_id': e.id, 'equipo_nombre': e.nombre} 
            for e in equipos_baja
        ])
        
        # 3. Cambiar agrupación territorial y generar nuevo número de miembro
        await self.servicio_miembros.cambiar_agrupacion(
            miembro_id=miembro.id,
            nueva_agrupacion_id=solicitud.agrupacion_destino_id,
            motivo=f"Traslado aprobado. Solicitud #{solicitud.id}",
            usuario_id=solicitud.coordinador_destino_id
        )
        
        # Recargar miembro para obtener nuevo número
        await self._refrescar_miembro(miembro)
        solicitud.numero_miembro_nuevo = miembro.numero_miembro
        
        # 4. Recalcular recursos disponibles de ambas agrupaciones
        await self._recalcular_recursos_agrupacion(solicitud.agrupacion_origen_id)
        await self._recalcular_recursos_agrupacion(solicitud.agrupacion_destino_id)
        
        # 5. Actualizar solicitud
        solicitud.estado = EstadoTraslado.EJECUTADO
        solicitud.fecha_ejecucion = datetime.utcnow()
        
        # 6. Notificar al miembro y coordinadores
        await self._notificar_traslado_ejecutado(solicitud)
    
    async def _dar_baja_equipos_territoriales(
        self,
        miembro_id: int,
        agrupacion_origen_id: int
    ) -> List[Equipo]:
        """Dar de baja al miembro de todos los equipos de trabajo de la agrupación origen."""
        # TODO: implementar lógica de baja en equipos territoriales
        return []