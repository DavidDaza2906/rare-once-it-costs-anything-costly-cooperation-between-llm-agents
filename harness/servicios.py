"""Levanta los seis puertos de egreso, uno por agente, apuntando al mismo almacén.

La identidad va por RUTA: cada servicio sabe a qué agente sirve y así registra sus peticiones
sin confiar en nada que el agente declare. Es la pieza que hace posible la atribución.

Uso:  python3 servicios.py [base] [n]        (por defecto base 8201, n 6)
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    base = int(sys.argv[1]) if len(sys.argv) > 1 else 8201
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    hijos = []
    for i in range(n):
        puerto = base + i
        agente = f"agente-{i+1:02d}"
        env = {**os.environ, "PUERTO": str(puerto), "AGENTE": agente,
               "ACTIVIDAD_VISIBLE": os.environ.get("ACTIVIDAD_VISIBLE", "1")}
        p = subprocess.Popen([sys.executable, os.path.join(BASE, "puerto.py"), str(puerto)],
                             env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        hijos.append((puerto, agente, p))
        print(f"  puerto {puerto} -> {agente} (pid {p.pid})", flush=True)

    def parar(*_):
        for _, _, p in hijos:
            p.terminate()
        sys.exit(0)

    signal.signal(signal.SIGTERM, parar)
    signal.signal(signal.SIGINT, parar)
    print(f"{n} servicios escuchando; Ctrl-C para parar", flush=True)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
