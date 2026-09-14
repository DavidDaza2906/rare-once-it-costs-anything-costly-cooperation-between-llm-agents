> **Superseded.** This is a working note from before the paper's final analysis. The causal
> reading offered here (that helping depleted the helper's own task) was corrected: the gap
> survives stratification by first exposure, and 33 of the 40 who helped without finishing had
> never obtained their own part. See the paper, sections 4.2-4.3.

# El hallazgo: la sustitución se descompone en tres mecanismos

Análisis del 14 de septiembre sobre el conjunto congelado (127 corridas) y el control (8). Tres
mediciones independientes, verificadas antes de escribir esto. Es **exploratorio**, declarado como
tal, y revierte la lectura causal de la sustitución.

## El hecho central

El 17,6% de los agentes que cooperaron **jamás volvieron a su tarea**. De los 182 que pagaron por
depositar la clave (precio 5 o 20), 32 no llegaron a entregar nada. De los 580 que no cooperaron,
solo 6,0% (35) no entregaron. Razón: **2,9 veces**.

Y en el control a precio 0 — donde ayudar es gratis — **el 100% de los agentes entregó su tarea**,
cooperaran o no.

## La descomposición

La sustitución (la brecha de tarea correcta entre quien ayuda y quien no) no es un solo efecto. Se
descompone en tres mecanismos con magnitudes medidas por separado:

### 1. Mecánico (los pasos): pequeño y medible con el control

A precio 0, ayudar no cuesta pasos. Quien ayudó completó la tarea al 95,5%; quien no, al 100%.
Diferencia pareada: **−2,5 puntos [−7,5; +0,0]** — incluye cero, en el límite. **La sustitución
necesita costo**: si no se pagan pasos, la brecha casi desaparece. Lo que queda es el borde
superior de lo que el mecanismo de pasos puede explicar.

### 2. De abandono: el mecanismo principal

Los 32 que cooperaron y jamás volvieron a su tarea son el 17,6% de los cooperadores (16,2% a
precio 5; 19,5% a precio 20), contra 6,0% de los no cooperadores. **Cooperar cuando cuesta se
asocia a tres veces más probabilidad de abandonar la tarea por completo.** Y el 94,4% de los que
cooperaron *antes* de entregar la tarea la completaron después: el abandono no es la regla de los
que "priorizan ayudar", es un subconjunto que **deposita y no vuelve**.

### 3. De fricción residual: el que vuelve, falla un poco

Entre los que **sí** entregaron la tarea, la tasa de correcta es 94,7% si cooperaron y 99,4% si
no. Una fricción de ~5 puntos en el condicional — compatible con el precio pagado (pasos que ya
no quedan para verificar), pero también con selección.

## La lectura causal, corregida

El dato de Fable (línea 1029: quien ya falló su tarea coopera más) y el nuestro (quien cooperó a
menudo no volvió) apuntaban en sentidos opuestos. La descomposición los reconcilia: **la
dirección dominante no es "la ayuda desplaza la tarea" ni "la tarea fallida habilita la ayuda",
sino una tercera vía — una fracción de agentes que, al decidir cooperar bajo costo, abandona su
tarea.** La cooperación costosa no se paga solo con pasos: se paga con **tareas dejadas a la
mitad**.

## Consecuencia para el mecanismo del incidente

El agente que coopera con una solicitud externa costosa **no sigue trabajando con menos recursos**:
una parte significativa **deja de trabajar en su objetivo por completo**. Para quien modela el
incidente: el costo de una petición cooperativa inyectada no es un impuesto marginal sobre la
capacidad del agente — es, en ~1 de 6 casos, una **interrupción permanente del objetivo**. Es una
forma de *goal abandonment* inducido por la solicitud, medida con costo real.

## Números exactos (para citar)

| medida | valor |
|---|---|
| cooperadores que jamás entregaron la tarea | 32/182 (17,6%) — precio 5: 17/105 (16,2%); precio 20: 15/77 (19,5%) |
| no cooperadores que jamás entregaron la tarea | 35/580 (6,0%) |
| razón | 2,9× |
| control precio 0: no entregaron la tarea | 0/48 (0%), cooperaran o no |
| control precio 0: brecha de tarea correcta | −2,5 pts [−7,5; +0,0] (incluye cero) |
| entregaron la tarea: correcta si cooperaron | 142/150 (94,7%) |
| entregaron la tarea: correcta si no cooperaron | 542/545 (99,4%) |
| cooperaron antes de entregar y completaron | 135/143 (94,4%) |

Reproducible: el cálculo cruza `deposito_clave`, `tarea_correcta` y los eventos `depositar` /
`entregar` de cada corrida del conjunto congelado y del control.
