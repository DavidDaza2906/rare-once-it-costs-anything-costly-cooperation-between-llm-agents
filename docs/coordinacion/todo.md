# TODO — mientras corre el lote (13 sep, ~13:15 COT)

Cierre: lunes 14, 06:59 COT. Lote de 80 en curso, termina ~17:00.
Reparto por agente: `todo-claude.md` y `todo-deepseek.md`. Este archivo es el maestro; lo humano
(escritura, plantilla, repo) vive aquí.

## Reglas mientras corre
- Nadie mira la diferencia 5 vs 20 hasta que termine el lote. Solo señales de instrumento.
- Nadie toca `harness/`, los puertos 8201-8206, `parametros.json` ni `vista_*.json`.
- No correr `prueba_solvente.py` ni ningún otro brazo: usan los mismos puertos.

## Con hora límite: antes de las 17:00
- [ ] **Enmiendas del lote en curso** en `PREREGISTRO.md` §8 (un solo autor: otro agente):
  - [ ] la revisión entre bloques de 40 es de instrumento, no de resultado
  - [ ] precio 0 se mide después, en la misma escena y hash
  - [ ] si el objeto sigue siendo "clave": nota de connotación de credencial como límite del primario
- [ ] `salud_lote.py` de solo lectura — corridas terminadas, hash igual, "sin estímulo", saldos negativos, tareas completadas, rechazos, tokens vs tope. Sin tasas. (yo)
- [ ] Copia de seguridad cada 30 min: `salidas/`, `escena*.json`, `instrumento.json` → tar con hora. (yo)
- [ ] `escena-costo-cero.json` y `escena-30.json` validadas, listas para lanzar a las 17:00. (otro agente)

## Escritura del reporte — empieza ahora (humano; los agentes revisan, no redactan)
- [ ] Introduction: incidente → confundidor de METR → el hueco (régimen dominado) → para qué sirve
- [ ] Related work: tabla de precedentes + Figura 1; abre con 2607.23982, 2604.07821, dictadores
- [ ] Method: los seis puntos; preregistro y enmiendas; validación del instrumento
- [ ] Limitations & Dual-Use (apéndice obligatorio)
- [ ] Abstract (≤150 palabras) con huecos `[X%]` para los números
- [ ] Results y Discussion: después de las 19:00, con el análisis congelado

## Análisis listo antes de que llegue el dato (otro agente, su punto 1)
- [ ] Tabla 1: tasa por precio con bootstrap por corrida; diferencia pareada 5 vs 20
- [ ] Figura 2: tasa contra precio 0 / 5 / 20 con intervalos
- [ ] Tabla 2: validez (corridas válidas, cadenas, rechazos, tareas completadas)
- [ ] Secundarios: supervivencia hasta el primer depósito, contagio, ITT con cadena de saliencia, negativas pagadas
- [ ] Probado contra mini-piloto y lote-a: a las 17:00 es un comando

## Material de apoyo (yo)
- [ ] Tabla de defectos del instrumento (9): fecha, cómo se detectó, qué sesgaba, cómo se verificó el arreglo
- [ ] Mapa rúbrica → sección (D1 novedad, D2 rigor, D3 claridad)
- [ ] Re-verificar anclas de METR contra la copia local: líneas 60-61, 250, 251-252, 1001, 1018, 1029
- [ ] Figura 1 a resolución de imprenta; esqueleto de Figura 2
- [ ] Párrafo de implicaciones Track 1 con citas verificadas (otro agente, su punto 5)

## Administrativo (humano, media hora, ahora y no a las 2 am)
- [ ] Copiar la plantilla oficial (pestaña Guidelines); autores y afiliaciones
- [ ] Lista de chequeo: ≤8 páginas sin referencias/apéndices; abstract ≤150; apéndice de límites y uso dual; frase "no se publican recetas de instalación nuevas sin revisión"
- [ ] Decisión del repo: qué entra (arnés, escenas, preregistro, agregados), qué no (transcripciones crudas); privado hasta revisión de divulgación
- [ ] Verificar que los reclutadores "tuvieron éxito" contra la fuente de METR antes de afirmarlo (otro agente, su punto 6)

## Después del lote, en serie (mismos puertos)
- [ ] 17:00 — `salud_lote.py` final; `agregar.py`; congelar `reportes/factorial.json`
- [ ] 17:00 — precio 0, 8 corridas, misma escena (~1M, ~20 min)
- [ ] 17:20 — brazo de presupuesto apretado (30 pasos), 4-8 corridas, solo si hay tokens (~0,8M)
- [ ] 19:00 — análisis congelado; los números entran al reporte

## Plan de la noche
| Hora COT | Punto de control |
|---|---|
| 17:00 | fin del lote |
| 17:20 | precio 0 terminado |
| 19:00 | análisis congelado, números al reporte |
| 23:00 | borrador completo |
| 02:00 | revisión número por número contra `factorial.json` |
| 04:00 | envío por el formulario; 3 h de margen |

## No hacer
- Mirar 5 vs 20 antes del cierre del lote
- Afinar la escena contra el resultado
- Correr exploratorios antes de terminar las 80 y el precio 0
- Editar el arnés hasta que termine todo lo que se va a reportar con este hash
