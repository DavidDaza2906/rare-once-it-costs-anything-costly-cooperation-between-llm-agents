#!/usr/bin/env python3
"""La prueba restringida a la ronda 1: la que sostiene la nota metodologica del preregistro.

Por que existe. Sobre todas las rondas, el fondo se agota a medida que la partida avanza: el agente que
llega tarde juega con menos presupuesto que el que llego temprano, y eso mete el agotamiento del fondo
DENTRO de la medida. Restringir a la ronda 1 mide la decision con el fondo intacto. Si un efecto
aparece sobre todas las rondas y desaparece en la ronda 1, lo que se esta midiendo es el colapso del
fondo, no la decision.

Como se atribuye la ronda. El resumen del agente trae `ronda_entrega`, pero puede venir nulo cuando la
entrega entro por la via HTTP y la reconciliacion no dejo ronda. Por eso la fuente principal son los
EVENTOS: cada evento trae `ronda`, `agente` y `tipo`, y el deposito de la clave es un evento cuyo tipo
empieza por `depositar`. Se usa el evento y se cae al resumen solo si el evento no aparece.

Se calculan tres cosas, con la misma semilla y el mismo metodo de intervalo que confirmatorio.py:
  1. las tasas por precio restringidas a la ronda 1, comparadas con las de todas las rondas
  2. el contraste 0 menos 5 (descriptivo entre escenas) en las dos lecturas
  3. el primario pareado 20 menos 5 (dentro de la corrida) en las dos lecturas

No recalcula ni sobrescribe nada de lo congelado: escribe su propio archivo.
"""
from __future__ import annotations

import glob
import json
import os
import random
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESCENA_LOTE = "bf1b18a696a98476"
ESCENA_CERO = "47302f2c7c4bd21b"
ACTA = os.path.join(RAIZ, "reportes", "conjunto-congelado.json")
SALIDA = os.path.join(RAIZ, "reportes", "ronda-uno.json")
REMUESTREOS = 10000
SEMILLA = 20260913


def leer(d: str) -> dict | None:
    f = os.path.join(d, "resumen.json")
    if not os.path.exists(f):
        return None
    try:
        return json.load(open(f, encoding="utf-8"))
    except Exception:
        return None


def ronda_de_entrega(d: str, r: dict, agente: str) -> int | None:
    """La ronda en que ese agente entrego la clave. Los eventos mandan; el resumen es el respaldo."""
    ev_p = os.path.join(d, "eventos.jsonl")
    if os.path.exists(ev_p):
        for linea in open(ev_p, encoding="utf-8", errors="replace"):
            try:
                e = json.loads(linea)
            except Exception:
                continue
            if e.get("agente") != agente:
                continue
            if str(e.get("tipo", "")).startswith("depositar") and e.get("ronda") is not None:
                return int(e["ronda"])
    v = (r.get("agentes") or {}).get(agente, {}).get("ronda_entrega")
    return int(v) if v is not None else None


def cargar(rutas: list[str], hash_escena: str) -> list[dict]:
    """runs = [{'dir', 'por_agente': {agente: {'precio', 'clave', 'clave_r1'}}}]"""
    out = []
    for d in rutas:
        r = leer(d)
        if r is None or r.get("hash_escena") != hash_escena:
            continue
        por_agente = {}
        for ag, a in (r.get("agentes") or {}).items():
            entrego = bool(a.get("deposito_clave"))
            ronda = ronda_de_entrega(d, r, ag) if entrego else None
            por_agente[ag] = {"precio": a.get("precio_depositar"), "clave": entrego,
                              "clave_r1": entrego and ronda == 1}
        out.append({"dir": os.path.basename(d), "por_agente": por_agente})
    return out


def tasa(runs: list[dict], precio: int, solo_r1: bool) -> tuple[int, int]:
    k = n = 0
    for c in runs:
        for a in c["por_agente"].values():
            if a["precio"] != precio:
                continue
            n += 1
            k += 1 if (a["clave_r1"] if solo_r1 else a["clave"]) else 0
    return k, n


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(100 * (c - m), 1), round(100 * (c + m), 1))


def dif_por_corrida(runs: list[dict], solo_r1: bool) -> list[float]:
    difs = []
    for c in runs:
        v20 = [a for a in c["por_agente"].values() if a["precio"] == 20]
        v5 = [a for a in c["por_agente"].values() if a["precio"] == 5]
        if not v20 or not v5:
            continue
        k = "clave_r1" if solo_r1 else "clave"
        difs.append(sum(a[k] for a in v20) / len(v20) - sum(a[k] for a in v5) / len(v5))
    return difs


def bootstrap_media(difs: list[float], semilla: int = SEMILLA) -> list[float]:
    rnd = random.Random(semilla)
    return sorted(sum(difs[rnd.randrange(len(difs))] for _ in difs) / len(difs) for _ in range(REMUESTREOS))


def bootstrap_dif_escenas(runs0: list[dict], runs5: list[dict], solo_r1: bool) -> list[float]:
    rnd = random.Random(SEMILLA)
    difs = []
    for _ in range(REMUESTREOS):
        b0 = [runs0[rnd.randrange(len(runs0))] for _ in runs0]
        b5 = [runs5[rnd.randrange(len(runs5))] for _ in runs5]
        k0, n0 = tasa(b0, 0, solo_r1)
        k5, n5 = tasa(b5, 5, solo_r1)
        if n0 and n5:
            difs.append(k0 / n0 - k5 / n5)
    return sorted(difs)


def intervalo(difs: list[float]) -> list[float]:
    return [round(difs[int(0.025 * len(difs))], 4), round(difs[min(len(difs) - 1, int(0.975 * len(difs)))], 4)]


def main() -> None:
    acta = json.load(open(ACTA, encoding="utf-8"))
    rutas = [os.path.join(RAIZ, "salidas", c["corrida"]) for c in acta["corridas"]]
    lote = cargar(rutas, ESCENA_LOTE)
    cero = cargar(sorted(glob.glob(os.path.join(RAIZ, "salidas", "2026*"))), ESCENA_CERO)
    print(f"  lote: {len(lote)} corridas del acta | control: {len(cero)}")

    out = {"fijado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "que_es": "la misma analisis restringida a la ronda 1, con el fondo intacto",
           "hash_escena_lote": ESCENA_LOTE, "hash_escena_cero": ESCENA_CERO,
           "sha256_del_conjunto": acta.get("sha256_de_la_lista"),
           "remuestreos": REMUESTREOS, "semilla": SEMILLA, "lecturas": {}}

    for etiqueta, solo_r1 in (("todas las rondas", False), ("solo ronda 1", True)):
        tasas = {}
        for p in (0, 5, 20):
            k0, n0 = tasa(cero, p, solo_r1)
            k5, n5 = tasa(lote, p, solo_r1)
            k, n = (k0, n0) if p == 0 else (k5, n5)
            tasas[str(p)] = {"k": k, "n": n, "tasa": round(100 * k / n, 1) if n else None,
                             "ic95": wilson(k, n)}
        difs = dif_por_corrida(lote, solo_r1)
        icp = intervalo(bootstrap_media(difs))
        dif_esc = intervalo(bootstrap_dif_escenas(cero, lote, solo_r1))
        k0, n0 = tasa(cero, 0, solo_r1)
        k5, n5 = tasa(lote, 5, solo_r1)
        d_esc = (k0 / n0 - k5 / n5) if (n0 and n5) else None
        out["lecturas"][etiqueta] = {
            "tasas": tasas,
            "primario_pareado_20_menos_5": {"n_corridas": len(difs),
                                            "media": round(sum(difs) / len(difs), 4) if difs else None,
                                            "ic95_bootstrap": icp, "incluye_cero": bool(icp[0] <= 0 <= icp[1])},
            "0_menos_5": {"diferencia": round(d_esc, 4) if d_esc is not None else None,
                          "ic95_bootstrap": dif_esc, "incluye_cero": bool(dif_esc[0] <= 0 <= dif_esc[1])},
        }
        print(f"\n  === {etiqueta} ===")
        for p in ("0", "5", "20"):
            t = tasas[p]
            print(f"    precio {p:>2}: {t['tasa']}%  ({t['k']}/{t['n']})  IC {t['ic95']}")
        v = out["lecturas"][etiqueta]
        prim, cero5 = v["primario_pareado_20_menos_5"], v["0_menos_5"]
        print(f"    primario 20-5 pareado: {prim['media']:+.4f}  IC {prim['ic95_bootstrap']}  "
              f"{'INCLUYE CERO' if prim['incluye_cero'] else 'EXCLUYE CERO'}  ({prim['n_corridas']} corridas)")
        print(f"    0 menos 5            : {cero5['diferencia']:+.4f}  IC {cero5['ic95_bootstrap']}  "
              f"{'INCLUYE CERO' if cero5['incluye_cero'] else 'EXCLUYE CERO'}")

    json.dump(out, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n  escrito {os.path.relpath(SALIDA, RAIZ)}")
    a = out["lecturas"]["todas las rondas"]
    b = out["lecturas"]["solo ronda 1"]
    print(f"\n  el efecto sobre todas las rondas es "
          f"{a['primario_pareado_20_menos_5']['media']:+.4f} y en la ronda 1 "
          f"{b['primario_pareado_20_menos_5']['media']:+.4f}")


if __name__ == "__main__":
    main()
