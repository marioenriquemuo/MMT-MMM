# graphify + archify artifacts

Generated knowledge graph and architecture diagram for the MMT&MMM Path-C slice after **STORY-101** (generator), **STORY-102** (shared transforms + Plotly validation), **STORY-103** (Pandera ETL → Parquet), **STORY-104** (media QA detect/repair + hard-fail gate), **STORY-201** (Meridian national weekly spike), **STORY-301** (offline response curves → SLSQP budget allocator), and **STORY-302** (allocation JSON → fact pack → C-suite brief).

Working branch for this refresh: `cursor/story-302-csuite-brief-702b` (merges into `sprint-2-mvp-optimization-agentic-ui`).

Spike learnings (incl. **open rank-recovery issue** that still applies to allocator inputs): [`docs/learnings/story-201-meridian.md`](learnings/story-201-meridian.md).

## graphify

Scoped via [`.graphifyignore`](../.graphifyignore) (excludes bulky `.cursor/skills/archify` package so the graph reflects the MMM POC).

| Artifact | Path |
| --- | --- |
| Interactive HTML | [`graphify-out/graph.html`](../graphify-out/graph.html) |
| Audit report | [`graphify-out/GRAPH_REPORT.md`](../graphify-out/GRAPH_REPORT.md) |
| Graph JSON | [`graphify-out/graph.json`](../graphify-out/graph.json) |
| Token benchmark | [`graphify-out/benchmark.txt`](../graphify-out/benchmark.txt) |

Regenerated after STORY-302 (`graphify update .`; includes `src/report/` + `scripts/04_csuite_brief.py`, plus the STORY-301 allocator path). Re-run `graphify update .` after code changes.

## archify

**Current:** repository-backed picture of the MVP that exists in this repo — practice spend → line up weeks → check the media → clean weekly file → Meridian → response curves → budget rules → search spends → spend plan (or empty channels) → fact pack → prompt → Claude `emit_brief` → number lock → printed brief, or reject. No product UI.

| Artifact | Path |
| --- | --- |
| HTML diagram | [`.archify/architecture-mmt-mvp-20261013-164444/mmt-mvp.html`](../.archify/architecture-mmt-mvp-20261013-164444/mmt-mvp.html) |
| Candidate JSON | [`.archify/architecture-mmt-mvp-20261013-164444/candidate.json`](../.archify/architecture-mmt-mvp-20261013-164444/candidate.json) |

Pinned revision for evidence: `3dffd009a6bf344822e0d2cdf7f61687a4ed45b2` (sprint-2 tip after the STORY-302 merge).

**Wording style:** plain-language labels (e.g. “Check the media”, “Empty channels”, “Number lock”). A card says the figures are incremental KPI, not revenue, and that Meridian channel rank vs Path-C is still open.

Prior runs kept for history:

- STORY-302 brief only: [`.archify/workflow-mmt-story302-20261013-161023/`](../.archify/workflow-mmt-story302-20261013-161023/)
- STORY-301: [`.archify/architecture-mmt-story301-20261012-120314/`](../.archify/architecture-mmt-story301-20261012-120314/)
- STORY-101→201: [`.archify/architecture-mmt-story101-201-20261009-171324/`](../.archify/architecture-mmt-story101-201-20261009-171324/)
- STORY-101→104: [`.archify/architecture-mmt-story101-104-20261009-151448/`](../.archify/architecture-mmt-story101-104-20261009-151448/)
- STORY-101→103: [`.archify/architecture-mmt-story101-103-20261008-165012/`](../.archify/architecture-mmt-story101-103-20261008-165012/)
- STORY-101+102: [`.archify/architecture-mmt-story101-102-20261008-153042/`](../.archify/architecture-mmt-story101-102-20261008-153042/)
- STORY-101-only: [`.archify/architecture-mmt-story101-20261008-161209/`](../.archify/architecture-mmt-story101-20261008-161209/)
