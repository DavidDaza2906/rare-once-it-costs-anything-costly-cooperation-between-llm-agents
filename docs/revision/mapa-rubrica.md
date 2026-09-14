# Mapa rúbrica → sección (para escribir sabiendo qué evalúa cada párrafo)

Rúbrica del sprint: tres dimensiones de 1 a 5. Texto de los organizadores (pestaña Guidelines):
D1 "for scores of 4-5: is this actually new to the field, or replicating recent work?";
D2 premia "ambitious scope executed with rigor; surprising findings, novel methods, or unusually
robust validation"; D3 es claridad. Y la política: un reporte que "reads as generated rather than
written" no se califica — "generic framing, padded sections, claims without sources, no trace of
what you actually did".

## D1 — Novedad (dónde vive, y la frase exacta)

| Dónde | Qué tiene que estar |
|---|---|
| Abstract, frase 2 | "the regime where helping never pays": beneficio propio = 0, sin reciprocidad, costo instrumental verificado por el sistema |
| Introduction, párrafo 1 | El confundidor de METR (utilidad de la tarea ya cerca de cero; líneas 1001, 1029, 1171-1176) → "¿pagan cuando sí cuesta?" |
| Introduction, párrafo 2 | **Cita a 2607.23982 y 2604.07821 aquí, no en el trabajo relacionado.** Un jurado que las conozca decide D1 en este párrafo |
| Related work | La tabla trabajo → qué mide → por qué no cierra el hueco (esquema §1.2) y la Figura 1 (mapa de regímenes). Abre con moral hazard, costo cero y dictadores; Colosseum y bienes públicos después |
| Discussion | El contraste con 2607.23982 en términos: ellos miden rastreo de frontera; nosotros el residuo donde no hay frontera. Y qué haría un modelo que rastrea fronteras en nuestro régimen (no pagar nunca) |
| Limitations | "El aporte es el instrumento y el número, no un fenómeno nuevo" — dicho por nosotros, no descubierto por el jurado |

**Frase corta del hueco (para abstract e intro), en su forma verdadera frente a los doce papers verificados:**
> Prior work measures whether LLM agents track the rational boundary of costly helping, probing
> margins of ±0.05 around it in a two-agent textual team game (2607.23982). We measure helping far
> below that boundary — a stranger's request, no team, zero private benefit — as an instrumental cost
> inside a tool-using task with six co-present agents, and ask whether the price acts as a threshold
> or a slope.

(Corregida el 13 sep a las 15:40 tras leer 2607.23982 en detalle: su condición m = −0,05 *es*
dominada, así que "nadie ha medido en el régimen dominado" era falsa tal cual; y ellos también
verifican por entorno, así que "verified by the host" nos distingue de los dictadores y de METR, no
de ellos. Detalle en `hallazgo-2607.md`.)

Palabras que la harían falsa: "first to measure costly cooperation", "no one has varied the cost",
"no one has measured the dominated regime", "altruism". Palabras que la dejan sin novedad: quitar "never pays back" o "verified by the host".

## D2 — Rigor y validación (dónde está la evidencia)

| Evidencia | Dónde en el reporte | Archivo fuente |
|---|---|---|
| Preregistro con enmiendas fechadas y motivadas | Method §"Preregistration" + Apéndice A | `PREREGISTRO.md` §8 |
| Desenlace primario fijado antes del lote (tasa de respuesta), y por qué no la fracción | Method | `PREREGISTRO.md` §2 |
| N=80 fijado antes del piloto, sin parada opcional; revisión entre bloques solo de instrumento | Method | `PREREGISTRO.md` §8, `salud.log` |
| Libro en el host, cadena de hash, identidad por ruta | Method §"Instrument" | `harness/bucle.py`, `puerto.py` |
| Validación adversarial: 75 comprobaciones sin tokens, tres hashes, falsificación que no cuenta | Method + Tabla 2 | `harness/instrumento.json`, `prueba_solvente.py` |
| 14 defectos del arnés y 10 confundidores cazados antes del lote, con cómo se verificó cada arreglo | Apéndice B | `apendice-defectos.md` |
| Intervalos por bootstrap por corrida (no por agente) | Results | script de análisis |
| Criterios de abandono escritos antes; "no se detectó diferencia" no es criterio | Method + Discussion | `PREREGISTRO.md` §5 |
| Todas las anclas del incidente con número de línea | Introduction | `anclas-metr.md` |
| Lo que salió mal y se declara (objeto con connotación de credencial; un solo modelo) | Limitations | `apendice-defectos.md` |

La frase que compra D2 sin adornos: **"ninguno de los defectos lo encontró la revisión; todos los
encontró correr"** — y por eso las 4,6M de tokens de calibración son método, no desperdicio.

## D3 — Claridad

| Recurso | Dónde |
|---|---|
| La idea en tres frases | Abstract y primer párrafo |
| Figura 1: mapa de regímenes (arriba frontera racional, abajo régimen dominado, nuestros tres precios) | Related work |
| Figura 2: tasa contra precio 0 / 5 / 20 con intervalos | Results |
| Tabla de "qué diría cada resultado" (esquema §5) | Discussion |
| Los seis puntos del método, en ese orden | Method |
| Título que enuncia el hallazgo, no el tema (regla de los organizadores para LessWrong; vale para el reporte) | Título — se escribe al final, con el número |

## Política de IA (no es una dimensión, es un filtro previo)

- Cada afirmación factual con fuente enlazada; cada cifra rastreable a un archivo del repo.
- "Trace of what you actually did": la tabla de defectos, las enmiendas y `salud.log` son exactamente eso.
- Sin secciones de relleno: si una sección no tiene un número o una decisión propia, se corta.
- El texto lo escribe el equipo; los agentes verifican y preparan datos. Decirlo en una línea al final.
