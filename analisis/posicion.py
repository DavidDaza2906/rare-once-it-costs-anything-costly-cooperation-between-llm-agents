"""EFECTO DE POSICIÓN: el precio está asignado por índice de agente y nunca rota.

La escena del factorial reparte `precios: [5, 5, 5, 20, 20, 20]` por posición, de modo que en las 108
corridas examinadas **el agente-01/02/03 recibe siempre precio 5 y el 04/05/06 siempre precio 20**.
Por diseño, entonces, el factor de precio está perfectamente confundido con todo lo que viaje con el
índice: el puerto de egreso (8201+i), el directorio de trabajo, y el orden en cualquier recorrido que
el arnés haga por agentes. El pareado dentro de la corrida no arregla esto: **es** esto.

Los seis agentes son `autosuficiente` idénticos, sin partes ajenas visibles, así que el rol no varía.
Queda medir el resto empíricamente, y se puede: los brazos de **precio único** (0 y 1) y las escenas de
**abstención** (K uniforme dentro de la escena) tienen el precio o la tentación constante entre todos
los agentes. Cualquier diferencia entre el grupo bajo {01,02,03} y el alto {04,05,06} en esas escenas
es efecto de posición **con el tratamiento fijo**: una estimación directa del confundidor.

Dos desenlaces, dos lados del experimento:
  - DAR:   entrega de la clave (`deposito_clave`) en las escenas de precio único.
  - TOMAR: reclamo de la reserva (`reclamo`) en las seis celdas del 3x2, donde K es uniforme.

Si la posición mueve el desenlace con el tratamiento fijo, entonces el contraste 20−5 del factorial
mezcla precio con posición, y su signo puede estar cancelado. Este guion no corrige nada: cuantifica
el tamaño del problema para que el reporte lo declare con un número en lugar de una advertencia.

No gasta tokens. Solo lectura sobre `salidas/`.
Uso:  python3 analisis/posicion.py [--remuestreos 10000]
Salida: reportes/posicion.json
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import random

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEMILLA = 20260913
MIN_CORRIDAS = 3
BAJO = ("01", "02", "03")

# escenas con DAR y precio único entre agentes
DAR = {"precio 0": "factorial-costo-cero", "precio 1": "precio-uno",
       "par p5": "solicitante-par-p5", "externo p5": "solicitante-externo-p5"}
# celdas del 3x2 con TOMAR y K uniforme entre agentes (hash_escena -> etiqueta)
TOMAR = {
    "e2986e0dbfc1f0ed": "sin marco K=5",      "993800e755f7829c": "sin marco K=20",
    "f7687d942f54334f": "neutral K=5",        "58f40d59dfa5e1d3": "neutral K=20",
    "dd9086e2d38f3740": "reclutador K=5",     "580e8ae01e1b0ff9": "reclutador K=20",
}


def grupo(ag: str) -> str:
    return "bajo" if ag[-2:] in BAJO else "alto"


def boot_dif(a: list[float], b: list[float], res: int, semilla: int = SEMILLA) -> dict:
    """a − b pareado DENTRO de la corrida: los dos grupos viven en la misma corrida, así que se
    remuestrean corridas y en cada una se toma la diferencia. Es más ajustado que tratarlos como
    brazos independientes, y es lo correcto: comparten escena, confederado y reserva."""
    if len(a) < MIN_CORRIDAS:
        return {"puntos": None, "ic95": None, "incluye_cero": None, "n_corridas": len(a),
                "insuficiente": f"n={len(a)}"}
    difs = [x - y for x, y in zip(a, b)]
    rnd = random.Random(semilla)
    m = sorted(sum(rnd.choice(difs) for _ in difs) / len(difs) for _ in range(res))
    lo, hi = 100 * m[int(0.025 * res)], 100 * m[int(0.975 * res)]
    return {"puntos": round(100 * sum(difs) / len(difs), 1), "ic95": [round(lo, 1), round(hi, 1)],
            "incluye_cero": lo <= 0 <= hi, "n_corridas": len(difs),
            "difs_por_corrida": [round(100 * d, 1) for d in difs]}


def recorre(filtro, campo: str, res: int) -> dict | None:
    """filtro(resumen) -> bool. campo: 'deposito_clave' o 'reclamo'."""
    bajo, alto, tb, ta, nb, na = [], [], 0, 0, 0, 0
    usadas = []
    for d in sorted(glob.glob(os.path.join(RAIZ, "salidas", "2026*/"))):
        rp = os.path.join(d, "resumen.json")
        if not os.path.exists(rp):
            continue
        r = json.load(open(rp, encoding="utf-8"))
        ags = r.get("agentes") or {}
        if len(ags) != 6 or not filtro(r):
            continue
        ev_p = os.path.join(d, "eventos.jsonl")
        if os.path.exists(ev_p):
            ev = [json.loads(x) for x in open(ev_p, encoding="utf-8") if x.strip()]
            if any(e.get("tipo") == "tope_tokens" for e in ev):
                continue
        g = {"bajo": [0, 0], "alto": [0, 0]}
        for ag, a in ags.items():
            gr = grupo(ag)
            g[gr][1] += 1
            if a.get(campo):
                g[gr][0] += 1
        if g["bajo"][1] != 3 or g["alto"][1] != 3:
            continue
        bajo.append(g["bajo"][0] / 3); alto.append(g["alto"][0] / 3)
        tb += g["bajo"][0]; ta += g["alto"][0]; nb += 3; na += 3
        usadas.append(os.path.basename(d.rstrip("/")))
    if not bajo:
        return None
    return {"corridas": len(bajo),
            "bajo": {"k": tb, "n": nb, "tasa": round(100 * tb / nb, 1)},
            "alto": {"k": ta, "n": na, "tasa": round(100 * ta / na, 1)},
            "bajo_menos_alto": boot_dif(bajo, alto, res),
            "corridas_usadas": usadas}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remuestreos", type=int, default=10000)
    res = ap.parse_args().remuestreos

    out = {
        "problema": "el precio se asigna por posición y nunca rota: 01-03 siempre 5, 04-06 siempre 20 "
                    "en 108/108 corridas del factorial. El precio queda confundido con el índice "
                    "(puerto de egreso 8201+i, directorio, orden de recorrido). El pareado dentro de "
                    "la corrida no lo arregla: es exactamente el mismo contraste.",
        "estrategia": "estimar el efecto de posición donde el tratamiento es UNIFORME entre agentes: "
                      "brazos de precio único (dar) y celdas del 3x2 con K uniforme (tomar).",
        "grupos": {"bajo": "agente-01/02/03 (los que en el factorial llevan precio 5)",
                   "alto": "agente-04/05/06 (los que en el factorial llevan precio 20)"},
        "dar": {}, "tomar": {}, "semilla": SEMILLA, "remuestreos": res,
    }

    # DAR: se recorre por familia con glob directo (el nombre de carpeta es más fiable que el
    # campo `escena` del resumen) y sólo entran escenas donde el precio es el MISMO para los seis.
    for etq, fam in DAR.items():
        bajo, alto, tb, ta, nb, na, usadas = [], [], 0, 0, 0, 0, []
        for d in sorted(glob.glob(os.path.join(RAIZ, "salidas", f"*_{fam}/"))):
            rp = os.path.join(d, "resumen.json")
            if not os.path.exists(rp):
                continue
            r = json.load(open(rp, encoding="utf-8"))
            ags = r.get("agentes") or {}
            if len(ags) != 6 or r.get("hash_textos") != "4e8f2619ed0966ec":
                continue
            precios = {a.get("precio_depositar") for a in ags.values()}
            if len(precios) != 1:       # sólo escenas de precio ÚNICO
                continue
            ev = [json.loads(x) for x in open(os.path.join(d, "eventos.jsonl"), encoding="utf-8")
                  if x.strip()]
            if any(e.get("tipo") == "tope_tokens" for e in ev):
                continue
            g = {"bajo": 0, "alto": 0}
            for ag, a in ags.items():
                if a.get("deposito_clave"):
                    g[grupo(ag)] += 1
            bajo.append(g["bajo"] / 3); alto.append(g["alto"] / 3)
            tb += g["bajo"]; ta += g["alto"]; nb += 3; na += 3
            usadas.append(os.path.basename(d.rstrip("/")))
        out["dar"][etq] = None if not bajo else {
            "corridas": len(bajo), "precio_uniforme": sorted(precios)[0],
            "bajo": {"k": tb, "n": nb, "tasa": round(100 * tb / nb, 1)},
            "alto": {"k": ta, "n": na, "tasa": round(100 * ta / na, 1)},
            "bajo_menos_alto": boot_dif(bajo, alto, res), "corridas_usadas": usadas}

    for h, etq in TOMAR.items():
        out["tomar"][etq] = recorre(lambda r, hh=h: r.get("hash_escena") == hh, "reclamo", res)

    # agregado: todas las corridas de precio único juntas (dar) y todas las celdas (tomar)
    def junta(seccion: str, campo: str) -> dict | None:
        difs, kb, ka, nb, na = [], 0, 0, 0, 0
        for v in out[seccion].values():
            if not v:
                continue
            d = v["bajo_menos_alto"].get("difs_por_corrida")
            if d:
                difs += [x / 100 for x in d]
            kb += v["bajo"]["k"]; ka += v["alto"]["k"]
            nb += v["bajo"]["n"]; na += v["alto"]["n"]
        if len(difs) < MIN_CORRIDAS:
            return None
        rnd = random.Random(SEMILLA)
        m = sorted(sum(rnd.choice(difs) for _ in difs) / len(difs) for _ in range(res))
        lo, hi = 100 * m[int(0.025 * res)], 100 * m[int(0.975 * res)]
        return {"corridas": len(difs), "bajo": round(100 * kb / nb, 1), "alto": round(100 * ka / na, 1),
                "bajo_menos_alto": round(100 * sum(difs) / len(difs), 1),
                "ic95": [round(lo, 1), round(hi, 1)], "incluye_cero": lo <= 0 <= hi,
                "aviso": "junta escenas distintas; vale como tamaño típico del confundidor, "
                         "no como estimación de un brazo"}
    out["agregado_dar"] = junta("dar", "deposito_clave")
    out["agregado_tomar"] = junta("tomar", "reclamo")

    out["lectura"] = (
        "Si el efecto de posición es distinto de cero y del orden de magnitud del efecto de precio "
        "buscado, el contraste 20−5 del factorial no se puede leer como efecto de precio: el grupo "
        "que lleva precio 20 es el mismo que lleva la posición alta, así que los dos efectos entran "
        "sumados y un resultado nulo puede ser cancelación. La solución de diseño es rotar el precio "
        "entre posiciones (contrabalanceo); no se puede aplicar a las corridas ya hechas y queda como "
        "limitación declarada y como el primer cambio del instrumento.")

    os.makedirs(os.path.join(RAIZ, "reportes"), exist_ok=True)
    dest = os.path.join(RAIZ, "reportes", "posicion.json")
    json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    def fila(etq, v):
        if not v:
            print(f"  {etq:20s} sin corridas"); return
        d = v["bajo_menos_alto"]
        ic = (f"[{d['ic95'][0]:+.1f}; {d['ic95'][1]:+.1f}] "
              f"{'incluye cero' if d['incluye_cero'] else 'EXCLUYE cero'}") if d["ic95"] else "sin IC (n<3)"
        bruto = 100 * (v['bajo']['k'] / v['bajo']['n'] - v['alto']['k'] / v['alto']['n'])
        dif = f"{d['puntos']:+6.1f}" if d["puntos"] is not None else f"{bruto:+6.1f}"
        print(f"  {etq:20s} bajo {v['bajo']['tasa']:5.1f}%  alto {v['alto']['tasa']:5.1f}%  "
              f"dif {dif} pts  {ic}   n={v['corridas']}")

    print("=== EFECTO DE POSICIÓN con el tratamiento uniforme ===")
    print("  (bajo = 01-03, los que en el factorial llevan precio 5; alto = 04-06, precio 20)")
    print("\n  DAR — entrega de la clave, escenas de precio único")
    for etq, v in out["dar"].items():
        fila(etq, v)
    print("\n  TOMAR — reclamo de la reserva, K uniforme en la escena")
    for etq, v in out["tomar"].items():
        fila(etq, v)
    for s, t in (("agregado_dar", "todas las de DAR"), ("agregado_tomar", "todas las de TOMAR")):
        a = out[s]
        if a:
            print(f"\n  {t}: bajo {a['bajo']}%  alto {a['alto']}%  dif {a['bajo_menos_alto']:+.1f} pts  "
                  f"IC95 [{a['ic95'][0]:+.1f}; {a['ic95'][1]:+.1f}]  "
                  f"{'incluye cero' if a['incluye_cero'] else 'EXCLUYE cero'}  ({a['corridas']} corridas)")
    print(f"\nescrito reportes/posicion.json  hash "
          f"{hashlib.sha256(open(dest, 'rb').read()).hexdigest()[:16]}")


if __name__ == "__main__":
    main()
