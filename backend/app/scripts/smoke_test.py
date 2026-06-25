"""Smoke test post-deploy (se ejecuta DENTRO del contenedor backend).

Comprueba los caminos críticos contra el propio API GraphQL en localhost:8000:
login → miPerfil → socios → sociosCount → cuotasAnuales. Pensado para correr tras
el deploy, p. ej.:

    docker compose ... exec -T -e SMOKE_EMAIL -e SMOKE_PASSWORD backend \
        python -m app.scripts.smoke_test

Identidad: SMOKE_EMAIL/SMOKE_PASSWORD; por defecto la cuenta de sistema
`superadmin` + SUPERADMIN_PASSWORD. GQL_URL (por defecto
http://localhost:8000/graphql). Sale con código !=0 si algún check falla.
"""
import json
import os
import sys
import urllib.request

URL = os.environ.get("GQL_URL", "http://localhost:8000/graphql")
# Identificador de login: email o username. Por defecto la cuenta `superadmin`.
EMAIL = os.environ.get("SMOKE_EMAIL") or "superadmin"
PASSWORD = os.environ.get("SMOKE_PASSWORD") or os.environ.get("SUPERADMIN_PASSWORD")

_fails = 0


def gql(query: str, variables: dict | None = None, token: str | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(URL, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode())


def check(name: str, ok: bool, detail="") -> None:
    global _fails
    print(("  ✓" if ok else "  ✗"), name, "" if ok else f"-> {detail}")
    if not ok:
        _fails += 1


def main() -> int:
    if not EMAIL or not PASSWORD:
        print("[smoke] Falta SMOKE_PASSWORD o SUPERADMIN_PASSWORD.")
        return 2

    print(f"[smoke] GraphQL en {URL} como {EMAIL}")

    # 1) Login (camino crítico — si falla, no funciona nada)
    r = gql(
        "mutation($e:String!,$p:String!){ login(email:$e,password:$p){ token user{ id email } } }",
        {"e": EMAIL, "p": PASSWORD},
    )
    token = ((r.get("data") or {}).get("login") or {}).get("token")
    check("login", bool(token), r.get("errors"))
    if not token:
        return 1  # sin token no tiene sentido seguir

    # 2) miPerfil (usa _to_mi_perfil / Usuario.contacto_id)
    r = gql("{ miPerfil { id email tipoVinculacionId } }", token=token)
    check("miPerfil", bool((r.get("data") or {}).get("miPerfil")), r.get("errors"))

    # 3) socios (read-model denormalizado) + count
    r = gql(
        "{ socios { id nombre apellido1 tipoMiembro{ nombre } estado{ nombre color } "
        "esVoluntario iban agrupacion{ id nombre } } }",
        token=token,
    )
    socios = (r.get("data") or {}).get("socios")
    check("socios", not r.get("errors") and socios is not None, r.get("errors"))

    r = gql("{ sociosCount }", token=token)
    check("sociosCount", not r.get("errors"), r.get("errors"))
    count = (r.get("data") or {}).get("sociosCount")

    # 4) cuotasAnuales con el campo de compat `miembro` (vinculacion_socio.contacto)
    r = gql(
        "{ cuotasAnuales { id ejercicio importe miembro { id nombre apellido1 } } }",
        token=token,
    )
    check("cuotasAnuales(miembro compat)", not r.get("errors"), r.get("errors"))

    print(f"[smoke] socios totales: {count}; listados: {len(socios or [])}")
    if _fails:
        print(f"[smoke] FALLOS: {_fails}")
        return 1
    print("[smoke] OK — todos los caminos críticos verdes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
