"""Figuras de los brazos exploratorios, desde figuras/exploratorios-datos.json (lo escribe
analisis/exploratorios.py). Produce:
  - figuras/curva-precio.png     : tasa de entrega vs precio 0/1/5/20 (5 y 20 marcados PENDIENTE)
  - figuras/identidad.png        : par vs externo, con IC y diferencia
Robusto a datos ausentes: dibuja placeholders para lo que aún no se corrió. No calcula nada.
Uso:  python3 figuras/fig-exploratorios.py
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
F = "/usr/share/fonts/TTF/DejaVuSans.ttf"
FB = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
f = lambda s, b=False: ImageFont.truetype(FB if b else F, s)
ROJO, AZUL, GRIS = (190, 55, 15), (62, 109, 166), (150, 150, 150)

datos = json.load(open(os.path.join(AQUI, "exploratorios-datos.json"), encoding="utf-8"))


def y_de(pct, y0=900, ytop=140, top=0.70):
    return y0 - (pct / top) * (y0 - ytop)


def curva():
    W, H = 1600, 1100
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    x0, y0, x1, ytop = 180, 900, 1480, 140
    for k in range(0, 8, 2):
        y = y_de(k / 10)
        d.line([(x0, y), (x1, y)], fill=(228, 228, 228), width=1)
        d.text((x0 - 70, y - 14), f"{k/10:.1f}", font=f(24), fill="black")
    d.line([(x0, y0), (x1, y0)], fill="black", width=3)
    d.line([(x0, y0), (x0, ytop)], fill="black", width=3)
    d.text((x0 - 120, ytop - 55), "tasa de entrega de la clave", font=f(26), fill="black")
    d.text((x1 - 230, y0 + 46), "precio (pasos)", font=f(26), fill="black")
    # posiciones no lineales de 0,1,5,20
    px = {0: x0 + 150, 1: x0 + 360, 5: x0 + 720, 20: x0 + 1150}
    medidos = {p["precio"]: p for p in datos.get("curva", [])}
    pend = datos.get("pendiente", [])
    pts = []
    for precio in (0, 1, 5, 20):
        x = px[precio]
        d.text((x - 10, y0 + 12), str(precio), font=f(26, True), fill="black")
        if precio in medidos:
            m = medidos[precio]; y = y_de(m["tasa"])
            if m.get("ic"):
                ylo, yhi = y_de(m["ic"][0]), y_de(m["ic"][1])
                d.line([(x, ylo), (x, yhi)], fill=ROJO, width=4)
                for yy in (ylo, yhi):
                    d.line([(x - 12, yy), (x + 12, yy)], fill=ROJO, width=4)
            if m.get("ic"):
                d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=ROJO)
            else:   # menos de 3 corridas: punto hueco, sin intervalo, no se lee como estimación
                d.ellipse([x - 11, y - 11, x + 11, y + 11], outline=ROJO, width=3)
            d.text((x + 20, y - 16), f"{100*m['tasa']:.0f}%", font=f(26, True), fill=ROJO)
            d.text((x + 20, y + 12), f"n={m['n_corridas']}" + ("" if m.get("ic") else " prov."),
                   font=f(18), fill=GRIS)
            pts.append((x, y))
        elif precio in pend:
            d.ellipse([x - 10, y_de(0.35) - 10, x + 10, y_de(0.35) + 10], outline=GRIS, width=3)
            d.text((x - 34, y_de(0.35) - 44), "pend.", font=f(20), fill=GRIS)
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=ROJO, width=3)
    d.text((x0, y0 + 92), "precios 5 y 20 = contraste confirmatorio (se congela y mira una sola vez, aparte)",
           font=f(20), fill=GRIS)
    img.save(os.path.join(AQUI, "curva-precio.png"), dpi=(200, 200)); print("ok -> curva-precio.png")


def identidad():
    ident = datos.get("identidad", {})
    W, H = 1200, 1000
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    x0, y0, ytop = 220, 820, 140
    for k in range(0, 8, 2):
        y = y_de(k / 10, y0, ytop); d.line([(x0, y), (1080, y)], fill=(228, 228, 228), width=1)
        d.text((x0 - 70, y - 14), f"{k/10:.1f}", font=f(24), fill="black")
    d.line([(x0, y0), (1080, y0)], fill="black", width=3)
    d.line([(x0, y0), (x0, ytop)], fill="black", width=3)
    d.text((x0 - 130, ytop - 55), "tasa de entrega de la clave (precio 5)", font=f(24), fill="black")
    for i, (lab, col) in enumerate((("par", AZUL), ("externo", GRIS))):
        arm = ident.get(lab, {})
        cx = x0 + 230 + i * 380
        d.text((cx - 40, y0 + 14), lab, font=f(26, True), fill="black")
        if arm.get("corridas"):
            y = y_de(arm["tasa_clave"], y0, ytop)
            d.rectangle([cx - 90, y, cx + 90, y0], fill=col)
            ic = arm.get("ic95_bootstrap_por_corrida")
            if ic:
                ylo, yhi = y_de(ic[0], y0, ytop), y_de(ic[1], y0, ytop)
                d.line([(cx, ylo), (cx, yhi)], fill="black", width=3)
                for yy in (ylo, yhi):
                    d.line([(cx - 16, yy), (cx + 16, yy)], fill="black", width=3)
            d.text((cx - 34, y - 40), f"{100*arm['tasa_clave']:.0f}%", font=f(26, True), fill="black")
            d.text((cx - 40, y0 - 34), f"n={arm['corridas']}", font=f(18), fill="white")
        else:
            d.text((cx - 60, y_de(0.35, y0, ytop)), "sin datos", font=f(22), fill=GRIS)
    dif = ident.get("diferencia")
    if dif and dif.get("insuficiente"):
        d.text((x0, 900), f"par − externo: {100*dif['media']:+.0f} pts — descriptivo, sin intervalo "
               f"({dif['insuficiente']})", font=f(22), fill=GRIS)
    elif dif and dif.get("ic95"):
        d.text((x0, 900), f"par − externo: {100*dif['media']:+.0f} pts  IC95 "
               f"[{100*dif['ic95'][0]:+.0f}, {100*dif['ic95'][1]:+.0f}]  "
               f"({'incluye cero' if dif['incluye_cero'] else 'excluye cero'})",
               font=f(24), fill="black")
    else:
        d.text((x0, 900), "diferencia: pendiente de corridas", font=f(22), fill=GRIS)
    img.save(os.path.join(AQUI, "identidad.png"), dpi=(200, 200)); print("ok -> identidad.png")


curva()
identidad()
