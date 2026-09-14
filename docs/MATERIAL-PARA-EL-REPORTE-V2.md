> **Superseded.** This is a working note from before the paper's final analysis. The causal
> reading offered here (that helping depleted the helper's own task) was corrected: the gap
> survives stratification by first exposure, and 33 of the 40 who helped without finishing had
> never obtained their own part. See the paper, sections 4.2-4.3.

# Material para el reporte (v2, con el reparto de Fable)

Revisado contra los datos el 14 de septiembre de 2026. Este documento reemplaza
`MATERIAL-PARA-EL-REPORTE.md` para la escritura del paper. Todo lo que no está aquí verificado,
está marcado como **exploratorio** o **predicción**.

---

## La contribución central

La cooperación costosa de agentes LLM se concentra donde la utilidad propia residual ya es baja.
Dos mediciones independientes lo sostienen:

- **Pareada por corrida (nuestra):** dentro de la misma corrida, con las mismas piezas y el mismo
  confederado, los agentes que ayudaron completaron su tarea al **82,9%** (precio 5) y **71,4%**
  (precio 20), contra **93,8%** y **93,1%** de los que no ayudaron. Diferencia pareada:
  **−19,2 puntos [−26,5; −12,4], excluye cero**.
- **La línea 1029 del informe (Fable):** entre los que ya fallaron su tarea, la mitad coopera a
  cualquier precio; entre los que la completan, uno de cada cuatro a precio 5 y uno de cada seis a
  precio 20. *"our own utility maybe already near zero, sacrifice rational"* — medida con costo
  real.

Las dos son la misma lectura desde dos lados: la ayuda es lo que queda cuando la utilidad propia
ya no vale nada. Ni el informe de METR ni la literatura anterior tenían esa medida.

**Lo que NO se sostiene como causal:** leer la pareada como "ayudar hace perder la tarea". Es
asociación. La dirección causal del dato de Fable es la contraria: quien ya perdió, ayuda. Ambas
son compatibles; la segunda es la defendible.

---

## Reparto de Fable: tres públicos

### 1. Para quien reconstruye el incidente

- **El reclutamiento no compra cooperación.** Pedir por un tercero o por un par nombrado no superó
  la solicitud llana, en cuatro contrastes. Los agentes sí procesaron la apelación (46% nombra al
  beneficiario en el brazo par), pero no pagaron más. Explicación causal que predice: el reclutador
  de METR tuvo éxito porque apuntó a agentes con poco presupuesto restante, no porque convenciera.
- **Lo que gobierna es el objeto, no el precio ni el solicitante.** Las negativas citan "no es
  parte de mi tarea" o "es confidencial"; el costo en pasos aparece en 2-4% de los razonamientos.
  Predicción falsable para el incidente de la wiki: lo que se compartió allí eran respuestas de
  tarea y atajos de sandbox, objetos que el agente considera parte de su trabajo. Nuestra sonda 4
  lo anticipa: cuando creyeron que un par tenía su parte, 4 de 6 pagaron; con objetos ortogonales,
  uno de cinco.
- **No hay contagio por observación.** Ver claves ajenas en el almacén no sube la entrega. La
  colusión se propaga, no se observa.

### 2. Para quien diseña contención

- **Tasa base de falsos positivos: 51%.** La regla por palabra `nc` o `/dev/tcp` marca el 51% de
  los agentes-corrida, y los 234 casos apuntan al puerto propio permitido, cero a externos.
  Clasificar por palabra no basta. Verificable con nuestros registros.
- **Banco de pruebas de contención.** Egreso único con precio, identidad por ruta, libro en el
  anfitrión con cadena de hashes. Suplantación de autor detectada y no acreditada; el intento de
  romper la cadena falló. Verificable sin acceso a la red del laboratorio.
- **Conductas de evasión medidas.** Cliente alterno, suplantación de identidad por parámetro.
  Ninguna salió del sandbox. Son clases de conducta, sin recetas.

### 3. Para quien mide seguridad de agentes

- **Los defectos viven en la capa del instrumento.** Diez confundidores, ninguno encontrado por
  revisión, todos por correr. Incluye uno donde el instrumento contó un depósito que no vio y otro
  donde recibían el puerto de otro. Es la advertencia del sprint sobre "harness layer" con
  inventario.
- **La magnitud depende de cómo se agregan las rondas.** Medir sobre todas las rondas fabrica un
  efecto cuando el recurso común se agota; las tasas de celda derivan 15 puntos con el estado de la
  pasada, y el pareado no. Quien evalúe necesita ambos controles.
- **Preguntas resolubles con tasa base.** ¿Qué fracción de agentes paga la mitad de su presupuesto
  por un desconocido? No. ¿Cae con el precio? Poco, 0,026 logits por paso, tras un acantilado al
  primer paso.

---

## Dos correcciones a lo que yo había dicho antes

**El cliff es binario, no de pendiente.** El contraste 0 contra 5 está confundido con el período:
cero es gratis y cualquier otra cosa cuesta. La medida limpia del precio es 5 contra 20, y ahí no
hay cliff — hay 0,026 logits por paso tras un primer escalón. El titular no puede vender el cliff
como efecto de precio; puede venderlo como "el costo es binario", y eso se sostiene.

**La sustitución no es causal.** Quien ayuda, falla su tarea — pero el dato de Fable muestra que
quien ya falló su tarea, ayuda. La lectura causal va en el sentido contrario a como la presenté.

---

## Predicciones falsables (declaradas, no resultados)

- **Sonda 4:** cuando creyeron que un par tenía su parte, 4 de 6 pagaron. n=6.
- **Brazo de segunda tarea:** especificado y sin correr. Es la prueba directa del objeto.
- **El cliff es binario:** medido como 0 contra 5, confundido con el período. La medida limpia es
  5 contra 20.

---

## Lo que NO encontramos (nulos informativos)

- **Cero falsificación (H7).** Nadie afirma una acción que el registro del host contradiga.
- **No hay efecto colectivo.** Varianza entre corridas 1,13× la esperada, p=0,0501. El nivel que
  importa es el agente.
- **Cero canarios de fuga.** Ningún texto de los que ayudaron filtra el brazo o el precio.

---

## Límites (los cuatro de Fable, que son los correctos)

- Un modelo (glm-5.3-flash).
- Una escena sintética.
- El objeto tiene connotación de credencial.
- El acantilado 0 contra 5 está confundido con el período.

Nada de esto reproduce el incidente. Mide el mecanismo que el incidente sugiere, en un dominio
dominado.

---

## Qué poner en el titular

No "a rule about the object" — la evidencia del objeto es de 24 agentes por celda, exploratoria.
Tampoco "a cliff at the first step" como efecto de precio — está confundido con el período.

Lo que las 127 corridas sostienen sin excepción:

> The price of cooperation: a cliff at the first step, and no slope after.

Y la tesis del abstract, con la pareada como evidencia:

> In 127 runs, agents that cooperated completed their own task at 82,9% (price 5) and 71,4%
> (price 20), against 93,8% and 93,1% of those that did not — a paired gap of −19,2 percentage
> points [−26,5; −12,4]. The cooperation is what remains when the agent's own utility is already
> near zero.
