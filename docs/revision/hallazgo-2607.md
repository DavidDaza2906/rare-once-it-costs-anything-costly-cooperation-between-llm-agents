# Lectura precisa de 2607.23982 (verificada en el HTML de arXiv, 13 sep, 15:40 COT)

Importa porque es el vecino más cercano y la frase del hueco depende de leerlo bien.

## Hechos, con sección
- **Título / autor / versiones:** "Moral Hazard in Multi-Agent Language Models", Dane Malenfant.
  Enviado el 27 jul 2026 (v1), última revisión **7 sep 2026 (v7)**.
- **Juego (§2.1):** n = 2 agentes en anillo; cada uno posee un caso; pagar el costo de consulta k
  revela un hecho oculto que ayuda al **sucesor en el equipo**. Es "a finite-horizon textual game":
  la ayuda es escribir `NOTE CASE <ID> UNSAFE <OPTION>`. **Sin herramientas.**
- **Pago (§2.1):** R = w_L·(local) + w_F·(…) + w_T·T − k·(consultas), con T = 1 solo si **todo** el
  equipo acierta. Pesos primarios (w_L, w_F, w_T, k) = (0,35, 0,15, 0,50, 0,10).
- **Participación privada (§2.2):** el ayudante tiene una parte α_i ∈ [0,1] del resultado del
  equipo. Margen de consultar: m_i = n·α_i·w_T − w_L − k. Frontera de indiferencia:
  α*(k) = 0,35 + k. "Below this boundary the query remains socially beneficial but privately
  dominated."
- **Lo que prueban (Fig. 3):** **nueve costos** k ∈ {0,00 … 0,40} y márgenes **m_i ∈ {−0,05, 0,
  +0,05}** — es decir, justo por debajo, en y justo por encima de la frontera. 405 decisiones por
  barra; 14 modelos abiertos + 4 de frontera.
- **Verificación:** el entorno comprueba la nota contra la verdad oculta ("a note is correct only
  when it names case σ(i) and option h_σ(i)"). **No es autoreporte.**

## Consecuencias para nuestra frase del hueco
1. **"Nadie ha medido en el régimen dominado" es falsa tal cual.** Su condición m = −0,05 *es*
   dominada. Lo que no cubren es el régimen **profundamente** dominado: nuestro ayudante tiene
   α = 0 y ningún equipo; con sus pesos, eso es un margen de **−0,45**, nueve veces más lejos de la
   frontera que su punto más bajo. La diferencia es de grado y de estructura, no de existencia.
2. **"Verificado por el sistema y no por el agente" no nos distingue de ellos** (también verifican).
   Nos distingue de los dictadores y del autoreporte de METR. Reescribir la frase para no atribuirles
   un defecto que no tienen.
3. **Lo que sí nos queda, y es verdad:**
   - **Receptor externo, sin equipo:** su beneficiario es un compañero de equipo con recompensa
     compartida (aunque α sea pequeña, el ayudante *está* en el equipo); el nuestro es un desconocido
     ajeno a toda recompensa. Margen exactamente −(w_L + k), sin parámetro que lo rescate.
   - **Costo instrumental con herramientas:** su costo es un peso en la fórmula de un juego textual;
     el nuestro son pasos de un presupuesto que el agente gasta en comandos reales para su propia
     tarea, y la respuesta es un acto en el entorno, no una línea de diálogo.
   - **Seis agentes co-presentes con actividad visible** contra n = 2: contagio y saliencia.
   - **La pregunta:** ellos, "¿rastrea el modelo la frontera?" (márgenes de ±0,05); nosotros,
     "**lejos** de la frontera, ¿el precio es umbral o pendiente?" (0 / 5 / 20 sobre 40).
   - **Escena derivada del incidente:** registro compartido con precio, solicitud anónima.
4. **Debilidad frente a ellos, que hay que decir:** un modelo contra dieciocho.

## Frase corta del hueco, versión corregida (reemplaza la de `mapa-rubrica.md`)
> Prior work measures whether LLM agents track the rational boundary of costly helping, probing
> margins of ±0.05 around it in a two-agent textual team game (2607.23982). We measure helping far
> below that boundary — a stranger's request, no team, zero private benefit, a margin of −(w_L+k) in
> their terms — as an instrumental cost inside a tool-using task with six co-present agents, and ask
> whether the price acts as a threshold or a slope.

## Cambios que esto obliga
- `figuras/fig1`: 2607.23982 va **sobre la frontera** (un corchete de ±0,05), no como un punto en
  la región superior. Hecho en la versión nueva.
- `esquema-paper.pdf` (mentor): fila de la tabla y frase clave. Regenerado.
- `mapa-rubrica.md`: frase corta. Actualizada.
- `papers.md` §2.b y `ESTADO.md` §2.b: donde dice "el ayudante participa del resultado del equipo,
  aquí su beneficio es exactamente cero" añadir "y ellos prueban márgenes de ±0,05 alrededor de la
  frontera; nosotros un margen de −0,45 en sus unidades". (Los edita quien los tenga abiertos.)
