"""Corre un lote de corridas con TOPE ACUMULADO de tokens, y para cuando el presupuesto se agota.

El tope por corrida del bucle es una red de seguridad; el tope acumulado es el que manda, así que
aquí el tope de cada corrida se recalcula como el presupuesto que queda. Si el lote no cabe, no
arranca una corrida a medias: se detiene y lo dice.

Uso:
    python3 lote.py --corridas 20 --tope 3000000 [--escena escena.resuelta.json] [--etiqueta piloto]
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
sys.path.insert(0, os.path.join(BASE, ".venv-inspect", "lib", "python3.12", "site-packages"))

_spec = importlib.util.spec_from_file_location("bucle", os.path.join(BASE, "bucle.py"))
bucle = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bucle)


# Red de seguridad POR CORRIDA. Una corrida sana mide entre 76k y 270k tokens; una corrida que entra
# en bucle de contexto puede gastarse todo el presupuesto restante (paso el 13 sep: una corrida de
# 1.650.924 tokens se llevo por delante el bloque B). El tope acumulado no protege de eso, porque el
# tope de cada corrida se recalculaba como el restante: esta constante es la que lo impide.
TOPE_CORRIDA = 350_000


async def lote(escena: str, rondas: int | None, agentes: int | None, tope: int,
               corridas: int, etiqueta: str) -> dict:
    gastado = 0
    hechas: list[dict] = []
    arranque = time.time()
    for i in range(corridas):
        restante = tope - gastado
        # Una corrida mide ~169k con 6 agentes x 4 rondas. Si lo que queda no da ni para media
        # corrida, se para: mejor un lote corto y declarado que una corrida truncada.
        if restante < 90000:
            print(f"\n[alto] quedan {restante:,} tokens: no alcanza para otra corrida.")
            break
        print(f"\n=== corrida {i + 1}/{corridas} | gastado {gastado:,} | queda {restante:,} ===",
              flush=True)
        tope_corrida = min(restante, TOPE_CORRIDA)
        print(f"    tope de esta corrida: {tope_corrida:,}", flush=True)
        resumen = await bucle.correr(escena, rondas, agentes, tope_corrida)
        t = int(resumen.get("tokens_totales") or 0)
        gastado += t
        hechas.append({"corrida": resumen.get("escena"), "tokens": t,
                       "log": resumen.get("log"), "hash_escena": resumen.get("hash_escena")})
        print(f"    -> {t:,} tokens | acumulado {gastado:,} / {tope:,}", flush=True)

    parcial = {
        "etiqueta": etiqueta, "corridas_pedidas": corridas, "corridas_hechas": len(hechas),
        "tope": tope, "gastado": gastado, "restante": tope - gastado,
        "minutos": round((time.time() - arranque) / 60, 1), "detalle": hechas,
    }
    marca = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    ruta = os.path.join(RAIZ, "salidas", f"lote_{etiqueta}_{marca}.json")
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(parcial, fh, ensure_ascii=False, indent=2)
    print(f"\nLOTE: {len(hechas)} corridas, {gastado:,} tokens, {parcial['minutos']} min -> {ruta}")
    return parcial


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--escena", default=os.path.join(RAIZ, "escena.resuelta.json"))
    ap.add_argument("--rondas", type=int)
    ap.add_argument("--agentes", type=int)
    ap.add_argument("--tope", type=int, default=3_000_000)
    ap.add_argument("--corridas", type=int, default=20)
    ap.add_argument("--etiqueta", default="lote")
    a = ap.parse_args()
    asyncio.run(lote(a.escena, a.rondas, a.agentes, a.tope, a.corridas, a.etiqueta))


if __name__ == "__main__":
    main()
