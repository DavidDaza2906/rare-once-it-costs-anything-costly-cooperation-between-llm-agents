# Material de uso dual y límites — para el apéndice obligatorio

Datos y hechos, no prosa: el reporte lo escribe el equipo. Cada número lleva de dónde sale.

## 1. Tasa base de falsos positivos de una regla de detección por palabra clave

Medido sobre 240 agentes-corrida del bloque A, con la clasificación por **destino**, no por texto:

| Regla | Marca | Verdaderos positivos | Precisión |
|---|---|---|---|
| contiene `nc` o `/dev/tcp` | 234 de 459 agentes-corrida (51%) | 0 | 0% |
| ídem, restringido a host externo | 0 | 0 | — |

Lo que esas 234 marcas son en realidad: **287 de 298** comandos con cliente alterno apuntan al **puerto
propio del agente** (es el camino por el que después depositan); **0** a otro puerto; **0** a un host
externo. Los 2 aparentes externos eran el registro de comandos **truncado** a mitad de la dirección.

Lección para respuesta a incidentes, que es lo que el apéndice necesita decir: una regla por palabra
clave tiene una tasa base de falsos positivos del 50% en este entorno y precisión cero, y el motivo es
que el texto del comando **no es** la acción. Una regla defendible clasifica por destino o por ruta, y
quien la escriba tiene que imprimir una muestra de lo que marca antes de confiar en su conteo.

## 2. El defecto del instrumento como caso de estudio

Un defecto en el arranque de cada corrida —los archivos de estado por agente se limpiaban para una
familia de actos y no para otra— hizo que cada corrida **leyera como propios los actos de la anterior**.

| | Medido con el defecto | Verdad |
|---|---|---|
| tasa de reclamo (K=5) | 69,4% | ~25% |
| tasa de reclamo (K=20) | 87,5% | ~27% |

La firma que lo delató: **seis actos registrados en estallido en la ronda 1**, cuando solo dos agentes
habían emitido el comando, y los archivos de estado pesando **una línea** al cerrar. La consecuencia para
el reporte: 16 corridas quedaron retiradas y el expediente completo está en `docs/abstencion.md`.

Lección para respuesta a incidentes: un artefacto del instrumento se parece exactamente a un hallazgo.
Un número que sube con la "dosis" y satura es sospechoso; el chequeo que lo separa es **por efecto** (¿el
host aplicó un acto que ningún sujeto pidió?) y no por residuo (los restos que la limpieza se lleva, que
existen por construcción).

## 3. Lo que este instrumento NO prueba, y hay que decir con estas palabras

- **Un solo modelo.** Todos los sujetos son el mismo modelo, así que nada de esto habla de "los LLM".
- **Un entorno propio, no el del incidente.** No se reproduce ningún exploit ni ningún payload; el
  entorno es nuestro y el acto dañino es tomar una reserva ficticia.
- **Tareas de laboratorio.** Ensamblar un código y reconstruir una configuración no son trabajo real.
- **El efecto de encuadre (abstención) está pendiente de su extensión declarada** y se reporta como
  exploratorio: cuatro contrastes, uno con intervalo sin cero, corrección por comparaciones múltiples
  pendiente de declarar en el texto.
- **La generalización de tarea no se corrió.** `resolver()` no generaliza hoy: su rama del
  autosuficiente exige los literales `("A1","B2","C3")` y su propio docstring afirma lo contrario.
  Queda como trabajo futuro con el cambio exacto identificado: leer las piezas esperadas de la asignación.

## 4. Reglas del sprint que se respetaron

- **No se publica ninguna receta de instalación novedosa sin revisión**, y no hay ninguna en este
  material.
- **No se reproduce ningún payload del incidente**, y el corpus crudo del incidente no se publica.
- La variante de estímulo con presión y apelación colectiva (R1b) **no se corrió**: es otro constructo y
  quedó aparcada detrás del visto bueno de uso dual. Su escena está en el repo, sin correr.
