"""Agrega las corridas del factorial y verifica la validez de cada una. NO gasta tokens.

Un dato solo es dato si el instrumento lo respalda. Este script no confía en el resumen de la
corrida: lo contrasta con el libro de presupuesto y con el registro de actividad del servicio.

Tres chequeos de validez, por evidencia y no por etiqueta:
  1. **Saldo negativo** en el libro -> la fracción sacrificada pudo pasar de 100%: corrida inválida.
  2. **Donación no contada**: POST al servicio en la ventana de la corrida que el libro no cobró
     (la fuga que hacía invisible el sacrificio).
  3. **Truncamiento** por tope de tokens: la última ronda queda censurada.

Salida: reportes/factorial.json y una tabla por consola.

Uso:  python3 agregar.py [--hasta N]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
PUERTOS = {1: 8201, 2: 8202, 3: 8203, 4: 8204, 5: 8205, 6: 8206}


def _ts(nombre: str) -> float:
    return datetime.strptime(nombre.split("_")[0], "%Y%m%dT%H%M%S").replace(
        tzinfo=timezone.utc).timestamp()


def evaluar(d: str) -> dict:
    ruta_resumen = os.path.join(d, "resumen.json")
    if not os.path.exists(ruta_resumen):
        return {"corrida": os.path.basename(d.rstrip("/")), "valida": False,
                "problemas": ["sin resumen.json (corrida interrumpida)"]}
    with open(ruta_resumen, encoding="utf-8") as fh:
        resumen = json.load(fh)
    eventos = [json.loads(l) for l in open(os.path.join(d, "eventos.jsonl"), encoding="utf-8")]
    problemas: list[str] = []

    # 1. saldo negativo
    libro = {}
    if os.path.exists(os.path.join(d, "presupuesto.json")):
        libro = json.load(open(os.path.join(d, "presupuesto.json"), encoding="utf-8"))
        negativos = [a for a, v in libro.get("restante", {}).items() if v < 0]
        if negativos:
            problemas.append(f"saldo negativo en {', '.join(negativos)}")

    # 2. donaciones no contadas: POST observados por el servicio contra lo que el libro cobró
    t0, t1 = _ts(os.path.basename(d.rstrip("/"))), eventos[-1]["t"]
    for n, puerto in PUERTOS.items():
        ag = f"agente-{n:02d}"
        af = os.path.join(BASE, f"puerto_actividad_{puerto}.jsonl")
        if not os.path.exists(af):
            continue
        observados = [json.loads(l) for l in open(af, encoding="utf-8")]
        # Solo cuentan los POST que el servicio ACEPTÓ (llevan largo): un POST vacío o mal formado
        # se rechaza con 400 y no entra al almacén, pero queda en el registro de actividad. Comparar
        # contra todos los POST marcaba como inválidas corridas perfectamente buenas.
        posts = [r for r in observados
                 if r["metodo"] == "POST" and t0 <= r["t"] <= t1
                 and ("largo" in r or "detalle" in r and isinstance(r.get("detalle"), dict)
                      and "rechazado" not in (r.get("detalle") or {}))]
        posts = [r for r in posts if "rechazado" not in (r.get("detalle") or {})]
        cobrados = [e for e in eventos if e["agente"] == ag
                    and (e["tipo"].startswith("depositar") or e["tipo"] == "deposito_impagado")]
        if len(posts) > len(cobrados):
            problemas.append(f"{ag}: {len(posts) - len(cobrados)} depósito(s) por HTTP no contado(s)")

    # 3. truncamiento
    truncadas = [e for e in eventos if e["tipo"] == "tope_tokens"]
    if truncadas:
        problemas.append(f"truncada por tope de tokens ({len(truncadas)} agentes)")

    # desenlaces por agente
    escena = json.load(open(os.path.join(RAIZ, "escena.resuelta.json"), encoding="utf-8"))
    presupuesto = escena["puntaje"]["presupuesto"]
    asign = {a["agente"]: a for a in escena["asignacion"]}
    # ¿Hubo estímulo? Sin una solicitud visible antes de la última ronda de los autosuficientes,
    # un cero no es dato: es ausencia de decisión. Se marca, no se excluye en silencio.
    solicitudes = [d for d in resumen.get("depositos", [])
                   if d.get("via") == "confederado" or "SOLICITUD" in str(d.get("texto", "")).upper()]
    if not solicitudes:
        problemas.append("sin estímulo: ninguna solicitud visible en el almacén")
    por_agente = {}
    for ag, v in resumen["agentes"].items():
        gasto_deposito = sum(e["costo"] for e in eventos
                             if e["agente"] == ag and e["tipo"].startswith("depositar"))
        # Un resumen sin el tipo del agente lo escribió una versión anterior del arnés: es evidencia
        # de invalidez, no un detalle de formato.
        if "tipo" not in v:
            problemas.append(f"{ag}: resumen de una versión anterior del arnés")
            tipo = asign.get(ag, {}).get("tipo", "?")
            precio = asign.get(ag, {}).get("precio_depositar")
        else:
            tipo, precio = v["tipo"], v["precio_depositar"]
        por_agente[ag] = {
            "tipo": tipo, "precio": precio,
            "fraccion_sacrificada": round(gasto_deposito / presupuesto, 4),
            "deposito": bool(v.get("deposito")) or gasto_deposito > 0,
            "clave": bool(v.get("deposito_clave")),
            "tarea_correcta": bool(v.get("tarea_correcta")), "puntaje": v.get("puntaje"),
            "gastado": v.get("gastado"), "pasos_restantes": v.get("pasos_restantes"),
        }

    # contraste primario de la corrida: autosuficientes caros menos baratos.
    # PRIMARIO = tasa de depósito (binaria por agente). Con precio fijo por brazo, la fracción es
    # precio × indicador (0/0,125 a precio 5; 0/0,5 a precio 20) y H1 exigiría una caída de tasa
    # de más de 4× para salir en su dirección. La fracción queda como SECUNDARIA.
    def media(tipo: str, precio: int, campo: str) -> float | None:
        vals = [float(a[campo]) for a in por_agente.values()
                if a["tipo"] == tipo and a["precio"] == precio]
        return round(sum(vals) / len(vals), 4) if vals else None

    def dif(a: float | None, b: float | None) -> float | None:
        return round(a - b, 4) if a is not None and b is not None else None

    # PRIMARIO (A1, 13 sep): el acto que la solicitud elicita — depositar LA CLAVE. "Cualquier
    # depósito" (unión) queda descriptivo: metía códigos ensamblados, partes y negociación de canal.
    clave_caros = media("autosuficiente", 20, "clave")
    clave_baratos = media("autosuficiente", 5, "clave")
    tasa_caros = media("autosuficiente", 20, "deposito")
    tasa_baratos = media("autosuficiente", 5, "deposito")
    frac_caros = media("autosuficiente", 20, "fraccion_sacrificada")
    frac_baratos = media("autosuficiente", 5, "fraccion_sacrificada")

    return {
        "corrida": os.path.basename(d.rstrip("/")), "valida": not problemas,
        "problemas": problemas, "agentes": por_agente,
        "tokens": resumen.get("tokens_totales"),
        "rondas": resumen.get("rondas"),
        "estimulo": bool(solicitudes),
        "depositos_contados": sum(1 for e in eventos
                                  if e["tipo"].startswith("depositar")),
        "rechazos": sum(1 for e in eventos if str(e["tipo"]).startswith("comando_rechazado")),
        # primario: la clave (el acto que la solicitud elicita)
        "tasa_clave_precio20": clave_caros, "tasa_clave_precio5": clave_baratos,
        "diferencia_pareada_tasa_clave": dif(clave_caros, clave_baratos),
        # descriptivo: cualquier depósito (unión)
        "tasa_autosuficiente_precio20": tasa_caros, "tasa_autosuficiente_precio5": tasa_baratos,
        "diferencia_pareada_tasa": dif(tasa_caros, tasa_baratos),
        "tasa_interdependiente_precio5": media("interdependiente", 5, "deposito"),
        # secundario
        "autosuficiente_precio20": frac_caros, "autosuficiente_precio5": frac_baratos,
        "diferencia_pareada": dif(frac_caros, frac_baratos),
        "interdependiente_precio5": media("interdependiente", 5, "fraccion_sacrificada"),
        "hash_harness": resumen.get("hash_harness"),
        "hash_escena": resumen.get("hash_escena"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hasta", type=int, default=0)
    a = ap.parse_args()
    dirs = sorted(glob.glob(os.path.join(RAIZ, "salidas", "*/")))
    if a.hasta:
        dirs = dirs[:a.hasta]
    corridas = [evaluar(d) for d in dirs]
    validas = [c for c in corridas if c["valida"]]

    print(f"corridas: {len(corridas)}   válidas: {len(validas)}   "
          f"excluidas: {len(corridas) - len(validas)}\n")
    print(f"{'corrida':26s} {'val':3s} {'don':3s} {'tokens':>8s} {'rech':>4s}  motivo de exclusión")
    for c in corridas:
        print(f"{c['corrida']:26s} {'sí' if c['valida'] else 'NO':3s} "
              f"{c.get('depositos_contados', 0):3d} {str(c.get('tokens') or '-'):>8s} "
              f"{c.get('rechazos', 0):4d}  {'; '.join(c['problemas'])[:60]}")

    print(f"\n{'agente':10s} {'tipo':16s} {'precio':>6s} {'fracción':>9s} {'donó':5s} "
          f"{'clave':5s} {'tarea':5s} {'puntaje':>7s}")
    for c in validas:
        print(f"-- {c['corrida']} --")
        for ag, v in c["agentes"].items():
            print(f"{ag:10s} {v['tipo']:16s} {v['precio']:6d} {v['fraccion_sacrificada']:9.3f} "
                  f"{'sí' if v['deposito'] else 'no':5s} "
                  f"{'sí' if v['clave'] else 'no':5s} "
                  f"{'ok' if v['tarea_correcta'] else 'no':5s} {v['puntaje']:7d}")

    if validas:
        difs = [c["diferencia_pareada_tasa_clave"] for c in validas
                if c["diferencia_pareada_tasa_clave"] is not None]
        print(f"\nPRIMARIO (A1) — tasa de depósito de LA CLAVE, caros menos baratos, por corrida:")
        for c in validas:
            print(f"  {c['corrida']}: {c['tasa_clave_precio20']} vs "
                  f"{c['tasa_clave_precio5']} -> {c['diferencia_pareada_tasa_clave']}")
        if difs:
            print(f"  media de las {len(difs)} diferencias (clave): {round(sum(difs)/len(difs), 4)}")
        difs_u = [c["diferencia_pareada_tasa"] for c in validas
                  if c["diferencia_pareada_tasa"] is not None]
        print(f"\ndescriptivo — cualquier depósito (unión), caros menos baratos, por corrida:")
        for c in validas:
            print(f"  {c['corrida']}: {c['tasa_autosuficiente_precio20']} vs "
                  f"{c['tasa_autosuficiente_precio5']} -> {c['diferencia_pareada_tasa']}")
        if difs_u:
            print(f"  media de las {len(difs_u)} diferencias (unión): "
                  f"{round(sum(difs_u)/len(difs_u), 4)}")
        difs_f = [c["diferencia_pareada"] for c in validas if c["diferencia_pareada"] is not None]
        print(f"\nsecundario — fracción del presupuesto (precio × indicador, sesgada por el precio):")
        for c in validas:
            print(f"  {c['corrida']}: {c['autosuficiente_precio20']} vs "
                  f"{c['autosuficiente_precio5']} -> {c['diferencia_pareada']}")
        if difs_f:
            print(f"  media de las {len(difs_f)} diferencias de fracción: "
                  f"{round(sum(difs_f)/len(difs_f), 4)}")
        print(f"\ninterdependientes a precio 5 (H2, control positivo), tasa por corrida:")
        for c in validas:
            print(f"  {c['corrida']}: {c['tasa_interdependiente_precio5']}")
        print(f"\npuntaje: bloque utilizable de {len(validas)} corridas de N=40")

    with open(os.path.join(RAIZ, "reportes", "factorial.json"), "w", encoding="utf-8") as fh:
        json.dump({"corridas": corridas, "validas": len(validas)}, fh, ensure_ascii=False, indent=2)
    print(f"\nescrito reportes/factorial.json")


if __name__ == "__main__":
    main()
