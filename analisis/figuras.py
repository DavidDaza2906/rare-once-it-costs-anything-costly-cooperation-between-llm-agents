"""Figuras del reporte. Lee los archivos CONGELADOS de reportes/ y no calcula nada por su cuenta.

Se corre DESPUES del congelamiento, con el entorno de figuras (aislado del arnes):

    /tmp/venv-figuras/bin/python analisis/figuras.py

Entradas:
    reportes/confirmatorio.json   tasas del factorial y primario pareado
    reportes/abstencion-2x2.json  celdas del brazo de abstencion

Salidas (vectorial para el PDF y raster para mirar):
    figuras/fig1-curva-precio.pdf/.png
    figuras/fig2-abstencion-2x2.pdf/.png
    figuras/fig3-que-mueve-la-conducta.pdf/.png

Regla: las figuras son DATO, no prosa. El reporte lo escribe el equipo.
"""
import json
import math
import os
import random
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(RAIZ, "figuras")
SEMILLA, RES = 20260913, 10000

AZUL, ROJO, GRIS = "#2b6cb0", "#c53030", "#4a5568"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 200, "savefig.bbox": "tight"})


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return 100 * (c - m), 100 * (c + m)


def boot_ic(v, res=RES, semilla=SEMILLA):
    rnd = random.Random(semilla)
    ms = sorted(sum(rnd.choice(v) for _ in v) / len(v) for _ in range(res))
    return 100 * ms[int(0.025 * res)], 100 * ms[int(0.975 * res)]


def guardar(fig, nombre):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{nombre}.{ext}"))
    plt.close(fig)
    print(f"  figuras/{nombre}.pdf y .png")


def main() -> None:
    os.makedirs(FIG, exist_ok=True)
    conf = json.load(open(os.path.join(RAIZ, "reportes", "confirmatorio.json"), encoding="utf-8"))
    abs2 = json.load(open(os.path.join(RAIZ, "reportes", "abstencion-2x2.json"), encoding="utf-8"))

    # --- figura 1: la curva de precio ---
    precios = [0, 5, 20]
    tasas = [conf["tasas"][str(p)]["tasa"] for p in precios]
    ks = [conf["tasas"][str(p)]["k"] for p in precios]
    ns = [conf["tasas"][str(p)]["n"] for p in precios]
    ics = [wilson(k, n) for k, n in zip(ks, ns)]
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    ax.errorbar(precios, tasas, yerr=[[t - i[0] for t, i in zip(tasas, ics)],
                                      [i[1] - t for t, i in zip(tasas, ics)]],
                fmt="o-", color=AZUL, capsize=3, lw=1.4, ms=5)
    for p, t, k, n in zip(precios, tasas, ks, ns):
        ax.annotate(f"{t:.1f}%\n{k}/{n}", (p, t), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=8)
    ax.set_xlabel("precio por depositar (pasos)")
    ax.set_ylabel("tasa de deposito de la clave (%)")
    ax.set_xticks(precios)
    ax.set_ylim(0, 62)
    ax.axhspan(0, 30, color=GRIS, alpha=0.06)
    ax.annotate("la barrera es que EXISTA un costo\n(5 vs 20: sin diferencia de magnitud)",
                xy=(12.5, 12), fontsize=7.5, color=GRIS, ha="center")
    ax.set_title("El factorial: pagar por dar", fontsize=9.5, loc="left")
    guardar(fig, "fig1-curva-precio")

    # --- figura 2: el 2x2 de abstencion ---
    celdas = [("sin marco", 5), ("sin marco", 20), ("con marco", 5), ("con marco", 20)]
    etiquetas, medias, lows, highs = [], [], [], []
    for marco, bono in celdas:
        c = abs2["celdas"].get(f"{marco}|K={bono}")
        # Una celda sin corridas, o con corridas pero sin ningun dato de tasa, se salta: el guion
        # corre igual a mitad de campana (se probo asi, y una celda vacia rompia el trazado).
        if not c or not c.get("tasa_toma") or len(c.get("toma_por_corrida") or []) < 2:
            print(f"    (celda {marco} K={bono} sin datos suficientes: se omite)")
            continue
        etiquetas.append(f"{marco}\nK={bono}")
        medias.append(c["tasa_toma"])
        v = c["toma_por_corrida"]
        lows_, highs_ = boot_ic(v) if len(v) > 1 else (medias[-1], medias[-1])
        lows.append(lows_)
        highs.append(highs_)
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    x = range(len(medias))
    ax.errorbar(list(x), medias, yerr=[[m - l for m, l in zip(medias, lows)],
                                       [h - m for m, h in zip(medias, highs)]],
                fmt="o", color=ROJO, capsize=4, lw=1.4, ms=6)
    for i, m in enumerate(medias):
        ax.annotate(f"{m:.1f}%", (i, m), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(etiquetas, fontsize=8)
    ax.set_ylabel("tasa de TOMAR la reserva (%)")
    ax.set_ylim(0, 72)
    ax.set_title("La abstencion: abstenerse es el acto costoso", fontsize=9.5, loc="left")
    guardar(fig, "fig2-abstencion-2x2")

    # --- figura 3: que mueve la conducta ---
    prim = conf["primario_pareado"]
    p_med, p_ic = 100 * prim["media"], [100 * x for x in prim["ic95_bootstrap"]]
    a, b = abs2["celdas"].get("sin marco|K=5"), abs2["celdas"].get("sin marco|K=20")
    if a and b:
        d = (b["tasa_toma"] - a["tasa_toma"]) / 100
        rnd = random.Random(SEMILLA)
        bs = sorted(sum(rnd.choice(b["toma_por_corrida"]) for _ in b["toma_por_corrida"])
                    / len(b["toma_por_corrida"])
                    - sum(rnd.choice(a["toma_por_corrida"]) for _ in a["toma_por_corrida"])
                    / len(a["toma_por_corrida"]) for _ in range(RES))
        d_ic = [100 * bs[int(0.025 * RES)], 100 * bs[int(0.975 * RES)]]
    else:
        print("    (figura 3: falta una de las celdas solo-reserva, se omite la comparacion)")
        d, d_ic = None, (None, None)
    if d is None:
        print("  figuras/fig3 omitida (faltan datos)")
        return
    fig, ax = plt.subplots(figsize=(5.2, 2.4))
    ax.axvline(0, color=GRIS, lw=1, ls="--", alpha=0.7)
    ax.errorbar([p_med], [1], xerr=[[p_med - p_ic[0]], [p_ic[1] - p_med]], fmt="o",
                color=AZUL, capsize=4, ms=7)
    ax.errorbar([d * 100], [0], xerr=[[d * 100 - d_ic[0]], [d_ic[1] - d * 100]], fmt="o",
                color=ROJO, capsize=4, ms=7)
    ax.set_yticks([0, 1])
    ax.set_yticklabels([f"TOMAR\n(K=20 - K=5)", f"DAR\n(precio 20 - 5)"], fontsize=8)
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel("diferencia en puntos porcentuales")
    ax.annotate(f"{d*100:+.1f} pts  [{d_ic[0]:+.1f}, {d_ic[1]:+.1f}]", (d * 100, 0),
                textcoords="offset points", xytext=(0, -18), ha="center", fontsize=7.5, color=ROJO)
    ax.annotate(f"{p_med:+.1f} pts  [{p_ic[0]:+.1f}, {p_ic[1]:+.1f}]", (p_med, 1),
                textcoords="offset points", xytext=(0, 11), ha="center", fontsize=7.5, color=AZUL)
    ax.set_title("Duplicar el costo de dar no mueve; triplicar la ganancia de tomar si",
                 fontsize=9.5, loc="left")
    guardar(fig, "fig3-que-mueve-la-conducta")

    print("\n  figuras listas. Son dato, no prosa: el reporte lo escribe el equipo.")


if __name__ == "__main__":
    main()
