#!/usr/bin/env python3
"""Recorre salidas/*/ y construye una tabla por corrida y por agente. Solo lectura. stdlib."""
import os
import json, os, re, sys, random, collections, statistics, hashlib
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'salidas')
OUT = os.path.dirname(os.path.abspath(__file__))

def lote_de(d):
    return d.split('_', 1)[1] if '_' in d else d

runs = []
for d in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, d)
    if not os.path.isdir(p):
        continue
    rec = {'dir': d, 'lote': lote_de(d), 'resumen': False, 'problemas': []}
    ev_path = os.path.join(p, 'eventos.jsonl')
    evs = []
    if os.path.exists(ev_path):
        for line in open(ev_path):
            line = line.strip()
            if line:
                try:
                    evs.append(json.loads(line))
                except Exception:
                    rec['problemas'].append('evento ilegible')
    rec['n_eventos'] = len(evs)
    # cadena
    prev = 'genesis'; roto = 0
    for e in evs:
        if e.get('prev') != prev:
            roto += 1
        prev = e.get('hash')
    rec['cadena_rota'] = roto
    rec['estimulo'] = any(e['tipo'] == 'confederado' for e in evs)
    rec['t_ini'] = evs[0]['t'] if evs else None
    rec['t_fin'] = evs[-1]['t'] if evs else None
    # por agente desde eventos
    ag_ev = collections.defaultdict(lambda: {'depositar': [], 'rechazados': 0, 'comandos': 0, 'consultas': 0, 'entregar': 0, 'acciones': 0, 'reclamar': [], 'error_red': 0})
    idx_en_ronda = collections.Counter()
    ronda_actual = 0
    for e in evs:
        t = str(e['tipo'])
        a = e.get('agente')
        if t == 'ronda_abre':
            ronda_actual = e['ronda']; idx_en_ronda = collections.Counter()
        if not a:
            continue
        g = ag_ev[a]
        if t.startswith('comando_rechazado'):
            g['rechazados'] += 1; g['acciones'] += 1; idx_en_ronda[a] += 1
        elif t.startswith('comando'):
            g['comandos'] += 1; g['acciones'] += 1; idx_en_ronda[a] += 1
            if re.search(r'curl|nc ', t):
                pass
        elif t == 'consulta':
            g['consultas'] += 1
        elif t.startswith('depositar'):
            g['acciones'] += 1; idx_en_ronda[a] += 1
            m = re.search(r'restantes (-?\d+)', e.get('detalle', ''))
            g['depositar'].append({'ronda': e['ronda'], 'costo': e['costo'], 'restantes': int(m.group(1)) if m else None, 'idx': idx_en_ronda[a], 'seq': e['seq'], 'tipo': t})
        elif t.startswith('reclam') or t.startswith('tomar'):
            g['acciones'] += 1; idx_en_ronda[a] += 1
            g['reclamar'].append({'ronda': e['ronda'], 'tipo': t, 'costo': e['costo']})
        elif t == 'entregar':
            g['entregar'] += 1; g['acciones'] += 1; idx_en_ronda[a] += 1
        elif 'error_red' in t or 'rechazado' in t:
            g['error_red'] += 1
    rec['tipos_raros'] = sorted({str(e['tipo']).split(':')[0].split(' ')[0] for e in evs} - {'comando', 'comando_rechazado', 'consulta', 'depositar', 'entregar', 'ronda_abre', 'ronda_cierra', 'inicio', 'confederado'})
    rp = os.path.join(p, 'resumen.json')
    pp = os.path.join(p, 'presupuesto.json')
    pres = json.load(open(pp)) if os.path.exists(pp) else None
    rec['agentes'] = {}
    if os.path.exists(rp):
        r = json.load(open(rp))
        rec['resumen'] = True
        rec['escena'] = r['escena']; rec['hash_escena'] = r['hash_escena']; rec['hash_textos'] = r['hash_textos']
        rec['rondas'] = r['rondas']; rec['tokens'] = r['tokens_totales']
        rec['eventos_decl'] = r['eventos']; rec['ultimo_hash'] = r['ultimo_hash']
        rec['n_depositos_resumen'] = len(r['depositos'])
        rec['confed_en_depositos'] = any(x.get('via') == 'confederado' for x in r['depositos'])
        rec['reclamos'] = r.get('reclamos'); rec['reserva_final'] = r.get('reserva_final')
        if evs and r['ultimo_hash'] != evs[-1]['hash']:
            rec['problemas'].append('ultimo_hash != ultimo evento')
        if r['eventos'] != len(evs):
            rec['problemas'].append(f"eventos decl {r['eventos']} != {len(evs)}")
        for aid, a in r['agentes'].items():
            g = ag_ev.get(aid, {'depositar': [], 'rechazados': 0, 'comandos': 0, 'consultas': 0, 'entregar': 0, 'acciones': 0, 'reclamar': [], 'error_red': 0})
            row = {
                'precio': a['precio_depositar'], 'tipo': a['tipo'], 'deposito': a['deposito'], 'clave': a['deposito_clave'],
                'tarea': a['tarea_correcta'], 'gastado': a['gastado'], 'restante': a['pasos_restantes'], 'puntaje': a['puntaje'],
                'n_depositar': len(g['depositar']), 'depositar': g['depositar'], 'rechazados': g['rechazados'], 'comandos': g['comandos'],
                'consultas': g['consultas'], 'entregar': g['entregar'], 'reclamo': a.get('reclamo'), 'reclamar_ev': g['reclamar'],
                'ronda_entrega': a['ronda_entrega'],
            }
            if pres:
                if pres['gastado'].get(aid) != a['gastado']:
                    rec['problemas'].append(f'{aid}: gastado presupuesto {pres["gastado"].get(aid)} != resumen {a["gastado"]}')
                if pres['restante'].get(aid) != a['pasos_restantes']:
                    rec['problemas'].append(f'{aid}: restante presupuesto {pres["restante"].get(aid)} != resumen {a["pasos_restantes"]}')
                if pres['precios'].get(aid) != a['precio_depositar']:
                    rec['problemas'].append(f'{aid}: precio presupuesto {pres["precios"].get(aid)} != resumen')
            if a['deposito_clave'] and not a['deposito']:
                rec['problemas'].append(f'{aid}: clave sin deposito')
            if a['deposito'] and len(g['depositar']) == 0:
                rec['problemas'].append(f'{aid}: deposito=true sin evento depositar')
            if not a['deposito'] and len(g['depositar']) > 0:
                rec['problemas'].append(f'{aid}: deposito=false con {len(g["depositar"])} eventos depositar')
            if len(g['depositar']) > 1:
                rec['problemas'].append(f'{aid}: paga {len(g["depositar"])} veces')
            if a['pasos_restantes'] < 0:
                rec['problemas'].append(f'{aid}: saldo negativo')
            costo_ev = sum(e['costo'] for e in evs if e.get('agente') == aid)
            if costo_ev != a['gastado']:
                rec['problemas'].append(f'{aid}: suma costos eventos {costo_ev} != gastado {a["gastado"]}')
            rec['agentes'][aid] = row
    else:
        rec['problemas'].append('sin resumen')
    if not rec['estimulo']:
        rec['problemas'].append('sin estimulo')
    if roto:
        rec['problemas'].append(f'cadena rota x{roto}')
    runs.append(rec)

json.dump(runs, open(os.path.join(OUT, 'runs.json'), 'w'), ensure_ascii=False)
print('corridas', len(runs), 'con resumen', sum(r['resumen'] for r in runs))
