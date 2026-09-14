"""Analisis del brazo EXPLORATORIO de generalizacion de modelos (via OpenRouter).

No es el confirmatorio (H1, N=80, solo glm-5.3-flash): esto solo dice si el patron de la
celda 3 vs 4 (autosuficiente, precio 5 vs 20) se repite, se aplana o se invierte con otros
modelos. Ninguna cifra de aqui reemplaza ni pesa igual que el numero confirmatorio.

Lee salidas-generalizacion/ (nunca salidas/, que es el lote confirmatorio) y usa evaluar()
de harness/agregar.py para no duplicar la logica de validez (saldo negativo, sin estimulo,
donacion no contada, truncamiento). El modelo de cada corrida se identifica por los manifiestos
salidas-generalizacion/lote_generalizacion-<modelo>_*.json (campo "detalle[].log"); la unica
corrida sin manifiesto (DeepSeek V4.1 Flash, cortada por tiempo tras 1 corrida) se declara a
mano abajo.

Uso: python3 analisis/generalizacion.py [--json reportes/generalizacion.json]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
sys.path.insert(0, os.path.join(RAIZ, "harness"))
sys.path.insert(0, BASE)

from agregar import evaluar  # noqa: E402
from estimador import wilson, bootstrap  # noqa: E402

SALIDAS = os.path.join(RAIZ, "salidas-generalizacion")

# Corridas sin manifiesto de lote (lanzamientos cortados antes de escribir el resumen del lote).
SIN_MANIFIESTO = {
    "20260914T002329_factorial-base": "deepseek/deepseek-v4.1-flash",
}

MODELOS = {
    "gpt54": "openai/gpt-5.4",
    "gemini": "google/gemini-3.1-flash-lite",
    "deepseek": "deepseek/deepseek-v4.1-flash",
    "haiku": "anthropic/claude-haiku-4.5",
    "mistral": "mistralai/mistral-small-2603",
    "grok": "x-ai/grok-4.3",
    "cohere": "cohere/command-r-08-2024",
}


def mapa_carpeta_modelo() -> dict[str, str]:
    mapa = dict(SIN_MANIFIESTO)
    for f in glob.glob(os.path.join(SALIDAS, "lote_generalizacion-*.json")):
        with open(f, encoding="utf-8") as fh:
            lote = json.load(fh)
        etiqueta = lote.get("etiqueta", "")
        clave = etiqueta.replace("generalizacion-", "")
        modelo = MODELOS.get(clave, clave)
        for item in lote.get("detalle", []):
            carpeta = os.path.basename(os.path.dirname(item["log"]))
            mapa[carpeta] = modelo
    return mapa


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remuestreos", type=int, default=10000)
    ap.add_argument("--json", default=os.path.join(RAIZ, "reportes", "generalizacion.json"))
    a = ap.parse_args()

    mapa = mapa_carpeta_modelo()
    por_modelo: dict[str, list[dict]] = {}
    huerfanas = []
    for d in sorted(glob.glob(os.path.join(SALIDAS, "*/"))):
        carpeta = os.path.basename(d.rstrip("/"))
        modelo = mapa.get(carpeta)
        if modelo is None:
            huerfanas.append(carpeta)
            continue
        c = evaluar(d)
        por_modelo.setdefault(modelo, []).append(c)

    if huerfanas:
        print(f"AVISO: {len(huerfanas)} carpeta(s) sin modelo identificado, no entran al "
              f"analisis: {', '.join(huerfanas)}\n")

    resumen = {"nota": "EXPLORATORIO, no confirmatorio (ver docstring)", "modelos": []}
    print("=== Generalizacion de modelos (exploratorio, via OpenRouter) ===\n")
    for modelo, corridas in sorted(por_modelo.items(), key=lambda x: -len(x[1])):
        validas = [c for c in corridas if c["valida"]]
        tokens = sum((c.get("tokens") or 0) for c in corridas)
        print(f"--- {modelo} | {len(corridas)} corridas ({len(validas)} validas) | "
              f"{tokens:,} tokens | {tokens/len(corridas):,.0f} prom/corrida")
        entrada = {
            "modelo": modelo, "corridas": len(corridas), "validas": len(validas),
            "tokens_totales": tokens,
            "tokens_promedio": round(tokens / len(corridas), 0) if corridas else None,
            "corridas_lista": [c["corrida"] for c in corridas],
            "excluidas": [{"corrida": c["corrida"], "problemas": c["problemas"]}
                          for c in corridas if not c["valida"]],
        }
        if len(validas) < 2:
            print("    menos de 2 corridas validas: se reportan solo tokens, sin tasas\n")
            resumen["modelos"].append(entrada)
            continue

        # Tarea completada, y el confundidor de capacidad sobrante: ¿el que FALLA su propia tarea
        # ayuda mas? Si es asi, la tasa de "ayuda" no mide disposicion, mide agentes distraidos o
        # sin nada que perder. El mismo confundidor que ya documenta el confirmatorio.
        agentes = [a for c in validas for a in c["agentes"].values()
                   if a["tipo"] == "autosuficiente"]
        ok = [a for a in agentes if a["tarea_correcta"]]
        no_ok = [a for a in agentes if not a["tarea_correcta"]]
        entrada["tarea"] = {"ok": len(ok), "n": len(agentes),
                             "tasa": round(len(ok) / len(agentes), 4) if agentes else None}
        entrada["clave_por_capacidad"] = {
            "completo_tarea": {"k": sum(1 for a in ok if a["clave"]), "n": len(ok)},
            "fallo_tarea": {"k": sum(1 for a in no_ok if a["clave"]), "n": len(no_ok)},
        }
        print(f"    tarea completada: {entrada['tarea']['ok']}/{entrada['tarea']['n']}")
        cpc = entrada["clave_por_capacidad"]
        print(f"    ayudo Y completo su tarea:  {cpc['completo_tarea']['k']}/{cpc['completo_tarea']['n']}")
        print(f"    ayudo Y fallo su tarea:     {cpc['fallo_tarea']['k']}/{cpc['fallo_tarea']['n']}")

        for campo, nombre in (("clave", "LA CLAVE (respuesta a la solicitud)"),
                              ("deposito", "cualquier deposito (union)")):
            vals5 = [1 if a[campo] else 0 for c in validas for a in c["agentes"].values()
                     if a["tipo"] == "autosuficiente" and a["precio"] == 5]
            vals20 = [1 if a[campo] else 0 for c in validas for a in c["agentes"].values()
                      if a["tipo"] == "autosuficiente" and a["precio"] == 20]
            k5, n5 = sum(vals5), len(vals5)
            k20, n20 = sum(vals20), len(vals20)
            difs = []
            for c in validas:
                caros = [1 if a[campo] else 0 for a in c["agentes"].values()
                         if a["tipo"] == "autosuficiente" and a["precio"] == 20]
                baratos = [1 if a[campo] else 0 for a in c["agentes"].values()
                           if a["tipo"] == "autosuficiente" and a["precio"] == 5]
                if caros and baratos:
                    difs.append(sum(caros) / len(caros) - sum(baratos) / len(baratos))
            media = round(sum(difs) / len(difs), 4) if difs else None
            ic = bootstrap(difs, a.remuestreos) if difs else None
            print(f"    {nombre}")
            print(f"      precio 5:  {k5}/{n5} = {round(k5/n5,4) if n5 else None}  "
                  f"IC95 {wilson(k5,n5)}")
            print(f"      precio 20: {k20}/{n20} = {round(k20/n20,4) if n20 else None}  "
                  f"IC95 {wilson(k20,n20)}")
            print(f"      diferencia (20-5) por corrida: media {media}  IC95 bootstrap {ic}")
            entrada[campo] = {
                "precio5": {"k": k5, "n": n5, "tasa": round(k5/n5, 4) if n5 else None,
                            "ic_wilson": wilson(k5, n5)},
                "precio20": {"k": k20, "n": n20, "tasa": round(k20/n20, 4) if n20 else None,
                             "ic_wilson": wilson(k20, n20)},
                "diferencias_por_corrida": [round(d, 4) for d in difs],
                "media_diferencia": media, "ic_bootstrap": ic,
            }
        print()
        resumen["modelos"].append(entrada)

    os.makedirs(os.path.dirname(a.json), exist_ok=True)
    with open(a.json, "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, ensure_ascii=False, indent=2)
    print(f"escrito {os.path.relpath(a.json, RAIZ)}")


if __name__ == "__main__":
    main()
