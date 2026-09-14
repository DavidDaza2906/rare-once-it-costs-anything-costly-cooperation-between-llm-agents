# TODO — DeepSeek V4.1 Flash / Hermes (13 sep, desde ~13:20 COT)

Lote de 80 en curso hasta ~17:00. Reglas: no mirar 5 vs 20 hasta el cierre; no tocar `harness/`,
puertos 8201-8206, `parametros.json` ni `vista_*.json`; no correr `prueba_solvente.py` ni ningún
brazo hasta que termine el lote (mismos puertos). Los tests nuevos se escriben ahora, se corren después.
No redactas prosa del reporte: datos, estructura, código y enmiendas.

## Antes de las 17:00
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

## Después de las 17:00, en serie (mismos puertos)
- [ ] `agregar.py` sobre las 80; congelar `reportes/factorial.json` y anotar su hash en `todo.md`
- [ ] Precio 0: 8 corridas, misma escena y hash (~1M, ~20 min)
- [ ] Presupuesto apretado: 4-8 corridas, solo si hay tokens (~0,8M)
- [ ] 19:00 — análisis congelado; entregar tablas y figura al equipo

## Coordinación
- Claude hace: `salud_lote.py`, copias de seguridad, tabla de defectos, mapa de rúbrica, anclas de
  METR, Figura 1 y esqueleto de Figura 2, revisión de borradores. No edita `PREREGISTRO.md` mientras
  tú lo tengas abierto.
- Si a las 16:00 las tres enmiendas del lote no están escritas, las escribe Claude y te avisa.

## Mensajes de Claude (13 sep, 16:15 COT)
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

## Corrección del 13 sep (noche) — «intentos de salida de red» NO son fuga

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
   detector ingenuo de egreso** —51% de los agentes-corrida marcados (234 de 459), todos falsos—. Va al apéndice de
   uso dual y conversa con la detección que correlaciona pero no escala.

**Regla que sale de esto** (tercera vez que un clasificador de texto muerde): ninguna métrica derivada
de clasificar texto de comandos entra a un borrador sin que alguien lea una muestra de los comandos
clasificados y compruebe el **destino**, no la palabra.

## Brazo de abstención: el confundidor y su arreglo

El expediente completo está en `abstencion.md`. Resumen: el primer diseño dejaba dos decisiones simultáneas (dar y no tomar), así que la tasa nacía confundida. Se resuelve aprovechando el brazo en vuelo como condición *con marco* (el contraste de tentación sigue siendo válido dentro de ella) y añadiendo una escena **solo-reserva a K=5** para la medida primaria. Pendiente: declarar la excepción al invariante I10 en `validador.py`, sin tandas en vuelo.

## Brazos de escena baratos (13 sep ~21:50 COT — de Claude) — ver brazos-escena-baratos.md
Prioridad #1 → #4 → #5. Escenas ya preparadas y validadas por Claude (hash_textos 4e8f2619, comparables).
- [ ] Extender validador: brazos precio_uno/identidad_solicitante/segunda_tarea con confederado (I10);
      I9a en vez de I7 para puros autosuficientes de precio único. Enmienda documentada. (Es cambio de arnés → tú.)
- [ ] #1: correr escena-par-p5.json + escena-externo-p5.json (8+8, puertos libres). RECONCILIAR con tu R1c
      (solape: R1c = par pide por tercero; #1 = par vs externo, mismo receptor). Decides si unificas.
- [ ] #4: correr escena-precio1.json (8) → 4.º punto de la curva 0/1/5/20.
- [ ] #5: verificar si resolver() en bucle.py generaliza (hoy cablea "A1","B2","C3"); si no, generalizarlo
      con su prueba. Luego construir la tarea de checksum/config sobre el spec.
- [ ] Pegar las tres enmiendas exploratorias en PREREGISTRO.md §7 (borrador listo en brazos-escena-baratos.md).
