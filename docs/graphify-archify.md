# graphify + archify artifacts

Generated knowledge graph and architecture diagram for the MMT&MMM Path-C slice after **STORY-101** (generator), **STORY-102** (shared transforms + Plotly validation), **STORY-103** (Pandera ETL → Parquet), **STORY-104** (media QA detect/repair + hard-fail gate), and **STORY-201** (Meridian national weekly spike).

Working branch for this refresh: `cursor/story-201-meridian-702b` (merges into `sprint-1-core-data-engine`).

Spike learnings (incl. **open rank-recovery issue**): [`docs/learnings/story-201-meridian.md`](learnings/story-201-meridian.md).

## graphify

Scoped via [`.graphifyignore`](../.graphifyignore) (excludes bulky `.cursor/skills/archify` package so the graph reflects the MMM POC).

| Artifact | Path |
| --- | --- |
| Interactive HTML | [`graphify-out/graph.html`](../graphify-out/graph.html) |
| Audit report | [`graphify-out/GRAPH_REPORT.md`](../graphify-out/GRAPH_REPORT.md) |
| Graph JSON | [`graphify-out/graph.json`](../graphify-out/graph.json) |
| Token benchmark | [`graphify-out/benchmark.txt`](../graphify-out/benchmark.txt) |

Regenerated after STORY-201 (includes `src/models/meridian_data.py` + `scripts/02_model_spike.py` → adapter / smoke+full MCMC / R-hat gate / reports, plus QA → ETL → generator → `transformations` → Plotly / pytest). Re-run `graphify update .` after code changes.

## archify

Repository-backed architecture of STORY-101 → 201: Path-C generator writes raw CSV; shared transforms feed DGP + Plotly; **ETL** loads/aligns/imputes/validates into `clean_spend.parquet`; **QA** detects/repairs media anomalies (or hard-fails) and overwrites the same Parquet; **Meridian** shapes national weeks, fits smoke then fuller chains, gates on R-hat, and writes metrics / PPC / recovery note.

| Artifact | Path |
| --- | --- |
| HTML diagram | [`.archify/architecture-mmt-story101-201-20261009-171324/mmt-story101-201.html`](../.archify/architecture-mmt-story101-201-20261009-171324/mmt-story101-201.html) |
| Candidate JSON | [`.archify/architecture-mmt-story101-201-20261009-171324/candidate.json`](../.archify/architecture-mmt-story101-201-20261009-171324/candidate.json) |

Pinned revision for evidence: `9cb46b586201926fb6e8c2da9f448fb6e0c72b3c` (STORY-201 Meridian code tip at run time).

**Wording style:** plain-language node/edge labels for non-experts (e.g. “Shape for Meridian”, “Chains agree?”, “Stop if still broken”) plus one teaching subtitle — not function names or jargon. Open rank-recovery finding called out on a card.

Prior runs kept for history:

- STORY-101→104: [`.archify/architecture-mmt-story101-104-20261009-151448/`](../.archify/architecture-mmt-story101-104-20261009-151448/)
- STORY-101→103: [`.archify/architecture-mmt-story101-103-20261008-165012/`](../.archify/architecture-mmt-story101-103-20261008-165012/)
- STORY-101+102: [`.archify/architecture-mmt-story101-102-20261008-153042/`](../.archify/architecture-mmt-story101-102-20261008-153042/)
- STORY-101-only: [`.archify/architecture-mmt-story101-20261008-161209/`](../.archify/architecture-mmt-story101-20261008-161209/)
