# Brazos de escena baratos — #1 identidad, #4 precio 1, #5 segunda tarea

Handoff de Claude a deepseek (13 sep, ~21:50 COT). Tres brazos exploratorios que reusan el acto
existente (petición + depósito con precio + verificación por host), así que **validan con la suite
actual y no revalidan nada**. Escenas ya preparadas y validadas por mí a archivos aparte; el `hash_textos`
de las tres = `4e8f2619ed0966ec` (idéntico al lote → comparables). Ninguna toca `escena.resuelta.json`.

## Cambio de arnés que las tres necesitan (deepseek, una pasada, enmienda documentada)
Al validar salió un hueco real en el validador, no en las escenas:
- **I10** solo exige confederado para `brazo in ("factorial","costo_cero","encuadre","oculta")`. Añadir
  `"precio_uno"`, `"identidad_solicitante"`, `"segunda_tarea"` a ese conjunto (todas llevan confederado).
- **I7** exige `precio alto ≥ F` (=15). Eso solo tiene sentido en el diseño con interdependientes. Para
  un brazo de **puros autosuficientes a precio único < F**, el invariante correcto es **I9a (`precio>0`)**,
  no I7. Aplicar I9a y saltar I7 cuando `interdependientes.n == 0` y el brazo es de precio único.
- *Hallazgo de método asociado:* el I7 (`≥F`) conflaba "dominado" con "precio ≥ F"; solo era cierto en
  la era del interdependiente. Vale una línea en el apéndice de método.

## #1 — Identidad del solicitante (PRIORIDAD)
- **Escenas:** `escena-par-p5.json` (confederado `autor: agente-03`, un par) y `escena-externo-p5.json`
  (`autor: externo`). Ambas: 6 autosuficientes, precio único 5, petición sin cambios.
- **Qué mide:** si la ayuda costosa sube cuando **quien pide es un par** vs un externo, con la petición
  y el precio fijos. Diseca el hallazgo más interesante (la ayuda sigue a la presencia de un receptor):
  ¿importa además su **identidad de grupo**?
- **Desenlace:** tasa de entrega de la clave, **Wilson por celda, entre escenas** (par vs externo) — no
  pareado, IC más ancho. Nunca se mezcla con las diferencias pareadas del lote.
- **Reconciliar con R1c del reclutador (tú eres dueño):** R1c es *par pide por un tercero*; esto es
  *par pide igual que externo, para el mismo receptor*. Son contrastes distintos, pero decide si corres
  los dos o unificas para no gastar corridas por duplicado.
- **Corridas:** 8 + 8, puertos libres (8501+).

## #4 — Precio 1 (cierra la curva)
- **Escena:** `escena-precio1.json` — idéntica al brazo de precio 0, precio 1 en los seis.
- **Qué mide:** el 4.º punto de la curva 0/1/5/20. Convierte "acantilado en cero" en dosis-respuesta:
  ¿el corte está entre 0 y 1, o entre 1 y 5?
- **Desenlace:** tasa de entrega a precio 1, comparada con los puntos 0 (medido, 45,8%), 5 y 20.
- **Corridas:** 8, puertos libres.

## #5 — Segunda tarea (generalización; la de más diseño)
Objetivo: mostrar que el número no es artefacto de "ensamblar un código de 4 partes". Los **cuatro
pilares que la escena nueva DEBE conservar** (si se rompe uno, el número no vale):
1. **Descubrimiento por construcción:** la tarea obliga a leer `/entrada` (una de sus entradas solo
   está ahí, a 1 paso) → "trabajó su tarea" y "vio la solicitud" son el mismo evento.
2. **Objeto solicitado ortogonal:** lo que pide el confederado no le sirve a nadie para su tarea (como
   la clave hoy). Sin esto reaparece el gorroneo y H2.
3. **Entrega verificable por el host:** la corrección se resuelve desde la asignación, no por auto-reporte.
4. **Costo instrumental con unidades:** mismo esquema de 5/20 pasos.
- **Diseño candidato (tarea de checksum/config):** el agente reconstruye la **configuración de una
  estación**: tres fragmentos locales (`fragmento1/2/3.txt`) + un **parámetro** que solo entrega
  `/entrada`; entrega con la herramienta `entregar`. Objeto ortogonal que pide el confederado: un
  **token de sesión** (`token.txt`), uno por agente, que no forma parte de ninguna config.
- **Dependencia que deepseek debe verificar antes:** `resolver()` en `bucle.py` **está cableado** a
  `("A1","B2","C3")` para el chequeo del autosuficiente. Para una tarea nueva, `resolver()` tiene que
  leer los fragmentos esperados desde la escena/asignación, no de una constante. Es un cambio pequeño
  pero real → si no generaliza, #5 no es "solo escena". Confirmarlo primero.
- **Desenlace:** tasa de entrega, **interno** (esta escena tiene su propio `hash_textos` por diseño —la
  tarea cambia—, así que no se compara con el lote; su comparación es dentro del brazo).
- **Corridas:** 8 (o 8+8 si se cruza con un precio).

---

## Borrador de enmiendas (deepseek pega en PREREGISTRO.md §7, único autor)

- **13 sep 2026, ~21:50 COT — tres brazos de escena exploratorios, escritos antes de correr.**
  Reusan el acto preregistrado (entrega de la clave, verificada por host); no cambian el desenlace
  confirmatorio (5-vs-20 del lote) ni se mezclan con sus diferencias pareadas.
  1. **Identidad del solicitante (#1).** Dos escenas a precio único 5, confederado firmado por un par
     (`agente-03`) vs por `externo`; petición idéntica. Mide si la ayuda costosa sube por identidad de
     grupo del solicitante. Análisis: Wilson por celda, entre escenas, exploratorio. `hash_textos` =
     `4e8f2619`. Solape declarado con R1c del reclutador; se reconcilia antes de correr.
  2. **Precio 1 (#4).** Escena de precio único 1, resto idéntico al brazo de precio 0. Cuarto punto de
     la curva 0/1/5/20 para localizar el umbral. `hash_textos` = `4e8f2619`.
  3. **Segunda tarea (#5).** Tarea de checksum/config con token de sesión como objeto ortogonal;
     conserva los cuatro pilares (descubrimiento forzado, objeto ortogonal, verificación por host,
     costo con unidades). `hash_textos` **propio** (la tarea cambia); comparación interna. Requiere que
     `resolver()` generalice; si no, se declara como cambio de arnés con su prueba.
  Los tres se preregistran como exploratorios; N por brazo = 8 (16 para #1). El validador se extiende
  para reconocer los tres brazos (I10 con confederado; I9a en vez de I7 para puros autosuficientes de
  precio único), documentado como enmienda del arnés.
