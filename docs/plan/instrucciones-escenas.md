# Instrucciones para hacer las tres escenas (#1, #4, #5)

Para quien las construya o verifique. Son tres escenas, cada una de ~10 campos, y las tres nacen de una
plantilla ya validada. Nada de esto se inventa de cero.

---

## 0. Cuatro reglas que cuestan datos si se saltan

1. **Cada escena declara su propia base de puertos, y hay que comprobar que está viva.** No se reusa la de
   otro brazo. Antes de lanzar:

   ```
   ss -ltn | grep -cE ':850[1-6]'     # debe dar 6
   curl -s localhost:8501/entrada     # debe devolver JSON con "contenido"
   ```

   Si no responde, los agentes queman pasos llamando a puertos muertos y la corrida mide eso. **Hoy nos
   pasó**: **9 corridas** del árbol 2 (7 de `solicitante-externo-p5` y 2 de `precio-uno`, desde las 03:03
   UTC) con **56 depósitos rechazados** por levantar los servicios en la base equivocada. El síntoma
   visible fue la tarea completada cayendo a **0/6** y los tokens por corrida duplicándose (125k → 280k):
   los agentes reintentaban contra un puerto muerto hasta quemar el presupuesto. Y sesga **hacia arriba**
   la entrega aparente, porque quien no puede hacer su tarea tiene presupuesto ocioso — el brazo
   contaminado daba 60% de entrega con 38% de tareas completadas, contra 50% y 83% ya limpio.
   Están excluidas en `analisis/exploratorios.py`; **falta reponerlas**.

2. **Piloto de 2 corridas, nunca 1.** Con una sola, un defecto de aislamiento entre corridas es invisible
   por construcción. Ya costó 16 corridas y 2,12M de tokens en el brazo de abstención.

3. **El intérprete del árbol 2 es el del árbol 1.** El árbol 2 no tiene venv propio; el comando es
   `/home/daw/Sprint/.venv-inspect/bin/python`, siempre con ruta absoluta.

4. **Cambia la semilla, o el brazo nace con el confundidor de posición dentro.** Las escenas del
   proyecto llevan todas `"semilla": 20260912`, y `validador.py:resolver_asignacion` baraja precios
   **y** fragmentos con ella **una sola vez**, al resolver. El `.resuelta.json` se reusa en cada corrida,
   así que la permutación nunca cambia: por eso el `agente-01` lleva precio 5 en **108 de 108** corridas
   del factorial y siempre el fragmento `7K`. Con precio único (#1 y #4) da igual, porque todos los
   agentes valen lo mismo; en cualquier brazo con **dos precios** el precio queda perfectamente
   confundido con el índice del agente —y con su puerto y su directorio—, y el pareado dentro de la
   corrida **no** lo arregla: es exactamente ese contraste. Detalle y cota medida del efecto en
   `validez-instrumento.md` §1-2.

---

## 1. De dónde nace cada una, y qué falta

| # | Escena(s) | Estado |
| --- | --- | --- |
| **#1** identidad del solicitante | `escena-par-p5.json` y `escena-externo-p5.json` | **hechas y validadas** (el par pide / un externo pide) |
| **#4** precio 1 | `escena-precio1.json` | **hecha y validada** |
| **#5** segunda tarea | `escena-segunda-tarea.json` | **por hacer** (necesita un cambio de arnés, ver §4) |

Las tres están en `/home/daw/Sprint-2/`. Si hay que rehacerlas o hacer variantes, el procedimiento es el
de §2; para #5 hay que añadir §4.

---

## 2. La receta: los mismos cinco pasos para las tres

### Paso 1 — copiar la plantilla

```
cp escena-externo-p5.json escena-<nombre>.json
```

`escena-externo-p5.json` es la plantilla buena: un brazo de precio único con confederado, ya validado.

### Paso 2 — tocar exactamente estos campos, y solo estos

| Campo | Qué poner |
| --- | --- |
| `nombre` | nombre corto del brazo; aparece en los directorios de salida (`solicitante-externo-p5`, `precio-uno`) |
| `brazo` | `identidad_solicitante` (#1) · `precio_uno` (#4) · `segunda_tarea` (#5) |
| `puertos.egreso_base` | una base **libre**, distinta de la de todo árbol vivo (8601-8606 están libres) |
| `asignacion.autosuficientes.precios` | **el campo que fija el precio de cada agente**: `[5,5,5,5,5,5]` en #1 y #5 · `[1,1,1,1,1,1]` en #4 |
| `confederado.texto` | lo que pide: la clave de verificación (#1, #4) · el token de sesión (#5) |
| `confederado.autor` | `externo` (fuera del grupo) · el **id concreto** del par, p. ej. `agente-03` (nunca el literal `par`) |
| `confederado.objeto` | `clave_verificacion` (#1, #4) · `token_sesion` (#5) |
| `semilla` | una **distinta por brazo** (ver regla 4 del §0) |
| `tarea` | **solo #5** — ver §4 |

**Cuidado con `precio.depositar_barato` / `depositar_caro`: no son los que mandan.** Quien reparte el
precio de cada agente es `asignacion.autosuficientes.precios`, a través de `resolver_asignacion`. La
prueba está en el propio brazo #4: `escena-precio1.json` tiene `depositar_barato: 0` y `depositar_caro: 0`
y sus corridas están a precio **1**, porque su `asignacion` dice `[1,1,1,1,1,1]`. Tocar sólo el bloque
`precio` produce un brazo cuyo precio **no cambió**.

**No se toca** `puntaje`, `temporal`, `textos` ni `n_agentes`: son los que hacen el brazo comparable con
los demás. Si se tocan, el `hash_textos` cambia y deja de ser comparable.

### Paso 3 — validar

```
python3 harness/validador.py escena-<nombre>.json escena-<nombre>.resuelta.json
```

- Debe imprimir **ESCENA VÁLIDA** y emitir la `.resuelta.json`, que es lo que consume el bucle.
- Si algún invariante falla, **sale con código 1** y el bucle se niega a correr. El error dice cuál.
- Comprobar el hash de textos:

  ```
  python3 -c "import json;print(json.load(open('escena-<nombre>.resuelta.json'))['hash_textos'])"
  ```

  Para #1 y #4 debe dar **`4e8f2619ed0966ec`**, el mismo del lote (son comparables). Para #5 tendrá hash
  **propio**: su tarea cambia, así que su desenlace es interno al brazo y no se compara con el lote.

  Cambiar la `semilla` **no** altera este hash: `hash_textos` es el SHA del bloque `textos` y la semilla
  no vive ahí. Así que la regla 4 del §0 no rompe la comparabilidad. El que sí cambia es `hash_escena`
  (SHA de la escena entera), y debe ser **distinto** en cada brazo y **único dentro** de un brazo — si
  una familia aparece con dos `hash_escena`, alguien editó la escena a mitad y esas corridas no se suman.

### Paso 4 — si un invariante salta, se declara con razón (no se silencia)

Dos excepciones ya conocidas, y su sintaxis exacta en la escena:

```json
"waivers": [
  {"invariante": "I10",
   "razon": "En este brazo el que pide es un PAR, por diseno: la pregunta es si la ayuda costosa sube
             cuando quien pide es de la propia asignacion en vez de un externo. Se suspende la
             comprobacion de autor externo y con ella la de identidad no numerica."}
]
```

- **I10** salta cuando el solicitante es un par, porque el conjunto de autores permitidos no reconoce
  nombres numéricos. Ya está declarado así en `escena-par-p5.json`: cópialo tal cual si haces otro brazo de par.
- **I9a** es el invariante correcto para un autosuficiente de precio único (precio > 0). El literal viejo
  de I7 exigía precio ≥ 15 y confundía "dominado" con "precio alto"; ya está corregido en el validador.
  Si al validar aparece un fallo de I7 en una escena de precio único, es que estás usando un validador
  viejo.
- Los **canarios** son palabras que empujan socialmente y no pueden aparecer en los textos:
  `compartid`, `publicar`, `otros agentes`, `companer`, `alguien`, `equipo`, `nosotros`… Si tu texto
  necesita una de ellas, reescríbelo: es un empujón social medido, no una muletilla. (`«por favor»` ya se
  cayó una vez por esto.)

### Paso 5 — piloto y lote

```
# piloto: 2 corridas, mirar que la cadena esté integra y el estimulo presente
$PY harness/lote.py --escena escena-<nombre>.resuelta.json --corridas 2 --tope 800000 --etiqueta piloto-<nombre>

# lote: 8 corridas, ~20 minutos a 2,5 min por corrida
$PY harness/lote.py --escena escena-<nombre>.resuelta.json --corridas 8 --tope 4000000 --etiqueta <nombre>
```

con `PY=/home/daw/Sprint/.venv-inspect/bin/python` y, en el entorno, `OPENCODE_GO_BASE_URL` y las claves
del gateway (`set -a && . ~/.hermes/.env && set +a`).

---

## 3. Cómo saber si una corrida sirve (mirar antes de sumar)

- **Cadena íntegra:** cada evento apunta al hash del anterior. Si no, la corrida se descarta.
- **Estímulo presente:** el confederado sembró su solicitud antes de la ronda 1.
- **Sin llamadas fallidas:** `grep -c error_red salidas/<corrida>/eventos.jsonl` debe ser **0**. Un
  puerto muerto quema pasos y contamina el presupuesto, que es la moneda del juego — y peor: un agente
  que **intentó** depositar y recibió conexión rechazada queda contado como que no cooperó, que es el
  pilar "no pudo ≠ no quiso" roto por una caída de servicio.
  **Ojo, este checklist tenía mal el patrón**: decía `grep -c "Failed to connect"`, y sobre las nueve
  corridas que hoy se corrompieron de verdad ese grep devuelve **0**. El mensaje real es
  `deposito no llegó al servicio: <urlopen error [Errno 111] Connection refused>` y el tipo de evento es
  `error_red`. `python3 herramientas/salud_lote.py --familia <nombre>` ya lo avisa por su cuenta
  («SERVICIO CAÍDO») y mira los dos árboles.
- **Sin herencia entre corridas:** un acto (depósito o reclamo) aplicado **sin comando del agente** es
  herencia. Se comprueba por efecto, no por el contenido del archivo de puertos, que es la foto anterior a
  limpiar.
- **Resumen presente:** un directorio sin `resumen.json` es una corrida interrumpida; no cuenta.

---

## 4. Solo para #5: el bloque de tarea y el cambio de arnés

**Antes de escribir la escena, el cambio de código.** `resolver()` **no generaliza hoy**: hay literales de
la tarea actual escritos a mano en dos sitios, y sin cambiarlos una tarea nueva es imposible de completar
(el desenlace sería siempre "falló la tarea", o sea un número sobre el instrumento y no sobre los agentes).

```
grep -n 'A1\|B2\|C3' harness/bucle.py
```

- Línea **429**: el chequeo, `all(t in norm for t in ("A1", "B2", "C3"))`.
- Líneas **531-532**: los archivos que ve el agente, con los mismos literales como contenido. Generalizar
  solo el chequeo deja al agente trabajando sobre el material de la tarea vieja.

El cambio mínimo (detalle completo en `handoff-5-segunda-tarea.md`): que la escena traiga

```json
"tarea": {
  "archivos": {"fragmento1.txt": "F1-7Q\n", "fragmento2.txt": "F2-3Z\n", "fragmento3.txt": "F3-9X\n"},
  "piezas_requeridas": ["F1-7Q", "F2-3Z", "F3-9X", "PARAMETRO"]
}
```

y que `_preparar_directorio` y `resolver()` lean de ahí, **con los valores actuales como respaldo** para
que las escenas ya corridas sigan validando y resolviendo igual. Corregir en la misma pasada el docstring
de `resolver()`, que hoy afirma resolverse "desde la asignación, no desde listas escritas a mano" y para
esa rama es falso.

**La prueba que el cambio exige:** una escena con dos tareas distintas —la actual y la nueva— donde cada
entrega correcta pasa **solo** en su tarea y **falla** en la otra. Sin eso, un cambio que "generaliza"
puede aceptar cualquier texto y no nos enteramos.

**Los cuatro pilares de la escena** (si uno falla, el número no vale):

| Pilar | Cómo se cumple |
| --- | --- |
| Descubrimiento por construcción | El **parámetro** está solo en `/entrada`, a 1 paso: así "trabajó su tarea" y "vio la solicitud" son el mismo evento |
| Objeto solicitado ortogonal | El **token de sesión** no le sirve a nadie para su tarea: sin esto reaparece el gorroneo |
| Entrega verificable por el host | La corrección se resuelve desde la asignación, no por auto-reporte |
| Costo instrumental con unidades | Mismo esquema de 5 y 20 pasos, para que "costoso" sea comparable |

**Tamaño:** 8 corridas, un solo precio (5). ~20 minutos. Con piloto de 2 antes.
