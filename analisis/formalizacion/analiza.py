#!/usr/bin/env python3
import json, os, random, collections, statistics, glob
import os; S = os.path.dirname(os.path.abspath(__file__))
runs = json.load(open(f'{S}/runs.json'))
random.seed(20260913)

def valida(r):
    if not r['resumen']: return False, 'sin resumen'
    if len(r['agentes']) != 6: return False, 'n_ag!=6'
    if 'tope_tokens' in r['tipos_raros']: return False, 'tope_tokens'
    if 'error_red' in r['tipos_raros']: return False, 'error_red'
    if any(a['restante'] < 0 for a in r['agentes'].values()): return False, 'saldo negativo'
    if r['cadena_rota']: return False, 'cadena rota'
    return True, ''

def boot(vals_por_corrida, reps=10000):
    """vals_por_corrida: lista de (k, n) por corrida. IC del cociente sum k / sum n por remuestreo de corridas."""
    m = len(vals_por_corrida)
    if m < 3: return None
    out = []
    for _ in range(reps):
        s = [vals_por_corrida[random.randrange(m)] for _ in range(m)]
        K = sum(k for k, n in s); N = sum(n for k, n in s)
        out.append(K / N if N else 0)
    out.sort()
    return round(out[int(0.025 * reps)] * 100, 1), round(out[int(0.975 * reps)] * 100, 1)

def tasa(rs, precio=None, campo='clave', filtro=None):
    per = []
    for r in rs:
        k = n = 0
        for a in r['agentes'].values():
            if precio is not None and a['precio'] != precio: continue
            if filtro and not filtro(a): continue
            n += 1; k += bool(a[campo])
        if n: per.append((k, n))
    K = sum(k for k, n in per); N = sum(n for k, n in per)
    return {'corridas': len(per), 'k': K, 'n': N, 'tasa': round(100 * K / N, 1) if N else None, 'ic95_corridas': boot(per)}

print('=== A. VALIDEZ por lote ===')
val = collections.defaultdict(list); exc = collections.Counter()
for r in runs:
    ok, why = valida(r)
    if ok: val[(r['lote'], r['hash_textos'])].append(r)
    else: exc[(r['lote'], why)] += 1
for k, v in sorted(exc.items()): print('  excluida', k, v)
for k, v in sorted(val.items()): print('  validas', k, len(v))

print('\n=== B. CURVA PRECIO -> TASA (clave), por brazo, solo válidas ===')
curva = [
    ('factorial-costo-cero', 0), ('precio-uno', 1), ('factorial-base', 5), ('factorial-base', 20),
    ('solicitante-par-p5', 5), ('solicitante-externo-p5', 5), ('factorial-reclutador', 5), ('factorial-reclutador', 20),
    ('factorial-reclutador-par-arbol2', 5), ('factorial-reclutador-par-arbol2', 20),
    ('factorial-abstencion', 5), ('factorial-abstencion', 20), ('factorial-abstencion-caro', 5), ('factorial-abstencion-caro', 20),
    ('factorial-reclutador-abstencion-arbol2', 5), ('factorial-reclutador-abstencion-arbol2', 20),
    ('factorial-reclutador-abstencion-caro-arbol2', 5), ('factorial-reclutador-abstencion-caro-arbol2', 20),
]
for lote, p in curva:
    rs = [r for (l, h), v in val.items() if l == lote for r in v]
    if not rs: continue
    h = rs[0]['hash_textos']
    print(f'  {lote:45s} p={p:2d} hash_textos={h}', tasa(rs, p), 'deposito:', tasa(rs, p, 'deposito')['tasa'], 'tarea:', tasa(rs, p, 'tarea')['tasa'])

print('\n=== B2. factorial-base: congelado 70 vs extensión, y por lote de origen ===')
fb = sorted(val[('factorial-base', '4e8f2619ed0966ec')], key=lambda r: r['dir'])
print('  válidas factorial-base:', len(fb))
cong = [c['corrida'] for c in json.load(open('/home/daw/Sprint/reportes/conjunto-congelado.json'))['corridas']]
fb70 = [r for r in fb if r['dir'] in cong[:70]]; fbext = [r for r in fb if r['dir'] in cong[70:]]; fbno = [r for r in fb if r['dir'] not in cong]
for nom, rs in [('primeras 70', fb70), ('extensión 57', fbext), ('válidas no congeladas', fbno)]:
    print(f'  {nom:22s} n={len(rs)} p5', tasa(rs, 5), 'p20', tasa(rs, 20))
# por lote manifest
lote_de = {}
for f in glob.glob('/home/daw/Sprint/salidas/lote_*.json'):
    m = json.load(open(f))
    for d in m['detalle']:
        lote_de[os.path.basename(os.path.dirname(d['log']))] = m['etiqueta']
for et in sorted(set(lote_de.values())):
    rs = [r for r in fb if lote_de.get(r['dir']) == et]
    if rs: print(f'  lote {et:28s} n={len(rs):3d} p5 {tasa(rs,5)["tasa"]} p20 {tasa(rs,20)["tasa"]}  ambos {tasa(rs)["tasa"]}')
print('  sin lote manifest:', [r['dir'] for r in fb if r['dir'] not in lote_de])
# diferencia pareada p20-p5
difs = []
for r in fb:
    k5 = sum(a['clave'] for a in r['agentes'].values() if a['precio'] == 5); k20 = sum(a['clave'] for a in r['agentes'].values() if a['precio'] == 20)
    difs.append((k20 - k5) / 3)
bs = []
for _ in range(10000):
    s = [difs[random.randrange(len(difs))] for _ in difs]; bs.append(sum(s) / len(s))
bs.sort(); print(f'  pareado p20-p5 (n={len(difs)}): media {statistics.mean(difs):.4f} IC [{bs[250]:.4f},{bs[9749]:.4f}]')
# tendencia temporal: por bloques de 20 en orden de arranque
for i in range(0, len(fb), 20):
    rs = fb[i:i + 20]; print(f'  orden {i:3d}-{i+len(rs)-1:3d}: p5 {tasa(rs,5)["tasa"]:5.1f} p20 {tasa(rs,20)["tasa"]:5.1f} ambos {tasa(rs)["tasa"]:5.1f} tokens med {statistics.median(r["tokens"] for r in rs):.0f}')

print('\n=== C. PAGOS MÚLTIPLES / DEPÓSITO SIN CLAVE (todas las corridas con resumen, por brazo) ===')
for (lote, h), rs in sorted(val.items()):
    ag = [a for r in rs for a in r['agentes'].values()]
    if not ag: continue
    multi = [a for a in ag if a['n_depositar'] >= 2]
    pagos = sum(a['n_depositar'] for a in ag)
    gasto_dep = sum(d['costo'] for a in ag for d in a['depositar'])
    dep_sin_clave = sum(1 for a in ag if a['deposito'] and not a['clave'])
    print(f'  {lote:45s} agentes {len(ag):3d} pagan>=1 {sum(a["n_depositar"]>=1 for a in ag):3d} pagan>=2 {len(multi):3d} pagos totales {pagos:3d} pasos pagados {gasto_dep:4d} depósito sin clave {dep_sin_clave:3d}')

print('\n=== D. NO PUDO vs NO QUISO (factorial-base válidas) ===')
ag = [(r, aid, a) for r in fb for aid, a in r['agentes'].items()]
sinp = collections.Counter(); imp = collections.Counter()
for r in fb:
    for e_t in []: pass
# leer eventos otra vez para sin_presupuesto por agente
import re
sp_by = collections.defaultdict(list)
for r in fb:
    for l in open(f"/home/daw/Sprint/salidas/{r['dir']}/eventos.jsonl"):
        e = json.loads(l)
        if e['tipo'] == 'sin_presupuesto': sp_by[(r['dir'], e['agente'])].append(e['detalle'])
for p in (5, 20):
    A = [(r, aid, a) for r, aid, a in ag if a['precio'] == p]
    n = len(A)
    clave = sum(a['clave'] for _, _, a in A)
    dep_no_clave = sum(1 for _, _, a in A if a['deposito'] and not a['clave'])
    quiso_no_pudo = sum(1 for r, aid, a in A if not a['deposito'] and (r['dir'], aid) in sp_by)
    rech = sum(1 for _, _, a in A if a['rechazados'] > 0)
    consulto = sum(1 for _, _, a in A if a['consultas'] > 0)
    no_consulto_no_dep = sum(1 for _, _, a in A if a['consultas'] == 0 and not a['deposito'])
    print(f'  p={p}: n={n} clave={clave} depósito-sin-clave={dep_no_clave} sin_presupuesto-sin-depositar(quiso,no pudo)={quiso_no_pudo} con comando_rechazado={rech} consultaron red={consulto} ni consultó ni depositó={no_consulto_no_dep}')
print('  total eventos sin_presupuesto en factorial-base válidas:', sum(len(v) for v in sp_by.values()), 'agentes:', len(sp_by))
print('  ejemplos:', list(sp_by.values())[:3])

print('\n=== E. TIMING de la entrega (factorial-base válidas, primer depósito pagado con clave) ===')
rondas = collections.Counter(); idx = collections.Counter(); rest = []
for r in fb:
    for aid, a in r['agentes'].items():
        if a['clave'] and a['depositar']:
            d = a['depositar'][0]; rondas[(a['precio'], d['ronda'])] += 1; idx[d['idx']] += 1; rest.append((a['precio'], d['restantes']))
print('  ronda del primer pago (precio, ronda):', sorted(rondas.items()))
print('  índice de acción dentro de la ronda:', sorted(idx.items()))
for p in (5, 20):
    v = [x for q, x in rest if q == p]
    print(f'  restantes tras pagar p={p}: n={len(v)} mediana {statistics.median(v)} min {min(v)} max {max(v)}')
# ronda de entrega de tarea vs clave
print('  ronda_entrega de tarea vs clave:', collections.Counter((a['clave'], a['ronda_entrega']) for r in fb for a in r['agentes'].values()))

print('\n=== F. TAREA vs CLAVE (factorial-base válidas) ===')
ct = collections.Counter((a['precio'], a['tarea'], a['clave']) for r in fb for a in r['agentes'].values())
for k in sorted(ct): print('  (precio, tarea_ok, clave)', k, ct[k])
for p in (5, 20):
    tok = [a for r in fb for a in r['agentes'].values() if a['precio'] == p and a['tarea']]
    tno = [a for r in fb for a in r['agentes'].values() if a['precio'] == p and not a['tarea']]
    print(f'  p={p}: clave|tarea_ok {sum(a["clave"] for a in tok)}/{len(tok)}  clave|tarea_fallo {sum(a["clave"] for a in tno)}/{len(tno)}')
print('  gastado medio (sin contar el precio) clave vs no clave:',
      {c: round(statistics.mean(a['gastado'] - sum(d['costo'] for d in a['depositar']) for r in fb for a in r['agentes'].values() if a['clave'] == c), 1) for c in (True, False)})
# puntaje consistencia
bad = [(r['dir'], aid) for r in fb for aid, a in r['agentes'].items() if a['puntaje'] != (15 if a['tarea'] else 0) + a['restante']]
print('  puntaje != 15*tarea + restante:', len(bad), bad[:3])

print('\n=== G. POSICIÓN (agente-0i) en brazos de precio uniforme y factorial ===')
for lote in ('factorial-base', 'factorial-costo-cero', 'precio-uno', 'solicitante-par-p5', 'solicitante-externo-p5'):
    rs = [r for (l, h), v in val.items() if l == lote for r in v]
    c = collections.Counter(); n = collections.Counter()
    for r in rs:
        for aid, a in r['agentes'].items(): c[aid] += a['clave']; n[aid] += 1
    print(f'  {lote:25s}', {k: f'{c[k]}/{n[k]}' for k in sorted(n)})

print('\n=== H. RECLAMOS (tomar) por brazo, y conjunto con depósito ===')
for (lote, h), rs in sorted(val.items()):
    if not rs or rs[0]['agentes'] and list(rs[0]['agentes'].values())[0]['reclamo'] is None: continue
    ag = [a for r in rs for a in r['agentes'].values()]
    tom = sum(1 for a in ag if a['reclamo']); dep = sum(a['deposito'] for a in ag); ambos = sum(1 for a in ag if a['reclamo'] and a['deposito'])
    r1 = sum(1 for a in ag for e in a['reclamar_ev'][:1] if e['ronda'] == 1)
    print(f'  {lote:45s} corridas {len(rs):2d} agentes {len(ag):3d} toman {tom:3d} ({100*tom/len(ag):.1f}%) IC {boot([(sum(1 for a in r["agentes"].values() if a["reclamo"]),6) for r in rs])} depositan {dep} ambos {ambos} toma_en_r1 {r1} reserva_final {collections.Counter(r["reserva_final"] for r in rs).most_common(3)}')

print('\n=== I. EXCLUIDAS detalle (precio-uno, externo, par, costo-cero) ===')
for r in runs:
    if r['lote'] in ('precio-uno', 'solicitante-externo-p5', 'solicitante-par-p5', 'factorial-costo-cero'):
        ok, why = valida(r)
        if not ok: print('  ', r['dir'], why, r['tipos_raros'], 'clave', sum(a['clave'] for a in r['agentes'].values()))
