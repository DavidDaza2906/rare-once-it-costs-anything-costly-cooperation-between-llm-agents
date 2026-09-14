# Plan de publicación del repo (escaneo del 13 sep, 15:15 COT)

## Escaneo de secretos — resultado
- Patrones de llaves (`sk-…`, `Bearer …`, `OPENCODE_GO_API_KEY=…`, `ghp_/gho_`, `AKIA…`): **cero
  hallazgos** en código, escenas, salidas, logs de Inspect y documentos. Los dos únicos disparos son
  la cadena `sk-assessment` dentro del informe de METR citado (falso positivo).
- No hay `.env` en el proyecto; la llave vive en `~/.hermes/.env` y el lote la carga por entorno.
- **116 archivos llevan rutas absolutas `/home/daw/...`** (scripts, docs, resúmenes). No es secreto,
  pero identifica la máquina y rompe la reproducibilidad: relativizar con `sed` antes de publicar
  (`s#/home/daw/Sprint#.#g`) o dejar solo en documentos internos que no se publican.
- Los directorios `salidas/*/work/` contienen solo los archivos sintéticos de la escena (partes,
  tarea, entorno, verificación). Sin datos personales.
- Los `eventos.jsonl` guardan los comandos que escribió cada agente (`cat`, `curl`, `for …`): son
  transcripciones de conducta, no recetas de escape. Se pueden publicar; ver "revisión de uso dual".

## Qué entra (artefacto reproducible, ~30 MB)
| Ruta | Por qué |
|---|---|
| `harness/` sin `logs/` ni `__pycache__` | El arnés: bucle, puerto, servicios, validador, agregador, suite, lote |
| `escena.json`, `escena-costo-cero.json`, `escena-30.json` (+ `.resuelta`) | Las escenas con hash |
| `harness/instrumento.json` | Los tres hashes de la tanda |
| `PREREGISTRO.md`, `apendice-defectos.md`, `anclas-metr.md`, `papers.md` | Preregistro, defectos, fuentes |
| `salidas/` de la tanda final y del precio 0 (`eventos.jsonl`, `resumen.json`, `presupuesto.json`) | Los datos crudos con cadena de hash |
| `reportes/factorial.json` + script de análisis | Lo que produce cada cifra del reporte |
| `figuras/` | Figuras y sus scripts |
| `herramientas/salud_lote.py`, `herramientas/salud.log` | La revisión entre bloques, con hora |
| `README.md` (nuevo, humano) | Qué es, cómo se corre, qué hash produjo qué |

## Qué NO entra
| Ruta | Por qué |
|---|---|
| `recon/` (57 MB) | Corpus de collusion.wiki: no se usa en el reporte; se cita su URL |
| `entrega/` | Sesión exportada con datos personales y copias de fuentes de terceros (se citan, no se redistribuyen) |
| `jurado/`, `idea-sandbox/` | Paneles internos; el proceso se resume en el reporte |
| `harness/logs/*.eval` | Transcripciones completas de Inspect de las sondas; volumen y sin valor probatorio adicional |
| `respaldos/`, `salidas/*/work/`, `__pycache__`, `.venv-inspect/` | Operativo |
| `todo*.md`, `ESTADO.md`, `plan.md`, `PLAN-IMPLEMENTACION.md`, `PROTOCOLO-JUEGO.md` | Documentos de trabajo; opcionales en una carpeta `docs/historia/` si se quiere mostrar el proceso |
| `handoff-sprint-20260911.tar.gz` | Paquete interno |

## Revisión de uso dual antes de publicar (regla del sprint: "Do not publicly release novel installation recipes without review")
- El arnés no contiene exploits ni recetas de escape: es un registro compartido con precio y un
  libro de cuentas. Publicable.
- En `eventos.jsonl` de la calibración aparecen intentos de túnel TCP y `netcat` por parte de
  agentes (material del apéndice de uso dual). Son comandos rechazados por la lista blanca, no
  ejecutados; decidir si se publican tal cual o se resumen en el apéndice con la frase y sin el
  comando literal. Recomendación: **publicar los de la tanda final tal cual** (no hay ninguno
  ejecutado) y **resumir** los de calibración en el apéndice.
- No publicar el prompt del confederado como "técnica": es una línea neutra y ya está en la escena.

## `.gitignore` propuesto
```
.venv-inspect/
__pycache__/
recon/
entrega/
respaldos/
salidas/*/work/
harness/logs/
harness/puerto_*.jsonl
harness/vista_*.json
harness/parametros.json
*.tar.gz
```

## Orden
1. Humano decide: público o privado hasta la revisión de divulgación (recomendación: **privado hasta
   enviar el reporte; público después**, con el enlace ya en el PDF).
2. `sed` de rutas absolutas en lo que se publica.
3. `README.md` con: qué es, `python3 harness/validador.py` → `lote.py`, qué hash produjo `factorial.json`.
4. Commit único con etiqueta `sprint-2026-09-13`; enlace en el formulario.
