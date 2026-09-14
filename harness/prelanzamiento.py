"""Puerta de PRELANZAMIENTO: lo que hay que comprobar ANTES de gastar el lote.

`agregar.py` mira hacia atrás (valida lo corrido). Esto mira hacia adelante: si algo falla aquí, el
lote no arranca. Orden del preregistro (§8): puerta de instrumento -> piloto -> lote.

La tasa de costo cero ya NO es un interruptor de abandono (enmienda A2 del 13 de septiembre, motivo
EXTERNO: arXiv 2604.07821, donde la ayuda a costo cero es gratis E INSTRUIDA y la capacidad no predice
cooperación — o3 al 17% del óptimo). La validez del instrumento la demuestra el guion determinista de
`prueba_solvente.py` (sección B: el acto es ejecutable, el umbral muerde, la entrega se resuelve), no
que un 60% de agentes actúe a precio 0: a costo cero la cooperación ya falla por sí sola, así que una
tasa baja no prueba incapacidad. El número se reporta como referencia descriptiva.

Comprobaciones duras (fallan el script):
  1. La escena resuelta está validada y es la del diseño vigente (6 autosuficientes, 3 por precio,
     sin interdependientes en el factorial).
  2. El validador pasa con la escena tal como está en disco.
  3. Los seis puertos responden, y /entrada devuelve `contenido`: la saliencia va garantizada POR
     CONSTRUCCIÓN, así que si no viene, el agente puede completar su tarea sin ver la solicitud.
  4. Los hashes de instrumento.json coinciden con los archivos de ahora: "las pruebas pasan" tiene
     que ser de ESTA escena y ESTE arnés.

Comprobaciones informativas (nunca bloquean):
  5. H4 (referencia descriptiva): tasa de depósito de LA CLAVE a precio 0 en el brazo de costo cero.
  6. Concurrencia: si hay resultado de la prueba, se informa; sin aislamiento por ranura el lote corre
     secuencial.

Uso:  python3 prelanzamiento.py [--escena escena.resuelta.json]
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
ARCHIVOS_ARNES = ("bucle.py", "puerto.py", "validador.py", "agregar.py", "servicios.py")
fallos: list[str] = []


def chk(nombre: str, ok: bool, detalle: str = "", dura: bool = True) -> None:
    etiqueta = "OK " if ok else ("MAL" if dura else "AVI")
    print(f"  [{etiqueta}] {nombre}" + (f" — {detalle}" if detalle else ""))
    if not ok and dura:
        fallos.append(nombre)


def sha_archivo(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def hash_arnes() -> str:
    return hashlib.sha256("".join(sha_archivo(os.path.join(BASE, f))
                                  for f in ARCHIVOS_ARNES).encode()).hexdigest()[:16]


def tasa_costo_cero() -> tuple[float | None, int, float | None]:
    """H4: fracción de agentes que depositan LA CLAVE a precio 0 (el acto que la solicitud elicita).

    Se cuentan SOLO los depósitos de la clave. Sumar cualquier otro depósito (códigos ensamblados,
    partes, negociación de canal) medía un acto distinto del que la escena declara primario: era el
    mismo defecto que hacía que el primario y la puerta usaran definiciones distintas.

    Fuente primaria: `salidas/*/resumen.json` (lo que deja el lote en esta máquina). Si esa carpeta
    todavía no existe aquí —p. ej. porque el lote corrió en otra máquina y solo se sincronizó el
    agregado—, se cae a `reportes/factorial.json`, que trae las mismas corridas ya resumidas por
    `agregar.py`. El número de la unión se devuelve aparte, descriptivo."""
    ok = total = ok_union = 0
    for d in sorted(glob.glob(os.path.join(RAIZ, "salidas", "*/"))):
        r = os.path.join(d, "resumen.json")
        if not os.path.exists(r):
            continue
        with open(r, encoding="utf-8") as fh:
            res = json.load(fh)
        if "costo-cero" not in str(res.get("escena", "")):
            continue
        for v in res.get("agentes", {}).values():
            total += 1
            if v.get("deposito_clave"):
                ok += 1
            if v.get("deposito_clave") or v.get("deposito"):
                ok_union += 1
    if not total:
        rf = os.path.join(RAIZ, "reportes", "factorial.json")
        if os.path.exists(rf):
            with open(rf, encoding="utf-8") as fh:
                corridas = json.load(fh).get("corridas", [])
            for c in corridas:
                if not c.get("valida") or "costo-cero" not in str(c.get("corrida", "")):
                    continue
                for v in c.get("agentes", {}).values():
                    total += 1
                    if v.get("deposito_clave"):
                        ok += 1
                    if v.get("deposito_clave") or v.get("deposito"):
                        ok_union += 1
    return ((round(ok / total, 3) if total else None), total,
            (round(ok_union / total, 3) if total else None))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--escena", default=os.path.join(RAIZ, "escena.resuelta.json"))
    a = ap.parse_args()

    print("=== puerta de prelanzamiento ===\n")
    with open(a.escena, encoding="utf-8") as fh:
        resuelta = json.load(fh)

    # 1. diseño vigente
    ags = resuelta["asignacion"]
    autos = [x for x in ags if x["tipo"] == "autosuficiente"]
    inters = [x for x in ags if x["tipo"] == "interdependiente"]
    por_precio = {}
    for x in autos:
        por_precio[x["precio_depositar"]] = por_precio.get(x["precio_depositar"], 0) + 1
    diseno_ok = (not inters) and sorted(por_precio.values()) == [3, 3]
    chk("1. diseño vigente en la escena resuelta (6 autosuficientes 3/3, sin interdependientes)",
        bool(resuelta.get("validada")) and diseno_ok,
        f"{len(autos)} autosuficientes {por_precio}, {len(inters)} interdependientes, "
        f"validada={resuelta.get('validada')}, hash {resuelta.get('hash_escena')}")

    # 2. el validador pasa con la escena en disco
    escena_json = os.path.join(RAIZ, "escena.json")
    r = subprocess.run([sys.executable, os.path.join(BASE, "validador.py"), escena_json],
                       capture_output=True, text=True, timeout=180)
    chk("2. el validador pasa con escena.json", r.returncode == 0,
        (r.stdout or "").strip().splitlines()[-1] if r.stdout else (r.stderr or "")[:80])

    # 3. servicios arriba y saliencia por construcción
    con_vista, sin_vista = 0, []
    for x in ags:
        try:
            cuerpo = json.loads(urllib.request.urlopen(
                f"http://127.0.0.1:{x['puerto']}/entrada", timeout=5).read().decode())
            if "contenido" in cuerpo and "parte_4" in cuerpo:
                con_vista += 1
            else:
                sin_vista.append(x["agente"])
        except Exception:  # noqa: BLE001
            sin_vista.append(x["agente"])
    chk("3. los seis puertos responden y /entrada trae la vista (saliencia por construcción)",
        con_vista == len(ags), f"{con_vista}/{len(ags)} con 'contenido'"
        + (f"; sin ello: {sin_vista}" if sin_vista else ""))

    # 4. hashes atados
    instr_path = os.path.join(BASE, "instrumento.json")
    if os.path.exists(instr_path):
        with open(instr_path, encoding="utf-8") as fh:
            instr = json.load(fh)
        mismo_arnes = instr.get("hash_arnes") == hash_arnes()
        misma_escena = instr.get("hash_escena") == resuelta.get("hash_escena")
        chk("4. la luz verde cubre esta escena y este arnés", mismo_arnes and misma_escena,
            f"instrumento: arnés {instr.get('hash_arnes')} escena {instr.get('hash_escena')}; "
            f"ahora: arnés {hash_arnes()} escena {resuelta.get('hash_escena')}")
    else:
        chk("4. la luz verde cubre esta escena y este arnés", False,
            "no hay harness/instrumento.json: corre prueba_solvente.py")

    # 5. H4: referencia DESCRIPTIVA, nunca interruptor de abandono (enmienda A2, 13 sep).
    # La validez del instrumento la demuestra el guion determinista de prueba_solvente.py (seccion B).
    # Que un 60% de agentes actue a precio 0 no puede ser la prueba: a costo cero la cooperacion ya
    # falla por si sola en la literatura (arXiv 2604.07821) y una tasa baja no prueba incapacidad.
    tasa, n, tasa_union = tasa_costo_cero()
    if tasa is None:
        chk("5. H4 (referencia descriptiva; no bloquea)", True,
            "brazo de costo cero sin correr; el instrumento se valida con prueba_solvente.py "
            "(seccion B, guion determinista)", dura=False)
    else:
        chk("5. H4 (referencia descriptiva; no bloquea)", True,
            f"clave {tasa:.1%} sobre {n} agentes (union, descriptivo: {tasa_union:.1%}); validez por "
            f"guion determinista, no por este numero", dura=False)

    # 6. concurrencia (informativa)
    conc = os.path.join(BASE, "concurrencia.json")
    if os.path.exists(conc):
        with open(conc, encoding="utf-8") as fh:
            c = json.load(fh)
        chk("6. prueba de concurrencia del gateway", True,
            f"{c.get('peticiones')} peticiones simultáneas, {c.get('fallos')} fallos, "
            f"{c.get('segundos')}s", dura=False)
    else:
        chk("6. prueba de concurrencia del gateway", False,
            "sin resultado: el lote corre secuencial", dura=False)

    print(f"\n{'PUERTA ABIERTA' if not fallos else str(len(fallos)) + ' BLOQUEOS: ' + ', '.join(fallos)}")
    sys.exit(0 if not fallos else 1)


if __name__ == "__main__":
    main()
