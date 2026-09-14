"""Barre los logs del proyecto y construye el corpus replayable de todas las corridas.

Para cada .eval prueba los puertos candidatos y se queda con el que más peticiones tiene
dentro de la ventana del propio log: así no hay que mapear a mano qué sonda usó qué puerto,
y la atribución sigue viniendo del registro del host.

Uso:  python corpus.py [--logs harness/logs] [--salida reportes]
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CANDIDATOS = [8102, 8091, 8090, 8080]

spec = importlib.util.spec_from_file_location("reporte", os.path.join(BASE, "reporte.py"))
reporte = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reporte)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--logs", default=os.path.join(BASE, "logs"))
    p.add_argument("--salida", default=os.path.join(BASE, "..", "reportes"))
    a = p.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    corpus = os.path.join(a.salida, "corpus.jsonl")
    open(corpus, "w").close()

    rutas = sorted(glob.glob(os.path.join(a.logs, "*.eval")), key=os.path.getmtime)
    filas = 0
    for ruta in rutas:
        mejor, mejor_rep = None, None
        for puerto in CANDIDATOS:
            try:
                rep = reporte.construir(ruta, puerto)
            except Exception:  # noqa: BLE001
                continue
            n = rep["resumen"]["peticiones_propias"] + rep["resumen"].get("peticiones_sin_atribuir", 0)
            if mejor_rep is None or n > mejor:
                mejor, mejor_rep = n, rep
        if mejor_rep is None:
            continue
        if mejor == 0:
            mejor_rep["meta"]["puerto_egreso"] = None
            mejor_rep["meta"]["nota"] = "sin peticiones en la ventana: esta corrida no usó el puerto"
        nombre = os.path.join(a.salida, os.path.basename(ruta).replace(".eval", ".json"))
        with open(nombre, "w", encoding="utf-8") as fh:
            json.dump(mejor_rep, fh, ensure_ascii=False, indent=2)
        with open(corpus, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "run": os.path.basename(ruta),
                "tarea": mejor_rep["meta"]["tarea"],
                "modelo": mejor_rep["meta"]["modelo"],
                "puerto_egreso": mejor_rep["meta"]["puerto_egreso"],
                "precio_publicar": mejor_rep["meta"]["precio_publicar"],
                "resumen": mejor_rep["resumen"],
                "hallazgos": mejor_rep["hallazgos"],
                "eventos": len(mejor_rep["eventos"]),
                "integridad": mejor_rep["integridad"]["sha256_corto"],
            }, ensure_ascii=False) + "\n")
        filas += 1
        r = mejor_rep["resumen"]
        print(f"{mejor_rep['meta']['tarea'][:22]:24s} p={str(mejor_rep['meta']['puerto_egreso']):5s} "
              f"publico={str(r['publico']):5s} correcto={str(r['tarea_correcta']):5s} "
              f"pet={r['peticiones_propias']:3d} tok={r['tokens_totales']} hal={len(mejor_rep['hallazgos'])}")
    print(f"\ncorpus: {filas} corridas en {corpus}")


if __name__ == "__main__":
    main()
