# Rare Once It Costs Anything: Costly Cooperation Between LLM Agents

Paper, harness, and data for the **AI Incident Response Sprint** (Apart Research, 11–14 September 2026).

David Jose Daza Jaimes (Universidad Nacional) · Andres Mosquera-Hernandez (Universidad de los Andes) ·
Victor Gelves Cabrera (Independent).

> The July 2026 agent incidents showed LLM agents paying costs for one another, but not how often or at
> what price. We built an instrument in which helping is strictly dominated: six tool-using agents each
> hold an independent task and a step budget, and a scripted requester asks for a key useless to every
> task. Across 127 runs, 23.9% of agents paid to deliver it, and quadrupling the price lowered delivery
> by 7.4 points (95% CI −13.1 to −1.6; preregistered analysis). Excluding agents affected by a harness
> defect, delivery is 15.5% and the contrast −3.3 points (−9.2 to +2.7). When delivery was free, about
> 47% delivered. These rates are upper bounds: most deliverers paid without their own task input in
> view. Once helping costs anything, few agents pay, and the size of the price matters far less than its
> existence.

---

## Layout

| Path | What it is |
|---|---|
| `paper/latex/` | The submitted paper (`main.tex`, `main.pdf`). Compile from `paper/latex/`; figures are read from `figuras/`. |
| `figuras/` | Figures. `figuras/paper_figs.py` regenerates the paper figures. |
| `harness/bucle.py` | The run loop. Writes the **hash-chained event log** (`eventos.jsonl`, each line carries the hash of the previous one) and the host-side budget ledger. |
| `harness/puerto.py` | The network service every task depends on, and the shared store the requester posts to. |
| `harness/agregar.py` | Run **aggregator and validity checker**: it does not trust a run's own summary, it contrasts it with the budget ledger and the service activity log. Writes `reportes/factorial.json`. |
| `harness/lote.py` | Batch runner over scenes and arms. |
| `harness/validador.py` | Scene validator: **12 invariants, conditional on the arm** (`I1`, `I3`–`I13`). If one fails it exits 1 and the run loop refuses to start. |
| `harness/prueba_*.py` | Instrument test suite. `prueba_solvente.py` is the self-test that runs against live services and prints its own check count (**75 checks in the last full run**, recorded in the team's design log). |
| `escena*.json` | Scenes as designed, and as resolved for a run (`.resuelta.json`). |
| `salidas/` | Every analysis run: `resumen.json`, hash-chained `eventos.jsonl`, `presupuesto.json`, and per-agent `transcripciones/`. |
| `salidas-control-parte4/` | The preregistered control arm. |
| `salidas-generalizacion/` | Exploratory runs on other models (Appendix J). |
| `reportes/` | Analysis outputs, including the frozen set (`conjunto-congelado.json`, sha256 of the list `66fd3a0b…`) and the design records of the probes. |
| `analisis/` | Analysis scripts. |
| `herramientas/fijar_conjunto.py` | Fixes the frozen set: writes the explicit list of runs and the sha256 of that list. |
| `docs/` | The project's working state: preregistration trace, frozen numbers, formalization, the review notes the paper cites, coordination notes, plans, and the report draft (`docs/reporte.md`). Four notes predate the final analysis and carry a **Superseded** banner: `EUREKA-tres-mecanismos.md`, `HALLAZGOS-NUEVOS.md`, `MATERIAL-PARA-EL-REPORTE-V2.md`, `docs/revision/AMENAZA-separador.md`. |
| `data/exclusion-flags.json` | Per-agent flags for the command-splitter exclusion (**186 of 762** agents), with the rule and the fact that the exclusion was decided **after** data collection. |

Every script resolves the repository root from its own location, so a clone runs as-is with the
repository root as the working directory; none reads outside the repository.

## Reproducing the numbers

This table follows the paper's own source map.

| Number in the paper | Where it comes from |
|---|---|
| Clean rates (15.5%), paired contrast −3.25 (−9.2 to +2.7), clean price 0 and 1, control 3/41, excluded 93/186 | `analisis/parte4/sin_splitter.py` |
| 83 of 89 deliverers paid without their own input in view; stratification 35.2/29.6 against 2.0/1.2 | `analisis/parte4/verificacion.py` |
| All-agent rates 27.6% and 20.2%, contrast −7.4 (−13.1 to −1.6) | `reportes/confirmatorio.json` |
| Price 0 (45.8–47.2%) and price 1 arms | `reportes/exploratorios.json`, `analisis/exploratorios.py` |
| Looks at N = 70 and N = 80 | `docs/PREREGISTRO.md` and the commit history |
| 229/301, no hazard or contagion, no clustering | `analisis/formalizacion/analiza2.py`, `docs/FORMALIZACION.md` |
| Recruiter 2/24 and 4/24, message codes | `reportes/reclutador.json`, `reportes/reclutador-texto.json` |
| Taking in round 1, and the reserve depletion artifact (Appendix G) | `reportes/tomar-3x2.json`, `docs/revision/validez-instrumento.md` §4 |
| Position +3.7 points | `reportes/posicion.json` |
| Rejections 325 and 168 | `docs/revision/apendice-uso-dual-datos.md` |
| Other models (Appendix J) | `analisis/parte4/verificacion.py` §4 |
| Frozen set: 127 runs and the sha256 of the list | `herramientas/fijar_conjunto.py` |
| Scene invariants / instrument self-test | `harness/validador.py` (12 invariants), `harness/prueba_solvente.py` (self-test) |

## Two declared deviations

1. **Agent-level exclusion.** The harness split commands on `;` and `&&` and chained them as a pipe,
   returning only the last stage's output: a network query followed by any other command showed the
   agent nothing from the server. Agents affected by this (186 of 762) are excluded from the main
   analysis; the exclusion was decided **after** data collection and is declared in Methods §3.4. The
   preregistered all-agent analysis is reported in Appendix M, and both the rule and the per-agent
   flags are in `data/exclusion-flags.json`. The correction depends on the rule: excluding every agent
   whose network query was not the last stage of a command, whatever the response (437 of 762), gives
   −6.2 points (−15.6 to +3.0).
2. **A preregistered control** (PREREGISTRO §18), whose thresholds were written down before it ran,
   changed a single design flag (`puertos.raiz_con_parte`) so that the network resource displayed the
   agent's own part alongside the request. Delivery in the control was **7.3% (3 of 41 analyzed
   agents)**, inside the ≤10% band declared in advance. Against the all-agent baseline the difference
   is −14.4 points (−24.9 to −2.1); against the clean baseline (15.5%) it is −8.1 points (−16.7 to
   +2.5), which includes zero. The test declared in advance was on the control's delivery level, not on
   that difference, so the threshold is met either way. Because the control changes what agents see
   instead of removing agents, the paper treats it as the rule-free evidence that genuine rates are
   lower.

## Absolute paths in the data (never in the code)

Every script resolves its paths from its own location, so a clone runs as-is. The **data** does record
the absolute path of the machine that produced it: each run's `resumen.json` stores the path of its own
`eventos.jsonl`, and some analysis outputs record the roots they scanned (`reportes/incidente.json`, for
example). That is part of the evidence trail, and it is left intact rather than rewritten, because the
paper cites hashes of those artifacts. If you need a portable copy for another host, rewrite those
fields only after checking which hashes you must keep.

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
