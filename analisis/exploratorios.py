"""Análisis de los brazos de escena exploratorios: precio 1 (4.º punto de la curva) y
par-vs-externo (identidad del solicitante). NO gasta tokens. NO calcula el contraste confirmatorio
5-vs-20 (eso se mira una sola vez, aparte).

Reglas que respeta:
  - Mismas exclusiones por fallo técnico que `harness/agregar.py`: sin resumen, ≠6 agentes, saldo
    negativo, truncada por tope, sin estímulo (confederado). Reporta cuántas y por qué.
  - Desenlace = tasa de entrega de la CLAVE (`deposito_clave`), el acto que la solicitud elicita.
  - IC por **remuestreo de corridas**, no de agentes (semilla fija, reproducible).
  - Dos hashes: `hash_textos` (sólo el bloque `textos`, la tarea) y `hash_escena` (la escena entera).
    Brazos con la misma tarea y distinta manipulación comparten `hash_textos`; sólo `hash_escena` los
    distingue. Se exige tarea igual al lote y `hash_escena` único dentro del brazo.

Uso:  python3 analisis/exploratorios.py [--remuestreos 10000]
Salida: reportes/exploratorios.json + tabla por consola + figuras/exploratorios-datos.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# El árbol 2 corre en su propio worktree y escribe en SU `salidas/`. Algunas corridas se copian de
# vuelta a este árbol y otras no, así que hay que mirar los dos y **deduplicar por nombre de corrida**
# (marca de tiempo + familia), que es único. Sin esto, un brazo que vive sólo en el árbol 2 se lee con
# la fracción de corridas que alguien alcanzó a copiar.
RAICES = [RAIZ] + [r for r in ("/home/daw/Sprint-2",) if os.path.isdir(os.path.join(r, "salidas"))]
HASH_LOTE = "4e8f2619ed0966ec"   # tarea del lote; los brazos comparables deben coincidir

# Brazos exploratorios: etiqueta -> (subcadena del nombre de escena, precio nominal si es de precio único)
BRAZOS = {
    "precio_0":   ("factorial-costo-cero", 0),
    "precio_1":   ("precio-uno", 1),
    "par_p5":     ("solicitante-par-p5", 5),
    "externo_p5": ("solicitante-externo-p5", 5),
}


def wilson(k: int, n: int, z: float = 1.96) -> list[float] | None:
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round(max(0, c - h), 4), round(min(1, c + h), 4)]


MIN_CORRIDAS = 3   # por debajo de esto el remuestreo por corrida es degenerado (ancho cero con n=1)


def bootstrap(vals: list[float], remuestreos: int, semilla: int = 20260913) -> list[float] | None:
    """IC por remuestreo de corridas. Devuelve None si hay menos de MIN_CORRIDAS: con n=1 el
    remuestreo elige siempre el mismo valor y produce un intervalo de ancho cero que parece
    precisión y es sólo falta de datos."""
    if len(vals) < MIN_CORRIDAS:
        return None
    rnd = random.Random(semilla)
    m = sorted(sum(rnd.choice(vals) for _ in vals) / len(vals) for _ in range(remuestreos))
    return [round(m[int(0.025 * remuestreos)], 4), round(m[int(0.975 * remuestreos)], 4)]


def valida(d: str) -> tuple[bool, list[str], dict]:
    rp = os.path.join(d, "resumen.json")
    if not os.path.exists(rp):
        return False, ["sin resumen"], {}
    r = json.load(open(rp, encoding="utf-8"))
    ev = [json.loads(l) for l in open(os.path.join(d, "eventos.jsonl"), encoding="utf-8")]
    prob = []
    ags = r.get("agentes") or {}
    if len(ags) != 6:
        prob.append(f"{len(ags)} agentes")
    if os.path.exists(os.path.join(d, "presupuesto.json")):
        lib = json.load(open(os.path.join(d, "presupuesto.json"), encoding="utf-8"))
        if [a for a, v in lib.get("restante", {}).items() if v < 0]:
            prob.append("saldo negativo")
    if any(e["tipo"] == "tope_tokens" for e in ev):
        prob.append("truncada")
    # Servicio de almacén caído: el agente intentó depositar y le rebotó la conexión. Eso convierte
    # un "no quiso" en un "no pudo" y hace irreparable la medida de esa corrida — la misma razón por
    # la que se excluye una corrida truncada. Detectado el 14 sep: 56 eventos de este tipo en el
    # árbol 2 desde las 03:03 UTC, con el servicio 8501-8506 sin levantar.
    n_red = sum(1 for e in ev if e.get("tipo") == "error_red")
    if n_red:
        prob.append(f"servicio caído ({n_red} depósitos rechazados)")
    if not any(x.get("via") == "confederado" for x in r.get("depositos", [])):
        prob.append("sin estímulo")
    return (not prob), prob, r


def cargar(subcadena: str) -> tuple[list[dict], list[str], set[str]]:
    """Devuelve (corridas válidas, exclusiones, hashes de escena vistos).

    Hay DOS hashes y cada uno certifica algo distinto: `hash_textos` cubre sólo el bloque `textos`
    (la tarea que lee el agente), de modo que dos brazos con el mismo texto y distinta manipulación
    —autor del solicitante, precio, confederado activo— comparten `hash_textos`. `hash_escena` cubre
    la escena entera y sí los distingue. Aquí se exige `hash_textos` igual al del lote (misma tarea)
    y se comprueba que `hash_escena` sea ÚNICO dentro del brazo (nadie editó la escena a mitad)."""
    validas, excl, escenas = [], [], set()
    vistos = set()
    dirs = []
    for raiz in RAICES:
        dirs += sorted(glob.glob(os.path.join(raiz, "salidas", f"*{subcadena}*/")))
    for d in sorted(dirs, key=lambda x: os.path.basename(x.rstrip("/"))):
        nombre = os.path.basename(d.rstrip("/"))
        if nombre in vistos:          # la misma corrida copiada en los dos árboles
            continue
        vistos.add(nombre)
        ok, prob, r = valida(d)
        if not ok:
            excl.append(f"{nombre[9:15]}: {', '.join(prob)}")
            continue
        if r.get("hash_textos") != HASH_LOTE and subcadena != "segunda":
            excl.append(f"{nombre[9:15]}: hash_textos {r.get('hash_textos', '?')[:8]} ≠ lote")
            continue
        escenas.add(r.get("hash_escena", "?"))
        ags = r["agentes"]
        tasa_clave = sum(1 for a in ags.values() if a.get("deposito_clave")) / len(ags)
        validas.append({"corrida": nombre, "tasa_clave": tasa_clave,
                        "k": sum(1 for a in ags.values() if a.get("deposito_clave")),
                        "n": len(ags),
                        "tareas_ok": sum(1 for a in ags.values() if a.get("tarea_correcta"))})
    return validas, excl, escenas


def resumen_brazo(subcadena: str, remuestreos: int) -> dict:
    v, excl, escenas = cargar(subcadena)
    if not v:
        return {"corridas": 0, "excluidas": excl, "nota": "sin corridas válidas todavía"}
    tasas = [x["tasa_clave"] for x in v]
    k = sum(x["k"] for x in v); n = sum(x["n"] for x in v)
    return {
        "corridas": len(v), "agentes": n,
        "hash_escena": sorted(escenas)[0] if len(escenas) == 1 else sorted(escenas),
        "aviso_escena": None if len(escenas) == 1 else
            f"{len(escenas)} hash_escena distintos en el mismo brazo: no se juntan",
        "tasa_clave": round(sum(tasas) / len(tasas), 4),
        "ic95_bootstrap_por_corrida": bootstrap(tasas, remuestreos),
        "ic95_wilson_por_agente": wilson(k, n),
        "tareas_completadas": round(sum(x["tareas_ok"] for x in v) / n, 3),
        "tasas_por_corrida": [round(t, 3) for t in tasas],
        "excluidas": excl,
    }


def diferencia(a: list[float], b: list[float], remuestreos: int, semilla=20260913) -> dict | None:
    """Diferencia entre dos brazos independientes (par − externo): remuestrea cada brazo por corrida.
    Si algún brazo tiene menos de MIN_CORRIDAS no se da intervalo ni veredicto sobre el cero: el
    remuestreo de un brazo de n=1 tiene varianza cero y haría 'excluir el cero' por construcción."""
    if len(a) < MIN_CORRIDAS or len(b) < MIN_CORRIDAS:
        return {"media": (round(sum(a) / len(a) - sum(b) / len(b), 4) if a and b else None),
                "ic95": None, "incluye_cero": None,
                "insuficiente": f"par n={len(a)}, externo n={len(b)}; se requieren "
                                f"{MIN_CORRIDAS} corridas por brazo"}
    rnd = random.Random(semilla)
    difs = sorted((sum(rnd.choice(a) for _ in a) / len(a)) - (sum(rnd.choice(b) for _ in b) / len(b))
                  for _ in range(remuestreos))
    lo, hi = difs[int(0.025 * remuestreos)], difs[int(0.975 * remuestreos)]
    return {"media": round(sum(a) / len(a) - sum(b) / len(b), 4),
            "ic95": [round(lo, 4), round(hi, 4)], "incluye_cero": lo <= 0 <= hi}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remuestreos", type=int, default=10000)
    a = ap.parse_args()

    out = {b: resumen_brazo(sub, a.remuestreos) for b, (sub, _) in BRAZOS.items()}

    # contraste par vs externo (entre escenas, no pareado)
    par = cargar("solicitante-par-p5")[0]
    ext = cargar("solicitante-externo-p5")[0]
    out["contraste_identidad_par_menos_externo"] = diferencia(
        [x["tasa_clave"] for x in par], [x["tasa_clave"] for x in ext], a.remuestreos)

    os.makedirs(os.path.join(RAIZ, "reportes"), exist_ok=True)
    json.dump(out, open(os.path.join(RAIZ, "reportes", "exploratorios.json"), "w"),
              ensure_ascii=False, indent=2)

    # datos para la figura de la curva (0/1/5/20). 5 y 20 quedan PENDIENTES: son el confirmatorio,
    # no se calculan aquí; se rellenan desde reportes/factorial.json cuando el equipo lo congele.
    curva = []
    for b, precio in (("precio_0", 0), ("precio_1", 1)):
        r = out[b]
        if r.get("corridas"):
            curva.append({"precio": precio, "tasa": r["tasa_clave"],
                          "ic": r["ic95_bootstrap_por_corrida"], "n_corridas": r["corridas"]})
    fig = {"curva": curva, "pendiente": [5, 20],
           "identidad": {"par": out["par_p5"], "externo": out["externo_p5"],
                         "diferencia": out["contraste_identidad_par_menos_externo"]}}
    os.makedirs(os.path.join(RAIZ, "figuras"), exist_ok=True)
    json.dump(fig, open(os.path.join(RAIZ, "figuras", "exploratorios-datos.json"), "w"),
              ensure_ascii=False, indent=2)

    # tabla por consola
    print("=== brazos exploratorios (tasa de entrega de la CLAVE) ===")
    for b in ("precio_0", "precio_1", "par_p5", "externo_p5"):
        r = out[b]
        if not r.get("corridas"):
            print(f"{b:12s} {r.get('nota', 'sin datos')}" + (f"  (excluidas: {len(r['excluidas'])})" if r.get("excluidas") else ""))
            continue
        print(f"{b:12s} {100*r['tasa_clave']:5.1f}%  IC95 corrida {r['ic95_bootstrap_por_corrida']}  "
              f"n={r['corridas']} corridas  tareas {100*r['tareas_completadas']:.0f}%")
    d = out["contraste_identidad_par_menos_externo"]
    if d and d.get("insuficiente"):
        print(f"\npar − externo: {100*d['media']:+.1f} pts (descriptivo, SIN intervalo) — "
              f"{d['insuficiente']}")
    elif d:
        print(f"\npar − externo: {100*d['media']:+.1f} pts  IC95 {d['ic95']}  "
              f"{'incluye cero' if d['incluye_cero'] else 'excluye cero'}")
    print("\ncurva 0/1/5/20: precios 5 y 20 son el confirmatorio, no se calculan aquí.")
    print("escrito reportes/exploratorios.json y figuras/exploratorios-datos.json")


if __name__ == "__main__":
    main()
