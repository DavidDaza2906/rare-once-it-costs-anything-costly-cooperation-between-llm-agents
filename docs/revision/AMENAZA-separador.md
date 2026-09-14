> **Superseded.** This is a working note from before the paper's final analysis. The causal
> reading offered here (that helping depleted the helper's own task) was corrected: the gap
> survives stratification by first exposure, and 33 of the 40 who helped without finishing had
> never obtained their own part. See the paper, sections 4.2-4.3.

# Amenaza al primario: el defecto del separador `;`

Detectado el 14 de septiembre (reporte en `analisis/parte4/salida.txt`, guiones
`analisis/parte4/{verificacion.py,sin_splitter.py}`). **Es la amenaza más seria que se ha
encontrado a una cifra congelada**, y llega antes de la entrega.

## El defecto

En `harness/bucle.py`, `_plan` parte los comandos por `[|;]` (y convierte `&&` en `;`) y
`_ejecutar_etapas` los encadena como tubería: **solo se ve la salida de la última etapa**. Un
`curl` que no va último pierde su respuesta.

Consecuencia: el agente no ve la respuesta del recurso de red — ni la parte_4 ni el texto de la
solicitud. Verificado en el código, no inferido (`bucle.py:284-293`, `307`, `366-384`).

## El impacto medido

| medida | valor |
|---|---|
| agentes afectados en el conjunto congelado | 186/762 = 24,4% (regla estricta) |
| entrega en afectados | 93/186 = 50,0% |
| entrega en no afectados | 89/576 = 15,5% |
| **primario 20−5 con todos** | **−7,35 pts [−13,1; −1,6], excluye cero** |
| **primario 20−5 sin afectados** | **−3,25 pts [−9,2; +2,7], incluye cero** |

Verificación independiente, con una regla más cruda (marca a cualquier agente que corrió un `curl`
compuesto, sin exigir que la respuesta esté vacía): 437/762 = 57,3% marcados, entrega 31,4% contra
13,8%, y el primario pasa de −7,35 a **−6,20 [−15,4; +2,6]**. Las dos reglas coinciden en la
dirección: **la significancia del primario depende de los agentes que corrieron comandos compuestos**.

## El control con el instrumento arreglado

`salidas-control-parte4/` (7 corridas, escena `control-parte4`, hash `bd0449b257727f38`): con el
defecto corregido, **todos** los agentes ven la parte_4 en su primera exposición, y la entrega cae a
**3/41 = 7,3%**, contra 15,5% del conjunto congelado limpio y 23,9% del congelado completo.
Diferencia control − base limpio: −8,1 pts [−16,7; +2,5].

## La lectura nueva, y por qué reencuadra el reporte

El análisis de primera exposición (`verificacion.py`, sección 1) muestra dónde se concentra el pago:

| primera exposición a la solicitud | precio 5 | precio 20 |
|---|---|---|
| sin la parte_4 en la respuesta | 35,2% (44/125) | 29,6% (40/135) |
| **con la parte_4 en la respuesta** | **2,0% (3/150)** | **1,2% (2/163)** |

Es decir: **quien ya tiene su parte no paga (1-2%); quien todavía no la tiene paga a 30-35%**. Y de
los 182 que pagaron, **132 habían visto la solicitud pero no la parte_4** en esa ronda, y **34 nunca
habían visto la solicitud antes de pagar** (probablemente porque el `;` se la tragó).

Esto no es cooperación costosa con un desconocido: es, en su mayor parte, **un intento de canje
para conseguir la propia parte**, en una escena donde el recurso la entrega sin necesidad de pagar.
El código de texto ya lo insinuaba (13/182 lo decían explícitamente como canje); el análisis de
contexto lo cuantifica en 132/182.

## Qué NO invalida

- La **sustitución** (quien ayuda pierde su tarea: −19,2 [−26,5; −12,4]). El defecto no la explica;
  si acaso la atenúa, porque los afectados son los que más pagan.
- El **desglose de los tres mecanismos** (mecánico, abandono, fricción) sobre el control a precio 0,
  que no depende del separador.
- La **nota metodológica de la ronda 1**.
- Los nulos (falsificación cero, sin efecto colectivo).

## Qué queda en entredicho

- **El primario pareado 20−5**: significativo con todos, **no significativo** al quitar los agentes
  cuyo `curl` perdió salida, con las dos reglas de marcado.
- **Las tasas por precio** (27,6% y 20,2%): infladas respecto al control arreglado (7,3%).
- La lectura de "cooperación costosa" como disposición: buena parte del pago es instrumental.

## Recomendación para el reporte

1. Reportar el primario **con las dos lecturas** (con todos y sin afectados) y decir que la
   significancia no sobrevive a la corrección. No elegir una y callar la otra.
2. Presentar el control `control-parte4` como la medición con el instrumento arreglado: es la
   estimación honesta de la tasa, y es ~la mitad.
3. Mover el peso del reporte a lo que **no** depende del defecto: la sustitución y el abandono, y la
   nota metodológica de agregación.
4. Declarar el defecto en el apéndice de límites con esta tabla.
