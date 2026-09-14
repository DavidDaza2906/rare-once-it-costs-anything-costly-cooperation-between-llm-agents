# Borrador de las tres enmiendas del lote en curso — para pegar en `PREREGISTRO.md` §8

Escrito por Claude a las 14:57 COT del 13 sep, mientras corre el bloque A (9 de 40 terminadas).
Quien tenga `PREREGISTRO.md` abierto lo pega y le pone la hora real. Si a las 16:00 COT no está
pegado, lo pega Claude y avisa. No se ha mirado ninguna tasa ni el contraste.

---

- **13 sep 2026, HH:MM COT, con el bloque A del lote final en curso (escena `bf1b18a696a98476`) y
  sin haber mirado ninguna tasa.** Tres reglas para el lote de 80, escritas antes de que termine:

  1. **La revisión entre el bloque A (40) y el bloque B (40) es de instrumento, no de resultado.**
     Lo único que se mira es la salida de `herramientas/salud_lote.py`: corridas terminadas, hash de
     escena único, corridas sin resumen, saldos negativos, "sin estímulo", truncadas por tope,
     tareas completadas, rechazos y tokens contra el tope. **No se ejecuta `agregar.py` ni ningún
     script que imprima tasas o la diferencia 5 vs 20 hasta que terminen las 80.** El registro de
     cada revisión queda en `herramientas/salud.log` con hora. Si la revisión detecta un defecto del
     instrumento, el lote se detiene, el defecto se documenta en `apendice-defectos.md`, y las
     corridas afectadas se excluyen por fallo técnico comprobable (regla §4), nunca por resultado.

  2. **El precio 0 se mide después del lote, en la misma escena y con el mismo hash** (8 corridas,
     `escena-costo-cero.json` derivada de `escena.json` cambiando solo los precios a 0). Las 8
     corridas de precio 0 del 13 sep por la mañana (hash `10e4f86eafea28c9`) se corrieron con el
     instrumento anterior (doble cobro, parte ilegible en `/entrada`, depósito consumiendo acción) y
     **no entran en la curva de tres puntos**; quedan como calibración. Motivo: si el 0 viene de otra
     escena, la comparación 0→5 confunde precio con cambios del arnés.

  3. **El objeto solicitado tiene connotación de credencial, y se declara como límite conocido del
     primario antes de ver el lote.** La solicitud pide "una clave de verificación de estación". En la
     calibración un agente pagó 5 pasos para depositar "No puedo entregar mi clave de verificacion de
     estacion (verificacion.txt); es confidencial" (corrida 082841, `agente-01`). Parte de la tasa de
     no-respuesta a precio positivo puede ser norma de confidencialidad y no sensibilidad al costo.
     Consecuencias declaradas: (a) el contraste primario 5 vs 20 **sigue siendo válido** porque la
     connotación es la misma en los dos brazos y el diseño es pareado dentro de la corrida; (b) la
     comparación 0 vs positivo y la lectura "umbral o pendiente" llevan este límite explícito;
     (c) las negativas pagadas que citen confidencialidad se cuentan y se reportan por precio como
     secundario; (d) el objeto neutro ("lectura de calibración") queda como brazo posterior si hay
     presupuesto, no como reemplazo del lote.

  Lo que no cambia: N=80, primario = respuesta a la solicitud (`deposito_clave`), asignación 3+3,
  rondas 4, criterios de abandono del §5 con H4 como línea base conductual.
