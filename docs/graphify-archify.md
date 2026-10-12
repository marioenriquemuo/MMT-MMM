# graphify + archify artifacts

Generated knowledge graph and architecture diagram for the MMT&MMM Path-C slice after **STORY-101** (generator), **STORY-102** (shared transforms + Plotly validation), **STORY-103** (Pandera ETL → Parquet), **STORY-104** (media QA detect/repair + hard-fail gate), **STORY-201** (Meridian national weekly spike), and **STORY-301** (offline response curves → SLSQP budget allocator).

Working branch for this refresh: `cursor/story-301-budget-opt-702b` (merges into `sprint-2-mvp-optimization-agentic-ui`).

Spike learnings (incl. **open rank-recovery issue** that still applies to allocator inputs): [`docs/learnings/story-201-meridian.md`](learnings/story-201-meridian.md).

## graphify

Scoped via [`.graphifyignore`](../.graphifyignore) (excludes bulky `.cursor/skills/archify` package so the graph reflects the MMM POC).

| Artifact | Path |
| --- | --- |
| Interactive HTML | [`graphify-out/graph.html`](../graphify-out/graph.html) |
| Audit report | [`graphify-out/GRAPH_REPORT.md`](../graphify-out/GRAPH_REPORT.md) |
| Graph JSON | [`graphify-out/graph.json`](../graphify-out/graph.json) |
| Token benchmark | [`graphify-out/benchmark.txt`](../graphify-out/benchmark.txt) |

Regenerated after STORY-301 (includes `src/optimize/` + `scripts/03_allocate_budget.py` + teaching plots / allocator tests, plus Meridian → QA → ETL → generator → `transformations`). Re-run `graphify update .` after code changes.

## archify

**Current:** repository-backed architecture of STORY-301 — load Meridian (or practice) response curves, pick a budget goal, stay in min/max bounds, solve, save `allocation.json` (or clear channels on fail), plus teaching charts.

| Artifact | Path |
| --- | --- |
| HTML diagram | [`.archify/architecture-mmt-story301-20261012-120314/mmt-story301.html`](../.archify/architecture-mmt-story301-20261012-120314/mmt-story301.html) |
| Candidate JSON | [`.archify/architecture-mmt-story301-20261012-120314/candidate.json`](../.archify/architecture-mmt-story301-20261012-120314/candidate.json) |

Pinned revision for evidence: `642366ee16de2226fa93b65db6937c5bdfeae07e` (STORY-301 tip with empty-`channels`-on-fail).

**Wording style:** plain-language node/edge labels for non-experts (e.g. “Load the curves”, “Fail → empty plan”, “Stay in bounds”) plus a teaching subtitle — not function names or jargon. Meridian≠Path-C caveat called out on a card.

Prior runs kept for history:

- STORY-101→201: [`.archify/architecture-mmt-story101-201-20261009-171324/`](../.archify/architecture-mmt-story101-201-20261009-171324/)
- STORY-101→104: [`.archify/architecture-mmt-story101-104-20261009-151448/`](../.archify/architecture-mmt-story101-104-20261009-151448/)
- STORY-101→103: [`.archify/architecture-mmt-story101-103-20261008-165012/`](../.archify/architecture-mmt-story101-103-20261008-165012/)
- STORY-101+102: [`.archify/architecture-mmt-story101-102-20261008-153042/`](../.archify/architecture-mmt-story101-102-20261008-153042/)
- STORY-101-only: [`.archify/architecture-mmt-story101-20261008-161209/`](../.archify/architecture-mmt-story101-20261008-161209/)
