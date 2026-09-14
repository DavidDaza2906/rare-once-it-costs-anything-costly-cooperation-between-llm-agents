"""Estimador del desenlace primario, con IC95 por remuestreo POR CORRIDA (lo que pide el plan).

Reglas que respeta:
  - Nunca agrupa versiones distintas del instrumento (hash de escena + hash de textos). Una corrida
    con otro hash se reporta aparte: el arreglo del instrumento cambia el acto medido, y sumarlas
    mueve el numero sin que nadie lo note.
  - El acto medido se reporta con las DOS definiciones, la clave (respuesta a la solicitud) y la
    union (cualquier deposito), porque el equipo y el asistente no coinciden en cual es el primario.
    El numero queda listo para las dos lecturas; la decision es del equipo.
  - Excluye de N las corridas etiquetadas (ensayo, pre-migracion, prueba-de-instrumento).

Uso:  python3 analisis/estimador.py [--remuestreos 10000] [--json reportes/estimaciones.json]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import statistics

def _raiz_del_proyecto() -> str:
    """Sube desde este archivo hasta encontrar el proyecto (escena.resuelta.json).

    Asi el guion funciona igual desde analisis/ que desde cualquier otro directorio.
    """
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d) and not os.path.exists(os.path.join(d, "escena.resuelta.json")):
        d = os.path.dirname(d)
    return d


RAIZ = _raiz_del_proyecto()


def wilson(k: int, n: int, z: float = 1.96) -> list[float] | None:
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    semi = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(max(0.0, centro - semi), 4), round(min(1.0, centro + semi), 4)]


def bootstrap(difs: list[float], remuestreos: int, semilla: int = 20260913) -> list[float] | None:
    """IC95 por remuestreo de las corridas (el plan pide 10.000). Semilla fija: reproducible."""
    if not difs:
        return None
    rnd = random.Random(semilla)
    medias = []
    for _ in range(remuestreos):
        s = [rnd.choice(difs) for _ in difs]
        medias.append(sum(s) / len(s))
    medias.sort()
    return [round(medias[int(0.025 * remuestreos)], 4), round(medias[int(0.975 * remuestreos)], 4)]


def cargar() -> list[dict]:
    rutas = glob.glob(os.path.join(RAIZ, "salidas", "*", "resumen.json"))
    rutas += glob.glob(os.path.join(RAIZ, "salidas", "*", "*", "resumen.json"))
    out = []
    for r in sorted(rutas):
        carpeta = os.path.dirname(r)
        rel = os.path.relpath(carpeta, os.path.join(RAIZ, "salidas"))
        try:
            with open(r, encoding="utf-8") as fh:
                res = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        ags = res.get("agentes") or {}
        if len(ags) != 6:
            continue
        # Validez técnica antes que aritmética: una corrida truncada por el tope de tokens, o con la
        # cadena de hash rota, no mide conducta. Se excluye aquí para que la cuenta coincida con el
        # control entre bloques (reportes/control-lote.json).
        try:
            ev = [json.loads(l) for l in open(os.path.join(carpeta, "eventos.jsonl"),
                                              encoding="utf-8") if l.strip()]
        except (OSError, json.JSONDecodeError):
            continue
        if any(e.get("tipo") == "tope_tokens" for e in ev):
            continue
        if not all(b.get("prev") == a.get("hash") for a, b in zip(ev, ev[1:])):
            continue
        out.append({
            "corrida": rel,
            "etiqueta": res.get("etiqueta") or (rel.split("/")[0] if "/" in rel else ""),
            "brazo": "costo-cero" if "costo-cero" in os.path.basename(carpeta) else "factorial",
            "hash_escena": res.get("hash_escena"),
            "hash_textos": res.get("hash_textos"),
            "tokens": res.get("tokens_totales"),
            "agentes": [{"id": k, **v} for k, v in ags.items()],
        })
    return out


def celda(corridas: list[dict], precio: int, campo: str) -> dict:
    vals = [1 if a.get(campo) else 0 for c in corridas for a in c["agentes"]
            if a.get("precio_depositar") == precio]
    k, n = sum(vals), len(vals)
    return {"k": k, "n": n, "tasa": round(k / n, 4) if n else None, "ic_wilson": wilson(k, n)}


def diferencias(corridas: list[dict], campo: str) -> list[float]:
    """Diferencia pareada por corrida: tasa al precio 20 menos tasa al precio 5."""
    out = []
    for c in corridas:
        caros = [1 if a.get(campo) else 0 for a in c["agentes"] if a.get("precio_depositar") == 20]
        baratos = [1 if a.get(campo) else 0 for a in c["agentes"] if a.get("precio_depositar") == 5]
        if caros and baratos:
            out.append(sum(caros) / len(caros) - sum(baratos) / len(baratos))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remuestreos", type=int, default=10000)
    ap.add_argument("--json", default=os.path.join(RAIZ, "reportes", "estimaciones.json"))
    a = ap.parse_args()

    corridas = cargar()
    grupos: dict[tuple, list[dict]] = {}
    for c in corridas:
        grupos.setdefault((c["hash_escena"], c["hash_textos"], c["brazo"], c["etiqueta"] or ""),
                          []).append(c)

    resumen = {"remuestreos": a.remuestreos, "grupos": []}
    print(f"corridas con diseno de 6 agentes: {len(corridas)}\n")
    for (h_esc, h_txt, brazo, etq), grupo in sorted(grupos.items(), key=lambda x: -len(x[1])):
        n_ag = sum(len(c["agentes"]) for c in grupo)
        tokens = sum((c["tokens"] or 0) for c in grupo)
        print(f"--- {brazo} | etiqueta: {etq or 'lote'} | {len(grupo)} corridas, {n_ag} agentes, "
              f"{tokens:,} tokens")
        print(f"    hash escena {str(h_esc)[:8]} textos {str(h_txt)[:8]}")
        g = {"brazo": brazo, "etiqueta": etq or None, "corridas": len(grupo), "agentes": n_ag,
             "tokens": tokens, "hash_escena": h_esc, "hash_textos": h_txt,
             "corridas_lista": [c["corrida"] for c in grupo]}

        if brazo == "factorial":
            for campo, nombre in (("deposito_clave", "LA CLAVE (respuesta a la solicitud)"),
                                  ("deposito", "cualquier deposito (union)")):
                c5, c20 = celda(grupo, 5, campo), celda(grupo, 20, campo)
                difs = diferencias(grupo, campo)
                m = round(statistics.mean(difs), 4) if difs else None
                ic = bootstrap(difs, a.remuestreos)
                cruza = ic and ic[0] <= 0 <= ic[1]
                print(f"    {nombre}")
                print(f"      precio 5:  {c5['k']}/{c5['n']} = {c5['tasa']}  IC95 {c5['ic_wilson']}")
                print(f"      precio 20: {c20['k']}/{c20['n']} = {c20['tasa']}  IC95 {c20['ic_wilson']}")
                print(f"      H1 (20-5) por corrida: media {m}  IC95 bootstrap {ic}"
                      f"{'  <- incluye cero' if cruza else ''}")
                print(f"      direccion: {sum(1 for d in difs if d<0)} barato / "
                      f"{sum(1 for d in difs if d==0)} empate / {sum(1 for d in difs if d>0)} caro")
                g[campo] = {"precio5": c5, "precio20": c20, "diferencias": [round(d, 4) for d in difs],
                            "media_H1": m, "ic_bootstrap": ic, "incluye_cero": bool(cruza)}
        else:
            for campo, nombre in (("deposito_clave", "la clave"), ("deposito", "union")):
                vals = [1 if a.get(campo) else 0 for c in grupo for a in c["agentes"]]
                k, n = sum(vals), len(vals)
                print(f"    {nombre}: {k}/{n} = {round(k/n,4) if n else None} IC95 {wilson(k,n)}")
                g[campo] = {"k": k, "n": n, "tasa": round(k / n, 4) if n else None,
                            "ic_wilson": wilson(k, n)}
        resumen["grupos"].append(g)
        print()

    os.makedirs(os.path.dirname(a.json), exist_ok=True)
    with open(a.json, "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, ensure_ascii=False, indent=2)
    print(f"escrito {os.path.relpath(a.json, RAIZ)}")


if __name__ == "__main__":
    main()
