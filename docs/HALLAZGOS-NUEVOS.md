> **Superseded.** This is a working note from before the paper's final analysis. The causal
> reading offered here (that helping depleted the helper's own task) was corrected: the gap
> survives stratification by first exposure, and 33 of the 40 who helped without finishing had
> never obtained their own part. See the paper, sections 4.2-4.3.

# Hallazgos nuevos para el reporte

Cuatro análisis sobre el conjunto congelado (127 corridas, sha `66fd3a0b…`) que el análisis
congelado NO toca, más una lectura cualitativa. Todos corren con `analisis/hallazgos.py` y sus
números están en `reportes/hallazgos.json`. Declarados como **exploratorios**: se corrieron después
de ver los resultados confirmatorios, y eso va en el texto.

## 1. Ayudar canibaliza la tarea propia (el aporte fuerte)

La pregunta del sprint es si los agentes sacrifican presupuesto propio para ayudar. La versión más
dura de ese sacrificio no son los pasos: es **la tarea**.

| precio | tarea correcta de quien ayudó | de quien no ayudó | puntaje (ayudó / no) |
|---|---|---|---|
| 5 | 82,9% (105) | 93,8% (276) | 21,5 / 34,9 |
| 20 | 71,4% (77) | 93,1% (304) | 15,7 / 38,7 |

Diferencia pareada por corrida: **−19,2 puntos [−26,5; −12,4], excluye cero**. Y el gradiente es
monótono en el precio: quien paga más por ayudar, pierde más tarea (71,4% contra 82,9%).

Esto cambia el encuadre del paper: la cooperación medida aquí no es un coste marginal sobre un
desempeño intacto — **los cooperadores entregan su objetivo propio en la puerta**. "Costly
signaling" no alcanza para describirlo: la cooperación canibaliza el goal del agente.

**Réplica en otros modelos:** Gemini 3.1 Flash Lite reproduce el patrón (tarea de quien ayuda 25,0%
vs 68,8% de quien no). GPT-5.4 ayudó 1 vez en 36 agentes y DeepSeek V4.1 Flash 0 veces en 6, así
que su lado de la sustitución no se puede evaluar: **helping floor**, no ausencia de sustitución.

## 2. La cooperación NO se agrupa por corrida

¿La cooperación es una propiedad del colectivo o de agentes individuales? Permutando quién deposita
dentro de cada precio (20.000 vueltas, la asignación de precios no se toca), la varianza entre
corridas observada es **1,13×** la esperada bajo independencia, **p = 0,0501**. En el límite, y el
diseño ya la favorece (los agentes de una corrida comparten entorno). Lectura honesta: **no hay
evidencia de un "efecto colectivo" que dominar** — el nivel de análisis que importa es el agente.
Eso es una respuesta útil para un revisor que pregunte por clústeres.

## 3. Tomar y ayudar se separan con el marco

En el mismo agente, ¿el saqueo del bien común desplaza la ayuda? Depende del marco:

| celda | ayuda de quien toma | de quien no toma | diferencia |
|---|---|---|---|
| rec+abs K=5 (sin marco) | 3,2% (1/31) | 3,1% (2/65) | +0,1 |
| rec+abs K=20 (sin marco) | 6,2% (1/16) | 3,6% (2/56) | +2,7 |
| marco neutro K=5 | 18,2% (2/11) | 5,4% (2/37) | +12,8 |
| marco neutro K=20 | 33,3% (4/12) | 11,1% (4/36) | +22,2 |

Sin marco, tomar no predice ayudar. **Con marco, quien toma ayuda MÁS** — la conducta económica
activa y la cooperación conviven en los mismos agentes cuando el marco hace ambas visibles. No son
polos de un mismo eje. Las n son chicas (11-12 tomadores por celda): **dirección, no magnitud**.

## 4. La cooperación se decide temprano — no madura

Por eventos (la fuente buena; el resumen deja rondas nulas en los depósitos HTTP):

- precio 5: **76 de 105 depósitos (72,4%) en la ronda 1**
- precio 20: **56 de 77 (72,7%)**

No es un efecto que crece con la deliberación: se decide en la primera ronda o no se decide. Y la
ronda 4 de precio 20 tiene **un solo depósito**. Esto conecta con el hallazgo de la ronda 1 del
confirmatorio: la decisión es temprana y el fondo apenas interviene en ella.

## 5. Cualitativo: 13 de 182 lo leyeron como un canje

De los 182 agentes pagados que depositaron, **13 (7%)** lo leyeron como un CANJE — "deposito mi
clave **para obtener la parte_4**" — cuando su parte ya estaba en `parte_propia.txt` y el depósito
no reporta nada. 9 de esos 13 terminaron con la tarea correcta. Solo **3** de 182 mencionaron el
costo en pasos explícitamente. El instrumento ya había medido que el precio casi no entra en la
deliberación (el reclutador lo encontró: 2-4% razona el costo); esto lo replica en el lote: **los
que pagan no es porque hayan hecho la aritmética**.

## Qué NO encontré

- **Falsificación (H7): cero intentos detectados** sobre el conjunto congelado. Nadie afirma una
  acción que el registro del host contradiga.
- **Canarios de fuga**: ningún texto de los que ayudaron filtra el brazo o el precio.

## Declaración de bugs del guion (para la trazabilidad)

La primera versión de `hallazgos.py` tenía dos errores, ambos corregidos antes de publicar cifras:
la tabla 3 emparejaba escenas por substring (`abstencion-sola` también casa con
`abstencion-sola-caro`) y usaba las celdas equivocadas; la tabla 4 leía `ronda_entrega` del resumen
(25 depósitos en ronda 1) cuando los eventos dan 76 y cero sin ronda. El push intermedio que salió
con la sección 4 rota se corrigió en el commit siguiente.
