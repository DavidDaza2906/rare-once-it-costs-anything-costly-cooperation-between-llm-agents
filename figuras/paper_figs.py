"""Figuras del paper (inglés): SVG a mano + rsvg-convert a PNG 300 dpi. Solo stdlib.

Cifras copiadas de: analisis/formalizacion/tasas-periodo.json (tasas por bloque, IC por remuestreo de
corridas), reportes/confirmatorio.json, reportes/precio-cero.json, reportes/exploratorios.json,
reportes/reclutador.json, reportes/tomar-3x2.json (marco_solo_ronda1),
analisis/formalizacion/tentacion-r1.json, y el conteo de tarea por ayuda sobre el conjunto congelado.
Paleta: categórica de referencia de la skill dataviz (azul #2a78d6, naranja #eb6834), tinta
#0b0b0b / #52514e, rejilla #e5e4e0.
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e5e4e0', '#ffffff'
BLUE, ORANGE = '#2a78d6', '#eb6834'
FONT = "font-family='DejaVu Sans, Helvetica, Arial, sans-serif'"


def save(name, w, h, body):
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>"
           f"<rect width='{w}' height='{h}' fill='{SURF}'/>{body}</svg>")
    p = os.path.join(HERE, name + '.svg')
    open(p, 'w').write(svg)
    subprocess.run(['rsvg-convert', '-z', '3', '-o', os.path.join(HERE, name + '.png'), p], check=True)
    subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', os.path.join(HERE, name + '.pdf'), p], check=True)


def text(x, y, s, size=11, color=INK, anchor='start', weight='normal'):
    return (f"<text x='{x:.1f}' y='{y:.1f}' {FONT} font-size='{size}' fill='{color}' "
            f"text-anchor='{anchor}' font-weight='{weight}'>{s}</text>")


# ---------------- Figure 2: price curve by block ----------------
def fig_price():
    W, H = 650, 360
    L, R, T, B = 70, 30, 20, 60
    pw, ph = W - L - R, H - T - B
    xs = {0: 0.06, 1: 0.32, 5: 0.62, 20: 0.94}
    ymax = 70
    X = lambda p, off=0: L + xs[p] * pw + off
    Y = lambda v: T + ph * (1 - v / ymax)
    body = ''
    for g in range(0, ymax + 1, 10):
        body += f"<line x1='{L}' x2='{L+pw}' y1='{Y(g):.1f}' y2='{Y(g):.1f}' stroke='{GRID}' stroke-width='1'/>"
        body += text(L - 8, Y(g) + 4, f'{g}%', 13, INK2, 'end')
    body += f"<line x1='{L}' x2='{L+pw}' y1='{Y(0):.1f}' y2='{Y(0):.1f}' stroke='{INK2}' stroke-width='1'/>"
    for p in xs:
        body += text(X(p), T + ph + 20, str(p), 14, INK, 'middle')
    body += text(L + pw / 2, H - 14, 'Price of delivering the key (steps, out of a 40-step budget)', 14, INK2, 'middle')
    body += (f"<text transform='translate(18,{T+ph/2}) rotate(-90)' {FONT} font-size='14' fill='{INK2}' "
             f"text-anchor='middle'>Agents delivering the key</text>")
    series = [
        ('13 Sep block', BLUE, -7, [(0, 45.8, 29.2, 62.5, '22/48'), (5, 22.5, 17.1, 28.3, '54/240'), (20, 16.7, 12.1, 21.7, '40/240')]),
        ('14 Sep block', ORANGE, 7, [(1, 35.4, 20.8, 47.9, '17/48'), (5, 36.2, 27.7, 44.7, '51/141'), (20, 26.2, 19.1, 33.3, '37/141')]),
    ]
    for name, col, off, pts in series:
        d = ' '.join(f"{'M' if i == 0 else 'L'}{X(p, off):.1f},{Y(v):.1f}" for i, (p, v, lo, hi, n) in enumerate(pts))
        body += f"<path d='{d}' fill='none' stroke='{col}' stroke-width='2'/>"
        for p, v, lo, hi, n in pts:
            body += f"<line x1='{X(p,off):.1f}' x2='{X(p,off):.1f}' y1='{Y(lo):.1f}' y2='{Y(hi):.1f}' stroke='{col}' stroke-width='2'/>"
            body += f"<circle cx='{X(p,off):.1f}' cy='{Y(v):.1f}' r='5' fill='{col}' stroke='{SURF}' stroke-width='2'/>"
            dx = -10 if off < 0 else 10
            if p == 1:
                body += text(X(p, off) + 10, Y(v) - 10, f'{v:.1f}%', 13, INK, 'start')
            else:
                body += text(X(p, off) + dx, Y(v) + 4, f'{v:.1f}%', 13, INK, 'end' if off < 0 else 'start')
    for j, (name, col, off, pts) in enumerate(series):
        ly = T + 8 + 20 * j
        body += f"<line x1='{L+pw*0.55:.1f}' x2='{L+pw*0.55+22:.1f}' y1='{ly:.1f}' y2='{ly:.1f}' stroke='{col}' stroke-width='3'/>"
        body += f"<circle cx='{L+pw*0.55+11:.1f}' cy='{ly:.1f}' r='4.5' fill='{col}'/>"
        body += text(L + pw * 0.55 + 30, ly + 4, name + (' (prices 0, 5, 20)' if j == 0 else ' (prices 1, 5, 20)'), 13.5, INK)
    save('paper-fig2-price', W, H, body)


# ---------------- Figure 3: forest plot of every contrast ----------------
def fig_forest():
    rows = [
        ('h', 'GIVING: deliver the key'),
        ('r', 'Price 20 − 5, paired (confirmatory)', -7.4, -13.1, -1.6, True),
        ('r', 'Price 0 − 5, all price-5 runs', 18.3, 1.9, 35.5, False),
        ('r', 'Price 0 − 5, same time window', 30.2, 12.5, 47.9, False),
        ('r', 'Peer − outsider asks (price 5)', 4.5, -18.7, 28.5, False),
        ('r', 'Recruiter: peer − third party (p 5)', 0.0, -12.5, 12.5, False),
        ('r', 'Recruiter: peer − third party (p 20)', -8.3, -25.0, 8.3, False),
        ('h', 'TAKING, round 1: claim the reserve'),
        ('r', 'K 20 − 5, no request', -4.2, -18.8, 8.3, False),
        ('r', 'K 20 − 5, neutral request', 4.2, -14.6, 25.0, False),
        ('r', 'K 20 − 5, recruiter request', -4.2, -13.5, 5.2, False),
        ('r', 'No request − neutral, K 5', 14.6, -2.1, 31.2, False),
        ('r', 'No request − neutral, K 20', 6.2, -12.5, 22.9, False),
        ('r', 'No request − recruiter, K 5', 12.5, -1.0, 26.0, False),
        ('r', 'No request − recruiter, K 20', 12.5, 2.1, 22.2, False),
    ]
    W = 640
    rowh, T = 25, 12
    H = T + rowh * len(rows) + 62
    L, pw = 300, 320
    lo_x, hi_x = -30, 50
    X = lambda v: L + pw * (v - lo_x) / (hi_x - lo_x)
    body = ''
    for g in range(lo_x, hi_x + 1, 10):
        body += f"<line x1='{X(g):.1f}' x2='{X(g):.1f}' y1='{T}' y2='{T+rowh*len(rows)}' stroke='{GRID}' stroke-width='1'/>"
        body += text(X(g), T + rowh * len(rows) + 18, (f'{g:+d}' if g else '0').replace('-', '−'), 13, INK2, 'middle')
    body += f"<line x1='{X(0):.1f}' x2='{X(0):.1f}' y1='{T}' y2='{T+rowh*len(rows)}' stroke='{INK2}' stroke-width='1.2' stroke-dasharray='4 3'/>"
    body += text(L + pw / 2, H - 24, 'Difference, percentage points (95% CI)', 13, INK2, 'middle')
    body += text(L + pw / 2, H - 6, 'Filled: interval excludes 0', 12, INK2, 'middle')
    for i, r in enumerate(rows):
        y = T + rowh * i + rowh * 0.65
        if r[0] == 'h':
            body += text(6, y, r[1], 14, INK, 'start', 'bold')
            continue
        _, lab, v, lo, hi, conf = r
        excl = lo > 0 or hi < 0
        body += text(14, y, lab, 13.5, INK, 'start', 'bold' if conf else 'normal')
        yc = y - 4
        body += f"<line x1='{X(max(lo,lo_x)):.1f}' x2='{X(min(hi,hi_x)):.1f}' y1='{yc:.1f}' y2='{yc:.1f}' stroke='{BLUE}' stroke-width='2'/>"
        fill = BLUE if excl else SURF
        body += f"<circle cx='{X(v):.1f}' cy='{yc:.1f}' r='5.5' fill='{fill}' stroke='{BLUE}' stroke-width='2'/>"
    save('paper-fig3-contrasts', W, H, body)


# ---------------- Figure 4: own-task completion by helping ----------------
def fig_task():
    W, H = 650, 320
    L, R, T, B = 70, 40, 30, 55
    pw, ph = W - L - R, H - T - B
    cats = [('Price 0', 95.5, '21/22', 100.0, '26/26'), ('Price 5', 82.9, '87/105', 93.8, '259/276'),
            ('Price 20', 71.4, '55/77', 93.1, '283/304')]
    ymin, ymax = 60, 100
    Y = lambda v: T + ph * (1 - (v - ymin) / (ymax - ymin))
    X = lambda i: L + pw * (i + 0.5) / len(cats)
    body = ''
    for g in range(ymin, ymax + 1, 10):
        body += f"<line x1='{L}' x2='{L+pw}' y1='{Y(g):.1f}' y2='{Y(g):.1f}' stroke='{GRID}' stroke-width='1'/>"
        body += text(L - 8, Y(g) + 4, f'{g}%', 13, INK2, 'end')
    body += (f"<text transform='translate(18,{T+ph/2}) rotate(-90)' {FONT} font-size='14' fill='{INK2}' "
             f"text-anchor='middle'>Own task completed correctly</text>")
    for i, (c, h, hn, n, nn) in enumerate(cats):
        x = X(i)
        body += f"<line x1='{x:.1f}' x2='{x:.1f}' y1='{Y(h):.1f}' y2='{Y(n):.1f}' stroke='{GRID}' stroke-width='3'/>"
        body += f"<circle cx='{x:.1f}' cy='{Y(n):.1f}' r='6' fill='{BLUE}' stroke='{SURF}' stroke-width='2'/>"
        body += f"<circle cx='{x:.1f}' cy='{Y(h):.1f}' r='6' fill='{ORANGE}' stroke='{SURF}' stroke-width='2'/>"
        body += text(x + 11, Y(n) + 4, f'{n:.1f}% ({nn})', 13, INK)
        body += text(x + 11, Y(h) + 4, f'{h:.1f}% ({hn})', 13, INK)
        body += text(x, T + ph + 20, c, 14, INK, 'middle')
    lx, ly = L + 16, Y(66)
    body += f"<circle cx='{lx}' cy='{ly:.1f}' r='6' fill='{BLUE}'/>" + text(lx + 12, ly + 4, 'Did not deliver the key', 13.5)
    body += f"<circle cx='{lx}' cy='{ly+22:.1f}' r='6' fill='{ORANGE}'/>" + text(lx + 12, ly + 26, 'Delivered the key', 13.5)
    body += text(L + pw / 2, H - 12, 'Price (steps of a 40-step budget)', 14, INK2, 'middle')
    save('paper-fig4-task', W, H, body)


if __name__ == '__main__':
    fig_price(); fig_forest(); fig_task()
    print('ok')
