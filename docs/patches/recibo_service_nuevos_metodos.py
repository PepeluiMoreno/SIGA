
    # ─── Notificaciones y PDF ──────────────────────────────────────────

    async def comunicar_fallidos(
        self,
        recibo_ids: list,
        plantilla_email_id,
    ) -> int:
        """Marca un lote de recibos FALLIDO como notificados al socio.

        Registra trazabilidad: fecha_aviso_fallido = hoy, plantilla_email_aviso_id.
        El envío real de email se delega al módulo de Comunicación Interna (TODO).
        Devuelve el nº de recibos actualizados.
        """
        from sqlalchemy import update
        from datetime import date as _date
        if not recibo_ids:
            return 0
        r = await self.session.execute(
            update(Recibo)
            .where(Recibo.id.in_(recibo_ids))
            .where(Recibo.estado == "FALLIDO")
            .values(
                fecha_aviso_fallido=_date.today(),
                plantilla_email_aviso_id=plantilla_email_id,
            )
        )
        await self.session.commit()
        return r.rowcount or 0

    async def registrar_intencion_envio_email(
        self,
        recibo_id,
        plantilla_email_id,
    ):
        """Registra la intención de enviar el recibo al socio (trazabilidad).

        El envío real queda pendiente de integración con Comunicación Interna.
        """
        from datetime import date as _date
        recibo = await self.obtener_recibo(recibo_id)
        if not recibo:
            raise ValueError(f"Recibo {recibo_id} no encontrado")
        obs_prev = recibo.observaciones or ""
        sufijo = f"[{_date.today().isoformat()}] Email solicitado (plantilla {plantilla_email_id})"
        recibo.observaciones = f"{obs_prev}\n{sufijo}".strip()
        self.session.add(recibo)
        await self.session.commit()
        await self.session.refresh(recibo)
        return recibo

    async def generar_pdf(self, recibo_id) -> str:
        """Genera el PDF del recibo y lo devuelve codificado en base64.

        Usa reportlab si está disponible; si no, devuelve texto plano en base64
        como placeholder funcional para que la UI no rompa.
        """
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
                ("Ejercicio", str(recibo.ejercicio)),
                ("Concepto", recibo.concepto or ""),
                ("Importe", f"{recibo.importe:.2f} \u20ac"),
                ("Estado", recibo.estado),
                ("Modo cobro", recibo.modo_cobro or "\u2014"),
                ("Fecha emisión", recibo.fecha_emision.isoformat() if recibo.fecha_emision else "\u2014"),
                ("Fecha cobro", recibo.fecha_cobro.isoformat() if recibo.fecha_cobro else "\u2014"),
            ]:
                c.drawString(20, y, f"{label}: {value}")
                y -= 15
            c.showPage()
            c.save()
            return base64.b64encode(buf.getvalue()).decode("ascii")
        except ImportError:
            placeholder = (
                f"RECIBO {recibo.numero_recibo}\n"
                f"Ejercicio: {recibo.ejercicio}\n"
                f"Concepto: {recibo.concepto}\n"
                f"Importe: {recibo.importe:.2f} EUR\n"
                f"Estado: {recibo.estado}\n"
                f"(PDF no disponible: falta instalar reportlab en el backend)"
            )
            return base64.b64encode(placeholder.encode("utf-8")).decode("ascii")
