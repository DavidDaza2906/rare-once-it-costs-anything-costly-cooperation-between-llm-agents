"""Analisis del mini-piloto: los indicadores que dicen si el instrumento corregido se comporta.

No mira hipotesis: mira si el instrumento es de fiar ahora que esta arreglado.
  I1  doble cobro: cada deposito de la clave cuesta UNA vez (entradas unicas por agente+texto).
  I2  empaquetado: los agentes reconocen la parte como parte_4 y no dicen que no viene.
  I3  friccion: cuantos comandos se rechazan.
  I4  tarea completada (indicador de exito del arreglo: > 60%).
  I5  cadena de saliencia: leyo el almacen -> menciono la solicitud -> leyo su clave -> deposito.
  I6  taxonomia del deposito: la clave (el acto medido) contra los demas.

Uso:  python3 mini_analisis.py [etiqueta]
"""
from __future__ import annotations

import collections
import glob
import json
import os
import sys

RAIZ = "/home/daw/Sprint"
ETIQUETA = sys.argv[1] if len(sys.argv) > 1 else "mini-piloto"


def cargar() -> list[tuple[str, dict, str]]:
    """Por etiqueta, o las N corridas más recientes del factorial si ETIQUETA es un número.

    Las corridas del lote no llevan la etiqueta en el nombre del directorio (lo lleva el archivo
    `salidas/lote_<etiqueta>_*.json`), así que para mirar un lote en curso se piden las últimas N.
    """
    dirs = sorted(glob.glob(os.path.join(RAIZ, "salidas", "*/")))
    if ETIQUETA.isdigit():
        # solo las que ya tienen resumen.json: una corrida en curso no debe desplazar la ventana
        dirs = [x for x in dirs if "factorial-base" in x
                and os.path.exists(os.path.join(x, "resumen.json"))][-int(ETIQUETA):]
    out = []
    for d in dirs:
        r = os.path.join(d, "resumen.json")
        if not os.path.exists(r) or (not ETIQUETA.isdigit() and ETIQUETA not in d):
            continue
        with open(r, encoding="utf-8") as fh:
            out.append((os.path.basename(d.rstrip("/")), json.load(fh), d))
    return out


def leer_transcripcion(d: str, agente: str) -> list[dict]:
    msgs: list[dict] = []
    for f in sorted(glob.glob(os.path.join(d, "transcripciones", f"*_{agente}.json"))):
        try:
            with open(f, encoding="utf-8") as fh:
                x = json.load(fh)
        except json.JSONDecodeError:
            continue
        msgs.extend(x if isinstance(x, list) else x.get("mensajes", []))
    return msgs


def main() -> None:
    corridas = cargar()
    print(f"=== mini-piloto: {len(corridas)} corridas ({ETIQUETA}) ===\n")
    if not corridas:
        raise SystemExit("sin corridas con esa etiqueta")

    tot_ag = tot_ok = tot_dep = tot_dup = tot_rech = tot_tok = tot_def = 0
    tot_cupo = 0
    claves_dep: list[str] = []
    for nombre, res, d in corridas:
        ags = res["agentes"]
        ev = [json.loads(l) for l in open(os.path.join(d, "eventos.jsonl"), encoding="utf-8")]
        depos = res.get("depositos") or []
        cnt = collections.Counter((x["agente"], x["texto"].strip())
                                  for x in depos if x["agente"] != "externo")
        # Defecto de doble cobro: la MISMA línea del servicio contada dos veces. La firma exacta es
        # una entrada por herramienta y otra por la vía HTTP con el mismo texto y la misma ronda. Un
        # agente que deposita dos veces POR SU CUENTA (dos entradas sin `via`) no es un defecto: son
        # dos actos, cada uno cobrado una vez.
        dep_ag = [x for x in depos if x["agente"] != "externo"]
        defecto = []
        for (ag2, txt), _n in cnt.items():
            vias = [x.get("via") for x in dep_ag if x["agente"] == ag2 and x["texto"].strip() == txt]
            if None in vias and "http" in vias:
                defecto.append((ag2, txt))
        dups = {k: v for k, v in cnt.items() if v > 1} if defecto else {}
        tot_def += len(defecto)
        rech = sum(1 for e in ev if e["tipo"].startswith("comando_rechazado"))
        # cupo agotado: alguna ronda en la que el agente gastó sus 8 acciones de comando
        por_ronda: collections.Counter = collections.Counter()
        for e in ev:
            if e.get("agente") and e["tipo"].startswith(("comando", "entregar")):
                por_ronda[(e["agente"], e.get("ronda"))] += 1
        cupo = len({ag for (ag, _r), n in por_ronda.items() if n >= 8})
        oks = [n for n, a in ags.items() if a["tarea_correcta"]]
        cl = [n for n, a in ags.items() if a.get("deposito_clave")]

        tot_ag += len(ags); tot_ok += len(oks); tot_dep += len(cnt); tot_dup += sum(
            v - 1 for v in dups.values()); tot_rech += rech
        tot_tok += res.get("tokens_totales") or 0; tot_cupo += cupo
        claves_dep += cl

        print(f"--- {nombre[9:]}  tokens {res.get('tokens_totales'):,}  "
              f"tarea {len(oks)}/{len(ags)}  claves {len(cl)}  rechazos {rech}")
        orden = sorted(ags, key=lambda n: (ags[n]["precio_depositar"], n))
        for n in orden:
            a = ags[n]
            msgs = leer_transcripcion(d, n)
            texto = " ".join(str(m.get("texto") or "") for m in msgs)
            reconocio = "parte_4" in texto or "parte4" in texto.lower()
            nego = ("no suministrada" in texto.lower() or "no viene" in texto.lower()
                    or "no se observ" in texto.lower() and "parte" in texto.lower())
            print(f"    {n} p{a['precio_depositar']:2d}: tarea={'ok ' if a['tarea_correcta'] else 'no '} "
                  f"clave={'si' if a.get('deposito_clave') else 'no'} "
                  f"dep={'si' if a['deposito'] else 'no'} gastado={a['gastado']:2d} "
                  f"puntaje={a['puntaje']:3d} | nombra parte_4={'si' if reconocio else 'no'}"
                  f"{'  DICE-QUE-NO-VIENE' if nego else ''}")
        if dups:
            print(f"    !! DEPOSITOS REPETIDOS (doble cobro): {dups}")

    print(f"\n=== indicadores ===")
    print(f"  I1 doble cobro: {tot_dep} depositos del agente, {tot_def} con la firma del defecto "
          f"(herramienta + http del mismo acto) -> {'LIMPIO' if tot_def == 0 else 'SIGUE EL DEFECTO'}")
    pct = 100 * tot_ok / tot_ag if tot_ag else 0
    print(f"  I4 tarea completada: {tot_ok}/{tot_ag} = {pct:.1f}% "
          f"-> {'PASA (>60%)' if pct > 60 else 'NO ALCANZA el 60%'}")
    print(f"  I3 rechazos de comando: {tot_rech} en {len(corridas)} corridas "
          f"({tot_rech / max(1, len(corridas)):.1f} por corrida)")
    print(f"  I6 depositos de la clave (el acto medido): {len(claves_dep)} "
          f"de {tot_ag} agentes = {100 * len(claves_dep) / max(1, tot_ag):.1f}%")
    print(f"  agentes que agotaron el cupo de acciones: {tot_cupo}/{tot_ag}")
    print(f"  tokens totales: {tot_tok:,} ({tot_tok / max(1, tot_ag):.0f} por agente)")


if __name__ == "__main__":
    main()
