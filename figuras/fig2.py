"""Figura 2 — tasa de respuesta contra precio (0 / 5 / 20) con intervalos por corrida.

Lee `figuras/fig2-datos.json`:
  {"puntos": [{"precio": 0, "tasa": 0.48, "lo": 0.35, "hi": 0.61, "n_corridas": 8},
              {"precio": 5, ...}, {"precio": 20, ...}],
   "diferencia_5_20": {"media": -0.02, "lo": -0.12, "hi": 0.08},
   "placeholder": false}
Escribe `figuras/fig2-rate-vs-price.png` (300 dpi). Con "placeholder": true dibuja una marca de agua.
No calcula nada: los números vienen del script de análisis.
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
F = "/usr/share/fonts/TTF/DejaVuSans.ttf"
FB = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
f = lambda s, b=False: ImageFont.truetype(FB if b else F, s)

datos = json.load(open(os.path.join(AQUI, "fig2-datos.json"), encoding="utf-8"))
W, H = 1600, 1100
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

x0, y0, x1, y1 = 180, 900, 1480, 140          # marco del gráfico
d.line([(x0, y0), (x1, y0)], fill="black", width=3)
d.line([(x0, y0), (x0, y1)], fill="black", width=3)
# rejilla y eje y (0 a 1)
for k in range(0, 11, 2):
    y = y0 - (y0 - y1) * k / 10
    d.line([(x0, y), (x1, y)], fill=(225, 225, 225), width=1)
    d.text((x0 - 70, y - 14), f"{k / 10:.1f}", font=f(24), fill="black")
d.text((x0 - 120, y1 - 60), "share of agents that answered the request", font=f(26), fill="black")
d.text((x1 - 260, y0 + 50), "price of helping (steps of 40)", font=f(26), fill="black")

# posiciones x: escala no lineal para que 0, 5 y 20 se lean; se etiqueta con el valor real
pos = {0: x0 + 200, 5: x0 + 650, 20: x0 + 1100}
ROJO = (190, 55, 15)
pts = []
for p in sorted(datos["puntos"], key=lambda z: z["precio"]):
    x = pos[p["precio"]]
    y = y0 - (y0 - y1) * p["tasa"]
    ylo, yhi = y0 - (y0 - y1) * p["lo"], y0 - (y0 - y1) * p["hi"]
    d.line([(x, ylo), (x, yhi)], fill=ROJO, width=4)
    for yy in (ylo, yhi):
        d.line([(x - 14, yy), (x + 14, yy)], fill=ROJO, width=4)
    d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=ROJO)
    d.text((x - 12, y0 + 12), str(p["precio"]), font=f(26, True), fill="black")
    d.text((x + 24, y - 16), f"{100 * p['tasa']:.0f}%", font=f(26, True), fill=ROJO)
    d.text((x + 24, y + 16), f"n = {p['n_corridas']} runs", font=f(20), fill=(90, 90, 90))
    pts.append((x, y))
for a, b in zip(pts, pts[1:]):
    d.line([a, b], fill=ROJO, width=3)

dif = datos.get("diferencia_5_20")
if dif:
    d.text((x0 + 40, y1 + 10),
           f"paired difference 20 − 5 (per run): {100 * dif['media']:+.0f} pts "
           f"[{100 * dif['lo']:+.0f}, {100 * dif['hi']:+.0f}] 95% bootstrap CI by run",
           font=f(24), fill="black")
d.text((x0 + 40, y1 + 46), "price 0 measured on the same scene and hash, after the batch; "
       "bars are bootstrap CIs resampling runs, not agents", font=f(20), fill=(90, 90, 90))

if datos.get("placeholder"):
    d.text((x0 + 300, (y0 + y1) // 2 - 40), "PLACEHOLDER", font=f(60, True),
           fill=(200, 200, 200))

img.save(os.path.join(AQUI, "fig2-rate-vs-price.png"), dpi=(300, 300))
print("ok -> figuras/fig2-rate-vs-price.png")
