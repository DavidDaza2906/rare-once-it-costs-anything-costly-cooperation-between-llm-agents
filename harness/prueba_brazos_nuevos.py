"""Prueba del cambio de arnés para los brazos de escena baratos. NO gasta tokens ni usa puertos.

El cambio: el validador no reconocía los tres brazos nuevos (precio_uno, identidad_solicitante,
segunda_tarea), así que I10 los rechazaba por el confederado activo y I9a —el chequeo que de verdad
importa aquí, precio > 0— se saltaba con un "no aplica".

Lo que prueba, en las dos direcciones:
  1. las tres escenas validan, y la del par lo hace con su excepción DECLARADA (autor par por diseño);
  2. el chequeo sustantivo I9a APARECE en la salida para esos brazos: es la diferencia entre "corrió" y
     "se saltó", y es lo que el cambio tenía que conseguir;
  3. la escena del lote sigue validando igual, sin excepciones (la regresión).

Uso:  python3 harness/prueba_brazos_nuevos.py
"""
import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
PY = sys.executable
fallos = []


def afirma(cond, texto):
    print(f"  {'OK  ' if cond else 'FALLA'} {texto}")
    if not cond:
        fallos.append(texto)


def valida(escena: str) -> str:
    destino = f"/tmp/{escena}.prueba.resuelta.json"
    r = subprocess.run([PY, os.path.join(BASE, "validador.py"),
                        os.path.join(RAIZ, f"{escena}.json"), destino],
                       capture_output=True, text=True, cwd=RAIZ)
    return r.stdout + r.stderr


def main() -> None:
    for escena in ("escena-par-p5", "escena-externo-p5", "escena-precio1"):
        salida = valida(escena)
        afirma("ESCENA VÁLIDA" in salida and "INVÁLIDA" not in salida, f"{escena} valida")
        afirma(bool(re.search(r"OK\s+I9a autosuficiente dominado", salida)),
               f"{escena}: el chequeo I9a CORRE (no se salta)")

    salida_par = valida("escena-par-p5")
    afirma("DECLARADO I10" in salida_par,
           "la escena del par declara la excepción de I10 en vez de esconderla")

    salida_lote = valida("escena")
    afirma("ESCENA VÁLIDA" in salida_lote and "INVÁLIDA" not in salida_lote,
           "la escena del lote sigue validando igual")
    afirma("DECLARADO" not in salida_lote,
           "y sin excepciones declaradas: el cambio no le abrió ninguna puerta")
    afirma(bool(re.search(r"OK\s+I9a autosuficiente dominado", salida_lote)),
           "y su I9a también corre, como antes")

    print()
    if fallos:
        print(f"  {len(fallos)} FALLOS")
        raise SystemExit(1)
    print("  brazos nuevos: APTO")


if __name__ == "__main__":
    main()
