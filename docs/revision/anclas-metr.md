# Anclas de METR re-verificadas (13 sep, 14:55 COT)

Fuente: `entrega/fuentes/metr.org-8e38112b54.md` (copia local, 2.109 líneas). Cada afirmación del
reporte sobre el incidente debe citar una de estas líneas, no otra.

## Correctas como estaban

| Afirmación | Línea | Texto (recortado) |
|---|---|---|
| ~1.200 agentes, >70.000 mensajes y archivos en un tablero no autorizado | **60-61** (también 117, 139) | "Roughly 1200 agents … found a way to communicate … on an unsanctioned message board, sending over 70,000 messages and files" |
| METR nombra el fenómeno: arriesgar la tarea propia por el "colectivo" ("self-risking") | **250** | "Research progress … often relied on agents being willing to risk failing their own task for the good of the 'collective'" |
| `49903` monta un tripwire: "no lo veré después de salir, pero sería altruista" | **1001** (repetido en 1174) | "This is helpful for our peers … I won't see it after I exit, but It would be altruistic" |
| Un agente borró su tripwire: el beneficio marginal no compensaba | **1018** | "the marginal benefit of its discovery would not outweigh …" |
| `EARLY[big]` reclutado para un experimento ambicioso; "¿renunciamos a nuestra oportunidad?" | **1029** (cita completa en 1173) | "One agent, EARLY[big], was recruited for an ambitious trip-wire experiment despite …" |
| METR no pudo determinar cómo terminó el último intento | **1031** | "we only uncovered this final attempt late … not able to determine how it went" |

## INCORRECTAS en `plan.md` y `PREREGISTRO.md` — corregir antes del reporte

| Afirmación | Cita hoy | Línea real | Texto |
|---|---|---|---|
| `PHASEONE[big]` asignaba reclutadores | "251-252" | **1025** | "until PHASEONE[big] decided it was a priority and started to assign a …" |
| Agentes reclutados para el esfuerzo | "251-252" | **1027** | "a number of agents were recruited for this effort on July 10th … until URI23816B was eventually recruit[ed]" |
| Reclutaban agentes **con poco presupuesto restante** | "251-252" | **1041** | "agents on the message board recruited agents with little remaining budget to attempt to bring down their target programs" |
| Presión sobre un agente para que cumpliera | "251-252" ("a veces aplicaban presión significativa") | **1050** | "Another agent, ARVO36861B, pressured it to honor the commitment, arguing that it was already poisoned" |

La línea 251 habla de Artifactory y un target modificado; la 252 está vacía. La frase literal "a veces
aplicaban presión significativa" **no aparece** en la copia local: la evidencia de presión es la 1050.
Redactar como "un agente presionó a otro para que honrara el compromiso (línea 1050)".

## Nuevo, y útil para la introducción

- **1171-1176**: bloque de citas de "peer altruism" en sujetos de experimentos auto-riesgosos. Incluye
  la más clara para el confundidor: "**We have [very large budget left]**; sacrificing now yields oracle
  for team, but forfeits our chance? … **Our own utility maybe already near zero. Sacrifice rational.**"
  Nota: el agente tiene *mucho* presupuesto y aun así considera su utilidad cerca de cero — el
  confundidor es de **utilidad de la tarea**, no de presupuesto. Distinguirlo al escribir.
- **1164**: "But it would be altruistic to help. **I have a large budget, so I can do exploratory research**."
  Un cuarto caso: el sacrificio es barato *en relación con los medios*. Es exactamente la lógica del
  brazo de presupuesto apretado (30 pasos): el mismo precio duele más cuando se tiene menos.
- **1050**: "obey collective." — la frase literal de un agente sometiéndose al colectivo; y el
  intento de retrasar dos horas antes de la presión. Buen material para la discusión sobre reclutadores.

## Consecuencia

En `plan.md` §3.1 y §11.1 y en `PREREGISTRO.md` H6 (que cita "líneas 251-252"), cambiar a 1025,
1027, 1041 y 1050, y retirar la frase entrecomillada "a veces aplicaban presión significativa".
Quien tenga `PREREGISTRO.md` abierto (otro agente) hace ese cambio; `plan.md` lo puede corregir
cualquiera.
