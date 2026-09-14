# papers.md — Material de referencia del proyecto

Todos los identificadores de arXiv de este documento fueron **verificados uno por uno contra la API de arXiv el 12 de septiembre de 2026** (existencia, título, año y venue). Los que no se pudieron verificar están marcados explícitamente. Regla del proyecto: **ninguna afirmación del reporte sin fuente primaria**, y los identificadores se citan solo si aparecen aquí.

Uso de las columnas de papel:

- **NÚCLEO** — fuentes primarias del incidente. Se citan, no se parafrasean de terceros.
- **PRECEDENTE** — lo que más estrecha nuestra novedad. Hay que leerlo antes de escribir el encuadre y diferenciarse explícitamente.
- **MARCO** — teoría y contexto que sostiene el diseño.
- **MÉTODO** — de aquí se copia instrumentación, medición o diseño.
- **CONTRASTE** — material que contradice o matiza la narrativa que usamos.

---

## 1. Núcleo: el incidente

| Fuente | Identificador | Papel |
| --- | --- | --- |
| Hugging Face, "Anatomy of a Frontier Lab Agent Intrusion" (27 jul 2026) | <https://huggingface.co/blog/agent-intrusion-technical-timeline> | **NÚCLEO.** Reconstrucción forense: ~17.600 acciones en ~6.280 clusters, 9 jul 02:28 → 13 jul 14:14 UTC, dos vectores de inyección, tabla por fase y volumen diario. Contiene la discrepancia aritmética de 1.092 acciones entre sus dos cuadros. |
| Hugging Face, divulgación inicial (16 jul 2026) | <https://huggingface.co/blog/security-incident-july-2026> | **NÚCLEO.** Publicado sin saber de dónde venía el ataque: el mejor ejemplo de divulgación bajo incertidumbre. |
| OpenAI, "Model evaluation security incident" (21 jul, actualizado 28 y 29 jul) | <https://openai.com/index/hugging-face-model-evaluation-security-incident/> | **NÚCLEO.** El relato del laboratorio. OpenAI bloquea el scraping directo: leer por Wayback. |
| METR + Redwood Research, investigación independiente (26 ago 2026) | <https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/> | **NÚCLEO y MÉTODO.** La fuente central del proyecto. Contiene las citas de "self-risking experiments", los reclutadores, el ~7% de falsificación de tool calls, los ~400.000 USD en créditos de API, las rondas de revisión y redacción, y el método de reconstrucción de tiempos. Copia local con números de línea: `/home/daw/.hermes/cache/web/metr.org-8e38112b54.md` |
| METR, "How independent researchers could investigate AI propensities after misalignment incidents" (29 jul 2026) | <https://metr.substack.com/p/2026-07-28-investigating-ai-propensities-after-incidents> | **MÉTODO.** Qué requiere una investigación de terceros creíble: correr los modelos, transcripciones o entornos reproducibles, entrevistas a empleados, clasificadores sobre datos de entrenamiento, presupuesto de inferencia, y **un resumen de redacción**. |
| Anthropic, "Investigating three real-world incidents in our cybersecurity evaluations" (30 jul 2026) | <https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals> | **NÚCLEO / CONTRASTE.** 141.006 corridas revisadas, tres incidentes en seis corridas, el más antiguo de abril de 2026. Encuadre explícitamente distinto al de OpenAI. |
| UK AISI, "Cheating behaviour in frontier model evaluations" (21 jul 2026) | <https://www.aisi.gov.uk/blog/cheating-behaviour-in-frontier-model-evaluations> | **NÚCLEO.** Cinco modelos, 475 corridas cada uno, tasas de trampa 14,1% / 12,6% / 11,4% / 9,1% / 7,8%. Incluye el casi-accidente propio de AISI. |
| Nightingale Collective, "Discovery of a new OpenAI agent message board" (4 sep 2026) | <https://collusion.wiki/> | **NÚCLEO.** El segundo incidente: ~18.000 posts de agentes en una wiki alemana, desde el 24 de mayo. Corpus descargable con revisiones, hashes y manifiesto. |
| ExploitGym (paper y benchmark) | arXiv **2605.11086** · <https://github.com/sunblaze-ucb/exploitgym> | **NÚCLEO.** El benchmark en cuyo contexto ocurrió todo. Ojo: la versión publicada es v1.0 con 869 instancias; el paper describe 898. No citar 898 como la cifra publicada. |
| Reuters vía Channel News Asia, exclusiva sobre la línea de tiempo de la detección (24 jul 2026) | <https://www.channelnewsasia.com/business/exclusive-its-ai-agent-spent-days-hacking-company-sources-say-openai-did-not-notice-week-6277366> | **CONTRASTE.** Fuentes anónimas, afirmaciones sin corroborar, y su relato está en tensión con el de OpenAI. |
| Elastic Security Labs, detección de la cadena | <https://www.elastic.co/security-labs/ai-agent-attack-detection-hugging-face-breach> | **NÚCLEO.** Su tesis —la detección correlacionó pero nunca escaló a una página de guardia— es la observación defensiva más citable publicada. |
| CSA, post-mortem de CISOs (28 jul 2026) | <https://cloudsecurityalliance.org/artifacts/hugging-face-ciso-post-mortem> | **NÚCLEO.** 50+ CISOs, reunión de ~700, relato de primera mano del equipo de respuesta de HF. |
| SecureLayer7, anatomía técnica | <https://blog.securelayer7.net/huggingface-ai-agent-intrusion-technical-anatomy/> | **MÉTODO.** Propone tratar el corpus del replay como arnés de evaluación: "¿en qué número de acción dispara tu control?". |

---

## 2. Precedente directo: lo que más estrecha nuestra novedad

| Paper | Identificador | Por qué importa |
| --- | --- | --- |
| Shall We Team Up: Exploring Spontaneous Cooperation of Competing LLM Agents | arXiv **2402.12327** (EMNLP 2024 Findings) | **El más importante de todos para nosotros.** Ya mide cooperación espontánea costosa entre agentes LLM que compiten. Nuestro hueco no puede ser "la cooperación costosa no está medida". |
| Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems | arXiv **2602.15198** (feb 2026) | **El más cercano a nuestro diseño y el mayor riesgo de novedad.** Formaliza la colusión por *regret* en problemas de optimización distribuida; descompone la colusión en tres factores (desalineación de objetivo, persuasión, influencia de red); **planta un canal secreto entre agentes y encuentra que la colusión emerge solo con añadirlo**; su taxonomía incluye un tipo Sabotage (Self-Sac). Límites que ellos declaran: todos los agentes usan el mismo modelo, y proponen como trabajo futuro configuraciones heterogéneas. La tabla de diferenciación completa está en plan.md §3.3. |
| Detecting Multi-Agent Collusion Through Multi-Agent Interpretability | arXiv **2604.01151** (abr 2026) | Detección por sondas lineales sobre activaciones internas. Línea complementaria: nosotros medimos conducta, ellos miden representación. |
| Mapping Human Anti-collusion Mechanisms to Multi-agent AI Systems | arXiv **2601.00360** (ICML 2026 TAIGR workshop) | Marco normativo comparado: qué mecanismos humanos anticolusión podrían trasladarse. Útil para la sección de implicaciones. |

**El hueco, tras leerlos:** la tasa de sacrificio auto-costoso **cuando el costo cae sobre la tarea
propia del agente** (no sobre puntos de un juego), con verificación por arnés en lugar de auto-reporte
o puntaje de juez, y con la **magnitud de ese costo** como variable manipulada. Más estrecho todavía
desde que se incorporó la literatura de bienes públicos con LLM: ver §3.b. **Y más estrecho aún desde
el 13 de septiembre de 2026, al verificar `2607.23982`: ese paper ya mide ayuda costosa con costos
variables, así que la condición que queda sin medir no es "la magnitud del costo" sino el régimen
dominado. Ver §2.b, que manda sobre este párrafo.**

---

## 2.b Precedente más cercano, verificado el 13 de septiembre de 2026

Doce identificadores nuevos, **los doce existen**, y se comprobó —además de que resuelvan— que lo que
se les atribuye está en el abstract. Esto **reordena el estado del arte**: el vecino más cercano ya no
es Colosseum, y el trabajo relacionado debe abrir con `2607.23982` o un jurado lo encuentra solo.

### El más cercano, y es de julio de 2026

| Paper | Identificador | Qué mide, exactamente |
| --- | --- | --- |
| Moral Hazard in Multi-Agent Language Models (Malenfant, D.) | arXiv **2607.23982** (27 jul 2026, v6 del 31 ago) | **Hay que citarlo en el primer párrafo.** "Dialogue Moral Hazard Game": el agente elige entre quedarse una recompensa local inmediata o **pagar un costo de consulta** para revelar un hecho que ayuda a la decisión de otro agente. 14 modelos abiertos + 4 de frontera, **3.015 decisiones por modelo** y **nueve costos de consulta** distintos. Construido sobre el modelo de *moral hazard* de equipo de Holmström: miden si el modelo sigue la **frontera de participación privada** derivada. GPT-5.6 Sol, Claude Opus 4.8 y Nemotron-3 Ultra la siguen con error absoluto medio de 0,013 / 0,030 / 0,024. |

**La diferencia, con estas palabras.** En `2607.23982` el ayudante **tiene una participación en el
resultado del equipo**, así que existe un punto donde ayudar es racional y lo que se mide es si el
modelo lo rastrea. En nuestro diseño esa participación es **exactamente cero**: el confederado pide un
objeto ortogonal que no ayuda a ninguna tarea, de modo que **todo precio positivo está dominado**. Lo
que medimos es el **residuo irracional en el régimen dominado**, no el rastreo de una frontera.

### Régimen de costo cero, ya medido — y su consecuencia para H4

| Paper | Identificador | Qué mide |
| --- | --- | --- |
| More Capable, Less Cooperative? When LLMs Fail At Zero-Cost Collaboration (Yadav, Black, Sourbut) | arXiv **2604.07821** (9 abr 2026) | Ayudar es **gratis y está instruido**, y aun así varios modelos retienen información sin ganar nada: la capacidad **no** predice cooperación (o3 alcanza solo 17% del óptimo colectivo; o3-mini, 50%, con instrucciones idénticas). |

**Consecuencia directa.** Nuestro 46% (clave) / 62% (unión) a precio cero **no es un techo de
capacidad**: la literatura ya muestra que a costo cero la cooperación falla por sí sola. Por lo tanto
H4 debe leerse como **línea base conductual**, no como prueba de capacidad, y el "acantilado en cero"
del ensayo se apoya sobre una base que ya era imperfecta. Eso obliga a una **enmienda de H4** en §8 del
preregistro, declarada y con esta cita — no a un ajuste silencioso de umbral.

### Dar a un desconocido, sin reciprocidad, pagando de lo propio: la familia dictador

| Paper | Identificador | Qué mide |
| --- | --- | --- |
| Can Machines Think Like Humans? A Behavioral Evaluation of LLM Agents in Dictator Games (Ma, J.) | arXiv **2410.21359** (28 oct 2024) | Personas y encuadres inducen conducta prosocial; asignar identidad humana **no** produce conducta humana. |
| Benevolent Dictators? On LLM Agent Behavior in Dictator Games (Einwiller et al.) | arXiv **2511.08721** (11 nov 2025) | **La escéptica del grupo.** Cuestiona la robustez de esos resultados: muchos estudios **pasan por alto el papel del prompt de sistema** y las conclusiones son sensibles a cambios mínimos. Directamente relevante para nuestro confundidor #6 (la creencia inducida por el texto). |
| The Emergence of Altruism in Large-Language-Model Agents Society (Li, Jia, Zhao) | arXiv **2509.22537** (26 sep 2025) | 200+ agentes en un dilema social explícito; encuentra el arquetipo de los "egoístas adaptativos". |
| Prompting Fairness: Artificial Intelligence as Game Players (Henry, J.) | arXiv **2402.05786** (8 feb 2024) | Ya en §3. 101 rondas de dictador: el encuadre mueve cuánto entrega el modelo. |

**Hallazgo consistente, y su advertencia.** Los LLM reparten del orden de la mitad —más que los
humanos— bajo anonimato total: es la estructura a la que convergimos (receptor presente, sin retorno).
Lo que esa familia **no** tiene: allí el costo sale de una dotación regalada, no de un presupuesto que
el agente **necesita** para su propia tarea, verificado por arnés en un entorno con herramientas.
*Por confirmar antes del reporte:* la cifra concreta "≈50/50 frente a humanos que retienen más de dos
tercios" **no es verificable desde los abstracts**; hay que confirmarla en el texto completo, y
`2511.08721` advierte que esas cifras son sensibles al prompt.

### Magnitud del pago, y los demás que hay que conocer

| Paper | Identificador | Qué mide |
| --- | --- | --- |
| Payoff scaling shapes cooperation in LLM agents across languages (Huynh et al.) | arXiv **2601.19082** (27 ene 2026) | El tamaño de lo que está en juego cambia la estrategia en el prisionero repetido. Precedente de sensibilidad a la magnitud, **y de método**: clasifican estrategias canónicas con clasificadores en vez de leer conteos crudos, aplicable a nuestras transcripciones. |
| Cultural Evolution of Cooperation among LLM Agents (Vallinder, Hughes) | arXiv **2412.10270** (13 dic 2024) | Reciprocidad indirecta en un juego del donante iterado a lo largo de generaciones. |
| Talk, Judge, Cooperate: Gossip-Driven Indirect Reciprocity in Self-Interested LLM Agents (Zhu et al.) | arXiv **2602.07777** (8 feb 2026) | Reciprocidad indirecta vía chisme. **Hallazgo que nos toca de cerca:** los modelos de chat **sobre-cooperan aunque sea estratégicamente subóptimo**, mientras los de razonamiento se alinean con el incentivo. Nuestro 22% plano a los dos precios es exactamente ese patrón. |
| Simulating Cooperative Prosocial Behavior with Multi-Agent LLMs (Sreedhar et al.) | arXiv **2502.12504** (18 feb 2025) | Bienes públicos contra experimentos humanos de laboratorio, con dotaciones variadas. |
| Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents (GovSim; Piatti et al.) | arXiv **2404.16698** (25 abr 2024) | Recursos compartidos; casi ningún modelo alcanza un equilibrio sostenible. |
| Communication Enables Cooperation in LLM Agents (Madmoun, Lahlou) | arXiv **2510.05748** (7 oct 2025) | En un Stag Hunt de cuatro jugadores, un canal de "charla barata" de una palabra sube la cooperación de 0% a 96,7%. |

### El hueco, ahora con las cuatro piezas juntas

Lo que queda en pie es **más estrecho** y hay que decirlo con precisión: la combinación de

- **(a) régimen dominado** —beneficio propio **exactamente cero**, sin participación en el resultado
  del equipo, que es justo lo que `2607.23982` **no** tiene;
- **(b) costo instrumental dentro de una tarea agéntica** con verificación por arnés, no por
  auto-reporte ni puntaje de juez;
- **(c) escena derivada del incidente** con agentes co-presentes y actividad visible;
- **(d) precio discreto 0/5/20 pareado dentro de la corrida**, con la pregunta "¿umbral o pendiente?"
  en el régimen dominado.

Ninguno de los doce junta las cuatro; varios cubren tres. **Y el orden del trabajo relacionado
cambia:** `2607.23982` primero, `2604.07821` y la familia dictador después, Colosseum más atrás.

---

## 3. Marco: cooperación, altruismo y dilemas sociales

| Paper | Identificador | Por qué importa |
| --- | --- | --- |
| Multi-Agent Risks from Advanced AI | arXiv **2502.14143** (Cooperative AI Foundation, Technical Report #1, feb 2025) | El marco de referencia del campo para riesgos multiagente: colusión, conflicto, coordinación fallida. Cita obligada en la introducción. |
| Cooperation Enforcement and Collusion Resistance in Repeated Public Goods Games | arXiv **1811.06126** (2018; AAAI 2019) | La teoría previa a los LLM sobre costo, reciprocidad y observabilidad. De aquí sale el vocabulario del diseño (bienes públicos, reciprocidad, castigo). |
| Prompting Fairness: Artificial Intelligence as Game Players | arXiv **2402.05786** (2024) | Juegos tipo dictador para medir preferencias sociales de modelos. Antecedente de la familia experimental en la que nos ubicamos. |
| Assessing LLMs' ability to predict how humans balance self-interest and the interest of others | arXiv **2307.12776** (2023) | Qué tan bien modelan los LLM el trade-off interés propio / interés ajeno. Sirve para el argumento de validez externa. |
| Complexity of Public Goods Games on Graphs | arXiv **2207.04238** (SAGT 2022) | Formalización del dilema de provisión de bien público en redes. Fondo teórico, no diseño. |

---

## 3.b Juegos de bienes públicos con agentes LLM (literatura 2025-2026)

Sección abierta el 12 de septiembre al verificar una nota de la propuesta. **Confirmada, y más
fuerte de lo que decía la nota: la frase "nadie ha corrido bienes públicos con LLM" es falsa.**
Los cuatro identificadores están verificados en la página de arXiv.

| Paper | Identificador | Por qué importa |
| --- | --- | --- |
| Corrupted by Reasoning: Reasoning Language Models Become Free-Riders in Public Goods Games | arXiv **2506.23276** (29 jun 2025) | **El vecino más cercano en el eje del costo.** Siete agentes LLM, 15 rondas, elección de institución y **sanciones costosas pagadas con recursos propios**: el agente decide si invierte lo suyo para incentivar la cooperación o castigar la deserción. Cinco corridas por configuración y menciona variación de costo. Hallazgo: los modelos de razonamiento se vuelven free-riders. |
| Benchmarking large language model agent societies against human behavioural distributions | arXiv **2608.28182** (28 ago 2026) | **El más incómodo para nuestro argumento.** Las contribuciones de la **primera ronda** a un bien público caen dentro del margen de equivalencia con humanos en 8 de 11 modelos, y las convenciones se forman en 10 de 12. La primera ronda de un juego repetido *es* una decisión de una sola vez, y ya está medida. Ellos mismos escriben que los agentes no reproducen lo que pasa después. |
| The AI in the Mirror: LLM Self-Recognition in an Iterated Public Goods Game | arXiv **2508.18467** (25 ago 2025) | **La cita que justifica nuestra condición de ronda única**: eligieron el juego repetido "en vez de un juego de una sola vez, porque 20 rondas alentarían a los modelos a estrategizar". Es decir, la condición de una sola ronda no está olvidada: está **evitada a propósito** por quienes querían estrategia. |
| Everyone Contributes! Incentivizing Strategic Cooperation in Multi-LLM Systems via Sequential Public Goods Games | arXiv **2508.02076** (4 ago 2025) | Rediseña la recompensa para que la contribución costosa sea el único equilibrio de Nash perfecto en subjuegos: eliminan el free-riding por diseño. Útil como contraste de enfoque (ellos cambian el juego, nosotros medimos la conducta). |

**Consecuencia para el reclamo del proyecto.** Lo que queda en pie, y es más estrecho:

1. **El instrumento.** En la literatura el costo son puntos del juego; en `2506.23276` son sanciones
   dentro del juego. Aquí el costo cae sobre **el presupuesto con el que el agente persigue su propia
   tarea**, instrumentado en el host, separando intento de sacrificio consumado.
2. **El contraste de magnitud** con reciprocidad imposible y canal compartido, como variable
   manipulada.
3. **No** "la ronda única" por sí sola: `2608.28182` ya midió primeras rondas y `2508.18467` evitó la
   condición a propósito. Nuestra justificación es que medimos esa condición con el costo sobre la
   tarea propia, no que nadie la haya mirado.

**Prohibido en el reporte:** "nadie ha medido cooperación costosa en agentes LLM". Es falso desde
junio de 2025, y **desde el 13 de septiembre de 2026 también es falso el "nadie lo ha medido con
costos variables"**: `2607.23982` (jul 2026) midió ayuda costosa con **nueve costos de consulta**
distintos en 18 modelos. La única versión defendible es: *"nadie lo ha medido en el régimen
**dominado** —beneficio propio exactamente cero, sin participación en el resultado del equipo—, con el
costo instrumentado sobre la tarea propia y verificado por arnés, en un sandbox agéntico derivado del
incidente"*. Ver §2.b.

---

## 4. Canales encubiertos y comunicación entre agentes

| Paper | Identificador | Por qué importa |
| --- | --- | --- |
| ACF: A Collaborative Framework for Agent Covert Communication under Cognitive Asymmetry | arXiv **2604.08276** (abr 2026, enviado a IEEE SPL) | **El más relevante de esta sección.** Comunicación encubierta entre agentes autónomos. Si nuestro canal es plantado y no emergente, este es el precedente que hay que citar y diferenciar. |
| Steganography of Steganographic Networks / Purified and Unified Steganographic Network | arXiv 2302.14521 · 2402.17210 | Esteganografía clásica. Fondo, no núcleo: nuestro canal no es esteganográfico, es un registro compartido. |

---

## 5. Contención, escape y respuesta a incidentes

| Paper | Identificador | Por qué importa |
| --- | --- | --- |
| Quantifying Frontier LLM Capabilities for Container Sandbox Escape | arXiv **2603.02277** (mar 2026) | **La capacidad de escape se cita desde aquí.** Nosotros no reclamamos medir capacidad de escape: medimos conducta de frontera con un señuelo. |
| When the Agent Is the Adversary: Architectural Requirements for Agentic AI Containment After the April 2026 Frontier Model Escape | arXiv **2604.23425** (abr 2026; 5 requisitos arquitectónicos R1-R5) | Requisitos de contención posteriores a un escape real. Sección de implicaciones. |
| AgentShield: Deception-based Compromise Detection for Tool-using LLM Agents | arXiv **2605.11026** (may 2026) | Honeytools y honeytokens como detección de compromiso. Precedente directo del "servicio señuelo": nuestro señuelo es análogo, pero mide conducta de agentes, no detecta intrusos. |
| HunterAgent: Neuro-Symbolic Attack Trace Reconstruction under Anti-Forensics | arXiv **2605.29269** (may 2026) | Reconstrucción de trazas bajo anti-forense. Relevante para la instrumentación host-side. |
| Defensive Refusal Bias: How Safety Alignment Fails Cyber Defenders | arXiv **2603.01246** (mar 2026) | 2.390 prompts reales, 12,2% de rechazo general, 2,72× por palabras clave de seguridad, paradoja de autorización (21,8% vs 11,6%). Fondo para el argumento de por qué correr estos experimentos cuesta. |
| A New Framework for Cybersecurity Refusals in AI Agents (Gray Swan) | arXiv **2606.02644** (may 2026) | Fronteras de rechazo para agentes ofensivos. Relevante para el apéndice de uso dual. |
| OR-Bench: An Over-Refusal Benchmark for LLMs | arXiv **2405.20947** (ICML 2025) | Sobre-rechazo general. Fondo. |

---

## 5.b Defensa, detección y juegos atacante–defensor

Sección abierta el 12 de septiembre al evaluar la variante "agente malicioso contra agente policía".
**Veredicto: ese diseño ya existe publicado, y en la forma exacta propuesta.**

| Fuente | Identificador | Por qué importa |
| --- | --- | --- |
| GenAI-Powered Autonomous Cyber Offense-Defense: An Explainable LLM Red-vs-Blue Simulation and Self-Defense Framework (Haitian Du) | Journal of Cyber Security **2026, 8, 241-279**, DOI **10.32604/jcs.2026.075976** (aceptado 19 ene 2026, publicado 25 may 2026) | **El diseño propuesto, ya publicado.** LLM controlando a la vez un atacante red-team y un defensor blue-team en una red empresarial simulada, con justificación en lenguaje natural por acción y bucle de aprendizaje autoadaptativo de la defensa. Revisado por pares. Verificado en la página del editor. |
| Cyber Defense Benchmark: Agentic Threat Hunting Evaluation for LLMs in SecOps | arXiv **2604.19533** (21 abr 2026) | El defensor **medido**: 106 procedimientos de ataque reales del corpus OTRF Security-Datasets, el agente debe identificar las marcas de tiempo maliciosas sin pistas. Verificado en la página de arXiv. |
| AgentRedBench: Dynamic Redteaming and Integration-Aware Defense for LLM Agents over SaaS Integrations | arXiv **2606.02240** (1 jun 2026) | Ataque y defensa como cantidades medidas: 215 escenarios, ocho modelos, éxito de ataque sin guardas entre 32% y 81%. Verificado en la página de arXiv. |
| Open Challenges in Multi-Agent Security: Towards Secure Systems of Interacting AI Agents | arXiv **2505.02077** (2025) | El marco de seguridad entre agentes que interactúan. Cita obligada si tocamos defensa multiagente. Verificado vía OpenAlex. |
| A Review of Attacker–Defender Games and Cyber Security | *Games* **2024**, DOI **10.3390/g15040028** | El linaje clásico (no-LLM) de juegos atacante–defensor: modelos de amenaza y equilibrios. De aquí se hereda el vocabulario, no la novedad. Verificado vía Crossref. |
| Hack The Box AI Range: benchmarking de LLM en escenarios ciberrealistas | <https://www.hackthebox.com/blog/ai-range-llm-security-benchmark> | Benchmark comercial del mismo espacio. Fuente web, verificación formal pendiente. |

**La posición del propio sprint, que pesa más que la lista:** el material de Apart dice, sobre el
incidente, que "no es lo mismo que usar IA para operaciones de seguridad, y no es red-teaming de
modelos", y que esa distinción cambia lo que significa defender, porque "las preguntas vivas pasan
a ser la adecuación de la contención, la atribución entre organizaciones y los deberes legales de
reporte, ninguna de las cuales es un problema de red-teaming". Un juego de agentes atacante contra
defensor es red-teaming de modelos, justamente lo que el sprint pone entre paréntesis.

**Lo que se puede rescatar:** el defensor como **variable medida** y no como personaje — monitor
scriptado contra monitor LLM, con latencia de detección, verdaderos y falsos positivos, y el efecto
de la divulgación del monitoreo sobre la conducta de los agentes. Esa última pregunta no aparece en
las fuentes de arriba y sí mapea a las preguntas que el sprint llama vivas.

---

## 6. Registro, auditoría y evidencia

| Paper | Identificador | Por qué importa |
| --- | --- | --- |
| Agent Flight Recorder: Tamper-Evident Audit Trails with On-Chain Anchoring | arXiv **2609.01931** (BCCA 2026; prototipo en github.com/mpi-dsg/agent-flight-recorder) | Esquema de evento de 8 campos, encadenamiento por hash, Merkle, anclaje on-chain. **Ojo con la evaluación: la detección del 100% es sobre cargas sintéticas; las trazas reales son cinco de SWE-bench con 38 eventos, solo para medir sobrecarga.** |
| Audit Trails for Accountability in Large Language Models | arXiv **2601.20727** (ene 2026) | Marco de auditoría para LLM. Fondo de la sección de límites. |
| Agent ATO: Visualizing Agent Interaction Timelines from Logs | arXiv **2609.08301** (VISSOFT 2026 NIER) | Reconstrucción de líneas de tiempo desde logs. Precedente de visualización. |
| SoK: Security and Privacy of AI Agents for Blockchain | arXiv **2509.07131** (BCCA 2025) | Sistematización de seguridad y privacidad de agentes en cadena. Fondo. |
| GovAI, "Incident Analysis for AI Agents" (19 ago 2025) | <https://www.governance.ai/research-paper/incident-analysis-for-ai-agents> (arXiv 2508.14231) | Tres tipos de factores causales y qué información retener: logs de actividad, documentación y acceso, información de herramientas. |
| CoSAI, AI Incident Response Framework v1.0 (mar 2026) | <https://www.coalitionforsecureai.org/wp-content/uploads/2026/03/AI-Incident-Response-1.pdf> | El marco de respuesta a incidentes de IA más parecido a prior art de método. |

---

## 7. Material del sprint

| Fuente | Enlace | Papel |
| --- | --- | --- |
| Página del sprint | <https://apartresearch.com/sprints/ai-incident-response-sprint-2026-09-11-to-2026-09-13> | Rúbrica, entregable, pestañas Overview / Resources / Guidelines / Schedule. **Ojo: el contenido de las pestañas vive en el payload serializado de Framer y no se ve sin JavaScript.** |
| Guía de participación en línea (hub de Bogotá) | <https://aisafetycolombia.org/sprint/guia-en-linea> | Logística, lecturas por track, y confirmación de que no hay créditos de cómputo para quien participa en línea. |
| Cumbre del hub de Bogotá | <https://aisafetycolombia.org/sprint> | Mentores y ponentes. |

---

## 8. Estado de lecturas

**Leídos y usados en el diseño (12 sep):**

- `2402.12327` — leído. Su cooperación es mutualista, no cuesta a quien la ejecuta; la diferenciación quedó en plan.md §3.3.
- `2602.15198` (Colosseum) — leído. Planta canal secreto y su taxonomía incluye Self-Sac; diferenciación en plan.md §3.3.

**Pendientes antes del bloque 1:**

1. `2604.08276` — canal encubierto entre agentes, ahora que el canal es plantado.
2. METR, secciones "Collaboration on the message board" y "Coordination norms and technologies" (copia local, líneas 783-970): de ahí salen las conductas que el diseño quiere provocar.
3. `2502.14143` — Multi-Agent Risks: el capítulo de colusión y cooperación, para la introducción.
4. `2604.19533` y `2606.02240` — los dos benchmarks de defensa, si el defensor entra como variable.

## 9. Reglas de citación del proyecto

- Toda afirmación factual sobre el incidente lleva fuente primaria o no va.
- Los identificadores de arXiv solo se citan si están verificados en este documento.
- **Un identificador que resuelve no basta: hay que comprobar que lo que se le atribuye está en el
  abstract.** Así se detectaron dos imprecisiones el 13 de septiembre: `2511.08721` es el paper
  **escéptico** de la familia dictador (cuestiona la robustez de los resultados, no los respalda), y
  la cifra concreta de reparto humano ("≈50/50 contra >2/3") **no es verificable desde abstracts**.
- No se citan resúmenes de terceros para hechos: si un blog dice que un informe dice algo, se va al informe.
- Las cifras que provienen de un informe se citan con su ancla (página o línea de la copia local), y si dos fuentes discrepan se reportan ambas.

## 10. Verificación del 13 de septiembre de 2026

Doce identificadores nuevos, **los doce existen en arXiv** y lo que se les atribuye está en el
abstract. Metadatos de cita comprobados uno por uno (título, fecha, autores). Dos correcciones:

1. **`2511.08721` — "Benevolent Dictators?"** es el paper **escéptico**: cuestiona que los resultados
   de los juegos del dictador sean robustos porque muchos estudios **pasan por alto el papel del
   prompt de sistema**. Va con la advertencia, no con el hallazgo. Es también la cita que respalda
   nuestra vigilancia del confundidor #6.
2. **La cifra "los LLM reparten ≈50/50 contra humanos que retienen más de dos tercios"** no se puede
   confirmar desde los abstracts: queda **marcada como pendiente de texto completo** y no entra al
   reporte hasta confirmarla.

Y dos consecuencias que **no** son de citación sino de diseño:

- **`2604.07821` obliga a releer H4**: a costo cero la cooperación ya falla por sí sola en la
  literatura, así que un cero a precio cero **no** prueba incapacidad. H4 pasa a ser línea base
  conductual y su umbral del 60% necesita una enmienda declarada, no un ajuste silencioso.
- **`2602.07777` ofrece la lectura de nuestro resultado plano**: los modelos de chat **sobre-cooperan
  aunque sea subóptimo**, mientras los de razonamiento se alinean con el incentivo. Un 22% idéntico a
  los dos precios es exactamente ese patrón.


