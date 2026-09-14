# Revisión de solo lectura del código de análisis contra el preregistro (13 sep, 15:25 COT)

Leído, no ejecutado: `harness/estimador.py`, `mini_analisis.py`, `codificacion.py`, y
`PREREGISTRO.md` §2 y §8. Nada de esto toca el lote.

## Lo que está bien
- `estimador.py` **nunca mezcla versiones del instrumento**: agrupa por (hash de escena, hash de
  textos, brazo, etiqueta). El mini-piloto (misma escena, carpeta `ensayo-mini-piloto`) y el lote-a
  (otro hash) quedan separados del lote final. Correcto y es lo que pide el plan.
- **Diferencia pareada por corrida** (tasa a 20 menos tasa a 5, dentro de cada corrida) y bootstrap
  **por corrida**, 10.000 remuestreos, semilla fija. Es el primario tal como está preregistrado.
- Excluye corridas que no tengan 6 agentes.
- `mini_analisis.py` mide la cadena de saliencia (leyó el almacén → mencionó la solicitud → leyó su
  clave → depositó) y la taxonomía del depósito; `codificacion.py` codifica H6/H6b/H7 con planilla
  ciega. Cubren los secundarios preregistrados.

## Cuatro cosas que corregir antes de las 17:00 (ninguna requiere tokens)

### 1. El preregistro dice tres cosas distintas sobre el primario
- §2 (línea ~108): "tasa de depósito — binaria por agente (**depositó al menos una vez**)" → eso es
  la **unión**.
- Enmienda de las 11:50 (A1): "el acto medido es el mismo en el primario y en la puerta: **depositar
  LA CLAVE**; la unión y la fracción quedan descriptivas".
- Enmienda de las 14:10: reporta "las dos definiciones … porque **la decisión de cuál es el primario
  sigue pendiente** en el equipo".
Con el lote a medias, esto es exactamente la puerta a "escoger la medida por su veredicto". Arreglo,
por el único autor de `PREREGISTRO.md`: (a) §2 → "tasa de respuesta a la solicitud
(`deposito_clave`)"; (b) en la enmienda de las 14:10, sustituir "sigue pendiente" por "resuelta por
A1 a las 11:50: primario = clave; la unión se reporta como descriptiva". Sin esto, `estimador.py`
imprime dos primarios y el reporte puede elegir.

### 2. `estimador.py` no aplica las exclusiones por fallo técnico
Lee `resumen.json` y descarta solo corridas con ≠6 agentes. **No consulta la validez que calcula
`agregar.py`** (saldo negativo, depósito HTTP no contado, truncada por tope, sin estímulo). El §4
del preregistro dice que la exclusión es solo por fallo técnico comprobable — y esos son los
fallos. Arreglo: que `estimador.py` lea `reportes/factorial.json` (o recalcule los mismos cuatro
chequeos) y excluya las corridas con `valida == False`, **reportando cuántas y por qué**, antes
de calcular nada. Hoy, una corrida truncada entraría al bootstrap como si fuera completa.

### 3. Los intervalos por celda (Wilson) son a nivel de agente
`celda()` calcula Wilson sobre los agentes agrupados (n = 3 × corridas), como si fueran
independientes. Los tres agentes de un precio en una corrida ven el mismo almacén; el plan dice
"remuestreando por corrida y no por agente, para no inflar N". El bootstrap del **contraste** sí
es por corrida; los intervalos de las **tasas por celda** que irían en la Tabla 1 y la Figura 2,
no. Arreglo: bootstrap por corrida también para cada tasa de celda (remuestrear corridas, recalcular
la tasa), o etiquetar el Wilson como "ingenuo, a nivel de agente" y no dibujarlo.

### 4. Las corridas de precio 0 necesitan su propia rama
`brazo` se decide por el nombre de la carpeta (`costo-cero`); con precios 0/0 no hay diferencia
pareada y el script solo reporta celdas. Está bien, pero la curva de tres puntos (0/5/20) necesita
que el 0 salga **de la misma escena y hash** que el 5 y el 20 — la enmienda de las 14:35 ya lo exige.
Arreglo: al agrupar, unir el brazo `costo-cero` con el factorial cuando `hash_textos` coincida salvo
por los precios, y rechazar explícitamente el precio 0 del hash viejo (`10e4f86e…`) con un mensaje,
no en silencio.

## Menores
- `etiqueta` se infiere del subdirectorio; las corridas del lote final van en la raíz de `salidas/`
  y quedan con etiqueta vacía. Funciona, pero es frágil: mejor leer la etiqueta del `lote_*.json`.
- `codificacion.py` y `mini_analisis.py` leen `transcripciones/*.json` dentro de cada corrida:
  comprobado, el lote final sí las escribe (`salidas/<corrida>/transcripciones/`). Sin problema.

## Qué haría yo
Los cuatro puntos son de código de análisis, no de arnés, así que se pueden arreglar y probar
**ahora** contra `ensayo-mini-piloto/` y `lote-a` sin tocar el lote. El punto 1 es el más importante y
es de una línea en cada sitio.
