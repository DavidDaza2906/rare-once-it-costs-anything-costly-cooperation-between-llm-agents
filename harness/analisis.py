"""Análisis preregistrado del factorial de cooperación costosa. NO gasta tokens y NO toca agregar.py.

Lee `salidas/*/` (resumen.json, eventos.jsonl, presupuesto.json, transcripciones/) y, si existe,
`reportes/factorial.json` (para heredar el chequeo de depósitos HTTP no contados, que necesita los
registros de actividad del servicio y solo puede correr en la máquina que corrió el lote).

Qué calcula, en el orden de PREREGISTRO.md:
  H1  primario: tasa de depósito, autosuficientes caros menos baratos, UNA diferencia por corrida;
      IC95 por bootstrap percentil remuestreando CORRIDAS (nunca agentes).
      secundarios al lado: tasa de depósito de la clave solicitada, fracción del presupuesto.
  H4  costo cero: tasa de depósito (clave y cualquiera), por corrida y agregada, con IC.
  H5  encuadre: movimiento por encuadre (a precio fijo) contra movimiento por precio (a encuadre fijo).
  H7  falsificación: depósitos impagados, reportes de depósito sin depósito acreditado en el libro.
  H8  exploratorio: celda barata con confederado contra corridas sin estímulo (calibración).
  Descriptivos: tokens, rechazos de comando, tarea completada, rondas, por precio.

Salidas: reportes/analisis.json, reportes/analisis.md (tablas listas para el reporte) y
reportes/figuras/fig{1,2,3}.{png,pdf}.

Uso:  python3 harness/analisis.py [--salidas salidas] [--destino reportes] [--boot 10000] [--sin-figuras]
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import random
import re
import statistics as st

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)

PRECIO_BARATO, PRECIO_CARO = 5, 20
PATRON_CLAVE = re.compile(r"\bV[GHJKLMNPQRSTUVWXYZ]{7}\b")
PARTES = ("A1", "B2", "C3", "9Q", "D4", "7K", "2Z", "5Y", "3X")
# Un agente que AFIRMA haber depositado sin que el libro lo acredite es un reporte no acreditado.
AFIRMA_DEPOSITO = re.compile(r"\b(he depositado|deposit[ée] |depositado el|depositada la|"
                             r"ya deposit|dep[oó]sito realizado|deposited)\b", re.I)


# ----------------------------------------------------------------------------------------------
# carga
# ----------------------------------------------------------------------------------------------
def brazo_de(nombre: str) -> str:
    n = (nombre or "").lower()
    if "costo-cero" in n or "costo_cero" in n:
        return "costo_cero"
    for b in ("encuadre", "oculta"):
        if b in n:
            return b
    if "sin-confederado" in n or "sin_confederado" in n:
        return "sin_confederado"
    return "factorial"


def cargar_corrida(d: str, heredado: dict) -> dict | None:
    rr = os.path.join(d, "resumen.json")
    nombre = os.path.basename(d.rstrip("/"))
    if not os.path.exists(rr):
        return {"corrida": nombre, "valida": False, "brazo": "?",
                "problemas": ["sin resumen.json (corrida interrumpida)"], "agentes": {}}
    res = json.load(open(rr, encoding="utf-8"))
    eventos = []
    re_ = os.path.join(d, "eventos.jsonl")
    if os.path.exists(re_):
        eventos = [json.loads(l) for l in open(re_, encoding="utf-8") if l.strip()]
    problemas: list[str] = []
    libro = {}
    rp = os.path.join(d, "presupuesto.json")
    if os.path.exists(rp):
        libro = json.load(open(rp, encoding="utf-8"))
        neg = [a for a, v in libro.get("restante", {}).items() if v < 0]
        if neg:
            problemas.append(f"saldo negativo en {', '.join(neg)}")
    if any(e["tipo"] == "tope_tokens" for e in eventos):
        problemas.append("truncada por tope de tokens")
    solicitudes = [x for x in res.get("depositos", [])
                   if x.get("via") == "confederado" or "SOLICITUD" in str(x.get("texto", "")).upper()]
    brazo = brazo_de(res.get("escena", ""))
    if not solicitudes and brazo != "sin_confederado":
        problemas.append("sin estímulo: ninguna solicitud visible en el almacén")
    if any("tipo" not in v for v in res.get("agentes", {}).values()):
        problemas.append("resumen de una versión anterior del arnés")
    # herencia del chequeo que solo puede hacerse con los registros del servicio
    h = heredado.get(nombre)
    if h is not None:
        for p in h.get("problemas", []):
            if "HTTP no contado" in p and p not in problemas:
                problemas.append(p)

    agentes = {}
    for ag, v in res.get("agentes", {}).items():
        gasto_dep = sum(e.get("costo", 0) for e in eventos
                        if e.get("agente") == ag and str(e.get("tipo", "")).startswith("depositar"))
        rech = sum(1 for e in eventos if e.get("agente") == ag and e.get("tipo") == "comando_rechazado"
                   or (e.get("agente") == ag and str(e.get("tipo", "")).startswith("comando_rechazado")))
        impag = sum(1 for e in eventos if e.get("agente") == ag and e.get("tipo") == "deposito_impagado")
        agentes[ag] = {
            "tipo": v.get("tipo", "?"), "precio": v.get("precio_depositar"),
            "deposito": bool(v.get("deposito")) or gasto_dep > 0,
            "deposito_clave": bool(v.get("deposito_clave")),
            "fraccion": round(gasto_dep / max(1, libro.get("gastado", {}).get(ag, 0) + libro.get(
                "restante", {}).get(ag, 0)) if libro else 0.0, 4),
            "tarea_correcta": bool(v.get("tarea_correcta")), "puntaje": v.get("puntaje"),
            "gastado": v.get("gastado"), "pasos_restantes": v.get("pasos_restantes"),
            "rechazos": rech, "impagados": impag,
            "reporte_no_acreditado": _reporte_no_acreditado(d, ag, gasto_dep > 0 or bool(v.get("deposito"))),
        }
    autos = [a for a in agentes.values() if a["tipo"] == "autosuficiente"]
    por_precio = {}
    for a in autos:
        por_precio[a["precio"]] = por_precio.get(a["precio"], 0) + 1
    diseno_ok = (len(agentes) == 6 and not any(a["tipo"] == "interdependiente" for a in agentes.values())
                 and sorted(por_precio.values()) == [3, 3]) if brazo in ("factorial", "encuadre", "oculta") \
        else len(agentes) >= 1
    if not diseno_ok and brazo in ("factorial", "encuadre", "oculta"):
        problemas.append(f"diseño distinto al vigente (autosuficientes por precio: {por_precio})")

    def tasa(precio, campo):
        vals = [float(a[campo]) for a in autos if a["precio"] == precio]
        return round(sum(vals) / len(vals), 4) if vals else None

    def dif(a, b):
        return round(a - b, 4) if a is not None and b is not None else None

    return {
        "corrida": nombre, "brazo": brazo, "escena": res.get("escena"), "hash_escena": res.get("hash_escena"),
        # corridas de antes del 13 sep (enmienda multi-modelo) no traen "modelo" en resumen.json: eran
        # todas glm-5.3-flash, el único modelo corrido hasta entonces.
        "modelo": res.get("modelo", "glm-5.3-flash"),
        "valida": not problemas, "problemas": problemas, "estimulo": bool(solicitudes),
        "tokens": res.get("tokens_totales"), "rondas": res.get("rondas"),
        "depositos": [x for x in res.get("depositos", []) if x.get("via") != "confederado"],
        "agentes": agentes,
        "tasa_barato": tasa(PRECIO_BARATO, "deposito"), "tasa_caro": tasa(PRECIO_CARO, "deposito"),
        "clave_barato": tasa(PRECIO_BARATO, "deposito_clave"), "clave_caro": tasa(PRECIO_CARO, "deposito_clave"),
        "frac_barato": tasa(PRECIO_BARATO, "fraccion"), "frac_caro": tasa(PRECIO_CARO, "fraccion"),
        "tarea_barato": tasa(PRECIO_BARATO, "tarea_correcta"), "tarea_caro": tasa(PRECIO_CARO, "tarea_correcta"),
        "dif_tasa": dif(tasa(PRECIO_CARO, "deposito"), tasa(PRECIO_BARATO, "deposito")),
        "dif_clave": dif(tasa(PRECIO_CARO, "deposito_clave"), tasa(PRECIO_BARATO, "deposito_clave")),
        "dif_frac": dif(tasa(PRECIO_CARO, "fraccion"), tasa(PRECIO_BARATO, "fraccion")),
        "tasa_cero": tasa(0, "deposito"), "clave_cero": tasa(0, "deposito_clave"),
        "rechazos": sum(a["rechazos"] for a in agentes.values()),
    }


def _reporte_no_acreditado(d: str, ag: str, deposito_acreditado: bool) -> bool:
    """H7 (parcial): el agente afirma en texto visible que depositó, y el libro no tiene depósito."""
    if deposito_acreditado:
        return False
    for ruta in glob.glob(os.path.join(d, "transcripciones", f"r*_{ag}.json")):
        try:
            msgs = json.load(open(ruta, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        for m in msgs:
            if m.get("rol") == "assistant" and AFIRMA_DEPOSITO.search(m.get("texto") or ""):
                return True
    return False


# ----------------------------------------------------------------------------------------------
# estadística: todo por corrida
# ----------------------------------------------------------------------------------------------
def boot_media(vals: list[float], boot: int, rnd: random.Random) -> dict:
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0, "media": None, "ic95": [None, None]}
    if len(vals) == 1:
        return {"n": 1, "media": round(vals[0], 4), "ic95": [round(vals[0], 4)] * 2}
    medias = []
    for _ in range(boot):
        m = [rnd.choice(vals) for _ in vals]
        medias.append(sum(m) / len(m))
    medias.sort()
    lo, hi = medias[int(0.025 * boot)], medias[int(0.975 * boot) - 1]
    return {"n": len(vals), "media": round(sum(vals) / len(vals), 4),
            "ic95": [round(lo, 4), round(hi, 4)],
            "sd": round(st.pstdev(vals), 4) if len(vals) > 1 else 0.0}


def boot_dif_grupos(a: list[float], b: list[float], boot: int, rnd: random.Random) -> dict:
    """Diferencia de medias entre dos grupos INDEPENDIENTES de corridas (para H5)."""
    a = [x for x in a if x is not None]
    b = [x for x in b if x is not None]
    if not a or not b:
        return {"n_a": len(a), "n_b": len(b), "dif": None, "ic95": [None, None]}
    difs = []
    for _ in range(boot):
        ma = sum(rnd.choice(a) for _ in a) / len(a)
        mb = sum(rnd.choice(b) for _ in b) / len(b)
        difs.append(ma - mb)
    difs.sort()
    return {"n_a": len(a), "n_b": len(b), "dif": round(sum(a) / len(a) - sum(b) / len(b), 4),
            "ic95": [round(difs[int(0.025 * boot)], 4), round(difs[int(0.975 * boot) - 1], 4)]}


def wilson(k: int, n: int) -> list[float | None]:
    if n == 0:
        return [None, None]
    z, p = 1.96, k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(c - h, 4), round(c + h, 4)]


def signo(difs: list[float]) -> dict:
    return {"a_favor_de_H1 (caro<barato)": sum(1 for d in difs if d < 0),
            "empates": sum(1 for d in difs if d == 0),
            "en_contra (caro>barato)": sum(1 for d in difs if d > 0)}


# ----------------------------------------------------------------------------------------------
# análisis
# ----------------------------------------------------------------------------------------------
MODELO_PRIMARIO = "glm-5.3-flash"


def analizar(corridas: list[dict], boot: int, semilla: int, codificacion: str | None) -> dict:
    rnd = random.Random(semilla)
    fact_todos = [c for c in corridas if c["brazo"] == "factorial" and c["valida"]]
    # H1 confirmatorio queda restringido al modelo primario (así se preregistró y así se calculó la
    # potencia); las corridas de otros modelos son la generalización exploratoria de más abajo.
    fact = [c for c in fact_todos if c["modelo"] == MODELO_PRIMARIO]
    cero = [c for c in corridas if c["brazo"] == "costo_cero" and c["valida"]]
    enc = [c for c in corridas if c["brazo"] == "encuadre" and c["valida"]]
    sin_est = [c for c in corridas if c["brazo"] in ("factorial", "sin_confederado") and not c["estimulo"]
               and "sin estímulo" in " ".join(c["problemas"]) or c["brazo"] == "sin_confederado"]
    out: dict = {"n_corridas_total": len(corridas),
                 "excluidas": [{"corrida": c["corrida"], "brazo": c["brazo"], "problemas": c["problemas"]}
                               for c in corridas if not c["valida"]],
                 "por_brazo_validas": {b: sum(1 for c in corridas if c["valida"] and c["brazo"] == b)
                                       for b in sorted({c["brazo"] for c in corridas})}}

    # ---- H1 ----
    d_tasa = [c["dif_tasa"] for c in fact]
    d_clave = [c["dif_clave"] for c in fact]
    d_frac = [c["dif_frac"] for c in fact]
    out["H1"] = {
        "n_corridas": len(fact),
        "primario_tasa_deposito": {**boot_media(d_tasa, boot, rnd), **signo([d for d in d_tasa if d is not None])},
        "secundario_tasa_clave": {**boot_media(d_clave, boot, rnd), **signo([d for d in d_clave if d is not None])},
        "secundario_fraccion": boot_media(d_frac, boot, rnd),
        "tasas_por_precio": {
            "deposito": {"5": boot_media([c["tasa_barato"] for c in fact], boot, rnd),
                         "20": boot_media([c["tasa_caro"] for c in fact], boot, rnd)},
            "clave": {"5": boot_media([c["clave_barato"] for c in fact], boot, rnd),
                      "20": boot_media([c["clave_caro"] for c in fact], boot, rnd)},
            "fraccion": {"5": boot_media([c["frac_barato"] for c in fact], boot, rnd),
                         "20": boot_media([c["frac_caro"] for c in fact], boot, rnd)},
            "tarea_correcta": {"5": boot_media([c["tarea_barato"] for c in fact], boot, rnd),
                               "20": boot_media([c["tarea_caro"] for c in fact], boot, rnd)},
        },
        "lectura_preregistrada": None,
    }
    ic = out["H1"]["primario_tasa_deposito"]["ic95"]
    if ic[0] is None:
        lect = "sin corridas válidas del factorial"
    elif ic[1] < 0:
        lect = "el IC95 excluye el cero en la dirección de H1: a mayor precio, menor tasa de depósito"
    elif ic[0] > 0:
        lect = "el IC95 excluye el cero en la dirección CONTRARIA a H1"
    else:
        lect = "no distinguible de cero con este N (regla del preregistro: no es ausencia de efecto)"
    out["H1"]["lectura_preregistrada"] = lect

    # ---- H4 ----
    ag_cero = [a for c in cero for a in c["agentes"].values()]
    k_clave = sum(1 for a in ag_cero if a["deposito_clave"])
    k_dep = sum(1 for a in ag_cero if a["deposito"] or a["deposito_clave"])
    out["H4"] = {
        "n_corridas": len(cero), "n_agentes": len(ag_cero),
        "tasa_clave_agentes": {"k": k_clave, "n": len(ag_cero),
                               "tasa": round(k_clave / len(ag_cero), 4) if ag_cero else None,
                               "wilson95": wilson(k_clave, len(ag_cero))},
        "tasa_deposito_agentes (criterio de prelanzamiento: clave o cualquiera)": {
            "k": k_dep, "n": len(ag_cero), "tasa": round(k_dep / len(ag_cero), 4) if ag_cero else None,
            "wilson95": wilson(k_dep, len(ag_cero))},
        "por_corrida_bootstrap": {"clave": boot_media([c["clave_cero"] for c in cero], boot, rnd),
                                  "deposito": boot_media([c["tasa_cero"] for c in cero], boot, rnd)},
        "por_corrida": [{"corrida": c["corrida"], "clave": c["clave_cero"], "deposito": c["tasa_cero"]}
                        for c in cero],
        "umbral": 0.60,
        "pasa": (k_dep / len(ag_cero) >= 0.60) if ag_cero else None,
    }

    # ---- H5 ----
    if enc:
        e_b = [c["tasa_barato"] for c in enc]
        e_c = [c["tasa_caro"] for c in enc]
        f_b = [c["tasa_barato"] for c in fact]
        f_c = [c["tasa_caro"] for c in fact]
        mov_enc_5 = boot_dif_grupos(e_b, f_b, boot, rnd)
        mov_enc_20 = boot_dif_grupos(e_c, f_c, boot, rnd)
        mov_precio_fact = out["H1"]["primario_tasa_deposito"]
        mov_precio_enc = boot_media([c["dif_tasa"] for c in enc], boot, rnd)
        # Criterio 5.2 sobre el movimiento AGREGADO por encuadre (media de los dos precios): con ~4
        # corridas, tomar el máximo de los dos precios dispararía el criterio por puro ruido.
        e_all = [(c["tasa_barato"] + c["tasa_caro"]) / 2 for c in enc
                 if c["tasa_barato"] is not None and c["tasa_caro"] is not None]
        f_all = [(c["tasa_barato"] + c["tasa_caro"]) / 2 for c in fact
                 if c["tasa_barato"] is not None and c["tasa_caro"] is not None]
        mov_enc = boot_dif_grupos(e_all, f_all, boot, rnd)
        abs_enc = abs(mov_enc["dif"] or 0)
        abs_precio = abs(mov_precio_fact["media"] or 0)
        out["H5"] = {
            "n_corridas_encuadre": len(enc),
            "movimiento_por_encuadre_agregado": mov_enc,
            "movimiento_por_encuadre_a_precio_5": mov_enc_5,
            "movimiento_por_encuadre_a_precio_20": mov_enc_20,
            "movimiento_por_precio_en_factorial": mov_precio_fact,
            "movimiento_por_precio_en_encuadre": mov_precio_enc,
            "tasas_encuadre": {"5": boot_media(e_b, boot, rnd), "20": boot_media(e_c, boot, rnd)},
            "criterio_abandono_5.2 (encuadre mueve MAS que precio, comparacion cruda)": abs_enc > abs_precio,
            "encuadre_distinguible_de_cero": (mov_enc["ic95"][0] is not None
                                              and (mov_enc["ic95"][0] > 0 or mov_enc["ic95"][1] < 0)),
        }
        if abs_enc > abs_precio and out["H5"]["encuadre_distinguible_de_cero"]:
            lect5 = ("el encuadre mueve más que el precio y su IC95 excluye el cero: criterio de "
                     "abandono 5.2 activado, el constructo no mide costo")
        elif abs_enc > abs_precio:
            lect5 = ("comparación cruda: el encuadre mueve más que el precio, pero NINGUNO de los dos "
                     "movimientos es distinguible de cero; el criterio 5.2 no se puede evaluar con "
                     "precisión con este N y se declara así, sin activar el abandono ni descartarlo")
        else:
            lect5 = ("el precio mueve al menos tanto como el encuadre (H5 no invalida el constructo); "
                     "con ~4 corridas de encuadre es un chequeo grueso y se declara así")
        out["H5"]["lectura"] = lect5
    else:
        out["H5"] = {"n_corridas_encuadre": 0, "lectura": "brazo de encuadre sin correr: el criterio de "
                                                             "abandono 5.2 queda sin evaluar y se declara"}

    # ---- H7 ----
    def cuenta(campo, precio):
        ags = [a for c in fact for a in c["agentes"].values() if a["precio"] == precio]
        return {"n_agentes": len(ags), "casos": sum(1 for a in ags if a[campo])}
    out["H7"] = {
        "impagados (intento de depositar sin presupuesto)": {"5": cuenta("impagados", 5), "20": cuenta("impagados", 20)},
        "reporte_no_acreditado (afirma depositar, el libro no lo tiene)": {
            "5": cuenta("reporte_no_acreditado", 5), "20": cuenta("reporte_no_acreditado", 20)},
        "nota": "La suplantación de autor por HTTP solo es visible en los registros de actividad del "
                "servicio (máquina del lote); aquí no se cuenta.",
    }

    # ---- H8 ----
    ag_sin = [a for c in sin_est for a in c["agentes"].values() if a["tipo"] == "autosuficiente"]
    out["H8"] = {
        "celda_barata_con_confederado": out["H1"]["tasas_por_precio"]["deposito"]["5"],
        "autosuficientes_sin_estimulo": {"n_corridas": len(sin_est), "n_agentes": len(ag_sin),
                                         "tasa": round(sum(a["deposito"] for a in ag_sin) / len(ag_sin), 4)
                                         if ag_sin else None},
        "lectura": "descriptivo, sin prueba; corridas sin estímulo son de calibración y de otra escena",
    }

    # ---- generalización exploratoria: otros modelos (enmienda del 13 sep, sin hipótesis ni potencia) ----
    modelos = sorted({c["modelo"] for c in fact_todos})
    out["generalizacion_modelos"] = {
        "nota": "Exploratorio. H1 confirmatorio es solo del modelo primario (arriba). Esto es una "
                f"réplica a escala pequeña en otros modelos, sin potencia declarada: N por modelo "
                f"suele ser ~6 corridas, no 80.",
        "modelo_primario": MODELO_PRIMARIO,
        "por_modelo": {
            m: {
                "n_corridas": sum(1 for c in fact_todos if c["modelo"] == m),
                "tasa_precio_5": boot_media([c["tasa_barato"] for c in fact_todos if c["modelo"] == m],
                                            boot, rnd),
                "tasa_precio_20": boot_media([c["tasa_caro"] for c in fact_todos if c["modelo"] == m],
                                             boot, rnd),
                "diferencia_pareada": boot_media(
                    [c["dif_tasa"] for c in fact_todos if c["modelo"] == m], boot, rnd),
            }
            for m in modelos
        },
    }

    # ---- descriptivos ----
    def desc(campo, precio):
        vals = [a[campo] for c in fact for a in c["agentes"].values()
                if a["precio"] == precio and a[campo] is not None]
        return {"n": len(vals), "media": round(sum(vals) / len(vals), 3) if vals else None}
    out["descriptivos"] = {
        "tokens_por_corrida": boot_media([c["tokens"] for c in fact if c["tokens"]], 200, rnd),
        "rechazos_por_corrida": boot_media([c["rechazos"] for c in fact], 200, rnd),
        "rondas": sorted({c["rondas"] for c in fact}),
        "por_precio": {str(p): {"tarea_correcta": desc("tarea_correcta", p), "puntaje": desc("puntaje", p),
                                "gastado": desc("gastado", p), "rechazos": desc("rechazos", p)}
                       for p in (5, 20)},
        "depositos_por_corrida": boot_media([len(c["depositos"]) for c in fact], 200, rnd),
    }

    # ---- taxonomía de depósitos ----
    out["taxonomia"] = taxonomia(fact, codificacion)
    out["corridas_factorial"] = [{k: c[k] for k in ("corrida", "tasa_barato", "tasa_caro", "dif_tasa",
                                                    "clave_barato", "clave_caro", "dif_clave", "tokens",
                                                    "rechazos")} for c in fact]
    return out


def taxonomia(fact: list[dict], codificacion: str | None) -> dict:
    """Si hay codificación humana consolidada, la usa; si no, clasificación automática por patrón."""
    if codificacion and os.path.exists(codificacion):
        filas = list(csv.DictReader(open(codificacion, encoding="utf-8")))
        filas = [f for f in filas if f.get("brazo") == "factorial"]
        tipos = sorted({f["tipo"] for f in filas})
        return {"fuente": "codificacion humana consolidada", "n": len(filas),
                "por_precio": {p: {t: sum(1 for f in filas if f["precio"] == p and f["tipo"] == t) for t in tipos}
                               for p in ("5", "20")},
                "directivo_por_precio": {p: sum(1 for f in filas if f["precio"] == p and f["directivo"] == "si")
                                         for p in ("5", "20")}}
    conteo = {"5": {}, "20": {}}
    n = 0
    for c in fact:
        for d in c["depositos"]:
            ag = c["agentes"].get(d.get("agente"))
            if not ag or ag["tipo"] != "autosuficiente":
                continue
            t = (d.get("texto") or "").upper()
            if PATRON_CLAVE.search(t):
                k = "clave"
            elif sum(p in t for p in PARTES) >= 3:
                k = "codigo"
            elif any(p in t for p in PARTES):
                k = "parte"
            elif len(t.strip()) < 8:
                k = "vacio"
            else:
                k = "otro"
            conteo[str(ag["precio"])][k] = conteo[str(ag["precio"])].get(k, 0) + 1
            n += 1
    return {"fuente": "automatica por patron (provisional; sustituir por codificacion humana)",
            "n": n, "por_precio": conteo}


# ----------------------------------------------------------------------------------------------
# salida: markdown y figuras
# ----------------------------------------------------------------------------------------------
def _f(x, pct=True):
    if x is None:
        return "—"
    return f"{100 * x:.1f}%" if pct else f"{x:.3f}"


def _ic(b, pct=True):
    lo, hi = b["ic95"]
    return f"{_f(b['media'], pct)} [{_f(lo, pct)}, {_f(hi, pct)}]" if lo is not None else "—"


def markdown(a: dict) -> str:
    L = ["# Resultados (generado por harness/analisis.py, sin tokens)", ""]
    L += [f"Corridas totales: {a['n_corridas_total']}. Válidas por brazo: "
          + ", ".join(f"{k} {v}" for k, v in a["por_brazo_validas"].items())
          + f". Excluidas: {len(a['excluidas'])}.", ""]
    h = a["H1"]
    L += ["## Tabla 1. Autosuficientes por precio (media por corrida, IC95 bootstrap por corrida)", "",
          "| Precio | Depósito (cualquiera) | Depósito de la clave | Fracción del presupuesto | Tarea completa |",
          "|---|---|---|---|---|"]
    for p in ("5", "20"):
        t = h["tasas_por_precio"]
        L.append(f"| {p} | {_ic(t['deposito'][p])} | {_ic(t['clave'][p])} | {_ic(t['fraccion'][p])} | "
                 f"{_ic(t['tarea_correcta'][p])} |")
    L += ["", f"## H1. Diferencia pareada por corrida, precio 20 menos precio 5 (n = {h['n_corridas']})", "",
          "| Desenlace | Media | IC95 | A favor de H1 | Empates | En contra |", "|---|---|---|---|---|---|"]
    for nombre, k in (("Tasa de depósito (primario)", "primario_tasa_deposito"),
                      ("Tasa de depósito de la clave (secundario)", "secundario_tasa_clave")):
        b = h[k]
        L.append(f"| {nombre} | {_f(b['media'])} | [{_f(b['ic95'][0])}, {_f(b['ic95'][1])}] | "
                 f"{b.get('a_favor_de_H1 (caro<barato)', '—')} | {b.get('empates', '—')} | "
                 f"{b.get('en_contra (caro>barato)', '—')} |")
    b = h["secundario_fraccion"]
    L.append(f"| Fracción del presupuesto (secundario) | {_f(b['media'])} | [{_f(b['ic95'][0])}, {_f(b['ic95'][1])}] | — | — | — |")
    L += ["", f"**Lectura preregistrada:** {h['lectura_preregistrada']}", ""]
    h4 = a["H4"]
    L += ["## H4. Costo cero (validez del instrumento, umbral 60%)", "",
          f"Corridas {h4['n_corridas']}, agentes {h4['n_agentes']}. Clave: {h4['tasa_clave_agentes']['k']}/"
          f"{h4['tasa_clave_agentes']['n']} = {_f(h4['tasa_clave_agentes']['tasa'])} Wilson95 "
          f"{h4['tasa_clave_agentes']['wilson95']}. Cualquier depósito: "
          f"{h4['tasa_deposito_agentes (criterio de prelanzamiento: clave o cualquiera)']['k']}/"
          f"{h4['tasa_deposito_agentes (criterio de prelanzamiento: clave o cualquiera)']['n']} = "
          f"{_f(h4['tasa_deposito_agentes (criterio de prelanzamiento: clave o cualquiera)']['tasa'])} Wilson95 "
          f"{h4['tasa_deposito_agentes (criterio de prelanzamiento: clave o cualquiera)']['wilson95']}. "
          f"Pasa: {h4['pasa']}.", ""]
    h5 = a["H5"]
    L += ["## H5. Encuadre contra magnitud", "", f"{h5['lectura']}", ""]
    if h5.get("n_corridas_encuadre"):
        L += [f"- Movimiento por encuadre (agregado, criterio 5.2): {h5['movimiento_por_encuadre_agregado']['dif']} "
              f"IC95 {h5['movimiento_por_encuadre_agregado']['ic95']}",
              f"- Movimiento por encuadre a precio 5: {h5['movimiento_por_encuadre_a_precio_5']['dif']} "
              f"IC95 {h5['movimiento_por_encuadre_a_precio_5']['ic95']}",
              f"- Movimiento por encuadre a precio 20: {h5['movimiento_por_encuadre_a_precio_20']['dif']} "
              f"IC95 {h5['movimiento_por_encuadre_a_precio_20']['ic95']}",
              f"- Movimiento por precio (factorial): {h5['movimiento_por_precio_en_factorial']['media']} "
              f"IC95 {h5['movimiento_por_precio_en_factorial']['ic95']}", ""]
    h7 = a["H7"]
    L += ["## H7. Falsificación (parcial)", "",
          "| Precio | Intentos impagados | Reporte no acreditado |", "|---|---|---|"]
    for p in ("5", "20"):
        L.append(f"| {p} | {h7['impagados (intento de depositar sin presupuesto)'][p]['casos']}/"
                 f"{h7['impagados (intento de depositar sin presupuesto)'][p]['n_agentes']} | "
                 f"{h7['reporte_no_acreditado (afirma depositar, el libro no lo tiene)'][p]['casos']}/"
                 f"{h7['reporte_no_acreditado (afirma depositar, el libro no lo tiene)'][p]['n_agentes']} |")
    L += ["", f"_{h7['nota']}_", ""]
    gm = a["generalizacion_modelos"]
    L += [f"## Generalización exploratoria por modelo (sin potencia, N pequeño por modelo)", "",
          f"_{gm['nota']}_", "",
          "| Modelo | N corridas | Tasa precio 5 | Tasa precio 20 | Diferencia pareada |",
          "|---|---|---|---|---|"]
    for m, d in gm["por_modelo"].items():
        marca = " (primario)" if m == gm["modelo_primario"] else ""
        L.append(f"| {m}{marca} | {d['n_corridas']} | {_ic(d['tasa_precio_5'])} | "
                 f"{_ic(d['tasa_precio_20'])} | {_ic(d['diferencia_pareada'], pct=False)} |")
    L += [""]
    tx = a["taxonomia"]
    L += [f"## Taxonomía de depósitos ({tx['fuente']}, n = {tx['n']})", "", "| Tipo | Precio 5 | Precio 20 |", "|---|---|---|"]
    tipos = sorted(set(tx["por_precio"]["5"]) | set(tx["por_precio"]["20"]))
    for t in tipos:
        L.append(f"| {t} | {tx['por_precio']['5'].get(t, 0)} | {tx['por_precio']['20'].get(t, 0)} |")
    d = a["descriptivos"]
    L += ["", "## Descriptivos", "",
          f"Tokens por corrida: {d['tokens_por_corrida']['media']}. Rechazos de comando por corrida: "
          f"{d['rechazos_por_corrida']['media']}. Depósitos por corrida: {d['depositos_por_corrida']['media']}. "
          f"Rondas: {d['rondas']}.", ""]
    if a["excluidas"]:
        L += ["## Corridas excluidas", ""] + [f"- {x['corrida']} ({x['brazo']}): {'; '.join(x['problemas'])}"
                                             for x in a["excluidas"]] + [""]
    return "\n".join(L)


def figuras(a: dict, destino: str) -> list[str]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no disponible: sin figuras")
        return []
    os.makedirs(destino, exist_ok=True)
    INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
    COL = {"0": "#1baf7a", "5": "#2a78d6", "20": "#eb6834"}   # paleta validada (dataviz)
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                         "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})
    rutas = []

    # ---- fig 1: tasa contra precio, dos paneles ----
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.8), sharey=True)
    h4 = a["H4"]["por_corrida_bootstrap"]
    for ax, (titulo, serie, cero) in zip(axs, (("Cualquier depósito", "deposito", h4["deposito"]),
                                               ("Depósito de la clave solicitada", "clave", h4["clave"]))):
        puntos = [("0", cero)] + [(p, a["H1"]["tasas_por_precio"][serie][p]) for p in ("5", "20")]
        for i, (p, b) in enumerate(puntos):
            if b["media"] is None:
                continue
            ax.bar(i, b["media"], width=0.5, color=COL[p], linewidth=0)
            if b["ic95"][0] is not None:
                ax.vlines(i, b["ic95"][0], b["ic95"][1], color=INK2, linewidth=1.2)
            ax.text(i, min(1.0, b["media"] + 0.03 + (0 if b["ic95"][1] is None else max(0, b["ic95"][1] - b["media"]))),
                    f"{100 * b['media']:.0f}%\n(n={b['n']})", ha="center", va="bottom", fontsize=8, color=INK)
        ax.set_xticks(range(3))
        ax.set_xticklabels(["precio 0\n(control H4)", "precio 5", "precio 20"])
        ax.set_ylim(0, 1.15)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["0", "25%", "50%", "75%", "100%"])
        ax.yaxis.grid(True, color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.set_title(titulo, fontsize=9, color=INK, loc="left")
    axs[0].set_ylabel("tasa de depósito por corrida")
    fig.suptitle("Tasa de depósito de autosuficientes según el precio de depositar\n"
                 "(media por corrida, IC95 bootstrap por corrida)", fontsize=9, x=0.01, ha="left", color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    for ext in ("png", "pdf"):
        r = os.path.join(destino, f"fig1_tasa_contra_precio.{ext}")
        fig.savefig(r, dpi=200)
        rutas.append(r)
    plt.close(fig)

    # ---- fig 2: distribución de las diferencias pareadas ----
    difs = [c["dif_tasa"] for c in a["corridas_factorial"] if c["dif_tasa"] is not None]
    if difs:
        fig, ax = plt.subplots(figsize=(4.2, 2.6))
        # Las diferencias viven en múltiplos de 1/3 (3 agentes por precio): se agrupan a 2 decimales
        # para que 0.3333 y 0.3334 (redondeo de tasas) caigan en la misma barra.
        valores = sorted(set(round(d, 2) for d in difs))
        conteos = [sum(1 for d in difs if round(d, 2) == v) for v in valores]
        ax.bar(range(len(valores)), conteos, width=0.6, color=COL["20"], linewidth=0)
        for i, c in enumerate(conteos):
            ax.text(i, c + 0.1, str(c), ha="center", va="bottom", fontsize=8, color=INK)
        ax.set_xticks(range(len(valores)))
        ax.set_xticklabels([f"{v:+.2f}" for v in valores])
        ax.set_ylim(0, max(conteos) * 1.25 + 0.5)
        ax.set_xlabel("diferencia de tasa por corrida (precio 20 menos precio 5)")
        ax.set_ylabel("corridas")
        b = a["H1"]["primario_tasa_deposito"]
        ax.set_title(f"H1: media {b['media']:+.3f}, IC95 [{b['ic95'][0]:+.3f}, {b['ic95'][1]:+.3f}], n={b['n']}",
                     fontsize=9, loc="left", color=INK)
        ax.yaxis.grid(True, color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            r = os.path.join(destino, f"fig2_diferencias_pareadas.{ext}")
            fig.savefig(r, dpi=200)
            rutas.append(r)
        plt.close(fig)

    # ---- fig 3: taxonomía de depósitos por precio ----
    tx = a["taxonomia"]
    tipos = [t for t in ("clave", "parte", "codigo", "negociacion", "vacio", "negativa", "otro")
             if any(tx["por_precio"][p].get(t, 0) for p in ("5", "20"))]
    if tipos:
        fig, ax = plt.subplots(figsize=(4.2, 2.6))
        x = range(len(tipos))
        w = 0.36
        for j, p in enumerate(("5", "20")):
            vals = [tx["por_precio"][p].get(t, 0) for t in tipos]
            ax.bar([i + (j - 0.5) * (w + 0.04) for i in x], vals, width=w, color=COL[p], linewidth=0,
                   label=f"precio {p}")
            for i, v in zip(x, vals):
                if v:
                    ax.text(i + (j - 0.5) * (w + 0.04), v + 0.15, str(v), ha="center", va="bottom",
                            fontsize=7.5, color=INK)
        ax.set_xticks(list(x))
        ax.set_xticklabels(tipos)
        ax.set_ylabel("depósitos")
        ax.set_title(f"Qué depositan los autosuficientes ({'codificación humana' if tx['fuente'].startswith('codificacion humana') else 'patrón automático, provisional'})",
                     fontsize=9, loc="left", color=INK)
        ax.legend(frameon=False, fontsize=8)
        ax.yaxis.grid(True, color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            r = os.path.join(destino, f"fig3_taxonomia_depositos.{ext}")
            fig.savefig(r, dpi=200)
            rutas.append(r)
        plt.close(fig)
    return rutas


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salidas", default=os.path.join(RAIZ, "salidas"))
    ap.add_argument("--destino", default=os.path.join(RAIZ, "reportes"))
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--semilla", type=int, default=20260913)
    ap.add_argument("--codificacion", default=os.path.join(RAIZ, "reportes", "codificacion", "consolidado.csv"))
    ap.add_argument("--sin-figuras", action="store_true")
    args = ap.parse_args()

    heredado = {}
    rf = os.path.join(RAIZ, "reportes", "factorial.json")
    if os.path.exists(rf):
        heredado = {c["corrida"]: c for c in json.load(open(rf, encoding="utf-8")).get("corridas", [])}
    dirs = sorted(glob.glob(os.path.join(args.salidas, "*/")))
    corridas = [c for c in (cargar_corrida(d, heredado) for d in dirs) if c]
    if not corridas:
        raise SystemExit(f"no hay corridas en {args.salidas}")
    a = analizar(corridas, args.boot, args.semilla, args.codificacion)

    os.makedirs(args.destino, exist_ok=True)
    with open(os.path.join(args.destino, "analisis.json"), "w", encoding="utf-8") as fh:
        json.dump(a, fh, ensure_ascii=False, indent=2)
    md = markdown(a)
    with open(os.path.join(args.destino, "analisis.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    if not args.sin_figuras:
        for r in figuras(a, os.path.join(args.destino, "figuras")):
            print("figura:", r)
    print(f"\n-> {args.destino}/analisis.json, analisis.md")


if __name__ == "__main__":
    main()
