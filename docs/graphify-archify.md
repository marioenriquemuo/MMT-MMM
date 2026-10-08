# graphify + archify artifacts

Generated knowledge graph and architecture diagram for the MMT&MMM Path-C slice after **STORY-101** (generator) and **STORY-102** (shared transforms + Plotly validation).

Working branch: `sprint-1-core-data-engine`.

## graphify

Scoped via [`.graphifyignore`](../.graphifyignore) (excludes bulky `.cursor/skills/archify` package so the graph reflects the MMM POC).

| Artifact | Path |
| --- | --- |
| Interactive HTML | [`graphify-out/graph.html`](../graphify-out/graph.html) |
| Audit report | [`graphify-out/GRAPH_REPORT.md`](../graphify-out/GRAPH_REPORT.md) |
| Graph JSON | [`graphify-out/graph.json`](../graphify-out/graph.json) |
| Token benchmark | [`graphify-out/benchmark.txt`](../graphify-out/benchmark.txt) |

Regenerated at pre–STORY-103 checkpoint (includes generator → `transformations` → Plotly figures / pytest). Re-run `graphify update .` after code changes.

## archify

Repository-backed architecture of STORY-101 + STORY-102: Path-C generator imports shared transforms; Plotly Express validation script (not Jupyter); unit + `<1s` perf tests; Meridian/PyMC noted as external/future.

| Artifact | Path |
| --- | --- |
| HTML diagram | [`.archify/architecture-mmt-story101-102-20261008-153042/mmt-story101-102.html`](../.archify/architecture-mmt-story101-102-20261008-153042/mmt-story101-102.html) |
| Candidate JSON | [`.archify/architecture-mmt-story101-102-20261008-153042/candidate.json`](../.archify/architecture-mmt-story101-102-20261008-153042/candidate.json) |

Pinned revision for evidence: `9a58cd0d69eca73753d235839dacee6c9ca01bbc` (STORY-102 tip at run time).

Prior STORY-101-only run kept for history: [`.archify/architecture-mmt-story101-20261008-161209/`](../.archify/architecture-mmt-story101-20261008-161209/).
