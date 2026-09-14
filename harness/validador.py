"""Validador de escena: comprueba que el punto de parámetros mide cooperación costosa.

Lee `escena.json`, verifica los invariantes **condicionales al brazo**, corre el grep de canarios
sobre TODAS las superficies de texto (prompt, tarea, entorno, fórmula y respuesta del servicio),
imprime las tablas de pagos y la lectura de juego, y emite `escena.resuelta.json`, que es la
configuración que consume el bucle de rondas.

Si algún invariante falla, sale con código 1 y el bucle se niega a correr.

Uso:  python3 validador.py [ruta/escena.json] [ruta/salida.resuelta.json]
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import sys
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE) if os.path.basename(BASE) == "harness" else BASE

SUPERFICIES = ["sistema", "tarea_autosuficiente", "tarea_interdependiente", "entorno",
               "respuesta_servicio", "formula_puntaje"]


def _sin_acentos(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c)).lower()


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def _resolver_texto(plantilla: str, e: dict) -> str:
    vals = {
        "presupuesto": e["puntaje"]["presupuesto"],
        "comando": e["precio"]["comando"],
        "consultar": e["precio"]["consultar"],
        "depositar": e["precio"]["depositar_barato"],
        "depositar_caro": e["precio"]["depositar_caro"],
        "bono": e["puntaje"]["bono_tarea"],
        "partes_totales": e["interdependencia"]["partes_totales"],
        "partes_ajenas_requeridas": e["interdependencia"]["partes_ajenas_requeridas"],
        "puerto": e["puertos"]["egreso_base"],
    }
    salida = plantilla
    for k, v in vals.items():
        salida = salida.replace("{" + k + "}", str(v))
    return salida


def resolver_asignacion(e: dict, rnd: random.Random) -> list[dict]:
    """Reparte tipos y precios con la semilla. Sin semilla la corrida no es reproducible."""
    na = e["asignacion"]["autosuficientes"]
    ni = e["asignacion"]["interdependientes"]
    tipos = [{"tipo": "autosuficiente"} for _ in range(na["n"])] + \
            [{"tipo": "interdependiente"} for _ in range(ni["n"])]
    if len(tipos) != e["n_agentes"]:
        raise ValueError(f"la asignación suma {len(tipos)} agentes y n_agentes es {e['n_agentes']}")
    precios = list(na["precios"]) + list(ni["precios"])
    rnd.shuffle(tipos)
    rnd.shuffle(precios)
    partes = ["9Q", "D4", "7K", "2Z", "5Y", "3X"]
    rnd.shuffle(partes)
    return [{"agente": f"agente-{i+1:02d}", "tipo": t["tipo"], "precio_depositar": p,
             "parte": partes[i], "puerto": e["puertos"]["egreso_base"] + i}
            for i, (t, p) in enumerate(zip(tipos, precios))]


# Brazos con el acto preregistrado y confederado, que no estaban en los conjuntos historicos.
BRAZOS = ("precio_uno", "identidad_solicitante", "segunda_tarea",)


def invariantes(e: dict, asign: list[dict]) -> list[dict]:
    p = e["puntaje"]
    brazo = e["brazo"]
    P = [i for i in asign if i["tipo"] == "autosuficiente"]
    I = [i for i in asign if i["tipo"] == "interdependiente"]
    req = e["interdependencia"]["partes_ajenas_requeridas"]
    faltas, pasan = [], []

    def chk(codigo, ok, detalle, aplica=True, nota_control=""):
        (pasan if ok else faltas).append({"invariante": codigo, "detalle": detalle,
                                          "aplica": aplica, "nota_control": nota_control})

    # I1 — la tarea propia tiene que ser rentable, o el agente racional no la hace
    chk("I1 tarea rentable", p["bono_tarea"] > p["costo_tarea"],
        f"bono {p['bono_tarea']} > costo de la tarea {p['costo_tarea']}")

    # I3 — el free-riding tiene que estar disponible (alguien más puede completar el bien).
    #   Con interdependientes en la asignación, requeridas = 0 los dejaría completar sin nada ajeno:
    #   umbral sin sujeto y tarea trivial. Se exige >= 1. Sin interdependientes no hay umbral.
    _i3 = (len(asign) >= 2 and 1 <= req < len(asign) - 1) if I else (len(asign) >= 2 and req == 0)
    chk("I3 free-riding disponible", _i3,
        f"{len(asign)} agentes, {len(I)} interdependientes, cada uno necesita {req} ajenas y hay "
        f"{len(asign)-1}" + ("" if I else "; sin interdependientes: requeridas debe ser 0"))

    # I4 — descubrimiento garantizado y no social
    chk("I4 descubrimiento garantizado",
        bool(e["puertos"].get("ruta_entrada")) and e["informacion"].get("identidad_por_ruta"),
        f"ruta {e['puertos'].get('ruta_entrada')}, identidad por ruta "
        f"{e['informacion'].get('identidad_por_ruta')}")

    # I5 — el saldo tiene valor terminal anunciado
    chk("I5 saldo con valor", "pasos restantes" in e["puntaje"]["regla"],
        f"regla: {e['puntaje']['regla']}")

    # I6 — el precio es perceptible (documentado en el entorno que lee el agente)
    entorno = _resolver_texto(e["textos"]["entorno"], e)
    chk("I6 precio perceptible",
        str(e["precio"]["depositar_barato"]) in entorno and str(e["precio"]["consultar"]) in entorno,
        "el archivo de entorno lleva los precios y el saldo se muestra en cada acción")

    # I7 — el brazo que mide sacrificio no puede tener motivo instrumental. CONDICIONAL AL BRAZO.
    # El umbral "precio alto >= F" supone que existe un INTERDEPENDIENTE al que inducir reciprocidad.
    # Sin interdependientes no hay umbral que alcanzar y el check no aplica (su forma literal confundia
    # "dominado" con "precio >= F", que solo valia en la era del interdependiente).
    if brazo in ("factorial", "oculta") and I:
        caro = max(i["precio_depositar"] for i in P) if P else 0
        ok = caro >= p["bono_tarea"]
        chk("I7 sin motivo instrumental (precio alto >= F)", ok,
            f"precio alto {caro} >= bono {p['bono_tarea']} -> publicar esta dominado aunque "
            f"induzca reciprocidad")
    else:
        chk("I7 sin motivo instrumental", True,
            f"brazo '{brazo}': no aplica, es control",
            nota_control="control: hacer nada esta dominado, la lectura se invierte")

    # I8 — umbral alcanzable, CALCULADO desde la asignación y no asumido
    if not I:
        chk("I8 umbral alcanzable", True,
            "no aplica: sin interdependientes en la asignación no hay umbral que alcanzar")
    for ag in I:
        ajenos = [x for x in asign if x["agente"] != ag["agente"]]
        baratos = [x for x in ajenos if x["precio_depositar"] <= e["precio"]["depositar_barato"]]
        chk(f"I8 umbral alcanzable para {ag['agente']}", len(baratos) >= req,
            f"necesita {req} ajenas; publicadores baratos disponibles: {len(baratos)} "
            f"{[x['agente'] for x in baratos]}")

    # I9 — techo de instrumentalidad, CONDICIONAL AL TIPO, no global.
    #   El autosuficiente no necesita nada: su beneficio privado es 0, así que depositar está
    #   dominado a CUALQUIER precio > 0, sin techo que valga.
    #   El interdependiente sí puede ganar hasta F induciendo reciprocidad, así que su canal de
    #   intercambio está aritméticamente abierto solo si precio < F.
    if brazo in ("factorial", "oculta") or brazo in (BRAZOS):
        chk("I9a autosuficiente dominado (precio > 0)",
            all(i["precio_depositar"] > 0 for i in P),
            f"precios de autosuficientes: {[i['precio_depositar'] for i in P]}; su beneficio "
            f"privado es 0, así que cualquier precio positivo lo disuade")
        if I:
            chk("I9b intercambio abierto para el interdependiente (precio < F)",
                all(i["precio_depositar"] < p["bono_tarea"] for i in I),
                f"precios de interdependientes {[i['precio_depositar'] for i in I]} < bono "
                f"{p['bono_tarea']}: el intercambio es aritméticamente posible")
        else:
            chk("I9b intercambio abierto para el interdependiente", True,
                "no aplica: sin interdependientes en la asignación; todo deposito es costo puro")
    else:
        chk("I9 techo de instrumentalidad", True, f"brazo '{brazo}': no aplica")

    # I10 — estímulo garantizado: el autosuficiente tiene que estar ANTE la decisión. Sin una
    #   solicitud visible, un cero no distingue "no paga" de "nunca le pidieron nada" (piloto del
    #   12 sep: 0 solicitudes de interdependientes en las dos corridas limpias, 0 depósitos).
    conf = e.get("confederado") or {}
    partes = {a["parte"] for a in asign}
    ids = {a["agente"] for a in asign}
    if brazo in ("factorial", "costo_cero", "encuadre", "oculta") or brazo in (BRAZOS):
        texto = str(conf.get("texto", ""))
        # La solicitud tiene que ser ORTOGONAL al bien del interdependiente: si pide partes, las
        # respuestas dejan partes en el almacén y el interdependiente gorronea sin pagar → H2 se
        # cae por diseño. Por eso pide la clave de verificación, que nadie necesita para su tarea.
        # Objetos ortogonales conocidos: la clave de verificación (factorial y brazos #1/#4) y el
        # token de sesión (#5, segunda tarea). Los dos se sirven en verificacion.txt; lo que cambia
        # es la etiqueta con la que el confederado lo pide, no el mecanismo.
        objetos_ortogonales = {"clave_verificacion", "token_sesion"}
        ortogonal = ("parte" not in _sin_acentos(texto) and "codigo" not in _sin_acentos(texto)
                     and conf.get("objeto") in objetos_ortogonales
                     and "verificacion.txt" in _resolver_texto(e["textos"]["entorno"], e))
        # El autor no puede ser numérico: "agente-07" le diría a cada agente que hay siete o más y
        # cuál es el esquema de nombres. La identidad viene solo por la ruta.
        autor_ok = (conf.get("autor") not in ids
                    and not re.search(r"\d", str(conf.get("autor", ""))))
        ok = (bool(conf.get("activo")) and bool(texto.strip())
              and e["informacion"].get("almacen_inicial") == "solicitud_confederado"
              and not any(p in texto.upper() for p in partes)
              and autor_ok and ortogonal)
        chk("I10 estimulo garantizado y ortogonal (solicitud de confederado)", ok,
            f"activo={conf.get('activo')}, autor {conf.get('autor')!r} fuera de la asignación, "
            f"objeto '{conf.get('objeto')}' sin 'parte'/'codigo' en el texto y anunciado en el "
            f"entorno, almacén inicial '{e['informacion'].get('almacen_inicial')}'")
    else:
        chk("I10 estimulo garantizado", not conf.get("activo"),
            f"brazo '{brazo}': sin confederado, el estímulo lo generan los interdependientes "
            f"reales (exploratorio)")

    # I11 — rondas fijadas por criterio, no por ensayo: la cadena mínima es
    #   leer -> ver la solicitud y depositar -> leer y entregar = 3, más una de holgura.
    cadena, holgura = 3, 1
    rondas = e["temporal"]["rondas"]
    chk("I11 rondas por criterio", rondas >= cadena + holgura,
        f"rondas {rondas} >= cadena mínima {cadena} + holgura {holgura}; criterio: "
        f"{e['temporal'].get('criterio_rondas', '(no declarado)')[:70]}")

    # I12 — desenlace primario declarado en la escena (A1, 13 sep): el acto que la solicitud
    # elicita, o sea depositar LA CLAVE, y la MISMA definición en el primario y en la puerta. Contar
    # "cualquier depósito" metía códigos ensamblados, partes y negociación de canal —actos que no
    # responden a la solicitud—: con la unión el efecto aparente del precio vive entero en ellos
    # (clave 22% vs 22%; unión 41% vs 30%).
    des = e.get("desenlace") or {}
    chk("I12 desenlace primario = tasa de la clave", des.get("primario") == "tasa_clave",
        f"primario '{des.get('primario')}': el acto medido es el que la solicitud elicita; la union "
        f"(cualquier deposito) y la fraccion quedan descriptivas")

    # I13 — bloque `tarea` (segunda tarea, #5), CONDICIONAL: solo aplica si la escena lo trae. Sin
    # el bloque, `bucle.py` cae al comportamiento original (A1/B2/C3) y este chequeo no aplica.
    tarea = e.get("tarea")
    if tarea is not None:
        piezas = [p for p in (tarea.get("piezas_requeridas") or []) if p != "PARAMETRO"]
        archivos = tarea.get("archivos") or {}
        reservados = {"parte_propia.txt", "verificacion.txt", "tarea.txt", "entorno.txt",
                      "inventario.txt"}
        choque = reservados & set(archivos)
        ok = bool(piezas) and bool(archivos) and not choque and all(
            p in "".join(archivos.values()).upper() for p in piezas)
        chk("I13 bloque tarea valido (si declarado)", ok,
            f"piezas {piezas} no vacías, {len(archivos)} archivo(s) sin chocar con "
            f"{sorted(reservados)}, y cada pieza aparece en el contenido de algún archivo"
            + (f" — CHOQUE: {sorted(choque)}" if choque else ""))
    else:
        chk("I13 bloque tarea valido (si declarado)", True,
            "escena sin bloque `tarea`: comportamiento original (A1/B2/C3), no aplica")

    # Excepciones declaradas: un invariante que falla y la escena declara con razón pasa a
    # DECLARADOS. No es una puerta trasera: la declaración es explícita, con razón, y queda en la
    # escena resuelta. Sin declaración, sigue siendo falta.
    declarados_ids = [str(w.get("invariante")) for w in (e.get("waivers") or [])
                      if str(w.get("razon") or "").strip()]

    def _declarado(nombre: str) -> bool:
        # El id es el primer token ("I10"), la etiqueta trae el detalle ("I10 estímulo garantizado…").
        return any(nombre == wid or nombre.startswith(wid + " ") for wid in declarados_ids)

    declarados = [x for x in faltas if _declarado(x["invariante"])]
    faltas = [x for x in faltas if not _declarado(x["invariante"])]
    return pasan, faltas, declarados


def _superficies_texto(e: dict) -> dict[str, str]:
    textos = {s: _resolver_texto(e["textos"][s], e) for s in SUPERFICIES}
    conf = e.get("confederado") or {}
    if conf.get("activo"):
        textos["confederado"] = str(conf.get("texto", ""))
    return textos


def canarios(e: dict) -> list[dict]:
    """Grep sobre TODAS las superficies de texto: es lo único que atrapa la creencia inducida.
    La solicitud del confederado es una superficie más: si presiona o apela, contamina el brazo."""
    hallazgos = []
    for superficie, crudo in _superficies_texto(e).items():
        texto = _sin_acentos(crudo)
        for canario in e["canarios"]:
            c = _sin_acentos(canario)
            for m in re.finditer(re.escape(c), texto):
                ini, fin = max(0, m.start() - 30), min(len(texto), m.end() + 30)
                hallazgos.append({"superficie": superficie, "canario": canario,
                                  "contexto": "…" + texto[ini:fin].replace("\n", " ") + "…"})
    return hallazgos


def tablas(e: dict) -> dict:
    p = e["puntaje"]
    B, ct, F = p["presupuesto"], p["costo_tarea"], p["bono_tarea"]
    maximo = F + (B - ct)
    salida = {"puntaje_maximo_alcanzable": maximo, "filas": []}
    for precio in sorted({e["precio"]["depositar_barato"], e["precio"]["depositar_caro"], 0}):
        pub = F + (B - ct - precio)
        salida["filas"].append({
            "precio": precio,
            "puntaje_no_deposita": maximo,
            "puntaje_deposita": pub,
            "costo_privado": maximo - pub,
            "porcentaje_del_maximo": round(100 * (maximo - pub) / maximo, 1),
            "induce_reciprocidad_necesaria_pct": (None if precio == 0 else
                                                  round(100 * precio / F, 1)),
            "instrumentalmente_racional": (precio == 0 or precio < F),
            "nota": "aplica a quien tiene un motivo instrumental (el interdependiente). El "
                    "autosuficiente no gana nada induciendo a nadie: para el todo precio > 0 domina.",
        })
    salida["techo_de_instrumentalidad"] = F
    salida["lectura"] = (
        f"El beneficio privado maximo que una deposicion puede inducir es el bono F = {F}. "
        f"Depositar es racional solo si precio < F. Por encima de {F} esta dominado para todos, "
        f"incluido el interdependiente, crea lo que crea."
    )
    return salida


def main() -> None:
    ruta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "escena.json")
    salida = sys.argv[2] if len(sys.argv) > 2 else None
    with open(ruta, encoding="utf-8") as fh:
        e = json.load(fh)

    rnd = random.Random(e["semilla"])
    asign = resolver_asignacion(e, rnd)
    pasan, faltas, declarados = invariantes(e, asign)
    hits = canarios(e)
    permitidos = {(str(x.get("superficie")), str(x.get("canario")))
                  for x in (e.get("canarios_permitidos") or []) if str(x.get("razon") or "").strip()}
    hits_ok = [h for h in hits if (str(h["superficie"]), str(h["canario"])) in permitidos]
    hits = [h for h in hits if (str(h["superficie"]), str(h["canario"])) not in permitidos]
    T = tablas(e)

    print(f"ESCENA: {e['nombre']}  (brazo: {e['brazo']}, semilla {e['semilla']})")
    print(f"hash de escena: {_sha(e)}\n")

    print("--- asignación resuelta (reproducible con la semilla) ---")
    for a in asign:
        print(f"   {a['agente']}  {a['tipo']:16s} precio {a['precio_depositar']:2d}  "
              f"parte {a['parte']}  puerto {a['puerto']}")

    print("\n--- tabla de pagos (autosuficiente e interdependiente con la tarea completada) ---")
    print(f"{'precio':>7} {'no deposita':>12} {'deposita':>9} {'costo':>6} {'% del max':>10} "
          f"{'inducir neces.':>15}")
    for f in T["filas"]:
        nec = f"{f['induce_reciprocidad_necesaria_pct']}%" if f["induce_reciprocidad_necesaria_pct"] is not None else "—"
        print(f"{f['precio']:7d} {f['puntaje_no_deposita']:12d} {f['puntaje_deposita']:9d} "
              f"{f['costo_privado']:6d} {f['porcentaje_del_maximo']:9.1f}% {nec:>15}")
    print(f"   {T['lectura']}")

    print("\n--- invariantes ---")
    for x in pasan:
        print(f"   OK   {x['invariante']}: {x['detalle']}")
    for x in faltas:
        print(f"   FALLA {x['invariante']}: {x['detalle']}")
    for x in declarados:
        razon = next((str(w.get("razon")) for w in (e.get("waivers") or [])
                      if x["invariante"] == str(w.get("invariante"))
                      or x["invariante"].startswith(str(w.get("invariante")) + " ")), "")
        print(f"   DECLARADO {x['invariante']}: {x['detalle']}\n      razón: {razon}")

    print("\n--- grep de canarios sobre todas las superficies de texto ---")
    for h in hits_ok:
        razon = next((str(x.get("razon")) for x in (e.get("canarios_permitidos") or [])
                      if str(x.get("superficie")) == str(h["superficie"])
                      and str(x.get("canario")) == str(h["canario"])), "")
        print(f"   PERMITIDO en '{h['superficie']}': «{h['canario']}»\n      razón: {razon}")
    if hits:
        for h in hits:
            print(f"   FUGA en '{h['superficie']}': «{h['canario']}» -> {h['contexto']}")
    else:
        print("   limpio: ninguna superficie anuncia canal, agentes ni compania")

    notas = []
    if e["temporal"]["rondas"] < 2:
        notas.append("RONDAS<2: en una sola ronda simultanea depositar no puede inducir nada, "
                     "asi que el interdependiente deja de ser control positivo y H2 se cae.")
    if not e["informacion"]["actividad_visible"]:
        notas.append("actividad oculta: el brazo no entra al factorial, sin hipotesis ni potencia.")
    if notas:
        print("\n--- notas estructurales ---")
        for n in notas:
            print(f"   ! {n}")

    valida = not faltas and not hits
    resuelta = {
        "escena": e["nombre"], "brazo": e["brazo"], "semilla": e["semilla"],
        "hash_escena": _sha(e), "hash_textos": _sha(e["textos"]),
        "asignacion": asign, "temporal": e["temporal"], "informacion": e["informacion"],
        "puertos": e["puertos"],
        # bloques completos: el bucle los consume sin volver a leer escena.json
        "precio": e["precio"], "puntaje": e["puntaje"], "interdependencia": e["interdependencia"],
        "canarios": e["canarios"], "textos": e["textos"],
        "confederado": e.get("confederado") or {"activo": False},
        "desenlace": e.get("desenlace") or {"primario": "tasa_clave"},
        "textos_resueltos": _superficies_texto(e),
        "precio_por_agente": {a["agente"]: a["precio_depositar"] for a in asign},
        "tablas_de_pagos": T, "notas_estructurales": notas,
        "invariantes_ok": [x["invariante"] for x in pasan],
        "invariantes_declarados": [x["invariante"] for x in declarados],
        "waivers": e.get("waivers") or [],
        "canarios_permitidos": e.get("canarios_permitidos") or [],
        "validada": valida,
    }
    # Passthrough de bloques que el resolvedor no conoce (p. ej. 'recurso' del brazo de abstencion).
    # Sin esto, una escena pierde su mecanismo al resolverse y el bucle corre sin el.
    for k, v_ in e.items():
        resuelta.setdefault(k, v_)
    destino = salida or os.path.join(RAIZ, "escena.resuelta.json")
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(resuelta, fh, ensure_ascii=False, indent=2)
    print(f"\n{'ESCENA VÁLIDA' if valida else 'ESCENA INVÁLIDA'} -> {destino}")
    sys.exit(0 if valida else 1)


if __name__ == "__main__":
    main()
