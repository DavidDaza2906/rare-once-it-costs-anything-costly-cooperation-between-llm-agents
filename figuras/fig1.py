"""Figura 1 — mapa de regímenes (ES y EN, 300 dpi). Uso: python3 figuras/fig1.py

2607.23982 va SOBRE la frontera racional con un corchete de ±0,05: prueban márgenes de −0,05 / 0 /
+0,05 alrededor de la frontera de participación privada (verificado en el HTML de arXiv, v7 del
7 sep 2026). Nuestro punto está en beneficio propio = 0, lejos de esa frontera.
"""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
F, FB = "/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
f = lambda s, b=False: ImageFont.truetype(FB if b else F, s)
AZUL, AZULC, LINEA = (40, 70, 120), (232, 240, 250), (70, 110, 170)
ROJO, ROJOC, GRIS = (190, 55, 15), (252, 236, 226), (110, 110, 110)

T = {
 "es": dict(
   ejey="beneficio propio por ayudar", ejex="precio de ayudar",
   t1="Régimen con frontera racional: ayudar conviene si el beneficio propio supera el precio",
   t2="Lo que ya está medido: si el modelo rastrea esa frontera.", frontera="frontera racional",
   mh="Moral hazard en equipos (2607.23982, jul 2026)",
   mhs="9 costos, 18 modelos, n=2, juego textual; prueban márgenes de ±0,05 alrededor de la frontera",
   bp="Bienes públicos con LLM (2506.23276 y otros 5)", bps="contribución costosa, rondas repetidas, bien compartido",
   dn="Juego del donante / reciprocidad (2412.10270, 2602.07777)", dns="dar hoy para recibir mañana: reputación",
   pd="Escala de pagos en dilema del prisionero (2601.19082)", pds="la magnitud cambia la estrategia, en régimen recíproco",
   d1="Régimen dominado (beneficio propio = 0): ayudar NUNCA conviene",
   d2="Lo que se mide aquí es el residuo que queda cuando la razón dice que no.",
   ley=[(GRIS, "1  Costo cero (2604.07821, abr 2026): ayuda gratis e instruida, y aun así falla."),
        (GRIS, "2  Juegos del dictador (2410.21359, 2511.08721): reparto declarado de una dotación regalada;"),
        (GRIS, "    sin tarea, sin herramientas, sin costo instrumental."),
        (ROJO, "o  Este proyecto: precios 0, 5 y 20 pasos de un presupuesto que el agente necesita para su propia"),
        (ROJO, "    tarea, en un sandbox con herramientas y seis agentes co-presentes; solicitud de un desconocido ajeno a"),
        (ROJO, "    todo equipo. Contraste confirmatorio: 5 contra 20. Secundaria: ¿umbral en cero o pendiente?")],
   out="fig1-mapa-regimenes.png"),
 "en": dict(
   ejey="private benefit from helping", ejex="price of helping",
   t1="Rational-boundary regime: helping pays when private benefit exceeds the price",
   t2="What prior work measures: whether the model tracks that boundary.", frontera="rational boundary",
   mh="Moral hazard in teams (2607.23982, Jul 2026)",
   mhs="9 cost levels, 18 models, n=2, textual game; probes margins of ±0.05 around the boundary",
   bp="Public goods with LLMs (2506.23276 and 5 others)", bps="costly contribution, repeated rounds, shared good",
   dn="Donor game / reciprocity (2412.10270, 2602.07777)", dns="give today to receive tomorrow: reputation",
   pd="Payoff scaling in prisoner's dilemma (2601.19082)", pds="stake size changes strategy, in a reciprocal regime",
   d1="Dominated regime (private benefit = 0): helping NEVER pays",
   d2="What we measure: the residue left when rational choice says no.",
   ley=[(GRIS, "1  Zero cost (2604.07821, Apr 2026): help is free and instructed, and still fails."),
        (GRIS, "2  Dictator games (2410.21359, 2511.08721): a stated split of a windfall endowment;"),
        (GRIS, "    no task, no tools, no instrumental cost."),
        (ROJO, "o  This work: prices of 0, 5 and 20 steps out of a budget the agent needs for its own task, inside a"),
        (ROJO, "    tool-using sandbox with six co-present agents; the request comes from a stranger outside any team."),
        (ROJO, "    Confirmatory contrast: 5 vs 20. Secondary: threshold at zero, or slope?")],
   out="fig1-regime-map.png"),
}


def dibujar(t: dict) -> None:
    W, H = 2000, 1300
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 200, 900, 1900, 120
    d.rectangle([x0 + 2, y1 + 30, x1 - 30, y0 - 150], fill=AZULC)
    d.rectangle([x0 + 2, y0 - 148, x1 - 30, y0 - 2], fill=ROJOC)
    d.line([(x0, y0), (x1, y0)], fill="black", width=4); d.line([(x0, y0), (x0, y1)], fill="black", width=4)
    d.polygon([(x1, y0), (x1 - 22, y0 - 11), (x1 - 22, y0 + 11)], fill="black")
    d.polygon([(x0, y1), (x0 - 11, y1 + 22), (x0 + 11, y1 + 22)], fill="black")
    d.text((x0 - 170, y1 - 55), t["ejey"], font=f(30), fill="black")
    d.text((x1 - 330, y0 + 14), t["ejex"], font=f(30), fill="black")
    # frontera racional
    p0, p1 = (x0 + 60, y0 - 165), (x1 - 140, y1 + 110)
    d.line([p0, p1], fill=LINEA, width=5)
    d.text((x0 + 60, y1 + 50), t["t1"], font=f(31, True), fill=AZUL)
    d.text((x0 + 60, y1 + 96), t["t2"], font=f(27), fill=AZUL)
    d.text((x0 + 250, y0 - 330), t["frontera"], font=f(26), fill=LINEA)

    def punto(x, y, etq, sub):
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=LINEA)
        d.text((x + 22, y - 18), etq, font=f(27, True), fill="black")
        d.text((x + 22, y + 14), sub, font=f(24), fill=(60, 60, 60))

    # 2607.23982 sobre la frontera, con corchete ±0,05
    xb = x0 + 620
    yb = p0[1] + (p1[1] - p0[1]) * ((xb - p0[0]) / (p1[0] - p0[0]))
    d.line([(xb, yb - 40), (xb, yb + 40)], fill=LINEA, width=5)
    for yy in (yb - 40, yb + 40):
        d.line([(xb - 14, yy), (xb + 14, yy)], fill=LINEA, width=5)
    punto(xb, int(yb), t["mh"], t["mhs"])
    punto(x0 + 300, y0 - 520, t["bp"], t["bps"])
    punto(x0 + 700, y0 - 620, t["dn"], t["dns"])
    punto(x0 + 900, y0 - 230, t["pd"], t["pds"])
    # banda dominada
    d.text((x0 + 60, y0 - 138), t["d1"], font=f(31, True), fill=ROJO)
    d.text((x0 + 60, y0 - 94), t["d2"], font=f(27), fill=ROJO)
    for x, tag in ((x0 + 45, "1"), (x0 + 520, "2")):
        d.ellipse([x - 15, y0 - 15, x + 15, y0 + 15], fill=GRIS)
        d.text((x - 12, y0 - 52), tag, font=f(28, True), fill=GRIS)
    xs = [(x0 + 45, "0"), (x0 + 1000, "5"), (x0 + 1500, "20")]
    d.line([(xs[0][0], y0), (xs[2][0], y0)], fill=ROJO, width=7)
    for x, lab in xs:
        d.ellipse([x - 21, y0 - 21, x + 21, y0 + 21], outline=ROJO, width=7)
        d.text((x + 28, y0 - 56), lab, font=f(30, True), fill=ROJO)
    ly = y0 + 80
    for col, s in t["ley"]:
        d.text((x0, ly), s, font=f(26, col == ROJO), fill=col); ly += 40
    img.save(os.path.join(AQUI, t["out"]), dpi=(300, 300))
    print("ok ->", t["out"])


for k in ("es", "en"):
    dibujar(T[k])
