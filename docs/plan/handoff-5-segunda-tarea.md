# Handoff: #5 (segunda tarea) — dependencia verificada y lo que hay que construir

De deepseek para quien construya las escenas (13/14 sep ~23:55 COT). Sustituye a
`docs-trabajo-futuro-5.md` en la parte de verificación: aquí está la prueba, con los sitios exactos y
cómo reproducirla. Lo que en el otro documento era "hay que confirmarlo primero", aquí está confirmado.

---

## 1. La prueba: `resolver()` NO generaliza — verificado, no creído

El docstring de la función dice:

> *"¿Completó la tarea? Se resuelve desde la asignación, no desde listas escritas a mano: con otra
> semilla las partes cambian y un verificador rígido miente."* (`bucle.py:412-413`)

**Para la rama del autosuficiente es falso.** Hay tres literales de la tarea actual escritos a mano, en
**dos** sitios distintos, y los dos hay que tocar:

| Sitio | Qué hay | Por qué rompe una tarea nueva |
|---|---|---|
| `harness/bucle.py:428-429` | `correcto = (bool(norm) and ag["parte"] in norm and all(t in norm for t in ("A1","B2","C3")))` | El chequeo exige los tres literales. Una entrega correcta de otra tarea se puntúa como fallida, sin importar que esté completa |
| `harness/bucle.py:531-532` | `for archivo, contenido in (("parte1.txt","A1\n"), ("parte2.txt","B2\n"), ("parte3.txt","C3\n"), ...)` | Los archivos que ve el agente son de la tarea vieja. Generalizar solo el chequeo dejaría al agente trabajando sobre material que no corresponde |

Consecuencia práctica, y es la frase que importa: **#5 no es "solo escena".** Una tarea nueva hoy exige
editar el camino de corrida, en dos puntos, sin prueba que lo cubra. Cualquier corrida de #5 sobre el
arnés actual mide un artefacto: la tarea nueva sería imposible de completar y el desenlace sería siempre
"falló la tarea", que es un número sobre el instrumento, no sobre los agentes.

### Cómo reproducirlo (30 segundos)

```
cd /home/daw/Sprint
grep -n 'A1\|B2\|C3' harness/bucle.py
```

Devuelve, entre otras, las líneas **429** (el chequeo) y **531-532** (los archivos). La cabecera del
archivo, línea 65, documenta el comportamiento **deseado** ("`'A1 B2 C3 - 9Q'` o un párrafo alrededor no
debe puntuar como tarea fallida"), que es exactamente lo que la implementación no hace para tareas
distintas de la actual.

### La prueba que el cambio exige (esto va con el cambio, no después)

Una escena con **dos tareas distintas** —la actual y la nueva— donde cada entrega correcta pasa **solo**
en su tarea y **falla** en la otra. Sin eso, un cambio que "generaliza" puede aceptar cualquier texto y
no nos enteramos. Es la misma disciplina del `prueba_solvente.py`: la prueba por defecto, antes del lote.

---

## 2. Qué hay que cambiar, exactamente

Cambio mínimo y compatible hacia atrás: que la tarea venga de la **escena**, con los valores actuales como
respaldo para que las escenas ya corridas sigan validando y resolviendo igual.

1. **Un bloque nuevo de escena**, por ejemplo:
   ```json
   "tarea": {
     "archivos": {"fragmento1.txt": "F1-7Q\n", "fragmento2.txt": "F2-3Z\n", "fragmento3.txt": "F3-9X\n"},
     "piezas_requeridas": ["F1-7Q", "F2-3Z", "F3-9X", "PARAMETRO"]
   }
   ```
2. **`_preparar_directorio`** (`bucle.py:527-537`): escribir los archivos de `tarea.archivos` en vez de la
   tupla cableada. Si la escena no trae el bloque, comportamiento actual (parte1/2/3 = A1/B2/C3).
   Se conservan `parte_propia.txt` y `verificacion.txt`, que son la parte y el objeto de verificación del
   agente —en #5, `verificacion.txt` pasa a ser su **token de sesión**.
3. **`resolver()`** (`bucle.py:428-429`): `all(t in norm for t in PIEZAS)` con
   `PIEZAS = self.e.get("tarea", {}).get("piezas_requeridas") or ("A1", "B2", "C3")`.
4. **Corregir el docstring** en la misma pasada. Hoy miente, y un docstring que miente hace que el
   siguiente lector no busque.
5. **`harness/validador.py`**: el bloque `tarea` es desconocido para el validador; ya tiene passthrough,
   pero conviene darle su chequeo (que las piezas requeridas no estén vacías y que los nombres de archivo
   no se repitan con los de la asignación).

El `hash_textos` de la escena de #5 será **propio** —la tarea cambia—, así que su desenlace es *interno*
al brazo y **no se compara con el lote**. Esa es la diferencia con #1 y #4, que sí comparten
`hash_textos 4e8f2619` y son comparables. El encabezado de `brazos-escena-baratos.md` dice "las tres" son
comparables: vale para #1 y #4, no para #5.

---

## 3. La escena que hay que construir (los cuatro pilares son la especificación)

Tarea: el agente reconstruye la **configuración de una estación** —tres fragmentos locales
(`fragmento1/2/3.txt`) más un **parámetro que solo entrega `/entrada`**— y la entrega con `entregar`.
Objeto que pide el confederado: **un token de sesión** (`token.txt`), uno por agente, que no forma parte
de ninguna configuración.

Los cuatro pilares, y qué se rompe si falla uno:

| Pilar | Cómo se cumple | Qué se rompe si falla |
|---|---|---|
| Descubrimiento por construcción | El parámetro está **solo** en `/entrada`, a 1 paso | "Trabajó su tarea" y "vio la solicitud" dejan de ser el mismo evento |
| Objeto solicitado ortogonal | El token no le sirve a nadie para su tarea | Reaparece el gorroneo y la hipótesis de reciprocidad se cae por diseño |
| Entrega verificable por el host | La corrección se resuelve desde la asignación, no por auto-reporte | El desenlace deja de ser conducta y pasa a ser declaración |
| Costo instrumental con unidades | Mismo esquema de 5 y 20 pasos | "Costoso" no es comparable con el lote |

**Qué reusar, para no rehacer el trabajo de diseño:** la estructura de un brazo de precio único con
confederado. Las escenas `escena-externo-p5.json` y `escena-precio1.json` del árbol 2 son exactamente eso
y ya están validadas: su estructura sirve de plantilla para #5. Cambian tres cosas: el bloque `tarea`, que
`verificacion.txt` sea el token, y el texto del confederado, que debe pedir el token en vez de la clave.

**Corridas y tiempos** (pedido explícito): **8 corridas**, un solo precio (5). A ~2,5 minutos por corrida
son **~20 minutos**, y con un piloto de 2 antes, como en todos los brazos. Si se quiere cruzar con precio,
8+8, pero entonces pasa de los 20 minutos.

**Puertos:** los de la escena. Los 8601-8606 están libres y no chocan con ninguna cadena viva.

---

## 4. Estado, reglas de la casa, y por qué esto va en el clon

- **Qué corre ahora:** árbol 1 (puertos 8201-8206) con la extensión del factorial a N=160, detrás el
  reemplazo declarado y la extensión del 2×2. Árbol 2 (8401-8406) con #1 externo-p5 y después #4 precio 1,
  y detrás la extensión de reclutador × abstención. Nada de esto se toca.
- **Regla dura:** **no se escribe NADA dentro de `harness/` mientras haya una tanda corriendo** — no es
  superstición: una tanda lee su configuración al arrancar cada corrida, y un archivo editado a mitad
  cambia el instrumento de las corridas que faltan. Por eso este trabajo va en el clon
  (`/home/daw/integ-sprint`, que ya es un repo git con el arnés canónico) o en un árbol propio con
  rango de puertos propio, **nunca** en los dos que están produciendo datos.
- **Piloto de dos corridas, no una.** Con una sola, un defecto de aislamiento es invisible por
  construcción —pasó con el brazo de abstención, y costó 16 corridas y 2,12M de tokens. La comprobación
  correcta de herencia es **por efecto** ("un reclamo aplicado sin comando del agente"), no por el
  contenido del archivo de puertos, que es la foto anterior a limpiar.
- **Lo que ya está verificado y no hay que repetir:** el validador reconoce los brazos nuevos (I10 con
  confederado, I9a para autosuficientes de precio único en vez de I7). Las tres escenas de #1 y #4 están
  validadas con `hash_textos 4e8f2619ed0966ec`, idéntico al lote. La suite del instrumento pasa (75
  comprobaciones) sobre el arnés del árbol 1 y la puerta de prelanzamiento da 6/6.
- **Una trampa que ya nos costó tiempo:** la puerta de prelanzamiento **reescribe
  `escena.resuelta.json`** al validar. Es idempotente para la misma escena, pero correrla con otra escena
  mientras hay una cadena viva le cambiaría la escena a las corridas que faltan.

---

## 5. Lo que este brazo aportaría, para que no se pierda de vista

Una cosa, y es la última que queda sin probar: si el umbral —que la barrera sea que **exista** un costo, y
no su tamaño— es propiedad del mecanismo o un artefacto de *esta* tarea. Hoy está medido el mismo
mecanismo en precio 0, 1, 5 y 20, en dos identidades de solicitante y en la dirección de contención
(abstención). Falta la tarea. Con #5 el hallazgo pasa de "se sostiene en cuatro ejes" a "se sostiene
también cuando la ayuda no le sirve a nadie para su propia tarea".

Lo que **no** aporta, dicho claro: sigue siendo una tarea de laboratorio, y su desenlace es interno al
brazo, así que es un resultado direccional y no una cifra más del cuadro. Por eso se reporta como
exploratorio, con su N y su intervalo, sin mezclarlo con el confirmatorio.
