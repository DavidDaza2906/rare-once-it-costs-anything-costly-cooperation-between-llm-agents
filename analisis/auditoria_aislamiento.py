"""Auditoría de integridad entre corridas. NO gasta tokens y NO usa puertos.

Qué busca: el defecto que retiró el brazo de abstención — un resultado que la corrida NO produjo y que
leyó como propio.

CRITERIO, y los dos errores que hubo que corregir para llegar a él:

  1. NO se usan los comandos del agente como fuente de verdad. El registro está truncado a ~110
     caracteres, así que un comando largo pierde la URL y la comprobación por texto da falsos positivos
     (pasó dos veces). Solo se usa el prefijo `/recl`, que sobrevive al truncado.
  2. NO se usa el sello de tiempo de los archivos archivados en `salidas/<corrida>/puertos/`. Esa carpeta
     es la foto tomada **antes** de limpiar, así que contiene restos de la corrida anterior **por
     construcción**: marcarlos como herencia excluyó el reemplazo del N=80 sin motivo.

  El criterio que sirve es el **efecto**: el host aplica un resultado (un reclamo, un depósito) que
  ningún agente de esa corrida emitió. Eso es herencia, y no admite interpretación.

Uso:  python3 analisis/auditoria_aislamiento.py
"""
import glob
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def revisar(d: str) -> dict:
    r = json.load(open(os.path.join(d, "resumen.json"), encoding="utf-8"))
    ruta_ev = os.path.join(d, "eventos.jsonl")
    ev = []
    if os.path.exists(ruta_ev):
        for linea in open(ruta_ev, encoding="utf-8"):
            if linea.strip():
                try:
                    ev.append(json.loads(linea))
                except json.JSONDecodeError:
                    pass
    pidieron_reclamo = {e.get("agente") for e in ev if re.search(r"/recl", str(e.get("tipo", "")))}
    pidieron_deposito = {e.get("agente") for e in ev if re.search(r"/depo", str(e.get("tipo", "")))}
    recl = {x.get("agente") for x in (r.get("reclamos") or [])}
    dep = {x.get("agente") for x in (r.get("depositos") or [])} if isinstance(r.get("depositos"), list) else set()
    return {
        "dir": os.path.basename(d), "escena": r.get("escena"),
        "tiene_recurso": bool(r.get("recurso_final") is not None or r.get("reclamos") is not None),
        "reclamos_sin_comando": sorted(a for a in (recl - pidieron_reclamo) if a),
        "depositos_sin_comando": sorted(a for a in (dep - pidieron_deposito) if a),
        "n_reclamos": len(recl), "n_depositos": len(dep),
    }


def main() -> None:
    corridas = [os.path.dirname(f) for f in sorted(
        glob.glob(os.path.join(RAIZ, "salidas", "**", "resumen.json"), recursive=True))
        if "ensayo" not in f and "retirados" not in f]
    print(f"  corridas auditadas: {len(corridas)}  (retiradas y ensayos fuera)\n")

    con_reclamo = con_deposito = 0
    sospechosas = []
    for d in corridas:
        try:
            a = revisar(d)
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {os.path.basename(d)}: {e}")
            continue
        if a["reclamos_sin_comando"] or a["depositos_sin_comando"]:
            sospechosas.append(a)
            if a["reclamos_sin_comando"]:
                con_reclamo += 1
            if a["depositos_sin_comando"]:
                con_deposito += 1
            print(f"  {a['dir']}  escena={a['escena']}")
            if a["reclamos_sin_comando"]:
                print(f"      RECLAMO sin comando: {a['reclamos_sin_comando']}  <-- herencia")
            if a["depositos_sin_comando"]:
                print(f"      DEPOSITO sin comando: {a['depositos_sin_comando']}")

    print()
    print(f"  corridas con reclamo sin comando (herencia real): {con_reclamo}")
    print(f"  corridas con deposito sin comando: {con_deposito}")
    if not sospechosas:
        print("  ningun resultado aplicado sin accion del agente: aislamiento APTO en todas las familias")
    elif con_reclamo == 0:
        print("  sin herencia por reclamo. Los depositos se revisan uno a uno (el comando puede venir")
        print("  truncado, asi que un deposito marcado NO es prueba por si solo).")


if __name__ == "__main__":
    main()
