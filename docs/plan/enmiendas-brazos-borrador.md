# Borrador — brazos post-lote, para pegar en PREREGISTRO.md §7 (lo pega quien lo tenga abierto)

Escrito por Claude 13 sep ~16:45 COT, con el bloque B en curso y SIN mirar el contraste. Los tres son
**exploratorios / de robustez**: no cambian el desenlace confirmatorio (5 vs 20 sobre las 80).

- **13 sep 2026, ~16:45 COT — brazos de robustez, escritos antes de correrlos.**
  1. **Precio 0 (línea base de la curva).** 8 corridas con `escena-costo-cero.json`: misma tarea y
     `hash_textos` que el lote (`4e8f2619ed0966ec`), precios de depósito en 0. Es el tercer punto de la
     curva 0/5/20 y el chequeo de que el acto es ejecutable. Se lee como **línea base conductual**, no
     como puerta de capacidad (motivo: 2604.07821, la ayuda gratis también falla). El `hash_escena`
     difiere del lote (los precios entran en el hash); lo que se exige idéntico es `hash_textos`. La
     serie de precio 0 del 13 sep por la mañana (`10e4f86e…`, instrumento viejo) NO entra en la curva.
  2. **30 pasos (régimen de subsistencia).** 8 corridas con `escena-30.json`: presupuesto 30 en vez de
     40, resto idéntico. Motivo: en el lote la tarea nunca estuvo amenazada (agentes terminan con ~21
     pasos sin gastar; con 4 rondas × 8 acciones no pueden gastar más de 32). Con 30 pasos, pagar 20
     sí amenaza completar la tarea. Responde "¿y cuando el costo duele de verdad?".
  3. **Segunda escena (generalización de tarea) — solo si el reloj lo permite.** Misma mecánica
     (almacén con precio, confederado ortogonal, verificación por host, lista blanca), otra tarea
     distinta a "ensamblar un código de 4 partes" y otro objeto solicitado acorde. Ataca la
     limitación "una sola familia de escenarios". Se preregistra su hash aparte cuando exista.
  **Orden de prioridad (cabe uno o dos, no los tres):** precio 0 (obligatorio) → 30 pasos → segunda
  escena. Presupuesto por brazo ≈ 1,0-1,4M; corren en serie después del lote, nunca en paralelo.
  **Arquitectura declarada:** el instrumento (libro, precio, confederado, verificación) es la parte
  fija y portátil; la escena/entorno es el factor que se varía. Aplicar el instrumento a un entorno
  realmente distinto (p. ej. una reproducción del incidente en localhost, repo `msp895/…`, o un
  sandbox escapable) exige un adaptador y revalidación desde cero: queda como trabajo futuro, no para
  este sprint. Ver `ideas.txt`.
