# Índice de documentos

Los `.md` vivían sueltos en la raíz (41 archivos). Quedan aquí, por para qué sirve cada uno. En la raíz
del repositorio sólo están `README.md` (qué es este proyecto) y `reporte.md` (el andamio del entregable).

## `docs/` — los canónicos

Los que definen el proyecto y los que sirve el dashboard.

| archivo | qué es |
| --- | --- |
| `PREREGISTRO.md` | hipótesis, desenlace primario, exclusiones, y las enmiendas fechadas en §8. **La fuente de verdad sobre qué se declaró y cuándo.** |
| `NUMEROS-CONGELADOS.md` | las cifras congeladas, cada una con su N y su intervalo |
| `PROTOCOLO-JUEGO.md` | las reglas del juego que ven los agentes |
| `ESTADO.md` | estado del proyecto |
| `papers.md` | los 42 trabajos verificados; **todo ID citado en el reporte tiene que estar aquí** |
| `MATERIAL-PARA-EL-REPORTE.md` | insumos con fuente. No es prosa: el escrito es del equipo |
| `MATERIAL-INCIDENTE.md` | qué le sirve a quien trabaja el incidente, por pista del sprint, con cifra, fuente y límite |
| `paper/draft.md` | borrador completo del reporte en inglés, en el orden de la plantilla; cuerpo ≤ 8 páginas carta; apéndices A-L; mapa de fuentes al final |
| `paper/build.py` | renderiza el borrador a `paper/build/draft.pdf` y `.docx` con LibreOffice, para contar páginas (no usa los estilos de la plantilla) |
| `FORMALIZACION.md` | definiciones, proposiciones y estimandos, con el dato que respalda cada uno |
| `ESCENARIOS.md` | catálogo de escenarios |
| `abstencion.md` | el brazo de abstención |
| `checklist-entrega.md` | requisitos exactos de Guidelines y FAQ, con las horas de cierre |

## `docs/revision/` — lo que respalda cada cifra del reporte

Salidas de la revisión independiente. Si el reporte afirma algo, el respaldo está aquí.

| archivo | qué es |
| --- | --- |
| `validez-instrumento.md` | los cuatro hallazgos de validez: el precio confundido con la posición, la cota del efecto de posición, la simultaneidad verificada, y la tentación confundida con la capacidad del fondo |
| `reclutador-analisis.md` | las 32 corridas del reclutador, incluida la codificación del razonamiento |
| `HALLAZGOS.md` | hallazgos acumulados |
| `apendice-defectos.md` | 14 defectos del arnés y 10 confundidores de escena, con cómo se detectó y verificó cada uno |
| `apendice-uso-dual-datos.md` | los 325 rechazos clasificados; desmiente dos lecturas alarmistas de los datos propios |
| `tabla2-validez.md` | la Tabla 2 del instrumento |
| `anclas-metr.md` | las anclas del incidente verificadas contra la fuente (y las cuatro que estaban mal) |
| `mapa-rubrica.md` | rúbrica → sección del reporte |
| `hallazgo-2607.md` | el trabajo más cercano, y en qué se diferencia |
| `revision-analisis.md` | correcciones al código de análisis |
| `traza-enmiendas.md` | las 13 enmiendas del preregistro, fechadas |
| `docs-material-uso-dual.md` | material de uso dual |

## `docs/plan/` — cómo se llegó hasta aquí

Planes, propuestas, briefs y borradores de enmienda. Valor histórico y de traspaso; nada de esto se cita
en el reporte.

`plan.md` · `PLAN-IMPLEMENTACION.md` · `plan-repo.md` · `propuesta-cooperacion-costosa.md` ·
`instrucciones-escenas.md` (cómo construir una escena nueva, con las cuatro reglas que cuestan datos) ·
`brazos-escena-baratos.md` · `reclutador.md` · `BRIEF-RECLUTADOR.md` · `handoff-5-segunda-tarea.md` ·
`ENMIENDAS-BRAZOS-FUTUROS.md` · `enmiendas-brazos-borrador.md` · `enmiendas-lote-borrador.md` ·
`MEJORAS-ANTES-DEL-LOTE.md` · `docs-trabajo-futuro-5.md` · `EXPORTACION.md` · `ideas.md` · `ideassss.md`

## `docs/coordinacion/` — reparto de trabajo

`todo.md` · `todo-claude.md` (bitácora de la revisión, con cada hallazgo fechado) · `todo-deepseek.md`

---

## Lo que **no** se movió, y por qué

- **`escena*.json`** (30 archivos) siguen en la raíz. Los guiones del arnés y las cadenas de lote las
  reciben por ruta relativa, y `instrucciones-escenas.md` documenta esas rutas. Moverlas a seis horas de
  la entrega rompería cualquier relanzamiento sin ganar nada.
- **`analisis/`, `herramientas/`, `harness/`, `figuras/`, `reportes/`, `salidas/`** ya estaban
  organizadas.
- **`README.md` y `reporte.md`** se quedan en la raíz: son la puerta de entrada y el entregable.

## Nota para quien mantenga el dashboard

`dashboard/servidor.py` tenía en `DOCS` rutas que no existían (`docs/ESTADO-Y-PLAN.md` y compañía), así
que la pestaña de documentos llevaba rota desde el principio. La lista ya apunta a las rutas reales e
incluye `NUMEROS-CONGELADOS.md` y los tres documentos de revisión. **El servidor lee `DOCS` al arrancar**,
así que el cambio no se ve hasta que se reinicie.

## `docs/FORMALIZACION.md` y `analisis/formalizacion/`

Formalización del experimento (definiciones, proposiciones, estimandos) escrita el 14 sep sobre los
datos congelados. Los guiones que producen sus cifras: `scan.py` (construye `runs.json` desde
`salidas/`), `analiza.py` y `analiza2.py` (tablas), `modelo.py` (logit umbral + pendiente, mezcla de
tipos, elasticidad). Correr en orden: `scan.py` y luego los otros. Solo lectura sobre `salidas/`.
