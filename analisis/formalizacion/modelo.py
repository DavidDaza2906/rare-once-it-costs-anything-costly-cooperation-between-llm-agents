"""Formulaciones sobre la curva de precio: logit con umbral + pendiente, mezcla de tipos,
costo esperado en unidades de puntaje. Solo stdlib. Remuestreo por corrida."""
import json, math, random, datetime as dt
from collections import defaultdict

import os; R = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'runs.json')))
HASH = '4e8f2619ed0966ec'
CORTE = dt.datetime(2026, 9, 14, 1, 0, tzinfo=dt.timezone.utc).timestamp()  # 13 sep vs 14 sep UTC

runs = []
for q in R:
    if not q['resumen'] or q.get('hash_textos') != HASH or len(q['agentes']) != 6:
        continue
    if any(t in q['tipos_raros'] for t in ('tope_tokens', 'error_red')) or q['cadena_rota']:
        continue
    if any(p.startswith(('sin ', 'saldo')) for p in q['problemas']):
        continue
    if q['lote'] not in ('factorial-base', 'factorial-costo-cero', 'precio-uno'):
        continue
    if q['dir'] == '20260914T021758_factorial-base':  # contaminada, excluida del congelado
        continue
    per = 1 if q['t_ini'] >= CORTE else 0
    ags = [(a['precio'], int(a['clave']), int(a['tarea']), per, q['lote']) for a in q['agentes'].values()]
    runs.append(ags)
print('corridas', len(runs), 'agentes', sum(len(r) for r in runs))

def tabla(rs):
    c = defaultdict(lambda: [0, 0])
    for r in rs:
        for p, y, t, per, l in r:
            c[(per, p)][0] += y; c[(per, p)][1] += 1
    return c
for k, (y, n) in sorted(tabla(runs).items()):
    print(f'  periodo {k[0]} precio {k[1]:2d}: {y}/{n} = {100*y/n:.1f}%')

# --- logit: logit P = a + g*periodo + d*1[p>0] + b*p
def fit(rs, feats):
    X, Y = [], []
    for r in rs:
        for p, y, t, per, l in r:
            X.append(feats(p, per)); Y.append(y)
    k = len(X[0]); w = [0.0] * k
    for _ in range(50):
        g = [0.0] * k; H = [[0.0] * k for _ in range(k)]
        for x, y in zip(X, Y):
            z = sum(wi * xi for wi, xi in zip(w, x)); z = max(min(z, 30), -30)
            m = 1 / (1 + math.exp(-z)); s = m * (1 - m)
            for i in range(k):
                g[i] += (y - m) * x[i]
                for j in range(k):
                    H[i][j] += s * x[i] * x[j]
        # resolver H dw = g (gauss)
        A = [row[:] + [g[i]] for i, row in enumerate(H)]
        for i in range(k):
            piv = max(range(i, k), key=lambda r_: abs(A[r_][i])); A[i], A[piv] = A[piv], A[i]
            for r_ in range(k):
                if r_ != i:
                    f = A[r_][i] / A[i][i]
                    for c_ in range(i, k + 1): A[r_][c_] -= f * A[i][c_]
        dw = [A[i][k] / A[i][i] for i in range(k)]
        w = [wi + di for wi, di in zip(w, dw)]
        if max(abs(d) for d in dw) < 1e-8: break
    return w

def boot(rs, feats, B=2000, seed=20260913):
    rnd = random.Random(seed); est = fit(rs, feats); out = []
    for _ in range(B):
        s = [rs[rnd.randrange(len(rs))] for _ in rs]
        try: out.append(fit(s, feats))
        except ZeroDivisionError: pass
    lo = [sorted(o[i] for o in out)[int(0.025 * len(out))] for i in range(len(est))]
    hi = [sorted(o[i] for o in out)[int(0.975 * len(out))] for i in range(len(est))]
    return est, lo, hi

nombres = ['intercepto', 'periodo14', 'umbral 1[p>0]', 'pendiente por paso']
f = lambda p, per: [1.0, float(per), float(p > 0), float(p)]
est, lo, hi = boot(runs, f)
print('\nLOGIT umbral+pendiente, IC por remuestreo de corridas (2000):')
for n, e, l, h in zip(nombres, est, lo, hi):
    print(f'  {n:20s} {e:+.3f}  [{l:+.3f}, {h:+.3f}]')
d, b = est[2], est[3]
print(f'  pendiente equivalente en pasos: el umbral vale como {d/b:.1f} pasos de precio' if b else '')
# probabilidades ajustadas por precio, periodo 0 y 1
for per in (0, 1):
    fila = []
    for p in (0, 1, 5, 20):
        z = est[0] + est[1] * per + est[2] * (p > 0) + est[3] * p
        fila.append(f'p{p}={100/(1+math.exp(-z)):.1f}%')
    print(f'  ajustado periodo {per}:', ' '.join(fila))

# Modelo solo pendiente (sin umbral) para comparar verosimilitud
def loglik(rs, feats, w):
    ll = 0
    for r in rs:
        for p, y, t, per, l in r:
            z = sum(wi * xi for wi, xi in zip(w, feats(p, per))); m = 1 / (1 + math.exp(-z))
            ll += y * math.log(m) + (1 - y) * math.log(1 - m)
    return ll
f2 = lambda p, per: [1.0, float(per), float(p)]
w2 = fit(runs, f2)
print(f'\n  log-verosimilitud umbral+pendiente {loglik(runs, f, est):.1f}  solo pendiente {loglik(runs, f2, w2):.1f}  '
      f'(LR = {2*(loglik(runs,f,est)-loglik(runs,f2,w2)):.1f}, 1 gl; ingenuo, agentes no independientes)')
f3 = lambda p, per: [1.0, float(per), float(p > 0)]
w3 = fit(runs, f3)
print(f'  solo umbral {loglik(runs, f3, w3):.1f}  (LR umbral+pend vs solo umbral = {2*(loglik(runs,f,est)-loglik(runs,f3,w3)):.1f})')

# --- Mezcla de tipos: nunca / siempre / sensibles
print('\nMEZCLA DE TIPOS (por periodo, tasas crudas):')
for per in (0, 1):
    t = tabla(runs); r = {p: t[(per, p)][0] / t[(per, p)][1] for p in (0, 1, 5, 20) if t[(per, p)][1]}
    if 0 in r and 20 in r:
        print(f'  periodo {per}: siempre~p20={100*r[20]:.1f}%  nunca~1-p0={100*(1-r[0]):.1f}%  '
              f'sensibles={100*(r[0]-r[20]):.1f}% de los cuales ceden entre 0 y 5: {100*(r[0]-r[5]):.1f}pts, entre 5 y 20: {100*(r[5]-r[20]):.1f}pts')
    else:
        print(f'  periodo {per}: ' + '  '.join(f'p{p}={100*v:.1f}%' for p, v in sorted(r.items())))

# --- Costo esperado en puntaje y semi-elasticidad
print('\nPUNTAJE SACRIFICADO ESPERADO por agente = tasa(p) * p  (puntaje = 15*tarea + restantes):')
t = tabla(runs); agg = defaultdict(lambda: [0, 0])
for (per, p), (y, n) in t.items(): agg[p][0] += y; agg[p][1] += n
for p in (0, 1, 5, 20):
    y, n = agg[p]; r = y / n
    print(f'  p{p:2d}: tasa {100*r:.1f}%  -> {r*p:.2f} pasos de puntaje por agente ({100*r*p/15:.0f}% del bono de tarea)')
r5, r20 = agg[5][0] / agg[5][1], agg[20][0] / agg[20][1]
print(f'  semi-elasticidad 5->20: dlogP/dp = {math.log(r20/r5)/15:+.4f} por paso; elasticidad-arco = {(math.log(r20/r5))/(math.log(20/5)):+.3f}')

# --- Curva de "precio de reserva": fraccion que paga a precio >= p (supervivencia)
print('\nDEMANDA: fraccion dispuesta a pagar al menos p (agregado, mezcla periodos):')
for p in (0, 1, 5, 20):
    y, n = agg[p]; print(f'  D({p:2d}) = {100*y/n:.1f}%')
