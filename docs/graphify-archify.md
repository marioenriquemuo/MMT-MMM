# graphify + archify artifacts

Generated knowledge graph and architecture diagram for the MMT&MMM Path-C slice after **STORY-101** (generator), **STORY-102** (shared transforms + Plotly validation), and **STORY-103** (Pandera ETL → Parquet).

Working branch for this refresh: `cursor/story-103-etl-4e92` (PR into `sprint-1-core-data-engine`).

## graphify

Scoped via [`.graphifyignore`](../.graphifyignore) (excludes bulky `.cursor/skills/archify` package so the graph reflects the MMM POC).

| Artifact | Path |
| --- | --- |
| Interactive HTML | [`graphify-out/graph.html`](../graphify-out/graph.html) |
| Audit report | [`graphify-out/GRAPH_REPORT.md`](../graphify-out/GRAPH_REPORT.md) |
| Graph JSON | [`graphify-out/graph.json`](../graphify-out/graph.json) |
| Token benchmark | [`graphify-out/benchmark.txt`](../graphify-out/benchmark.txt) |

Regenerated after STORY-103 (includes `src/data/etl.py` → `run_etl` / align / impute / Pandera / Parquet, plus generator → `transformations` → Plotly / pytest). Re-run `graphify update .` after code changes.

## archify

Repository-backed architecture of STORY-101 → 103: Path-C generator writes raw CSV; shared transforms feed DGP + Plotly; **ETL** loads/aligns/imputes/validates into `clean_spend.parquet`; Meridian/PyMC remains external/future and consumes the clean Parquet (not raw holes).

| Artifact | Path |
| --- | --- |
| HTML diagram | [`.archify/architecture-mmt-story101-103-20261008-165012/mmt-story101-103.html`](../.archify/architecture-mmt-story101-103-20261008-165012/mmt-story101-103.html) |
| Candidate JSON | [`.archify/architecture-mmt-story101-103-20261008-165012/candidate.json`](../.archify/architecture-mmt-story101-103-20261008-165012/candidate.json) |

Pinned revision for evidence: `65b3d419e969dc8374795c5796a433454f536638` (STORY-103 ETL tip at run time).

Prior runs kept for history:

- STORY-101+102: [`.archify/architecture-mmt-story101-102-20261008-153042/`](../.archify/architecture-mmt-story101-102-20261008-153042/)
- STORY-101-only: [`.archify/architecture-mmt-story101-20261008-161209/`](../.archify/architecture-mmt-story101-20261008-161209/)
