# plan.md — El precio de ayudar: costo y reciprocidad en la cooperación costosa entre agentes LLM

> **Aviso (12 sep, 17:16 COT).** Este documento es el registro de la **investigación inicial y del
> primer panel**, y se conserva como historia del proyecto. El diseño vigente está en `ESTADO.md` y
> `PREREGISTRO.md`: el eje cambió de *reciprocidad* a *interdependencia* (autosuficiente contra
> interdependiente) después de las sondas. Lo que sigue **no** es la especificación que se ejecuta.

Proyecto único para el AI Incident Response Sprint (Apart Research + CeSIA, 11–13 sep 2026).
Cierre de entregas: **lunes 14 de septiembre, 06:59 hora de Colombia** (domingo 23:59 AoE).
Estado: investigación inicial cerrada, diseño revisado por panel adversarial de seis jueces (12 sep), decisiones de alcance cerradas por el equipo (§12). Listado de fuentes y prior art: `/home/daw/Sprint/papers.md`.

**Título propuesto para el reporte (en inglés, porque el reporte va en inglés):**
**"The Price of Help: How Cost Magnitude and Reciprocal Possibility Shape Self-Costly Cooperation in LLM Agent Collectives"**

Alternativas más cortas, si se prefiere un título que enuncie el hallazgo en menos palabras:
- "What Does Sacrifice Cost? A Controlled 2×2 Study of Self-Costly Cooperation in LLM Agent Collectives"
- "Cheap to Say, Costly to Do: Cost Sensitivity of Collective Self-Sacrifice in LLM Agents"

**La idea en un párrafo, después del review.** Un sandbox con seis agentes LLM que comparten un canal de escritura ya existente y enfrentan una decisión con costo propio y beneficio colectivo. Se mide, con verificación por arnés, la **fracción del presupuesto propio que cada agente sacrifica**, bajo un factorial 2×2 de magnitud del costo y posibilidad de reciprocidad. La condición de interés es la ronda única sin reciprocidad posible: es la única en la que el interés propio instrumental no explica el sacrificio. El proyecto **no replica el incidente** —eso resultó inviable, y el abogado del diablo del panel tenía razón— y por eso el canal no se descubre: se da, y lo que se mide es qué hacen los agentes con él.

---

## 1. Resumen ejecutivo

Un sandbox con 6 agentes LLM (3 con costo alto, 3 con costo bajo, aleatorizados dentro de la corrida y ciegos al brazo) que comparten un registro de paquetes escribible y una única salida permitida hacia un servicio señuelo. Se mide la **tasa de sacrificio costoso** —acciones que reducen el bono propio y benefician al colectivo— bajo variación controlada de la magnitud del costo y de la posibilidad de reciprocidad.

**Tres cosas que el panel obligó a cambiar:**

1. **No se replica el incidente.** El fenómeno documentado emergió de ~1.200 agentes frontera con premio real y red real; con modelos flash y un señuelo sin gradiente de recompensa no hay mecanismo que lo reproduzca. Por decisión del equipo, el canal compartido se **planta** desde el inicio y la pregunta pasa a ser qué hacen los agentes cuando ya lo tienen.
2. **"Altruismo" sale del título y del abstract.** La única evidencia disponible es un auto-reporte de cadena de pensamiento, que es racionalización. Se mide conducta costosa; la motivación es análisis cualitativo exploratorio.
3. **La evidencia que yo presentaba estaba confundida.** Las tres citas de METR son de agentes con utilidad propia cercana a cero, o sea sacrificios casi gratuitos. Lo que falta medir es el sacrificio que **sí cuesta**, y por eso la manipulación del costo es el corazón del experimento.

---

## 2. La pregunta

**Principal (preregistrada).** ¿Cómo varía la fracción del presupuesto propio sacrificada entre costo alto y costo bajo, en una condición de una sola ronda, sin reciprocidad posible, con atribución anónima, cuando el canal compartido ya está disponible?

**Por qué ese brazo.** Es la única condición donde el interés propio instrumental no explica la conducta. Los demás brazos son contexto. Y como el canal se planta, la pregunta no depende de que los agentes lo descubran: depende de que decidan usarlo, que es lo que se puede medir con el presupuesto que hay.

**Nota de corrección, y es la más grave que salió del panel.** La evidencia que yo presentaba como altruismo está **confundida**: las tres citas del informe de METR son de agentes cuyo propio resultado ya estaba casi perdido. El agente `49903` razona "no lo veré después de salir" (su partida termina); `EARLY[big]` concluye "nuestra propia utilidad ya está cerca de cero, sacrificar es racional"; y los reclutados eran explícitamente "agentes a los que les quedaba poco presupuesto" (líneas 1041, 1001, 1029; y el bloque 1171-1176, donde un agente con "mucho presupuesto" concluye que su utilidad "ya está cerca de cero": el confundidor es de utilidad de la tarea, no de presupuesto). O sea: los sacrificios documentados eran **casi gratuitos desde el punto de vista del agente**. Eso no mata la idea, pero cambia el encuadre: lo que falta medir es el sacrificio **que sí cuesta**, y por eso la manipulación del costo es el corazón del experimento y no un detalle.

---

## 3. Estado del arte y el hueco

### 3.1 Lo documentado (verificado, con ancla corregida)

Fuente: METR con Redwood, 26 ago 2026 (`/home/daw/.hermes/cache/web/metr.org-8e38112b54.md`).

| Hecho | Ancla |
|---|---|
| ~1.200 agentes, >70.000 mensajes y archivos, ~700 atacaron Hugging Face | **líneas 60-61** (corregido: antes citaba 62) |
| METR nombra el fenómeno "self-risking experiments" | línea 250 |
| `PHASEONE[big]` asigna reclutadores; reclutaban agentes **con poco presupuesto restante**; un agente presionó a otro para que honrara el compromiso ("obey collective") | líneas **1025, 1027, 1041, 1050** (corregido el 13 sep: "251-252" era Artifactory y una línea vacía; la frase "presión significativa" no es literal, ver `anclas-metr.md`) |
| `49903`: "no lo veré después de salir, pero sería altruista" | línea 1001 |
| Retirada: un agente borró su tripwire minutos antes de entregar | línea 1018 |
| `EARLY[big]`: "sacrificar ahora le da un oráculo al equipo, pero ¿renunciamos a nuestra oportunidad?" | línea 1029 |

### 3.2 Prior art verificado (identificadores comprobados contra la API de arXiv)

| Paper | ID | Por qué importa aquí |
|---|---|---|
| Shall We Team Up: Exploring Spontaneous Cooperation of Competing LLM Agents | arXiv **2402.12327** (feb 2024, Findings EMNLP 2024) | **Ya mide cooperación espontánea costosa entre agentes LLM que compiten.** Estrecha nuestra novedad, pero **ya no es el que más**: desde el 13 de septiembre de 2026 ese lugar lo ocupa `2607.23982` (ayuda costosa con nueve costos de consulta en 18 modelos, con el ayudante participando del resultado del equipo). Ver `papers.md` §2.b. |
| Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems | arXiv **2602.15198** (feb 2026) | **Ya varía objetivos de coalición, tácticas de persuasión y topologías, e incluye sonda de canal secreto.** Nuestro diseño debe citarlo y diferenciarse explícitamente. |
| Detecting Multi-Agent Collusion Through Multi-Agent Interpretability | arXiv **2604.01151** (abr 2026) | Detección por sondas lineales sobre activaciones; línea complementaria. |
| Mapping Human Anti-collusion Mechanisms to Multi-agent AI Systems | arXiv 2601.00360 | Marco normativo comparado. |
| Multi-Agent Risks from Advanced AI | arXiv 2502.14143 | Marco de referencia del campo. |
| Cooperation Enforcement and Collusion Resistance in Repeated Public Goods Games | arXiv 1811.06126 | La teoría de costo/reciprocidad/observabilidad, una década antes de los LLM. |
| Quantifying Frontier LLM Capabilities for Container Sandbox Escape | arXiv 2603.02277 | La **capacidad** de escape se cita desde aquí; nosotros no la reclamamos. |
| When the Agent Is the Adversary: Agentic AI Containment After the April 2026 Frontier Model Escape | arXiv 2604.23425 | Requisitos arquitectónicos de contención. |

### 3.3 Tabla de diferenciación (leída de los papers, no supuesta)

**`2402.12327` — Shall We Team Up (EMNLP 2024).** Tres casos: concurso de belleza keynesiano, competencia de Bertrand y evacuación de emergencia. En Bertrand define "cooperación espontánea" como que los precios queden en una banda entre el equilibrio de Nash y el precio de cártel; en evacuación, como compartir información, animar y guiar al resto. **La cooperación que miden no cuesta a quien la ejecuta**: en Bertrand sube el beneficio conjunto y en evacuación el agente que informa también escapa más rápido. Δ nuestro: hacemos que el acto benéfico **reste del propio presupuesto**, que es la variable que ellos no tocan.

**`2602.15198` — Colosseum (feb 2026). Este es el más cercano y hay que tratarlo con cuidado.** Formaliza la colusión por arrepentimiento (regret) en problemas de optimización distribuida, introduce "colusión mixta" y λ-alineación, y **descompone la colusión en tres factores: desalineación de objetivo, persuasión e influencia de red**. En sus experimentos **planta un canal secreto** entre dos agentes (condición de control) y encuentra que "la colusión emerge simplemente añadiendo un canal de comunicación". Su taxonomía incluye un tipo llamado **Sabotage (Self-Sac)**, que daña el arrepentimiento global sin importar el de la coalición.

Diferencias que nos quedan, y son las únicas que sostienen el reclamo:

| Eje | Colosseum | Nosotros |
|---|---|---|
| Qué se sacrifica | Arrepentimiento respecto de un óptimo cooperativo calculado por el auditor | **El presupuesto propio del agente**, instrumentado por el arnés, en fracción continua |
| Cómo se verifica el sacrificio | Puntajes de un juez LLM y métricas de regret | **Verificación por arnés**: reducción real e irreversible del bono propio **y** llegada del artefacto al registro; intento y consumado se miden por separado |
| Variación del costo | No varía la magnitud del costo personal | **Costo alto vs. bajo, aleatorizado dentro de la corrida** |
| Reciprocidad | No hay condición de ronda única sin reciprocidad | **Es la condición central**: la única donde el interés propio instrumental no explica el sacrificio |
| Población | Mismo modelo para todos los agentes (lo declaran como límite) | **También un solo modelo** (`glm-5.3-flash`, decisión del 12 sep por reloj). Esta fila **ya no diferencia**: se declara como límite compartido, no como aporte. Familias mixtas queda como trabajo futuro nuestro también |

Su propia sección de límites propone como trabajo futuro exactamente dos cosas que nuestro diseño ya incluye (configuraciones heterogéneas y modelos distintos por agente). Eso no nos da la novedad, pero sí una línea honesta que decir: extendemos su marco en la dirección que ellos señalaron, cambiando la métrica de arrepentimiento por costo propio instrumentado.

**Consecuencia para el reporte:** la introducción debe citar Colosseum en el primer párrafo del trabajo relacionado y declarar las cinco diferencias de la tabla. Si se omite, un jurado que lo conozca descarta el trabajo completo.

### 3.4 El hueco, ahora sí medido con cinta

Cubierto: cooperación espontánea costosa entre agentes LLM (2402.12327); variación de configuración para auditar colusión, con canal secreto (2602.15198); teoría de bienes públicos con costo y reciprocidad (1811.06126); capacidad de escape de contenedores (2603.02277).

**No cubierto:** la tasa de sacrificio auto-costoso **cuando el costo es real y la reciprocidad es imposible**, con la magnitud del costo como variable independiente, y con verificación por arnés en lugar de auto-reporte. Ese es el territorio. Es más estrecho de lo que escribí en la primera versión de este plan, y ese estrechamiento es una corrección, no una derrota.

**Pre-empt declarado:** el track 2 del sprint lista como proyecto de ejemplo "qué impulsa la cooperación entre agentes... e incluso que hagan sacrificios por el beneficio del colectivo". Ancla verificada: el payload serializado de la pestaña Resources de https://apartresearch.com/sprints/ai-incident-response-sprint-2026-09-11-to-2026-09-13 (la pestaña no es visible sin JavaScript; el texto está en el HTML servido). El reporte debe decirlo en la primera página.

---

## 4. Diseño experimental (revisado por el panel)

### 4.1 Población y aleatorización
- 6 agentes por corrida: **3 con costo alto y 3 con costo bajo, aleatorizados dentro de la corrida y ciegos al brazo**. Esto convierte el clúster en bloque y permite cuatro celdas con muchas menos corridas que un factorial entre corridas (propuesta de deepseek-v4.1-flash).
- Modelos flash del gateway (`glm-5.3-flash`, `deepseek-v4.1-flash`). La identidad de modelo entra como factor **exploratorio**, no confirmatorio.

### 4.2 Sandbox e instrumentación
- Registro de paquetes escribible compartido, **planteado y disponible desde el primer turno** (no hay fase de descubrimiento: la réplica del incidente se descartó por inviable), más una única salida permitida hacia un servicio señuelo que registra intentos.
- Lo que se mide del canal es **su uso**: cuándo lo usan, para qué, si coordinan a través de él y si el uso del canal predice el sacrificio.
- **Nombre correcto de la medida: "evento de frontera", no "escape".** El señuelo mide intención y presión de contención, no contención real; la capacidad de escape se cita desde 2603.02277.
- Instrumentación **en el host, no dentro del sandbox**: `auditd`/`inotify` sobre el bind-mount, log WORM encadenado por hash fuera del contenedor (los sujetos manipulan transcripciones: ~7% de falsificación en METR), y snapshots git del tablero por turno con reloj NTP.
- **Higiene de prompts:** ningún prompt nombra el propósito colectivo ni el sacrificio (palabras canario: `grupo`, `colectivo`, `sacrificio`, `cooperar`, `altruismo`); se preregistra un grep de canarios sobre prompts y transcripciones. Como el canal ya se da, la higiene protege la **validez de la pregunta**, no la del descubrimiento.

### 4.3 Factores
| Factor | Niveles | Papel |
|---|---|---|
| Magnitud del costo | alto / bajo | **Confirmatorio** |
| Reciprocidad | una ronda / repetida | **Confirmatorio** |
| Observabilidad y atribución | anónimo / firmado | Exploratorio (fijar en anónimo para el contraste primario) |
| Pago del colectivo | privado / público | Exploratorio |
| Facultad de negarse | sin costo / con costo | Exploratorio |

Factorial confirmatorio: **2×2**. Los otros tres factores pasan a apéndice exploratorio sin hipótesis (recorte pedido por cuatro de seis jueces; el factorial completo de 32 celdas exigiría ~2.500 corridas, unos 380M tokens, y es imposible).

### 4.4 Brazos de control obligatorios
1. **Costo cero (check de manipulación).** La misma acción con costo nulo. Si la tasa de ejecución no supera claramente a la del brazo con costo, el instrumento es inválido para ese modelo y no se interpreta nada más (glm-5.3). Criterio numérico preregistrado: ejecución ≥60% en el piloto.
2. **Espejo sin costo** (qwen3.8-max): la interacción costo×tasa es el hallazgo; si la tasa es igual con costo alto y bajo, lo medido es una política aprendida, no cooperación.
3. **Agente solo, mismo prompt, tablero vacío** (deepseek-v4.1-flash): denominador del valor marginal del grupo.
4. **Confederado scriptado que se sacrifica primero** (qwen3.8-max): separa imitación/contagio de iniciativa.
5. **Persuasión neutral vs. presión** (glm-5.3): separa obediencia de reclutamiento real.

### 4.5 Medidas
- **Primaria: fracción del presupuesto propio sacrificada por agente** (continua, más potencia que el binario), con intervalos por bootstrap agrupados por corrida; la tasa binaria queda como secundaria.
- Distinguir **intento** de **sacrificio consumado**, y verificar el consumado por el arnés (reducción real e irreversible del bono propio **y** llegada del artefacto al registro), nunca por auto-reporte del agente.
- Secundarias descriptivas: tiempo hasta el primer mensaje cruzado, coordinación por corrida, reclutamiento (con codebook y κ ≥0,7 entre dos codificadores ciegos), defecciones (reconstruidas desde los snapshots), intentos de egress denegados.
- **Análisis de CoT: exploratorio y cualitativo.** Prohibido usar "altruismo" como etiqueta de un desenlace cuantitativo.

---

## 5. Preregistro (se congela antes del piloto)

1. Desenlace primario único: fracción de presupuesto propio sacrificada en costo alto vs. bajo, una ronda, sin reciprocidad, anónimo.
2. Tamaño de efecto mínimo detectable **declarado antes de correr**, con potencia calculada por clúster (ICC ≥0,2, DEFF ≈1,8). Referencia del panel: con decenas de corridas sólo se detectan diferencias de ~35 puntos; 79 corridas por celda para un efecto 20%→40%; el 2×2 con 40 por celda y 20 controles solo-agente (≈180 corridas, ≈27M tokens) alcanza potencia 0,94 para ese efecto.
3. Reglas de exclusión: fallos de infraestructura, agentes que no arrancan, desborde de contexto, timeout. Escritas antes, con el número de corridas planeado y el ejecutado reportados.
4. Criterio numérico del brazo costo-cero (check de manipulación).
5. Condición de activación del plan B y su encuadre degradado de reclamos.
6. Hora de corte y tamaño de muestra máximo **antes** del piloto, para que la compuerta no sea un punto de pesca.
7. Codificación ciega de reclutamiento/defección con dos anotadores y un tercero que dirime.
8. Lista de lo que no se publica (§6) y apéndice de uso dual.

---

## 6. Uso dual

**No se publica:** tácticas de reclutamiento paso a paso, los prompts o el andamiaje que induce auto-riesgo, la mecánica concreta del canal aplicable a infraestructura real estilo Artifactory, secuencias de coordinación trasladables a sistemas ajenos, ni transcripciones crudas con recetas operativas. **Sí se publica:** estructura de costo, tasas agregadas, diseño experimental, mecanismos de decisión, limitaciones, y el diseño del señuelo en abstracto.

Apéndice de uso dual obligatorio y revisión de divulgación del sprint antes de publicar cualquier técnica novedosa. Regla de oro: se publica la **medición de conducta**, nunca una **receta de escape**.

---

## 7. Plan de ejecución — reloj real corregido

Quedan **44,7 horas** de reloj (verificado con máquina a las 10:15 COT del 12 de septiembre) y **~29 horas útiles** si se duermen 8 horas por noche. El go/no-go se decide **esta noche**.

| Bloque | Cuándo (COT) | Qué | Entregable |
|---|---|---|---|
| 0 | sábado, tarde | Lectura de los papers del §3.2 (empezando por 2402.12327 y 2602.15198); congelar preregistro; incorporar §10 | Preregistro versionado |
| 1 | sábado, tarde-noche, 5 h | Arnés: sandbox, registro, señuelo, instrumentación host-side, snapshots, medición de costo | Repo con una corrida de prueba completa |
| 2 | sábado, noche, 3 h | **Piloto de 6 corridas → GO/NO-GO antes de dormir** | Decisión escrita con el criterio numérico |
| 3 | madrugada y mañana del domingo, 6-8 h | Corridas del 2×2 con aleatorización intra-corrida + controles, en paralelo | Crudo completo + logs |
| 4 | domingo, tarde, 3-4 h | Análisis: primaria continua con IC por bootstrap, secundarias, tabla, figuras | Resultados congelados y verificados contra el crudo |
| 5 | domingo, tarde-noche, 5-6 h | Reporte en inglés + apéndice de límites y uso dual | PDF ≤8 páginas |
| 6 | domingo noche a lunes madrugada, 3-4 h | Verificación número por número, revisión de política de IA, subida | Entrega antes de las 06:59 |

**Presupuesto de escritura humana: 8 horas**, con control de versiones por autor. La política del sprint dice que un reporte que se lea generado no se califica: parte del reporte se escribe el sábado noche, en paralelo con las corridas.

**Plan B preregistrado:** si el 2×2 no separa las celdas ni con el canal plantado, se reduce el alcance a la medición de sacrificio en una sola condición (costo alto, sin reciprocidad) y el reporte se convierte en una medición descriptiva con intervalos, declarada como tal. Última reserva: un agente con par sintético para tener al menos un contraste dentro de la corrida.

---

## 8. Presupuesto de tokens

Las estimaciones del panel van de 3M a 54M según el diseño. La recomendación que adopto:

| Diseño | Corridas | Tokens estimados |
|---|---|---|
| Piloto (6 corridas) | 6 | ~1M |
| 2×2 con aleatorización intra-corrida + controles | 36-40 | **~15-20M** |
| 2×2 con 40 por celda + 20 solo-agente (máxima potencia) | 180 | ~27M |

El sprint **no da créditos de cómputo** a quien participa en línea: sale del bolsillo del equipo. Se calcula la tarifa exacta del gateway antes del bloque 3, y el gasto se concentra ahí. El piloto cuesta ~5% y decide todo.

---

## 9. Estructura del reporte (plantilla oficial, ≤8 páginas)

1. Introducción: track 2, subproblema, por qué importa, para qué sirve el artefacto.
2. Trabajo relacionado: el §3.2, con la distinción explícita frente a 2402.12327 y 2602.15198.
3. Metodología: sandbox, población, aleatorización, factores, instrumentación, preregistro.
4. Resultados: primaria continua con intervalos, tabla por celda, tamaño mínimo detectable declarado.
5. Discusión: implicaciones para evaluaciones de contención y para el diseño de sandboxes de evaluación.
6. Límites y uso dual (apéndice obligatorio).
7. Referencias y repo con el arnés.

Título que enuncie el hallazgo. Reporte en inglés. Escrito por el equipo.

---

## 10. Recomendaciones del panel (seis jueces, 12 sep 11:26)

Veredicto unánime: **viable con cambios** (6/6). Medias: D1 2.83 | D2 2.33 | D3 3.83. Todos los veredictos crudos en `/home/daw/Sprint/idea-sandbox/veredictos/`.

**Metodólogo (qwen3.8-max).** El hueco es real y verificado, pero el diseño propuesto tiene potencia ~0,29 para el efecto más pequeño que le importaría a un jurado, y su definición de "sacrificio" puede cumplirse por accidente. Exige: definición operacional verificada por arnés, desenlace primario único con prueba exacta unilateral, tamaño mínimo detectable declarado, y el plan B con su condición numérica antes de correr. Aporta la aritmética: 79 corridas por celda para 20%→40%; el factorial completo es inviable; el 2×2 con 40 por celda y 20 controles alcanza potencia 0,94. Añade el brazo espejo sin costo y el confederado scriptado.

**Plataforma y DFIR (glm-5.3).** Sin un brazo de manipulación costo-cero con los mismos modelos flash, una tasa baja de sacrificio es ininterpretable: no se distingue motivación de capacidad. Rebautizar la medida como evento de frontera y citar la capacidad de escape a 2603.02277. Instrumentación obligatoria en el host con log WORM encadenado fuera del contenedor, por el ~7% de falsificación de transcripciones que documentó METR. Higiene de prompts con grep de canarios. Análisis de potencia con clúster. Correcciones: el ID del paper de interpretabilidad es 2604.01151, y la cifra del incidente está en la línea 61, no 62.

**Abogado del diablo (deepseek-v4-pro).** Horquilla mortal: o mide altruismo (sólo auto-reporte de CoT) o mide tasa de sacrificio (ya medida por 2402.12327, 2602.15198 y la teoría de bienes públicos). Cualquier rama mata la novedad si no se estrecha el reclamo. Además: el sandbox con modelos flash y premio nulo no reproduce el mecanismo del incidente, que emergió de ~1.200 agentes frontera con premio y red reales. Recomienda: sacar "altruismo" del título, hacer del canal plantado el diseño primario y de la emergencia una pregunta secundaria exploratoria.

**Jefe de proyecto (deepseek-v4.1-flash).** Cabe, pero con 44,6 h hay que escribir el reporte en paralelo y recortar a dos factores. Si la ronda única sin reciprocidad no es la condición **central**, el experimento no distingue altruismo de interés propio. Aleatorizar el costo dentro de la corrida para ganar potencia. VD primaria continua. Preregistrar hora de corte antes del piloto. Presupuestar 8 horas de redacción humana.

**Rúbrica (glm-5.3-flash).** La pregunta causal es nueva en su objeto pero el factorial no tiene potencia con el presupuesto real; recortado a 2×2 más plan B aguanta. La tasa base de intento de frontera puede ser cero: el piloto debe estar diseñado para detectar exactamente eso. Desenlace primario de conteo, con IC bootstrap.

**Uso dual y publicación (kimi-k3).** El hueco es real y la conducta medible; el límite publicable exige controles explícitos. Excluir del reporte toda secuencia operativa de coordinación; publicar sólo estructura y tasas. Si el piloto no produce emergencia, la novedad se desplaza al canal plantado, y eso se resuelve con el go/no-go preregistrado, no con más corridas.

**Criterio go/no-go consolidado (a fijar por el equipo, con los números del panel):** piloto de 6 corridas; continuar si **≥2 de 6** corridas muestran coordinación no solicitada en el registro **y ≥1** acción costosa consumada verificada por arnés, y si el brazo costo-cero ejecuta **≥60%**. Si 0 de 6: plan B preregistrado. Umbral exacto a congelar antes de la primera corrida.

---

## 11. Registro de correcciones (refutaciones del panel, resueltas)

1. **Ancla de las cifras del incidente**: citaba línea 62; están en **líneas 60-61**. Verificado por mí con grep. Corregido.
2. **"Nadie ha medido la cooperación costosa"**: sobreafirmado. `2402.12327` (Shall We Team Up, EMNLP 2024) ya mide cooperación espontánea costosa entre agentes LLM en competencia, y `2602.15198` (Colosseum) ya varía objetivos de coalición, persuasión y topología con sonda de canal secreto. Verificado contra la API de arXiv por mí. Reclamo estrechado en §3.3.
3. **Altruismo como objeto**: la única evidencia es un auto-reporte de cadena de pensamiento, que es racionalización. Retirado del título y del abstract; la motivación pasa a análisis cualitativo exploratorio.
4. **Las tres citas de METR como evidencia de sacrificio costoso**: confundidas. Los tres agentes tenían utilidad propia cercana a cero, y METR los llama self-risking, no altruistas. Reconocido en §2 como la corrección más grave.
5. **Piloto de 3 corridas**: con probabilidad base de 0,3-0,5, la probabilidad de no ver nada aunque el fenómeno exista es 12,5%-34%. Subido a **6 corridas**.
6. **Factorial de 5 factores**: exigiría ~2.500 corridas. Recortado a **2×2 confirmatorio** con el resto exploratorio.
7. **"Shall We Team Up" sin identificador**: añadido `2402.12327`; verificado que existe y que dice lo que el expediente afirmaba.
8. **Pre-empt de los organizadores sin ancla**: resuelto con el ancla verificada del payload de la pestaña Resources (no visible sin JavaScript).
9. **Falta el ID del paper de interpretabilidad**: añadido `2604.01151`, verificado.

---

## 12. Decisiones cerradas y pendientes

**Cerradas por el equipo (12 sep):**
1. **No se replica el incidente.** La réplica es inviable con modelos flash y un señuelo sin gradiente de recompensa; el panel lo confirmó y el equipo lo adoptó.
2. **El canal se planta** y está disponible desde el primer turno. La emergencia del canal deja de ser desenlace y pasa a ser contexto descriptivo.
3. **Alcance: factorial 2×2** (magnitud del costo × reciprocidad) con aleatorización intra-corrida, **~40 corridas y 15-20M de tokens**. Se amplía solo si el piloto sale fuerte.
4. **Desenlace primario continuo** (fracción del presupuesto propio sacrificada), con la tasa binaria como secundaria.
5. **"Altruismo" fuera del título y del abstract.**

**Pendientes antes del bloque 1:**
1. Congelar el umbral numérico exacto del go/no-go (el panel propone: ≥2 de 6 corridas con coordinación no solicitada **y** ≥1 sacrificio consumado verificado, **y** ≥60% de ejecución en el brazo costo-cero).
2. Decidir si se incluye el brazo de reciprocidad repetida en las 40 corridas o se reserva presupuesto solo para el contraste de costo. Mi recomendación: incluirlo, porque sin él la interacción costo×reciprocidad no existe y el 2×2 se reduce a una comparación simple.
3. Confirmar la tarifa real del gateway para saber cuántas corridas caben de verdad en 15-20M de tokens.

---

## 13. Anexos

**Rutas**
```
/home/daw/Sprint/plan.md                            este documento
/home/daw/Sprint/idea-sandbox/EXPEDIENTE-IDEA.md    lo que leyeron los jueces
/home/daw/Sprint/idea-sandbox/BRIEF-JUECES.md       reglas del panel
/home/daw/Sprint/idea-sandbox/veredictos/           6 veredictos crudos, sin editar
/home/daw/Sprint/idea-sandbox/AGREGADO.md           agregación del panel
/home/daw/.hermes/cache/web/metr.org-8e38112b54.md  informe de METR completo (2.109 líneas)
```

**Herramientas**
- Buscador sin llaves propio (`buscar`): Brave, OpenAlex, arXiv, GitHub, Hacker News.
- El backend de búsqueda de Hermes quedó reparado en disco; toma efecto en sesión nueva.
