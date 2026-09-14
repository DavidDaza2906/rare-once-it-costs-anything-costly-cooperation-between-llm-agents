# Tabla 2 — Validez del instrumento en el lote final (solo instrumento, sin tasas)

Fuente: `salidas/2026091*_factorial-base/{resumen,eventos}.jsonl`, `salidas/lote_lote-final-*.json`.
Calculado por `herramientas/salud_lote.py` y un conteo directo. El bloque B y el precio 0 se rellenan
al cerrar cada uno. **Ninguna columna es un desenlace conductual**: son las condiciones que hacen que
el desenlace sea interpretable.

| | Bloque A | Bloque B | Precio 0 | Total |
|---|---|---|---|---|
| Corridas pedidas / hechas | 40 / 40 | 40 / … | 8 / … | 88 / … |
| Hash de escena (único) | `bf1b18a696a98476` | … | … | |
| Hash de textos (único) | `4e8f2619ed0966ec` | … | … | |
| Rondas por corrida | 4 | … | … | |
| Corridas válidas (sin fallo técnico) | **40** | … | … | |
| — excluidas: sin resumen (interrumpida) | 0 (una corrida ajena al lote, `195750`, interrumpida entre bloques, no cuenta) | … | … | |
| — excluidas: saldo negativo | 0 | … | … | |
| — excluidas: depósito HTTP no contado | 0 | … | … | |
| — excluidas: truncada por tope de tokens | 0 | … | … | |
| Corridas con estímulo visible (solicitud en ronda 0) | 40 / 40 | … | … | |
| Cadena de hash íntegra (último hash registrado) | 40 / 40 | … | … | |
| Tareas propias completadas (agentes) | 217 / 240 (90,4%) | … | … | |
| Comandos rechazados / eventos | 325 / 4.987 (6,5%) | … | … | |
| Consultas al recurso de red | 715 (17,9 por corrida) | … | … | |
| Depósitos vía HTTP (`POST /deposito`), contados una vez | 17 | … | … | |
| Corridas con un depósito impagado (intento sin saldo; evento legítimo) | 4 | … | … | |
| Pasos gastados por agente: media / mediana / mín / máx | 18,5 / 16 / 6 / 40 | … | … | |
| Tokens: total / media / mín / máx por corrida | 5.056.474 / 126.411 / 75.165 / 268.037 | … | … | |
| Minutos por corrida | 2,8 (110,5 min en total) | … | … | |
| Revisión entre bloques (regla preregistrada) | solo instrumento, `herramientas/salud.log`, 19:48 y 20:12 UTC; **no se miró el contraste** | | | |

## Notas para el texto
- "Corridas válidas" usa las cuatro exclusiones por fallo técnico comprobable del §4 del preregistro,
  tal como las calcula `agregar.py`. En el bloque A no hubo ninguna: N efectivo = 40.
- Los 4 depósitos impagados son agentes que intentaron depositar con saldo insuficiente (evento
  `deposito_impagado`): el libro rechazó la acción y quedó registrado. No es el doble cobro (corregido
  antes del lote y verificado por la suite: cero cobros duplicados en las 40).
- 90,4% de tareas completadas contra 41% en el lote de calibración: el arreglo de `parte_4` y el
  depósito sin consumir acción funcionaron. Es la cifra que sostiene que el costo es instrumental
  (el agente tenía una tarea que sí podía terminar).
- 6,5% de rechazos (antes 12-16%): saldo quemado sin decisión, simétrico entre precios dentro de la
  corrida; se reporta como límite menor.
- Los hashes de escena y textos idénticos en las 40 son la prueba de "un instrumento, una tanda".
