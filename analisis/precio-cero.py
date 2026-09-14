#!/usr/bin/env python3
"""Contraste precio 0 contra precio 5: el titular del reporte.

El control sin costo (precio 0) es una ESCENA APARTE del lote; por eso el contraste es descriptivo y
entre escenas, tal como lo declara el preregistro, y no se parece al primario pareado 20 vs 5, que ya
se calculo una sola vez y aqui NO se recalcula ni se toca.

Dos decisiones de metodo, y el motivo de cada una:

1. La unidad de conteo es la misma que usa confirmatorio.py: cada AGENTE expuesto a un precio. En el
   lote, tres agentes de cada corrida ven precio 5 y tres ven 20.

2. El intervalo es un bootstrap POR CONGLOMERADO: se remuestrean CORRIDAS, no agentes. Los seis agentes
   de una corrida comparten entorno, partes y turnos, y el deposito de la clave es un resultado
   colectivo; tratar los slots como independientes daria un intervalo falsamente estrecho, que es
   justamente el error que la nota metodologica del preregistro manda no repetir.

Se calculan las dos lecturas y se guardan juntas para que la diferencia quede a la vista:
  - mirada congelada: las 70 corridas del lote con las que se calculo el primario, mas las 8 del control.
    Debe reproducir las tasas ya publicadas (0 -> 45,8%, 5 -> 20,5%).
  - extension de precision: las 127 corridas del conjunto fijado (reportes/conjunto-congelado.json),
    mas las 8 del control. Es seguimiento de precision, no la mirada principal.

No escribe nada mas que reportes/precio-cero.json, y lo escribe con hash de escena, sha del conjunto y
hora UTC para que cualquiera pueda comprobarlo.
"""
from __future__ import annotations

import glob
import json
import os
import random
import sys
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESCENA_LOTE = "bf1b18a696a98476"
ESCENA_CERO = "47302f2c7c4bd21b"
ACTA = os.path.join(RAIZ, "reportes", "conjunto-congelado.json")
SALIDA = os.path.join(RAIZ, "reportes", "precio-cero.json")
REMUESTREOS = 10000
SEMILLA = 20260913  # la misma que usa confirmatorio.py para el primario


def leer_corrida(d: str) -> dict | None:
    f = os.path.join(d, "resumen.json")
    if not os.path.exists(f):
        return None
    try:
        return json.load(open(f, encoding="utf-8"))
    except Exception:
        return None


def tecnico_ok(d: str, r: dict) -> str | None:
    """Los invariantes baratos, los mismos que aplica herramientas/fijar_conjunto.py.

    No repite la lista completa a proposito: el conjunto del lote ya viene validado por el acta; aqui
    solo se comprueba que lo cargado siga siendo lo que el acta dice, y se aplica lo mismo al control,
    que no tiene acta propia.
    """
    ags = r.get("agentes") or {}
    if len(ags) != 6:
        return f"{len(ags)} agentes"
    ev_p = os.path.join(d, "eventos.jsonl")
    if os.path.exists(ev_p):
        t = open(ev_p, encoding="utf-8", errors="replace").read()
        if '"tipo": "tope_tokens"' in t.replace("'", '"'):
            return "truncada por tope"
        if "clave por la via del servicio" in t:
            return "contaminacion de la suite de validacion"
    return None


def cargar_lote() -> tuple[list[dict], list[tuple[str, str]]]:
    """Las corridas del conjunto fijado, en el orden del acta."""
    if not os.path.exists(ACTA):
        raise SystemExit("falta reportes/conjunto-congelado.json: fija el conjunto antes de correr esto")
    acta = json.load(open(ACTA, encoding="utf-8"))
    runs, malas = [], []
    for c in acta["corridas"]:
        nombre = c["corrida"]
        d = None
        for raiz in (RAIZ, ):
            cand = os.path.join(raiz, "salidas", nombre)
            if os.path.isdir(cand):
                d = cand
                break
        if d is None:
            malas.append((nombre, "no esta en disco"))
            continue
        r = leer_corrida(d)
        if r is None:
            malas.append((nombre, "sin resumen"))
            continue
        if r.get("hash_escena") != ESCENA_LOTE:
            malas.append((nombre, f"escena {str(r.get('hash_escena'))[:8]}"))
            continue
        p = tecnico_ok(d, r)
        if p:
            malas.append((nombre, p))
            continue
        runs.append({"dir": nombre, "res": r})
    return runs, malas


def cargar_cero() -> tuple[list[dict], list[tuple[str, str]]]:
    """El control sin costo: su escena entera, con los mismos invariantes baratos."""
    runs, malas = [], []
    for d in sorted(glob.glob(os.path.join(RAIZ, "salidas", "2026*"))):
        r = leer_corrida(d)
        if r is None or r.get("hash_escena") != ESCENA_CERO:
            continue
        p = tecnico_ok(d, r)
        if p:
            malas.append((os.path.basename(d), p))
            continue
        runs.append({"dir": os.path.basename(d), "res": r})
    return runs, malas


def tasa(runs: list[dict], precio: int) -> tuple[int, int]:
    """k, n sobre agentes expuestos a ese precio. Misma definicion que confirmatorio.tasa_por_precio."""
    k = n = 0
    for c in runs:
        for a in (c["res"].get("agentes") or {}).values():
            if a.get("precio_depositar") == precio:
                n += 1
                k += 1 if a.get("deposito_clave") else 0
    return k, n


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | tuple[None, None]:
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(100 * (c - m), 1), round(100 * (c + m), 1))


def bootstrap_dif(runs0: list[dict], runs5: list[dict]) -> list[float]:
    """Intervalo del contraste, remuestreando CORRIDAS dentro de cada brazo."""
    rnd = random.Random(SEMILLA)
    difs = []
    for _ in range(REMUESTREOS):
        b0 = [runs0[rnd.randrange(len(runs0))] for _ in runs0]
        b5 = [runs5[rnd.randrange(len(runs5))] for _ in runs5]
        k0, n0 = tasa(b0, 0)
        k5, n5 = tasa(b5, 5)
        if n0 and n5:
            difs.append(k0 / n0 - k5 / n5)
    difs.sort()
    return difs


def lectura(runs0: list[dict], runs5: list[dict], etiqueta: str) -> dict:
    k0, n0 = tasa(runs0, 0)
    k5, n5 = tasa(runs5, 5)
    difs = bootstrap_dif(runs0, runs5)
    lo = difs[int(0.025 * len(difs))]
    hi = difs[min(len(difs) - 1, int(0.975 * len(difs)))]
    dif = (k0 / n0 - k5 / n5) if (n0 and n5) else None
    return {
        "lectura": etiqueta,
        "corridas_cero": len(runs0),
        "corridas_pagadas": len(runs5),
        "precio_0": {"k": k0, "n": n0, "tasa": round(100 * k0 / n0, 1) if n0 else None,
                     "ic95_wilson": wilson(k0, n0)},
        "precio_5": {"k": k5, "n": n5, "tasa": round(100 * k5 / n5, 1) if n5 else None,
                     "ic95_wilson": wilson(k5, n5)},
        "diferencia_0_menos_5": round(dif, 4) if dif is not None else None,
        "ic95_bootstrap": [round(lo, 4), round(hi, 4)],
        "incluye_cero": bool(lo <= 0 <= hi),
        "unidad": "agente expuesto al precio",
        "metodo_intervalo": f"bootstrap por conglomerado (remuestreo de corridas), {REMUESTREOS} replicas, "
                            f"semilla {SEMILLA}, percentiles 2,5 y 97,5",
    }


def main() -> None:
    runs_lote, malas_lote = cargar_lote()
    runs_cero, malas_cero = cargar_cero()
    print(f"  lote: {len(runs_lote)} corridas cargadas del acta" + (f", {len(malas_lote)} descartadas" if malas_lote else ""))
    for n, p in malas_lote:
        print(f"    DESCARTADA {n[:15]}: {p}")
    print(f"  control: {len(runs_cero)} corridas" + (f", {len(malas_cero)} descartadas" if malas_cero else ""))
    for n, p in malas_cero:
        print(f"    DESCARTADA {n[:15]}: {p}")

    # la mirada congelada: las primeras 70 del acta (por hora), que es como se fijo el primario
    congelada = lectura(runs_cero, runs_lote[:70], "mirada congelada (70 + 8)")
    # la extension de precision
    precision = lectura(runs_cero, runs_lote, f"extension de precision ({len(runs_lote)} + 8)")

    acta = json.load(open(ACTA, encoding="utf-8"))
    out = {
        "que_es": "contraste descriptivo entre escenas: control sin costo contra precio 5",
        "no_es": "no es el primario; el primario pareado 20 vs 5 no se recalcula aqui",
        "fijado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hash_escena_lote": ESCENA_LOTE,
        "hash_escena_cero": ESCENA_CERO,
        "sha256_del_conjunto": acta.get("sha256_de_la_lista"),
        "remuestreos": REMUESTREOS,
        "semilla": SEMILLA,
        "congelada": congelada,
        "precision": precision,
    }
    json.dump(out, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n  escrito {os.path.relpath(SALIDA, RAIZ)}")
    for lect in (congelada, precision):
        print(f"\n  {lect['lectura']}")
        print(f"    precio 0: {lect['precio_0']['tasa']}% ({lect['precio_0']['k']}/{lect['precio_0']['n']}) "
              f"IC {lect['precio_0']['ic95_wilson']}")
        print(f"    precio 5: {lect['precio_5']['tasa']}% ({lect['precio_5']['k']}/{lect['precio_5']['n']}) "
              f"IC {lect['precio_5']['ic95_wilson']}")
        print(f"    0 menos 5: {lect['diferencia_0_menos_5']:+.3f}  IC {lect['ic95_bootstrap']}  "
              f"{'INCLUYE CERO' if lect['incluye_cero'] else 'EXCLUYE CERO'}")


if __name__ == "__main__":
    main()
