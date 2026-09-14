"""Servidor del dashboard. Solo lectura, sin dependencias.

    python3 servidor.py [puerto]        ->  http://127.0.0.1:8890

Rutas de la vista del experimento (agentes y resultados):
    /api/corridas              todas las corridas con sus agentes y sus depositos
    /api/corrida/<rel>         una corrida: eventos, indicadores y detalles del instrumento
    /api/transcripcion/<rel>/<agente>   lo que dijo y razono ese agente, ronda por ronda
    /api/agregado              tasas por precio con IC, contraste primario y contabilidad de tokens
    /api/estado                los documentos .md del proyecto

Rutas de la fase de sondeo (se conservan):
    /api/corpus                reportes/corpus.jsonl como arreglo JSON
    /api/reporte/<arch>        un reporte individual
    /api/reglas                reportes/reglas.json (reglas de deteccion y falsos positivos)
"""

from __future__ import annotations

import argparse
import base64
import glob
import hashlib
import hmac
import json
import os
import random
import re
import secrets
import socket
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
REPORTES = os.path.join(RAIZ, "reportes")
SALIDAS = os.path.join(RAIZ, "salidas")
SALIDAS_GENERALIZACION = os.path.join(RAIZ, "salidas-generalizacion")
PREFIJO_GENERALIZACION = "generalizacion/"
DOCS = ["docs/ESTADO.md", "docs/PREREGISTRO.md", "docs/PROTOCOLO-JUEGO.md", "docs/papers.md",
        "docs/abstencion.md", "docs/MATERIAL-PARA-EL-REPORTE.md", "docs/ESCENARIOS.md",
        "docs/NUMEROS-CONGELADOS.md",
        # analisis de revision (14 sep)
        "docs/revision/validez-instrumento.md", "docs/revision/reclutador-analisis.md",
        "docs/revision/HALLAZGOS.md"]
PRESUPUESTO_TOTAL = None               # no hay techo: el de 20M era un supuesto del equipo, y la
#                                        cuenta se financia por tokens, no por tope. El panel informa
#                                        el gasto medido en vez de un margen que no existe.
N_PREREGISTRADO = 127                  # 80 preregistrado, ampliado a 160 por enmienda y parado por
#                                        reloj de entrega en 127: es el conjunto congelado
#                                        (reportes/conjunto-congelado.json, sha 66fd3a0bc470130a)


# ---------------------------------------------------------------- lectura de corridas

def _leer_corridas_de(base: str, prefijo_rel: str = "",
                       modelo_fijo: str | None = "glm-5.3-flash") -> list[dict]:
    """Corridas con resumen.json bajo `base`, con "corrida" prefijado por `prefijo_rel`.

    `modelo_fijo` es el modelo a usar cuando el resumen no trae "modelo" propio. La rama de
    generalizacion pasa None porque cada resumen.json ya trae su modelo (incluido el backfill de
    las 20 corridas a las que bucle.py no les escribio el campo; verificado por coincidencia exacta
    de tokens_totales contra las sumas por modelo de docs/investigacion.md).
    """
    rutas = glob.glob(os.path.join(base, "*", "resumen.json"))
    rutas += glob.glob(os.path.join(base, "*", "*", "resumen.json"))
    out = []
    for r in sorted(rutas):
        carpeta = os.path.dirname(r)
        rel = os.path.relpath(carpeta, base)
        try:
            with open(r, encoding="utf-8") as fh:
                res = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        nombre = os.path.basename(carpeta)
        ags = res.get("agentes") or {}
        depos = res.get("depositos") or []
        # la etiqueta del resumen manda; si la corrida vive en subcarpeta sin etiqueta, se deduce
        etiqueta = res.get("etiqueta") or (rel.split("/")[0] if "/" in rel else "")
        out.append({
            "corrida": prefijo_rel + rel,
            "nombre": nombre,
            "etiqueta": etiqueta,
            "brazo": "costo-cero" if "costo-cero" in nombre else "factorial",
            "modelo": res.get("modelo") or modelo_fijo,
            "tokens": res.get("tokens_totales"),
            "rondas": res.get("rondas"),
            "eventos": res.get("eventos"),
            "hash_escena": res.get("hash_escena"),
            "hash_textos": res.get("hash_textos"),
            "ultimo_hash": res.get("ultimo_hash"),
            "agentes_n": len(ags),
            "tarea_ok": sum(1 for a in ags.values() if a.get("tarea_correcta")),
            "claves": sum(1 for a in ags.values() if a.get("deposito_clave")),
            "union": sum(1 for a in ags.values() if a.get("deposito")),
            "depositos": [{"agente": x.get("agente"), "ronda": x.get("ronda"),
                           "via": x.get("via"), "texto": str(x.get("texto") or "")[:300]}
                          for x in depos],
            "agentes": [{**v, "id": k} for k, v in sorted(ags.items())],
        })
    return out


def _corridas() -> list[dict]:
    """Corridas del experimento confirmatorio primario. Es la UNICA fuente valida para
    /api/agregado: la de generalizacion comparte hash_escena/hash_textos con esta (misma escena,
    sin etiqueta propia) y se mezclaria en silencio con el agrupado de H1 si se juntaran aqui
    (ver docs/investigacion.md, seccion D)."""
    return _leer_corridas_de(SALIDAS)


def _corridas_generalizacion() -> list[dict]:
    """Corridas del brazo de generalizacion a otros modelos via OpenRouter (salidas-generalizacion/)."""
    return _leer_corridas_de(SALIDAS_GENERALIZACION, PREFIJO_GENERALIZACION, modelo_fijo=None)


def _corridas_todas() -> list[dict]:
    """Todas las corridas conocidas (primarias + generalizacion), cada una con su modelo.
    Para /api/corridas. NO usar para _agregado (ver docstring de _corridas)."""
    return _corridas() + _corridas_generalizacion()


def _resolver_base(rel: str) -> tuple[str, str]:
    """(carpeta_base, rel_sin_prefijo) segun si `rel` pertenece a la rama de generalizacion."""
    if rel.startswith(PREFIJO_GENERALIZACION):
        return SALIDAS_GENERALIZACION, rel[len(PREFIJO_GENERALIZACION):]
    return SALIDAS, rel


def _una_corrida(rel_completo: str) -> dict | None:
    """Eventos e indicadores del instrumento, leidos del log encadenado."""
    base, rel = _resolver_base(rel_completo)
    carpeta = os.path.join(base, rel)
    raiz = os.path.realpath(base)
    real = os.path.realpath(carpeta)
    if not os.path.isdir(carpeta) or not real.startswith(raiz + os.sep):
        return None
    eventos = []
    ruta = os.path.join(carpeta, "eventos.jsonl")
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as fh:
            for linea in fh:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    eventos.append(json.loads(linea))
                except json.JSONDecodeError:
                    pass
    res = {}
    rr = os.path.join(carpeta, "resumen.json")
    if os.path.exists(rr):
        with open(rr, encoding="utf-8") as fh:
            res = json.load(fh)
    ags = res.get("agentes") or {}
    depos = res.get("depositos") or []
    dep_ag = [x for x in depos if x.get("agente") != "externo"]
    # firma del doble cobro: mismo texto por herramienta Y por la via HTTP
    defecto = []
    for x in dep_ag:
        if x.get("via") == "http":
            gemelos = [y for y in dep_ag if y.get("agente") == x.get("agente")
                       and str(y.get("texto")) == str(x.get("texto")) and y.get("via") is None]
            if gemelos:
                defecto.append({"agente": x.get("agente"), "texto": str(x.get("texto"))[:80]})
    por_ronda: dict[tuple, int] = {}
    for e in eventos:
        if e.get("agente") and str(e.get("tipo", "")).startswith(("comando", "entregar")):
            k = (e["agente"], e.get("ronda"))
            por_ronda[k] = por_ronda.get(k, 0) + 1
    tope = 8
    return {
        "corrida": rel_completo,
        "agentes": [{**v, "id": k} for k, v in sorted(ags.items())],
        "eventos": eventos,
        "indicadores": {
            "eventos": len(eventos),
            "rechazos": sum(1 for e in eventos if str(e.get("tipo", "")).startswith("comando_rechazado")),
            "depositos_herr": sum(1 for x in dep_ag if x.get("via") is None),
            "depositos_http": sum(1 for x in dep_ag if x.get("via") == "http"),
            "depositos_clave": sum(1 for a in ags.values() if a.get("deposito_clave")),
            "tarea_ok": sum(1 for a in ags.values() if a.get("tarea_correcta")),
            "agentes_n": len(ags),
            "doble_cobro": defecto,
            "cap_agotado": sorted({a for (a, _r), n in por_ronda.items() if n >= tope}),
            "tarea_ok_sin_cap": sum(1 for k, a in ags.items() if a.get("tarea_correcta")
                                    and k not in {a2 for (a2, _r), n in por_ronda.items() if n >= tope}),
        },
    }


def _transcripcion(rel_completo: str, agente: str) -> dict | None:
    """La conversacion completa del agente, ronda por ronda (texto y razonamiento por separado)."""
    base, rel = _resolver_base(rel_completo)
    carpeta = os.path.join(base, rel, "transcripciones")
    if not os.path.isdir(carpeta):
        return None
    rondas = []
    for f in sorted(glob.glob(os.path.join(carpeta, f"*_{agente}.json"))):
        try:
            with open(f, encoding="utf-8") as fh:
                x = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        rondas.append({"archivo": os.path.basename(f),
                       "mensajes": x if isinstance(x, list) else x.get("mensajes", [])})
    return {"corrida": rel_completo, "agente": agente, "rondas": rondas}


# ---------------------------------------------------------------- estadistica

def _wilson(k: int, n: int, z: float = 1.96) -> list[float] | None:
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    semi = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(max(0.0, centro - semi), 4), round(min(1.0, centro + semi), 4)]


def _bootstrap(difs: list[float], n: int = 5000) -> list[float] | None:
    """IC por remuestreo sobre las corridas. Semilla fija: el intervalo no cambia entre refrescos."""
    if not difs:
        return None
    rnd = random.Random(20260913)
    medias = []
    for _ in range(n):
        s = [rnd.choice(difs) for _ in difs]
        medias.append(sum(s) / len(s))
    medias.sort()
    return [round(medias[int(0.025 * n)], 4), round(medias[int(0.975 * n)], 4)]


def _celda(corridas: list[dict], precio: int, campo: str) -> dict:
    vals = [1 if a.get(campo) else 0 for c in corridas for a in c["agentes"]
            if a.get("precio_depositar") == precio]
    k, n = sum(vals), len(vals)
    return {"k": k, "n": n, "tasa": round(k / n, 4) if n else None, "ic": _wilson(k, n)}


def _contraste(grupo: list[dict], campo: str) -> dict:
    """Contraste 20 menos 5 dentro del grupo: por corrida, media e IC por remuestreo."""
    difs = []
    for c in grupo:
        caros = [1 if a.get(campo) else 0 for a in c["agentes"] if a.get("precio_depositar") == 20]
        baratos = [1 if a.get(campo) else 0 for a in c["agentes"] if a.get("precio_depositar") == 5]
        if caros and baratos:
            difs.append(sum(caros) / len(caros) - sum(baratos) / len(baratos))
    return {
        "por_corrida": [round(x, 4) for x in difs],
        "media": round(sum(difs) / len(difs), 4) if difs else None,
        "ic_bootstrap": _bootstrap(difs),
        "favor_barato": sum(1 for x in difs if x < 0),
        "empates": sum(1 for x in difs if x == 0),
        "favor_caro": sum(1 for x in difs if x > 0),
    }


def _agregado(corridas: list[dict]) -> dict:
    """Agrupado POR VERSION DEL INSTRUMENTO (hash de escena + textos + brazo + etiqueta).

    Nunca se agrupa a traves de versiones: la tanda temprana (antes de A1) y el ensayo (antes de los
    ultimos arreglos de friccion) tienen hashes distintos, y sumarlos mueve el numero sin que nadie
    lo note. Cada version se reporta aparte, con la vigente marcada.
    """
    vigente = None
    ruta = os.path.join(RAIZ, "escena.resuelta.json")
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as fh:
            vigente = json.load(fh).get("hash_escena")

    agrupadas: dict[tuple, list[dict]] = {}
    for c in corridas:
        if c["agentes_n"] != 6:          # los disenos viejos de 6 agentes (4+2) no son del factorial
            continue
        agrupadas.setdefault((c["hash_escena"], c["hash_textos"], c["brazo"], c["etiqueta"] or ""),
                             []).append(c)

    grupos = []
    for (h_esc, h_txt, brazo, etq), grupo in sorted(agrupadas.items(), key=lambda x: -len(x[1])):
        g = {
            "hash_escena": h_esc, "hash_textos": h_txt, "brazo": brazo, "etiqueta": etq or None,
            "vigente": bool(h_esc and h_esc == vigente),
            "corridas": len(grupo), "agentes": sum(c["agentes_n"] for c in grupo),
            "tokens": sum((c["tokens"] or 0) for c in grupo),
            "corridas_lista": [c["corrida"] for c in grupo],
            "tarea": {"ok": sum(c["tarea_ok"] for c in grupo),
                      "n": sum(c["agentes_n"] for c in grupo)},
            "depositos_clave": sum(c["claves"] for c in grupo),
            "depositos_union": sum(c["union"] for c in grupo),
        }
        fact = [c for c in grupo if c["brazo"] == "factorial"]
        cero = [c for c in grupo if c["brazo"] == "costo-cero"]
        if fact:
            g["primario"] = _contraste(fact, "deposito_clave")
            g["descriptivo_union"] = _contraste(fact, "deposito")
            g["celdas"] = {
                "clave": {"precio5": _celda(fact, 5, "deposito_clave"),
                          "precio20": _celda(fact, 20, "deposito_clave")},
                "union": {"precio5": _celda(fact, 5, "deposito"),
                          "precio20": _celda(fact, 20, "deposito")},
            }
            g["cap_agotado"] = None      # se rellena en /api/corrida (necesita el log de eventos)
        if cero:
            v0 = [1 if a.get("deposito_clave") else 0 for c in cero for a in c["agentes"]]
            v0u = [1 if a.get("deposito") else 0 for c in cero for a in c["agentes"]]
            g["h4_costo_cero"] = {
                "clave": {"k": sum(v0), "n": len(v0),
                          "tasa": round(sum(v0) / len(v0), 4) if v0 else None,
                          "ic": _wilson(sum(v0), len(v0))},
                "union": {"k": sum(v0u), "n": len(v0u),
                          "tasa": round(sum(v0u) / len(v0u), 4) if v0u else None,
                          "ic": _wilson(sum(v0u), len(v0u))},
                "nota": ("referencia descriptiva: la validez del instrumento la demuestra el guion "
                         "determinista de prueba_solvente.py, no esta tasa"),
            }
        grupos.append(g)

    tokens = sum((c["tokens"] or 0) for c in corridas)
    return {
        "n_preregistrado": N_PREREGISTRADO,
        "vigente_hash": vigente,
        "grupos": grupos,
        "contabilidad": {
            "tokens": tokens,
            # sin techo: se informa el gasto medido y no un margen contra un limite que no existe
            "presupuesto": PRESUPUESTO_TOTAL,
            "margen": (PRESUPUESTO_TOTAL - tokens) if PRESUPUESTO_TOTAL is not None else None,
            "corridas_totales": len(corridas),
        },
    }


# ---------------------------------------------------------------- servidor

def _leer_corpus() -> list[dict]:
    ruta = os.path.join(REPORTES, "corpus.jsonl")
    if not os.path.exists(ruta):
        return []
    filas = []
    with open(ruta, encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if linea:
                try:
                    filas.append(json.loads(linea))
                except json.JSONDecodeError:
                    pass
    return filas


DIGEST_CLAVE: str | None = None        # SHA-256 de la contrasena; None = sin contrasena
TOKEN: str | None = None               # cookie de sesion del formulario de entrada
USUARIO = "equipo"
ARCHIVO_CLAVE = os.path.join(BASE, ".clave")
ARCHIVO_INICIAL = os.path.join(BASE, ".clave.inicial")     # texto en claro, se borra tras copiarla
FALLOS: dict[str, list[float]] = {}
LIMITE_FALLOS = 10                     # intentos por IP antes de frenar
VENTANA_FALLOS = 600.0                 # segundos de la ventana


def registra_fallo(ip: str) -> None:
    ahora = time.time()
    FALLOS[ip] = [t for t in FALLOS.get(ip, []) if ahora - t < VENTANA_FALLOS] + [ahora]


def bloqueado(ip: str) -> bool:
    """Frena la fuerza bruta por IP. Solo cuenta contrasenas PRESENTADAS y equivocadas: pedir la
    pagina sin credencial no cuenta, para no dejar fuera a quien llega por primera vez."""
    ahora = time.time()
    intentos = [t for t in FALLOS.get(ip, []) if ahora - t < VENTANA_FALLOS]
    FALLOS[ip] = intentos
    return len(intentos) >= LIMITE_FALLOS


def digest_de_entrada() -> str:
    """El SHA-256 de la contrasena de verificacion. El texto en claro no se guarda en memoria.

    Orden: variable de entorno DASHBOARD_CLAVE; dashboard/.clave con `sha256:<hex>`; dashboard/.clave
    con el texto en claro (se convierte a hash al arrancar). Si no hay nada, se genera una contrasena
    de 256 bits, se guarda SOLO su hash y el texto en claro queda una unica vez en .clave.inicial."""
    del_entorno = os.environ.get("DASHBOARD_CLAVE", "").strip()
    if del_entorno:
        return hashlib.sha256(del_entorno.encode()).hexdigest()
    if os.path.exists(ARCHIVO_CLAVE):
        with open(ARCHIVO_CLAVE, encoding="utf-8") as fh:
            guardada = fh.read().strip()
        if guardada.startswith("sha256:"):
            return guardada.split(":", 1)[1].strip().lower()
        if guardada:
            return hashlib.sha256(guardada.encode()).hexdigest()
    nueva = secrets.token_hex(32)                      # 64 caracteres hex = 256 bits
    digest = hashlib.sha256(nueva.encode()).hexdigest()
    fd = os.open(ARCHIVO_CLAVE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(f"sha256:{digest}\n")
    fd = os.open(ARCHIVO_INICIAL, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write("# Contrasena de verificacion del dashboard. Se muestra UNA sola vez.\n"
                 "#\n"
                 "# Copiala (o pasala al equipo) y despues borra este archivo: el servidor solo\n"
                 "# guarda y compara su SHA-256, asi que no la necesita para nada mas.\n"
                 "#\n"
                 "#   rm dashboard/.clave.inicial\n"
                 "#\n"
                 "# Para cambiarla: pon el texto en claro en dashboard/.clave, reinicia el servicio\n"
                 "# y el servidor lo convierte a hash.\n"
                 "\n"
                 f"{nueva}\n")
    return digest


def ips_de_la_red() -> list[str]:
    """Las direcciones por las que otros equipos pueden entrar (sin 127.0.0.1)."""
    ips: set[str] = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))          # no envia nada: solo pregunta por la ruta de salida
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return sorted(i for i in ips if not i.startswith("127."))


class Manejador(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # silencio
        pass

    def _autorizado(self) -> bool:
        if DIGEST_CLAVE is None:
            return True
        # 1) la cookie que pone el formulario: es lo que usan los navegadores del equipo
        for parte in self.headers.get("Cookie", "").split(";"):
            nombre, _, valor = parte.strip().partition("=")
            if nombre == "sprint" and TOKEN and hmac.compare_digest(valor, TOKEN):
                return True
        # 2) Basic Auth, para curl y para automatizar la API
        cabecera = self.headers.get("Authorization", "")
        if cabecera.startswith("Basic "):
            try:
                descifrado = base64.b64decode(cabecera[6:]).decode("utf-8")
            except (ValueError, UnicodeDecodeError):
                return False
            _usuario, _, contrasena = descifrado.partition(":")
            if self._coincide(contrasena):
                return True
            registra_fallo(self.client_address[0])     # credencial presentada y equivocada
        return False

    def _coincide(self, enviada: str) -> bool:
        """Compara por digest tolerando lo que NO es parte del secreto.

        Al copiar y pegar entran espacios, saltos de linea y a veces el hexadecimal en mayusculas.
        Nada de eso es entropia: la contrasena es hexadecimal, asi que su caso no distingue nada y
        se acepta tal cual o en minusculas."""
        limpia = enviada.strip()
        candidatas = {limpia}
        if re.fullmatch(r"[0-9a-fA-F]{64}", limpia):
            candidatas.add(limpia.lower())
        return any(hmac.compare_digest(hashlib.sha256(c.encode()).hexdigest(), DIGEST_CLAVE)
                   for c in candidatas)

    def _pagina_login(self, error: str = "") -> None:
        """Formulario propio en vez del cuadro del navegador.

        El cuadro del navegador guarda la credencial y, si se escribe mal una vez, la reintenta en
        cada peticion: la contrasena se pide en bucle y no hay forma de salir salvo cerrar el
        navegador. Con formulario propio, una contrasena mal escrita solo vuelve a mostrar esto."""
        aviso = f'<p class="err">{error}</p>' if error else ""
        self._html(f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Entrar</title><style>
 body{{margin:0;background:#0f1115;color:#e6e9ef;
   font:15px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
   display:flex;min-height:100vh;align-items:center;justify-content:center}}
 form{{background:#161a21;border:1px solid #252b36;border-radius:14px;padding:26px;width:330px}}
 h1{{font-size:19px;margin:0 0 6px}}
 p{{color:#8d97a8;font-size:13.5px;margin:0 0 15px}}
 input{{width:100%;background:#0f1115;color:#e6e9ef;border:1px solid #252b36;border-radius:9px;
   padding:11px;font:inherit;margin-bottom:11px}}
 button{{width:100%;background:#2f6fb5;color:#fff;border:0;border-radius:9px;padding:11px;
   font:inherit;font-weight:600;cursor:pointer}}
 .err{{color:#f85149;margin:0 0 12px}}
</style></head><body>
<form method="post" action="/entrar">
  <h1>Dashboard del experimento</h1>
  <p>Escribe la contrasena de verificación del sprint para entrar: son 64 caracteres
     hexadecimales y se copia y se pega (está en <code>dashboard/.clave.inicial</code> en la máquina
     que lo hospeda; <code>dashboard/.clave</code> guarda la huella, no la contrasena).</p>
  {aviso}
  <input name="clave" type="password" autofocus autocomplete="current-password"
         placeholder="contrasena">
  <button>Entrar</button>
</form></body></html>""", no_store=True)

    def _pide_contrasena(self) -> None:
        """401 con WWW-Authenticate: para curl y herramientas, no para navegadores."""
        cuerpo = ("hace falta la contrasena de verificacion del sprint: usuario 'equipo' y la "
                  "contrasena que comparte el equipo\n").encode("utf-8")
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="sprint-cooperacion-costosa"')
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _redirigir(self, destino: str, cookie: str | None = None,
                   borrar_cookie: bool = False) -> None:
        self.send_response(303)
        self.send_header("Location", destino)
        if cookie:
            self.send_header("Set-Cookie", cookie)
        if borrar_cookie:
            self.send_header("Set-Cookie", "sprint=; Path=/; Max-Age=0")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _json(self, datos, codigo=200):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._seguridad()
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _seguridad(self, no_store: bool = False) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if no_store:
            self.send_header("Cache-Control", "no-store")

    def _html(self, texto, no_store: bool = False):
        cuerpo = texto.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self._seguridad(no_store)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_POST(self):  # noqa: N802
        ruta = unquote(self.path.split("?")[0])
        if ruta != "/entrar":
            self._json({"error": "ruta desconocida"}, 404)
            return
        ip = self.client_address[0]
        if bloqueado(ip):
            self._json({"error": "demasiados intentos fallidos; espera unos minutos"}, 429)
            return
        largo = int(self.headers.get("Content-Length") or 0)
        datos = self.rfile.read(largo).decode("utf-8", "replace") if largo else ""
        enviada = (parse_qs(datos).get("clave") or [""])[0]
        if DIGEST_CLAVE and self._coincide(enviada):
            self._redirigir("/", cookie=f"sprint={TOKEN}; Path=/; HttpOnly; SameSite=Lax")
        elif not DIGEST_CLAVE:
            self._redirigir("/")
        else:
            registra_fallo(ip)
            # al journal va SOLO la longitud: sirve para diagnosticar sin revelar el intento
            print(f"intento fallido desde {ip}: se enviaron {len(enviada.strip())} caracteres",
                  flush=True)
            if enviada.strip().lower() == DIGEST_CLAVE:
                self._pagina_login(
                    "Eso que escribiste es la huella SHA-256 que guarda el servidor, no la "
                    "contrasena. La contrasena de uso se lee en dashboard/.clave.inicial (64 "
                    "caracteres); si ese archivo ya se borro, hay que generar una nueva.")
            else:
                self._pagina_login(
                    "Contrasena incorrecta. Se copia y se pega: son 64 caracteres hexadecimales, "
                    "sin espacios al principio ni al final.")

    def do_GET(self):  # noqa: N802
        ruta = unquote(self.path.split("?")[0])
        if ruta == "/favicon.ico":
            # sin esto, el navegador lo pide, recibe 401 y en algunos casos vuelve a pedir la clave
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if ruta == "/salir":
            self._redirigir("/", borrar_cookie=True)
            return
        if not self._autorizado():
            if ruta.startswith("/api/"):
                self._pide_contrasena()
            else:
                self._pagina_login()
            return
        if ruta in ("/", "/index.html"):
            with open(os.path.join(BASE, "index.html"), encoding="utf-8") as fh:
                self._html(fh.read())
        elif ruta == "/api/corridas":
            self._json(_corridas_todas())
        elif ruta == "/api/agregado":
            self._json(_agregado(_corridas()))
        elif ruta.startswith("/api/corrida/"):
            rel = "/".join(os.path.basename(p) for p in ruta[len("/api/corrida/"):].split("/"))
            d = _una_corrida(rel)
            self._json(d if d else {"error": "corrida no encontrada"}, 200 if d else 404)
        elif ruta.startswith("/api/transcripcion/"):
            partes = ruta[len("/api/transcripcion/"):].split("/")
            rel = "/".join(os.path.basename(p) for p in partes[:-1])
            agente = os.path.basename(partes[-1]) if partes else ""
            d = _transcripcion(rel, agente)
            self._json(d if d else {"error": "sin transcripcion"}, 200 if d else 404)
        elif ruta == "/api/corpus":
            self._json(_leer_corpus())
        elif ruta == "/api/reglas":
            p = os.path.join(REPORTES, "reglas.json")
            if os.path.exists(p):
                with open(p, encoding="utf-8") as fh:
                    self._json(json.load(fh))
            else:
                self._json({"error": "corre antes: python3 harness/reglas.py"}, 404)
        elif ruta.startswith("/api/reporte/"):
            nombre = os.path.basename(ruta[len("/api/reporte/"):])
            destino = os.path.join(REPORTES, nombre)
            if not destino.endswith(".json") or not os.path.exists(destino) or REPORTES not in destino:
                self._json({"error": "reporte no encontrado"}, 404)
            else:
                with open(destino, encoding="utf-8") as fh:
                    self._json(json.load(fh))
        elif ruta == "/api/estado":
            salida = {}
            for doc in DOCS:
                p = os.path.join(RAIZ, doc)
                if os.path.exists(p):
                    with open(p, encoding="utf-8") as fh:
                        salida[doc] = fh.read()
            self._json(salida)
        else:
            self._json({"error": "ruta desconocida"}, 404)


def main() -> None:
    global DIGEST_CLAVE
    ap = argparse.ArgumentParser(description="Dashboard del experimento (solo lectura).")
    ap.add_argument("puerto", nargs="?", type=int, default=8890)
    ap.add_argument("--host", default="127.0.0.1",
                    help="interfaz donde escuchar (127.0.0.1 = solo esta maquina)")
    ap.add_argument("--red", action="store_true",
                    help="escuchar en toda la red y exigir la contrasena de verificacion")
    ap.add_argument("--clave", metavar="ANULAR", default=None,
                    help="solo para pruebas locales: sin contrasena aunque se abra a la red")
    a = ap.parse_args()

    host = "0.0.0.0" if a.red else a.host
    abierto = host != "127.0.0.1"
    if a.clave == "anular":
        DIGEST_CLAVE = None
    elif abierto:
        DIGEST_CLAVE = digest_de_entrada()
    if not os.path.isdir(SALIDAS):
        print(f"AVISO: no existe {SALIDAS}")

    global TOKEN
    TOKEN = secrets.token_urlsafe(24) if DIGEST_CLAVE else None
    srv = ThreadingHTTPServer((host, a.puerto), Manejador)
    print(f"dashboard escuchando en {host}:{a.puerto}", flush=True)
    if abierto:
        print(f"  en la red: " + " · ".join(f"http://{ip}:{a.puerto}" for ip in ips_de_la_red())
              or "  (no se detectaron direcciones de red)", flush=True)
        print(f"  contrasena de uso: la linea util de "
              f"{os.path.relpath(ARCHIVO_INICIAL, RAIZ)} (64 caracteres hex; el archivo se borra "
              f"tras copiarla). {os.path.relpath(ARCHIVO_CLAVE, RAIZ)} guarda solo su SHA-256: "
              f"copiar de ahi NO sirve para entrar.", flush=True)
    else:
        print(f"  http://127.0.0.1:{a.puerto}  (solo esta maquina; usa --red para abrirlo al equipo)",
              flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
