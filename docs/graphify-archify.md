# graphify + archify artifacts

Generated knowledge graph and architecture diagram for the MMT&MMM Path-C slice after **STORY-101** (generator), **STORY-102** (shared transforms + Plotly validation), **STORY-103** (Pandera ETL → Parquet), and **STORY-104** (media QA detect/repair + hard-fail gate).

Working branch for this refresh: `cursor/story-104-qa-702b` (merges into `sprint-1-core-data-engine`).

## graphify

Scoped via [`.graphifyignore`](../.graphifyignore) (excludes bulky `.cursor/skills/archify` package so the graph reflects the MMM POC).

| Artifact | Path |
| --- | --- |
| Interactive HTML | [`graphify-out/graph.html`](../graphify-out/graph.html) |
| Audit report | [`graphify-out/GRAPH_REPORT.md`](../graphify-out/GRAPH_REPORT.md) |
| Graph JSON | [`graphify-out/graph.json`](../graphify-out/graph.json) |
| Token benchmark | [`graphify-out/benchmark.txt`](../graphify-out/benchmark.txt) |

Regenerated after STORY-104 (includes `src/data/qa.py` → `detect_anomalies` / `repair_panel` / `run_qa` hard-fail + audit log, plus ETL → generator → `transformations` → Plotly / pytest). Re-run `graphify update .` after code changes.

## archify

Repository-backed architecture of STORY-101 → 104: Path-C generator writes raw CSV; shared transforms feed DGP + Plotly; **ETL** loads/aligns/imputes/validates into `clean_spend.parquet`; **QA** detects/repairs media anomalies (or hard-fails), overwrites the same Parquet, and optionally writes `qa_repair_log.csv`; Meridian/PyMC remains external/future and consumes the **QA'd** Parquet.

| Artifact | Path |
| --- | --- |
| HTML diagram | [`.archify/architecture-mmt-story101-104-20261009-151448/mmt-story101-104.html`](../.archify/architecture-mmt-story101-104-20261009-151448/mmt-story101-104.html) |
| Candidate JSON | [`.archify/architecture-mmt-story101-104-20261009-151448/candidate.json`](../.archify/architecture-mmt-story101-104-20261009-151448/candidate.json) |

Pinned revision for evidence: `61ef445b53c95d129f0f748f6cd787d2af62be1e` (STORY-104 QA code tip at run time).

**Wording style:** plain-language node/edge labels for non-experts (e.g. “Check media looks normal”, “Fill every day”, “Stop if still broken”) plus one teaching subtitle — not function names or jargon.

Prior runs kept for history:

- STORY-101→103: [`.archify/architecture-mmt-story101-103-20261008-165012/`](../.archify/architecture-mmt-story101-103-20261008-165012/)
- STORY-101+102: [`.archify/architecture-mmt-story101-102-20261008-153042/`](../.archify/architecture-mmt-story101-102-20261008-153042/)
- STORY-101-only: [`.archify/architecture-mmt-story101-20261008-161209/`](../.archify/architecture-mmt-story101-20261008-161209/)
