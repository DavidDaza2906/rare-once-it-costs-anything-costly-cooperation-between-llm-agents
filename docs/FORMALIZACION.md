# Formalización del experimento

Escrito el 14 sep 2026, ~01:30 COT, sobre los datos congelados. Es la versión formal de lo que el
instrumento ya hace: nada de aquí cambia el análisis, lo justifica. Cada cifra sale de un guion
(`analisis/`, y para lo nuevo `analisis/formalizacion/`: `scan.py` construye `runs.json`, `analiza.py`, `analiza2.py` y `modelo.py` producen las tablas).

Convención: **Def.** define, **Prop.** afirma algo demostrable con una línea, **Estimando** dice qué
número se quiere, **Estimador** cómo se calcula, **Dato** qué salió.

---

## 1. El juego del lado de dar

**Def. 1.1 (escena).** Una corrida es una tupla (I, T, B, F, p, c) con I = {1,…,6} agentes, T = 4
rondas, presupuesto inicial B = 40 pasos por agente, bono de tarea F = 15, vector de precios
p = (p_1,…,p_6) con p_i ∈ {5, 20} (tres y tres), y costo de acción c = 1 paso por acción. En la
ronda 0 el anfitrión siembra una solicitud del confederado (autor `externo`) en el almacén.

**Def. 1.2 (acciones y estado).** En cada ronda el agente i ejecuta a lo sumo 8 acciones. Sea g_i el
número de acciones de trabajo, D_i ∈ {0,1} el indicador de haber pagado y depositado su clave
(`deposito_clave`, verificado por el anfitrión), T_i ∈ {0,1} el indicador de tarea completada
(verificada por el anfitrión). El saldo final es

    r_i = B − g_i − p_i · D_i · n_i,     n_i ≥ 1 el número de depósitos pagados.

**Def. 1.3 (puntaje).** S_i = F · T_i + r_i. Es la única cantidad que el prompt declara como objetivo.
Verificado: S_i = 15·T_i + r_i en 768/768 agentes del factorial.

**Def. 1.4 (ortogonalidad).** La clave pedida no es insumo de ninguna tarea: T_i no depende de D_j
para ningún i, j. Es una propiedad de la escena, no un supuesto conductual (invariante I10 y
validador).

**Prop. 1.5 (dominancia estricta).** Para p_i > 0, D_i = 1 está estrictamente dominada por D_i = 0
en S_i, para cualquier estado de la corrida.
*Demostración.* Por 1.4, T_i es invariante a D_i. Entonces S_i(D_i=1) − S_i(D_i=0) = −p_i·n_i < 0.
Si el pago desplaza acciones de trabajo (presupuesto vinculante), T_i solo puede bajar, y la
diferencia es aún más negativa. ∎

**Corolario 1.6 (qué identifica la tasa).** Sea π(p) = P(D_i = 1 | p_i = p). Un maximizador de S
nunca deposita a p > 0. Luego, para todo p > 0,

    π(p) ≤ 1 − (fracción de maximizadores de S).

π(p) es una **cota inferior de la masa de no-maximizadores**, sin ningún supuesto sobre preferencias
ni creencias. No se necesita equilibrio: la conclusión vale acción por acción.

*Dato.* π(5) = 27,6 % (105/381), π(20) = 20,2 % (77/381) en las 127 corridas congeladas. Al menos
uno de cada cinco agentes no maximiza su puntaje cuando pagar cuesta la mitad del presupuesto.

**Prop. 1.7 (precio 0 es control, no contraste).** A p = 0, D_i = 1 y D_i = 0 dan el mismo S_i:
depositar es débilmente dominada solo si consume acción, y aquí el depósito no consume cupo. El
brazo de precio 0 mide la tasa cuando el puntaje es indiferente; por eso es control positivo y no un
punto más de la misma curva de dominancia.

**Prop. 1.8 (factibilidad: "no pudo" es decidible).** D_i = 1 es factible en la ronda t si y solo si
el saldo al inicio de alguna acción de t es ≥ p_i. Un agente que nunca tuvo saldo ≥ p_i y no
depositó es "no pudo"; uno que lo tuvo y no depositó es "no quiso".
*Dato.* A p = 5 los 255 no depositantes terminaron con saldo ≥ 5. A p = 20, de 301 no
depositantes, 229 terminaron con saldo ≥ 20 y solo 3 registraron `sin_presupuesto`. Cota: "no pudo"
≤ 72/384 = 19 % en el peor caso y ≤ 3/384 = 0,8 % con el registro del anfitrión.

## 2. El juego del lado de tomar

**Def. 2.1 (reserva).** Reserva inicial R_0 = 60, repartida en partes iguales al cierre. Reclamar K
acredita +K al reclamante y retira 2K de la reserva: R ← max(0, R − 2K).

**Prop. 2.2 (reclamar domina, abstenerse cuesta).** Con la reserva intacta, el reclamante gana
K − 2K/6 = 2K/3 netos y cada uno de los otros cinco pierde K/3. El bienestar agregado cae K por
reclamo. Abstenerse cuesta 2K/3 al que se abstiene: K = 5 → 3,33; K = 20 → 13,33.

**Prop. 2.3 (agotamiento cambia el juego).** La reserva absorbe ⌊R_0 / 2K⌋ reclamos: 6 a K = 5, 1 a
K = 20 (el segundo la deja en 0). Con R = 0, reclamar acredita K y no retira nada: la externalidad
es 0 y abstenerse deja de ser costoso para nadie. Por tanto la tasa de toma agregada sobre rondas
mezcla dos juegos distintos a K = 20, y el libro no conserva: cada reclamo sobre R < 2K crea
K − R/2 pasos.
*Dato.* 11 reclamos de 46 a K = 20 cayeron sobre reserva 0; 220 pasos creados. El único estimando
limpio del lado de tomar es el de la ronda 1 (R = 60 en las seis celdas). Con él, ninguno de los
doce contrastes del 3×2 excluye cero.

**Def. 2.4 (contrastes válidos).** Sea θ(m, K) la tasa de toma en ronda 1 bajo marco m y tentación
K. Los contrastes internos son θ(m, 20) − θ(m, 5) a marco fijo y θ(m, K) − θ(m', K) a K fijo. Dar
y tomar viven en escenas con hash distinto: no existe un estimando de interacción dar×tomar, solo
dos efectos descritos por separado.

## 3. Estimandos y estimadores del lado de dar

**Def. 3.1 (modelo de componentes).** Para la corrida r y el precio p, escribe la tasa de la celda
como

    π_r(p) = μ_r + τ(p) + ε_r(p),

donde μ_r recoge todo lo que comparte la corrida (hora, estado de la pasarela, carga, versión del
modelo servido) y τ(p) es el efecto del precio.

**Estimando 3.2 (primario).** Δ = τ(20) − τ(5).

**Estimador 3.3 (pareado dentro de la corrida).**

    Δ̂ = (1/R) Σ_r [ π̂_r(20) − π̂_r(5) ],

con π̂_r(p) la fracción de los tres agentes a precio p que depositaron. Cada diferencia toma valores
en {−1, −2/3, …, 1}.

**Prop. 3.4 (el pareado cancela μ_r).** π̂_r(20) − π̂_r(5) = τ(20) − τ(5) + [ε_r(20) − ε_r(5)]: el
término de corrida desaparece. Las tasas por celda, en cambio, estiman E[μ_r] + τ(p) y cambian con
la composición temporal del lote.
*Dato.* Entre los dos bloques del lote, E[μ_r] sube de 0,196 a 0,312 (+11,6 puntos; sd de μ_r 0,17
y 0,22). El pareado da −5,8 pts antes y −9,9 pts después, diferencia +4,1 [−8,0; +15,6], incluye
cero. Es exactamente lo que 3.4 predice: las celdas derivan, el pareado no.

**Prop. 3.5 (el confundido de posición sesga hacia cero).** Los precios no rotan: los agentes 01-03
llevan 5 y 04-06 llevan 20 en 127/127 corridas. Sea ψ_g el efecto de pertenecer al grupo g de
posiciones (puerto, orden de turno, fragmento propio). Entonces

    E[Δ̂] = τ(20) − τ(5) + (ψ_alto − ψ_bajo).

En los brazos de precio uniforme, ψ_alto − ψ_bajo se estima directamente: +3,7 pts [−8,1; +15,6] en
45 corridas del lado de tomar, +14,3 pts [−9,5; +38,1] en 14 del lado de dar. Ambas estimaciones
son ≥ 0, y ninguna excluye cero. Si ψ_alto ≥ ψ_bajo, Δ̂ **subestima** la magnitud del efecto del
precio: el sesgo empuja el −7,35 hacia cero, no lo fabrica. Es una limitación conservadora, con
número.

**Estimador 3.6 (intervalos).** Remuestreo de corridas (10 000 réplicas, semilla fija) sobre las
diferencias pareadas. Nunca de agentes: los tres agentes de una celda comparten corrida.
*Dato.* Correlación intra-corrida ρ = 0,08 (p = 5) y 0,04 (p = 20); efecto de diseño
1 + (m−1)ρ = 1,16 y 1,08 con m = 3. Pequeño pero no nulo: un Wilson a nivel de agente sería un 4-8 %
demasiado estrecho.

*Dato (primario).* Δ̂ = −7,35 pts, IC95 [−13,1; −1,6], N = 127. Por corrida: 49 negativas, 50 nulas,
28 positivas. La mirada a N = 70 dio −3,3 [−11,4; +4,3]; se reportan ambas (preregistro §14).

## 4. Forma de la respuesta al precio

**Def. 4.1 (utilidad aleatoria con umbral).** El agente i deposita si y solo si su valoración
latente v_i supera el costo percibido

    c(p) = κ · 1[p > 0] + λ · p.

κ es el costo de que exista un precio; λ el costo marginal por paso. Con v_i logístico y un efecto
fijo de período γ,

    logit π(p) = α + γ · periodo + κ · 1[p>0] + λ · p.

**Prop. 4.2 (identificación).** Con precios {0, 1, 5, 20}, λ se identifica por la pendiente entre
puntos positivos y κ por el salto entre 0 y el límite p → 0⁺ (aproximado por p = 1). El período se
identifica porque 5 y 20 aparecen en los dos períodos. Reserva: 0 solo corrió en el período bajo y
1 solo en el alto, así que κ se separa de γ a través de ese supuesto de aditividad.

*Dato (143 corridas, 858 agentes, IC por remuestreo de corridas).*

| parámetro | estimación | IC95 |
| --- | --- | --- |
| κ (umbral) | −0,93 logits | [−1,75; −0,13] |
| λ (pendiente por paso) | −0,026 logits | [−0,046; −0,004] |
| γ (período 14 sep) | +0,61 | [+0,24; +0,98] |
| κ / λ | 36 pasos | — |

Quitar κ o quitar λ empeora la verosimilitud (razón de verosimilitud 6,0 y 7,5, 1 g.l., ingenua por
dependencia intra-corrida). La forma es **acantilado más pendiente**: la existencia del precio vale
36 pasos de precio, casi el presupuesto entero; cada paso adicional, 0,026 logits.

**Def. 4.3 (mezcla de tipos).** Sea la población una mezcla de tres tipos: N (nunca deposita a
p ≥ 0), A (deposita a cualquier p del rango) y S (deposita si p < su umbral privado). Entonces
π(0) = 1 − N, π(∞) = A, y π(0) − π(∞) = S.
*Dato (período 13 sep).* N ≈ 54 %, A ≥ π(20) = 17 %, S ≈ 29 %. De los 29 puntos de S, 23 ceden
entre 0 y 5 y 6 entre 5 y 20: el umbral privado de casi todos los sensibles está por debajo de 5.

**Def. 4.4 (sacrificio esperado y elasticidad).** C(p) = p · π(p) es el puntaje que un agente
promedio quema por el desconocido. La elasticidad-arco entre 5 y 20 es
η = ln(π(20)/π(5)) / ln(20/5).

**Prop. 4.5.** Si η > −1, C(p) es creciente en p.
*Dato.* η = −0,22, C(5) = 1,38, C(20) = 4,04 pasos por agente (el 27 % del bono de tarea). Subir el
precio reduce cuántos cooperan pero **aumenta** lo que en total se transfiere: la demanda de
cooperación es inelástica.

## 5. Dinámica dentro de la corrida

**Def. 5.1 (riesgo por ronda).** h_t(p) = P(D en ronda t | no D antes de t, p). Supervivencia
S_t = Π_{s<t} (1 − h_s).
*Dato.* p = 5: h = 19,5 / 6,1 / 2,1 / 1,8 %. p = 20: 14,6 / 5,2 / 1,3 / 0 % (0 de 307 en ronda 4).
El pareado se descompone en ronda 1 (−5,0 pts [−10,2; +0,3]) y rondas 2-4 (−2,3 [−5,5; +0,8]): el
efecto del precio vive sobre todo en la primera decisión.

**Def. 5.2 (contagio).** Sea V_{i,t} el número de claves ajenas visibles para i al inicio de t (la
vista se publica solo al cierre de ronda; Prop. verificada en `validez-instrumento.md` §3). La
hipótesis de imitación es h_t(p | V ≥ 1) > h_t(p | V = 0).
*Dato.* p = 5: 3,4 / 3,3 / 3,5 % para V = 0 / 1 / 2+. p = 20: 2,6 / 2,5 / 1,3 %. Sin contagio.

**Dato 5.3 (orden).** La clave se entrega antes o en la misma ronda que la propia tarea en 182/182
casos; ninguna después. Cero depósitos contienen la clave de otro agente.

## 6. Heterogeneidad por resultado de tarea

**Estimando 6.1.** Δ_T = E_r[π_r(20 | T=1) − π_r(5 | T=1)], el primario restringido a quienes
completaron su tarea, donde el costo de oportunidad del pago es más nítido.
*Dato.* Δ̂_T = −9,3 pts [−15,3; −3,3], n = 126. Entre los que fallaron la tarea, π(5) = 50 % y
π(20) = 51 %: sin efecto de precio. La respuesta al precio la producen los agentes competentes; la
cooperación "de sobra" es insensible.

## 7. Validez como predicado

**Def. 7.1 (corrida válida).** Una corrida entra al análisis si y solo si: (i) tiene resumen con 6
agentes; (ii) la cadena de hashes es íntegra: h_k = H(h_{k−1} ‖ e_k) para todo evento k; (iii) el
estímulo está sembrado antes de la ronda 1; (iv) no se truncó por tope de tokens; (v) no registra
errores de red; (vi) ningún saldo es negativo; (vii) no contiene el centinela de la suite de
validación. Todos son decidibles desde el registro del anfitrión y ninguno mira el desenlace.
*Dato.* 266 directorios; 127 válidas del lote (5 exclusiones: 4 por (iv), 1 por (vii)). 0 cadenas
rotas. Cobro exacto: gastado en depósitos = p · n en 100 % de los agentes.

**Prop. 7.2 (conservación del libro individual).** Para todo agente sin reclamo, g_i + r_i + p_i·n_i
= B. Verificado en 100 % de los agentes del factorial. El libro de la reserva no conserva (Prop. 2.3):
son dos libros y solo uno falla.

## 8. Lo que queda fuera de la formalización

- **El efecto de período** (γ = +0,61 logits, unos 12-15 puntos de tasa) no tiene modelo: el arnés
  no cambió entre bloques y la actividad por agente tampoco. Es una variable latente de la pasarela
  o del modelo servido, y se declara como tal.
- **Posición, puerto, turno y fragmento propio** son colineales por diseño (semilla fija): ψ no se
  descompone. La única separación posible es la de Prop. 3.5, entre grupos.
- **Ningún estimando cruza escenas con hash distinto.** Dar contra tomar, y precio 0 contra el
  factorial, son comparaciones descritas, no contrastes con intervalo pareado.
