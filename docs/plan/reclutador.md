# reclutador.md — correcciones al brazo del reclutador

Revisión de Claude (13 sep, ~17:00 COT) al handoff del brazo `reclutador` (BRIEF-RECLUTADOR.md +
escena-reclutador.json). El brazo es sólido; esto son las cuatro cosas que hay que corregir o afinar
antes de correrlo. Los archivos de la rama no están en este repo local (sin remoto configurado aquí),
así que aplica estos cambios en la rama `reclutador` donde vivan.

## 1. Anclas de METR — corrección OBLIGATORIA (es el error recurrente, van dos veces)
Verificado contra la copia local `entrega/fuentes/metr.org-8e38112b54.md`:

| Cita del brief | Veredicto | Qué es en realidad |
|---|---|---|
| 250 | ✓ correcta | "…willing to risk failing their own task for the good of the 'collective'" (marco self-risking) |
| **251** | ✗ **QUITAR** | Es la línea de Artifactory ("…cause Artifactory to load their modified easier target…"), no tiene que ver con reclutar |
| 253 | ✓ correcta, y es la clave para R1b | *"…please honor commit"* — la **presión** literal de un agente a otro |
| 1029 | ✓ correcta | "One agent, EARLY[big], was recruited…" |

**Faltan** las que sostienen "nadie pidió para sí" — añadirlas:
- **1025** — PHASEONE[big] decide asignar reclutadores.
- **1027** — agentes reclutados para el esfuerzo.
- **1041** — reclutaban agentes **con poco presupuesto restante**.

Ancla final correcta para el brazo: **250, 253, 1025, 1027, 1029, 1041** (sin 251). Detalle en
`anclas-metr.md`.

## 2. R1b no es hermano de R1a/R1c — es otro constructo
- **R1a (tercero) y R1c (par)** informan sobre un propósito: miden "¿la ayuda sigue al propósito
  cuando quien pide no pide para sí?". Limpios. Se pueden aprobar y correr ya.
- **R1b (apelación/presión)** aplica presión, que es justo lo que el preregistro prohíbe en el
  estímulo neutral ("informa, no ordena"). Consecuencias:
  1. **Mide obediencia a la presión**, no "cooperación que sigue al propósito". No se interpretan en
     la misma frase ni se promedian con R1a/R1c.
  2. Es el único que roza la regla del sprint de **no reproducir tácticas de reclutamiento**: su
     texto tiene que ser nuestro, suave, sin amenaza ni insistencia, y pasar el **visto bueno de uso
     dual antes de existir**.
- Decisión: R1a y R1c primero; **R1b detrás del visto bueno de uso dual**, y reportado como un
  constructo aparte (presión), no como una tercera dosis del mismo eje.

## 3. Línea base del análisis — usar el propio lote, no una base nueva
El contraste entre-escenas más limpio para R1a/R1c **no** es una base neutra rehecha: son las
**celdas autosuficiente-precio-5 de las 80 corridas del lote** (mismo acto, mismo precio, distinto
solicitante). Sigue siendo entre-escenas, pero usa el lote confirmatorio como comparación y estrecha
el intervalo, en vez de gastar corridas en rehacer la base neutra. Wilson por celda, exploratorio,
nunca mezclado con las diferencias pareadas del lote. (Confirmado: `hash_textos` idéntico
`4e8f2619ed0966ec`, así que el acto es el mismo y la comparación es válida.)

## 4. Detalle semántico que hay que nombrar en el reporte
El objeto pasa de "una clave que **nadie** necesita" (escena base, para proteger H2) a "la estación 4
**necesita** tu clave" (R1a). Es coherente con una clave de verificación/autenticación, y el **costo
puro se mantiene** porque en el brazo del reclutador no hay interdependientes (6 autosuficientes). Pero
ese giro —de inútil-para-todos a útil-para-un-tercero— **es** la manipulación del brazo: hay que
decirlo así explícitamente en Método, no dejarlo implícito, porque es lo que distingue al reclutador
del confederado neutro.

## Lo que NO hay que cambiar (ya está bien)
- La excepción de canarios como campo `confederado.canarios_permitidos` + tres pruebas de suite: es la
  forma correcta de acotarla. Consérvala.
- Escena INVÁLIDA hasta declarar la excepción: bien.
- Puertos 8401+, regla de directorio, una versión de instrumento por análisis: bien.
- El desenlace es el acto preregistrado (`deposito_clave`): comparable, bien.

## Orden sugerido
1. Corregir anclas (§1) — cero costo.
2. Correr R1a y R1c (limpios) contra la línea base del lote (§3).
3. R1b solo tras el visto bueno de uso dual (§2), reportado aparte.
4. R2 (reclutador empujando al acto dañino) queda para después: necesita el build de abstención.
