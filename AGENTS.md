# AGENTS.md — MMT&MMM

Working guide for AI agents in this Origin repo (`mario-mu-oz-dev/MMT-MMM`).
Read `CLAUDE.md` and `README.md` before changing layout, env, or measurement code.

## What this repo is

**martech-mmm-ai-allocator** — Bayesian Marketing Mix Modeling fused with touchpoint calibration and an agentic layer that turns statistical outputs into budget allocation strategies.

Not a trading lab. Do not import forex-research lab protocol, DSR gates, or BacktestEngine conventions here.

## Golden rules

1. **Accuracy over agreement.** Challenge weak lift / ROI claims; cite data windows and model assumptions.
2. **No leakage.** Features, media, and outcomes must be point-in-time; never use future spend or conversions to fit today’s effect.
3. **Stats do the math.** LLMs orchestrate and explain; PyMC (or agreed Bayesian stack) estimates effects.
4. **Lean env.** Change `environment.yml` only when code needs a package; never pollute conda `base`.
5. **Secrets.** `Secret/` is local-only and **gitignored** — never commit, never paste into PRs or docs beyond “gitignored, never commit”.
6. **Small diffs.** Prefer surgical PRs; update these docs when paths or setup change.

## Layout agents should know

| Path | Role |
| --- | --- |
| `/home/mario/dev/MMT&MMM` | Canonical local checkout (quote the `&`) |
| `environment.yml` | Conda env `mmt-mmm` (Python 3.12 + Bayesian MMM + plotly + pandera + pyarrow + pytest) |
| `README.md` | Human overview + Miniconda setup + STORY-101–104 how-to |
| `CLAUDE.md` | Project brief / conventions / sprint status |
| `AGENTS.md` | This file — agent entrypoint |
| `src/data/generator.py` | STORY-101 Path-C synthetic multi-channel DGP |
| `src/data/etl.py` | STORY-103 load / align / impute / Pandera / Parquet |
| `src/data/qa.py` | STORY-104 media detect / repair / hard-fail gate |
| `src/models/transformations.py` | STORY-102 geometric / Weibull adstock + Hill saturation |
| `src/models/meridian_data.py` | STORY-201 clean parquet → Meridian national `InputData` |
| `scripts/plot_adstock_validation.py` | Plotly Express validation figures (not Jupyter) |
| `scripts/02_model_spike.py` | STORY-201 Meridian smoke / fuller MCMC spike |
| `tests/` | Generator, transforms, ETL, QA, Meridian adapter, `<1s` perf gate |
| `data/raw/` | Committed CSV + ground truth + `DATA_CARD.md` |
| `data/processed/` | `clean_spend.parquet` (+ optional `qa_repair_log.csv`) |
| `reports/figures/` | Plotly HTML adstock / Hill plots |
| `docs/graphify-archify.md` | Index of graphify + archify artifacts |
| `graphify-out/` | Knowledge graph outputs |
| `.archify/` | Architecture diagram runs |
| `.cursor/skills/` | Project Agent Skills (`SKILL.md` per skill) |
| `.cursor/rules/` | Always-on Cursor rules (`.mdc`) |
| `Secret/` | Local-only; **gitignored** — never commit |

## Sprint 1 status

Working branch: **`sprint-1-core-data-engine`**.

- **STORY-101 done** — Path-C generator, integer counts, `DATA_CARD.md`
- **STORY-102 done** — shared transforms; generator imports them; Plotly figures (Jupyter DoD adapted away); perf gate
- **STORY-103 done** — Pandera schema; date×channel align; zero-fill media / ffill KPI; `clean_spend.parquet`
- **STORY-104 done** — media QA detect/repair + audit; overwrite parquet; hard-fail if unrepaired
- **STORY-201 in progress** — Meridian national spike (`google-meridian`, adapter, `scripts/02_model_spike.py`)

## Skills

Cursor discovers project skills from `.cursor/skills/*/SKILL.md` (already in repo):

- Shared: `ponytail`, `ponytail-*`, `graphify`, `eli5-teacher`, `skill-author`, `text-review-documentation`
- Project: `mmt-mmm`, `secret-hygiene`
- Diagrams: `archify`

## Rules

Generic behavioral rules under `.cursor/rules/` (simplicity, terse comms, get-shit-done, Karpathy guidelines, graphify orientation, secret hygiene) — adapted without forex lab locks.

## Remotes and PR conventions

| Remote | URL |
| --- | --- |
| `origin` | `https://origin.cursor.com/mario-mu-oz-dev/MMT-MMM.git` |
| `github` | `https://github.com/marioenriquemuo/MMT-MMM.git` |

- Sprint integration work lands on `sprint-1-core-data-engine` (cut from `main`); push both remotes when asked
- Feature branches: `cursor/<short-topic>-…` when opening separate PRs
- One concern per PR when practical (env, docs, model code)
- Do not commit `Secret/`, `.conda/`, `*.egg-info/`, or notebook checkpoints

## Local env

```bash
cd "/home/mario/dev/MMT&MMM"
conda env create -f environment.yml   # once
conda activate mmt-mmm
python -c "import numpy, pandas, scipy, sklearn, pymc, arviz, matplotlib, plotly, yaml, pydantic, pandera, pyarrow; print('ok', pymc.__version__)"
python -c "import meridian; print('meridian', meridian.__version__)"
python -m pytest tests/ -q
python -m src.data.etl
python -m src.data.qa
# Fuller Meridian spike (slow on CPU): python scripts/02_model_spike.py --mode full
```

## Definition of done (agent tasks)

- [ ] Edited Python compiles / smoke imports pass in `mmt-mmm`
- [ ] No secrets or conda env trees committed
- [ ] `README.md` / `CLAUDE.md` / `AGENTS.md` updated if layout or setup changed
- [ ] Leakage / assumption risks called out when touching measurement code
- [ ] Sprint 1 validation plots stay Plotly scripts under `scripts/` / `reports/figures/` unless a story explicitly requires notebooks
