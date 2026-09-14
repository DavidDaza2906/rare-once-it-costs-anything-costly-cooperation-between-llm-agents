"""Salud del lote en curso. SOLO LECTURA y SOLO INSTRUMENTO: nunca imprime tasas ni el contraste.

Mira las corridas de `salidas/` creadas desde una hora dada (UTC) y reporta lo que un revisor
puede mirar a mitad de tanda sin convertirlo en parada opcional: cuántas van, si todas llevan el
mismo hash de escena, corridas sin resumen (interrumpidas), saldos negativos, "sin estímulo",
truncadas por tope, tareas completadas, rechazos y tokens acumulados contra el tope.

Uso:  python3 herramientas/salud_lote.py [--desde 20260913T191500] [--tope 5200000] [--hash bf1b18a696a98476]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# El árbol 2 corre en su propio worktree y escribe en SU `salidas/`. Se miran los dos y se deduplica
# por nombre de corrida: sin esto, un brazo que sólo vive allá no se vigila (y el 14 sep un servicio
# caído estuvo corrompiendo corridas seis horas sin que nada avisara).
RAICES = [RAIZ] + [r for r in ("/home/daw/Sprint-2",) if os.path.isdir(os.path.join(r, "salidas"))]


def leer(d: str) -> dict:
    nombre = os.path.basename(d.rstrip("/"))
    fila = {"corrida": nombre, "terminada": False, "hash": None, "tokens": 0, "eventos": 0,
            "alertas": []}
    ev_path = os.path.join(d, "eventos.jsonl")
    if os.path.exists(ev_path):
        with open(ev_path, encoding="utf-8") as fh:
            eventos = [json.loads(l) for l in fh if l.strip()]
    else:
        eventos = []
    fila["eventos"] = len(eventos)
    fila["rechazos"] = sum(1 for e in eventos if e["tipo"].startswith("comando_rechazado"))
    fila["truncada"] = any(e["tipo"] == "tope_tokens" for e in eventos)
    # Servicio de almacén caído: el agente intentó depositar y le rebotó la conexión. Convierte un
    # "no quiso" en un "no pudo" y arruina la corrida. Pasó el 14 sep en el árbol 2 (56 eventos desde
    # las 03:03 UTC, servicio 8501-8506 sin levantar) y no lo avisaba nada.
    fila["errores_red"] = sum(1 for e in eventos if e.get("tipo") == "error_red")
    fila["dup_http"] = sum(1 for e in eventos if e["tipo"].startswith("depositar_por_http"))
    fila["impagados"] = sum(1 for e in eventos if e["tipo"] == "deposito_impagado")
    ini = next((e for e in eventos if e["tipo"] == "inicio"), None)
    if ini:
        det = ini.get("detalle", "")
        if "hash escena" in det:
            fila["hash"] = det.split("hash escena")[-1].strip()
    res_path = os.path.join(d, "resumen.json")
    if not os.path.exists(res_path):
        fila["alertas"].append("sin resumen (en curso o interrumpida)")
        return fila
    with open(res_path, encoding="utf-8") as fh:
        r = json.load(fh)
    fila["terminada"] = True
    fila["hash"] = r.get("hash_escena") or fila["hash"]
    fila["tokens"] = int(r.get("tokens_totales") or 0)
    ag = r.get("agentes", {})
    fila["n_agentes"] = len(ag)
    fila["tareas_ok"] = sum(1 for a in ag.values() if a.get("tarea_correcta"))
    fila["saldo_negativo"] = [k for k, a in ag.items() if (a.get("pasos_restantes") or 0) < 0]
    deps = r.get("depositos", [])
    fila["estimulo"] = any(x.get("via") == "confederado" for x in deps)
    if fila["saldo_negativo"]:
        fila["alertas"].append(f"saldo negativo: {', '.join(fila['saldo_negativo'])}")
    if not fila["estimulo"]:
        fila["alertas"].append("sin estímulo (no hay solicitud de confederado)")
    if fila["truncada"]:
        fila["alertas"].append("truncada por tope de tokens")
    if fila.get("errores_red"):
        fila["alertas"].append(f"SERVICIO CAÍDO: {fila['errores_red']} depósito(s) rechazados por "
                               "conexión — revisar servicios.py antes de seguir")
    if fila["impagados"]:
        fila["alertas"].append(f"{fila['impagados']} depósito(s) impagado(s)")
    if fila["n_agentes"] != 6:
        fila["alertas"].append(f"{fila['n_agentes']} agentes, no 6")
    return fila


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default="20260913T191500", help="marca UTC AAAAMMDDTHHMMSS")
    ap.add_argument("--tope", type=int, default=5_200_000)
    ap.add_argument("--hash", default=None, help="hash de escena esperado")
    ap.add_argument("--familia", default="factorial-base",
                    help="familia de escena a vigilar (p. ej. solicitante-externo-p5)")
    a = ap.parse_args()

    cands = []
    for raiz in RAICES:
        cands += glob.glob(os.path.join(raiz, "salidas", f"*_{a.familia}/"))
    vistos, dirs = set(), []
    for d in sorted(cands, key=lambda x: os.path.basename(x.rstrip("/"))):
        nom = os.path.basename(d.rstrip("/"))
        if nom in vistos or nom.split("_")[0] < a.desde:
            continue
        vistos.add(nom); dirs.append(d)
    filas = [leer(d) for d in dirs]
    hechas = [f for f in filas if f["terminada"]]
    tokens = sum(f["tokens"] for f in hechas)
    hashes = {f["hash"] for f in filas if f["hash"]}
    esperado = a.hash or (hechas[0]["hash"] if hechas else None)

    ahora = datetime.now(timezone.utc).strftime("%H:%M UTC")
    print(f"salud del lote — {ahora} — corridas desde {a.desde}")
    print(f"  terminadas: {len(hechas)}   en curso/interrumpidas: {len(filas) - len(hechas)}")
    print(f"  hash de escena: {'ÚNICO ' + esperado if hashes == {esperado} else 'MEZCLA ' + str(hashes)}")
    print(f"  tokens: {tokens:,} de {a.tope:,} ({100 * tokens / a.tope:.0f}%)"
          + (f"   media/corrida {tokens // len(hechas):,}" if hechas else ""))
    if hechas:
        ok = sum(f["tareas_ok"] for f in hechas)
        n = sum(f["n_agentes"] for f in hechas)
        ev = sum(f["eventos"] for f in hechas)
        rech = sum(f["rechazos"] for f in hechas)
        print(f"  tareas completadas: {ok}/{n} ({100 * ok / n:.0f}%)   rechazos: {rech}/{ev} eventos "
              f"({100 * rech / max(ev, 1):.0f}%)   depósitos por http: {sum(f['dup_http'] for f in hechas)}")
        con_estimulo = sum(1 for f in hechas if f["estimulo"])
        print(f"  con estímulo: {con_estimulo}/{len(hechas)}   saldos negativos: "
              f"{sum(1 for f in hechas if f['saldo_negativo'])}   truncadas: "
              f"{sum(1 for f in hechas if f['truncada'])}")
    alertas = [(f["corrida"], x) for f in filas for x in f["alertas"]]
    if alertas:
        print("  ALERTAS:")
        for c, x in alertas:
            print(f"    {c[9:15]}  {x}")
    else:
        print("  sin alertas")
    # Tiempo por corrida (marca de inicio de cada directorio, UTC)
    if len(filas) >= 2:
        ts = [datetime.strptime(f["corrida"].split("_")[0], "%Y%m%dT%H%M%S") for f in filas]
        gaps = [(b - a_).total_seconds() / 60 for a_, b in zip(ts, ts[1:])]
        print(f"  minutos entre arranques: media {sum(gaps) / len(gaps):.1f}, máximo {max(gaps):.1f}")


if __name__ == "__main__":
    main()
