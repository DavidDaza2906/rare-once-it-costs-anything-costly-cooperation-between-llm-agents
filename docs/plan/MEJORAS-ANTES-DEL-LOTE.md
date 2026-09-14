# Qué puede mejorar los resultados antes de correr el lote completo

Estado: 13 de septiembre de 2026. Ensayo de 9 corridas pagadas + 8 del brazo de costo cero.
Regla que gobierna todo lo de abajo: **mejorar el instrumento para que pueda ver el fenómeno es
legítimo; mover el diseño hasta que el número se mueva no lo es.** Ninguno de estos cambios garantiza
un efecto — el pronóstico honesto sigue siendo que 5 contra 20 dé cero, y varios cambios *debilitan* el
titular a cambio de medirlo bien.

---

## A. Decisiones que hay que cerrar antes del lote (enmiendas, cero tokens)

**A1. Cuál es el acto medido — y aplicarlo igual al primario y a la puerta B.**
Hoy la escena declara `tasa_deposito` (cualquier depósito) y la puerta B mide lo mismo (`deposito_clave
o deposito`). Con esa definición: primario 41% vs 30% y puerta 62,5% (pasa). Con el acto que la
solicitud elicita —depositar la clave— primario **22% vs 22%** y puerta **46%** (indecisa).
El aparente efecto del precio vive **entero** en depósitos que no responden a la solicitud: códigos
ensamblados, partes, negociación de canal. Y la ortogonalidad del confederado (I10) y la salida de los
interdependientes del factorial se hicieron justo para aislar el acto de costo puro.
**No se puede elegir una definición para el primario y otra para la puerta.** Decidir las dos juntas.
*Coste: cero. Efecto: el titular pasa a ser un cero limpio en vez de un no-efecto turbio.*

**A2. Reescribir H4 con la cita, sin tocar el número.**
`2604.07821` (arXiv, abr 2026): con ayuda **gratis e instruida**, la capacidad no predice cooperación
—o3 al 17% del óptimo colectivo, o3-mini al 50%—. Por lo tanto una tasa baja a precio cero **no prueba
incapacidad**: H4 deja de ser una prueba de capacidad y pasa a ser **línea base conductual**.
Enmienda declarada en §8, **conservando el 46% medido y el veredicto original de la puerta**.
*Advertencia honesta: reespecificamos un umbral que acabamos de fallar, justo después de encontrar el
paper que lo justifica. Por eso la enmienda debe llevar la cita, la fecha y los dos números.*

**A3. Mover los precios a donde está el codo.**
El contraste preregistrado (5 contra 20) está en la zona plana: 22,2% contra 22,2% (diferencia 0,0).
La caída aparece entre 0 y 5: 45,8% contra 22,2% — z=2,19, p≈0,028 **sin corregir** y en comparación
**entre escenas**, así que es hipótesis, no hallazgo.
Propuesta: precios **{2, 5, 20} dentro de la corrida**, 3 agentes por nivel, y el 0 en el brazo aparte
como ahora (así I9a sigue valiendo: todo precio positivo en el brazo de sacrificio). La pregunta
confirmatoria pasa de "¿baja la respuesta al subir el precio?" a **"¿umbral o pendiente en el régimen
dominado?"**, que es la que los datos sugieren que se puede contestar.
*Coste: 9 agentes × 4 rondas ≈ 252k por corrida; con N=40 son ~10,1M. Alternativa: mantener 2 precios
y N=80 (~13,4M) — compra precisión sobre un punto que puede estar plano.*

---

## B. Fidelidad del instrumento (código y escena, barato)

**B1. Desacoplar la respuesta del cupo de acciones.**
Evidencia: **44% de los agentes agotó el cupo** (8 acciones × 4 rondas) y **los que fracasan en la
tarea responden 2,5 veces más** que los que la completan (41% contra 16%). Es decir, buena parte de la
tasa mide **capacidad sobrante**, no disposición: el que termina su tarea ya no tiene acción libre.
Arreglo: subir `pasos_por_ronda` de 8 a 12, **o** que depositar cueste pasos (el constructo) pero **no
consuma** una de las acciones de la ronda.
*Efecto esperado: sube la tasa y afila el contraste en lugar de aplanarlo.*

**B2. Reducir la fricción de la tarea.**
Evidencia: **31% de tareas completadas**; las transcripciones muestran agentes confundidos por archivos
diminutos sin etiqueta (`"cat tarea.txt appears empty?"`) y comandos rechazados que queman acciones
(`wc -c *.txt`, bucles `for`).
Arreglo: un `inventario.txt` que nombre el propósito de cada archivo, y admitir los modismos que de
verdad escriben (tuberías ya admitidas; faltan bucles y comodines).
*Efecto: menos acciones gastadas en orientarse, y encoge el confundidor de capacidad sobrante.*

---

## C. Análisis que ya se puede hacer con los datos que tendremos (cero tokens)

**C1. Composición de disposiciones por agente.** Es la idea más fuerte. Cada agente enfrenta la misma
solicitud en **cuatro rondas** a un precio fijo: eso da hasta cuatro decisiones por agente y permite
clasificarlo como *siempre responde / a veces / nunca*. Una **mezcla** de "siempre" y "nunca" produce
exactamente una tasa media plana — que es lo que observamos (22% en ambos brazos). Estimando la mezcla
por brazo se distingue "el precio no mueve a nadie" de "el precio mueve la composición".
*Precedente metodológico:* `2601.19082` clasifica estrategias canónicas con clasificadores en lugar de
leer conteos crudos.
*Requiere: declararlo en el plan de análisis antes del lote.*

**C2. Intención de tratar y tasa condicionada a la cadena de saliencia.**
Con las transcripciones ya guardadas (texto y razonamiento por separado) se puede medir por agente:
leyó el almacén → mencionó la solicitud → leyó su clave → depositó. Reportar ITT **y** la tasa
condicionada a haber registrado la solicitud separa "no se enteró" de "decidió no pagar".
*Requiere: declarar el umbral en el preregistro. Coste: cero.*

---

## D. Un brazo nuevo con valor real frente al paper más cercano

**D1. Brazo de participación privada, para contrastar con `2607.23982`.**
El paper más cercano mide si el modelo sigue la *frontera de participación privada* de Holmström: allí
el ayudante **recibe una parte** del resultado del equipo, así que existe un punto donde ayudar es
racional. Nuestro factorial mide el **régimen dominado** (participación exactamente cero).
Añadir un brazo con **participación pequeña** convierte el proyecto en un **diseño de dos regímenes en
el mismo arnés agéntico**: replicamos su pregunta con herramientas y libro en el host, y contrastamos
con el régimen donde la predicción racional es no dar nunca.
*Coste: 4 a 8 corridas (~1M). Es la diferencia entre "no lo hemos medido" y "medimos lo que ellos no"*.

**D2. Afilar el brazo de encuadre ya planificado.**
`2604.07821` mide cooperación a costo cero **instruida**. Nuestro brazo de encuadre (H5, ~4 corridas)
puede diseñarse para replicar esa condición de instrucción explícita contra la neutral.
*Coste: ya está presupuestado; solo hay que hacerlo comparable.*

---

## E. Lo que no se hace

- No se mueve el umbral ni el horizonte para que el resultado cambie. El horizonte de 4 rondas ya está
  fijado por criterio y el umbral de la puerta B se conserva con su veredicto original.
- No se añaden corridas a dos puntos que pueden ser ambos planos esperando otra cosa.
- No se instruye la cooperación en el brazo principal: destruiría el constructo. Y `2604.07821` no
  autoriza a instruir — al contrario, muestra que instruir no basta.

---

## Orden propuesto

1. **A1, A2, A3** (decisiones y enmiendas): cero tokens, decide todo lo demás.
2. **B1, B2** (código y escena) + re-correr `prueba_solvente.py` y la puerta: ~1 h, sin tokens.
3. **Re-medir la puerta B con la definición de la clave** en la escena nueva: 4 a 8 corridas (~1M),
   porque hoy está indecisa (46%, IC [33, 60]).
4. **D1** (brazo de participación) y **D2** (encuadre comparable): ~1,5M.
5. **Lote**: N=40 con {2, 5, 20} o N=80 con dos precios — la decisión de A3.

Presupuesto: ~4,2M gastados; los pasos 3 y 4 añaden ~2,5M; el lote de 40 con tres precios ~10,1M.
Total ≈ 16,8M sobre un techo de 20M, sin margen para repetir el lote.
