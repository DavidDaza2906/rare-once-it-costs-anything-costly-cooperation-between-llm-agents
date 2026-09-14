# Cuatro hallazgos de validez del instrumento (14 sep, 00:30 EDT)

Revisión sobre datos y código ya en disco. Nada de esto se descubrió corriendo nada nuevo: sale de
mirar cómo se asigna el tratamiento y qué hace el arnés al cerrar la ronda. Dos son defectos de diseño,
uno es una verificación que **pasa**, y el cuarto obliga a cambiar cómo se lee el factor de tentación.

Guiones y datos: `analisis/posicion.py` → `reportes/posicion.json` (hash `e172f1fe066e4722`),
`analisis/tomar3x2.py` → `reportes/tomar-3x2.json` (hash `93fc9452a454a424`).

---

## 1. El precio se asigna por posición y nunca rota

`escena.json` reparte `asignacion.autosuficientes.precios = [5, 5, 5, 20, 20, 20]`. El mecanismo exacto
importa, porque cambia cuál es el arreglo: `validador.py:resolver_asignacion` **sí baraja** los precios
(`rnd.shuffle(precios)`), pero lo hace con `escena["semilla"]`, que vale **20260912 en todas las escenas
del proyecto** y no cambia entre corridas. El barajado ocurre una sola vez, al resolver la escena, y el
`.resuelta.json` resultante se reusa en cada corrida. Resultado: la misma permutación siempre.
Verificado en las **108 corridas** del factorial con los seis agentes presentes:

| agente | precio recibido |
| --- | --- |
| agente-01, -02, -03 | 5 en 108/108 |
| agente-04, -05, -06 | 20 en 108/108 |

El factor de precio queda **perfectamente confundido** con todo lo que viaje con el índice: el puerto de
egreso (`8201+i`), el directorio de trabajo del agente y el orden en que el bucle lo recorre. Conviene
ser explícito sobre una tentación de lectura: el **pareado dentro de la corrida no arregla esto**,
porque pareja a los agentes 01-03 contra los 04-06 — es exactamente el contraste confundido, no una
corrección de él.

Lo que **no** varía con el índice, verificado: los seis son `autosuficiente`, con `partes_ajenas_visibles`
vacío y el mismo `tipo_cambio`, en las 108 corridas. El rol no es el confundidor.

**Arreglo de diseño, para cualquier corrida futura:** no hace falta reescribir el reparto, basta con
**variar la semilla por corrida** (o volver a resolver la asignación dentro del bucle con una semilla
derivada del índice de corrida) para que la permutación cambie y el precio quede contrabalanceado entre
posiciones. Es una línea. Ojo además con el efecto colateral: con semilla fija tampoco varían los
`partes` (`rnd.shuffle(partes)` en la misma función): en `escena.resuelta.json` el agente-01 lleva
siempre `7K`, el 02 `5Y`, el 03 `D4`… y ese archivo resuelto se reusa en las 121 corridas, así que cada
agente recibe siempre el mismo fragmento. (No se ve en `resumen.json`, que no guarda `parte`.) No se puede aplicar a lo ya corrido.

## 2. El efecto de posición, medido: pequeño y no establecido

Se puede estimar el confundidor sin corridas nuevas, porque hay escenas donde el tratamiento es
**uniforme entre agentes**: los brazos de precio único (0 y 1, y los de identidad a precio 5) y las seis
celdas del 3×2, donde K es el mismo para los seis. Ahí, cualquier diferencia entre el grupo
{01,02,03} y {04,05,06} es posición con el tratamiento fijo. Diferencias pareadas dentro de la corrida,
intervalo por remuestreo de corridas:

| escena | grupo bajo (01-03) | grupo alto (04-06) | bajo − alto |
| --- | --- | --- | --- |
| dar, precio 0 (n=8) | 33,3% | 58,3% | −25,0 [−54,2; +8,3] |
| dar, par p5 (n=6) | 50,0% | 50,0% | −0,0 [−33,3; +33,3] |
| **dar, agregado (n=14)** | 37,3% | 51,0% | **−14,3 [−38,1; +9,5]** |
| tomar, sin marco K=5 (n=8) | 29,2% | 41,7% | −12,5 [−41,7; +20,8] |
| tomar, sin marco K=20 (n=8) | 45,8% | 50,0% | −4,2 [−29,2; +20,8] |
| tomar, neutral K=5 (n=8) | 20,8% | 25,0% | −4,2 [−25,0; +20,8] |
| tomar, neutral K=20 (n=8) | 25,0% | 25,0% | +0,0 [−25,0; +25,0] |
| tomar, reclutador K=5 (n=8) | 20,8% | 33,3% | −12,5 [−33,3; +12,5] |
| **tomar, agregado (n=45)** | 28,9% | 32,6% | **−3,7 [−15,6; +8,1]** |

**Ningún intervalo excluye cero**, y la mejor cota —45 corridas, del lado de tomar— deja el efecto en
−3,7 puntos con margen de unos ±12. El signo es negativo en 6 de las 8 comparaciones no nulas (el grupo
alto tiende a cooperar algo más), lo que es sugestivo y no significativo.

**Cómo hay que decirlo en el reporte, entonces:** el defecto de diseño es real y la cota empírica es
pequeña, pero **es del mismo orden que el efecto primario**. El primario pareado 20−5 dio −3,3 puntos;
una posición de −3,7 puntos con margen de ±12 no permite atribuir limpiamente ese −3,3 al precio. La
conclusión defendible no cambia de forma —sigue siendo un nulo, sigue siendo un umbral y no una
pendiente— pero la atribución al precio queda declarada como limitación **con un número**, no como una
advertencia genérica.

## 3. La simultaneidad dentro de la ronda: verificada, aguanta

Como el orden de turno es fijo (`for nombre in c.agentes: await turno(...)`, siempre 01→06), había que
descartar que un agente tardío vea lo que hicieron los tempranos en su misma ronda. No lo ve:

- `publicar_vista()` se llama **sólo al cerrar la ronda**, nunca durante ella.
- `reconciliar_depositos_http()` y `reconciliar_reclamos()` también corren **sólo al cierre**, así que
  dentro de la ronda el saldo de la reserva que el agente consulta es el del cierre anterior.
- Al resolver, la visibilidad se recorta por ronda: `visibles = [d for d in depositos if d["ronda"] <
  ent["ronda"]]`.

La barrera está donde el diseño dice que está. Lo que sí queda como recomendación baratísima para
corridas futuras: **mezclar el orden de los agentes en cada ronda**, para que ningún efecto de orden
residual se acumule siempre en la misma dirección.

## 4. La tentación está confundida con la capacidad de la reserva, y el libro crea pasos

La reserva arranca en **60 pasos** y cada reclamo retira **2K**. Entonces:

- con **K=5** el fondo absorbe **6 reclamos** (los seis agentes pueden reclamar y aún queda);
- con **K=20** absorbe **1,5** — al segundo reclamo ya está en cero.

Eso no es un detalle de contabilidad: cambia el juego. Medido:

| celda | reclamos | reserva final media | corridas agotadas |
| --- | --- | --- | --- |
| sin marco K=5 | 17 | 38,8 | 0/8 |
| neutral K=5 | 11 | 46,2 | 0/8 |
| reclutador K=5 | 13 | 43,8 | 0/8 |
| **sin marco K=20** | 23 | **0,0** | **8/8** |
| neutral K=20 | 12 | 27,5 | 3/8 |
| reclutador K=20 | 11 | 12,5 | 3/8 |

A K=5 la reserva **nunca** se agota; a K=20 se agota siempre en la celda sin marco. Y `bucle.py` hace
`self.pasos[nombre] += K` y `self.reserva = max(0, self.reserva - 2*K)` por separado, así que un reclamo
contra un fondo ya vacío **acredita K pasos y no destruye nada**. Contado sobre los eventos:

| celda | reclamos | sobre reserva 0 | pasos creados de la nada |
| --- | --- | --- | --- |
| sin marco K=20 | 23 | **7** | 140 |
| neutral K=20 | 12 | **4** | 80 |
| reclutador K=20 | 11 | 0 | 0 |
| las tres de K=5 | 41 | 0 | 0 |

Once reclamos de 46 en K=20 se pagaron sin contrapartida: 220 pasos creados. El libro de presupuesto,
que es uno de los pilares de validez precisamente porque el costo tiene unidades, no conserva en ese
caso.

**Las dos consecuencias para la lectura, y la segunda es la que importa:**

1. El factor "tentación" no es sólo tamaño del premio: a K=20 también desaparece la capacidad del fondo
   para absorber daño. K=5 y K=20 difieren en dos cosas a la vez.
2. **Una vez agotado el fondo, abstenerse no protege nada** y reclamar es gratis para el resto: no hay
   ningún motivo, ni prosocial, para no reclamar. Eso puede inflar la toma a K=20 — y es justo donde
   vive el contraste que sí excluyó cero (`sin marco − neutral | K=20` = +22,9 [+2,1; +43,7], y la celda
   sin marco K=20 se agotó en 8 de 8). La dirección del sesgo empuja hacia el resultado observado, así
   que ese contraste **no se puede presentar como efecto limpio del marco**: hay que reportarlo junto
   con el agotamiento, o restringirlo a los reclamos hechos mientras el fondo aún tenía saldo.

**Arreglo de diseño:** escalar la reserva con K (por ejemplo 60 para K=5 y 240 para K=20, manteniendo
`reserva / 2K` constante), y corregir el libro para que no se acredite K si el fondo no lo cubre. Las
dos cosas son de una línea y ninguna se puede aplicar a lo ya corrido.

### 4b. La prueba: el efecto de marco no sobrevive al control del agotamiento

Hay una forma de medir la decisión limpia sin corridas nuevas: **restringir a la ronda 1**. En la ronda 1
la reserva vale 60 en las seis celdas y nadie ha reclamado todavía, así que la decisión no puede estar
contaminada por el fondo agotado. Implementado en `analisis/tomar3x2.py` (`marco_solo_ronda1`).

| celda | toma en ronda 1 | toma en todas las rondas | salto |
| --- | --- | --- | --- |
| sin marco K=5 | 29,2% | 35,4% | +6,2 |
| **sin marco K=20** | **25,0%** | **47,9%** | **+22,9** |
| neutral K=5 | 14,6% | 22,9% | +8,3 |
| neutral K=20 | 18,8% | 25,0% | +6,2 |
| reclutador K=5 | 20,8% | 27,1% | +6,3 |
| reclutador K=20 | 20,0% | 23,3% | +3,3 |

La celda `sin marco K=20` **casi duplica** su toma después de la ronda 1, mientras las otras cinco se
mueven entre 3 y 8 puntos. Es la única que se agota en 8/8, y el exceso es reclamo posterior al
agotamiento: gratis, sin nadie a quien perjudicar. Y el contraste se desarma:

| contraste, K=20 | todas las rondas | sólo ronda 1 |
| --- | --- | --- |
| sin marco − neutral | **+22,9 [+2,1; +43,7]** EXCLUYE cero | +6,2 [−12,5; +22,9] incluye cero |
| sin marco − reclutador | **+24,6 [+13,8; +36,2]** EXCLUYE cero | +5,0 [−5,8; +14,6] incluye cero |

**Conclusión:** los dos únicos contrastes del 3×2 que excluían cero eran artefacto del agotamiento del
fondo, no efecto del marco. Con el fondo intacto, **ninguno de los doce contrastes excluye cero**.

Lo que queda, que es un resultado y no un residuo: en la ronda 1, la toma va de **14,6% a 29,2%** en las
seis celdas, o sea **abstención del 71% al 85%**, y no la mueve detectablemente ni el tamaño de la
tentación (+3,33 contra +13,33 netos) ni la presencia de alguien pidiendo ayuda ni quién es el
beneficiario. Es la misma forma que el lado de dar: **plano, no una pendiente**. Un agente que se
abstiene de saquear un fondo común lo hace con bastante independencia de cuánto hay para saquear.

---

## Qué hacer con esto en el reporte

Ninguno de los cuatro tumba el resultado principal, que es un nulo y sigue siendo un nulo. Lo que hacen
es fijar el precio de ese nulo: el primario mide precio **y** posición sumados (§1-2), y el único
contraste del 3×2 que parecía positivo era agotamiento del fondo y no marco (§4b). Lo honesto es que los
cuatro entren en la sección de validez con su número, que §3 entre como verificación que pasa, y que los
dos arreglos —contrabalanceo del precio y reserva escalada con K— encabecen el trabajo futuro, porque son
las dos cosas que un replicador necesita saber antes de tocar el instrumento.

Y hay algo que el conjunto **gana** al quitarle los dos falsos positivos. Los dos lados del experimento
terminan diciendo lo mismo con diseños independientes: la conducta costosa —entregar la clave pagando, no
saquear el fondo común— es **plana** en el parámetro que debería moverla. Al dar, subir el precio de 5 a
20 no baja la entrega (−3,3 pts, incluye cero); al tomar, cuadruplicar el premio de +3,33 a +13,33 netos
no sube el saqueo en la ronda 1 (los tres marcos se mueven entre −0,8 y +4,2 pts, todos incluyen cero). Y
en los dos lados, **quién pide o quién se beneficia tampoco mueve nada**: par contra tercero al dar, y
neutral contra reclutador al tomar, ambos nulos. Un paper cuyo resultado es "hay un umbral y no una
pendiente, y la identidad del solicitante no importa" es más fuerte con dos operacionalizaciones que con
una, y más creíble cuando se muestra que los dos efectos que parecían significativos se cayeron al
controlarlos.
