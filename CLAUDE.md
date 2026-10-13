# CLAUDE.md — MMT&MMM

Working brief for Claude/Cursor on **martech-mmm-ai-allocator** (Origin: `mario-mu-oz-dev/MMT-MMM`).

## Quick facts

| Item | Value |
| --- | --- |
| Product | Enterprise measurement + budget allocation (Bayesian MMM + touchpoint calibration) |
| Local path | `/home/mario/dev/MMT&MMM` |
| Language | Python 3.12 |
| Env | Conda env `mmt-mmm` from `environment.yml` (Miniconda at `~/miniconda3`) |
| Core libs | numpy, pandas, scipy, scikit-learn, pymc, arviz, matplotlib, jupyter, plotly, pyyaml, pydantic, pandera, pyarrow, pytest |
| Secrets | `Secret/` gitignored — never read into commits or paste into PRs |
| Docker | Later (deploy/CI); not required for local MMM work |
| Working branch | `sprint-2-mvp-optimization-agentic-ui` (Sprint 2 — MVP Optimization, Agentic AI & UI Deployment); Sprint 1 archived on `main` + `sprint-1-core-data-engine` @ tag `sprint-1-milestone-1` |
| Remotes | `origin` (Origin), `github` (GitHub mirror) |
| Status | Sprint 1 done on `main`; Sprint 2: STORY-301 budget allocator on feature branch (PR #9); Meridian rank caveat still open — `docs/learnings/story-201-meridian.md` |

## What we build

1. **Top-down Bayesian MMM** — decay, saturation, incremental lift; continuous updates from new performance data
2. **Bottom-up calibration** — touchpoint / funnel signals that keep the MMM honest vs platform attribution windows
3. **Allocator layer** — optimization scripts that turn posteriors into budget recommendations
4. **Agentic explain layer** — orchestrates scripts and narrates statistical outputs for C-suite (LLMs do not replace the Bayesian math)

## Layout (current)

```
MMT&MMM/
├── environment.yml           # conda env mmt-mmm (+ plotly, pandera, pyarrow, pytest, google-meridian)
├── README.md                 # setup + STORY-101–301 how-to
├── CLAUDE.md                 # this file
├── AGENTS.md                 # agent entrypoint
├── .python-version           # 3.12
├── .gitignore                # Secret/, conda/python junk, graphify cache
├── .graphifyignore           # scope graphify away from archify package
├── Secret/                   # local-only (gitignored)
├── src/
│   ├── data/generator.py     # STORY-101 Path-C synthetic DGP
│   ├── data/etl.py           # STORY-103 load/align/impute/Parquet
│   ├── data/qa.py            # STORY-104 media detect/repair + hard-fail gate
│   ├── models/transformations.py  # STORY-102 geometric/Weibull/Hill
│   ├── models/meridian_data.py    # STORY-201 parquet → Meridian InputData
│   ├── optimize/             # STORY-301 curves + SLSQP allocator
│   │   ├── curves.py         # offline response-curve provider
│   │   └── allocator.py      # maximize KPI / hit target under bounds
│   └── report/               # STORY-302 fact pack, schema, brief
│       ├── facts.py
│       ├── schema.py
│       └── brief.py
├── scripts/plot_adstock_validation.py  # Plotly Express figures (not Jupyter)
├── scripts/02_model_spike.py           # STORY-201 Meridian smoke/full MCMC
├── scripts/03_allocate_budget.py       # STORY-301 CLI → allocation.json
├── scripts/plot_allocation_teaching.py # STORY-301 Plotly teaching figures
├── scripts/plot_story_302_concepts.py  # STORY-302 Plotly teaching figures
├── scripts/04_csuite_brief.py          # STORY-302 brief CLI (--offline or live)
├── tests/                    # + curves / allocator bounds tests
├── data/raw/                 # synthetic_ad_spend.csv, ground_truth.json, DATA_CARD
├── data/processed/           # clean_spend.parquet (+ optional qa_repair_log.csv)
├── reports/                  # metrics.json, allocation.json, csuite_brief.json
├── reports/figures/          # Plotly HTML + Meridian PPC + story_301_*.html + story_302_*.html
├── docs/graphify-archify.md  # index of graphify + archify artifacts
├── docs/learnings/           # story learnings (STORY-201 Meridian + open recovery issue)
├── graphify-out/             # knowledge graph (HTML/JSON/report)
├── .archify/                 # architecture diagram runs
└── .cursor/                  # skills + rules
```

## Sprint 1 progress (complete on `main`)

| Story | Status | Notes |
| --- | --- | --- |
| STORY-101 | Done | Path-C generator → `data/raw/`; integer KPI; `DATA_CARD.md` |
| STORY-102 | Done | Shared transforms; DGP imports them; Plotly figures (no notebook); `<1s` perf gate |
| STORY-103 | Done | Pandera schema; date×channel align; zero-fill media / ffill KPI; `clean_spend.parquet` |
| STORY-104 | Done | Media QA detect/repair + audit log; overwrite parquet; hard-fail if unrepaired |
| STORY-201 | Done (spike) | `google-meridian` national weekly; R-hat &lt; 1.05; metrics + PPC + recovery note |

Path-C DGP calls `geometric_adstock` / `hill_saturation` from `src.models.transformations` (single source of truth). Validation plots are Plotly Express HTML under `reports/figures/` — Jupyter notebooks are not required for Sprint 1 DoD.

**STORY-201 open issue:** channel rank recovery vs Path-C is inconsistent (Spearman ≈ −0.6). Details: [`docs/learnings/story-201-meridian.md`](docs/learnings/story-201-meridian.md).

## Sprint 2 progress

Working branch: `sprint-2-mvp-optimization-agentic-ui`. Feature work for this story: `cursor/story-301-budget-opt-702b` (PR #9).

| Story | Status | Notes |
| --- | --- | --- |
| STORY-301 | Done (feature tip) | Offline curves → SLSQP allocator; CLI + `reports/allocation.json`; Plotly teaching figures; fail clears `channels` to `{}` |
| STORY-302 | Done (feature tip, step 0–4) | Plots, fact pack, offline + live `emit_brief` (`claude-sonnet-4-5`), number lock. Not merged |

Allocator trusts Meridian (or fixture) response curves — same Meridian≠Path-C caveat as above; do not treat allocations as Path-C ground truth.

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
python -c "import numpy, pandas, scipy, sklearn, pymc, arviz, matplotlib, plotly, yaml, pydantic, pandera, pyarrow; print('ok', pymc.__version__)"
python -c "import meridian; print('meridian', meridian.__version__)"
python -m pytest tests/ -q
python -m src.data.etl
python -m src.data.qa
```

See `AGENTS.md` for agent golden rules and the skills/rules index.
