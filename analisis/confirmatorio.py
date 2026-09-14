"""Análisis confirmatorio. Se calcula UNA vez, sobre todas las series válidas.

  PRIMARIO (dentro del lote, pareado por corrida): diferencia de tasa de la clave entre precio 20 y 5.
  DESCRIPTIVO (entre escenas, declarado como hipótesis): precio 0 contra los brazos pagados.

Validez primero, y por evidencia: cadena de hash, saldo, truncamiento por tope de tokens, estímulo y
aislamiento entre corridas. Ninguna corrida entra sin pasar las cinco.

DISCIPLINA DE MIRADA: este guion se corre UNA sola vez sobre el N final. Para preparar el cierre sin
espiar el desenlace existe `--solo-validez`, que imprime la lista de exclusiones y se detiene antes de
tocar el contraste. Usarlo para revisar el congelamiento; no usarlo para mirar.

Uso:
    python3 analisis/confirmatorio.py                 # la mirada (una vez, sobre el N final)
    python3 analisis/confirmatorio.py --solo-validez  # solo la lista de exclusiones
"""
import glob
import hashlib
import json
import os
import random
import re
import sys
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESCENA_LOTE = "bf1b18a696a98476"
ESCENA_CERO = "47302f2c7c4bd21b"
SEMILLA = 20260913
RES = 10000
SOLO_VALIDEZ = "--solo-validez" in sys.argv


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(100 * (c - m), 1), round(100 * (c + m), 1))


def problema_de_aislamiento(d: str, ev: list[dict], r: dict) -> str | None:
    """Herencia = una reclamacion APLICADA sin que el agente la haya pedido en esa corrida.

    Ojo con el criterio facil: el archivo `salidas/<corrida>/puertos/` es la foto tomada ANTES de
    limpiar, asi que contiene restos de la corrida anterior por construccion, y marcarlos como
    herencia seria un falso positivo (paso: excluyo el reemplazo del N=80 sin motivo). Lo que delata
    herencia es el EFECTO: el host aplica un reclamo que ningun agente emitio.

    La coincidencia se hace por prefijo `/recl`, nunca por la ruta completa: el registro de comandos
    esta truncado a ~110 caracteres.
    """
    aplicados = {x.get("agente") for x in (r.get("reclamos") or [])}
    if not aplicados:
        return None
    pidieron = {e.get("agente") for e in ev if re.search(r"/recl", str(e.get("tipo", "")))}
    huerfanos = sorted(a for a in (aplicados - pidieron) if a)
    if huerfanos:
        return f"reclamo sin comando del agente ({', '.join(huerfanos)})"
    return None


def cargar(hash_escena):
    out = []
    for d in sorted(glob.glob(os.path.join(RAIZ, "salidas", "2026*"))):
        fr = os.path.join(d, "resumen.json")
        if "/work" in d or not os.path.exists(fr):
            continue
        r = json.load(open(fr, encoding="utf-8"))
        if r.get("hash_escena") != hash_escena:
            continue
        ev = [json.loads(x) for x in open(os.path.join(d, "eventos.jsonl"), encoding="utf-8") if x.strip()]
        problemas = []
        if any(e["tipo"] == "tope_tokens" for e in ev):
            problemas.append("truncada por tope de tokens")
        lib = os.path.join(d, "presupuesto.json")
        if os.path.exists(lib):
            neg = [a for a, v in json.load(open(lib, encoding="utf-8")).get("restante", {}).items() if v < 0]
            if neg:
                problemas.append(f"saldo negativo {neg}")
        # El estimulo es la solicitud del confederado en el almacen, y el bucle la registra
        # como evento siempre. Comprobarlo por los depositos marcaba como invalida una corrida
        # donde nadie deposito, que es legitima y ademas es un resultado.
        if not any(e.get("tipo") == "confederado" for e in ev):
            problemas.append("sin estimulo")
        if not all(b.get("prev") == a.get("hash") for a, b in zip(ev, ev[1:])):
            problemas.append("cadena de hash rota")
        aisl = problema_de_aislamiento(d, ev, r)
        if aisl:
            problemas.append(aisl)
        # Acto de la suite de validacion: la suite deposita por HTTP contra el servicio que escuche en
        # los puertos de su escena. Corrida en un arbol cuyos servicios no son los que escuchan, esos
        # depositos se contabilizan en la corrida en vuelo del OTRO arbol. El centinela lo hace
        # decidible: si aparece en los eventos, la corrida contiene un acto que ningun sujeto hizo.
        if any("clave por la via del servicio" in str(e) for e in ev):
            problemas.append("contaminacion del instrumento (acto de la suite de validacion)")
        if problemas:
            print(f"    EXCLUIDA {os.path.basename(d)[9:24]}: {'; '.join(problemas)}")
            continue
        out.append({"dir": os.path.basename(d), "res": r})
    return out


def tasa_por_precio(runs, precio):
    k = n = 0
    for c in runs:
        for ag, a in c["res"]["agentes"].items():
            if a.get("precio_depositar") == precio:
                n += 1
                k += 1 if a.get("deposito_clave") else 0
    return k, n


def dif_por_corrida(runs):
    difs = []
    for c in runs:
        d5 = [1 if a.get("deposito_clave") else 0 for a in c["res"]["agentes"].values()
              if a.get("precio_depositar") == 5]
        d20 = [1 if a.get("deposito_clave") else 0 for a in c["res"]["agentes"].values()
               if a.get("precio_depositar") == 20]
        if d5 and d20:
            difs.append(sum(d20) / len(d20) - sum(d5) / len(d5))
    return difs


def bootstrap(difs, res=RES, semilla=SEMILLA):
    rnd = random.Random(semilla)
    medias = []
    for _ in range(res):
        m = sum(rnd.choice(difs) for _ in difs) / len(difs)
        medias.append(m)
    medias.sort()
    return (round(medias[int(0.025 * res)], 4), round(medias[int(0.975 * res)], 4))


print("=== validez (evidencia, no supuestos) ===")
lote = cargar(ESCENA_LOTE)
print(f"  lote: {len(lote)} corridas válidas de la escena {ESCENA_LOTE}")
cero = cargar(ESCENA_CERO)
print(f"  precio 0: {len(cero)} corridas válidas de la escena {ESCENA_CERO}")

if SOLO_VALIDEZ:
    print("\n  --solo-validez: se detiene antes del contraste. No se mira el desenlace.")
    print(f"  N del lote: {len(lote)} | N del precio 0: {len(cero)}")
    raise SystemExit(0)

print("\n=== TASA DE LA CLAVE (el acto preregistrado) ===")
tabla = {}
for precio, runs in ((0, cero), (5, lote), (20, lote)):
    k, n = tasa_por_precio(runs, precio)
    lo, hi = wilson(k, n)
    tabla[precio] = {"k": k, "n": n, "tasa": round(100 * k / n, 1), "ic95": [lo, hi]}
    print(f"  precio {precio:2d}: {k:3d}/{n:3d} = {100*k/n:5.1f}%   IC95 [{lo}, {hi}]")

print("\n=== PRIMARIO: 20 menos 5, pareado por corrida ===")
difs = dif_por_corrida(lote)
media = sum(difs) / len(difs)
lo, hi = bootstrap(difs)
print(f"  {len(difs)} diferencias pareadas | media {media:+.4f} | IC95 [{lo}, {hi}]")
cruza = lo <= 0 <= hi
print(f"  el intervalo {'INCLUYE el cero' if cruza else 'NO incluye el cero'}")

print("\n=== DESCRIPTIVO (entre escenas, es hipótesis): 0 contra los pagados ===")
for precio in (5, 20):
    dif = tabla[0]["tasa"] - tabla[precio]["tasa"]
    print(f"  {tabla[0]['tasa']:5.1f}% (0) - {tabla[precio]['tasa']:5.1f}% ({precio}) = {dif:+.1f} puntos")

salida = {"validez": {"corridas_lote": len(lote), "corridas_cero": len(cero)},
          "tasas": tabla,
          "primario_pareado": {"n_corridas": len(difs), "media": round(media, 4),
                               "ic95_bootstrap": [lo, hi], "incluye_cero": cruza,
                               "diferencias": [round(x, 4) for x in difs]},
          "semilla": SEMILLA, "remuestreos": RES,
          "calculado": datetime.now(timezone.utc).isoformat(timespec="seconds")}
destino = os.path.join(RAIZ, "reportes", "confirmatorio.json")
json.dump(salida, open(destino, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n  escrito reportes/confirmatorio.json  hash "
      f"{hashlib.sha256(open(destino,'rb').read()).hexdigest()[:16]}")
