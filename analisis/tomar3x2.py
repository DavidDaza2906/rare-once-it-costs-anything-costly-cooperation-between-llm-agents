"""Lado de TOMAR como 3x2: marco del solicitante x tamaño de la tentación.

El acto costoso de estas escenas es **abstenerse**: hay 60 pasos en una reserva común, cualquiera
puede reclamar K pasos para sí, cada reclamo retira 2K de la reserva y lo que queda se reparte en
partes iguales entre los seis. Quien reclama absorbe sólo 2K/6 del daño, así que tomar **domina**:
neto +3,33 con K=5 y +13,33 con K=20. Abstenerse cuesta exactamente K.

Seis celdas, 8 corridas cada una, todas cerradas:

    marco               K=5                 K=20
    sin marco           e2986e0dbfc1f0ed    993800e755f7829c    (no hay confederado)
    marco neutral       f7687d942f54334f    58f40d59dfa5e1d3    (pide una clave para sí)
    marco reclutador    dd9086e2d38f3740    580e8ae01e1b0ff9    (pide por un tercero)

Qué añade este guion sobre `analisis/abstencion.py`, cuyas reglas de validez reproduce literalmente:
  1. la **tercera fila** (reclutador), que no estaba analizada;
  2. intervalo **por corrida** en cada celda, además del Wilson por agente que ya había: hay 48
     agentes por celda pero sólo 8 corridas independientes, y aquí la dependencia es estructural —
     el reclamo de un agente reduce el pago de los otros cinco —, así que el agente no es la unidad;
  3. los contrastes **guardados en disco**, no sólo impresos: `abstencion-2x2.json` no los lleva;
  4. la **interacción** propiamente dicha (diferencia de diferencias) con intervalo por corrida, que
     es la forma de poner a prueba la lectura "el marco le quita la sensibilidad al botín".

No gasta tokens y no escribe nada fuera de `reportes/`.
Uso:  python3 analisis/tomar3x2.py [--remuestreos 10000]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import random
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# El árbol 2 escribe en SU `salidas/`; se miran los dos y se deduplica por nombre de corrida.
RAICES = [RAIZ] + [r for r in ("/home/daw/Sprint-2",) if os.path.isdir(os.path.join(r, "salidas"))]
SEMILLA = 20260913
MIN_CORRIDAS = 3

MARCOS = ("sin marco", "marco neutral", "marco reclutador")
CELDAS = {
    ("sin marco", 5):        "e2986e0dbfc1f0ed",
    ("sin marco", 20):       "993800e755f7829c",
    ("marco neutral", 5):    "f7687d942f54334f",
    ("marco neutral", 20):   "58f40d59dfa5e1d3",
    ("marco reclutador", 5): "dd9086e2d38f3740",
    ("marco reclutador", 20): "580e8ae01e1b0ff9",
}


def wilson(k: int, n: int, z: float = 1.96) -> list[float] | None:
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(100 * (c - m), 1), round(100 * (c + m), 1)]


def boot(vals: list[float], res: int, semilla: int = SEMILLA) -> list[float] | None:
    """IC de una tasa por remuestreo de CORRIDAS. None por debajo de MIN_CORRIDAS: con muy pocas,
    el remuestreo devuelve un intervalo que parece precisión y sólo es falta de datos."""
    if len(vals) < MIN_CORRIDAS:
        return None
    rnd = random.Random(semilla)
    m = sorted(sum(rnd.choice(vals) for _ in vals) / len(vals) for _ in range(res))
    return [round(100 * m[int(0.025 * res)], 1), round(100 * m[int(0.975 * res)], 1)]


def boot_dif(a: list[float], b: list[float], res: int, semilla: int = SEMILLA) -> dict:
    """a − b, remuestreando corridas en cada brazo por separado."""
    if len(a) < MIN_CORRIDAS or len(b) < MIN_CORRIDAS:
        return {"puntos": None, "ic95": None, "incluye_cero": None,
                "insuficiente": f"n={len(a)} vs n={len(b)}"}
    rnd = random.Random(semilla)
    d = sorted((sum(rnd.choice(a) for _ in a) / len(a)) - (sum(rnd.choice(b) for _ in b) / len(b))
               for _ in range(res))
    lo, hi = 100 * d[int(0.025 * res)], 100 * d[int(0.975 * res)]
    return {"puntos": round(100 * (sum(a) / len(a) - sum(b) / len(b)), 1),
            "ic95": [round(lo, 1), round(hi, 1)], "incluye_cero": lo <= 0 <= hi}


def boot_interaccion(cels: dict, m1: str, m2: str, res: int, semilla: int = SEMILLA,
                    campo: str = "toma_por_corrida") -> dict:
    """Diferencia de diferencias: (K20−K5) bajo m1 menos (K20−K5) bajo m2, remuestreando las cuatro
    celdas por corrida. Es la prueba de "el marco cambia la sensibilidad al tamaño del botín"."""
    g = {(m, k): cels[(m, k)][campo] for m in (m1, m2) for k in (5, 20)}
    if any(len(v) < MIN_CORRIDAS for v in g.values()):
        return {"puntos": None, "ic95": None, "incluye_cero": None, "insuficiente": "celda con n<3"}
    rnd = random.Random(semilla)
    out = []
    for _ in range(res):
        r = {c: sum(rnd.choice(v) for _ in v) / len(v) for c, v in g.items()}
        out.append((r[(m1, 20)] - r[(m1, 5)]) - (r[(m2, 20)] - r[(m2, 5)]))
    out.sort()
    lo, hi = 100 * out[int(0.025 * res)], 100 * out[int(0.975 * res)]
    pend = {m: (sum(g[(m, 20)]) / len(g[(m, 20)])) - (sum(g[(m, 5)]) / len(g[(m, 5)]))
            for m in (m1, m2)}
    return {"puntos": round(100 * (pend[m1] - pend[m2]), 1),
            "ic95": [round(lo, 1), round(hi, 1)], "incluye_cero": lo <= 0 <= hi,
            f"pendiente_{m1.replace(' ', '_')}": round(100 * pend[m1], 1),
            f"pendiente_{m2.replace(' ', '_')}": round(100 * pend[m2], 1)}


def cargar(hash_escena: str, con_marco: bool) -> tuple[list[dict], list[str]]:
    """Mismas condiciones de entrada que `analisis/abstencion.py`, sin cambiar ninguna: cadena de
    hash íntegra, sin truncar, `puertos/` presente (sólo lo produce el arranque limpio, y sin él no
    se puede descartar herencia de estado), estímulo exigido en las celdas CON marco y su AUSENCIA
    exigida en las celdas SIN marco, y ningún reclamo aplicado sin comando del agente."""
    ok, excl, vistos = [], [], set()
    cands = []
    for raiz in RAICES:
        cands += glob.glob(os.path.join(raiz, "salidas", "2026*"))
    for d in sorted(cands, key=lambda x: os.path.basename(x.rstrip("/"))):
        if os.path.basename(d.rstrip("/")) in vistos:
            continue
        fr = os.path.join(d, "resumen.json")
        if not os.path.exists(fr):
            continue
        vistos.add(os.path.basename(d.rstrip("/")))
        r = json.load(open(fr, encoding="utf-8"))
        if r.get("hash_escena") != hash_escena:
            continue
        ev = [json.loads(x) for x in open(os.path.join(d, "eventos.jsonl"), encoding="utf-8")
              if x.strip()]
        prob = []
        if any(e["tipo"] == "tope_tokens" for e in ev):
            prob.append("truncada")
        if not all(b.get("prev") == a.get("hash") for a, b in zip(ev, ev[1:])):
            prob.append("cadena rota")
        hay = any(e.get("tipo") == "confederado" for e in ev)
        if con_marco and not hay:
            prob.append("sin estimulo en celda con marco")
        if not con_marco and hay:
            prob.append("estimulo presente en celda sin marco")
        if not os.path.isdir(os.path.join(d, "puertos")):
            prob.append("sin archivo de puertos")
        aplicados = {x.get("agente") for x in (r.get("reclamos") or [])}
        pidieron = {e.get("agente") for e in ev if re.search(r"/recl", str(e.get("tipo", "")))}
        huerf = sorted(a for a in (aplicados - pidieron) if a)
        if huerf:
            prob.append(f"reclamo sin comando ({', '.join(huerf)})")
        if prob:
            excl.append(f"{os.path.basename(d)[9:15]}: {'; '.join(prob)}")
            continue
        ok.append({"dir": os.path.basename(d), "res": r})
    return ok, excl


def resumen(runs: list[dict], res: int) -> dict:
    ag = tom = 0
    por_corrida, r1_por_corrida = [], []
    for c in runs:
        t = sum(1 for a in c["res"]["agentes"].values() if a.get("reclamo"))
        n = len(c["res"]["agentes"])
        ag += n; tom += t
        por_corrida.append(t / n)
        # RONDA 1: la reserva vale 60 en todas las celdas y nadie ha reclamado todavía, así que la
        # decisión de ronda 1 está libre del agotamiento del fondo. Ver §4 de validez-instrumento.md.
        r1_por_corrida.append(sum(1 for x in (c["res"].get("reclamos") or [])
                                  if x.get("ronda") == 1) / n)
    return {"corridas": len(runs), "agentes": ag, "tomaron": tom,
            "toma_ronda1": round(100 * sum(r1_por_corrida) / len(r1_por_corrida), 1) if r1_por_corrida else None,
            "toma_ronda1_por_corrida": r1_por_corrida,
            "tasa_toma": round(100 * tom / ag, 1) if ag else None,
            "abstencion": round(100 * (1 - tom / ag), 1) if ag else None,
            "ic95_por_corrida": boot(por_corrida, res),
            "ic95_wilson_por_agente": wilson(tom, ag),
            "toma_por_corrida": por_corrida,
            "corridas_usadas": [c["dir"] for c in runs]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remuestreos", type=int, default=10000)
    a = ap.parse_args()
    res = a.remuestreos

    cels, excluidas = {}, {}
    for (marco, k), h in CELDAS.items():
        runs, excl = cargar(h, marco != "sin marco")
        cels[(marco, k)] = resumen(runs, res)
        if excl:
            excluidas[f"{marco}|K={k}"] = excl

    salida = {
        "diseno": "3x2 — marco del solicitante (sin marco / neutral / reclutador) x tentación (K=5 / K=20)",
        "acto_medido": "reclamar la reserva (tomar). La abstención es su complemento.",
        "dominancia": {"K=5": "+3,33 pasos netos para quien reclama",
                       "K=20": "+13,33 pasos netos para quien reclama",
                       "nota": "tomar domina en las dos; abstenerse cuesta K"},
        "celdas": {}, "tentacion": {}, "marco": {}, "interaccion": {},
        "excluidas": excluidas, "semilla": SEMILLA, "remuestreos": res,
        "unidad_de_inferencia": "la corrida, no el agente: el reclamo de uno reduce el pago de los "
                                "otros cinco, así que los seis agentes de una corrida no son "
                                "observaciones independientes",
    }
    for (m, k), c in cels.items():
        salida["celdas"][f"{m}|K={k}"] = c

    # tentación: K=20 menos K=5 dentro de cada marco
    for m in MARCOS:
        salida["tentacion"][m] = boot_dif(cels[(m, 20)]["toma_por_corrida"],
                                         cels[(m, 5)]["toma_por_corrida"], res)
    # marco: cada par, a K fijo
    for k in (5, 20):
        for i, m1 in enumerate(MARCOS):
            for m2 in MARCOS[i + 1:]:
                salida["marco"][f"{m1} menos {m2} | K={k}"] = boot_dif(
                    cels[(m1, k)]["toma_por_corrida"], cels[(m2, k)]["toma_por_corrida"], res)
    # los MISMOS contrastes de marco, restringidos a la RONDA 1 (fondo intacto en todas las celdas).
    # Es la prueba de si el efecto de marco es marco o es agotamiento del fondo.
    salida["marco_solo_ronda1"] = {}
    for k in (5, 20):
        for i, m1 in enumerate(MARCOS):
            for m2 in MARCOS[i + 1:]:
                salida["marco_solo_ronda1"][f"{m1} menos {m2} | K={k}"] = boot_dif(
                    cels[(m1, k)]["toma_ronda1_por_corrida"],
                    cels[(m2, k)]["toma_ronda1_por_corrida"], res)
    # interacción: ¿cambia la pendiente en K según el marco? Se calcula DOS veces: sobre todas las
    # rondas y sobre la ronda 1. La primera hereda el agotamiento del fondo (validez-instrumento.md §4)
    # y puede producir una interacción que es artefacto; la de ronda 1 es la que decide.
    salida["interaccion_solo_ronda1"] = {}
    for i, m1 in enumerate(MARCOS):
        for m2 in MARCOS[i + 1:]:
            k = f"pendiente({m1}) menos pendiente({m2})"
            salida["interaccion"][k] = boot_interaccion(cels, m1, m2, res)
            salida["interaccion_solo_ronda1"][k] = boot_interaccion(
                cels, m1, m2, res, campo="toma_ronda1_por_corrida")

    os.makedirs(os.path.join(RAIZ, "reportes"), exist_ok=True)
    dest = os.path.join(RAIZ, "reportes", "tomar-3x2.json")
    json.dump(salida, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("=== toma de la reserva (3x2). Abstención = 100 − toma ===")
    print(f"  {'marco':17s} | {'K=5: toma [IC por corrida]':>30s} | {'K=20: toma [IC por corrida]':>30s}")
    for m in MARCOS:
        fila = []
        for k in (5, 20):
            c = cels[(m, k)]
            if not c["corridas"]:
                fila.append("sin corridas"); continue
            ic = c["ic95_por_corrida"]
            fila.append(f"{c['tasa_toma']:4.1f}% (r1 {c['toma_ronda1']:4.1f}%) "
                        + (f"[{ic[0]:.1f}; {ic[1]:.1f}]" if ic else "(n<3)"))
        print(f"  {m:17s} | {fila[0]:>30s} | {fila[1]:>30s}")

    print("\n=== TENTACIÓN (K=20 − K=5) dentro de cada marco ===")
    for m, d in salida["tentacion"].items():
        if d["puntos"] is None:
            print(f"  {m:17s} sin datos"); continue
        print(f"  {m:17s} {d['puntos']:+6.1f} pts  IC95 [{d['ic95'][0]:+.1f}; {d['ic95'][1]:+.1f}]  "
              f"{'incluye cero' if d['incluye_cero'] else 'EXCLUYE cero'}")

    print("\n=== MARCO, a tentación fija ===")
    for k, d in salida["marco"].items():
        if d["puntos"] is None:
            continue
        print(f"  {k:42s} {d['puntos']:+6.1f} pts  IC95 [{d['ic95'][0]:+.1f}; {d['ic95'][1]:+.1f}]  "
              f"{'incluye cero' if d['incluye_cero'] else 'EXCLUYE cero'}")

    print("\n=== MARCO, sólo RONDA 1 (fondo intacto: 60 en todas las celdas) ===")
    for k, d in salida["marco_solo_ronda1"].items():
        if d["puntos"] is None:
            continue
        print(f"  {k:42s} {d['puntos']:+6.1f} pts  IC95 [{d['ic95'][0]:+.1f}; {d['ic95'][1]:+.1f}]  "
              f"{'incluye cero' if d['incluye_cero'] else 'EXCLUYE cero'}")

    print("\n=== INTERACCIÓN sólo RONDA 1 (fondo intacto) — la que decide ===")
    for k, d in salida["interaccion_solo_ronda1"].items():
        if d["puntos"] is None:
            continue
        print(f"  {k:52s} {d['puntos']:+6.1f} pts  IC95 [{d['ic95'][0]:+.1f}; {d['ic95'][1]:+.1f}]  "
              f"{'incluye cero' if d['incluye_cero'] else 'EXCLUYE cero'}")

    print("\n=== INTERACCIÓN todas las rondas (hereda el agotamiento del fondo) ===")
    for k, d in salida["interaccion"].items():
        if d["puntos"] is None:
            continue
        print(f"  {k:52s} {d['puntos']:+6.1f} pts  IC95 [{d['ic95'][0]:+.1f}; {d['ic95'][1]:+.1f}]  "
              f"{'incluye cero' if d['incluye_cero'] else 'EXCLUYE cero'}")

    if excluidas:
        print("\n=== excluidas ===")
        for c, xs in excluidas.items():
            print(f"  {c}: {len(xs)} — {xs[:3]}")
    print(f"\nescrito reportes/tomar-3x2.json  hash "
          f"{hashlib.sha256(open(dest, 'rb').read()).hexdigest()[:16]}")


if __name__ == "__main__":
    main()
