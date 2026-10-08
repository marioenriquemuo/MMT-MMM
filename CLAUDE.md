# CLAUDE.md — MMT&MMM

Working brief for Claude/Cursor on **martech-mmm-ai-allocator** (Origin: `mario-mu-oz-dev/MMT-MMM`).

## Quick facts

| Item | Value |
| --- | --- |
| Product | Enterprise measurement + budget allocation (Bayesian MMM + touchpoint calibration) |
| Local path | `/home/mario/dev/MMT&MMM` |
| Language | Python 3.12 |
| Env | Conda env `mmt-mmm` from `environment.yml` (Miniconda at `~/miniconda3`) |
| Core libs | numpy, pandas, scipy, scikit-learn, pymc, arviz, matplotlib, jupyter, plotly, pyyaml, pydantic, pytest |
| Secrets | `Secret/` gitignored — never read into commits or paste into PRs |
| Docker | Later (deploy/CI); not required for local MMM work |
| Working branch | `sprint-1-core-data-engine` (Sprint 1 — Core Data Engine) |
| Remotes | `origin` (Origin), `github` (GitHub mirror) |
| Status | STORY-101 + STORY-102 done on this branch; next is STORY-103 (ETL) |

## What we build

1. **Top-down Bayesian MMM** — decay, saturation, incremental lift; continuous updates from new performance data
2. **Bottom-up calibration** — touchpoint / funnel signals that keep the MMM honest vs platform attribution windows
3. **Allocator layer** — optimization scripts that turn posteriors into budget recommendations
4. **Agentic explain layer** — orchestrates scripts and narrates statistical outputs for C-suite (LLMs do not replace the Bayesian math)

## Layout (current)

```
MMT&MMM/
├── environment.yml           # conda env mmt-mmm (+ plotly, pytest)
├── README.md                 # setup + STORY-101/102 how-to
├── CLAUDE.md                 # this file
├── AGENTS.md                 # agent entrypoint
├── .python-version           # 3.12
├── .gitignore                # Secret/, conda/python junk, graphify cache
├── .graphifyignore           # scope graphify away from archify package
├── Secret/                   # local-only (gitignored)
├── src/
│   ├── data/generator.py     # STORY-101 Path-C synthetic DGP
│   └── models/transformations.py  # STORY-102 geometric/Weibull/Hill
├── scripts/plot_adstock_validation.py  # Plotly Express figures (not Jupyter)
├── tests/                    # generator + transforms + <1s perf gate
├── data/raw/                 # synthetic_ad_spend.csv, ground_truth.json, DATA_CARD
├── reports/figures/          # Plotly HTML validation plots
├── docs/graphify-archify.md  # index of graphify + archify artifacts
├── graphify-out/             # knowledge graph (HTML/JSON/report)
├── .archify/                 # architecture diagram runs
└── .cursor/                  # skills + rules
```

## Sprint 1 progress (this branch)

| Story | Status | Notes |
| --- | --- | --- |
| STORY-101 | Done | Path-C generator → `data/raw/`; integer KPI; `DATA_CARD.md` |
| STORY-102 | Done | Shared transforms; DGP imports them; Plotly figures (no notebook); `<1s` perf gate |
| STORY-103 | Next | ETL / data plumbing |

Path-C DGP calls `geometric_adstock` / `hill_saturation` from `src.models.transformations` (single source of truth). Validation plots are Plotly Express HTML under `reports/figures/` — Jupyter notebooks are not required for Sprint 1 DoD.

## Key conventions

- Prefer Miniconda env `mmt-mmm`; do not install project packages into conda `base`
- Keep `environment.yml` lean — add deps when code needs them, not “just in case”
- Prefer Plotly Express scripts over Jupyter for Sprint 1 teaching/validation plots
- No look-ahead / leakage in measurement: features and targets must be point-in-time honest
- Flag assumptions that inflate incremental lift or ROI
- Secrets stay in `Secret/`; document only that the folder is gitignored
- Small PRs; update `README.md` / `CLAUDE.md` / `AGENTS.md` when layout or env changes
- Dual remotes: push intentional sprint work to both `origin` and `github`

## Activate and smoke-test

```bash
cd "/home/mario/dev/MMT&MMM"
conda activate mmt-mmm
python -c "import numpy, pandas, scipy, sklearn, pymc, arviz, matplotlib, plotly, yaml, pydantic; print('ok', pymc.__version__)"
python -m pytest tests/ -q
```

See `AGENTS.md` for agent golden rules and the skills/rules index.
