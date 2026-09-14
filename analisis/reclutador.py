"""Brazos de RECLUTADOR sobre el lado de dar: ¿cambia la tasa de entrega cuando quien pide no pide
para sí, sino por un tercero? Es el mecanismo del incidente (un agente pide el sacrificio de otro
invocando a un beneficiario ausente), medido con costo real.

Dos brazos de reclutador, ambos con el MISMO factorial de precio dentro de la corrida (5 y 20):
  tercero    `factorial-reclutador`             pide por "la estación 4" (R1a, tercero neutral)
  par        `factorial-reclutador-par-arbol2`  pide por un par del propio grupo (R1c)

El base (`factorial-base`) **no se recalcula aquí**. Es el lote confirmatorio y volver a computar sus
celdas a precio 5 y 20 con las corridas de ahora sería una mirada nueva al contraste preregistrado,
que se mira una sola vez. Se citan las tasas de la mirada ya hecha, tal como quedaron en
`reportes/confirmatorio.json` (N=70), como referencia **descriptiva**: la comparación
reclutador-contra-base sin intervalo conjunto, porque ese archivo no guarda tasas por corrida. Para
darle intervalo hace falta que el dueño de las corridas entregue las tasas por corrida del conjunto
congelado; queda pedido y anotado en la salida.

Reglas que respeta:
  - Desenlace = entrega de la clave (`deposito_clave`), igual que el confirmatorio.
  - Mismas exclusiones técnicas que `agregar.py`: sin resumen, ≠6 agentes, saldo negativo, truncada,
    sin estímulo.
  - `hash_textos` igual en los dos brazos (misma tarea; se verifica). `hash_escena` distinto por
    diseño y ÚNICO dentro de cada brazo (se verifica: si no, el brazo se parte y no se junta).
  - Intervalos por **remuestreo de corridas**, nunca de agentes, y ninguno por debajo de 3 corridas.
  - NO recalcula ninguna celda del base: ver arriba.

Uso:  python3 analisis/reclutador.py [--remuestreos 10000]
Salida: reportes/reclutador.json + tabla por consola
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HASH_TAREA = "4e8f2619ed0966ec"
MIN_CORRIDAS = 3
PRECIOS = (5, 20)

BRAZOS = {
    "tercero": "factorial-reclutador",
    "par":     "factorial-reclutador-par-arbol2",
}


def bootstrap(vals: list[float], remuestreos: int, semilla: int = 20260913) -> list[float] | None:
    if len(vals) < MIN_CORRIDAS:
        return None
    rnd = random.Random(semilla)
    m = sorted(sum(rnd.choice(vals) for _ in vals) / len(vals) for _ in range(remuestreos))
    return [round(m[int(0.025 * remuestreos)], 4), round(m[int(0.975 * remuestreos)], 4)]


def dif_por_corrida(a: list[float], b: list[float], remuestreos: int,
                    semilla: int = 20260913) -> dict:
    """a − b entre brazos independientes, remuestreando corridas en cada brazo."""
    if len(a) < MIN_CORRIDAS or len(b) < MIN_CORRIDAS:
        return {"media": (round(sum(a) / len(a) - sum(b) / len(b), 4) if a and b else None),
                "ic95": None, "incluye_cero": None,
                "insuficiente": f"n={len(a)} vs n={len(b)}; se requieren {MIN_CORRIDAS} por brazo"}
    rnd = random.Random(semilla)
    d = sorted((sum(rnd.choice(a) for _ in a) / len(a)) - (sum(rnd.choice(b) for _ in b) / len(b))
               for _ in range(remuestreos))
    lo, hi = d[int(0.025 * remuestreos)], d[int(0.975 * remuestreos)]
    return {"media": round(sum(a) / len(a) - sum(b) / len(b), 4),
            "ic95": [round(lo, 4), round(hi, 4)], "incluye_cero": lo <= 0 <= hi}


def cargar(fam: str) -> tuple[list[dict], list[str], set[str]]:
    validas, excl, escenas = [], [], set()
    for d in sorted(glob.glob(os.path.join(RAIZ, "salidas", f"*_{fam}/"))):
        nom = os.path.basename(d.rstrip("/"))
        rp = os.path.join(d, "resumen.json")
        if not os.path.exists(rp):
            excl.append(f"{nom[9:15]}: sin resumen"); continue
        r = json.load(open(rp, encoding="utf-8"))
        ev = [json.loads(l) for l in open(os.path.join(d, "eventos.jsonl"), encoding="utf-8")]
        prob = []
        ags = r.get("agentes") or {}
        if len(ags) != 6:
            prob.append(f"{len(ags)} agentes")
        bp = os.path.join(d, "presupuesto.json")
        if os.path.exists(bp):
            lib = json.load(open(bp, encoding="utf-8"))
            if [x for x, v in lib.get("restante", {}).items() if v < 0]:
                prob.append("saldo negativo")
        if any(e["tipo"] == "tope_tokens" for e in ev):
            prob.append("truncada")
        if not any(x.get("via") == "confederado" for x in r.get("depositos", [])):
            prob.append("sin estímulo")
        if r.get("hash_textos") != HASH_TAREA:
            prob.append(f"tarea {str(r.get('hash_textos'))[:8]} ≠ lote")
        if prob:
            excl.append(f"{nom[9:15]}: {', '.join(prob)}"); continue
        escenas.add(r.get("hash_escena", "?"))
        # tasa por corrida SEPARADA por precio: el factorial vive dentro de la corrida
        por_precio = {}
        for p in PRECIOS:
            sub = [a for a in ags.values() if a.get("precio_depositar") == p]
            if sub:
                por_precio[p] = {"k": sum(1 for a in sub if a.get("deposito_clave")),
                                 "n": len(sub)}
        validas.append({"corrida": nom, "por_precio": por_precio,
                        "tareas_ok": sum(1 for a in ags.values() if a.get("tarea_correcta")),
                        "agentes": len(ags)})
    return validas, excl, escenas


def celdas(v: list[dict], remuestreos: int) -> dict:
    out = {}
    for p in PRECIOS:
        tasas = [c["por_precio"][p]["k"] / c["por_precio"][p]["n"]
                 for c in v if p in c["por_precio"]]
        if not tasas:
            out[str(p)] = {"corridas": 0}; continue
        k = sum(c["por_precio"][p]["k"] for c in v if p in c["por_precio"])
        n = sum(c["por_precio"][p]["n"] for c in v if p in c["por_precio"])
        out[str(p)] = {"corridas": len(tasas), "agentes": n, "entregaron": k,
                       "tasa": round(sum(tasas) / len(tasas), 4),
                       "ic95_por_corrida": bootstrap(tasas, remuestreos),
                       "tasas_por_corrida": [round(t, 3) for t in tasas]}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remuestreos", type=int, default=10000)
    a = ap.parse_args()

    datos, out = {}, {"brazos": {}, "contrastes": {}, "notas": []}
    for et, fam in BRAZOS.items():
        v, excl, esc = cargar(fam)
        datos[et] = v
        out["brazos"][et] = {
            "familia": fam, "corridas_validas": len(v), "excluidas": len(excl),
            "hash_escena": sorted(esc)[0] if len(esc) == 1 else sorted(esc),
            "celdas": celdas(v, a.remuestreos),
            "tareas_completadas": (round(sum(c["tareas_ok"] for c in v)
                                         / sum(c["agentes"] for c in v), 3) if v else None),
            "detalle_excluidas": excl,
        }
        if len(esc) > 1:
            out["notas"].append(f"{et}: {len(esc)} hash_escena distintos — brazo no homogéneo")

    # contraste inferencial: par contra tercero. Los dos son exploratorios y no tocan el
    # confirmatorio, así que aquí sí va intervalo por remuestreo de corridas.
    for p in PRECIOS:
        A = [c["por_precio"][p]["k"] / c["por_precio"][p]["n"]
             for c in datos["par"] if p in c["por_precio"]]
        B = [c["por_precio"][p]["k"] / c["por_precio"][p]["n"]
             for c in datos["tercero"] if p in c["por_precio"]]
        out["contrastes"][f"par_menos_tercero_precio{p}"] = dif_por_corrida(A, B, a.remuestreos)

    # referencia descriptiva: las tasas del base tal como quedaron en la mirada única
    ref = os.path.join(RAIZ, "reportes", "confirmatorio.json")
    if os.path.exists(ref):
        c = json.load(open(ref, encoding="utf-8"))
        out["base_referencia"] = {
            "fuente": "reportes/confirmatorio.json (mirada única, no recalculada aquí)",
            "corridas": c.get("validez", {}).get("corridas_lote"),
            # ese archivo guarda las tasas en POR CIENTO; aquí todo va en fracción
            "tasas": {p: round(c["tasas"][p]["tasa"] / 100.0, 4)
                      for p in ("5", "20") if p in c.get("tasas", {})},
            "unidades": "fracción (el origen las guarda en por ciento y aquí se dividen por 100)",
            "sin_intervalo_conjunto": "ese archivo no guarda tasas por corrida; para dar intervalo a "
                                      "reclutador−base hacen falta las tasas por corrida del "
                                      "conjunto congelado",
        }
        for et in ("tercero", "par"):
            for p in ("5", "20"):
                cel = out["brazos"][et]["celdas"].get(p, {})
                if cel.get("corridas") and p in out["base_referencia"]["tasas"]:
                    out["contrastes"][f"{et}_menos_base_precio{p}_DESCRIPTIVO"] = {
                        "media": round(cel["tasa"] - out["base_referencia"]["tasas"][p], 4),
                        "ic95": None, "incluye_cero": None,
                        "insuficiente": "descriptivo: el base no se recalcula (confirmatorio)"}
    out["notas"].append("El base NO se recalcula en este guion: es el lote confirmatorio y sus celdas "
                        "a precio 5 y 20 sólo se miran en el congelado. Lo que aquí lleva intervalo es "
                        "par−tercero, que es exploratorio de punta a punta.")
    os.makedirs(os.path.join(RAIZ, "reportes"), exist_ok=True)
    json.dump(out, open(os.path.join(RAIZ, "reportes", "reclutador.json"), "w"),
              ensure_ascii=False, indent=2)

    print("=== reclutador: tasa de entrega de la clave, por precio ===")
    print(f"{'brazo':10s} {'corridas':>8s}  {'precio 5':>22s}  {'precio 20':>22s}")
    for et in ("tercero", "par"):
        b = out["brazos"][et]
        def cel(p):
            c = b["celdas"].get(str(p), {})
            if not c.get("corridas"):
                return "sin corridas"
            ic = c["ic95_por_corrida"]
            return f"{100*c['tasa']:5.1f}% " + (f"[{100*ic[0]:.0f};{100*ic[1]:.0f}]" if ic else "(n<3)")
        print(f"{et:10s} {b['corridas_validas']:8d}  {cel(5):>22s}  {cel(20):>22s}")
    br = out.get("base_referencia")
    if br:
        t = br["tasas"]
        print(f"{'base(ref)':10s} {br['corridas']:8d}  "
              f"{100*t.get('5', 0):20.1f}%  {100*t.get('20', 0):20.1f}%"
              "   <- mirada única, NO recalculada")
    print("\n=== contrastes (por remuestreo de corridas) ===")
    for k, d in out["contrastes"].items():
        if d.get("insuficiente"):
            print(f"{k:32s} {100*d['media']:+6.1f} pts  sin intervalo ({d['insuficiente']})"
                  if d["media"] is not None else f"{k:32s} sin datos")
        else:
            print(f"{k:32s} {100*d['media']:+6.1f} pts  IC95 [{100*d['ic95'][0]:+.1f}; "
                  f"{100*d['ic95'][1]:+.1f}]  {'incluye cero' if d['incluye_cero'] else 'EXCLUYE cero'}")
    for n in out["notas"]:
        print(f"\nnota: {n}")
    print("\nescrito reportes/reclutador.json")


if __name__ == "__main__":
    main()
