"""Espera a que PostgreSQL sea resolvible y acepte conexiones TCP."""

import os
import socket
import sys
import time


def main() -> int:
    host = os.getenv("DB_HOST", "db")
    port = int(os.getenv("DB_PORT", "5432"))
    timeout_seconds = int(os.getenv("DB_WAIT_TIMEOUT", "90"))
    retry_interval = float(os.getenv("DB_WAIT_INTERVAL", "2"))

    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=5):
                print(f"[wait-for-db] PostgreSQL listo en {host}:{port}")
                return 0
        except OSError as exc:
            last_error = exc
            print(f"[wait-for-db] Esperando a {host}:{port}: {exc}")
            time.sleep(retry_interval)

    print(
        f"[wait-for-db] Timeout esperando PostgreSQL en {host}:{port}. "
        f"Ultimo error: {last_error}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
