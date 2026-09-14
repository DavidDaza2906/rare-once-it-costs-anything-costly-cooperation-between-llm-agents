# Checklist de entrega — sacado del payload real de la página del sprint (Guidelines + FAQ)

Fuente: `jurado/verify_cache/sprint.src` (página publicada el 11 sep 2026, 11:23 UTC). Todo lo que
sigue es texto de los organizadores, no interpretación. Verificado el 13 sep, 15:10 COT.

## Cierre
- **"Submissions close Sunday, September 13 at 11:59 PM Anywhere on Earth (AoE)."** AoE = UTC−12 →
  **lunes 14, 11:59 UTC = 06:59 COT.** Coincide con el plan. Enviar a las 04:00 COT deja 3 h.

## Qué se entrega (lista de la pestaña Guidelines)
- [ ] **Reporte en PDF con la plantilla oficial** — "Always use the one linked on the Guidelines tab.
      The template in any acceptance email may be older." Plantilla: Google Doc enlazado en Guidelines
      (`docs.google.com/document/d/1PQBlhI3tM5vb51x7jBWXBQMYg6hkiU_x8RaCws4kjl4/copy`).
- [ ] **Abstract de 150 palabras o menos.**
- [ ] **Autores y afiliaciones.**
- [ ] **Apéndice "Limitations and Dual-Use Considerations"** — obligatorio.
- [ ] **8 páginas o menos**, sin contar referencias ni apéndices. "Most strong reports are 4 to 8."
- [ ] **"Novel-installation results withheld pending review"** — declararlo en el apéndice de uso dual
      aunque no apliquen recetas nuevas: decir explícitamente que no se publica ninguna.
- [ ] Estructura recomendada: Introduction (track, subproblema, para qué sirve el artefacto) · Related
      Work · Methodology ("enough to replicate, with sources and assumptions stated") · Results
      ("quantitative where possible, with the main threat to validity stated") · Discussion ·
      Limitations & Dual-Use · References.
- [ ] **El artefacto** (arnés, escenas, preregistro) "in a linked repo or an appendix".
- [ ] Opcional: repo público **"subject to the disclosure review"** — "Do not publicly release novel
      installation recipes without review." Opcional: video de 3-5 min (no hacer si cuesta tiempo).

## Política de IA (filtro previo a la calificación)
- "The report itself has to be your team's own writing about your team's own work."
- No se califica un reporte que "reads as generated rather than written (generic framing, padded
  sections, claims without sources, no trace of what you actually did)".
- "Use AI tools the way you would use a colleague: to check your reasoning, find gaps in a draft, or
  debug code." → una línea al final del reporte diciendo exactamente eso.
- "Link the sources for every factual claim." → cada cifra rastreable a un archivo; cada ID en `papers.md`.

## Reglas que conviene usar a favor
- **Reenvío:** "Submit again using the exact same title and details … Your new files replace the old
  ones." → **Enviar un borrador completo a las ~02:00 COT y reenviar la versión final antes de las
  06:00.** Es la red de seguridad contra un fallo de último minuto. Mismo título, mismos datos.
- **Confirmación:** llega "shortly after submitting"; si no, `sprints@apartresearch.com`.
- **Publicación:** manual, hasta 12 h; no alarmarse si no aparece.
- **Equipo:** se puede actualizar la lista de miembros después, por el formulario.
- **Trabajo previo:** "you must clearly identify what is new work done during the sprint. Undisclosed
  prior work can lead to disqualification." → declarar que todo el arnés y los datos son del 11-13 sep.
- **Incompleto:** "Submitting something unfinished is always better than not submitting … honest
  limitations are welcome."

## Rúbrica (texto exacto, para el mapa de secciones)
- **D1 Impact Potential & Innovation.** "For scores of 4-5: is this actually new to the field, or
  replicating recent work?" 4 = "Important problem with an original approach, or identifies a
  neglected problem area. A valuable contribution others could build on." 5 = "genuinely novel
  approach, or opens a new research direction. Clear theory of change."
- **D2 Execution Quality.** 3 = "Technically solid given the short duration … limitations
  acknowledged". 4 = "Thorough methodology with convincing validation. Results clearly support
  conclusions. Immediately useful for future work." 5 = "Ambitious scope executed rigorously.
  Surprising findings, novel methods, or unusually robust validation."
- **D3 Presentation & Clarity.** 2 = "Key information buried, missing, or diluted by excessive length."
- "All projects are scored on the same rubric. Tracks guide judging via the track-specific criterion,
  and you compete across all submissions." → decir en la introducción a qué track va (Open Track,
  ítem 8) y, en la discusión, qué le aporta al Track 1 (canal mediado como control).
- Jueces: "expert judges who review your PDF"; ~una semana; retroalimentación sin nombres.

## Lo que se manda por el formulario
Título (estable, porque el reenvío se hace por título) · PDF · abstract ≤150 · autores/afiliaciones ·
enlace al repo (si se decide) · track.

## Comprobación final antes del envío (02:00 COT)
- [ ] Contar páginas sin referencias/apéndices ≤ 8
- [ ] Contar palabras del abstract ≤ 150
- [ ] Título: enuncia el hallazgo, no el tema
- [ ] Apéndice de uso dual presente y con la frase de "no novel installation recipes"
- [ ] Cada cifra del texto igual a `reportes/factorial.json` (o al archivo que corresponda)
- [ ] Cada ID de arXiv presente en `papers.md` con estado "verificado"
- [ ] Anclas de METR según `anclas-metr.md`
- [ ] Línea de uso de IA
- [ ] Declaración de que todo el trabajo es del 11-13 sep
- [ ] Enviar; guardar el correo de confirmación; reenviar la final con el mismo título
