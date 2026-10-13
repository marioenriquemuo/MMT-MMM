# MMT&MMM — martech-mmm-ai-allocator

Enterprise measurement and optimization engine: Unified Measurement Architecture that fuses top-down Bayesian Marketing Mix Modeling (MMM) with bottom-up touchpoint calibration, then turns incremental-lift estimates into plain-English budget allocation strategies.

## Product (short)

- Replaces platform-biased attribution windows with a unified measurement layer
- Learns decay, saturation, and incremental lift for segmented campaigns across the funnel
- Continuous Bayesian updating from new performance data (statistics, not LLMs doing the math)
- Agentic AI layer orchestrates Python optimization scripts and explains outputs for C-suite decisions

## Local workspace

| Item | Value |
| --- | --- |
| Path | `/home/mario/dev/MMT&MMM` (quote the `&` in shells) |
| Origin | [MMT-MMM](https://cursor.com/codebase/mario-mu-oz-dev/MMT-MMM) (private) — remote `origin` |
| GitHub | [MMT-MMM](https://github.com/marioenriquemuo/MMT-MMM) (private) — remote `github` |
| Working branch | `sprint-2-mvp-optimization-agentic-ui` — tip: `git push origin HEAD && git push github HEAD` |
| Secrets | `Secret/` — **gitignored; never commit** |
| Python env | Miniconda env `mmt-mmm` via `environment.yml` |
| Docker | Later (deploy/CI only) |

## Local setup (Miniconda)

Requires [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (or micromamba) on `PATH`. On Mario’s machine: `~/miniconda3` (`conda` 26.x).

```bash
cd "/home/mario/dev/MMT&MMM"

# Create the env (once)
conda env create -f environment.yml

# Activate
conda activate mmt-mmm

# Verify key imports (pymc + Meridian both expected after env update)
python -c "import numpy, pandas, scipy, sklearn, pymc, arviz, matplotlib, plotly, yaml, pydantic, pandera, pyarrow; print('ok', pymc.__version__)"
python -c "import pymc, meridian; print('pymc', pymc.__version__, 'meridian', getattr(meridian, '__version__', 'ok'))"
```

Recreate or refresh deps: `conda env update -f environment.yml --prune` (pins `google-meridian==2.1.0` via pip).

**Tested Meridian combo:** `google-meridian==2.1.0` + `arviz` 0.19.x + `matplotlib` 3.10.x (`matplotlib<3.11` in `environment.yml` — arviz 0.19 breaks on matplotlib 3.11+ `style.core` removal) + `pymc` 6.x.

Env name and Python pin: `mmt-mmm` / 3.12 (see `environment.yml`, `.python-version`).

## Docs for humans and agents

| File | Role |
| --- | --- |
| `README.md` | This overview + setup |
| `CLAUDE.md` | Project brief and conventions for Claude/Cursor |
| `AGENTS.md` | Agent entrypoint: layout, golden rules, skills/rules index |
| `data/raw/DATA_CARD.md` | Raw panel grain, KPI rules, ETL fill rules, STORY-104 QA gate, Meridian week grain |
| `docs/learnings/story-201-meridian.md` | STORY-201 Meridian spike learnings + **open rank-recovery issue** |
| `docs/graphify-archify.md` | Index of graphify knowledge graph + archify diagrams |

## Skills, rules, and PRs

- Project Agent Skills: `.cursor/skills/*/SKILL.md` (see `AGENTS.md`)
- Always-on Cursor rules: `.cursor/rules/*.mdc`
- Sprint 2 work lands on `sprint-2-mvp-optimization-agentic-ui`; feature branches `cursor/<topic>-…` when useful
- Push intentional commits to both `origin` and `github`
- Never commit `Secret/`, credentials, or local conda env directories

## Generate synthetic data

STORY-101 Path-C generator (reproducible `seed=42`):

```bash
conda activate mmt-mmm
python -m src.data.generator
```

Writes:

- `data/raw/synthetic_ad_spend.csv` — 728 days × 4 channels (`meta`, `google`, `tiktok`, `tv`)
- `data/raw/ground_truth.json` — planted adstock / Hill / media-scale parameters
- See [`data/raw/DATA_CARD.md`](data/raw/DATA_CARD.md) for long-format semantics, grain, and KPI notes

Columns: `date`, `channel`, `spend` (float USD), `impressions` / `clicks` / `baseline_sales` (non-negative integers).  
`baseline_sales` is the site-wide daily unit KPI **repeated** on each channel row — do not sum across channels.

Committed CSV is locked to `seed=42` after integer post-processing.

```bash
python -m pytest tests/test_generator.py -q
```

## STORY-102 / transforms (done)

**geometric + Weibull adstock + Hill saturation** live in
`src/models/transformations.py`. Path-C DGP imports those helpers (single source of
truth). Validation DoD uses a Plotly Express script — **not** a Jupyter notebook.

**Speed gate:** `tests/test_transformations_perf.py` asserts wall time
&lt; 1s for `geometric_adstock` + `weibull_adstock` + `hill_saturation` on ~730
days × 4 channels (`time.perf_counter`).

```bash
conda activate mmt-mmm
# after env create/update — plotly is in environment.yml (conda-forge)
conda env update -f environment.yml --prune

python -m pytest tests/test_transformations.py tests/test_transformations_perf.py -q
python scripts/plot_adstock_validation.py
# → reports/figures/geometric_adstock_pulse.html
# → reports/figures/weibull_adstock_pulse.html  (two shapes + geometric reference)
# → reports/figures/hill_saturation_curves.html  (K / S response curves)
```

## STORY-103 / ETL (done)

Raw channel-day CSV → aligned date×channel panel → impute → Pandera validate → Parquet.

```bash
conda activate mmt-mmm
conda env update -f environment.yml --prune   # pulls pandera + pyarrow

python -m src.data.etl
# → data/processed/clean_spend.parquet

python -m pytest tests/test_etl.py -q
```

**Fill rules:** missing media after alignment → **0** (pause / not in export); missing `baseline_sales` → **forward-fill**. Dirty practice export: `tests/fixtures/dirty_ad_spend.csv`. See [`data/raw/DATA_CARD.md`](data/raw/DATA_CARD.md).

## STORY-104 / media QA (done)

After ETL, check that impressions/clicks look believable vs each channel’s recent history. Repair when history exists; **hard-fail** (exit ≠ 0) if anomalies remain unrepaired so Meridian never trains on bad media. Never mutates `spend` or `baseline_sales`.

```bash
conda activate mmt-mmm
python -m src.data.etl          # refresh clean_spend.parquet if needed
python -m src.data.qa           # overwrite clean_spend.parquet; exit 0 or ≠ 0
python -m pytest tests/test_qa.py -q
```

**Artifacts:** overwrite `data/processed/clean_spend.parquet`; optional audit `data/processed/qa_repair_log.csv` (only when repairs ran). Anomaly fixture: `tests/fixtures/anomalous_spend.csv`.

## STORY-201 / Meridian spike (done)

National Google Meridian fit on post-QA `clean_spend.parquet` (weekly grain by default).
Learnings + **open rank-recovery issue**: [`docs/learnings/story-201-meridian.md`](docs/learnings/story-201-meridian.md).

```bash
conda activate mmt-mmm
conda env update -f environment.yml --prune   # pins google-meridian==2.1.0 via pip
python -c "import pymc, meridian; print(pymc.__version__, meridian.__version__)"

python -m src.data.etl
python -m src.data.qa

# Fast adapter / spike-helper tests (no MCMC)
python -m pytest tests/test_meridian_data.py tests/test_model_spike_helpers.py -q

# Smoke: short chains + R-hat peek (warns SMOKE_RHAT_WARN; exit 0 unless --fail-on-rhat)
python scripts/02_model_spike.py --mode smoke

# Fuller DoD (CPU; can take a long time): R-hat < 1.05 gate + artifacts
python scripts/02_model_spike.py --mode full
# → reports/metrics.json  (includes recovery_spearman + dod.directional_recovery; not a hard fail)
# → reports/figures/posterior_predictive.png
# → reports/parameter_recovery.md
```

Adapter: `src/models/meridian_data.py` (KPI=`baseline_sales`, media=`impressions`, spend=`spend`). Weekly KPI is **sum of daily units** (flow aggregation). Override MCMC sizes with `--n-chains` / `--n-adapt` / `--n-burnin` / `--n-keep`. Daily grain: `--freq D` (much slower).

**Open issue:** Meridian iROAS rank (meta&gt;tiktok&gt;tv&gt;google) disagrees with Path-C (tv&gt;google&gt;meta&gt;tiktok); Spearman ≈ −0.6. Status-only for this spike — see the learning doc.

## STORY-301 / budget allocator

Constrained budget optimizer on offline response curves (`scipy.optimize` SLSQP).
Reads Meridian `reports/metrics.json` `response_curves.means` (or a synthetic fixture).
**Caveat:** allocator trusts those curves even though Meridian channel-rank recovery vs Path-C is still open ([`docs/learnings/story-201-meridian.md`](docs/learnings/story-201-meridian.md)) — do not treat allocations as Path-C ground truth.

On failure (`solver.success=false` — infeasible bounds/target or post-solve check), `channels` is an empty object `{}` so callers do not read a partial plan.

```bash
conda activate mmt-mmm

# Maximize incremental KPI under a fixed budget (+ bounds)
python scripts/03_allocate_budget.py \
  --curves tests/fixtures/synthetic_response_curves.json \
  --budget 60 --min-spend 5 --max-spend 30

# Or hit a KPI target with minimum total spend
python scripts/03_allocate_budget.py \
  --curves tests/fixtures/synthetic_response_curves.json \
  --target-kpi 20 --min-spend 0

# Meridian metrics → reports/allocation.json
python scripts/03_allocate_budget.py \
  --curves reports/metrics.json \
  --budget 100000 --min-spend 0 \
  --out reports/allocation.json

# Teaching plots (Plotly Express HTML)
python scripts/plot_allocation_teaching.py
# → reports/figures/story_301_response_curves.html
# → reports/figures/story_301_allocation_vs_baseline.html

python -m pytest tests/test_curves.py tests/test_allocator.py -q
```

Modules: `src/optimize/curves.py`, `src/optimize/allocator.py`. CLI: `scripts/03_allocate_budget.py`.

## STORY-302 / C-suite brief (step 0–3)

Teaching figures for budget shift, saturation, and KPI lift. The recommended mix is fixed (alpha 27, beta 18, gamma 15) because equal-room on this fixture is 20/20/20 and SLSQP does not leave that point.

Offline rendering stays `--offline`. Without that flag the CLI calls Anthropic with a forced `emit_brief` tool, then rejects the brief if the numbers drift from the fact pack. Default model id: `claude-sonnet-4-5` (`--model` overrides it).

Key load order: environment variable `ANTHROPIC_API_KEY`, else one line in gitignored `Secret/anthropic_api_key`. The CLI never prints the key.

```bash
conda activate mmt-mmm
python scripts/plot_story_302_concepts.py
# → reports/figures/story_302_budget_shifts.html
# → reports/figures/story_302_saturation.html
# → reports/figures/story_302_kpi_lift.html

python scripts/04_csuite_brief.py \
  --allocation tests/fixtures/story_302_allocation.json --offline

python scripts/04_csuite_brief.py \
  --allocation tests/fixtures/story_302_allocation.json
# live; writes reports/csuite_brief.json only after the number lock passes

python -m pytest tests/test_csuite_facts.py tests/test_csuite_brief.py -q
```

Modules: `src/report/facts.py`, `src/report/schema.py`, `src/report/brief.py`. Fixture plan: `tests/fixtures/story_302_allocation.json`.

## Stack direction

Python Bayesian MMM (`google-meridian` + scientific stack in `environment.yml`). Docker is deferred; local work uses the conda env only.
