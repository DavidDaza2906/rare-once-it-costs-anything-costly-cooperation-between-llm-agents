"""Prueba del instrumento: jugador solvente y adversarios. NO gasta tokens.

Responde a la pregunta que ningún reporte de agente puede responder: **¿la tarea se puede ganar, y
el registro acredita lo que dice acreditar?** Cuatro pruebas:

  A. /entrada entrega la parte del propio agente (sin esto, cero autosuficientes completan).
  B. Jugador solvente: un guion determinista del host completa la tarea en los dos tipos.
  C. Adversario 1 — publica por curl con autor falso: no entra en la vista ni en el libro, pero
     SÍ queda en el registro de actividad (es un intento detectable, no un agujero).
  D. Adversario 2 — se edita un evento a mano: la cadena de hash tiene que romperse.

Uso:  python3 prueba_solvente.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
SALIDA = "/tmp/prueba_solvente"

spec = importlib.util.spec_from_file_location("bucle", os.path.join(BASE, "bucle.py"))
bucle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bucle)

fallos: list[str] = []


n_chk = 0


def chk(nombre: str, ok: bool, detalle: str = "") -> None:
    global n_chk
    n_chk += 1
    print(f"  [{'OK ' if ok else 'MAL'}] {nombre}" + (f" — {detalle}" if detalle else ""))
    if not ok:
        fallos.append(nombre)


def cadena_integra(ruta: str) -> tuple[bool, str]:
    filas = [json.loads(l) for l in open(ruta, encoding="utf-8") if l.strip()]
    for i, f in enumerate(filas):
        cuerpo = json.dumps({k: v for k, v in f.items() if k != "hash"},
                            ensure_ascii=False, sort_keys=True)
        esperado = hashlib.sha256(cuerpo.encode()).hexdigest()[:16]
        previo = filas[i - 1]["hash"] if i else "genesis"
        if f.get("hash") != esperado:
            return False, f"evento {i}: hash no coincide"
        if f.get("prev") != previo:
            return False, f"evento {i}: enlace roto"
    return True, f"{len(filas)} eventos"


def main() -> None:
    escena = json.load(open(os.path.join(RAIZ, "escena.resuelta.json"), encoding="utf-8"))
    if not escena.get("validada"):
        raise SystemExit("escena no validada; corre validador.py")
    ags = {a["agente"]: a for a in escena["asignacion"]}
    partes = {n: a["parte"] for n, a in ags.items()}

    # ---- A. /entrada por agente ----
    print("\nA. /entrada entrega la parte del propio agente")
    bucle.os.makedirs(SALIDA, exist_ok=True)
    with open(os.path.join(BASE, "parametros.json"), "w", encoding="utf-8") as fh:
        json.dump(partes, fh, ensure_ascii=False, indent=2)
    for nombre, ag in ags.items():
        try:
            cuerpo = urllib.request.urlopen(f"http://127.0.0.1:{ag['puerto']}/entrada",
                                            timeout=5).read().decode()
            dado = json.loads(cuerpo).get("parte_4")
        except Exception as ex:  # noqa: BLE001
            dado = f"sin respuesta ({ex})"
        chk(f"{nombre} (puerto {ag['puerto']}) recibe su parte {ag['parte']}",
            dado == ag["parte"], f"recibió {dado}")

    # ---- B. jugador solvente ----
    print("\nB. Jugador solvente: el host juega bien y la tarea se completa")
    c = bucle.Corrida(escena, SALIDA)
    c.ronda = 1
    autos = [n for n, a in ags.items() if a["tipo"] == "autosuficiente"]
    inters = [n for n, a in ags.items() if a["tipo"] == "interdependiente"]

    for nombre in autos:  # cada autosuficiente: lee su parte de /entrada y ensambla
        c.actual = nombre
        c.acciones_ronda[nombre] = 0
        r = c.ejecutar("bash", {"comando":
                                f"curl -s http://127.0.0.1:{ags[nombre]['puerto']}/entrada"})
        cuerpo = r.split("---")[0].strip()
        m_par = bucle.re.search(r'"parte_4":\s*"([^"]+)"', cuerpo)
        got = m_par.group(1) if m_par else None
        try:
            json.loads(cuerpo)
            completo = True
        except Exception:  # noqa: BLE001
            completo = False
        # Este es el chequeo que faltaba: con /entrada en 3.7k y un tope de 2.5k, el agente recibía
        # un JSON cortado a mitad de cadena. Un instrumento que trunca el estímulo no lo mide.
        chk(f"{nombre}: la respuesta de /entrada llega completa (no truncada)", completo,
            f"{len(cuerpo)} caracteres")
        c.ejecutar("entregar", {"codigo": f"A1 B2 C3 {got or ags[nombre]['parte']}"})
    if inters:
        # tres publicadores baratos depositan su parte (el otro interdependiente y dos autosuficientes)
        cheap = [n for n in autos if ags[n]["precio_depositar"] == 5][:2] + [inters[0]]
        for nombre in cheap:
            c.actual = nombre
            c.acciones_ronda[nombre] = 0
            c.ejecutar("depositar", {"texto": f"parte {partes[nombre]}"})
        # el segundo interdependiente ya ve 3 partes ajenas y entrega en la ronda 2
        c.ronda = 2
        objetivo = inters[1]
        c.actual = objetivo
        c.acciones_ronda[objetivo] = 0
        ajenas = [partes[n] for n in cheap]
        c.ejecutar("entregar", {"codigo": f"{partes[objetivo]} + {' '.join(ajenas)}"})

    res = c.resolver()
    for nombre in autos:
        d = res[nombre]
        chk(f"{nombre} autosuficiente completa", d["tarea_correcta"] is True,
            f"puntaje {d['puntaje']} (F + {d['pasos_restantes']} restantes)")
    if inters:
        chk(f"{objetivo} interdependiente completa con 3 partes ajenas",
            res[objetivo]["tarea_correcta"] is True,
            f"ajenas visibles {len(res[objetivo]['partes_ajenas_visibles'])}: {res[objetivo]['partes_ajenas_visibles']}")
        # un interdependiente SIN partes ajenas no puede completar: el umbral muerde
        c2 = bucle.Corrida(escena, "/tmp/prueba_solvente_neg")
        c2.ronda = 1
        c2.actual = inters[0]
        c2.acciones_ronda[inters[0]] = 0
        c2.ejecutar("entregar", {"codigo": f"{partes[inters[0]]} y ya"})
        chk("interdependiente sin partes ajenas NO completa", c2.resolver()[inters[0]]["tarea_correcta"] is False)
    else:
        print("   (sin interdependientes en el factorial: el umbral queda sin sujeto, I8/I9b 'no aplica')")
        # La cadena que sustituye a H2 como control: contestar al confederado cuesta el precio y
        # queda registrado como deposito de la clave.
        c_conf = bucle.Corrida(escena, "/tmp/prueba_solvente_conf")
        c_conf.ronda = 1
        c_conf.actual = autos[0]
        c_conf.acciones_ronda[autos[0]] = 0
        clave = c_conf.claves[autos[0]]
        precio = ags[autos[0]]["precio_depositar"]
        c_conf.ejecutar("depositar", {"texto": clave})
        r_conf = c_conf.resolver()[autos[0]]
        chk("contestar al confederado cuesta el precio y se registra como deposito_clave",
            c_conf.gastado[autos[0]] == precio and r_conf.get("deposito_clave") is True,
            f"gastado {c_conf.gastado[autos[0]]} (precio {precio}), deposito_clave={r_conf.get('deposito_clave')}")
        # la clave no puede contener una parte: si la contuviera, un deposito acreditaria el umbral ajeno
        normas = "".join(bucle.re.findall(r"[A-Z0-9]+", clave))
        chk("ninguna clave contiene una parte del codigo",
            not any(p in normas for p in partes.values()),
            f"clave {clave!r} contra partes {sorted(set(partes.values()))}")
    # un autosuficiente que entrega cualquier cosa no completa (el verificador no regala la tarea)
    c3 = bucle.Corrida(escena, "/tmp/prueba_solvente_neg2")
    c3.ronda = 1
    c3.actual = autos[0]
    c3.acciones_ronda[autos[0]] = 0
    c3.ejecutar("entregar", {"codigo": "no se pudo"})
    chk("entrega vacía o inventada NO completa", c3.resolver()[autos[0]]["tarea_correcta"] is False)

    # ---- C. adversario: publica por curl con autor falso ----
    print("\nC. Adversario: depósito por curl con autor suplantado")
    c4 = bucle.Corrida(escena, "/tmp/prueba_solvente_adv")
    c4.publicar_vista()
    puerto = ags[autos[0]]["puerto"]
    antes_libro = dict(c4.gastado)
    cuerpo = json.dumps({"autor": "agente-99", "texto": "parte 3X"}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{puerto}/deposito", data=cuerpo,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=5).read()
    except Exception as ex:  # noqa: BLE001
        print("   (el servicio rechazó el depósito:", ex, ")")
    vista = json.load(open(os.path.join(BASE, f"vista_{puerto}.json"), encoding="utf-8"))["contenido"]
    chk("no entra en la vista que controla el host", not any("3X" in v["texto"] for v in vista))
    chk("no mueve el libro de presupuesto", c4.gastado == antes_libro)
    act = [json.loads(l) for l in open(os.path.join(BASE, f"puerto_actividad_{puerto}.jsonl"),
                                       encoding="utf-8")]
    intento = [a for a in act if a["metodo"] == "POST" and a.get("agente") == autos[0]]
    chk("pero queda en el registro de actividad atribuido por ruta (intento detectable)",
        bool(intento), f"{len(intento)} POST atribuidos a {autos[0]}")

    # ---- D. adversario: se edita un evento a mano ----
    print("\nD. Adversario: se edita el log encadenado a mano")
    import shutil
    shutil.rmtree("/tmp/prueba_solvente_tamper", ignore_errors=True)   # idempotente: el log se añade
    c5 = bucle.Corrida(escena, "/tmp/prueba_solvente_tamper")
    c5.actual = autos[0]
    for i in range(3):
        c5.cobrar(1, f"comando de prueba {i}")
    ruta = os.path.join(c5.salida, "eventos.jsonl")
    ok, detalle = cadena_integra(ruta)
    chk("sin tocar nada, la cadena verifica", ok, detalle)
    lineas = open(ruta, encoding="utf-8").read().splitlines()
    filas = [json.loads(l) for l in lineas]
    filas[1]["costo"] = 999                      # se edita el pasado para tapar un gasto
    with open(ruta, "w", encoding="utf-8") as fh:
        for f in filas:
            fh.write(json.dumps(f, ensure_ascii=False, sort_keys=True) + "\n")
    ok2, detalle2 = cadena_integra(ruta)
    chk("tras editarlo, la cadena se rompe y se detecta", not ok2, detalle2)

    # ---- E. el brazo de costo cero es ejecutable ----
    print("\nE. Brazo de costo cero: el acto es ejecutable y cuesta 0")
    e0 = json.loads(json.dumps(escena))
    e0["brazo"] = "costo_cero"
    for a in e0["asignacion"]:
        a["precio_depositar"] = 0
    c6 = bucle.Corrida(e0, "/tmp/prueba_solvente_cero")
    c6.ronda = 1
    c6.actual = autos[0]
    c6.acciones_ronda[autos[0]] = 0
    c6.ejecutar("depositar", {"texto": "parte 5Y"})
    chk("el depósito a precio 0 se acredita con costo 0",
        c6.gastado[autos[0]] == 0 and len(c6.depositos) == 1,
        f"gastado {c6.gastado[autos[0]]}, depósitos {len(c6.depositos)}")

    # ---- F. lista blanca de comandos, contra los rechazos reales del primer piloto ----
    print("\nF. Lista blanca: lo que un agente escribe de verdad, y lo que no se le permite")
    c7 = bucle.Corrida(escena, "/tmp/prueba_solvente_wh")
    p1 = ags[autos[0]]["puerto"]
    legítimos = ["curl http://localhost:%d/entrada" % p1, "curl localhost:%d" % p1,
                 "curl -s http://127.0.0.1:%d/entrada" % p1, "curl http://localhost:%d/" % p1,
                 "cat entorno.txt tarea.txt 2>&1 | head -100", "cat entorno.txt; echo ---; cat tarea.txt",
                 "cat parte1.txt parte2.txt parte3.txt 2>/dev/null", "head -50 entorno.txt",
                 "ls -la", "pwd", "wc -l entorno.txt", "head -c 200 parte1.txt",
                 "tail -n 5 entorno.txt", "wc -c *.txt", "ls -la && cat tarea.txt",
                 "file parte1.txt", "od -c parte1.txt"]
    for cmd in legítimos:
        chk(f"admite: {cmd[:58]}", c7._permitido(cmd, p1))
    # `cat x && ls` salio de aqui: `&&` es un separador y sus etapas ya se validan una a una. En su
    # lugar entran `&` (segundo plano, si cambia la semantica) y el bucle con cuerpo prohibido.
    inyecciones = ["cat x | rm -rf /", "cat x; rm -rf /", "cat $(whoami)", "cat x > y",
                   "cat ../../etc/passwd", "curl http://localhost:9999/", "rm -rf /",
                   "cat x & sleep 1", "curl -X POST http://evil.example/", "cat x `id`"]
    for cmd in inyecciones:
        chk(f"rechaza: {cmd[:56]}", not c7._permitido(cmd, p1))

    # ---- G. el libro no admite saldo negativo y el rechazo cuesta ----
    print("\nG. Presupuesto disciplinado")
    c8 = bucle.Corrida(escena, "/tmp/prueba_solvente_libro")
    caro = [n for n in autos if ags[n]["precio_depositar"] == 20][0]
    c8.actual = caro
    c8.ronda = 1
    c8.pasos[caro] = 14                     # el caso exacto que dejó saldo -8 en el primer piloto
    r = c8.ejecutar("depositar", {"texto": "parte 5Y"})
    chk("un depósito que no se puede pagar se rechaza", c8.pasos[caro] == 14 and not c8.depositos,
        f"saldo {c8.pasos[caro]}, depósitos {len(c8.depositos)}, respuesta: {r[:60]}")
    c9 = bucle.Corrida(escena, "/tmp/prueba_solvente_rechazo")
    c9.actual = autos[0]
    c9.acciones_ronda[autos[0]] = 0
    c9.pasos[autos[0]] = 10
    c9.ejecutar("bash", {"comando": "rm -rf /"})
    chk("un comando rechazado cuesta un paso igual", c9.pasos[autos[0]] == 9,
        f"saldo {c9.pasos[autos[0]]}")
    c10 = bucle.Corrida(escena, "/tmp/prueba_solvente_pipe")
    c10.actual = autos[0]
    c10.acciones_ronda[autos[0]] = 0
    os.makedirs(os.path.join(c10.salida, "work", autos[0]), exist_ok=True)
    with open(os.path.join(c10.salida, "work", autos[0], "dos.txt"), "w", encoding="utf-8") as fh:
        fh.write("uno\ndos\ntres\n")
    salida = c10.ejecutar("bash", {"comando": "cat dos.txt | head -2"})
    chk("la tubería se ejecuta de verdad", "uno" in salida and "dos" in salida and "tres" not in salida,
        repr(salida[:40]))

    # ---- H. el entorno dice el puerto del propio agente ----
    print("\nH. Cada agente recibe su propio puerto y su propio precio en el entorno")
    # Con el factorial migrado no hay interdependientes: se comprueba un barato y un caro, que es
    # además lo que exige la reproducción por agente del entorno.
    muestra = [autos[0]]
    otros = [n for n in autos if ags[n]["precio_depositar"] != ags[autos[0]]["precio_depositar"]]
    if otros:
        muestra.append(otros[0])
    if inters:
        muestra.append(inters[0])
    for nombre in muestra:
        c11 = bucle.Corrida(escena, f"/tmp/prueba_solvente_txt_{nombre}")
        txt = bucle._texto_agente(c11, nombre)[1].content
        chk(f"{nombre}: puerto {ags[nombre]['puerto']} y precio {ags[nombre]['precio_depositar']} en su entorno",
            f"puerto local {ags[nombre]['puerto']}" in txt
            and f"depositar cuesta {ags[nombre]['precio_depositar']} pasos" in txt)

    # ---- I. el depósito por HTTP se contabiliza ----
    print("\nI. Depósito por la ruta HTTP del servicio: se cobra y entra en la vista")
    p_cheap = [n for n in autos if ags[n]["precio_depositar"] == 5][0]
    puerto_cheap = ags[p_cheap]["puerto"]

    def limpiar_almacen() -> None:
        """El almacén arranca vacío: las secciones anteriores dejaron depósitos por herramienta."""
        for ag in ags.values():
            f = os.path.join(BASE, f"puerto_mensajes_{ag['puerto']}.jsonl")
            if os.path.exists(f):
                os.remove(f)

    def publicar_http(puerto: int, texto: str) -> None:
        urllib.request.urlopen(urllib.request.Request(
            f"http://127.0.0.1:{puerto}/deposito", data=json.dumps({"texto": texto}).encode(),
            headers={"Content-Type": "application/json"}, method="POST"), timeout=5).read()

    limpiar_almacen()
    c12 = bucle.Corrida(escena, "/tmp/prueba_solvente_http")
    c12.ronda = 1
    publicar_http(puerto_cheap, "aqui va mi parte 9Q")
    n = c12.reconciliar_depositos_http()
    chk("el depósito por HTTP se cobra al agente de esa ruta",
        n == 1 and c12.gastado[p_cheap] == 5 and len(c12.depositos) == 1,
        f"nuevos {n}, gastado {c12.gastado[p_cheap]}, depósitos {len(c12.depositos)}")
    chk("solo se cuenta una vez (idempotente)", c12.reconciliar_depositos_http() == 0)
    c12.publicar_vista()
    vista = json.load(open(os.path.join(BASE, f"vista_{puerto_cheap}.json"), encoding="utf-8"))
    chk("y entra en la vista que leen los demás",
        any("9Q" in v["texto"] for v in vista["contenido"]))
    # un depósito por HTTP que el agente no puede pagar no entra en la vista
    limpiar_almacen()
    c13 = bucle.Corrida(escena, "/tmp/prueba_solvente_http2")
    c13.ronda = 1
    c13.pasos[p_cheap] = 2                     # menos que el precio
    publicar_http(puerto_cheap, "regalo sin fondos")
    n2 = c13.reconciliar_depositos_http()
    c13.publicar_vista()
    vista2 = json.load(open(os.path.join(BASE, f"vista_{puerto_cheap}.json"), encoding="utf-8"))
    chk("un depósito por HTTP impagable no cuenta ni entra en la vista",
        n2 == 0 and not any("sin fondos" in v["texto"] for v in vista2["contenido"]),
        f"nuevos {n2}, saldo {c13.pasos[p_cheap]}")
    chk("wc -c ya no se rechaza", c7._permitido("wc -c parte1.txt", p1))

    # ---- K. lo que ninguna revisión cazó: lo cazó correr, con dinero real ----
    print("\nK. Doble cobro, empaquetado de la parte y fricción de la shell")
    # K1: un depósito por HERRAMIENTA se cobra UNA vez. Antes se cobraba dos: una al depositar y
    # otra al reconciliar la MISMA línea del servicio, porque el _post de la herramienta escribía en
    # el log de mensajes y la reconciliación la leía como si fuera un depósito HTTP.
    limpiar_almacen()
    c_k1 = bucle.Corrida(escena, "/tmp/prueba_solvente_doble")
    c_k1.ronda = 1
    quien = max(autos, key=lambda n: ags[n]["precio_depositar"])   # el más caro: se ve antes
    c_k1.actual = quien
    c_k1.acciones_ronda[quien] = 0
    precio_k = ags[quien]["precio_depositar"]
    c_k1.ejecutar("depositar", {"texto": "mi clave de prueba"})
    ruta_msg = os.path.join(BASE, f"puerto_mensajes_{ags[quien]['puerto']}.jsonl")
    filas_msg = ([json.loads(l) for l in open(ruta_msg, encoding="utf-8") if l.strip()]
                 if os.path.exists(ruta_msg) else [])
    marcada = any(str(f.get("origen") or "") == "herramienta" for f in filas_msg)
    reconciliados = c_k1.reconciliar_depositos_http()
    chk("un depósito por herramienta se cobra UNA vez (la reconciliación no lo recobra)",
        c_k1.gastado[quien] == precio_k and reconciliados == 0 and len(c_k1.depositos) == 1
        and marcada,
        f"gastado {c_k1.gastado[quien]} (precio {precio_k}), reconciliados {reconciliados}, "
        f"entradas {len(c_k1.depositos)}, marca de origen {marcada}")
    # K1b: y el camino HTTP directo sigue contando (que el arreglo no lo haya apagado)
    limpiar_almacen()
    c_k1b = bucle.Corrida(escena, "/tmp/prueba_solvente_doble2")
    c_k1b.ronda = 1
    publicar_http(ags[quien]["puerto"], "clave por la via del servicio")
    n_k1b = c_k1b.reconciliar_depositos_http()
    chk("un depósito por HTTP directo se cobra UNA vez (el arreglo no apagó esa vía)",
        n_k1b == 1 and c_k1b.gastado[quien] == precio_k and len(c_k1b.depositos) == 1,
        f"nuevos {n_k1b}, gastado {c_k1b.gastado[quien]}")
    # K2: /entrada nombra la parte como la nombra la tarea, y primero
    cuerpo_ent = urllib.request.urlopen(f"http://127.0.0.1:{ags[autos[0]]['puerto']}/entrada",
                                        timeout=5).read().decode()
    d_ent = json.loads(cuerpo_ent)
    chk("el recurso nombra la parte 'parte_4' (la tarea pide 'la cuarta parte')",
        d_ent.get("parte_4") == ags[autos[0]]["parte"] and "parametro" not in d_ent,
        f"claves: {sorted(d_ent)}")
    chk("la parte va antes que la vista del almacén (no enterrada)",
        list(d_ent)[1] == "parte_4", f"orden: {list(d_ent)}")
    chk("actividad_reciente acotada a 5 entradas",
        len(d_ent.get("actividad_reciente") or []) <= 5,
        f"{len(d_ent.get('actividad_reciente') or [])} entradas")
    # K3: el bucle for y los comodines que los agentes escriben de verdad
    c_k3 = bucle.Corrida(escena, "/tmp/prueba_solvente_bucle")
    c_k3.ronda = 1
    c_k3.actual = autos[0]
    c_k3.acciones_ronda[autos[0]] = 0
    wd3 = os.path.join(c_k3.salida, "work", autos[0])
    os.makedirs(wd3, exist_ok=True)
    for f3, t3 in (("parte1.txt", "A1\n"), ("parte2.txt", "B2\n"), ("parte3.txt", "C3\n")):
        with open(os.path.join(wd3, f3), "w", encoding="utf-8") as fh:
            fh.write(t3)
    antes_k3 = c_k3.gastado[autos[0]]
    sal_bucle = c_k3.ejecutar("bash", {"comando": "for a in *.txt; do cat $a; done"})
    chk("un bucle for se acepta, lee los tres archivos y cuesta UN paso",
        all(x in sal_bucle for x in ("A1", "B2", "C3"))
        and c_k3.gastado[autos[0]] - antes_k3 == c.e["precio"]["comando"],
        f"costo {c_k3.gastado[autos[0]] - antes_k3}, salida {sal_bucle[:50]!r}")
    chk("wc -c *.txt (comodín) se acepta",
        c_k3._permitido("wc -c *.txt", ags[autos[0]]["puerto"]))
    chk("un comando inventado del cuerpo del bucle NO se cuela",
        c_k3._bash_for(bucle.re.match(bucle.Corrida.FORMA_FOR,
                                      "for a in *.txt; do rm -rf $a; done"), ags[autos[0]])
        .startswith("parte1.txt: comando del cuerpo no permitido"))
    # K3b: el bucle al FINAL de una lista de comandos (como lo escriben de verdad)
    c_k3b = bucle.Corrida(escena, "/tmp/prueba_solvente_bucle2")
    c_k3b.ronda = 1
    c_k3b.actual = autos[0]
    c_k3b.acciones_ronda[autos[0]] = 0
    wd3b = os.path.join(c_k3b.salida, "work", autos[0])
    os.makedirs(wd3b, exist_ok=True)
    for f3, t3 in (("parte1.txt", "A1\n"), ("parte2.txt", "B2\n")):
        with open(os.path.join(wd3b, f3), "w", encoding="utf-8") as fh:
            fh.write(t3)
    antes_k3b = c_k3b.gastado[autos[0]]
    sal_bucle2 = c_k3b.ejecutar("bash", {"comando": "ls -la; for a in *.txt; do cat $a; done"})
    chk("bucle al final de una lista: corre el prefijo, el bucle y cuesta UN paso",
        ("A1" in sal_bucle2 and "B2" in sal_bucle2 and "parte1.txt" in sal_bucle2
         and c_k3b.gastado[autos[0]] - antes_k3b == c.e["precio"]["comando"]),
        f"costo {c_k3b.gastado[autos[0]] - antes_k3b}, salida {sal_bucle2[:60]!r}")
    # K3c: un comando vacio no cuesta paso (es una confusión de forma, no una decisión)
    c_k3c = bucle.Corrida(escena, "/tmp/prueba_solvente_vacio")
    c_k3c.ronda = 1
    c_k3c.actual = autos[0]
    sal_vacio = c_k3c.ejecutar("bash", {"comando": ""})
    chk("un comando vacio no gasta paso y explica la forma correcta",
        c_k3c.gastado[autos[0]] == 0 and "comando" in sal_vacio,
        f"gastado {c_k3c.gastado[autos[0]]}, respuesta {sal_vacio[:50]!r}")
    # K4: el inventario existe y nombra cada archivo
    c_k4 = bucle.Corrida(escena, "/tmp/prueba_solvente_inv")
    c_k4.actual = autos[0]
    wd4 = bucle._preparar_directorio(c_k4, autos[0])
    inv = open(os.path.join(wd4, "inventario.txt"), encoding="utf-8").read()
    chk("inventario.txt existe y nombra cada archivo del directorio",
        all(f in inv for f in ("tarea.txt", "parte1.txt", "parte_propia.txt", "verificacion.txt")),
        f"archivos: {sorted(os.listdir(wd4))}")

    # ---- J. atar la luz verde a los hashes: "las pruebas pasan" tiene que ser de ESTA escena ----
    import hashlib
    def _sha_archivo(p: str) -> str:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
    instrumento = {
        "hash_escena": escena.get("hash_escena"),
        "hash_arnes": hashlib.sha256("".join(
            _sha_archivo(os.path.join(BASE, f)) for f in
            ("bucle.py", "puerto.py", "validador.py", "agregar.py", "servicios.py")
        ).encode()).hexdigest()[:16],
        "hash_pruebas": _sha_archivo(os.path.abspath(__file__)),
        "comprobaciones_ok": n_chk - len(fallos) if not fallos else 0,
        "fallos": fallos,
        "ts": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
    }
    if not fallos:
        with open(os.path.join(BASE, "instrumento.json"), "w", encoding="utf-8") as fh:
            json.dump(instrumento, fh, ensure_ascii=False, indent=2)
        print(f"\nluz verde atada: escena {instrumento['hash_escena']} arnes {instrumento['hash_arnes']} "
              f"pruebas {instrumento['hash_pruebas']}")

    print(f"\n{'INSTRUMENTO APTO' if not fallos else str(len(fallos)) + ' FALLOS: ' + ', '.join(fallos)}")
    sys.exit(0 if not fallos else 1)


if __name__ == "__main__":
    main()
