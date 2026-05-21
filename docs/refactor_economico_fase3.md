# Refactor económico — Fase 3: Separación servicio/resolver

## Estado

Los 4 servicios de `backend/app/modules/economico/services/` necesitan
los métodos nuevos listados abajo. El resolver `economico_mutations.py`
está refactorizado completamente (ver sección 5).

## Aplicar en local

```bash
git checkout refactor/coherencia-modulos
# Para cada servicio, añadir el bloque de métodos al final de la clase
```

---

## Resumen de cambios

| Servicio | Métodos añadidos |
|---|---|
| `TesoreriaService` | `validar_imputacion_actividad()` — elimina la validación duplicada en 2 mutations |
| `ReciboService` | `comunicar_fallidos()`, `registrar_intencion_envio_email()`, `generar_pdf()` |
| `CuotaService` | `presentar/aprobar/rechazar/anular_solicitud_reduccion()`, `modificar_incremento_cuota()`, `crear/actualizar_motivo_reduccion()` |
| `DonacionService` | `_cfg_org()` — lee nombre+NIF de la organización desde configuraciones |
| `economico_mutations.py` | Refactorizado: todo el código de dominio movido a servicios |

---

## 1. `tesoreria_service.py` — Añadir al final de la clase `TesoreriaService`

```python
    # ─── Validación de imputación (reutilizable) ─────────────────────────────────────

    async def validar_imputacion_actividad(self, actividad_id, campania_id=None):
        """Valida que la actividad sea imputable: no plantilla recurrente, campaña no cerrada.
        Devuelve el campania_id efectivo. Raises ValueError si hay restricción.
        """
        from app.modules.actividades.models.actividad import Actividad
        from app.modules.actividades.models.campana import Campania
        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad_id))
        actividad = r.scalars().first()
        if not actividad:
            raise ValueError(f"Actividad {actividad_id} no encontrada.")
        if actividad.caracter == "RECURRENTE" and actividad.padre_id is None:
            raise ValueError("No se puede imputar a una plantilla recurrente. Elige una instancia concreta.")
        if actividad.campania_id:
            rc = await self.session.execute(select(Campania).where(Campania.id == actividad.campania_id))
            camp = rc.scalars().first()
            if camp and camp.esta_cerrada:
                raise ValueError(f"La campaña «{camp.nombre}» está cerrada y no admite nuevos gastos/ingresos.")
            campania_id = actividad.campania_id
        return campania_id
```

---

## 2. `recibo_service.py` — Añadir al final de la clase `ReciboService`

```python
    # ─── Notificaciones y PDF ──────────────────────────────────────────

    async def comunicar_fallidos(self, recibo_ids: list, plantilla_email_id) -> int:
        """Marca recibos FALLIDO como notificados. Devuelve nº actualizados."""
        from sqlalchemy import update
        from datetime import date as _date
        if not recibo_ids:
            return 0
        r = await self.session.execute(
            update(Recibo).where(Recibo.id.in_(recibo_ids)).where(Recibo.estado == "FALLIDO")
            .values(fecha_aviso_fallido=_date.today(), plantilla_email_aviso_id=plantilla_email_id)
        )
        await self.session.commit()
        return r.rowcount or 0

    async def registrar_intencion_envio_email(self, recibo_id, plantilla_email_id):
        """Registra intención de envío (trazabilidad). Envio real: TODO integración."""
        from datetime import date as _date
        recibo = await self.obtener_recibo(recibo_id)
        if not recibo:
            raise ValueError(f"Recibo {recibo_id} no encontrado")
        sufijo = f"[{_date.today().isoformat()}] Email solicitado (plantilla {plantilla_email_id})"
        recibo.observaciones = f"{recibo.observaciones or ''}\n{sufijo}".strip()
        self.session.add(recibo)
        await self.session.commit()
        await self.session.refresh(recibo)
        return recibo

    async def generar_pdf(self, recibo_id) -> str:
        """Genera PDF del recibo en base64. Usa reportlab si está disponible, si no placeholder."""
        import base64
        recibo = await self.obtener_recibo(recibo_id)
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
                ("Ejercicio", str(recibo.ejercicio)), ("Concepto", recibo.concepto or ""),
                ("Importe", f"{recibo.importe:.2f} €"), ("Estado", recibo.estado),
                ("Modo cobro", recibo.modo_cobro or "—"),
                ("Fecha emisión", recibo.fecha_emision.isoformat() if recibo.fecha_emision else "—"),
                ("Fecha cobro", recibo.fecha_cobro.isoformat() if recibo.fecha_cobro else "—"),
            ]:
                c.drawString(20, y, f"{label}: {value}")
                y -= 15
            c.showPage(); c.save()
            return base64.b64encode(buf.getvalue()).decode("ascii")
        except ImportError:
            placeholder = (f"RECIBO {recibo.numero_recibo}\nEjercicio: {recibo.ejercicio}\n"
                           f"Concepto: {recibo.concepto}\nImporte: {recibo.importe:.2f} EUR\n"
                           f"Estado: {recibo.estado}\n(PDF no disponible: falta reportlab)")
            return base64.b64encode(placeholder.encode("utf-8")).decode("ascii")
```

---

## 3. `cuota_service.py` — Añadir al final de la clase `CuotaService`

```python
    # ─── Solicitudes de reducción / incremento / motivos (ver suf_cuota.py en docs/) ───
    # Métodos: presentar_solicitud_reduccion, aprobar_solicitud_reduccion,
    # rechazar_solicitud_reduccion, anular_solicitud_reduccion,
    # modificar_incremento_cuota, crear_motivo_reduccion, actualizar_motivo_reduccion
    # Implementación completa en docs/suf_cuota.py
```

---

## 4. `donacion_service.py` — Añadir al final de la clase `DonacionService`

```python
    async def _cfg_org(self) -> tuple[str, str]:
        """Lee nombre y NIF de la organización desde la tabla de configuraciones."""
        from app.modules.configuracion.models.configuracion import Configuracion
        async def _get(clave: str, default: str = "") -> str:
            r = await self.session.execute(select(Configuracion).where(Configuracion.clave == clave))
            row = r.scalars().first()
            return (row.valor if row and row.valor else default) or default
        nombre = await _get("organizacion.nombre") or await _get("org.nombre") or "Asociación"
        nif = await _get("organizacion.nif") or await _get("org.nif") or "—"
        return nombre, nif
```

Además, actualizar `emitir_certificado_anual` para que lea los datos de org internamente:
```python
    async def emitir_certificado_anual(self, ejercicio, nif_donante, tipo) -> tuple[str, bytes]:
        organizacion_nombre, organizacion_nif = await self._cfg_org()
        # ... resto del método igual que antes ...
```

---

## 5. `economico_mutations.py` — Refactor completo

El fichero refactorizado está en `docs/suf_economico_mutations.py`.
Características clave del resolver refactorizado:
- Importa `CuotaService` al nivel de módulo (no con import diferido en cada método)
- Cada mutation queda en 3-8 líneas: instanciar servicio + delegar + devolver
- La validación de imputación llama a `svc.validar_imputacion_actividad()` (DRY)
- Las solicitudes de reducción delegan en `CuotaService`
- `comunicar_recibos_fallidos`, `descargar_recibo_pdf`, `enviar_recibo_email` delegan en `ReciboService`
- `emitir_certificado_donacion_anual` delega completamente en `DonacionService` (sin leer config)
