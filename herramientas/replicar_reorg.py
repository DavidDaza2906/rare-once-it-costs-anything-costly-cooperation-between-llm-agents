#!/usr/bin/env python3
"""Replica en el clon la reorganizacion que se hizo en el arbol 1.

Los renombrados se tratan como tales (mover el archivo) y no como borrado+alta, para que git los
reconozca por similitud y el diff del commit sea legible en vez de mostrar cientos de lineas cambiadas.
Los archivos de salidas/ se saltan: el clon ya los tiene por los empujes anteriores.
"""
import os
import shutil
import subprocess

T = "/home/daw/Sprint"
C = "/home/daw/integ-sprint"

lineas = subprocess.run(["git", "-C", T, "status", "--short"], capture_output=True, text=True).stdout.splitlines()

ren, mod, nue, bor = [], [], [], []
for l in lineas:
    if not l.strip():
        continue
    codigo, resto = l[:2], l[3:]
    if "->" in resto:
        a, b = resto.split("->")
        ren.append((a.strip(), b.strip()))
    elif codigo.strip() == "D":
        bor.append(resto.strip())
    elif codigo.strip() == "M":
        mod.append(resto.strip())
    elif codigo.strip() == "??":
        nue.append(resto.strip())

hechos = {"renombrados": 0, "modificados": 0, "nuevos": 0, "borrados": 0, "saltados": 0}

for a, b in ren:
    origen = os.path.join(T, b)
    destino = os.path.join(C, b)
    viejo = os.path.join(C, a)
    if os.path.isfile(origen):
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copy2(origen, destino)
    if os.path.exists(viejo):
        os.remove(viejo)
    hechos["renombrados"] += 1

for p in mod:
    s = os.path.join(T, p)
    d = os.path.join(C, p)
    if os.path.isfile(s):
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        hechos["modificados"] += 1

for p in nue:
    if p.startswith("salidas/") or p.startswith("recon/"):
        hechos["saltados"] += 1
        continue
    s = os.path.join(T, p)
    d = os.path.join(C, p)
    if os.path.isfile(s):
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        hechos["nuevos"] += 1
    else:
        hechos["saltados"] += 1

for p in bor:
    d = os.path.join(C, p)
    if os.path.exists(d):
        os.remove(d)
    hechos["borrados"] += 1

print(f"  renombrados: {hechos['renombrados']} | modificados: {hechos['modificados']} | "
      f"nuevos: {hechos['nuevos']} | borrados: {hechos['borrados']} | saltados (salidas): {hechos['saltados']}")
