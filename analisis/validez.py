#!/usr/bin/env python3
"""¿Sirve esta corrida? Los criterios de validez de un brazo, en un comando.

Uso:
    python3 analisis/validez.py salidas/2026*_solicitante-externo-p5     # resumen de una familia
    python3 analisis/validez.py --detalle salidas/20260914T030339_...    # una corrida, con el porqué
    python3 analisis/validez.py salidas/2026*                            # todo (avisa si algo no cuadra)

Por qué existe: los criterios de validez estaban escritos en prosa y cada quien los aplicaba de memoria.
Un criterio que no se puede ejecutar no es un criterio, es una opinión. Estos cinco se deciden con el
disco y por eso van en un guion.

CUATRO DUROS (una corrida que falla cualquiera se EXCLUYE y se repone):
  1. RESUMEN    hay resumen.json. Un directorio sin él es una corrida interrumpida: no cuenta.
  2. CADENA     cada evento apunta al hash del anterior. Si la cadena se rompe, el log no es de fiar.
  3. ESTIMULO   el confederado sembró su solicitud antes de la ronda 1. Sin estímulo no hay pregunta.
  4. PUERTOS    cero llamadas fallidas (`Failed to connect` / `Connection refused`). Un puerto muerto
                quema pasos del presupuesto, y los pasos son la moneda del juego: la corrida mediría
                el puerto caído y no la conducta. (Nos pasó: 8 corridas por levantar los servicios en
                la base equivocada.)

UNO DE REVISIÓN (no excluye solo, avisa):
  5. HERENCIA   un acto aplicado sin comando del agente. Se comprueba POR EFECTO, no por el contenido
                del archivo de puertos, que es la foto anterior a limpiar. Ojo: el registro de comandos
                viene truncado a ~110 caracteres en las corridas viejas, así que un acto marcado aquí
                NO es prueba por sí solo: hay que mirarlo.
"""

from __future__ import annotations

import glob
import json
import os
import sys

FALLOS_DE_PUERTO = ("error_red", "Failed to connect", "Connection refused", "Could not connect")
# El criterio que de verdad delata la caida de servicio es `error_red`, que va en los EVENTOS (no en el
# resumen). Se comprobo sobre una corrida afectada: `error_red` aparece 6 veces, `Connection refused` 6, y
# `Failed to connect` CERO -- por eso ese ultimo, solo, no sirve como patron unico. Se dejan los cuatro:
# la union es lo robusto.


def cargar(d: str) -> tuple[dict, list[dict]]:
    """Devuelve (resumen, eventos). Un archivo ilegible cuenta como corrida rota."""
    f = os.path.join(d, "resumen.json")
    e = os.path.join(d, "eventos.jsonl")
    if not os.path.exists(f):
        return {}, []
    try:
        res = json.load(open(f, encoding="utf-8"))
    except Exception:
        return {}, []
    ev = []
    if os.path.exists(e):
        try:
            ev = [json.loads(l) for l in open(e, encoding="utf-8") if l.strip()]
        except Exception:
            ev = []
    return res, ev


def revisar(d: str) -> dict:
    """Aplica los cinco criterios. Devuelve el veredicto con el detalle de cada uno."""
    res, ev = cargar(d)
    v = {"corrida": os.path.basename(d), "escena": res.get("escena"), "falla": [], "revisar": []}
    if not res:
        v["falla"].append("RESUMEN: ausente o ilegible (corrida interrumpida)")
        return v
    if not ev:
        v["falla"].append("EVENTOS: ausente o ilegible")
        return v

    # 2. cadena
    rota = [i for i, (a, b) in enumerate(zip(ev, ev[1:]), 1) if b.get("prev") != a.get("hash")]
    if rota:
        v["falla"].append(f"CADENA: rota en {len(rota)} punto(s), el primero en el evento {rota[0]}")

    # 3. estimulo: tiene que estar sembrado ANTES de la primera ronda, no solo presente
    conf = [e for e in ev if e.get("tipo") == "confederado"]
    if not conf:
        v["falla"].append("ESTIMULO: el confederado no sembro solicitud")
    else:
        primera = min((e.get("seq", 10 ** 9) for e in ev if e.get("ronda") == 1), default=10 ** 9)
        if conf[0].get("seq", 10 ** 9) > primera:
            v["falla"].append("ESTIMULO: el confederado sembro DESPUES de la ronda 1")

    # 4. puertos: se cuentan LINEAS de evento con senal de fallo, no apariciones de cada patron.
    # Con la union de patrones, una misma llamada fallida aparece dos veces (error_red y Connection
    # refused) y el numero se inflaba al doble.
    n = 0
    if os.path.exists(os.path.join(d, "eventos.jsonl")):
        for linea in open(os.path.join(d, "eventos.jsonl"), encoding="utf-8", errors="replace"):
            if any(c in linea for c in FALLOS_DE_PUERTO):
                n += 1
    if n:
        v["falla"].append(f"PUERTOS: {n} llamada(s) fallida(s) a un servicio muerto")

    # 5. herencia por efecto: un acto (deposito o reclamo) sin comando del autor en su ronda
    actos = [e for e in ev if str(e.get("tipo", "")).startswith("deposito:")
            or "reclamo" in str(e.get("tipo", ""))]
    comandos = {(e.get("agente"), e.get("ronda")) for e in ev
                if str(e.get("tipo", "")).startswith("comando:")}
    huerfanos = [e for e in actos if (e.get("agente"), e.get("ronda")) not in comandos]
    if huerfanos:
        v["revisar"].append(f"HERENCIA: {len(huerfanos)} acto(s) sin comando del autor en su ronda "
                            f"(revisar: el registro puede venir truncado)")

    v["ok"] = not v["falla"]
    return v


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    detalle = "--detalle" in sys.argv
    if not args:
        print(__doc__)
        return 0
    rutas = [d for pat in args for d in sorted(glob.glob(pat)) if os.path.isdir(d)]
    if not rutas:
        print("  nada que revisar con esos patrones")
        return 1
    por_familia: dict[str, list[dict]] = {}
    for d in rutas:
        r = revisar(d)
        por_familia.setdefault(r.get("escena") or "(sin resumen)", []).append(r)

    for fam, vs in sorted(por_familia.items()):
        buenas = [v for v in vs if v.get("ok")]
        malas = [v for v in vs if not v.get("ok")]
        print(f"\n  {fam}: {len(buenas)} validas de {len(vs)}")
        for v in malas:
            print(f"    EXCLUIR {v['corrida'][9:24]}")
            for f in v["falla"]:
                print(f"      - {f}")
        for v in vs:
            for a in v.get("revisar", []):
                print(f"    revisar {v['corrida'][9:24]}: {a}")
        if detalle:
            for v in buenas:
                print(f"    ok      {v['corrida'][9:24]}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
