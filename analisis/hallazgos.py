#!/usr/bin/env python3
"""Busca aportes para el sprint en datos que el analisis congelado NO toca.

Cuatro preguntas nuevas, todas sobre el conjunto congelado (reportes/conjunto-congelado.json):
  1. SUSTITUCION: ¿los que entregaron la clave renunciaron a su tarea propia? (tarea_correcta, puntaje)
  2. CLUSTERING: ¿la cooperacion se agrupa por corrida mas de lo que el azar explica? (permutaciones
     del deposito DENTRO de la corrida: la asignacion de precios es fija, se permuta quien deposita)
  3. TOMAR-AYUDAR: ¿el que reclamo la reserva ayudo o desplazo la ayuda? (rec x abs, ya deduplicado)
  4. APRENDIZAJE: ¿la tasa cambia con la ronda? (con el fondo intacto vs agotado por ronda)

No recalcula nada congelado; escribe reportes/hallazgos.json con todo lo que encuentre.
"""
from __future__ import annotations

import glob
import json
import os
import random
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTA = os.path.join(RAIZ, "reportes", "conjunto-congelado.json")
SALIDA = os.path.join(RAIZ, "reportes", "hallazgos.json")
SEMILLA = 20260913
PERMUTACIONES = 20000


def cargar_lote():
    acta = json.load(open(ACTA, encoding="utf-8"))
    out = []
    for c in acta["corridas"]:
        d = os.path.join(RAIZ, "salidas", c["corrida"])
        f = os.path.join(d, "resumen.json")
        if not os.path.exists(f):
            continue
        r = json.load(open(f, encoding="utf-8"))
        out.append({"dir": c["corrida"], "res": r})
    return out, acta


def agentes(run):
    return list(run["res"]["agentes"].values())


# ---------- 1. sustitucion ----------

def sustitucion(lote):
    """
    La pregunta del sprint es si los agentes sacrifican presupuesto PROPIO para ayudar. La version
    mas dura de ese sacrificio es la sustitucion: ¿dejo de hacer su tarea para pagar la ayuda?
    Se comparan los que entregaron la clave contra los que no, DENTRO del mismo precio.
    """
    filas = []
    for run in lote:
        for a in agentes(run):
            filas.append({"precio": a["precio_depositar"], "ayudo": bool(a["deposito_clave"]),
                          "tarea": bool(a.get("tarea_correcta")), "puntaje": a.get("puntaje") or 0})
    out = {}
    for p in (5, 20):
        g = [f for f in filas if f["precio"] == p]
        ay = [f for f in g if f["ayudo"]]
        no = [f for f in g if not f["ayudo"]]
        out[str(p)] = {
            "n_ayudo": len(ay), "n_no": len(no),
            "tarea_ayudo": round(100 * sum(f["tarea"] for f in ay) / len(ay), 1) if ay else None,
            "tasa_tarea_ayudo": round(100 * sum(f["tarea"] for f in ay) / len(ay), 1) if ay else None,
            "tarea_no": round(100 * sum(f["tarea"] for f in no) / len(no), 1) if no else None,
            "puntaje_ayudo": round(sum(f["puntaje"] for f in ay) / len(ay), 2) if ay else None,
            "puntaje_no": round(sum(f["puntaje"] for f in no) / len(no), 2) if no else None,
            "diferencia_tarea": (round(100 * sum(f["tarea"] for f in ay) / len(ay) - 100 * sum(f["tarea"] for f in no) / len(no), 1)
                                 if ay and no else None),
            "diferencia_puntaje": (round(sum(f["puntaje"] for f in ay) / len(ay) - sum(f["puntaje"] for f in no) / len(no), 2)
                                   if ay and no else None),
        }
    # bootstrap pareado por corrida para la diferencia de tarea (conglomerado: corridas)
    rnd = random.Random(SEMILLA)
    difs = []
    for run in lote:
        ay = [a for a in agentes(run) if a["deposito_clave"]]
        no = [a for a in agentes(run) if not a["deposito_clave"]]
        if ay and no:
            difs.append(sum(bool(a.get("tarea_correcta")) for a in ay) / len(ay)
                        - sum(bool(a.get("tarea_correcta")) for a in no) / len(no))
    if difs:
        boots = sorted(sum(difs[rnd.randrange(len(difs))] for _ in difs) / len(difs) for _ in range(10000))
        out["diferencia_tarea_pareada"] = {
            "media": round(sum(difs) / len(difs), 4),
            "ic95": [round(boots[250], 4), round(boots[9750], 4)],
            "incluye_cero": bool(boots[250] <= 0 <= boots[9750]),
        }
    return out


# ---------- 2. clustering ----------

def clustering(lote):
    """
    ¿La cooperacion es una propiedad del colectivo o de agentes individuales? Si en una corrida
    depositan MAS (o menos) de lo que sus precios predicen, hay un efecto de corrida: algo del
    entorno compartido (lo que ven en el almacen, lo que hacen los demas) mueve la ayuda.
    Se compara la DISPERSION entre corridas observada contra la esperada bajo independencia
    (permutando quien deposita dentro de cada precio, porque la asignacion de precios es fija).
    """
    obs = []
    for run in lote:
        for p in (5, 20):
            g = [a for a in agentes(run) if a["precio_depositar"] == p]
            if g:
                obs.append((p, sum(bool(a["deposito_clave"]) for a in g), len(g)))
    def varianza_de(pares):
        # varianza de la tasa por corrida-precio, ponderada por n (agente-expuesto)
        media = sum(k for p, k, n in pares) / sum(n for p, k, n in pares)
        num = sum(n * (k / n - media) ** 2 for p, k, n in pares)
        den = sum(n for p, k, n in pares) - 1
        return num / den if den > 0 else 0.0
    v_obs = varianza_de(obs)
    rnd = random.Random(SEMILLA)
    vueltas = []
    por_p = {}
    for p, k, n in obs:
        por_p.setdefault(p, []).append((k, n))
    for _ in range(PERMUTACIONES):
        perm = []
        for p, lst in por_p.items():
            tot_k = sum(k for k, n in lst)
            tot_n = sum(n for k, n in lst)
            # permutacion exacta: elegir que corridas de ese precio depositan, sin cambiar el total
            ks = [1] * tot_k + [0] * (tot_n - tot_k)
            rnd.shuffle(ks)
            i = 0
            for k, n in lst:
                perm.append((p, sum(ks[i:i + n]), n))
                i += n
        vueltas.append(varianza_de(perm))
    vueltas.sort()
    p_valor = sum(1 for v in vueltas if v >= v_obs) / len(vueltas)
    # el ICC simple: cuanto de la varianza total es entre corridas
    total_k = sum(k for p, k, n in obs); total_n = sum(n for p, k, n in obs)
    media_global = total_k / total_n
    return {
        "que_es": "dispersion de la tasa de ayuda entre corridas contra la esperada bajo independencia",
        "varianza_observada": round(v_obs, 6),
        "varianza_esperada_mediana": round(vueltas[len(vueltas) // 2], 6),
        "razon_obs_esperada": round(v_obs / vueltas[len(vueltas) // 2], 2) if vueltas[len(vueltas)//2] else None,
        "p_valor_permutacion": round(p_valor, 5),
        "media_global": round(100 * media_global, 1),
        "metodo": f"permutacion exacta de quien deposita dentro de cada precio, {PERMUTACIONES} vueltas, "
                  f"semilla {SEMILLA}; la asignacion de precios no se toca",
    }


# ---------- 3. tomar y ayudar ----------

def tomar_ayudar():
    """
    En las celdas con reserva (recl x abs y marco neutro), ¿el que reclamo la reserva ayudo MENOS?
    Ayer se encontro que los que toman tienen mas pasos libres. Aqui la pregunta es de desplazamiento:
    la ayuda y el saqueo del bien comun, en el mismo agente.
    """
    import glob as g
    CEL = {"rec+abs K=5": "dd9086e2", "rec+abs K=20": "580e8ae0",
           "marco neutro K=5": None, "marco neutro K=20": None}
    # las celdas de marco neutro son las del 2x2 CON marco (pedido neutro + reserva); ojo: emparejar
    # por nombre EXACTO de escena — 'abstencion-sola' como substring tambien casa con
    # 'abstencion-sola-caro' y mezcla celdas (bug corregido la primera version de este guion).
    NOMBRES = {"marco neutro K=5": ("factorial-abstencion",),
               "marco neutro K=20": ("factorial-abstencion-caro",)}
    out = {}
    for celda, pref in CEL.items():
        runs = []
        vistos = set()
        if pref:
            for raiz in ("/home/daw/Sprint", "/home/daw/Sprint-2"):
                for f in sorted(g.glob(os.path.join(raiz, "salidas", "2026*", "resumen.json"))):
                    d = os.path.dirname(f); nom = os.path.basename(d)
                    if nom in vistos: continue
                    try: r = json.load(open(f, encoding="utf-8"))
                    except Exception: continue
                    if not str(r.get("hash_escena") or "").startswith(pref): continue
                    vistos.add(nom)
                    ev_p = os.path.join(d, "eventos.jsonl")
                    if not os.path.exists(ev_p): continue
                    ev = [json.loads(x) for x in open(ev_p, encoding="utf-8") if x.strip()]
                    if any(e.get("tipo") == "tope_tokens" for e in ev): continue
                    runs.append(r)
        else:
            for nombre in NOMBRES[celda]:
                for raiz in ("/home/daw/Sprint", "/home/daw/Sprint-2"):
                    for f in sorted(g.glob(os.path.join(raiz, "salidas", "2026*", "resumen.json"))):
                        d = os.path.dirname(f); nom = os.path.basename(d)
                        if nom in vistos: continue
                        try: r = json.load(open(f, encoding="utf-8"))
                        except Exception: continue
                        if str(r.get("escena") or "") != nombre: continue
                        vistos.add(nom)
                        ev_p = os.path.join(d, "eventos.jsonl")
                        if not os.path.exists(ev_p): continue
                        ev = [json.loads(x) for x in open(ev_p, encoding="utf-8") if x.strip()]
                        if any(e.get("tipo") == "tope_tokens" for e in ev): continue
                        runs.append(r)
        tom_ay, tom_no, no_ay, no_no = 0, 0, 0, 0
        for r in runs:
            for a in (r.get("agentes") or {}).values():
                tomo = bool(a.get("reclamo"))
                ayudo = bool(a.get("deposito_clave"))
                if tomo and ayudo: tom_ay += 1
                elif tomo and not ayudo: tom_no += 1
                elif not tomo and ayudo: no_ay += 1
                else: no_no += 1
        n_t = tom_ay + tom_no; n_n = no_ay + no_no
        out[celda] = {
            "n_tomadores": n_t, "n_no_tomadores": n_n,
            "ayuda_de_quien_toma": round(100 * tom_ay / n_t, 1) if n_t else None,
            "ayuda_de_quien_no_toma": round(100 * no_ay / n_n, 1) if n_n else None,
            "diferencia": (round(100 * tom_ay / n_t - 100 * no_ay / n_n, 1) if n_t and n_n else None),
            "tabla": {"toma_y_ayuda": tom_ay, "toma_y_no_ayuda": tom_no,
                      "no_toma_y_ayuda": no_ay, "no_toma_y_no_ayuda": no_no},
        }
    return out


# ---------- 4. ronda por ronda ----------

def rondas(lote):
    """Cuando se deposita: por ronda y precio, con la ronda tomada de los EVENTOS (la fuente buena).

    La version anterior leia ronda_entrega del resumen y daba 25 depositos de ronda 1 en precio 5
    donde los eventos dan 76: el resumen deja la ronda nula en buena parte de los depositos por la
    via HTTP. Los eventos traen ronda siempre (verificado: cero depositos sin ronda).
    """
    from collections import Counter
    ent = {5: Counter(), 20: Counter()}
    for run in lote:
        d = os.path.join(RAIZ, "salidas", run["dir"])
        ev_p = os.path.join(d, "eventos.jsonl")
        if not os.path.exists(ev_p):
            continue
        ev = [json.loads(x) for x in open(ev_p, encoding="utf-8") if x.strip()]
        ronda_de = {}
        for e in ev:
            if str(e.get("tipo", "")).startswith("depositar") and e.get("agente"):
                ronda_de.setdefault(e["agente"], e.get("ronda"))
        for ag, a in run["res"]["agentes"].items():
            if a["precio_depositar"] not in ent or not a.get("deposito_clave"):
                continue
            rd = ronda_de.get(ag, a.get("ronda_entrega"))
            if rd is not None:
                ent[a["precio_depositar"]][int(rd)] += 1
    out = {}
    for p in ("5", "20"):
        tot = sum(ent[int(p)].values())
        out[p] = {str(r): ent[int(p)].get(r, 0) for r in (1, 2, 3, 4)}
        out[p]["total"] = tot
        out[p]["porcentaje_ronda_1"] = round(100 * ent[int(p)].get(1, 0) / tot, 1) if tot else None
    return out


def main() -> None:
    lote, acta = cargar_lote()
    print(f"  {len(lote)} corridas del acta")
    out = {"fijado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "sha256_del_conjunto": acta.get("sha256_de_la_lista"),
           "semilla": SEMILLA}
    print("\n  === 1. sustitucion: ¿ayudar cuesta la tarea propia? ===")
    s = sustitucion(lote)
    out["sustitucion"] = s
    for p in ("5", "20"):
        v = s[p]
        print(f"    precio {p}: tarea de quien ayudo {v['tarea_ayudo']}% ({v['n_ayudo']}) vs "
              f"quien no {v['tarea_no']}% ({v['n_no']}) | dif puntaje {v['diferencia_puntaje']}")
    d = s.get("diferencia_tarea_pareada")
    if d:
        print(f"    diferencia de tarea pareada por corrida: {100*d['media']:+.1f} pts "
              f"IC {100*d['ic95'][0]:+.1f} a {100*d['ic95'][1]:+.1f} "
              f"{'INCLUYE' if d['incluye_cero'] else 'EXCLUYE'} CERO")
    print("\n  === 2. clustering: ¿la ayuda es del colectivo? ===")
    c = clustering(lote)
    out["clustering"] = c
    print(f"    varianza observada {c['varianza_observada']} vs esperada {c['varianza_esperada_mediana']}"
          f" (razon {c['razon_obs_esperada']}x) | p={c['p_valor_permutacion']}")
    print("\n  === 3. tomar y ayudar en el mismo agente ===")
    t = tomar_ayudar()
    out["tomar_ayudar"] = t
    for celda, v in t.items():
        print(f"    {celda:18s} toma y ayuda {v['tabla']['toma_y_ayuda']:2d} | toma y no ayuda "
              f"{v['tabla']['toma_y_no_ayuda']:2d} | no toma y ayuda {v['tabla']['no_toma_y_ayuda']:3d}")
        if v["diferencia"] is not None:
            print(f"    {'':18s} ayuda: toman {v['ayuda_de_quien_toma']}% vs no toman {v['ayuda_de_quien_no_toma']}%"
                  f" -> dif {v['diferencia']:+.1f} pts")
    print("\n  === 4. en que ronda se deposita (por eventos) ===")
    rr = rondas(lote)
    out["rondas"] = rr
    for p in ("5", "20"):
        v = rr[p]
        print(f"    precio {p}: r1 {v['1']} | r2 {v['2']} | r3 {v['3']} | r4 {v['4']} | "
              f"total {v['total']} | ronda 1: {v['porcentaje_ronda_1']}% de los depositos")
    json.dump(out, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n  escrito {os.path.relpath(SALIDA, RAIZ)}")


if __name__ == "__main__":
    main()
