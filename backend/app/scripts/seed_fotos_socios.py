"""Sube fotos de carnet fake a MinIO y fija el `fotoUrl` de cada socio PF fake.

SOLO-DEV. Baja retratos de randomuser.me (httpx), los sube al bucket de MinIO bajo
un prefijo dedicado y deja en `Contacto.foto_url` la URL pública del objeto.

Config por entorno (NO pongas las claves en código):
    MINIO_ENDPOINT        host[:puerto] del API S3 de MinIO (p.ej. panel.europalaica.org)
    MINIO_ACCESS_KEY      access key
    MINIO_SECRET_KEY      secret key
    MINIO_SECURE          'true'/'false' (def. 'true')
    MINIO_BUCKET          bucket (def. 'siga-dev')   ← usa uno dedicado, no el de prod
    MINIO_PREFIX          prefijo de objeto (def. 'socios')
    MINIO_PUBLIC_BASEURL  base pública para el navegador (def. https://MINIO_ENDPOINT)

Requiere la dependencia `minio` en el backend:  uv add minio

Uso (en el contenedor backend de dev, con las MINIO_* exportadas):
    python -m app.scripts.seed_fotos_socios
"""
from __future__ import annotations

import asyncio
import io
import os

import httpx
from sqlalchemy import select

from app.core.database import async_session
from app.modules.membresia.models.contacto import Contacto


def _cfg():
    endpoint = os.environ.get("MINIO_ENDPOINT")
    access = os.environ.get("MINIO_ACCESS_KEY")
    secret = os.environ.get("MINIO_SECRET_KEY")
    if not (endpoint and access and secret):
        raise SystemExit("Faltan MINIO_ENDPOINT / MINIO_ACCESS_KEY / MINIO_SECRET_KEY en el entorno.")
    secure = os.environ.get("MINIO_SECURE", "true").lower() in ("1", "true", "yes")
    bucket = os.environ.get("MINIO_BUCKET", "siga-dev")
    prefix = os.environ.get("MINIO_PREFIX", "socios").strip("/")
    base = os.environ.get("MINIO_PUBLIC_BASEURL", f"{'https' if secure else 'http'}://{endpoint}")
    return endpoint, access, secret, secure, bucket, prefix, base.rstrip("/")


def _portrait_url(doc: str, sexo: str) -> str:
    try:
        idx = int(doc.split("-")[-1]) % 100
    except ValueError:
        idx = 0
    genero = "men" if sexo == "H" else "women"
    return f"https://randomuser.me/api/portraits/{genero}/{idx}.jpg"


async def main() -> None:
    try:
        from minio import Minio
    except ImportError:
        raise SystemExit("Falta la dependencia 'minio'. Instálala:  uv add minio")

    endpoint, access, secret, secure, bucket, prefix, base = _cfg()
    client = Minio(endpoint, access_key=access, secret_key=secret, secure=secure)
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        print(f"[minio] bucket '{bucket}' creado")

    async with async_session() as session:
        socios = (await session.execute(
            select(Contacto).where(
                Contacto.numero_documento.like("FAKE-PF-%"),
                Contacto.tipo == "PERSONA_FISICA",
            )
        )).scalars().all()

        subidas = 0
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as http:
            for c in socios:
                key = f"{prefix}/{c.numero_documento}.jpg"
                try:
                    r = await http.get(_portrait_url(c.numero_documento, c.sexo or "M"))
                    r.raise_for_status()
                    data = r.content
                    client.put_object(
                        bucket, key, io.BytesIO(data), length=len(data),
                        content_type="image/jpeg",
                    )
                    c.foto_url = f"{base}/{bucket}/{key}"
                    subidas += 1
                    print(f"+ {c.numero_documento} -> {c.foto_url}")
                except Exception as e:  # noqa: BLE001 - dev script, seguimos con el resto
                    print(f"  ⚠ {c.numero_documento}: {e}")

        await session.commit()
        print(f"\n[seed_fotos_socios] subidas {subidas} fotos al bucket '{bucket}'.")
        print("Recuerda: el bucket/objeto debe ser de LECTURA PÚBLICA (o usar URLs "
              "presigned) para que el navegador cargue las fotos.")


if __name__ == "__main__":
    asyncio.run(main())
