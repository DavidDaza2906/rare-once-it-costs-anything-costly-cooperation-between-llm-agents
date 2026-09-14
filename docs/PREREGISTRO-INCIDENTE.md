
## 10. Brazos del incidente en el segundo arbol (declarado 13 sep ~20:05 COT, antes de correr)

**Por que un arbol aparte.** Los puertos 8201-8206 los ocupa el 2x2 de abstencion. Estos brazos corren en
`/home/daw/Sprint-2`, con el arnes **copiado identico** y puertos **8401-8406**, para no competir por los
puertos ni mezclar corridas. La escena cambia de puertos, asi que **tiene hash propio**: sus corridas se
analizan como brazo independiente y **no se mezclan con el lote ni con el 2x2**.

**Que se corre, y por que.**

| Brazo | Escena | hash | pregunta | N |
|---|---|---|---|---|
| R1c | `escena-reclutador-par` | d8f455c37626be8c | ¿importa **quien pide**? El mismo pedido firmado por un par en vez de por un externo | 8 |
| Reclutador × abstención, K=5 | `escena-reclutador-abstencion` | dd9086e2d38f3740 | el que pide empuja **y** la reserva existe: ¿cambia la tasa de tomar? | 8 |
| Reclutador × abstención, K=20 | `escena-reclutador-abstencion-caro` | 580e8ae01e1b0ff9 | lo mismo con la tentación grande | 8 |

**R1b sigue fuera**: la variante de presión con apelación colectiva es otro constructo y no se corre sin
visto bueno de uso dual.

**Piloto obligatorio de dos corridas por brazo**, y no una: el defecto de herencia entre corridas es
invisible con una sola corrida de piloto, porque lo que delata es el estallido en la segunda.

**Condiciones de entrada al analisis**, las mismas de siempre mas dos: el archivo
`salidas/<corrida>/puertos/` (prueba de que la corrida la produjo el arranque limpio) y la
comprobacion de **efecto** — un reclamo aplicado sin comando del agente es herencia, y excluye.

**Potencia, declarada de antemano:** con 8 corridas (48 corridas-agente) el intervalo de una diferencia
de tasas es de ~+-13 puntos, y el de una **interaccion** (diferencia de diferencias) bastante mas ancho.
Estos brazos se reportan como **exploratorios de direccion, no de magnitud**.
