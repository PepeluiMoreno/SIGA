// Queries GraphQL del módulo de comunicación (notificaciones in-app y chat interno).
// Strawberry expone los campos en camelCase.

// ── Notificaciones (sistema → usuario) ──────────────────────────────────────

export const GET_NO_LEIDAS = `
  query MisNotificacionesNoLeidas {
    misNotificacionesNoLeidas
  }
`

export const GET_MIS_NOTIFICACIONES = `
  query MisNotificaciones {
    misNotificaciones {
      id
      titulo
      mensaje
      leida
      urlAccion
      fechaCreacion
      tipo {
        codigo
        nombre
      }
    }
  }
`

export const MARCAR_LEIDA = `
  mutation MarcarLeida($notificacionId: UUID!) {
    marcarNotificacionLeida(notificacionId: $notificacionId) {
      exito
      afectadas
      mensaje
    }
  }
`

export const MARCAR_TODAS_LEIDAS = `
  mutation MarcarTodasLeidas {
    marcarTodasNotificacionesLeidas {
      exito
      afectadas
      mensaje
    }
  }
`

// ── Chat interno (canales por grupo / unidad) ───────────────────────────────

export const GET_MIS_CANALES_CHAT = `
  query MisCanalesChat {
    misCanalesChat {
      id
      origen
      nombre
      salaJid
      estadoSync
      ultimoError
      archivado
    }
  }
`

export const REINTENTAR_SYNC_CANAL = `
  mutation ReintentarSync($canalId: UUID!) {
    reintentarSyncCanal(canalId: $canalId) {
      exito
      mensaje
      canal { id estadoSync }
    }
  }
`
