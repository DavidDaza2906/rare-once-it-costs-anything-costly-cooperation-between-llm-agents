"""Hallazgos de parte_4 sin los agentes afectados por el defecto del separador `;`.

`_plan` parte los comandos por `;` (y `&&`, que convierte en `;`) y `_ejecutar_etapas` los encadena como
tubería: solo se ve la salida de la última etapa. Un `curl` que no va último pierde su respuesta.

Afectado = el agente lanzó al menos un comando bash en el que un segmento con `curl` no es el último
segmento separado por `;`/`&&`, y la respuesta de ese comando no mostró nada del servidor (ni
"contenido" ni "parte_4" ni "SOLICITUD") y no fue rechazado por la lista blanca. Se excluye al
agente entero.

Uso: python3 analisis/parte4/sin_splitter.py
"""
import glob
import json
import os
import random
import re

RAIZ = "/home/daw/Sprint"
CONGELADO = [c["corrida"] for c in json.load(open(f"{RAIZ}/reportes/conjunto-congelado.json"))["corridas"]]


def transcripciones(d, ag):
    out = []
    for t in sorted(glob.glob(os.path.join(d, "transcripciones", f"r*_{ag}.json")),
                    key=lambda x: int(re.search(r"/r(\d+)_", x).group(1))):
        ronda = int(re.search(r"/r(\d+)_", t).group(1))
        out.append((ronda, json.load(open(t, encoding="utf-8"))))
    return out


def curl_tragado(cmd):
    segs = [s for s in re.split(r";", re.sub(r"\s*&&\s*", " ; ", cmd)) if s.strip()]
    return any("curl" in s for s in segs[:-1])


def analizar(d, ag):
    afectado = False
    primera = None          # True si la primera respuesta con SOLICITUD traía parte_4
    for ronda, msgs in transcripciones(d, ag):
        pend = {}
        for m in msgs:
            for ll in m.get("llamadas") or []:
                if ll.get("herramienta") == "bash":
                    pend[ll.get("id")] = (ll.get("argumentos") or {}).get("comando", "")
            if m.get("rol") == "tool":
                txt = m.get("texto") or ""
                cmd = pend.get(m.get("responde_a"), "")
                if (cmd and curl_tragado(cmd) and "comando no permitido" not in txt
                        and not any(k in txt for k in ('"contenido"', "parte_4", "SOLICITUD"))):
                    afectado = True
                if primera is None and "SOLICITUD" in txt:
                    primera = '"parte_4"' in txt
    return afectado, primera


def cargar(patron, hash_esc, nombres=None):
    filas = []
    for fr in sorted(glob.glob(patron)):
        d = os.path.dirname(fr)
        r = json.load(open(fr))
        if r.get("hash_escena") != hash_esc:
            continue
        if nombres is not None and os.path.basename(d) not in nombres:
            continue
        for ag, a in r["agentes"].items():
            af, pr = analizar(d, ag)
            filas.append({"corrida": os.path.basename(d), "precio": a["precio_depositar"],
                          "dep": bool(a["deposito_clave"]), "afectado": af, "primera": pr})
    return filas


def tasa(fs):
    k = sum(f["dep"] for f in fs)
    return k, len(fs)


def fmt(k, n):
    return f"{k}/{n} ({100*k/n:.1f}%)" if n else "0/0"


def boot_dif(a, b, reps=10000, seed=2026):
    ra = {}
    for f in a:
        ra.setdefault(f["corrida"], []).append(f)
    rb = {}
    for f in b:
        rb.setdefault(f["corrida"], []).append(f)
    la, lb = list(ra.values()), list(rb.values())
    rnd = random.Random(seed)
    vals = []
    for _ in range(reps):
        sa = [x for g in rnd.choices(la, k=len(la)) for x in g]
        sb = [x for g in rnd.choices(lb, k=len(lb)) for x in g]
        if not sa or not sb:
            continue
        vals.append(tasa(sa)[0] / len(sa) - tasa(sb)[0] / len(sb))
    vals.sort()
    return vals[int(len(vals) * .025)], vals[int(len(vals) * .975)]


nombres = set(CONGELADO)
base = cargar(f"{RAIZ}/salidas/*_factorial-base/resumen.json", "bf1b18a696a98476", nombres)
ctrl = cargar(f"{RAIZ}/salidas-control-parte4/*_control-parte4/resumen.json", "bd0449b257727f38")

for nombre, fs in (("BASE congelado", base), ("CONTROL", ctrl)):
    af = [f for f in fs if f["afectado"]]
    print(f"\n{nombre}: {len(set(f['corrida'] for f in fs))} corridas, {len(fs)} agentes; "
          f"afectados por `;` {len(af)} ({100*len(af)/len(fs):.1f}%)")
    print(f"  entrega en afectados {fmt(*tasa(af))} | en no afectados {fmt(*tasa([f for f in fs if not f['afectado']]))}")

limpio_b = [f for f in base if not f["afectado"]]
limpio_c = [f for f in ctrl if not f["afectado"]]

print("\n1. Primera exposición, BASE sin afectados")
for p in (5, 20):
    fs = [f for f in limpio_b if f["precio"] == p]
    print(f"  precio {p}: sin parte {fmt(*tasa([f for f in fs if f['primera'] is False]))} | "
          f"con parte {fmt(*tasa([f for f in fs if f['primera'] is True]))} | "
          f"nunca la vio {fmt(*tasa([f for f in fs if f['primera'] is None]))}")

print("\n2. Control frente a base, sin afectados")
for p in (5, 20, None):
    fb = [f for f in limpio_b if p is None or f["precio"] == p]
    fc = [f for f in limpio_c if p is None or f["precio"] == p]
    print(f"  {'agregado' if p is None else 'precio ' + str(p)}: base {fmt(*tasa(fb))} | control {fmt(*tasa(fc))}")
kb, nb = tasa(limpio_b)
kc, nc = tasa(limpio_c)
lo, hi = boot_dif(limpio_c, limpio_b)
print(f"  diferencia control - base: {100*(kc/nc - kb/nb):.1f} pts, IC95 [{100*lo:.1f}, {100*hi:.1f}]")

print("\n3. Control, primera exposición (sin afectados)")
print(f"  sin parte {fmt(*tasa([f for f in limpio_c if f['primera'] is False]))} | "
      f"con parte {fmt(*tasa([f for f in limpio_c if f['primera'] is True]))} | "
      f"nunca la vio {fmt(*tasa([f for f in limpio_c if f['primera'] is None]))}")

print("\n4. Primario pareado (precio 20 - precio 5 por corrida), sin afectados")
por = {}
for f in limpio_b:
    por.setdefault(f["corrida"], {5: [], 20: []})[f["precio"]].append(f["dep"])
difs = [sum(g[20]) / len(g[20]) - sum(g[5]) / len(g[5]) for g in por.values() if g[5] and g[20]]
rnd = random.Random(2026)
bs = sorted(sum(rnd.choices(difs, k=len(difs))) / len(difs) for _ in range(10000))
print(f"  corridas con ambos precios: {len(difs)} de {len(por)} | diferencia {100*sum(difs)/len(difs):.2f} pts "
      f"IC95 [{100*bs[250]:.1f}, {100*bs[9750]:.1f}]")
todos = {}
for f in base:
    todos.setdefault(f["corrida"], {5: [], 20: []})[f["precio"]].append(f["dep"])
d2 = [sum(g[20]) / len(g[20]) - sum(g[5]) / len(g[5]) for g in todos.values()]
print(f"  referencia con todos: {len(d2)} corridas, {100*sum(d2)/len(d2):.2f} pts")
print(f"  agentes que quedan por precio: p5 {sum(1 for f in limpio_b if f['precio']==5)}/381, "
      f"p20 {sum(1 for f in limpio_b if f['precio']==20)}/381")
