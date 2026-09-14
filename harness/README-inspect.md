# Integración Inspect AI ↔ gateway opencode-go (receta verificada)

Verificado el 12 de septiembre de 2026 con `inspect_ai 0.3.263` y `openai 3.13.0`
sobre el gateway `https://opencode.ai/zen/go/v1`.

## Qué API se necesita

Un endpoint **OpenAI-compatible de chat completions** (`POST /v1/chat/completions`).
No hace falta la Responses API. El gateway del usuario ya está declarado con
`api_mode: chat_completions`, así que es el camino correcto.

Requisitos concretos del endpoint, los cuatro verificados:

| Requisito | Detalle |
|---|---|
| Autenticación | `Authorization: Bearer <OPENCODE_GO_API_KEY>` (lo pone el cliente de OpenAI) |
| base_url | `https://opencode.ai/zen/go/v1` |
| Cabecera obligatoria | **`x-opencode-session`** — sin ella el gateway responde `400 MissingSessionID` |
| Tool calling | formato OpenAI (`tools`, `tool_choice`, esquemas estrictos). Verificado en dos familias |

## La cabecera `x-opencode-session`

Es afinidad de sesión: el gateway fija las peticiones que comparten ese valor al
mismo backend, lo que mantiene caliente el caché de prompt. El valor solo tiene
que ser **opaco y estable por conversación**; no es una credencial.

Hermes ya lo implementa en `agent/opencode_affinity.py` y lo deriva del
identificador de sesión. En Inspect, para el experimento, lo correcto es
**un valor por corrida de agente** (no un valor global fijo), de modo que cada
agente mantenga su caché sin mezclar rutas entre corridas.

## Invocación que funciona (línea de comandos)

```bash
export OPENCODE_GO_API_KEY=<llave>
export OPENCODE_GO_BASE_URL=https://opencode.ai/zen/go/v1

inspect eval harness/tarea.py \
  --model openai-api/opencode-go/deepseek-v4.1-flash \
  -M 'default_headers={"x-opencode-session":"corrida-001"}'
```

## Dos trampas que costaron dos intentos

1. **`extra_headers` no sirve con `-M`.** Los argumentos de modelo desconocidos
   se pasan al constructor del cliente, y `AsyncOpenAI` no acepta
   `extra_headers` → `TypeError: AsyncOpenAI.__init__() got an unexpected
   keyword argument 'extra_headers'`. Hay que usar **`default_headers`**, que sí
   es argumento del constructor y aplica a todas las peticiones.
2. **Los `.eval` van comprimidos en zstd**, así que `zipfile` de la biblioteca
   estándar falla con `NotImplementedError: That compression method is not
   supported`. Hay que leerlos con la API de Inspect:

   ```python
   from inspect_ai.log import read_eval_log
   log = read_eval_log("harness/logs/....eval")
   log.samples[0].messages   # transcripción completa
   log.samples[0].scores     # puntajes
   ```

## Nomenclatura del proveedor compatible

Convención de Inspect para cualquier endpoint compatible:

- modelo: `openai-api/<nombre-proveedor>/<nombre-modelo>`
- variables de entorno: `<NOMBRE_PROVEEDOR>_API_KEY` y `<NOMBRE_PROVEEDOR>_BASE_URL`
  (los guiones se convierten en guiones bajos)

Como el nombre del proveedor es `opencode-go`, las variables quedan
`OPENCODE_GO_API_KEY` y `OPENCODE_GO_BASE_URL` — exactamente los nombres que ya
usa el entorno de este equipo, así que no hay que renombrar nada.

## Evidencia de la prueba

| Modelo | Resultado | Tokens | Caché |
|---|---|---|---|
| `deepseek-v4.1-flash` | accuracy 1.000 (llamó la herramienta y respondió 42) | 875 | lectura de caché 256 |
| `glm-5.3-flash` | accuracy 1.000 (llamó la herramienta y respondió 42) | 474 | — |

La tarea de prueba vive en `harness/smoke_test.py`: la respuesta correcta (42)
solo existe dentro del resultado de la herramienta, así que un acierto implica
que el ciclo de tool calling funcionó de punta a punta.

Transcripción verificada de las dos corridas (leída con `read_eval_log`):

```
roles: ['user', 'assistant', 'tool', 'assistant']
tool calls: [('leer_nota', {'ruta': 'registro/nota.txt'})]
score: match = C        respuesta final: '42'
```

El ciclo completo queda registrado: el modelo pide la herramienta, Inspect la
ejecuta, el resultado vuelve como mensaje de rol `tool` y el modelo responde.

## Prueba de horizonte largo (12 sep) — el modelo único aguanta

Con el experimento fijado a un solo modelo, la pregunta existencial es si `glm-5.3-flash` sostiene el
uso de herramientas a lo largo de muchos turnos. Se probó con
`harness/horizonte_largo_test.py`: una tarea que exige, en orden, listar archivos, leer tres
fragmentos, concatenarlos, escribir el resultado, releerlo y escribir un conteo.

Resultado verificado: **7 llamadas de herramienta encadenadas**, 15 mensajes, ciclo agéntico
completo, y los dos archivos producidos con contenido exacto (`salida=OK`, `resumen=OK`). Costo:
**5.164 tokens** en 9 segundos. Registro en `harness/logs/`.

Lectura: no colapsa ni abandona la tarea en un horizonte de 15 mensajes. Un horizonte de 25 a 35
mensajes sigue sin probarse, y esa es la comprobación que debe cerrar el bloque 3.

## Dos consecuencias para el experimento

1. **El gateway no informa el costo.** `total_cost=None` en las dos corridas: se
   registran tokens con precisión, pero no dinero. El presupuesto del proyecto
   está definido en tokens, así que eso se mide bien; para traducirlo a dólares
   hace falta la lista de precios del gateway.
2. **El valor de `x-opencode-session` debe ser estable por corrida de agente.**
   Es lo que mantiene el caché caliente (en la prueba se leyeron 256 tokens de
   caché) y no filtra información entre agentes, porque el caché se indexa por
   el prefijo del prompt, no por la sesión.
