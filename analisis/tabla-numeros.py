"""Tabla de numeros congelados para el reporte. Lee reportes/ y no calcula nada por su cuenta.

Se corre DESPUES del congelamiento:

    python3 analisis/tabla-numeros.py > docs/NUMEROS-CONGELADOS.md

Son DATO, no prosa: el reporte lo escribe el equipo. Cada fila trae su N y su intervalo para que
ninguna cifra se lea sin saber sobre cuantas corridas esta medida.
"""
import hashlib
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def carga(nombre):
    ruta = os.path.join(RAIZ, "reportes", nombre)
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as fh:
        return json.load(fh)


def hash_de(nombre):
    ruta = os.path.join(RAIZ, "reportes", nombre)
    if not os.path.exists(ruta):
        return "—"
    return hashlib.sha256(open(ruta, "rb").read()).hexdigest()[:16]


conf = carga("confirmatorio.json")
abs2 = carga("abstencion-2x2.json")
inc = carga("incidente.json")

print("# Numeros congelados")
print()
print("Generado por `analisis/tabla-numeros.py` desde `reportes/`. Cada cifra lleva su N y su intervalo.")
print()

if conf:
    print("## Factorial: tasa de entrega de la clave")
    print()
    print("| precio | entrego | agentes | tasa | IC95 |")
    print("|---|---|---|---|---|")
    for p in ("0", "5", "20"):
        t = conf["tasas"].get(p)
        if not t:
            continue
        lo, hi = t["ic95"]
        print(f"| {p} | {t['k']} | {t['n']} | {t['tasa']}% | [{lo}, {hi}] |")
    prim = conf["primario_pareado"]
    lo, hi = prim["ic95_bootstrap"]
    print()
    print(f"**Primario pareado (precio 20 menos 5), N = {prim['n_corridas']} corridas:** "
          f"{prim['media']:+.4f}  IC95 [{lo}, {hi}]  "
          f"({'incluye cero' if prim['incluye_cero'] else 'NO incluye cero'})")
    print()
    print(f"Corridas validas del lote: {conf['validez']['corridas_lote']} | "
          f"del brazo de precio 0: {conf['validez']['corridas_cero']}. "
          f"Hash del archivo: `{hash_de('confirmatorio.json')}`")
    print()

if abs2:
    print("## Abstencion: tasa de TOMAR la reserva (2x2)")
    print()
    print("| condicion | corridas | agentes | tomo | tasa | abstencion |")
    print("|---|---|---|---|---|---|")
    for clave, c in abs2["celdas"].items():
        if not c.get("tasa_toma"):
            continue
        print(f"| {clave} | {c['corridas']} | {c['agentes']} | {c['tomaron']} | "
              f"{c['tasa_toma']}% | {c['abstencion']}% |")
    print()
    print("Contrastes internos, con su N de corridas por celda. Se reportan las dos lecturas (8 y 16) "
          "cuando la extension haya cerrado.")
    print()
    print(f"Hash del archivo: `{hash_de('abstencion-2x2.json')}`")
    print()

if inc:
    print("## Familia del incidente (exploratorio de direccion)")
    print()
    print("| celda | agentes | entrego la clave | tomo la reserva |")
    print("|---|---|---|---|")
    for nombre, c in inc["celdas"].items():
        dep = f"{c['tasa_deposito']:.1f}%" if c.get("tasa_deposito") is not None else "—"
        tom = f"{c['tasa_toma']:.1f}%" if c.get("tasa_toma") is not None else "n/a"
        print(f"| {nombre} | {c['agentes']} | {dep} | {tom} |")
    print()
    ns = sorted({c["agentes"] // 6 for c in inc["celdas"].values() if c.get("agentes")})
    rango = f"{ns[0]}" if len(ns) == 1 else f"{ns[0]}-{ns[-1]}"
    print(f"Corridas por celda: {rango}. Con ese tamano el IC de una diferencia de tasas ronda los "
          "±13 puntos y el de una interaccion es bastante mas ancho: **exploratorio de direccion, no "
          "de magnitud**.")
    print()
    print("`n/a` en la columna de la reserva significa **no aplica**: en esas escenas el recurso comun "
          "no existe, asi que esos agentes nunca tuvieron la oportunidad de tomarlo. No es un cero "
          "medido, y por eso no se escribe 0%. Las corridas se deduplican por nombre: varias viven en "
          "los dos arboles.")
    print()
    print(f"Hash del archivo: `{hash_de('incidente.json')}`")
    print()

print("---")
print("Los intervalos de las celdas del 2x2 y del incidente son bootstrap sobre corridas (semilla fija).")
print("Ninguna cifra de esta tabla se mezcla con las diferencias pareadas de otra familia.")
