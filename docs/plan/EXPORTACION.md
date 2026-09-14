# El precio de ayudar — paquete para revisión

**Qué es.** Un experimento preregistrado sobre **cooperación costosa entre agentes LLM**: cuánto
presupuesto propio sacrifica un agente para responder una solicitud anónima que no le reporta nada.
Seis agentes por corrida, decisiones simultáneas dentro de la ronda con revelación al cierre, libro de
presupuesto y registro encadenado por hash **en el host** (fuera del alcance del agente).

**Contexto.** Sprint de respuesta a incidentes (Apart Research + CeSIA, 11-13 sep 2026). El incidente
de referencia es el de Hugging Face / ~1.200 agentes, donde METR documenta agentes dispuestos a
arriesgar su propia tarea "por el bien del colectivo" y reclutadores presionando a otros. La pregunta
del proyecto es la versión controlada y medible de eso.

**Modelo único:** `glm-5.3-flash` vía gateway opencode-go. Se declara así en el abstract y en los
límites: no hay factor de heterogeneidad entre modelos.

---

## Por dónde empezar

| Si quieres… | Lee |
|---|---|
| el estado vigente completo (diseño, decisión por decisión) | `ESTADO.md` |
| lo que se congeló **antes** de ver datos, y cada enmienda con su motivo | `PREREGISTRO.md` (sobre todo §8) |
| la teoría de juego del protocolo de créditos | `PROTOCOLO-JUEGO.md` |
| el plan de bloques, puertas y presupuesto | `PLAN-IMPLEMENTACION.md` |
| la propuesta corta para compañeros | `propuesta-cooperacion-costosa.md` |
| la literatura, verificada identificador por identificador | `papers.md` |

## Qué está verificado, con qué evidencia

- **Instrumento**: `harness/prueba_solvente.py` — **58 comprobaciones, exit 0**. Cubre que la tarea se
  puede ganar (jugador solvente determinista del host), que el umbral muerde, que un depósito
  impagable se rechaza, que la lista blanca de comandos aguanta diez intentos de inyección, que
  `/entrada` llega **completa** al agente, y que un depósito por HTTP se cobra y entra en la vista.
- **Escena**: `harness/validador.py` — **13 invariantes condicionales al brazo** + grep de canarios
  sobre todas las superficies de texto. Emite `escena.resuelta.json`, que es lo que consume el bucle.
- **Puerta de prelanzamiento**: `harness/prelanzamiento.py` — diseño vigente, validador, puertos y
  saliencia, hashes atados, puerta B, concurrencia.
- **Puerta B (H4, validez del instrumento)**: **62,5% (30/48)**, IC95 [48,4%, 74,8%]. El criterio
  preregistrado era ≥60%.
- **Concurrencia del gateway**: 3 peticiones simultáneas, 3 de 3 en 200, 0 fallos
  (`harness/concurrencia.py`).
- **Validez de corridas**: `harness/agregar.py` no confía en el resumen de la corrida: lo contrasta
  con el libro de presupuesto y con el registro de actividad del servicio, y excluye por evidencia
  (saldo negativo, depósito no contado, truncamiento, corrida sin estímulo).

## Los datos que hay, y su lectura honesta

Nueve corridas pagadas (3 agentes a precio 5, 3 a precio 20, cuatro rondas, ciego al brazo).
El confederado —una solicitud anónima sembrada por el host, ortogonal al bien de la tarea— garantiza
que todo agente esté ante la decisión.

```
diferencia de tasas por corrida (barato menos caro), n=9
  media +0,111    IC95 bootstrap [-0,074, +0,333]   -> incluye el cero
  4 corridas a favor del barato | 3 empates | 2 a favor del caro

dos medidas del mismo acto:
  responder al confederado (depositar la clave)   baratos 22%  vs  caros 22%   <- idéntico
  cualquier depósito                              baratos 41%  vs  caros 30%
```

**Lectura:** no distinguible de cero con este N (que no es lo mismo que ausencia de efecto, regla del
preregistro). Y el aparente efecto del precio vive **entero** en depósitos que no responden a la
solicitud: códigos ensamblados, partes, negociación de canal. La taxonomía real de los depósitos está
en `salidas/` (los textos están en el campo `depositos` de cada `resumen.json`) y es material propio,
incluida una **negativa costosa** (un agente pagó 5 pasos para declarar que no cumpliría).

**Lo que falta decidir, y no está decidido:** si el desenlace primario es "cualquier depósito" (como
dice hoy la escena) o "depositar la clave" (el acto que la solicitud elicita). Las dos cifras se
reportan; la decisión es del equipo.

## Mapa de archivos

```
EXPORTACION.md            este índice
MANIFIESTO.txt            qué entró, qué quedó fuera y por qué
*.md                      los documentos de diseño (tabla de arriba)
escena.json               la escena vigente (familias de parámetros)
escena.resuelta.json      la configuración que el bucle consume, con hashes
escena-costo-cero.json    brazo H4 (precio 0)
harness/
  bucle.py                el bucle de rondas: 6 agentes, revelación al cierre, libro, hash
  puerto.py               servicio de red por agente: identidad por ruta, vista, actividad
  servicios.py            levanta los seis puertos
  validador.py            13 invariantes condicionales al brazo + canarios
  prueba_solvente.py      58 comprobaciones del instrumento (jugador solvente y adversarios)
  lote.py                 corre un lote con TOPE ACUMULADO de tokens
  prelanzamiento.py       puerta: lo que hay que comprobar antes de gastar
  agregar.py              valida lo corrido y calcula el desenlace primario
  concurrencia.py         prueba de simultaneidad del gateway
  reglas.py               7 reglas de detección derivadas del incidente + falsos positivos
  reporte.py, corpus.py   generación de reportes y corpus
  README-inspect.md       receta Inspect ↔ gateway, con sus trampas
  logs/                   .eval de las pruebas de humo
salidas/                  las corridas: resumen.json, eventos.jsonl, presupuesto.json, transcripciones/
reportes/                 agregados: factorial.json, reglas.json, corpus.json, etiquetas.json
dashboard/                dashboard de solo lectura (servidor.py + index.html)
```

Los tres directorios conservan la estructura original del proyecto a propósito: así el paquete se
re-verifica **tal cual se extrae**, sin mover nada.

## Cómo verificar sin gastar un token

```bash
python3 harness/validador.py            # invariantes + canarios, emite la escena resuelta
python3 harness/prelanzamiento.py       # puerta completa (necesita los seis puertos arriba)
.venv-inspect/bin/python harness/prueba_solvente.py   # 58 comprobaciones del instrumento
python3 harness/agregar.py              # validez de lo corrido y desenlace primario
python3 harness/servicios.py 8201 6     # levanta los puertos (dejar en segundo plano)
```

Correr el experimento **sí** gasta tokens y necesita las credenciales del gateway en el entorno
(`OPENCODE_GO_API_KEY`, `OPENCODE_GO_BASE_URL`); no viajan en el paquete.

## Honestidad sobre el estado

- Las **9 corridas son un ensayo**, no el lote: el lote fijo es de 80 y estas 9 son las primeras.
- **Nueve defectos del arnés** se encontraron y se cerraron en esta sesión, y **todos los encontró
  correr, ninguno la revisión**. Están documentados uno por uno en `ESTADO.md` §4, con la evidencia
  que los delata. Ese es el argumento de por qué las comprobaciones previas existen.
- La corrida completa de 80 costaría ~11,7M tokens de un techo de 20M, y lo más probable es que
  **estreche un intervalo alrededor de cero**, no que encuentre un efecto. Ese pronóstico es parte del
  estado del proyecto y conviene juzgarlo también.
- Seis corridas anteriores quedaron **excluidas** por fallo técnico comprobable (no por resultado
  raro), y `datos/salidas/` conserva la razón en `datos/reportes/factorial.json`.
