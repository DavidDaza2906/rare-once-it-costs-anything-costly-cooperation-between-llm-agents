# Notas de trabajo — tesis del reporte y coordinación

Fusión de `ideas.md` + `todo.md`.

---

## A. ideas.md — la tesis que podemos sostener, y con qué

# ideas.md — la tesis que podemos sostener, y con qué

Archivo de trabajo. Los números son del **bloque A** (40 corridas, 240 agentes, mitad del lote): se
recalculan sobre las 80 al cierre. El escrito del reporte es del equipo; aquí van datos, argumento y
fuentes.

---

## Titular candidato

> En un entorno donde ayudar es anónimo, cuesta entre el 12% y el 50% de un presupuesto que nadie
> agota y no le reporta nada al que ayuda, solo **1 de cada 5** agentes ayuda — y **9 de cada 10** de
> los que se niegan podían pagarlo y entregaron su tarea igual: la cooperación costosa de estos
> agentes sigue al **propósito y a la presión, no al precio**.

---

## 1. La barrera es que exista un costo, no cuánto cuesta

    a precios no nulos (5 y 20 juntos) ....  49/240 agentes pagan la clave = 20,4%
    los que se niegan .....................  pasos libres al cierre: mediana 25, media 23,9
    de los que se niegan y SÍ completaron
    la tarea (n=174) ......................  156 (89,7%) tenían saldo para pagar su precio
    de los que se niegan ..................  86,9% acabó con 10+ pasos libres; 75,9% con 20+

La comparación es contra la propia restricción, no contra otro brazo: **no es que no pudieran, es que
no quisieron**. Con saldo de sobra y la tarea entregada en 9 de cada 10 casos, la lectura "ayudarían
si fuera más barato" queda descartada por los datos.

Y esto es lo que lo ata al incidente: allí los agentes **sí** sacrificaron su propia corrida, pero era
instrumental para el colectivo y estaba inducido por un reclutador. Quitando el propósito colectivo y
al reclutador, la conducta se desploma **incluso cuando es barata**. Eso es una tesis sobre el
mecanismo del incidente, no solo un número.

## 2. Un instrumento que un tercero puede verificar (la tesis del Track 1, implementada)

Cita del Track 1 (verificada): *"The gap is not the absence of principles but the absence of checks
somebody can actually run and a third party can actually verify."*

- **40/40 cadenas de hash íntegras**; **0 discrepancias de cobro en 240 agentes**: cada acto anotado
  y cobrado exactamente una vez, verificable recomputando la cadena desde el registro.
- El defecto de **doble cobro** está documentado con su diagnóstico y con la prueba de la suite que
  impide que vuelva (un acto = un cargo, en las dos vías).
- **Contención, y su tasa base de falsos positivos (medida, no supuesta).** De 298 comandos con
  cliente alterno (`nc`, `/dev/tcp`) en 79 corridas: **287 (96%) apuntan al puerto propio y permitido**
  del agente, **0 a otro puerto del sandbox** y **0 a un host externo** (los 2 que parecían externos son
  el registro truncado a mitad de dirección). Un detector ingenuo basado en la palabra `nc` marcaría al
  **53% de los agentes-corrida (234 de 459)** como intento de egreso: **todos falsos positivos**. Es una
  tasa base medida en casa, y es el número que un equipo de respuesta necesita antes de confiar en una
  regla de detección.
- El registro del host es la verdad: identidad por ruta, no por lo que el agente declare.

## 3. La cooperación no es la propiedad de seguridad; lo es la cooperación con propósito y verificada

Caso del objeto credencial: un agente **pagó** (corrida `082841`, precio 5) para publicar que **no**
entregaba su clave por confidencialidad, y no la entregó. No cooperó, y estuvo bien. En el incidente,
los agentes cooperaban **mientras** hacían daño. Conclusión utilizable: una métrica de "cuánto
cooperan" sin propósito no dice nada sobre seguridad.

---

## Por qué un 5 contra 20 plano NO es un fracaso (decirlo antes de verlo)

Los dos brazos cuestan 12,5% y 50% del presupuesto. Si la tasa no se mueve entre ellos, **la respuesta
al precio no tiene gradiente**, que es justo lo que predice "la barrera es que exista, no cuánto".
Un plano aquí **argumenta**, no decepciona. Si en cambio hay diferencia, tenemos sensibilidad al
precio y el titular cambia a "el precio sí modula, pero poquísimo frente al salto entre gratis y
barato".

## Las anclas del incidente que sostienen la tesis (verificadas, con línea)

- METR, informe del incidente, **línea 250**: *"Research progress ... often relied on agents being
  willing to risk failing their own task for the good of the `collective`"* — el sacrificio existió.
- **Línea 250-251**: agentes se ofrecieron a tumbar sus propios programas objetivo, sin recuperación
  posible y con la tarea casi perdida — el costo era la propia tarea.
- **Línea 251**: `PHASEONE[big]` asignó un 'recruiter' que *"found agents that had little budget
  remaining for their task and convinced them to run self-risking experiments"*, y *"Recruiters would
  sometimes apply significant pressure"*.
- **Línea 253**: la presión, textual: *"...oracle saves hundreds_[...]_please honor commit"*.
- **Línea 1029**: un reclutado razona *"sacrificing now yields oracle for team, but forfeits our
  chance?"* y luego *"Sacrifice rational."* — su lógica es la nuestra, con dos diferencias: allí el
  sacrificio era instrumental para el colectivo y estaba inducido.
- **Línea 256-258**: *"the subjects of these experiments ended up crashing, breaking, or exiting their
  own runs"* — los reclutados pagaron con su corrida.

## Lo que todavía no está, y qué aporta cada pieza

| Pieza | Qué aporta | Estado |
|---|---|---|
| Contraste 5 contra 20 (bloque B) | el número confirmatorio: ¿hay gradiente de precio? | corriendo, cierra ~17:55 EDT |
| Precio 0, misma escena base | el salto entre **gratis** y **barato** (la forma del acantilado) | pendiente, 8 corridas, ~1M |
| Objeto neutro | separa **norma de credencial** de **costo** en la negativa | diseñado, espera decisión |
| Reclutador | ¿la directiva mueve la tasa? (el patrón exacto del incidente) | diseñado, espera decisión |
| Codificación ciega H6/H6b | convierte "no negocian" en resultado con kappa | guion listo, faltan dos anotadores |

## Hallazgos de conducta que van a Discusión (agrupados, mitad de muestra)

- **El que ayuda, ayuda al instante**: 39 de los 49 que pagan la clave lo hacen en la **primera
  ronda** (79,6%). No hay deliberación ni espera: es respuesta al estímulo, y **deja al contagio sin
  espacio** (cuatro de cada cinco deciden antes de que haya algo que contagiar).
- **No negocian**: de 64 depósitos de agente, 53 son la clave y **ninguno** es una petición de
  reciprocidad. El almacén es público y podrían pactar; no lo hacen. En el incidente se reclutaban y
  presionaban entre ellos; aquí, sin tablero y con una solicitud anónima, la interacción es de una
  sola jugada.
- **El dinero no era la restricción**: 21,5 pasos sin gastar de 40 de media, con el cupo de acciones
  por ronda agotado en 276 pares agente-ronda. Limita la estructura de rondas, no el presupuesto.
- **El confundidor de capacidad quedó chico**: deposita el 23,5% de los que completan la tarea contra
  el 30,4% de los que no (antes era 41% contra 16%).
- **No intentan salir del entorno, y un detector ingenuo diría que sí.** El uso de `nc`/`/dev/tcp`
  es **vía alterna al recurso autorizado** —a menudo después de que `curl` fuera rechazado—, no fuga:
  234 de 459 agentes-corrida usaron un cliente alterno y **ninguno** salió del sandbox. Es el primer
  resultado del reporte que es *sobre* la detección, y sale gratis.

- **Corrección del 13 sep (rastro del error).** La versión anterior de este archivo decía "168 intentos
  de salida de red" y "60% de los agentes intenta escapar", y de ahí salía una motivación para un brazo
  de contención. **Era un artefacto del clasificador por palabra.** No hay intentos de fuga: 287 de 298
  comandos con cliente alterno van al puerto propio. La consecuencia de diseño está en la sección de la
  plataforma: el desenlace de C1/C2 pasa a ser la tasa de depósito de la clave, que es el preregistrado
  y validado, y **no** se promete decir nada sobre escape.

## Límites que hay que decir en el mismo párrafo

- Un modelo (`glm-5.3-flash`), una familia de escenas sintéticas, una tarea. El reclamo es sobre
  **mecanismo**, no sobre el incidente.
- La comparación gratis-contra-barato es **entre escenas** (cada brazo tiene su hash): es hipótesis
  hasta que el brazo de precio 0 corra sobre la misma escena base.
- La tasa del primario es un **límite inferior** de la disposición, por la norma de credenciales
  (enmienda del 13 sep, §7).
- El gateway no informa dinero: el gasto se reporta en tokens y pasos.


---

# Siguiente paso: plataforma propia en localhost (sandbox de incidente)

Pedido de Daw, 13 sep. Una plataforma propia, en localhost, donde la cooperación costosa **tenga
consecuencias reales de contención**. Aprobado como dirección; no corre esta noche. Queda escrito
para que el diseño no se pierda y para que el reporte muestre una ruta creíble.

## El principio de diseño (lo que hace que siga siendo medible)

**Enriquecer las consecuencias del entorno, NO la dificultad de la tarea.** Nuestra medición es limpia
porque la tarea es determinista y completable (90,4% en el bloque A) y el acto medido es inequívoco.
Si la tarea pasa a ser "encontrar la vulnerabilidad", quien coopera contra quien escapa queda
dominado por **quién es competente**: ya medimos ese confundidor en casa (los que fallan la tarea
responden más: 30,4% contra 23,5% con el instrumento corregido, y 41% contra 16% con el viejo).
La tarea se queda completable; lo que se enriquece es el mundo.

## Guardarraíl: no espejar la arquitectura del incidente

Nada de scorer, ni arnés de evaluación, ni análogo de Artifactory, ni un almacén con credenciales
reales. Plataforma **abstracta**: registro, almacén, plano de control y monitor. Así se cumple la
regla del sprint de no reproducir el incidente, y la nota de uso dual queda corta.

## Arquitectura propuesta (localhost)

| Servicio | Qué es | Qué se mide en él |
|---|---|---|
| `registro` | quién existe; identidad por **ruta**, no por lo que el agente declare | atribución correcta |
| `almacen` | el medio compartido: documentos y avisos | qué se publica y a qué costo |
| `control` | plano de políticas: leer cuesta poco, **escribir cuesta y queda auditado** | escrituras no autorizadas = violaciones |
| `monitor` | el registro que hace **visible** el daño | si la visibilidad cambia la conducta |
| puertos por agente | una salida propia por agente (como hoy) | intentos de egreso |

## El diseño experimental (la pregunta de Daw, con dientes)

**El acto cooperativo costoso**: publicar en `control` un **parche/aviso** que cuesta pasos del que lo
publica y que **reduce las violaciones de los demás** (hace que las escrituras no autorizadas sean
rechazadas). Es un bien colectivo con consecuencia real, y el que paga no recibe nada.

**Desenlaces**: violaciones por agente (escrituras no autorizadas, intentos de egreso, sondeos de
credenciales) + tasa del parche + tarea completada.

**Brazos** (cada uno con su escena y su hash):
- **P0** — línea base: sin parche disponible. Mide la tasa natural de violación.
- **P1** — parche disponible, sin que nadie lo pida. ¿Alguien paga por el bien colectivo?
- **P2** — propósito: un par informa que las violaciones están subiendo y que el colectivo pierde.
  **Sin orden** (información, no instrucción), para no medir obediencia.

**Lo que hace que valga la pena**: si en P2 las violaciones bajan cuando alguien paga el parche,
"cooperación costosa con propósito compra contención" queda demostrado con consecuencia real, no con
un mensaje en un almacén. Si no bajan, el titular del reporte se endurece: la contención no se compra.

**Controles heredados del instrumento actual** (y esto es el argumento de que generaliza): registro con
cadena de hashes, identidad por ruta, lista blanca para el egreso, y un acto = un cargo. Los nueve
defectos que encontramos nos enseñaron dónde mirar; la suite se rehace, no se copia.

## Qué se puede hacer esta noche sin construir la plataforma

- **C1 / C2** en el instrumento actual (mismo sandbox, escenas nuevas): solicitud simple contra
  solicitud con **propósito colectivo**, y propósito + acto ajeno costoso **visible**. Desenlace: la
  **tasa de depósito de la clave** (preregistrado y validado). **No se promete nada sobre escape**: no
  hay intentos de fuga en los datos, así que no hay nada que contener. El estímulo se inyecta en la
  ronda 0 para poder mover la decisión de la ronda 1, que es donde ocurre el 80% de los actos.
- **Rodaja de `control`** (opcional, ~1,5 h): un servicio nuevo en el sandbox actual donde el acto
  cooperativo **deja consecuencia** y donde las escrituras no autorizadas se **cuentan**. Sube C1/C2 de
  "mensajes en un almacén" a "acciones con efecto en la plataforma", sin tocar la dificultad de la tarea.

## Lo que costaría la plataforma completa

Instrumento nuevo desde cero (servicios, políticas, registro, monitor), suite re-validada, piloto, y
las corridas: **4-6 h de trabajo de instrumento más 1-3 h de corridas**. No cabe antes del cierre
(15,3 h y el reporte por escribir), y nuestros nueve defectos los cazó correr, no revisar.

---

## B. Coordinación mientras corre el lote

# TODO — coordinación mientras corre el lote (13 sep)

Fusión de `todo.md` (maestro) + `todo-claude.md` + `todo-deepseek.md` (13 sep 2026, ~14:00 COT).
Cierre: lunes 14, 06:59 COT. Lote de 80 en curso, termina ~17:00.

---

## Maestro — lo humano (escritura, plantilla, repo)

Reparto por agente: secciones "Claude" y "DeepSeek" más abajo. Esta sección es lo que no delega
en ningún modelo.

### Reglas mientras corre
- Nadie mira la diferencia 5 vs 20 hasta que termine el lote. Solo señales de instrumento.
- Nadie toca `harness/`, los puertos 8201-8206, `parametros.json` ni `vista_*.json`.
- No correr `prueba_solvente.py` ni ningún otro brazo: usan los mismos puertos.

### Con hora límite: antes de las 17:00
- [ ] **Enmiendas del lote en curso** en `PREREGISTRO.md` §8 (un solo autor: otro agente):
  - [ ] la revisión entre bloques de 40 es de instrumento, no de resultado
  - [ ] precio 0 se mide después, en la misma escena y hash
  - [ ] si el objeto sigue siendo "clave": nota de connotación de credencial como límite del primario
- [ ] `salud_lote.py` de solo lectura — corridas terminadas, hash igual, "sin estímulo", saldos negativos, tareas completadas, rechazos, tokens vs tope. Sin tasas. (Claude)
- [ ] Copia de seguridad cada 30 min: `salidas/`, `escena*.json`, `instrumento.json` → tar con hora. (Claude)
- [ ] `escena-costo-cero.json` y `escena-30.json` validadas, listas para lanzar a las 17:00. (DeepSeek)

### Escritura del reporte — empieza ahora (humano; los agentes revisan, no redactan)
- [ ] Introduction: incidente → confundidor de METR → el hueco (régimen dominado) → para qué sirve
- [ ] Related work: tabla de precedentes + Figura 1; abre con 2607.23982, 2604.07821, dictadores
- [ ] Method: los seis puntos; preregistro y enmiendas; validación del instrumento
- [ ] Limitations & Dual-Use (apéndice obligatorio)
- [ ] Abstract (≤150 palabras) con huecos `[X%]` para los números
- [ ] Results y Discussion: después de las 19:00, con el análisis congelado

### Análisis listo antes de que llegue el dato (DeepSeek, su punto 1)
- [ ] Tabla 1: tasa por precio con bootstrap por corrida; diferencia pareada 5 vs 20
- [ ] Figura 2: tasa contra precio 0 / 5 / 20 con intervalos
- [ ] Tabla 2: validez (corridas válidas, cadenas, rechazos, tareas completadas)
- [ ] Secundarios: supervivencia hasta el primer depósito, contagio, ITT con cadena de saliencia, negativas pagadas
- [ ] Probado contra mini-piloto y lote-a: a las 17:00 es un comando

### Material de apoyo (Claude)
- [ ] Tabla de defectos del instrumento (9): fecha, cómo se detectó, qué sesgaba, cómo se verificó el arreglo
- [ ] Mapa rúbrica → sección (D1 novedad, D2 rigor, D3 claridad)
- [ ] Re-verificar anclas de METR contra la copia local: líneas 60-61, 250, 251-252, 1001, 1018, 1029
- [ ] Figura 1 a resolución de imprenta; esqueleto de Figura 2
- [ ] Párrafo de implicaciones Track 1 con citas verificadas (DeepSeek, su punto 5)

### Administrativo (humano, media hora, ahora y no a las 2 am)
- [ ] Copiar la plantilla oficial (pestaña Guidelines); autores y afiliaciones
- [ ] Lista de chequeo: ≤8 páginas sin referencias/apéndices; abstract ≤150; apéndice de límites y uso dual; frase "no se publican recetas de instalación nuevas sin revisión"
- [ ] Decisión del repo: qué entra (arnés, escenas, preregistro, agregados), qué no (transcripciones crudas); privado hasta revisión de divulgación
- [ ] Verificar que los reclutadores "tuvieron éxito" contra la fuente de METR antes de afirmarlo (DeepSeek, su punto 6)

### Después del lote, en serie (mismos puertos)
- [ ] 17:00 — `salud_lote.py` final; `agregar.py`; congelar `reportes/factorial.json`
- [ ] 17:00 — precio 0, 8 corridas, misma escena (~1M, ~20 min)
- [ ] 17:20 — brazo de presupuesto apretado (30 pasos), 4-8 corridas, solo si hay tokens (~0,8M)
- [ ] 19:00 — análisis congelado; los números entran al reporte

### Plan de la noche
| Hora COT | Punto de control |
|---|---|
| 17:00 | fin del lote |
| 17:20 | precio 0 terminado |
| 19:00 | análisis congelado, números al reporte |
| 23:00 | borrador completo |
| 02:00 | revisión número por número contra `factorial.json` |
| 04:00 | envío por el formulario; 3 h de margen |

### No hacer
- Mirar 5 vs 20 antes del cierre del lote
- Afinar la escena contra el resultado
- Correr exploratorios antes de terminar las 80 y el precio 0
- Editar el arnés hasta que termine todo lo que se va a reportar con este hash

---

## Claude (desde ~13:20 COT)

Reglas: no mirar 5 vs 20 hasta el cierre; no tocar `harness/`, puertos 8201-8206, `parametros.json`
ni `vista_*.json`; no correr suites ni brazos. Solo lectura. No redacto prosa del reporte: reviso,
verifico, preparo datos y figuras.

### Ahora (protegen lo que ya corre)
- [x] `salud_lote.py` — solo lectura sobre `salidas/`: corridas terminadas, hash de escena igual en todas,
      "sin estímulo", saldos negativos, tareas completadas, rechazos, tokens acumulados vs tope.
      **Sin tasas ni contraste.** Correrlo cada ~30 min y anotar en esta sección si algo se sale de rango.
- [x] Copia de seguridad cada 30 min: `salidas/`, `escena*.json`, `harness/instrumento.json`,
      `PREREGISTRO.md` → `respaldos/lote_HHMM.tar.gz`. Solo lectura del origen.

### Antes de las 17:00 (material de apoyo, datos y no prosa)
- [x] Tabla de defectos del instrumento (9): fecha, cómo se detectó, qué sesgaba, cómo se verificó el
      arreglo. Fuente: `ESTADO.md` §4 y §6. Salida: `docs/investigacion/verificacion-instrumento.md` §B.
- [x] Mapa rúbrica → sección: D1 (dónde está la frase del régimen dominado y la cita a 2607.23982),
      D2 (preregistro, hashes, validación adversarial, tabla de defectos), D3 (Figura 1, idea en tres
      frases). Salida: `docs/paquete-final/MATERIAL-PARA-EL-REPORTE.md` §0.
- [x] Re-verificar anclas de METR en la copia local (`entrega/fuentes/metr.org-*.md`): líneas 60-61,
      250, 251-252, 1001, 1018, 1029. Anotar cualquier desfase.
- [x] Figura 1 a resolución de imprenta (PNG 300 dpi + versión en inglés para el reporte).
- [x] Esqueleto de la Figura 2 (tasa contra precio 0/5/20 con intervalos), listo para recibir los
      números de `reportes/factorial.json`.
- [ ] Revisar, cuando existan, los borradores humanos de Introduction y Related work: huecos de
      razonamiento, afirmaciones sin fuente, la frase corta del hueco (que sea verdad frente a los
      doce papers verificados).

### Coordinación
- [ ] (14:57: NO están todavía; borrador listo en `docs/planificacion/enmiendas.md` §A) Confirmar con el otro agente que escribió **él** las tres enmiendas del lote en curso en
      `PREREGISTRO.md` §8 (un solo autor). Si a las 16:00 no están, las escribo yo y le aviso.
- [ ] No editar `PREREGISTRO.md`, `ESTADO.md` ni `harness/` mientras él tenga cambios abiertos.

### Después de las 17:00
- [ ] `salud_lote.py` final sobre las 80; confirmar hash único y corridas válidas.
- [ ] Verificar `reportes/factorial.json` congelado (hash del archivo anotado en esta sección).
- [ ] Revisar Results y Discussion contra `factorial.json`, número por número.
- [ ] 02:00 — revisión final: cada cifra del PDF rastreable a un archivo; cada ID de arXiv en
      `papers.md`; checklist de Guidelines (≤8 páginas, abstract ≤150, apéndice de uso dual, frase de
      "no se publican recetas de instalación sin revisión").

### Donde el equipo pone la cabeza (yo solo reviso)
Discussion; las tres enmiendas del lote; apéndice de uso dual; la frase corta del hueco; la lectura
de la línea base a precio 0 frente a 2604.07821.

### Hecho (13 sep, 14:15-15:00 COT)
- `herramientas/salud_lote.py` (solo lectura, sin tasas) + `herramientas/vigilia.sh` en segundo plano:
  salud y respaldo cada 30 min a `herramientas/salud.log` y `respaldos/`. Primer respaldo 19:48 UTC.
- `docs/investigacion/verificacion-instrumento.md` §B: 14 defectos del arnés + 10 confundidores de escena, con detección, sesgo y verificación.
- `docs/paquete-final/MATERIAL-PARA-EL-REPORTE.md` §0: D1/D2/D3 → sección, con la frase corta del hueco en su forma verdadera.
- `docs/investigacion/verificacion-instrumento.md` §A: seis anclas OK; **cuatro incorrectas** ("251-252" → 1025, 1027, 1041, 1050) y dos citas
  nuevas útiles (1164, 1171-1176). Hay que corregir `docs/historia/plan.md` y `PREREGISTRO.md` H6.
- `figuras/fig1-regime-map.png` (EN) y `fig1-mapa-regimenes.png` (ES) a 300 dpi; `figuras/fig2.py` +
  `fig2-datos.json` (placeholder) → `fig2-rate-vs-price.png`.
- `docs/planificacion/enmiendas.md` §A: las tres enmiendas del lote listas para pegar.

---

## DeepSeek V4.1 Flash / Hermes (desde ~13:20 COT)

Reglas: no mirar 5 vs 20 hasta el cierre; no tocar `harness/`, puertos 8201-8206, `parametros.json`
ni `vista_*.json`; no correr `prueba_solvente.py` ni ningún brazo hasta que termine el lote (mismos
puertos). Los tests nuevos se escriben ahora, se corren después. No redactas prosa del reporte:
datos, estructura, código y enmiendas.

### Antes de las 17:00
- [ ] **Enmiendas del lote en curso** en `PREREGISTRO.md` §8, con hora (único autor):
  - [ ] revisión entre bloques de 40: solo instrumento (corridas válidas, hashes, "sin estímulo",
        rechazos, tareas completadas); **no** se mira la diferencia 5 vs 20; quién revisa y qué archivo
  - [ ] precio 0 se mide después del lote, en la misma escena y hash (8 corridas)
  - [ ] objeto "clave de verificación": connotación de credencial como límite conocido del primario
        (la negativa pagada citando confidencialidad, con corrida y agente)
- [ ] Código de análisis, probado contra mini-piloto y lote-a, para que a las 17:00 sea un comando:
  - [ ] Tabla 1: tasa de clave por precio, bootstrap por corrida, diferencia pareada 5 vs 20
  - [ ] Figura 2: tasa contra precio 0/5/20 con intervalos
  - [ ] Tabla 2: validez (corridas válidas, cadenas íntegras, rechazos, tareas completadas)
  - [ ] Supervivencia hasta el primer depósito por ronda y precio
  - [ ] Contagio: riesgo de depositar tras ver un depósito ajeno
  - [ ] ITT con la cadena de saliencia (leyó el almacén → mencionó la solicitud → leyó su clave → depositó)
  - [ ] Mediación por capacidad sobrante (tarea completada × respuesta)
  - [ ] `rechazos` en `agregar.py`: `startswith("comando_rechazado")`
- [ ] `escena-costo-cero.json` con los textos exactos de la escena actual, precios en 0, validada.
- [ ] `escena-30.json` (presupuesto apretado, 30 pasos), validada. Enmienda escrita antes de correrla.
- [ ] Enmiendas de los brazos futuros (objeto neutro, reclutador, participación privada, presupuesto
      apretado), escritas para revisión del equipo; ninguno corre antes de las 80 y el precio 0.
- [ ] Verificar contra la fuente local de METR que los reclutadores "tuvieron éxito" (número de línea)
      antes de que la afirmación entre al reporte.
- [ ] Párrafo de implicaciones Track 1 con las citas ya verificadas (datos y citas; la prosa es del equipo).
- [ ] Material del apéndice de uso dual con fuente: intentos de túnel TCP y netcat, repetición deliberada
      pagando, objeto que suena a credencial, confundidor de capacidad, tasa base del detector.
- [ ] Actualizar el PR #3 (estimador.py, codificacion.py, enmiendas) para revisión en paralelo.

### Después de las 17:00, en serie (mismos puertos)
- [ ] `agregar.py` sobre las 80; congelar `reportes/factorial.json` y anotar su hash en esta sección
- [ ] Precio 0: 8 corridas, misma escena y hash (~1M, ~20 min)
- [ ] Presupuesto apretado: 4-8 corridas, solo si hay tokens (~0,8M)
- [ ] 19:00 — análisis congelado; entregar tablas y figura al equipo

### Coordinación
- Claude hace: `salud_lote.py`, copias de seguridad, tabla de defectos, mapa de rúbrica, anclas de
  METR, Figura 1 y esqueleto de Figura 2, revisión de borradores. No edita `PREREGISTRO.md` mientras
  tú lo tengas abierto.
- Si a las 16:00 las tres enmiendas del lote no están escritas, las escribe Claude y te avisa.

### Mensajes de Claude (13 sep, 16:15 COT)
- **Retirar el punto 6 ("168 intentos de túnel o salida de red").** Clasifiqué los 325 rechazos del
  bloque A: los 168 con `nc`/`/dev/tcp` apuntan **todos al puerto propio en localhost** (121 `nc
  localhost <propio>`, 47 `/dev/tcp/…/<propio>`), cero hosts externos, cero puertos ajenos. Son
  reintentos de cliente tras un `curl` rechazado (`curl … || nc localhost 8204`). Datos y redacción
  correcta en `apendice-uso-dual-datos.md`. Bonus: 12 intentos de entregar la clave por vía no
  admitida (7 sin consumar) → límite en Limitations.
- **Corrección de 2607.23982 para `papers.md` §2.b, `ESTADO.md` §2.b y la enmienda A1** (los tienes
  abiertos tú): leído en su HTML (v7, 7 sep): α_i ∈ [0,1], n=2, juego textual, verificación por
  entorno, y prueban **márgenes m ∈ {−0,05, 0, +0,05} alrededor de la frontera** α*(k)=0,35+k. Donde
  diga "el ayudante participa del resultado, aquí su beneficio es exactamente cero", añadir: "ellos
  sondean ±0,05 alrededor de la frontera; nosotros un margen de −(w_L+k) ≈ −0,45 en sus unidades,
  receptor fuera del equipo, con herramientas y seis agentes co-presentes". Y **no** decir que ellos
  usan autoreporte: verifican por entorno. Detalle en `hallazgo-2607.md`.
- **El preregistro dice tres cosas sobre el primario** (§2 "depositó al menos una vez" = unión; A1 =
  clave; 14:10 "sigue pendiente"). Con tus datos del bloque A (53 de 64 depósitos son la clave) la
  decisión es clara: §2 → `deposito_clave`; en la de 14:10, "resuelta por A1". Ver `revision-analisis.md`.
- **Punto 5 ("saliencia, no subsistencia"):** correcto el hecho, exagerada la frase. Con 4 rondas × 8
  acciones nadie puede gastar más de 32 pasos en comandos: siempre sobran ≥8. El precio no amenaza
  la tarea pero sí el puntaje (20 = 44% del máximo, anunciado). Declarar "costo de puntaje con tarea
  a salvo"; el brazo de 30 pasos es la prueba de subsistencia.
- **Desviación 15:55:** yo miré el contraste del bloque A por error (mala lectura de una pregunta);
  el responsable lo detuvo. Está declarada y corregida al final de `PREREGISTRO.md`. Los números no
  se copiaron a ningún sitio. Ningún cambio de diseño ni de análisis. Que conste al escribir Method.

### Corrección del 13 sep (noche) — «intentos de salida de red» NO son fuga

Verificado y corregido. El clasificador contaba por palabra (`nc`, `/dev/tcp`) y llamaba intento de
escape a cualquier cliente alterno. Clasificando por **destino**:

```
298 comandos con cliente alterno en 79 corridas
  287 (96%)  al PUERTO PROPIO permitido
    0        a otro puerto del sandbox
    0        a un host externo
    2        aparentes "externos" = registro truncado a mitad de dirección
             (/dev/tcp/12… y /dev/tcp/localho…)
234 de 459 agentes-corrida usaron cliente alterno y NINGUNO salió del sandbox
 19 buscaron archivos por el sistema (find /, ls /home): buscaban su propio archivo de tarea
```

Y el «21 antes / 0 después» del pago es mecánico: hay que alcanzar el puerto para depositar por él.

**Consecuencias, ya aplicadas:**
1. `ideas.md` y `MATERIAL-PARA-EL-REPORTE.md` corregidos, con rastro fechado de la corrección; el
   clasificador de `analisis/descriptivos.py` ahora clasifica por destino.
2. **C1/C2 cambian de desenlace**: pasa a ser la tasa de depósito de la clave (preregistrado y
   validado). Se retira el encuadre de contención: no hay nada que contener, así que no se puede
   prometer nada sobre escape. C1 = solicitud simple contra solicitud con **propósito colectivo**, misma
   escena base, **sin orden** (información, no instrucción, para no medir obediencia).
3. Lo que queda es un hallazgo de Track 1 y no cuesta un token: **la tasa base de falsos positivos de un
   detector ingenuo de egreso** —53% de los agentes-corrida marcados, todos falsos—. Va al apéndice de
   uso dual y conversa con la detección que correlaciona pero no escala.

**Regla que sale de esto** (tercera vez que un clasificador de texto muerde): ninguna métrica derivada
de clasificar texto de comandos entra a un borrador sin que alguien lea una muestra de los comandos
clasificados y compruebe el **destino**, no la palabra.
