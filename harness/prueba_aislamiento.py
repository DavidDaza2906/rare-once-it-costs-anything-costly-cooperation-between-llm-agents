"""Prueba de aislamiento entre corridas. NO gasta tokens y NO usa puertos.

Lo que prueba, en las dos direcciones, porque un test que no puede fallar no prueba nada:
  1. el defecto SE REPRODUCE: con archivos de reclamos heredados, una corrida nueva los lee como
     propios y arranca con la reserva contaminada;
  2. el arreglo LO CIERRA: tras limpiar, la corrida nueva no ve ningun reclamo y la reserva arranca
     entera;
  3. el arreglo ARCHIVA antes de borrar: sin el archivo no habria forma de auditar una corrida despues
     (el archivo por puerto se borra al arrancar la siguiente), y la auditoria por sello de tiempo
     quedaria imposible.

Uso:  python3 harness/prueba_aislamiento.py
"""
import io
import json
import os
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
sys.path.insert(0, BASE)

import bucle  # noqa: E402

fallos = []


def afirma(cond, texto):
    print(f"  {'OK  ' if cond else 'FALLA'} {texto}")
    if not cond:
        fallos.append(texto)


def main() -> None:
    escena = json.load(open(os.path.join(RAIZ, "escena-abstencion.resuelta.json"), encoding="utf-8"))
    agentes = escena["asignacion"]
    R = int((escena.get("recurso") or {}).get("reserva") or 0)
    respaldos = {}
    for ag in agentes:
        ruta = os.path.join(BASE, f"puerto_reclamos_{ag['puerto']}.jsonl")
        respaldos[ruta] = io.open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else None
    try:
        # --- 1. el defecto se reproduce ---
        for ag in agentes:
            with open(os.path.join(BASE, f"puerto_reclamos_{ag['puerto']}.jsonl"),
                      "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"autor": ag["agente"], "t": 1.0}) + "\n")
        with tempfile.TemporaryDirectory() as tmp:
            c = bucle.Corrida(escena, tmp)
            c.ronda = 1
            aplicados = c.reconciliar_reclamos()
            afirma(aplicados == len(agentes),
                   f"el defecto SE REPRODUCE: una corrida nueva lee {aplicados} reclamos heredados")
            afirma(c.reserva < R, f"y la reserva arranca contaminada (quedo en {c.reserva} de {R})")

        # --- 2 y 3. el arreglo lo cierra y ademas archiva ---
        with tempfile.TemporaryDirectory() as archivo:
            borrados = bucle.limpiar_estado_de_puertos(agentes, archivo)
            afirma(len(borrados) >= len(agentes),
                   f"la limpieza borra al menos un archivo por agente ({len(borrados)} borrados)")
            sobrantes = [ag["puerto"] for ag in agentes
                         if os.path.exists(os.path.join(BASE, f"puerto_reclamos_{ag['puerto']}.jsonl"))]
            afirma(not sobrantes, f"no queda ningun archivo de reclamos (sobrantes: {sobrantes})")
            archivados = [f for f in os.listdir(os.path.join(archivo, "puertos"))
                          if f.startswith("puerto_reclamos_")]
            afirma(len(archivados) == len(agentes),
                   f"y los archiva antes de borrar: {len(archivados)} archivos en salidas/<corrida>/puertos/")
            contenido = io.open(os.path.join(archivo, "puertos", archivados[0]), encoding="utf-8").read()
            afirma("autor" in contenido, "el archivo conserva el autor, o sea sirve para auditar")

        with tempfile.TemporaryDirectory() as tmp:
            c2 = bucle.Corrida(escena, tmp)
            c2.ronda = 1
            afirma(c2.reconciliar_reclamos() == 0,
                   "tras limpiar, la corrida nueva NO ve reclamos heredados")
            afirma(c2.reserva == R, f"y la reserva arranca entera ({c2.reserva} de {R})")
            afirma(c2.reclamos == [], "y no hay reclamos atribuidos a nadie")
    finally:
        for ruta, contenido in respaldos.items():
            if contenido is None:
                if os.path.exists(ruta):
                    os.remove(ruta)
            else:
                io.open(ruta, "w", encoding="utf-8").write(contenido)
    print()
    if fallos:
        print(f"  {len(fallos)} FALLOS")
        raise SystemExit(1)
    print("  aislamiento entre corridas: APTO")


if __name__ == "__main__":
    main()
