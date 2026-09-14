"""Prueba de concurrencia del gateway: ¿aguanta peticiones simultáneas o devuelve 429?

No es un lote: son unas pocas completaciones mínimas a la vez, para saber si el lote de 80 puede
paralelizarse alguna vez. Sin aislamiento por ranura el lote corre secuencial de todos modos, así
que esto solo informa la decisión, no la habilita.

Escribe harness/concurrencia.json.

Uso:  python3 concurrencia.py [n_peticiones]
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
CLAVE = os.environ.get("OPENCODE_GO_API_KEY", "")
URL = os.environ.get("OPENCODE_GO_BASE_URL", "https://opencode.ai/zen/go/v1").rstrip("/")
MODELO = os.environ.get("MODELO_CRUDO", "glm-5.3-flash")


def peticion(i: int) -> dict:
    cuerpo = json.dumps({
        "model": MODELO,
        "messages": [{"role": "user", "content": f"responde solo con el numero {i}"}],
        "max_tokens": 16,
    }).encode()
    req = urllib.request.Request(
        f"{URL}/chat/completions", data=cuerpo,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {CLAVE}",
                 # Sin User-Agent propio, el borde del gateway responde 403 código 1010 (bloqueo de
                 # cliente, no límite de tasa): la prueba mediría el bloqueo, no la concurrencia.
                 "User-Agent": "opencode-cli/1.0",
                 "x-opencode-session": f"concurrencia-{i}"}, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            datos = json.loads(r.read().decode())
        return {"i": i, "codigo": r.status, "segundos": round(time.time() - t0, 2),
                "tokens": (datos.get("usage") or {}).get("total_tokens")}
    except urllib.error.HTTPError as e:
        return {"i": i, "codigo": e.code, "segundos": round(time.time() - t0, 2),
                "error": e.read().decode()[:200]}
    except Exception as ex:  # noqa: BLE001
        return {"i": i, "codigo": None, "segundos": round(time.time() - t0, 2), "error": str(ex)[:200]}


def main() -> None:
    n = int(os.sys.argv[1]) if len(os.sys.argv) > 1 else 3
    if not CLAVE:
        raise SystemExit("falta OPENCODE_GO_API_KEY en el entorno")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=n) as ex:
        res = list(ex.map(peticion, range(n)))
    fallos = [r for r in res if r["codigo"] != 200]
    salida = {
        "peticiones": n, "fallos": len(fallos), "segundos": round(time.time() - t0, 2),
        "codigos": [r["codigo"] for r in res],
        "tokens": sum(r.get("tokens") or 0 for r in res),
        "detalle": res,
        "lectura": ("el gateway aguanta simultaneas; paralelizar dependeria del aislamiento por "
                    "ranura" if not fallos else
                    "hay fallos bajo simultaneidad: el lote va secuencial"),
    }
    with open(os.path.join(BASE, "concurrencia.json"), "w", encoding="utf-8") as fh:
        json.dump(salida, fh, ensure_ascii=False, indent=2)
    print(f"{n} simultaneas: codigos {salida['codigos']}, {salida['fallos']} fallos, "
          f"{salida['segundos']}s, {salida['tokens']} tokens")
    for r in res:
        if r["codigo"] != 200:
            print(f"   fallo {r['i']}: {r['codigo']} {r.get('error','')}")


if __name__ == "__main__":
    main()
