"""Fija el CONJUNTO congelado: la lista explícita de corridas que entran en el análisis final.

Por qué hace falta. "N=128" es un conteo, no un conjunto: si siguen cayendo corridas después de
congelar —y aquí siguen cayendo— nadie puede decir después *cuáles* 128 se usaron, y el análisis deja
de ser reproducible. Este guion escribe la lista ordenada de nombres de corrida con sus hashes, y un
SHA-256 de la lista misma. A partir de ahí, "el conjunto congelado" es un archivo, no una hora.

Qué NO hace, a propósito: no calcula ninguna tasa ni ningún contraste. Se puede correr antes del
análisis sin gastar la mirada única. Sólo mira identidad y validez técnica.

Criterios de validez, los mismos de `agregar.py` y `exploratorios.py`:
  sin `resumen.json` · ≠6 agentes · saldo negativo · truncada por tope · sin estímulo del confederado ·
  `error_red` (servicio caído: el agente intentó depositar y le rebotó) · `hash_textos` ≠ el del lote.

Uso:
  python3 herramientas/fijar_conjunto.py --familia factorial-base --n 128
  python3 herramientas/fijar_conjunto.py --familia factorial-base --n 128 --confirmar
Sin `--confirmar` sólo muestra lo que haría. Salida: reportes/conjunto-congelado.json
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAICES = [RAIZ] + [r for r in ("/home/daw/Sprint-2",) if os.path.isdir(os.path.join(r, "salidas"))]


def revisar(d: str, hash_tarea: str | None) -> tuple[list[str], dict]:
    """Devuelve (problemas, datos de identidad). Nunca lee desenlaces."""
    rp = os.path.join(d, "resumen.json")
    if not os.path.exists(rp):
        return ["sin resumen"], {}
    r = json.load(open(rp, encoding="utf-8"))
    prob = []
    ags = r.get("agentes") or {}
    if len(ags) != 6:
        prob.append(f"{len(ags)} agentes")
    ev_p = os.path.join(d, "eventos.jsonl")
    ev = [json.loads(x) for x in open(ev_p, encoding="utf-8") if x.strip()] if os.path.exists(ev_p) else []
    if any(e.get("tipo") == "tope_tokens" for e in ev):
        prob.append("truncada")
    n_red = sum(1 for e in ev if e.get("tipo") == "error_red")
    if n_red:
        prob.append(f"servicio caído ({n_red})")
    # Centinela de la suite de validacion: la corrida contabilizo un acto que NINGUN sujeto hizo (los
    # depositos de prueba de la suite de instrumento entraron en su ronda). Se caza solo con este texto:
    # en la corrida 021758 aparece 1 vez, mientras error_red, 'Connection refused' y 'Failed to connect'
    # dan cero, y su hash_textos es el del lote, asi que ningun otro criterio la ve.
    _t = open(ev_p, encoding="utf-8", errors="replace").read() if os.path.exists(ev_p) else ""
    if "clave por la via del servicio" in _t:
        prob.append("contaminacion (acto de la suite de validacion)")
    if not all(b.get("prev") == a.get("hash") for a, b in zip(ev, ev[1:])):
        prob.append("cadena rota")
    bp = os.path.join(d, "presupuesto.json")
    if os.path.exists(bp):
        lib = json.load(open(bp, encoding="utf-8"))
        if [x for x, v in lib.get("restante", {}).items() if v < 0]:
            prob.append("saldo negativo")
    if not any(x.get("via") == "confederado" for x in r.get("depositos", [])):
        prob.append("sin estímulo")
    if hash_tarea and r.get("hash_textos") != hash_tarea:
        prob.append(f"hash_textos {str(r.get('hash_textos'))[:8]} ≠ lote")
    return prob, {"corrida": os.path.basename(d.rstrip("/")),
                  "hash_escena": r.get("hash_escena"), "hash_textos": r.get("hash_textos"),
                  "ultimo_hash": r.get("ultimo_hash"), "tokens": r.get("tokens_totales")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--familia", default="factorial-base")
    ap.add_argument("--n", type=int, default=None, help="cuántas tomar (las N primeras por hora); todas si se omite")
    ap.add_argument("--hash-tarea", default="4e8f2619ed0966ec")
    ap.add_argument("--confirmar", action="store_true", help="escribir el archivo; sin esto sólo muestra")
    a = ap.parse_args()

    cands, vistos = [], set()
    for raiz in RAICES:
        cands += glob.glob(os.path.join(raiz, "salidas", f"2026*_{a.familia}/"))
    validas, excluidas = [], []
    for d in sorted(cands, key=lambda x: os.path.basename(x.rstrip("/"))):
        nom = os.path.basename(d.rstrip("/"))
        if nom in vistos:
            continue
        vistos.add(nom)
        prob, ident = revisar(d, a.hash_tarea)
        (excluidas if prob else validas).append(
            {"corrida": nom, "motivos": prob} if prob else ident)

    tomadas = validas[:a.n] if a.n else validas
    lista = "\n".join(x["corrida"] for x in tomadas)
    sha = hashlib.sha256(lista.encode()).hexdigest()

    salida = {
        "familia": a.familia, "hash_tarea": a.hash_tarea,
        "fijado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_objetivo": a.n, "n_validas_disponibles": len(validas), "n_congeladas": len(tomadas),
        "sha256_de_la_lista": sha,
        "regla": "las N primeras corridas válidas por hora de arranque; la validez es técnica y se "
                 "decide sin mirar ningún desenlace",
        "criterios_de_exclusion": ["sin resumen", "≠6 agentes", "truncada por tope", "error_red "
                                   "(servicio caído)", "cadena rota", "saldo negativo",
                                   "sin estímulo", "hash_textos ≠ lote",
                                   "contaminación por la suite de validación (un acto contabilizado "
                                   "que ningún sujeto hizo; se caza por el texto 'clave por la via "
                                   "del servicio', invisible a todos los demás criterios)"],
        "hashes_de_escena": sorted({x.get("hash_escena") for x in tomadas if x.get("hash_escena")}),
        "corridas": tomadas,
        "excluidas": excluidas,
    }

    print(f"familia {a.familia}: {len(validas)} válidas disponibles, {len(excluidas)} excluidas")
    if a.n and len(validas) < a.n:
        print(f"  AVISO: se pidieron {a.n} y sólo hay {len(validas)}. No se fija nada todavía.")
    print(f"  se congelarían {len(tomadas)}: de {tomadas[0]['corrida'][:15]} a {tomadas[-1]['corrida'][:15]}"
          if tomadas else "  no hay corridas")
    hs = salida["hashes_de_escena"]
    print(f"  hash_escena {'ÚNICO ' + hs[0][:16] if len(hs) == 1 else 'MÚLTIPLE ' + str(hs)}")
    print(f"  sha256 de la lista: {sha[:16]}")
    if excluidas:
        print("  excluidas:")
        for x in excluidas[:12]:
            print(f"    {x['corrida'][:15]}: {', '.join(x['motivos'])}")

    if not a.confirmar:
        print("\n(simulacro: añade --confirmar para escribir reportes/conjunto-congelado.json)")
        return
    if a.n and len(validas) < a.n:
        print("\nno se escribe nada: faltan corridas")
        return
    os.makedirs(os.path.join(RAIZ, "reportes"), exist_ok=True)
    dest = os.path.join(RAIZ, "reportes", "conjunto-congelado.json")
    if os.path.exists(dest):
        print(f"\nYA EXISTE {dest} — no se sobrescribe. Bórralo a mano si de verdad quieres refijar.")
        return
    json.dump(salida, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nescrito reportes/conjunto-congelado.json  ({len(tomadas)} corridas, sha {sha[:16]})")


if __name__ == "__main__":
    main()
