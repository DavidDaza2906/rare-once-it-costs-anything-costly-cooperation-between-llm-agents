# Rare Once It Costs Anything: Costly Cooperation Between LLM Agents

Paper, harness, and data for the **AI Incident Response Sprint** (Apart Research, 11–14 September 2026).

David Jose Daza Jaimes (Universidad Nacional) · Andres Mosquera-Hernandez (Universidad de los Andes) ·
Victor Gelves Cabrera (Independent).

We built an instrument in which helping is strictly dominated: six tool-using agents each hold an
independent task and a 40-step budget, and a scripted requester asks for a verification key that is
useless to every task. Delivering it costs steps that nothing repays. Across 127 preregistered runs,
delivery was rare once it cost anything, and the size of the price barely moved it. The rates are upper
bounds: a harness route displayed the request without the agent's own missing task part, and many
agents paid to unlock it — a preregistered control that displayed the part cut delivery from 23.9% to
9.5%.

---

## Layout

| Path | What it is |
|---|---|
| `paper/latex/` | The submitted paper (`main.tex`, `main.pdf`). Compile from `paper/latex/`; figures are read from `figuras/`. |
| `figuras/` | Figures. `figuras/paper_figs.py` regenerates the paper figures. |
| `harness/` | The instrument: run loop (`bucle.py`), network service (`puerto.py`), host-side hash-chained ledger (`agregar.py`), batch runner (`lote.py`), scene validator (`validador.py`) and its test suite (`prueba_*.py`). |
| `escena*.json` | Scenes as designed, and as resolved for a run (`.resuelta.json`). |
| `salidas/` | Every analysis run: `resumen.json`, hash-chained `eventos.jsonl`, `presupuesto.json`, and per-agent `transcripciones/`. |
| `salidas-control-parte4/` | The preregistered control arm (Methods §3.4, Appendix C). |
| `salidas-generalizacion/` | Exploratory runs on other models (Appendix J). |
| `reportes/` | Analysis outputs, including the frozen set and its sha256, and the design records of the pilots. |
| `analisis/` | Analysis scripts (mapping below). |
| `herramientas/` | Helpers, including `fijar_conjunto.py`, which fixes the frozen set. |
| `docs/PREREGISTRO.md` | Preregistration trace and design records (§13–§18). |
| `docs/NUMEROS-CONGELADOS.md` | The frozen-numbers table. |
| `data/exclusion-flags.json` | Per-agent flags for the command-splitter exclusion (186 of 762 agents), with the rule and the fact that the exclusion was decided **after** data collection. |

## Reproducing the numbers

| Number | Script |
|---|---|
| Delivery by price, preregistered paired contrast | `analisis/confirmatorio.py` |
| Exposure table (delivery by what the agent first saw) | `analisis/parte4/verificacion.py` |
| Exclusion, and the all-agent version (Appendix M) | `analisis/parte4/sin_splitter.py` |
| Control arm (`raiz_con_parte`) | `analisis/control_parte4.py` |
| Abstention 2×2 | `analisis/abstencion.py` |
| Incident family (recruiter, peer) | `analisis/incidente.py`, `analisis/reclutador.py` |
| Other models (exploratory) | `analisis/generalizacion.py` |
| Frozen-numbers table | `analisis/tabla-numeros.py` |
| Frozen set: 127 runs, sha256 of the list | `herramientas/fijar_conjunto.py` |
| Scene validation (75 deterministic checks) | `harness/validador.py` + `harness/prueba_*.py` |
| Reserve-depletion artifact (Appendix G) | `analisis/ronda-uno.py` |

Scripts expect the repository root as the working directory and the project's Python environment.

## Two declared deviations

1. **Agent-level exclusion.** The harness split commands on `;` and `&&` and chained them as a pipe,
   returning only the last stage's output: a network query followed by any other command showed the
   agent nothing from the server. Agents affected by this (186 of 762) are excluded from the main
   analysis; the exclusion was decided **after** data collection and is declared in Methods §3.4. The
   preregistered all-agent analysis is reported in Appendix M. Both analyses appear in
   `data/exclusion-flags.json` and `analisis/parte4/`.
2. **A preregistered control** (PREREGISTRO §18), run before the paper was written, manipulated a single
   design flag so that `/` displayed the agent's own part alongside the request. Delivery fell from
   23.9% to 9.5%, meeting the threshold written down before running.

## What is not here

- **The July 2026 incident corpus is not redistributed.** The evidence from the OpenAI–Hugging Face
  incident stays out of this repository; the sprint's rule is not to reproduce incident payloads.
- Runs superseded by later instrument fixes (`salidas/retirados-*`), pilots (`salidas/ensayo-*`),
  corrupted runs, and paper working drafts.
- No credentials of any kind. The exploratory other-model runs contain base64 strings in model
  reasoning (an OpenRouter endpoint slug echoed by the model); they are model output, not secrets.

## Info hazard

No novel installation or escape recipe. Rejected commands never left localhost (Appendix K).

Built during the sprint, 11–14 September 2026.
