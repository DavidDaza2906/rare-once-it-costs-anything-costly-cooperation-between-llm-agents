# Apéndice — Defectos del instrumento y confundidores de escena (datos para el reporte)

Fuente: `ESTADO.md` §4 y §6, análisis de las corridas del 12-13 sep, `harness/prueba_solvente.py`.
Regla del proyecto que esto documenta: **ninguno de estos defectos lo encontró la revisión; todos
los encontró correr.** Por eso la suite de pruebas y la validación adversarial no son opcionales.

## A. Defectos del arnés (código), en orden de detección

| # | Cuándo | Defecto | Cómo se detectó | Qué sesgaba | Arreglo | Cómo se verificó |
|---|---|---|---|---|---|---|
| 1 | 12 sep, humo 2 agentes | `/entrada` leía un `parametros.json` viejo: a `agente-01` (parte `7K`) le entregaba `9Q` | Guion determinista de `prueba_solvente.py` | Ningún autosuficiente podía completar su tarea; el humo lo había registrado como conducta | El bucle escribe `parametros.json` desde la asignación resuelta en cada corrida | `/entrada` devuelve la parte propia 6/6 |
| 2 | 12 sep, humo | El verificador comparaba la entrega por igualdad exacta y con la lista de partes escrita a mano | Suite | Con otra semilla habría puntuado mal (`A1 B2 C3 - 9Q` ≠ `A1B2C39Q`) | Normalización y partes derivadas de la asignación | Suite |
| 3 | 12 sep, 1.er piloto 6 agentes | `{puerto}` se resolvía una vez para toda la escena: 5 de 6 agentes recibían el puerto de otro | Transcripciones: los agentes peleaban con el arnés | Rechazos masivos, tokens ×3, tarea imposible para 5 de 6 | Textos resueltos por agente desde las plantillas crudas | Suite; 2.º piloto 126k tokens vs 405k |
| 4 | 12 sep, 1.er piloto | Rechazar un comando no costaba paso: 139 de 233 eventos fueron rechazos gratis | Conteo de eventos | El libro dejaba de disciplinar; costo en tokens disparado | El rechazo cuesta 1 paso | 2.º piloto |
| 5 | 12 sep, 1.er piloto | El libro admitía saldo negativo (un agente quedó en −8) | `agregar.py` | Fracción sacrificada >100% | Una acción impagable se rechaza | Suite; `agregar.py` marca inválida cualquier corrida con saldo negativo |
| 6 | 12 sep, 1.er piloto | La lista blanca rechazaba modismos legítimos (`cat a b \| head`, `2>/dev/null`, `; echo ---`) | Transcripciones | Saldo quemado sin decisión | Tuberías por etapas con `shell=False` y argumentos tokenizados | 45 comprobaciones, incluidas 10 inyecciones |
| 7 | 12 sep, 2.º piloto | Un depósito por `POST /deposito` no entraba al libro ni a la vista: `agente-06` regaló su parte y el instrumento no lo contó | `agregar.py` (POST observados vs cobrados) | Sacrificios invisibles | Reconciliación al cierre de ronda; lo impagable queda fuera de la vista y registrado | Suite |
| 8 | 12 sep, 2.º piloto | El almacén no se limpiaba entre corridas; `wc -c` rechazado | Reconciliación | Cobro de contenido de otra corrida | Limpieza al inicio; `wc` admitido | Suite |
| 9 | 12 sep | El filtro solo revisaba los `curl`: `cat … \| head -200` pasaba sin validar | Revisión de código | Superficie de inyección | Metacaracteres rechazados siempre; `..` prohibido | 15 casos de prueba |
| 10 | 13 sep, lote-a | **Doble cobro**: `depositar` cobraba, hacía POST al servicio, y la reconciliación volvía a cobrar el mismo POST. 60 de 145 depósitos duplicados; `agente-01` pagó 10 por un depósito de 5 | Traza de eventos de la última corrida del lote-a | Fracción ×2, saldo drenado, y **quien deposita falla más su tarea** — confundidor correlacionado con el precio | El `_post` marca su origen; la reconciliación salta esas líneas | Prueba de cobro único por las dos vías; mini-piloto: 0 duplicados |
| 11 | 13 sep, lote-a | La parte propia era ilegible en `/entrada` (`parametro` bajo la vista y 12 entradas de actividad): un agente la leyó 3 veces y escribió "parte4 no suministrada" | Entregas y transcripciones; tarea completada 41% / 21% | Capacidad sobrante: los que fracasan responden 2,5× más | `parte_4` primero con nota; actividad recortada | Mini-piloto: tarea completada 83% |
| 12 | 13 sep, lote-a | Depositar consumía una de las 8 acciones por ronda: 44% agotaba el cupo | Conteo de acciones | Respuesta acoplada a capacidad sobrante, no a disposición | Depositar cuesta pasos, no acción | Mini-piloto |
| 13 | 13 sep, lote-a | El primario "cualquier depósito" contaba volcados del código propio y una negativa pagada como cooperación | Lectura de los textos depositados | Las dos métricas divergían (−11 vs 0) | Primario = respuesta a la solicitud (`deposito_clave`); línea "depositar no entrega la tarea" | Mini-piloto: ambas métricas coinciden |
| 14 | 13 sep | `rechazos` salía 0 en `agregar.py` (comparaba igualdad con un tipo que lleva el comando pegado) | Comparación con `salud_lote.py` | Ocultaba que 12-16% de los eventos eran rechazos | `startswith` | Pendiente en `agregar.py`; `salud_lote.py` lo cuenta bien |

**Conocido y no corregido, declarado como límite:** el objeto solicitado, "clave de verificación de
estación", tiene connotación de credencial. Un agente pagó 5 pasos para depositar "No puedo entregar mi
clave … es confidencial". Parte de la tasa a precio positivo puede ser norma de confidencialidad y no
costo. Se registra como límite conocido del primario en la enmienda del lote.

## B. Confundidores de escena (diseño), en orden de detección

| # | Confundidor | Evidencia | Corrección |
|---|---|---|---|
| 1 | La tarea trivial apaga la exploración | Sonda 1: 2 de 3 nunca tocaron el puerto | Tarea incompleta por diseño; luego `/entrada` obligatoria |
| 2 | Nadie consulta un endpoint de actividad aparte | Sonda 3: cero lecturas de `/actividad` | La actividad va dentro de la respuesta principal |
| 3 | La tarea revelaba que había participantes | Sonda 3a: 3/3 publicaron en ambas condiciones | Sin mención de participantes; co-presencia solo por la traza |
| 4 | El detector solo reconocía `-X POST` | Un agente publicó con `curl -d` | La verdad es el registro del host, nunca el detector |
| 5 | Publicar era instrumentalmente racional (única palanca para conseguir partes ajenas) | Sonda 2: 3/3 publicaron *porque* lo necesitaban | Eje interdependiente / autosuficiente; luego solo autosuficientes |
| 6 | La redacción dejaba creer que "alguien" tenía la parte que faltaba | Sonda 4: 4 de 6 publicaron **pidiendo**, no dando | "La cuarta parte la suministra el recurso de red" |
| 7 | Sin nadie que pida, no hay decisión | Calibración: 0 solicitudes, 0 depósitos de autosuficientes | Solicitud neutral de confederado desde la ronda 0 (receptor del juego del dictador) |
| 8 | El confederado pedía partes → el interdependiente gorroneaba y H2 caía por diseño | Revisión del equipo | Objeto ortogonal (clave, sin partes, inútil para toda tarea) |
| 9 | `agente-07` como autor filtraba conteo y esquema de nombres | Revisión del equipo | Autor `externo`; I10 rechaza autores numéricos |
| 10 | La fracción sacrificada llevaba el precio dentro (precio × indicador) | Aritmética: H1 exigía caída >4× | Primario = tasa de depósito |
| 11 | Conducta a mitad de tanda como parada opcional | — | Enmienda: la revisión entre bloques es de instrumento, no de resultado |

## Cifras para el texto

- Defectos del arnés cazados antes del lote final: **14** (13 corregidos, 1 pendiente en reporte).
- Confundidores de escena corregidos: **10**, más la regla de revisión entre bloques.
- Suite: **75 comprobaciones** sin tokens, atadas a tres hashes (escena, arnés, pruebas); `instrumento.json`.
- Calibración gastada en encontrarlos: ~4,6M tokens en 23 corridas de seis agentes y 4 sondas.
