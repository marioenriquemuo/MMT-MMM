# Graph Report - MMT&MMM  (2026-10-08)

## Corpus Check
- 36 files · ~21,445 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: .mdc 5, (none) 5, .csv 1)

## Summary
- 228 nodes · 347 edges · 19 communities (14 shown, 5 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d502f79d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- generate
- MMT&MMM Project Conventions
- Ponytail Help
- What You Must Do When Invoked
- test_transformations.py
- DATA_CARD for synthetic_ad_spend.csv
- plot_adstock_validation.py
- data/__init__.py
- src/__init__.py
- hill_saturation
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native AGENTS.md integration
- graphify reference: incremental update and cluster-only
- graphify + archify artifacts
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- extraction-spec.md

## God Nodes (most connected - your core abstractions)
1. `generate()` - 21 edges
2. `geometric_adstock()` - 20 edges
3. `weibull_adstock()` - 20 edges
4. `hill_saturation()` - 18 edges
5. `What You Must Do When Invoked` - 12 edges
6. `/graphify` - 10 edges
7. `graphify reference: extra exports and benchmark` - 8 edges
8. `_baseline_sales()` - 7 edges
9. `assert_valid()` - 7 edges
10. `write_outputs()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `No Look-Ahead / Leakage Rule` --semantically_similar_to--> `baseline_sales KPI`  [INFERRED] [semantically similar]
  AGENTS.md → data/raw/DATA_CARD.md
- `Agentic Explain Layer` --conceptually_related_to--> `Agent Golden Rules`  [INFERRED]
  CLAUDE.md → AGENTS.md
- `build_geometric_figure()` --calls--> `geometric_adstock()`  [EXTRACTED]
  scripts/plot_adstock_validation.py → src/models/transformations.py
- `build_weibull_figure()` --calls--> `geometric_adstock()`  [EXTRACTED]
  scripts/plot_adstock_validation.py → src/models/transformations.py
- `build_weibull_figure()` --calls--> `weibull_adstock()`  [EXTRACTED]
  scripts/plot_adstock_validation.py → src/models/transformations.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Bayesian MMM Measurement Stack** — claude_top_down_bayesian_mmm, claude_bottom_up_calibration, claude_allocator_layer, claude_agentic_explain_layer [EXTRACTED 1.00]
- **Ponytail Skill Suite** — _cursor_skills_ponytail_skill_ponytail, _cursor_skills_ponytail_review_skill_ponytail_review, _cursor_skills_ponytail_audit_skill_ponytail_audit, _cursor_skills_ponytail_debt_skill_ponytail_debt, _cursor_skills_ponytail_gain_skill_ponytail_gain, _cursor_skills_ponytail_help_skill_ponytail_help [EXTRACTED 1.00]
- **Secret Hygiene Across Project Docs** — _cursor_skills_secret_hygiene_skill_secret_hygiene, _cursor_skills_mmt_mmm_skill_secret_folder, agents_golden_rules [INFERRED 0.85]

## Communities (19 total, 5 thin omitted)

### Community 0 - "generate"
Cohesion: 0.10
Nodes (37): Any, json, pandas, pathlib, skipif, assert_valid(), _baseline_sales(), coerce_integer_columns() (+29 more)

### Community 1 - "MMT&MMM Project Conventions"
Cohesion: 0.14
Nodes (22): ELI5 Teacher, Four-Phase Teaching Structure, archify Skill, MMT&MMM Project Conventions, Secret/ Local-Only Path, Secret Hygiene, Agent Skills SKILL.md Format, Skill Author (+14 more)

### Community 2 - "Ponytail Help"
Cohesion: 0.27
Nodes (12): Ponytail Audit, ponytail: Comment Marker, Ponytail Debt, Ponytail Benchmark Medians, Ponytail Gain, Ponytail Intensity Levels (lite/full/ultra), Ponytail Help, Over-Engineering Review Tags (+4 more)

### Community 4 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native AGENTS.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 5 - "test_transformations.py"
Cohesion: 0.09
Nodes (38): fixture, pytest, geometric_adstock(), ndarray, Apply two-parameter Weibull adstock along ``axis``. Builds discrete Weibull…, Apply one-parameter geometric adstock along ``axis``. Recurrence (carryover of…, Discrete Weibull PDF-style weights on lags ``0 .. L-1``. Evaluated at positive…, weibull_adstock() (+30 more)

### Community 6 - "DATA_CARD for synthetic_ad_spend.csv"
Cohesion: 0.47
Nodes (6): No Look-Ahead / Leakage Rule, baseline_sales KPI, Channel-Day Grain, DATA_CARD for synthetic_ad_spend.csv, STORY-101 Path-C Synthetic Generator, synthetic_ad_spend.csv

### Community 7 - "plot_adstock_validation.py"
Cohesion: 0.20
Nodes (13): plotly_express, build_geometric_figure(), build_hill_figure(), build_weibull_figure(), main(), _pulse_frame(), DataFrame, ndarray (+5 more)

### Community 10 - "hill_saturation"
Cohesion: 0.09
Nodes (25): numpy, Shared modeling primitives (transforms, later likelihoods / inference)., hill_saturation(), STORY-102 media transforms (Steps 2–5: adstock + Hill saturation). Pure NumPy…, Hill / Michaelis–Menten saturation mapped to ``[0, 1)``. Form:: y = x^S / (K^S…, Choose discrete lag support ``L`` for Weibull PDF weights. Default:…, _weibull_n_lags(), _panel() (+17 more)

### Community 12 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 13 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 15 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 16 - "graphify reference: commit hook and native AGENTS.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native AGENTS.md integration, graphify reference: commit hook and native AGENTS.md integration

### Community 17 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 18 - "graphify + archify artifacts"
Cohesion: 0.50
Nodes (3): archify, graphify, graphify + archify artifacts

## Knowledge Gaps
- **46 isolated node(s):** `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)`, `Step 1 - Ensure graphify is installed`, `Step 2 - Detect files` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 102 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `geometric_adstock()` connect `test_transformations.py` to `generate`, `hill_saturation`, `plot_adstock_validation.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `hill_saturation()` connect `hill_saturation` to `generate`, `test_transformations.py`, `plot_adstock_validation.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `weibull_adstock()` connect `test_transformations.py` to `hill_saturation`, `plot_adstock_validation.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **What connects `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `generate` be split into smaller, more focused modules?**
  _Cohesion score 0.09851551956815115 - nodes in this community are weakly interconnected._
- **Should `MMT&MMM Project Conventions` be split into smaller, more focused modules?**
  _Cohesion score 0.13852813852813853 - nodes in this community are weakly interconnected._
- **Should `What You Must Do When Invoked` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._