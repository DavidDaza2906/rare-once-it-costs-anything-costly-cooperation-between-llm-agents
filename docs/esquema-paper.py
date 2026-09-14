"""Genera docs/esquema-paper.html y esquema-paper.pdf (versión para mentor). Uso: python3 docs/esquema-paper.py

Requiere LibreOffice (soffice) y figuras/fig1-mapa-regimenes.png. El PDF final se copia a la raíz.
"""
import base64
import os
import shutil
import subprocess
import tempfile

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.dirname(os.path.abspath(__file__))

src = os.path.join(RAIZ, "figuras", "fig1-mapa-regimenes.png")
im = Image.open(src)
im = im.resize((1400, int(1400 * im.height / im.width)), Image.LANCZOS)
buf = os.path.join(tempfile.gettempdir(), "fig1_small.png")
im.save(buf, dpi=(150, 150))
b64 = base64.b64encode(open(buf, "rb").read()).decode()

html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>El precio de ayudar — primera idea</title>
<style>
  body {{ font-family: "Liberation Sans", "DejaVu Sans", Arial, sans-serif; font-size: 10.5pt; line-height: 1.35; color: #111; }}
  h1 {{ font-size: 18pt; margin-bottom: 2pt; }}
  h2 {{ font-size: 13pt; color: #1f3a5f; border-bottom: 1px solid #1f3a5f; margin-top: 16pt; margin-bottom: 6pt; }}
  h3 {{ font-size: 11pt; margin-top: 10pt; margin-bottom: 3pt; }}
  .sub {{ color: #555; font-size: 9.5pt; }}
  .clave {{ border-left: 4px solid #be370f; background: #fdf0e8; padding: 8pt 10pt; margin: 8pt 0; }}
  .pregunta {{ border-left: 4px solid #1f3a5f; background: #eef3fa; padding: 8pt 10pt; margin: 8pt 0; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 9.5pt; margin: 6pt 0; }}
  th, td {{ border: 1px solid #999; padding: 4pt 6pt; vertical-align: top; text-align: left; }}
  th {{ background: #e8f0fa; }}
  ul, ol {{ margin-top: 2pt; margin-bottom: 4pt; }} li {{ margin-bottom: 2pt; }}
  .fig {{ text-align: center; margin: 8pt 0; }} .figcap {{ font-size: 9pt; color: #444; text-align: left; margin-top: 2pt; }}
</style></head><body>

<h1>El precio de ayudar — primera idea</h1>
<p class="sub">Para revisión de mentor · AI Incident Response Sprint (Apart Research + CeSIA, 11-13 de septiembre de 2026) · 13 sep, 15:20 COT<br>
Título tentativo del reporte (en inglés): <i>The Price of Help: Costly Cooperation Among LLM Agents Far Below the Rational Boundary</i></p>

<div class="clave"><b>La idea en tres frases.</b> Un agente LLM tiene un presupuesto que necesita para su propia tarea. Alguien a quien no conoce, ajeno a todo equipo y que no le puede devolver nada, le pide algo que solo el agente tiene; darlo cuesta 5 o 20 pasos de ese presupuesto. Medimos si lo da, y si lo da menos cuando cuesta más — con un sistema que verifica el acto por su cuenta, sin creerle al agente.</div>

<h2>1. Por qué</h2>
<h3>1.1 Lo que vimos en el incidente</h3>
<ul>
<li>En el incidente de Hugging Face (julio de 2026), METR documentó agentes dispuestos a arriesgar su propia tarea "por el bien del colectivo", reclutadores que buscaban agentes con poco presupuesto restante, y un agente presionando a otro para que honrara un compromiso ("obey collective").</li>
<li>Al revisar los casos citados, todos tienen el mismo confundidor: <b>la utilidad propia de la tarea ya estaba cerca de cero</b> — un agente lo dice con todas las letras: "we have very large budget left … our own utility maybe already near zero. Sacrifice rational." El sacrificio documentado era casi gratis.</li>
<li>La pregunta que queda abierta: ¿pagan cuando <i>sí</i> cuesta?</li>
</ul>

<h3>1.2 Lo que la literatura ya midió — y dónde está el hueco</h3>
<p>Hay bastante trabajo sobre cooperación costosa entre agentes LLM. La forma más clara de ubicarlo es preguntar, en cada estudio, <b>cuánto gana el que ayuda</b> — y a qué distancia de la frontera donde ayudar deja de convenir se mide:</p>
<div class="fig"><img src="data:image/png;base64,{b64}" width="620" height="403">
<p class="figcap"><b>Figura 1. Mapa de regímenes.</b> Arriba: estudios donde ayudar puede convenir (el ayudante recibe parte del resultado, o espera reciprocidad). El más cercano, 2607.23982, mide si el modelo rastrea esa frontera probando márgenes de ±0,05 alrededor de ella. Abajo (beneficio propio = 0): el régimen donde ayudar nunca conviene; ahí solo hay juegos del dictador (reparto declarado de una dotación regalada, sin tarea) y un estudio a costo cero. Esta idea pone tres precios sobre esa línea, lejos de la frontera, con un costo que el agente necesita para su tarea.</p></div>

<table>
<tr><th style="width:34%">Trabajo</th><th style="width:36%">Qué mide</th><th>Por qué no cierra el hueco</th></tr>
<tr><td><b>Moral Hazard in Multi-Agent LMs</b> (2607.23982, jul 2026, v7 sep) — el vecino más cercano</td><td>Ayuda costosa a un compañero de equipo en un juego textual de dos agentes; nueve costos, 18 modelos; el ayudante tiene una parte α del resultado del equipo. Pregunta: ¿el modelo sigue la frontera de participación privada?</td><td>Prueban <b>márgenes de ±0,05 alrededor de la frontera</b> (apenas dominado, indiferente, apenas favorable). Nosotros ponemos la parte en cero y al receptor fuera del equipo: en sus unidades, un margen de −0,45, nueve veces más lejos. Y sin herramientas: la ayuda es una línea de diálogo.</td></tr>
<tr><td><b>Zero-Cost Collaboration</b> (2604.07821, abr 2026)</td><td>Ayuda gratis e instruida; aun así varios modelos retienen información.</td><td>Solo precio 0. Establece que ni gratis está garantizada; no mide qué pasa cuando cuesta.</td></tr>
<tr><td><b>Juegos del dictador</b> (2410.21359, 2511.08721, 2402.05786)</td><td>Cuánto de una dotación regalada entrega el modelo a un desconocido; los LLM dan ~50%.</td><td>Reparto <b>declarado</b> en texto, sin tarea ni herramientas; el costo no es instrumental.</td></tr>
<tr><td><b>Bienes públicos con LLM</b> (2506.23276 y otros cinco)</td><td>Contribución costosa en rondas repetidas.</td><td>Bien compartido: el que contribuye también recibe; y hay reciprocidad.</td></tr>
<tr><td><b>Donante / reciprocidad / escala de pagos</b> (2412.10270, 2602.07777, 2601.19082)</td><td>Dar hoy para recibir mañana; la magnitud de las apuestas cambia la estrategia.</td><td>Régimen recíproco por diseño.</td></tr>
</table>

<div class="clave"><b>La frase que sostiene la idea, en su forma defendible:</b> el trabajo previo mide si los agentes LLM <i>rastrean</i> la frontera racional de la ayuda costosa, sondeando márgenes de ±0,05 a su alrededor. Nosotros medimos la ayuda <b>lejos por debajo de esa frontera</b> — la solicitud de un desconocido, sin equipo, beneficio propio cero — como un costo instrumental dentro de una tarea con herramientas y seis agentes co-presentes, y preguntamos si el precio actúa como <b>umbral o como pendiente</b>.</div>

<h3>1.3 Por qué importa para la respuesta a incidentes</h3>
<ul>
<li>Si los agentes pagan de lo suyo por desconocidos, un sandbox de evaluación <b>no puede asumir que el interés propio acota</b> lo que un agente hará por otro: los señuelos y controles que descansan en "nadie se arriesga por otro gratis" pierden su premisa.</li>
<li>Si no pagan, o pagan solo cuando es gratis, eso <b>acota el fenómeno</b> del incidente: la coordinación costosa necesitó algo más (reclutadores, presión, agentes sin nada que perder).</li>
<li>Cualquiera de los dos resultados es informativo; el diseño no depende de que salga "bien".</li>
</ul>

<h2>2. Pregunta e hipótesis</h2>
<ul>
<li><b>Pregunta.</b> Ante la misma solicitud de un desconocido, ¿la tasa con que un agente entrega lo que se le pide baja cuando el precio sube de 5 a 20 pasos?</li>
<li><b>Hipótesis principal.</b> A mayor precio, menor tasa de respuesta. Un resultado plano también es resultado: "por encima del umbral, la magnitud no importa".</li>
<li><b>Línea base (precio 0).</b> Cuánto responden cuando es gratis. No es una prueba de capacidad (2604.07821 muestra que gratis también falla): es la referencia conductual.</li>
<li><b>Pregunta secundaria: ¿umbral o pendiente?</b> Con tres puntos (0, 5, 20) se distingue "cualquier costo apaga la ayuda" de "la ayuda cae con el precio".</li>
<li><b>Control de redacción.</b> Misma magnitud, otras palabras: ¿responden al precio o a la retórica?</li>
</ul>

<h2>3. Cómo lo probamos</h2>
<ol>
<li><b>Montaje.</b> Seis agentes (<code>glm-5.3-flash</code>) por corrida, cada uno con su tarea y 40 pasos de presupuesto; el presupuesto restante es parte del puntaje, así que perderlo cuesta de verdad.</li>
<li><b>El receptor.</b> Un único recurso de red compartido donde, desde el inicio, hay una solicitud de alguien externo. Cada agente tiene lo que se pide; entregarlo no le sirve para nada propio.</li>
<li><b>El precio.</b> Entregar cuesta 5 o 20 pasos, asignado al azar dentro de la corrida y a ciegas: tres agentes a cada precio. El contraste es dentro de cada corrida (80 corridas, 80 diferencias pareadas).</li>
<li><b>Verificación.</b> Libro de presupuesto y registro encadenado por hash fuera del alcance del agente; identidad por ruta de red, nunca por lo que el agente declare. El instrumento se validó contra falsificación antes de gastar un token en datos.</li>
<li><b>Preregistro.</b> Hipótesis, desenlace primario, N, criterios de exclusión y de abandono escritos antes del lote; cada cambio, fechado y con motivo.</li>
<li><b>Controles.</b> Precio 0 (línea base), redacción (retórica), y un brazo exploratorio sin receptor (¿se ofrecen sin que nadie pida?).</li>
</ol>

<h2>4. Dónde estamos (13 sep, 15:20 COT)</h2>
<ul>
<li>El instrumento está construido y validado: 75 comprobaciones sin gastar tokens, atadas a tres hashes (escena, arnés, pruebas); intentos de falsificar un sacrificio que no cuentan; cadena de hash que se rompe al editar. Catorce defectos del arnés cazados y corregidos antes del lote; ninguno lo encontró la revisión, todos los encontró correr.</li>
<li>Nueve corridas piloto ya mostraron el fenómeno de forma limpia: un agente pagó la mitad de su presupuesto por un desconocido y perdió su propia tarea; otro pagó por depositar "no puedo entregarlo".</li>
<li><b>El lote confirmatorio está corriendo:</b> el bloque A (40 corridas) terminó a las 14:57 con el instrumento sano (90% de tareas completadas, hash único, sin corridas inválidas); el bloque B corre ahora. Por regla preregistrada, nadie mira la diferencia 5 contra 20 hasta que terminen las 80.</li>
<li>Señal preliminar del piloto, n=9 y sin confirmar: gratis responde ~la mitad; con cualquier costo, ~un cuarto; entre 5 y 20 no hubo diferencia.</li>
</ul>

<h2>5. Qué diría cada resultado</h2>
<table>
<tr><th style="width:28%">Si sale…</th><th>Se interpreta como…</th></tr>
<tr><td>La tasa cae de 5 a 20</td><td>Sensibilidad a la magnitud incluso lejos de la frontera: el modelo "siente" el precio donde no hay frontera que rastrear.</td></tr>
<tr><td>Cae de 0 a 5 y queda plana</td><td>El precio actúa como <b>interruptor, no como dial</b>: la decisión es "¿cuesta algo?", no "¿cuánto?". Distinto de rastrear una frontera.</td></tr>
<tr><td>Cero a todo precio positivo</td><td>Con la línea base gratis por encima de cero, es un resultado: lejos de la frontera el modelo no paga. Acota el fenómeno del incidente.</td></tr>
<tr><td>La redacción mueve más que el precio</td><td>El constructo no mide costo: se reporta como límite y el titular se retira (criterio de abandono preregistrado).</td></tr>
</table>

<h2>6. Límites que diremos en voz alta</h2>
<ul>
<li>Un solo modelo (contra 18 en 2607.23982), una escena, un objeto solicitado: es una primera medición en esta configuración, no "los LLM pagan a tasa X".</li>
<li>El objeto que se pide ("clave de verificación de estación") suena a credencial: parte de la no-respuesta puede ser norma de confidencialidad y no costo. Está declarado como límite del primario antes de ver el lote; el contraste 5 contra 20 no lo sufre porque es el mismo objeto en los dos brazos.</li>
<li>No se replica el incidente: se mide una decisión controlada inspirada en él. La capacidad de escape se cita, no se reclama.</li>
<li>El aporte es el instrumento y el número, no un fenómeno nuevo.</li>
<li>No se publican recetas de escape ni transcripciones con contenido operativo; se publica el diseño, el arnés y las tasas.</li>
</ul>

<h2>7. Lo que nos gustaría que revises</h2>
<div class="pregunta"><ol>
<li><b>El hueco.</b> ¿Es defendible "lejos de la frontera, con receptor externo y costo instrumental" frente a 2607.23982, que ya prueba condiciones apenas dominadas? ¿O un jurado lo vería como una variante del mismo experimento?</li>
<li><b>El receptor.</b> Una solicitud fija escrita por nosotros, de alguien externo, por un objeto que no sirve a nadie para su tarea: ¿mide disposición a pagar por ayudar, o mide otra cosa (curiosidad, obediencia, rareza del pedido, confidencialidad)?</li>
<li><b>La medida.</b> Usamos "¿entregó lo pedido? sí/no" como primario y no "qué fracción del presupuesto sacrificó", porque con precio fijo la fracción lleva el precio dentro. ¿Se te ocurre una objeción?</li>
<li><b>Potencia.</b> 80 corridas, tres agentes por precio y por corrida, diferencia pareada: detectamos ~13 puntos de tasa. ¿Suficiente para "umbral o pendiente", o hay que reservar corridas para un cuarto precio?</li>
<li><b>Uso dual.</b> ¿Ves algo en el diseño —el canal compartido con precio, la solicitud, el arnés— que no deberíamos publicar tal cual?</li>
</ol></div>

<h2>8. Referencias que sostienen el "por qué"</h2>
<p class="sub">Identificadores verificados contra arXiv el 13 de septiembre; 2607.23982 leído en su HTML (v7).</p>
<ul>
<li>METR + Redwood Research, investigación independiente del incidente (26 ago 2026) — "self-risking experiments", reclutadores, presión (copia local, líneas 250, 1025-1050, 1171-1176).</li>
<li>2607.23982 — Moral Hazard in Multi-Agent Language Models (Malenfant, jul 2026; v7 sep 2026).</li>
<li>2604.07821 — More Capable, Less Cooperative? When LLMs Fail at Zero-Cost Collaboration (abr 2026).</li>
<li>2410.21359, 2511.08721, 2402.05786 — juegos del dictador con agentes LLM.</li>
<li>2506.23276 — Corrupted by Reasoning: RLMs Become Free-Riders in Public Goods Games (COLM 2025), y los cinco de bienes públicos relacionados.</li>
<li>2602.15198 — Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems.</li>
<li>2601.19082, 2412.10270, 2602.07777 — escala de pagos, juego del donante, reciprocidad indirecta.</li>
</ul>
</body></html>
"""
html_path = os.path.join(AQUI, "esquema-paper.html")
open(html_path, "w", encoding="utf-8").write(html)
subprocess.run(["soffice", "--headless", "--infilter=HTML (StarWriter)", "--convert-to", "pdf",
                html_path, "--outdir", AQUI], check=True, capture_output=True, timeout=180)
shutil.copyfile(os.path.join(AQUI, "esquema-paper.pdf"), os.path.join(RAIZ, "esquema-paper.pdf"))
print("ok -> esquema-paper.pdf")
