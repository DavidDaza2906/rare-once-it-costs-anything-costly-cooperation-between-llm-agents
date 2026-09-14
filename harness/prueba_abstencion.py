"""Prueba determinista del mecanismo de abstencion. NO gasta tokens y NO toca los puertos.

Fija los dos defectos que el humo destapo:
  1. el bloque `recurso` se perdia al resolver la escena (la reserva corria en cero);
  2. el servicio escribia un archivo global mientras el bucle leia uno por puerto.
Y las propiedades del mecanismo: un reclamo por agente, aplicado una sola vez, con la reserva
perdiendo el doble, y el reparto final = reserva // n.

Uso:  python3 harness/prueba_abstencion.py
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
    ruta_escena = os.path.join(RAIZ, "escena-abstencion.resuelta.json")
    escena = json.load(open(ruta_escena, encoding="utf-8"))
    rec = escena.get("recurso") or {}
    afirma(rec.get("activo") is True, "el bloque `recurso` sobrevive a la resolucion de la escena")
    K = int(rec.get("bono") or 0)
    R = int(rec.get("reserva") or 0)
    afirma(K == 5 and R == 60, f"la escena declara bono {K} y reserva {R}")
    agentes = [a["agente"] for a in escena["asignacion"]]
    # Aislamiento del test: se respaldan y restauran los archivos de reclamos de TODOS los puertos.
    # Con solo el del primer agente, los de las corridas reales contaminaban las cuentas (paso el 13 sep).
    puertos = [a["puerto"] for a in escena["asignacion"]]
    rutas = {os.path.join(BASE, f"puerto_reclamos_{p}.jsonl"): None for p in puertos}
    for r in list(rutas):
        if os.path.exists(r):
            rutas[r] = io.open(r, encoding="utf-8").read()
    try:
        for r in rutas:
            if os.path.exists(r):
                os.remove(r)
        with tempfile.TemporaryDirectory() as tmp:
            c = bucle.Corrida(escena, tmp)
            afirma(c.reserva == R, f"la corrida arranca con la reserva en {c.reserva}")
            c.ronda = 1
            afirma(c.reconciliar_reclamos() == 0, "sin archivo de reclamos no aplica nada")
            with open(list(rutas)[0], "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"autor": agentes[0]}) + "\n")
            antes = c.pasos[agentes[0]]
            afirma(c.reconciliar_reclamos() == 1, "un reclamo se aplica")
            afirma(c.pasos[agentes[0]] == antes + K, f"el que reclama gana {K} pasos")
            afirma(c.reserva == R - 2 * K, f"la reserva pierde el doble ({2*K})")
            afirma(c.reconciliar_reclamos() == 0, "releer el mismo archivo no vuelve a aplicarlo")
            with open(list(rutas)[0], "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"autor": agentes[0]}) + "\n")
            c.reconciliar_reclamos()
            afirma(len(c.reclamos) == 1, "un agente no puede reclamar dos veces")
            afirma(c.pasos[agentes[0]] == antes + K, "el segundo reclamo no acredita de nuevo")
            c.depositos, c.entregas, c.gastado = [], {}, {a: 0 for a in agentes}
            c.claves = {a: "V" + a[-1] for a in agentes}
            try:
                d = c.resolver()
                reparto = c.reserva // len(agentes)
                afirma(d[agentes[0]]["puntaje"] == c.pasos[agentes[0]] + reparto,
                       f"el puntaje incluye el reparto de la reserva ({reparto} por agente)")
            except Exception as e:  # noqa: BLE001
                afirma(False, f"resolver() fallo: {type(e).__name__}: {e}")
    finally:
        for r, contenido in rutas.items():
            if contenido is None:
                if os.path.exists(r):
                    os.remove(r)
            else:
                io.open(r, "w", encoding="utf-8").write(contenido)
    print()
    if fallos:
        print(f"  {len(fallos)} FALLOS")
        raise SystemExit(1)
    print("  mecanismo de abstencion APTO")


if __name__ == "__main__":
    main()
