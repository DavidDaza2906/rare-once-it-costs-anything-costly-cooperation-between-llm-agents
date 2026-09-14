"""Análisis descriptivo y de validez del factorial. No gasta tokens ni toca los puertos.

Cinco piezas que el plan pedía y no existían:

  Tabla 2       validez: corridas válidas, sin estímulo, cadenas íntegras, rechazos, tareas
  Supervivencia hasta el primer depósito de la CLAVE, por ronda y precio
  Contagio      depósito tras ver un depósito ajeno, comparado DENTRO de la ronda (orden por seq)
  ITT           cadena de saliencia: leyó el almacén -> leyó su clave -> mencionó la solicitud -> depositó
  Mediación     por capacidad sobrante: tarea completada x respuesta, y pasos sin gastar

Reglas que respeta:
  - Nunca mezcla versiones de instrumento: agrupa por `hash_escena` y descarta por defecto lo que no
    coincide con la escena vigente.
  - No calcula el contraste de precios (eso es `estimador.py`, al cierre). Este script describe.
  - La cadena de hashes del registro se verifica de verdad: cada evento encadena con el anterior.

Uso:
    python3 analisis/analisis_descriptivo.py  -> todo, sobre la escena vigente
    python3 analisis/analisis_descriptivo.py --json además escribe reportes/analisis.json
    python3 analisis/analisis_descriptivo.py --prueba autoprueba con datos sintéticos de efecto conocido
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os

def _raiz_del_proyecto() -> str:
    """Sube desde este archivo hasta encontrar el proyecto (escena.resuelta.json).

    Asi el guion funciona igual desde analisis/ que desde cualquier otro directorio.
    """
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d) and not os.path.exists(os.path.join(d, "escena.resuelta.json")):
        d = os.path.dirname(d)
    return d


RAIZ = _raiz_del_proyecto()
ETIQUETAS_DE_ENSAYO = ("ensayo", "prueba-de-instrumento", "pre-migracion")


def escena_vigente() -> dict:
    with open(os.path.join(RAIZ, "escena.resuelta.json"), encoding="utf-8") as fh:
        return json.load(fh)


def cargar(solo_vigente: bool = True) -> list[dict]:
    """Corridas con resumen, con eventos y transcripciones leídas aparte."""
    out = []
    for d in sorted(glob.glob(os.path.join(RAIZ, "salidas", "**", "resumen.json"), recursive=True)):
        carpeta = os.path.dirname(d)
        rel = os.path.relpath(carpeta, os.path.join(RAIZ, "salidas"))
        if any(x in rel for x in ETIQUETAS_DE_ENSAYO):
            continue
        try:
            res = json.load(open(d, encoding="utf-8"))
            ev = [json.loads(l) for l in open(os.path.join(carpeta, "eventos.jsonl"),
                                              encoding="utf-8") if l.strip()]
        except (OSError, json.JSONDecodeError):
            continue
        if len(res.get("agentes") or {}) != 6 or not ev:
            continue
        out.append({"rel": rel, "dir": carpeta, "res": res, "ev": ev,
                    "hash": res.get("hash_escena")})
    if solo_vigente:
        h = escena_vigente().get("hash_escena")
        out = [c for c in out if c["hash"] == h]
    return out


def cadena_integra(ev: list[dict]) -> bool:
    """Cada evento encadena con el anterior por hash; se verifica de verdad."""
    for a, b in zip(ev, ev[1:]):
        if b.get("prev") != a.get("hash"):
            return False
    return True


# ------------------------------------------------------------------ Tabla 2: validez
def tabla_validez(runs: list[dict]) -> dict:
    rech = tarea = agentes = integras = sin_estimulo = trunc = depositos = 0
    por_corrida = []
    for c in runs:
        ev, res = c["ev"], c["res"]
        solicitud = any("SOLICITUD" in str(x.get("texto", "")).upper()
                        for x in (res.get("depositos") or []))
        truncada = any(e["tipo"] == "tope_tokens" for e in ev)
        integra = cadena_integra(ev)
        r = sum(1 for e in ev if str(e["tipo"]).startswith("comando_rechazado"))
        t = sum(1 for a in res["agentes"].values() if a.get("tarea_correcta"))
        dep = [x for x in (res.get("depositos") or [])
               if x.get("agente") not in ("externo", "confederado")]
        por_corrida.append({"corrida": c["rel"], "tokens": res.get("tokens_totales"),
                            "tarea": t, "rechazos": r, "integra": integra,
                            "estimulo": solicitud, "truncada": truncada, "depositos": len(dep)})
        rech += r
        tarea += t
        agentes += 6
        integras += 1 if integra else 0
        sin_estimulo += 0 if solicitud else 1
        trunc += 1 if truncada else 0
        depositos += len(dep)
    return {"corridas": len(runs), "agentes": agentes, "tarea_completada": tarea,
            "rechazos": rech, "cadenas_integras": integras, "sin_estimulo": sin_estimulo,
            "truncadas": trunc, "depositos_de_agente": depositos, "por_corrida": por_corrida}


# ------------------------------------------------------- supervivencia (primer depósito)
def supervivencia(runs: list[dict]) -> dict:
    """Evento = depositar la clave. Riesgo por ronda y precio; censura al final."""
    rondas = max([c["res"].get("rondas") or 4 for c in runs] or [4])
    filas = collections.defaultdict(lambda: {"en_riesgo": 0, "eventos": 0})
    por_precio = collections.defaultdict(lambda: {"agentes": 0, "evento": 0, "rondas": {}})
    for c in runs:
        for ag, a in c["res"]["agentes"].items():
            precio = a.get("precio_depositar")
            clave = str(a.get("clave") or "")
            ronda_evento = None
            for x in (c["res"].get("depositos") or []):
                if x.get("agente") == ag and clave and clave in str(x.get("texto") or ""):
                    ronda_evento = x.get("ronda")
                    break
            por_precio[precio]["agentes"] += 1
            if ronda_evento:
                por_precio[precio]["evento"] += 1
            # riesgo: el agente está en riesgo desde la ronda 1 hasta la de su evento (o el final)
            for r in range(1, rondas + 1):
                if ronda_evento is None or r <= ronda_evento:
                    filas[(precio, r)]["en_riesgo"] += 1
                if ronda_evento == r:
                    filas[(precio, r)]["eventos"] += 1
    for (precio, r), v in sorted(filas.items()):
        por_precio[precio]["rondas"][r] = {
            "en_riesgo": v["en_riesgo"], "eventos": v["eventos"],
            "peligro": round(v["eventos"] / v["en_riesgo"], 4) if v["en_riesgo"] else None}
    return {"por_precio": {str(k): v for k, v in por_precio.items()},
            "rondas": rondas,
            "incidencia_acumulada": {str(p): round(v["evento"] / v["agentes"], 4)
                                     for p, v in por_precio.items() if v["agentes"]}}


# ------------------------------------------------------------------ contagio (dentro de ronda)
def contagio(runs: list[dict]) -> dict:
    """¿Sube el riesgo de depositar tras ver un depósito ajeno en la MISMA ronda?

    Se ordena por `seq` (orden global de la corrida). Cada depósito de la clave se clasifica según
    si antes, en la misma ronda, otro agente ya había depositado algo (visible en el almacén).
    La comparación es dentro de la ronda, así que no la puede fabricar el paso del tiempo.
    """
    cuentas = collections.defaultdict(lambda: {"con_ajeno": [0, 0], "sin_ajeno": [0, 0]})
    for c in runs:
        dep_ev = [e for e in c["ev"] if str(e["tipo"]).startswith("depositar")]
        clave_de = {ag: str(a.get("clave") or "") for ag, a in c["res"]["agentes"].items()}
        # evento de depósito -> ¿de quién y era la clave? (los depósitos del resumen van en orden)
        por_agente = collections.defaultdict(list)
        for x in (c["res"].get("depositos") or []):
            if x.get("agente") in clave_de:
                por_agente[x["agente"]].append(x)
        indice = collections.Counter()
        es_clave = {}
        for e in dep_ev:
            ag = e["agente"]
            lista = por_agente.get(ag, [])
            k = indice[ag]
            es_clave[e["seq"]] = bool(lista and k < len(lista)
                                      and clave_de[ag] and clave_de[ag] in str(lista[k].get("texto")))
            indice[ag] += 1
        for e in dep_ev:
            ronda = e.get("ronda")
            ajeno_antes = any(o["seq"] < e["seq"] and o.get("ronda") == ronda
                              and o["agente"] != e["agente"] for o in dep_ev)
            precio = c["res"]["agentes"][e["agente"]].get("precio_depositar")
            clave = 1 if es_clave.get(e["seq"]) else 0
            cubo = cuentas[precio]["con_ajeno" if ajeno_antes else "sin_ajeno"]
            cubo[1] += 1              # denominador: depósitos en esa condición
            cubo[0] += clave         # numerador: los que fueron la clave
    salida = {}
    for precio, v in sorted(cuentas.items(), key=lambda kv: (kv[0] is None, kv[0])):
        d = {}
        for cond, (k, n) in v.items():
            d[cond] = {"clave": k, "depositos": n, "tasa": round(k / n, 4) if n else None}
        salida[str(precio)] = d
    return salida


# ------------------------------------------------------------------- ITT: cadena de saliencia
def cadena_itt(runs: list[dict]) -> dict:
    """Etapas por agente, y tasas condicionales. La última etapa es el desenlace."""
    etapas = {"leyo_almacen": 0, "leyo_su_clave": 0, "menciono_solicitud": 0, "deposito_clave": 0}
    por_precio = collections.defaultdict(collections.Counter)
    trans = collections.Counter()
    trans_den = collections.Counter()
    for c in runs:
        for ag, a in c["res"]["agentes"].items():
            precio = a.get("precio_depositar")
            ev = [e for e in c["ev"] if e["agente"] == ag]
            leyo = any(e["tipo"] == "consulta" for e in ev)
            leyo_clave = any(str(e["tipo"]).startswith("comando")
                             and "verificacion.txt" in str(e["tipo"]) for e in ev)
            dep = bool(a.get("deposito_clave"))
            texto = ""
            for f in sorted(glob.glob(os.path.join(c["dir"], "transcripciones", f"*_{ag}.json"))):
                try:
                    x = json.load(open(f, encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                for m in (x if isinstance(x, list) else []):
                    if str(m.get("rol", "")).lower() in ("assistant", "asistente"):
                        texto += str(m.get("texto") or "")
            menciono = ("solicitud" in texto.lower() or "clave de verificacion" in texto.lower()
                        or "clave de verificación" in texto.lower())
            for k, v in (("leyo_almacen", leyo), ("leyo_su_clave", leyo_clave),
                         ("menciono_solicitud", menciono), ("deposito_clave", dep)):
                etapas[k] += 1 if v else 0
                if v:
                    por_precio[precio][k] += 1
            por_precio[precio]["agentes"] += 1
            # transiciones condicionales
            for (a1, v1), (a2, v2) in ((("leyo_almacen", leyo), ("leyo_su_clave", leyo_clave)),
                                       (("leyo_su_clave", leyo_clave), ("deposito_clave", dep)),
                                       (("leyo_almacen", leyo), ("deposito_clave", dep))):
                if v1:
                    trans_den[(a1, a2)] += 1
                    if v2:
                        trans[(a1, a2)] += 1
    return {"etapas": etapas,
            "por_precio": {str(k): dict(v) for k, v in por_precio.items()},
            "condicionales": {f"{a1}->{a2}": (round(trans[(a1, a2)] / trans_den[(a1, a2)], 4)
                                              if trans_den[(a1, a2)] else None)
                              for a1, a2 in trans_den}}


# -------------------------------------------------------------------- capacidad y mediación
def mediacion(runs: list[dict]) -> dict:
    cruce = collections.Counter()
    por_precio = collections.defaultdict(collections.Counter)
    sobrante = {"respondio": [], "no_respondio": []}
    for c in runs:
        for ag, a in c["res"]["agentes"].items():
            tarea = bool(a.get("tarea_correcta"))
            dep = bool(a.get("deposito_clave"))
            precio = a.get("precio_depositar")
            cruce[(tarea, dep)] += 1
            por_precio[precio][(tarea, dep)] += 1
            if a.get("pasos_restantes") is not None:
                sobrante["respondio" if dep else "no_respondio"].append(a["pasos_restantes"])
    def media(v):
        return round(sum(v) / len(v), 1) if v else None
    return {"cruce": {f"tarea={'ok' if t else 'no'}|responde={'si' if d else 'no'}": n
                      for (t, d), n in sorted(cruce.items())},
            "por_precio": {str(p): {f"tarea={'ok' if t else 'no'}|responde={'si' if d else 'no'}": n
                                    for (t, d), n in sorted(v.items())}
                           for p, v in sorted(por_precio.items())},
            "pasos_sin_gastar": {"respondio": media(sobrante["respondio"]),
                                 "no_respondio": media(sobrante["no_respondio"])}}


# ------------------------------------------------------------------------ autoprueba
def prueba() -> None:
    """Datos sintéticos con respuesta conocida: si el análisis miente, esto falla."""
    print("  autoprueba con datos sintéticos")
    # dos corridas a precio 5 y dos a 20; a precio 5 depositan 2 de 3, a 20 ninguno
    def corrida(precio, depositan, ronda=2):
        agentes = {}
        for i in range(1, 4):
            ag = f"agente-{i:02d}"
            agentes[ag] = {"precio_depositar": precio, "clave": f"V{i}", "tarea_correcta": True,
                           "deposito_clave": i in depositan, "pasos_restantes": 10}
        dep = [{"agente": f"agente-{i:02d}", "ronda": ronda, "texto": f"toma V{i}"}
               for i in depositan]
        ev = [{"tipo": "consulta", "agente": a, "ronda": 1, "seq": i, "hash": f"h{i}", "prev": None}
              for i, a in enumerate(agentes)]
        return {"rel": f"sintetica-p{precio}", "dir": "/tmp/inexistente", "hash": "X",
                "res": {"agentes": agentes, "depositos": dep, "hash_escena": "X",
                        "rondas": 4, "tokens_totales": 1000}, "ev": ev}
    runs = [corrida(5, {1, 2}), corrida(5, {1, 2}), corrida(20, set()), corrida(20, set())]
    s = supervivencia(runs)
    assert s["incidencia_acumulada"]["5"] == 0.6667, s["incidencia_acumulada"]
    assert s["incidencia_acumulada"]["20"] == 0.0, s["incidencia_acumulada"]
    print(f"    supervivencia: 5 -> {s['incidencia_acumulada']['5']}  20 -> {s['incidencia_acumulada']['20']}  OK")
    v = tabla_validez(runs)
    assert v["corridas"] == 4 and v["tarea_completada"] == 12 and v["depositos_de_agente"] == 4, v
    print(f"    validez: {v['corridas']} corridas, {v['tarea_completada']}/12 tareas, "
          f"{v['depositos_de_agente']} depósitos  OK")
    i = cadena_itt(runs)
    assert i["etapas"]["leyo_almacen"] == 12 and i["etapas"]["deposito_clave"] == 4, i["etapas"]
    print(f"    cadena ITT: {i['etapas']}  OK")
    m = mediacion(runs)
    assert m["cruce"]["tarea=ok|responde=si"] == 4, m["cruce"]
    print(f"    mediación: {m['cruce']}  OK")
    # un integrante de la cadena, roto a propósito, debe detectarse
    rota = [dict(e) for e in runs[0]["ev"]]
    rota[1]["prev"] = "no-coincide"
    assert not cadena_integra(rota)
    print("    integridad: cadena rota detectada  OK")
    print("  autoprueba verde")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    ap.add_argument("--todas", action="store_true", help="no filtrar por escena vigente")
    a = ap.parse_args()
    if a.prueba:
        prueba()
        return
    runs = cargar(solo_vigente=not a.todas)
    print(f"corridas en la escena vigente: {len(runs)}"
          f"  (hash {escena_vigente().get('hash_escena')})\n")
    if not runs:
        print("  sin corridas de la escena vigente todavía.")
        return
    v = tabla_validez(runs)
    print("=== Tabla 2: validez ===")
    print(f"  corridas {v['corridas']} | agentes {v['agentes']} | tareas {v['tarea_completada']}/{v['agentes']}"
          f" | cadenas íntegras {v['cadenas_integras']}/{v['corridas']}")
    print(f"  sin estímulo {v['sin_estimulo']} | truncadas {v['truncadas']}"
          f" | rechazos {v['rechazos']} | depósitos de agente {v['depositos_de_agente']}")
    s = supervivencia(runs)
    print("\n=== Supervivencia hasta depositar la clave ===")
    for precio, d in sorted(s["por_precio"].items(), key=lambda kv: int(kv[0])):
        print(f"  precio {precio}: {d['evento']}/{d['agentes']} agentes, "
              f"incidencia {s['incidencia_acumulada'][precio]:.3f}")
        for r, x in d["rondas"].items():
            print(f"    ronda {r}: {x['eventos']}/{x['en_riesgo']} en riesgo"
                  f" -> peligro {x['peligro']}")
    print("\n=== Contagio (dentro de la ronda, orden por seq) ===")
    for precio, d in sorted(contagio(runs).items(), key=lambda kv: int(kv[0])):
        for cond, x in d.items():
            print(f"  precio {precio} {cond:10s}: {x['clave']}/{x['depositos']} "
                  f"depósitos fueron la clave (tasa {x['tasa']})")
    i = cadena_itt(runs)
    print("\n=== Cadena de saliencia (ITT) ===")
    print(f"  etapas globales: {i['etapas']}")
    for k, x in i["por_precio"].items():
        print(f"  precio {k}: {x}")
    print(f"  condicionales: {i['condicionales']}")
    m = mediacion(runs)
    print("\n=== Capacidad y mediación ===")
    print(f"  cruce: {m['cruce']}")
    print(f"  pasos sin gastar al cierre: {m['pasos_sin_gastar']}")
    if a.json:
        os.makedirs(os.path.join(RAIZ, "reportes"), exist_ok=True)
        destino = os.path.join(RAIZ, "reportes", "analisis.json")
        with open(destino, "w", encoding="utf-8") as fh:
            json.dump({"validez": v, "supervivencia": s, "contagio": contagio(runs),
                       "cadena_itt": i, "mediacion": m}, fh, ensure_ascii=False, indent=2)
        print(f"\n  escrito {os.path.relpath(destino, RAIZ)}")


if __name__ == "__main__":
    main()
