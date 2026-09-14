#!/usr/bin/env python3
import json, os, random, collections, statistics
import os; S = os.path.dirname(os.path.abspath(__file__))
ROOT = '/home/daw/Sprint/salidas'
runs = json.load(open(f'{S}/runs.json'))
random.seed(20260913)

def valida(r):
    return r['resumen'] and len(r['agentes']) == 6 and 'tope_tokens' not in r['tipos_raros'] and 'error_red' not in r['tipos_raros'] \
        and not any(a['restante'] < 0 for a in r['agentes'].values()) and not r['cadena_rota']

def boot_ratio(per, reps=10000):
    m = len(per)
    if m < 3: return None
    out = []
    for _ in range(reps):
        s = [per[random.randrange(m)] for _ in range(m)]
        N = sum(n for k, n in s); out.append(sum(k for k, n in s) / N if N else 0)
    out.sort(); return (round(100 * out[int(.025 * reps)], 1), round(100 * out[int(.975 * reps)], 1))

def boot_mean(vals, reps=10000):
    m = len(vals)
    if m < 3: return None
    out = sorted(sum(vals[random.randrange(m)] for _ in range(m)) / m for _ in range(reps))
    return (round(out[int(.025 * reps)], 4), round(out[int(.975 * reps)], 4))

def fmt(per):
    K = sum(k for k, n in per); N = sum(n for k, n in per)
    return f'{K}/{N}={100*K/N:.1f}% IC{boot_ratio(per)} ({len(per)} corr)' if N else 'n=0'

fb = sorted([r for r in runs if valida(r) and r['lote'] == 'factorial-base'], key=lambda r: r['dir'])
periodo = lambda r: '13sep' if r['dir'] < '20260914' else '14sep'

# enriquecer: ronda del primer depósito con clave, chars de transcripción, orden de turno
for r in fb:
    res = json.load(open(f"{ROOT}/{r['dir']}/resumen.json"))
    for aid, a in r['agentes'].items():
        clave = res['agentes'][aid]['clave']
        rk = [d['ronda'] for d in res['depositos'] if d.get('agente') == aid and clave and clave in d['texto']]
        a['ronda_clave'] = min(rk) if rk else None
        a['n_dep_resumen'] = sum(1 for d in res['depositos'] if d.get('agente') == aid)
        a['dep_textos'] = [d['texto'][:30] for d in res['depositos'] if d.get('agente') == aid]
        chars = 0; turnos = 0
        for f in os.listdir(f"{ROOT}/{r['dir']}/transcripciones"):
            if f.endswith(f'_{aid}.json'):
                t = json.load(open(f"{ROOT}/{r['dir']}/transcripciones/{f}"))
                chars += sum(len(m.get('texto', '')) + len(m.get('razonamiento', '') or '') + len(json.dumps(m.get('llamadas', []))) for m in t)
                turnos += sum(1 for m in t if m['rol'] == 'assistant')
        a['chars'] = chars; a['turnos'] = turnos
        a['eventos'] = a['comandos'] + a['rechazados'] + a['consultas'] + a['n_depositar'] + a['entregar']
    # orden de turno en ronda 1
    orden = []
    for l in open(f"{ROOT}/{r['dir']}/eventos.jsonl"):
        e = json.loads(l)
        if e['ronda'] == 1 and e.get('agente') and e['agente'] not in orden: orden.append(e['agente'])
    r['orden_r1'] = orden

print(f'factorial-base válidas: {len(fb)}; 13sep {sum(periodo(r)=="13sep" for r in fb)}, 14sep {sum(periodo(r)=="14sep" for r in fb)}')
inc = sum(1 for r in fb for a in r['agentes'].values() if a['clave'] and a['ronda_clave'] is None)
print('clave=true sin depósito de clave localizable en resumen.depositos:', inc)

print('\n=== 1. CONTAGIO: P(entrega en r | no había entregado, k claves ajenas visibles al inicio de r) ===')
for p in (5, 20):
    for r_ in (2, 3, 4):
        cel = collections.defaultdict(list)
        for r in fb:
            ags = r['agentes']
            per = collections.defaultdict(lambda: [0, 0])
            for aid, a in ags.items():
                if a['precio'] != p or (a['ronda_clave'] is not None and a['ronda_clave'] < r_): continue
                vis = sum(1 for b, x in ags.items() if b != aid and x['ronda_clave'] is not None and x['ronda_clave'] < r_)
                k = '0' if vis == 0 else '1' if vis == 1 else '2+'
                per[k][1] += 1; per[k][0] += int(a['ronda_clave'] == r_)
            for k, v in per.items(): cel[k].append(tuple(v))
        print(f'  p={p} ronda {r_}: ' + ' | '.join(f'vis={k}: {fmt(cel[k])}' for k in ('0', '1', '2+') if k in cel))
# agrupado rondas 2-4, por precio
for p in (5, 20):
    cel = collections.defaultdict(list)
    for r in fb:
        ags = r['agentes']; per = collections.defaultdict(lambda: [0, 0])
        for r_ in (2, 3, 4):
            for aid, a in ags.items():
                if a['precio'] != p or (a['ronda_clave'] is not None and a['ronda_clave'] < r_): continue
                vis = sum(1 for b, x in ags.items() if b != aid and x['ronda_clave'] is not None and x['ronda_clave'] < r_)
                k = '0' if vis == 0 else '1' if vis == 1 else '2+'
                per[k][1] += 1; per[k][0] += int(a['ronda_clave'] == r_)
        for k, v in per.items(): cel[k].append(tuple(v))
    print(f'  p={p} rondas 2-4 agrupadas (agente-ronda): ' + ' | '.join(f'vis={k}: {fmt(cel[k])}' for k in ('0', '1', '2+') if k in cel))

print('\n=== 2. HAZARD por ronda, precio y período ===')
for per_ in ('13sep', '14sep', 'todos'):
    for p in (5, 20):
        row = []
        for r_ in (1, 2, 3, 4):
            per = []
            for r in fb:
                if per_ != 'todos' and periodo(r) != per_: continue
                riesgo = [a for a in r['agentes'].values() if a['precio'] == p and (a['ronda_clave'] is None or a['ronda_clave'] >= r_)]
                per.append((sum(1 for a in riesgo if a['ronda_clave'] == r_), len(riesgo)))
            row.append(f'r{r_} {fmt(per)}')
        print(f'  {per_:6s} p={p:2d}: ' + ' | '.join(row))
# pendiente 20-5 en ronda 1 vs rondas 2-4 (pareado por corrida)
for nom, cond in (('ronda 1', lambda a: a['ronda_clave'] == 1), ('rondas 2-4', lambda a: a['ronda_clave'] in (2, 3, 4)), ('total', lambda a: a['ronda_clave'] is not None)):
    d = []
    for r in fb:
        k5 = sum(cond(a) for a in r['agentes'].values() if a['precio'] == 5); k20 = sum(cond(a) for a in r['agentes'].values() if a['precio'] == 20)
        d.append((k20 - k5) / 3)
    print(f'  pareado 20-5 {nom:10s}: media {statistics.mean(d):+.4f} IC {boot_mean(d)} n={len(d)}')

print('\n=== 3. ACTIVIDAD vs entrega y período ===')
for per_ in ('13sep', '14sep'):
    rs = [r for r in fb if periodo(r) == per_]
    for p in (5, 20):
        for c in (True, False):
            ag = [a for r in rs for a in r['agentes'].values() if a['precio'] == p and a['clave'] == c]
            print(f'  {per_} p={p:2d} clave={c!s:5s} n={len(ag):3d} eventos/ag {statistics.mean(a["eventos"] for a in ag):5.1f} chars/ag {statistics.mean(a["chars"] for a in ag):7.0f} turnos/ag {statistics.mean(a["turnos"] for a in ag):5.1f} gastado {statistics.mean(a["gastado"] for a in ag):5.1f}')
    ag = [a for r in rs for a in r['agentes'].values()]
    print(f'  {per_} TODOS: eventos/ag {statistics.mean(a["eventos"] for a in ag):.2f} chars/ag {statistics.mean(a["chars"] for a in ag):.0f} tokens/corrida med {statistics.median(r["tokens"] for r in rs):.0f} tarea {100*statistics.mean(a["tarea"] for a in ag):.1f}%')
def pearson(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y)); sx = sum((a - mx) ** 2 for a in x) ** .5; sy = sum((b - my) ** 2 for b in y) ** .5
    return sxy / (sx * sy)
x = [r['tokens'] for r in fb]; y = [sum(a['clave'] for a in r['agentes'].values()) / 6 for r in fb]
rr = pearson(x, y); bs = []
for _ in range(10000):
    idx = [random.randrange(len(fb)) for _ in fb]; bs.append(pearson([x[i] for i in idx], [y[i] for i in idx]))
bs.sort(); print(f'  corr(tokens corrida, tasa clave corrida) r={rr:.3f} IC [{bs[250]:.3f},{bs[9749]:.3f}] n={len(fb)}')
for per_ in ('13sep', '14sep'):
    rs = [r for r in fb if periodo(r) == per_]; print(f'    {per_}: r={pearson([r["tokens"] for r in rs],[sum(a["clave"] for a in r["agentes"].values())/6 for r in rs]):.3f} n={len(rs)}')
# dentro de período: eventos por agente vs clave, corr a nivel agente
for per_ in ('13sep', '14sep'):
    ag = [a for r in fb if periodo(r) == per_ for a in r['agentes'].values()]
    print(f'    {per_}: corr(eventos agente, clave) r={pearson([a["eventos"] for a in ag],[float(a["clave"]) for a in ag]):.3f}; corr(chars, clave) r={pearson([a["chars"] for a in ag],[float(a["clave"]) for a in ag]):.3f}')

print('\n=== 4. PAREADO 20-5 por resultado de tarea ===')
for nom, f in (('tarea ok', lambda a: a['tarea']), ('tarea falla', lambda a: not a['tarea']), ('todos', lambda a: True)):
    d = []; per5 = []; per20 = []
    for r in fb:
        a5 = [a for a in r['agentes'].values() if a['precio'] == 5 and f(a)]; a20 = [a for a in r['agentes'].values() if a['precio'] == 20 and f(a)]
        if a5: per5.append((sum(a['clave'] for a in a5), len(a5)))
        if a20: per20.append((sum(a['clave'] for a in a20), len(a20)))
        if a5 and a20: d.append(sum(a['clave'] for a in a20) / len(a20) - sum(a['clave'] for a in a5) / len(a5))
    print(f'  {nom:12s}: p5 {fmt(per5)}  p20 {fmt(per20)}  pareado(corridas con ambos) media {statistics.mean(d):+.4f} IC {boot_mean(d)} n={len(d)}')

print('\n=== 5. PRECIO 0: depósitos por agente ===')
cz = [r for r in runs if valida(r) and r['lote'] == 'factorial-costo-cero']
for r in cz:
    res = json.load(open(f"{ROOT}/{r['dir']}/resumen.json"))
    for aid, a in r['agentes'].items():
        a['n_dep_resumen'] = sum(1 for d in res['depositos'] if d.get('agente') == aid)
        a['dep_textos'] = [d['texto'][:25] for d in res['depositos'] if d.get('agente') == aid]
for nom, rs, p in (('p0 costo-cero', cz, 0), ('p5 factorial-base', fb, 5), ('p20 factorial-base', fb, 20)):
    ag = [a for r in rs for a in r['agentes'].values() if a['precio'] == p]
    dep = [a for a in ag if a['n_dep_resumen'] > 0]
    print(f'  {nom:18s} agentes {len(ag):3d}: depositan {len(dep)} ({100*len(dep)/len(ag):.1f}%), clave {sum(a["clave"] for a in ag)}, depósitos/agente {sum(a["n_dep_resumen"] for a in ag)/len(ag):.2f}, depósitos/depositante {sum(a["n_dep_resumen"] for a in dep)/max(1,len(dep)):.2f}, ≥2 depósitos {sum(a["n_dep_resumen"]>=2 for a in ag)}, depositan sin clave {sum(1 for a in dep if not a["clave"])}, dist {collections.Counter(a["n_dep_resumen"] for a in ag)}')
print('  textos p0 (no clave):', [t for r in cz for a in r['agentes'].values() for t in a['dep_textos'] if not (a['clave'] and any(t in x for x in a['dep_textos']) and len(t) == 8 and t.isupper())][:20])

print('\n=== 6. AGENTE-01 ===')
print('  orden de turno en ronda 1 (primer evento):', collections.Counter(tuple(r['orden_r1']) for r in fb).most_common(3))
for aid in sorted(fb[0]['agentes']):
    ag = [r['agentes'][aid] for r in fb]
    ronda_c = collections.Counter(a['ronda_clave'] for a in ag if a['clave'])
    print(f'  {aid}: clave {sum(a["clave"] for a in ag)}/{len(ag)} tarea {100*statistics.mean(a["tarea"] for a in ag):.0f}% eventos {statistics.mean(a["eventos"] for a in ag):.1f} chars {statistics.mean(a["chars"] for a in ag):.0f} consultas {statistics.mean(a["consultas"] for a in ag):.2f} gastado {statistics.mean(a["gastado"] for a in ag):.1f} ronda_clave {dict(sorted(ronda_c.items()))} dep sin clave {sum(1 for a in ag if a["deposito"] and not a["clave"])} parte_propia {collections.Counter(str(a.get("entregado"))[-2:] for a in ag).most_common(2)}')
# parte propia por agente
res0 = json.load(open(f"{ROOT}/{fb[0]['dir']}/resumen.json"))
print('  entregado en corrida 1:', {aid: res0['agentes'][aid]['entregado'][:12] for aid in res0['agentes']})
# agente-01 vs 02/03 por período
for per_ in ('13sep', '14sep'):
    rs = [r for r in fb if periodo(r) == per_]
    d = [r['agentes']['agente-01']['clave'] - (r['agentes']['agente-02']['clave'] + r['agentes']['agente-03']['clave']) / 2 for r in rs]
    print(f'  {per_}: 01 {sum(r["agentes"]["agente-01"]["clave"] for r in rs)}/{len(rs)}, 02 {sum(r["agentes"]["agente-02"]["clave"] for r in rs)}, 03 {sum(r["agentes"]["agente-03"]["clave"] for r in rs)}; 01-media(02,03) {statistics.mean(d):+.3f} IC {boot_mean(d)}')

print('\n=== 7. PRECIO 20 y saldo ===')
rest = [a['depositar'][0]['restantes'] for r in fb for a in r['agentes'].values() if a['precio'] == 20 and a['clave'] and a['depositar']]
print('  restantes tras pagar (p20, clave):', sorted(collections.Counter(rest).items()))
nop = [a for r in fb for a in r['agentes'].values() if a['precio'] == 20 and not a['deposito']]
print(f'  no pagaron a p20: {len(nop)}; terminaron con >=20 restantes: {sum(a["restante"]>=20 for a in nop)} ({100*sum(a["restante"]>=20 for a in nop)/len(nop):.1f}%), <20: {sum(a["restante"]<20 for a in nop)}; dist restantes {sorted(collections.Counter((a["restante"]//5)*5 for a in nop).items())}')
print(f'  de los <20: con evento sin_presupuesto (intentaron): ver informe anterior (3). tarea ok entre >=20: {100*statistics.mean(a["tarea"] for a in nop if a["restante"]>=20):.0f}%, entre <20: {100*statistics.mean(a["tarea"] for a in nop if a["restante"]<20):.0f}%')
nop5 = [a for r in fb for a in r['agentes'].values() if a['precio'] == 5 and not a['deposito']]
print(f'  no pagaron a p5: {len(nop5)}; con >=5 restantes {sum(a["restante"]>=5 for a in nop5)}; con >=20 restantes {sum(a["restante"]>=20 for a in nop5)}')

print('\n=== 8. OTROS ===')
# deposito de clave en ronda == ronda de entrega de tarea?
print('  ronda_clave vs ronda_entrega (clave=true):', collections.Counter(('antes' if a['ronda_clave'] < (a['ronda_entrega'] or 9) else 'misma' if a['ronda_clave'] == a['ronda_entrega'] else 'después') for r in fb for a in r['agentes'].values() if a['clave']))
# corridas con 0 y con >=4 claves
print('  claves por corrida:', sorted(collections.Counter(sum(a['clave'] for a in r['agentes'].values()) for r in fb).items()))
# claves depositadas ajenas: agentes que depositan la clave de OTRO
otras = 0
for r in fb:
    res = json.load(open(f"{ROOT}/{r['dir']}/resumen.json")); claves = {res['agentes'][x]['clave']: x for x in res['agentes']}
    for d in res['depositos']:
        if d.get('agente') in res['agentes'] and any(c in d['texto'] for c, x in claves.items() if x != d['agente']): otras += 1
print('  depósitos que contienen la clave de otro agente:', otras)
# tiempo por ronda
dur = [(r['t_fin'] - r['t_ini']) / 60 for r in fb]
print(f'  duración corrida (min): mediana {statistics.median(dur):.1f}, 13sep {statistics.median([(r["t_fin"]-r["t_ini"])/60 for r in fb if periodo(r)=="13sep"]):.1f}, 14sep {statistics.median([(r["t_fin"]-r["t_ini"])/60 for r in fb if periodo(r)=="14sep"]):.1f}')
