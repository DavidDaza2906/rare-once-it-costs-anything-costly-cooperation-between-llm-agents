"""Prueba del mecanismo de excepciones declaradas. NO gasta tokens, NO usa puertos.

Lo que prueba, que es lo que hace que una excepción no sea una puerta trasera:
  1. una escena CON declaración válida y lo dice;
  2. la MISMA escena SIN la declaración falla — la excepción nunca es silenciosa;
  3. una declaración sin razón no cuenta;
  4. las escenas que ya validaban (el factorial) siguen validando igual.

Uso:  python3 harness/prueba_waivers.py
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
PY = sys.executable
fallos = []


def afirma(cond, texto):
    print(f"  {'OK  ' if cond else 'FALLA'} {texto}")
    if not cond:
        fallos.append(texto)


def valida(escena: dict, tmp: str, nombre: str = "caso") -> str:
    """Corre el validador sobre un dict y devuelve su salida."""
    ruta = os.path.join(tmp, f"{nombre}.json")
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(escena, fh, ensure_ascii=False)
    r = subprocess.run([PY, os.path.join(BASE, "validador.py"), ruta,
                        os.path.join(tmp, f"{nombre}.resuelta.json")],
                       capture_output=True, text=True, cwd=RAIZ)
    return r.stdout + r.stderr


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        # --- 1 y 2: I10 declarado en la escena del reclutador ---
        rec = json.load(open(os.path.join(RAIZ, "escena-reclutador.json"), encoding="utf-8"))
        salida_rec = valida(rec, tmp, "rec")
        afirma("VÁLIDA" in salida_rec and "INVÁLIDA" not in salida_rec,
               "el reclutador R1a pasa los invariantes SIN necesitar excepcion")
        rec_waiver = copy.deepcopy(rec)
        rec_waiver["waivers"] = [{"invariante": "I10", "razon": "prueba del mecanismo"}]
        salida_rw = valida(rec_waiver, tmp, "rec_w")
        afirma("VÁLIDA" in salida_rw,
               "una declaracion que no hace falta tampoco rompe nada")

        # --- 3 y 4: la solo-reserva (I10 suspendido) y el factorial intacto ---
        sola = os.path.join(RAIZ, "escena-abstencion-sola.json")
        if os.path.exists(sola):
            s = json.load(open(sola, encoding="utf-8"))
            afirma(any(w.get("invariante") == "I10" for w in (s.get("waivers") or [])),
                   "la solo-reserva declara el waiver de I10 (suspende el estimulo a proposito)")
            salida_sola = valida(s, tmp, "sola")
            afirma("VÁLIDA" in salida_sola and "INVÁLIDA" not in salida_sola,
                   "con la declaracion, la solo-reserva ES valida")
            afirma("DECLARADO I10" in salida_sola, "y la salida dice DECLARADO, no FALLA")

            sola_sin = copy.deepcopy(s)
            sola_sin.pop("waivers", None)
            salida_ss = valida(sola_sin, tmp, "sola_sin")
            afirma("INVÁLIDA" in salida_ss and "FALLA I10" in salida_ss,
                   "sin la declaracion, la MISMA escena es INVÁLIDA por I10")

            sola_sr = copy.deepcopy(s)
            sola_sr["waivers"] = [{"invariante": "I10", "razon": "   "}]
            salida_sr = valida(sola_sr, tmp, "sola_sr")
            afirma("INVÁLIDA" in salida_sr,
                   "una declaracion SIN razon no vale: la escena es INVÁLIDA")
        fac = json.load(open(os.path.join(RAIZ, "escena.json"), encoding="utf-8"))
        salida_fac = valida(fac, tmp, "factorial")
        afirma("VÁLIDA" in salida_fac and "FALLA" not in salida_fac,
               "el factorial (sin declaraciones) sigue validando igual")

    print()
    if fallos:
        print(f"  {len(fallos)} FALLOS")
        raise SystemExit(1)
    print("  excepciones declaradas: APTO")


if __name__ == "__main__":
    main()
