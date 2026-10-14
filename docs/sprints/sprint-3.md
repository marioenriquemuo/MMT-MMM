# Sprint 3 — Exogenous Controls, Multi-Tenant Architecture & MMT Calibration

| Item | Value |
| --- | --- |
| Working branch | `sprint-3-exogenous-multitenant-mmt` |
| Goal | Upgrade the data ingestion pipeline to handle organic traffic, holidays, quincenas, and inventory gaps, establish multi-tenant client isolation, and integrate MMT geo-experiment calibration anchors. |
| Builds on | Sprint 1–2 MVP on `main` / `sprint-2-mvp-optimization-agentic-ui` (tag `sprint-2-mvp`) |
| Duration (local sprint file) | 1 week (Days 15–21) |
| Story points (local sprint file) | 18 |
| Source of story IDs | Local sprint file under `Secret/` (gitignored) — titles/DoD summarized here; never commit that file |

## How this builds on Sprint 1–2

Sprint 1–2 delivered a single-tenant measurement → allocation → explain path:

1. **Path-C synthetic DGP** + shared adstock/saturation transforms → ETL/QA → `clean_spend.parquet`
2. **Meridian national weekly** MMM spike (`scripts/02_model_spike.py`) → response curves
3. **SLSQP allocator** (`src/optimize/`) → `reports/allocation.json`
4. **Fact pack + Claude brief** (`src/report/`, `scripts/04_csuite_brief.py`)
5. **Streamlit dashboard** (`app/streamlit_app.py`) with bounds + offline/live insights

Sprint 3 hardens that stack for enterprise use: control for non-media confounders, isolate clients, and anchor posteriors with real MMT experiments — without inventing a new allocator/UI MVP.

## Workstreams

### 1. Exogenous Controls

**Plain language:** Media alone is not the whole world. Holidays, paydays, organic search, promos, price, and stockouts move the KPI. If the MMM ignores them, paid channels get credit (or blame) they do not deserve.

**Technical intent:** Extend the ingestion / alignment layer so non-media regressors land on the same time index as spend and conversions, then condition the measurement model on those controls.

**Today:** Path-C + ETL/QA produce a media×date panel for one synthetic brand; Meridian spike is national weekly media + KPI. No first-class holiday/organic/inventory control matrices in the shipped pipeline.

**Architecture “done” (likely):** Aux inputs aligned without null holes; control columns available as regression conditioning for Meridian (or the agreed Bayesian stack); tests prove date alignment with spend/KPI. Detailed DoD lives with STORY-501 below.

### 2. Multi-Tenant Architecture

**Plain language:** One codebase, many clients — without mixing their data, configs, or model runs.

**Technical intent:** Partition raw/processed data, model artifacts, and reports by `client_id`; scripts take an explicit tenant flag; config maps currency, channels, and geography per client.

**Today:** Single-tenant assumptions — flat `data/raw/`, `data/processed/`, `reports/`; no `config/clients.yaml`; CLIs do not require `--client_id`.

**Architecture “done” (likely):** `data/clients/{client_id}/…` (or equivalent) isolation; client config map; cross-tenant load tests fail closed. Detailed DoD lives with STORY-502 below.

### 3. MMT Calibration

**Plain language:** Top-down MMM should be checked against bottom-up truth — geo lift tests / MMT — so platform attribution windows do not quietly warp channel strength.

**Technical intent:** Ingest structured experiment lift bounds and use them as informative priors / anchors in Meridian; emit a before/after calibration delta report.

**Today:** Product goal is stated in `CLAUDE.md` / `AGENTS.md` (“bottom-up calibration”); no `src/models/calibration.py` yet. Open measurement risk: **GAP-201-RANK** (Meridian channel order vs Path-C, Spearman ≈ −0.6) — MMT priors may help close or reframe that gap, but Sprint 3 does not automatically close it without new evidence.

**Architecture “done” (likely):** Calibration module + Meridian config hooks + `reports/calibration_delta.json` (or successor path under tenant layout). Detailed DoD lives with STORY-503 below.

## Stories (from local sprint file)

Stories below are **not invented** — they come from the local Sprint 3 backlog file (gitignored). High-level titles and DoD only.

### STORY-501 — Exogenous Control Variables & Organic Traffic ETL Pipeline (5 pts)

- Expand ETL (`src/data/etl.py`) for non-paid controls: organic SEO / brand search / CRM volume, holidays, LATAM pay cycles (quincenas), price drops, inventory stockouts.
- **DoD (summary):** Aux CSV/API inputs processed; holiday/payday/OOS control vectors injected; unit tests prove alignment with spend/KPI time series (no null holes); clean exogenous matrices ready for regression conditioning.

### STORY-502 — Multi-Tenant Data & Model Isolation Directory Structure (5 pts)

- Secure isolation pattern (e.g. `data/clients/{client_id}/`) across industries.
- **DoD (summary):** Per-client raw/processed/weights/reports partitions; `config/clients.yaml` for currency/channels/geo; scripts accept `--client_id`; security test that Client A cannot read Client B paths.

### STORY-503 — MMT Geo-Experiment Prior Calibration Module (8 pts)

- Calibration script (`src/models/calibration.py`) ingests live MMT geo-experiment results as informative Bayesian priors.
- **DoD (summary):** Reads structured lift JSON (region×channel bounds); Meridian config anchors posteriors; pre/post report (e.g. `reports/calibration_delta.json`); regional drift constrained by experiment outcomes.

## Open gaps Sprint 3 may or may not touch

From [`docs/learnings/open-gaps.md`](../learnings/open-gaps.md):

| Gap | Status | Sprint 3 relevance |
| --- | --- | --- |
| **GAP-201-RANK** | `open` | May be addressed indirectly via STORY-503 MMT priors / recovery work — only close when new evidence shows rank agreement or an accepted definitional mismatch. |
| **GAP-402-LOOM** | `open` | Portfolio DoD; not required for Sprint 3 workstreams. |
| **GAP-402-DOCKERIGNORE** | `open` | Optional housekeeping; not required for Sprint 3 workstreams. |
| **GAP-COMM-KPI** | `open` | Standing communication caveat (incremental KPI ≠ revenue); keep visible in copy/UI. |
| GAP-402-RENAME / GAP-402-VISIBILITY | `closed` | No Sprint 3 action. |

## Remotes

Push Sprint 3 commits to both `origin` and `github` on `sprint-3-exogenous-multitenant-mmt`. Do not force-push. Do not delete tags (`sprint-2-mvp`, `sprint-1-milestone-1`, …).
