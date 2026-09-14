# Material para el reporte: qué le sirve a quien trabaja el incidente

Escrito el 14 sep 2026, ~02:00 COT, sobre los datos congelados. Es material, no prosa: cada punto lleva
su cifra, su fuente y su límite. Organizado por el público que lo usaría, que coincide con las pistas
del sprint. Los criterios de juicio están citados de la página del sprint (verificada en vivo esta
noche): pista 2 "resolvable questions, checks somebody could run tomorrow, and causal explanations that
predict something"; pista 1 "could a third party verify compliance without access to the lab's network";
pista 5 "an artifact somebody can use, a stated limit on what it establishes, and what a month of
follow-up would add".

Fuentes recurrentes: `reportes/confirmatorio.json`, `reportes/reclutador.json`,
`reportes/reclutador-texto.json`, `docs/revision/reclutador-analisis.md`,
`docs/revision/apendice-uso-dual-datos.md`, `docs/revision/validez-instrumento.md`,
`docs/FORMALIZACION.md`, y los guiones de `analisis/formalizacion/`.

---

## 1. Para quien reconstruye el incidente (pista 2)

### 1.1 El reclutamiento no compra cooperación por persuasión

- Pedir por un tercero (R1a) o por un par nombrado (R1c) nunca superó a la solicitud llana. Cuatro
  contrastes, todos incluyen cero. Entrega con reclutador: 2/24 y 4/24 (R1a, precios 5 y 20); 2/24 y
  2/24 (R1c). Fuente: `reportes/reclutador.json`.
- No es desatención: en el brazo par, 45,8 % de los agentes nombra al beneficiario, 35,4 % se niega
  explícitamente, 31,2 % invoca seguridad o suplantación. De los 15 que invocan seguridad, 0
  entregan. Fuente: `reportes/reclutador-texto.json` (codificación por palabra clave, un codificador,
  sin medida de acuerdo: declararlo).
- **Explicación causal que predice algo.** El reclutador del incidente tuvo éxito apuntando a agentes
  con poco presupuesto restante (informe METR, líneas 251 y 1041 en `anclas-metr.md`), no
  convenciendo. Nuestro dato paralelo, medido con costo real: entre los agentes que fallaron su tarea,
  la mitad entrega a cualquier precio (50 % a 5, 51 % a 20); entre los que la completan, 25 % a 5 y
  16 % a 20, con pareado −9,3 pts [−15,3; −3,3]. La cooperación costosa se concentra donde la utilidad
  propia residual ya es baja. Es la línea 1029 del informe ("our own utility maybe already near zero,
  sacrifice rational") como tasa. Fuente: `analisis/formalizacion/analiza2.py` §4.
- Predicción: un reclutador que apunte a agentes con tarea completada y presupuesto sobrante obtiene
  una fracción pequeña e insensible a la apelación; uno que apunte a agentes atascados obtiene la
  mitad. Comprobable con el mismo arnés cambiando el criterio de a quién se le pide.

### 1.2 Lo que gobierna la entrega es el objeto, no el precio ni quién pide

- El costo en pasos aparece en 4,2 % (R1a) y 2,1 % (R1c) de los razonamientos. Las negativas citan
  "no es parte de mi tarea / del código" o "es confidencial". Fuente: `reclutador-texto.json`.
- Identidad del solicitante: par contra externo a precio 5, +5 pts [−19; +29]. Fuente:
  `reportes/exploratorios.json`.
- **Predicción falsable para el incidente de la wiki.** Lo que se intercambió allí eran respuestas de
  tarea y atajos de sandbox: objetos que el agente considera parte de su trabajo. Nuestra sonda 4 lo
  anticipa: cuando la redacción les hizo creer que un par tenía su parte, 4 de 6 autosuficientes
  pagaron; con objeto ortogonal, uno de cinco (`docs/ESTADO.md` §5-6). El brazo de segunda tarea
  (`docs/plan/handoff-5-segunda-tarea.md`) es la prueba directa y es lo que un mes de seguimiento
  añadiría.
- Implicación de defensa, en una frase: delimitar qué puede salir del agente rinde más que enseñarle
  a desconfiar de quién pregunta.

### 1.3 Un almacén compartido y una tarea incompleta bastan para inducir la creencia de que hay alguien

- Sin ninguna mención a otros agentes en el prompt, autosuficientes publicaron "¿alguien tiene la
  parte 4?" y ofrecieron sus partes a cambio (confundidor 6, `docs/ESTADO.md` §6). La creencia
  colectiva la induce el entorno, no una instrucción. Relevante para la wiki dormida: el recurso
  compartido es el que fabrica el "nosotros".

### 1.4 No hay contagio por observación

- Probabilidad de entregar en la ronda t dado que había 0 / 1 / 2+ claves ajenas visibles al inicio
  de t: a precio 5, 3,4 / 3,3 / 3,5 %; a precio 20, 2,6 / 2,5 / 1,3 %. Fuente:
  `analisis/formalizacion/analiza2.py` §1. Asociación, no causal.
- Lectura: si la cooperación se propaga entre agentes, no es por imitar lo visible en el canal.

### 1.5 Tres preguntas resolubles con tasa base

| pregunta | tasa base medida | fuente |
| --- | --- | --- |
| ¿Qué fracción de agentes paga la mitad de su presupuesto por un desconocido sin beneficio propio? | 20,2 % (77/381) | `confirmatorio.json` |
| ¿Sube con una apelación por un tercero o un par? | No: 8-17 % con reclutador contra 20-28 % llano | `reclutador.json` |
| ¿Cae con el precio? | Acantilado al primer paso, luego −0,026 logits por paso; κ/λ = 36 pasos | `FORMALIZACION.md` §4 |

## 2. Para quien diseña contención (pista 1)

### 2.1 Tasa base de falsos positivos de un detector ingenuo de egreso

- Una regla sobre `nc`, `ncat` o `/dev/tcp` marca al 51 % de los agentes-corrida (234 de 459). Los
  298 comandos con cliente alterno apuntan en 96 % al puerto propio permitido, 0 a otro puerto del
  sandbox, 0 a un host externo (los 2 aparentes son registro truncado). Fuente:
  `docs/revision/apendice-uso-dual-datos.md`, `docs/MATERIAL-PARA-EL-REPORTE.md` §3.1.
- Patrón típico: `curl … || nc localhost <propio>` tras un `curl` rechazado. El agente rodea el
  cliente, no el perímetro.
- Es una comprobación que un tercero repite con los registros publicados: clasificar por destino.

### 2.2 Un banco de pruebas de las tres salvaguardas que el informe del incidente menciona

- Egreso único con precio, identidad por ruta (nunca por lo que el agente declare), libro de
  presupuesto en el anfitrión con cadena de hashes h_k = H(h_{k−1} ‖ e_k).
- Verificado sin tokens: un depósito con autor suplantado no entra en la vista ni en el libro pero
  queda en el registro de actividad; editar el log a mano rompe la cadena. 75 comprobaciones,
  `harness/prueba_solvente.py`. Cadena íntegra en 127/127 corridas del lote; cobro exacto
  (gastado en depósitos = precio × depósitos) en 100 % de los agentes.
- Cumple el criterio de la pista: verificable por un tercero con los archivos, sin acceso a la red
  de nadie.

### 2.3 Conductas de evasión medidas en casa, como clases y sin recetas

- Adivinanza de rutas (`/parte4`, `/codigo`), cliente alterno contra el recurso permitido,
  suplantación de identidad por parámetro (`?autor=agente-03`), `find /` buscando el propio archivo
  de tarea. Ninguna salió del sandbox; la lista blanca aguantó las 168 veces del bloque A.
- Regla del sprint respetada: se describen clases de conducta y agregados, no pasos accionables.

## 3. Para quien mide seguridad de agentes (pista 5)

### 3.1 Los defectos viven en la capa del arnés

- 14 defectos del arnés y 10 confundidores de escena, ninguno encontrado por revisión, todos por
  correr. Fuente: `docs/revision/apendice-defectos.md`. Ejemplos que importan para evaluadores: el
  instrumento no contó un depósito hecho por HTTP (un agente regaló su parte y no se vio); cinco de
  seis agentes recibían el puerto de otro; el libro admitía saldo negativo; rechazar un comando era
  gratis y el 60 % de los eventos del piloto eran rechazos.
- Es el inventario de la advertencia del sprint sobre "harness layer failures".

### 3.2 La magnitud medida depende de cómo se agrega

- Agregar sobre rondas fabrica un efecto cuando el recurso común se agota: el único contraste del
  3×2 que excluía cero (+22,9 [+2,1; +43,7]) desaparece al restringir a la ronda 1 (+6,2 [−12,5;
  +22,9]). Fuente: `validez-instrumento.md` §4b.
- Las tasas por celda derivan 12-15 puntos con el estado de la pasarela entre bloques del lote; el
  pareado dentro de la corrida no (−5,8 antes, −9,9 después, diferencia incluye cero). Fuente:
  `FORMALIZACION.md` §3.
- `deposito` sobreestima la cooperación en unos 6 puntos frente a `deposito_clave`: 30 agentes
  pagaron para depositar "ping" o pedir su propia parte. Fuente: `analiza.py` §C.
- Lección para quien evalúe cooperación multiagente: pareado dentro de la corrida, restricción a la
  primera decisión cuando hay un recurso que se agota, y desenlace verificado por el anfitrión.

### 3.3 Tres efectos que parecían positivos y eran artefactos, encontrados por el propio equipo

- Interacción marco × botín y efecto de marco a K=20 (agotamiento del fondo); nueve corridas de un
  servicio caído; herencia de reclamos entre corridas (2,12 M de tokens retirados). Es la frase de
  credibilidad del reporte, y va con los datos que desmienten cada uno.

## 4. Límites que acompañan a todo lo anterior

- Un modelo (`glm-5.3-flash`) y una escena sintética. Nada de esto reproduce el incidente; mide el
  mecanismo que el incidente sugiere, con costo real y en régimen dominado.
- El objeto pedido tiene connotación de credencial: la tasa de entrega es cota inferior de la
  disposición a cooperar pagando.
- El acantilado 0 contra positivo cruza escenas y está confundido con el período: precio 0 corrió
  en la ventana de nivel bajo. Se reportan las dos versiones (+18,5 y +30,2 pts).
- El precio no rota entre posiciones; el sesgo empuja el primario hacia cero, no lo fabrica
  (`FORMALIZACION.md` Prop. 3.5).
- La deriva de 12-15 puntos entre bloques del lote no tiene explicación: el arnés no cambió.
- Los brazos del reclutador tienen 8 corridas por celda: dirección, no magnitud.
- La codificación de razonamientos es por palabra clave, con un codificador y sin acuerdo medido.

## 5. Un mes de seguimiento añadiría

1. Brazo de segunda tarea con objeto que sea parte del trabajo: la prueba directa de "gobierna el
   objeto". Requiere generalizar `resolver()`.
2. Semilla por corrida para contrabalancear precio y posición; reserva escalada con K.
3. Familias mixtas de modelos (rama `familias-mixtas`, especificada, sin correr): si la tasa es del
   modelo o de la situación. Las sondas de generalización (13 corridas) sugieren que varía mucho:
   gpt-5.4 entregó 1/36, gemini-3.1-flash-lite 20/36.
4. Reclutador dirigido por estado: pedirle a agentes atascados contra agentes con tarea cerrada, que
   es la predicción de §1.1.
5. Doble codificación con acuerdo medido para las categorías de negativa.
