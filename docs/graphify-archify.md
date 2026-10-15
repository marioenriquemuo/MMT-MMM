# graphify + archify artifacts

Generated knowledge graph and the current project architecture diagram: Path-C panel → ETL spend panel and date-level exogenous controls → QA → Meridian (controls not in the fit yet) → response curves → SLSQP allocator → fact pack / number lock → offline or Claude brief and Streamlit dashboard.

Working branch for this refresh: `cursor/story-501-exogenous-etl-702b`.

Spike learnings (incl. **open rank-recovery issue** that still applies to allocator inputs): [`docs/learnings/story-201-meridian.md`](learnings/story-201-meridian.md).

## graphify

Scoped via [`.graphifyignore`](../.graphifyignore) (excludes bulky `.cursor/skills/archify` package so the graph reflects the MMM POC).

| Artifact | Path |
| --- | --- |
| Interactive HTML | [`graphify-out/graph.html`](../graphify-out/graph.html) |
| Audit report | [`graphify-out/GRAPH_REPORT.md`](../graphify-out/GRAPH_REPORT.md) |
| Graph JSON | [`graphify-out/graph.json`](../graphify-out/graph.json) |
| Token benchmark | [`graphify-out/benchmark.txt`](../graphify-out/benchmark.txt) |

Regenerated after STORY-501 (`graphify update .`). Re-run `graphify update .` after code changes.

## archify

**Current:** [`.archify/architecture-mmt-project/architecture-mmt-project.html`](../.archify/architecture-mmt-project/architecture-mmt-project.html). Path-C panel → ETL (`clean_spend.parquet` and date-level `exogenous_controls.parquet`) → media QA → Meridian national weekly fit on the spend panel only → response curves → SLSQP allocator → fact pack and number lock → offline or Claude brief, and the Streamlit dashboard. Controls are not in the Meridian fit.

| Artifact | Path |
| --- | --- |
| HTML diagram | [`.archify/architecture-mmt-project/architecture-mmt-project.html`](../.archify/architecture-mmt-project/architecture-mmt-project.html) |
| Candidate JSON | [`.archify/architecture-mmt-project/candidate.json`](../.archify/architecture-mmt-project/candidate.json) |

Pinned revision for evidence: `0753a7e2bbfc215581bc147e22222f340ca42947` (STORY-501 controls code the diagram cites).

Prior runs kept for history:

- Sprint 2 MVP picture: [`.archify/architecture-mmt-mvp-20261013-164444/`](../.archify/architecture-mmt-mvp-20261013-164444/)
- STORY-302 brief only: [`.archify/workflow-mmt-story302-20261013-161023/`](../.archify/workflow-mmt-story302-20261013-161023/)
- STORY-301: [`.archify/architecture-mmt-story301-20261012-120314/`](../.archify/architecture-mmt-story301-20261012-120314/)
- STORY-101→201: [`.archify/architecture-mmt-story101-201-20261009-171324/`](../.archify/architecture-mmt-story101-201-20261009-171324/)
- STORY-101→104: [`.archify/architecture-mmt-story101-104-20261009-151448/`](../.archify/architecture-mmt-story101-104-20261009-151448/)
- STORY-101→103: [`.archify/architecture-mmt-story101-103-20261008-165012/`](../.archify/architecture-mmt-story101-103-20261008-165012/)
- STORY-101+102: [`.archify/architecture-mmt-story101-102-20261008-153042/`](../.archify/architecture-mmt-story101-102-20261008-153042/)
- STORY-101-only: [`.archify/architecture-mmt-story101-20261008-161209/`](../.archify/architecture-mmt-story101-20261008-161209/)
