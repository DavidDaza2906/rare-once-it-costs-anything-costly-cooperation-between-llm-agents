"""Congela los archivos de resultados: SHA-256 + hora + hashes del instrumento, para la revisión
número por número. Uso: python3 herramientas/congelar.py [archivos...]
Por defecto: reportes/factorial.json, reportes/estimaciones.json, escena.resuelta.json,
harness/instrumento.json. Escribe reportes/congelado.json (se anexa; nunca se sobreescribe una
entrada anterior)."""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POR_DEFECTO = ["reportes/factorial.json", "reportes/estimaciones.json", "escena.resuelta.json",
               "harness/instrumento.json"]


def sha(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def main() -> None:
    rutas = sys.argv[1:] or POR_DEFECTO
    entrada = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "archivos": {}}
    for r in rutas:
        p = os.path.join(RAIZ, r)
        entrada["archivos"][r] = ({"sha256": sha(p), "bytes": os.path.getsize(p)}
                                  if os.path.exists(p) else {"error": "no existe"})
    inst = os.path.join(RAIZ, "harness", "instrumento.json")
    if os.path.exists(inst):
        with open(inst, encoding="utf-8") as fh:
            entrada["instrumento"] = {k: v for k, v in json.load(fh).items()
                                      if k in ("hash_escena", "hash_arnes", "hash_pruebas")}
    destino = os.path.join(RAIZ, "reportes", "congelado.json")
    previas = []
    if os.path.exists(destino):
        with open(destino, encoding="utf-8") as fh:
            previas = json.load(fh)
    previas.append(entrada)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(previas, fh, ensure_ascii=False, indent=2)
    print(f"congelado {entrada['ts']}:")
    for r, v in entrada["archivos"].items():
        print(f"  {r:32s} {v.get('sha256', v.get('error'))[:16]}  {v.get('bytes', '')}")
    print(f"-> {destino} ({len(previas)} entradas)")


if __name__ == "__main__":
    main()
