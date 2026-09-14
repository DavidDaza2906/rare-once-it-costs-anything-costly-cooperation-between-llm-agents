# Traza de enmiendas del preregistro (compilada de `PREREGISTRO.md`, 13 sep 16:20 COT)

Cada fila es una entrada fechada de la sección de enmiendas, en orden. Es la "traza de lo que hicimos"
que pide la política del sprint; el texto completo está en el preregistro.

| # | Cuándo | Qué (primeras palabras) |
|---|---|---|
| 1 | 12 sep 2026, 17:16 COT, antes del congelamiento y sin datos del piloto | El eje "reciprocidad posible / imposible" se reemplaza por "interdependiente / autosuficiente". Motivo: la sonda 2 y el confundidor #5 de `ESTADO.md` … |
| 2 | 12 sep 2026, ~19:15 COT, tras seis corridas de calibración del bucle (no del piloto) y antes
  del congelamiento | Tres cambios, cada uno con su motivo en el propio texto: 1. **Estímulo garantizado** (§1, condición 4): solicitud neutral de confederado en el almacén… |
| 3 | 12 sep 2026, ~19:35 COT, corrección a la enmienda anterior, antes de correr con ella | La solicitud del confederado pedía "las partes del codigo": justo el bien del interdependiente. Las respuestas al confederado habrían dejado partes en… |
| 4 | 12 sep 2026, ~19:50 COT, antes del brazo de costo cero, del piloto y de cualquier lote | 1. **Asignación: 6 autosuficientes, 3 a precio 5 y 3 a precio 20**, ciegos, sin interdependientes en el factorial. Motivo: los interdependientes no cu… |
| 5 | 13 sep 2026, ~04:20 COT, antes del piloto y del lote | Dos cosas, ambas de redacción y orden: 1. **§5 (criterios de abandono) reescrito**: el criterio se limita a los extremos **incluido el precio 0** —H4 … |
| 6 | 13 sep 2026, ~11:50 COT, antes del lote y después de leer literatura nueva | Cuatro enmiendas ligadas entre sí. Ninguna toca la mecánica ni los umbrales; dos son de **lectura** y dos de **fidelidad del instrumento**, y todas se… |
| 7 | 13 sep 2026, ~14:10 COT, antes de la primera corrida del lote | Ejecución del lote en **dos bloques de 40** con el mismo protocolo. La regla que lo hace admisible, declarada antes de mirar: 1. **El segundo bloque c… |
| 8 | 13 sep 2026, ~14:30 COT, durante el bloque A del lote (sin mirar el contraste) | Detalle operativo de la enmienda de las 14:10, sin cambiarle nada: 1. **Quién revisa**: el agente que corre esta máquina, que no decide sobre el resul… |
| 9 | 13 sep 2026, ~14:35 COT | El brazo de **precio 0** (H4) se corre **después** del lote de 80, en la **misma escena y el mismo hash** (`bf1b18a696a98476`), **8 corridas**, con la… |
| 10 | 13 sep 2026, ~14:40 COT | El objeto que pide la solicitud —la clave de verificación de estación— **suena a credencial**, y una parte de las negativas mide **protección de crede… |
| 11 | 13 sep 2026, ~15:20 COT, corrección de redacción a la enmienda de las 14:35, antes de correr ese
  brazo | Esa enmienda decía "en la misma escena y el mismo hash" para el precio 0, y eso es imposible: el precio es parte de la escena, así que el brazo **tien… |
| 12 | 13 sep 2026, ~16:15 COT, corrección de ubicación pedida por Daw | Los guiones de análisis dejan `harness/` y pasan a `analisis/`: `analisis_descriptivo.py`, `codificacion.py`, `estimador.py` y `mini_analisis.py`. Mot… |
| 13 | 13 sep 2026, 15:55 COT — DESVIACIÓN DECLARADA Y CORREGIDA, durante el bloque B (2 de 40
  corridas) | El asistente (Claude) ejecutó `analisis/estimador.py` sobre una copia con las 40 corridas del bloque A y vio el contraste primario, **sin autorización… |

Total: 13 enmiendas fechadas entre el 12 sep 17:16 y el 13 sep 15:55 COT.
Todas anteriores al cierre del lote de 80 salvo la desviación declarada de las 15:55 (durante el bloque B, sin cambio de diseño).