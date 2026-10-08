# Graph Report - MMT&MMM  (2026-10-08)

## Corpus Check
- 40 files · ~21,874 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 301 nodes · 435 edges · 27 communities (17 shown, 10 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.85)
- Token cost: 4,200 input · 3,100 output

## Community Hubs (Navigation)
- Transforms + unit tests
- Graphify watch exports
- Path-C generator DGP
- STORY-101 data card
- Sprint branch + remotes
- Plotly validation figures
- Graphify pipeline steps
- Project skills conventions
- Ponytail skill suite
- Semantic extraction spec
- Transforms perf gate
- Graphify extra exports
- Graphify query path
- Graphify add watch
- Graphify commit hooks
- Graphify incremental update
- Graphify archify index
- Graphify GitHub merge
- Graphify transcription
- Extraction spec doc
- Data package init
- Src package root
- Secret hygiene path
- Pathlib Path

## God Nodes (most connected - your core abstractions)
1. `/graphify` - 33 edges
2. `generate()` - 21 edges
3. `geometric_adstock()` - 20 edges
4. `weibull_adstock()` - 20 edges
5. `hill_saturation()` - 18 edges
6. `What You Must Do When Invoked` - 12 edges
7. `Incremental Update (--update)` - 9 edges
8. `graphify reference: extra exports and benchmark` - 8 edges
9. `MMT&MMM Project Conventions` - 7 edges
10. `_baseline_sales()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `mmt-mmm` --semantically_similar_to--> `mmt-mmm conda env`  [INFERRED] [semantically similar]
  environment.yml → AGENTS.md
- `/graphify` --conceptually_related_to--> `archify`  [INFERRED]
  .cursor/skills/graphify/SKILL.md → AGENTS.md
- `geometric_adstock` --semantically_similar_to--> `weibull_adstock`  [INFERRED] [semantically similar]
  CLAUDE.md → README.md
- `test_baseline_sales_repeated_per_date()` --calls--> `generate()`  [EXTRACTED]
  tests/test_generator.py → src/data/generator.py
- `test_bounds_non_negative_no_nulls()` --calls--> `generate()`  [EXTRACTED]
  tests/test_generator.py → src/data/generator.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Ponytail Skill Suite** — _cursor_skills_ponytail_skill_ponytail, _cursor_skills_ponytail_review_skill_ponytail_review, _cursor_skills_ponytail_audit_skill_ponytail_audit, _cursor_skills_ponytail_debt_skill_ponytail_debt, _cursor_skills_ponytail_gain_skill_ponytail_gain, _cursor_skills_ponytail_help_skill_ponytail_help [EXTRACTED 1.00]
- **Secret Hygiene Across Project Docs** — _cursor_skills_secret_hygiene_skill_secret_hygiene, _cursor_skills_mmt_mmm_skill_secret_folder [INFERRED 0.85]
- **Sprint 1 Core Data Engine stories** — agents_sprint_1_core_data_engine, agents_story_101, agents_story_102, agents_story_103 [EXTRACTED 1.00]
- **Path-C generator imports shared transforms** — src_data_generator, src_models_transformations, claude_geometric_adstock, claude_hill_saturation, readme_weibull_adstock [EXTRACTED 1.00]
- **Dual remotes for sprint branch** — agents_origin_remote, agents_github_remote, agents_sprint_1_core_data_engine, claude_dual_remotes [EXTRACTED 1.00]
- **Core Extraction Pipeline** — _cursor_skills_graphify_skill_structural_ast_extraction, _cursor_skills_graphify_skill_semantic_extraction, _cursor_skills_graphify_skill_extraction_merge [EXTRACTED 1.00]
- **Optional Export Suite** — _cursor_skills_graphify_references_exports_wiki_export, _cursor_skills_graphify_references_exports_neo4j_export, _cursor_skills_graphify_references_exports_falkordb_export, _cursor_skills_graphify_references_exports_svg_export, _cursor_skills_graphify_references_exports_graphml_export, _cursor_skills_graphify_references_exports_mcp_graph_server [EXTRACTED 1.00]
- **Query Feedback Loop** — _cursor_skills_graphify_references_query_constrained_query_expansion, _cursor_skills_graphify_references_query_bfs_traversal, _cursor_skills_graphify_references_query_save_result_feedback, _cursor_skills_graphify_references_query_work_memory_reflect [EXTRACTED 1.00]

## Communities (27 total, 10 thin omitted)

### Community 0 - "Transforms + unit tests"
Cohesion: 0.07
Nodes (51): fixture, pytest, Shared modeling primitives (transforms, later likelihoods / inference)., geometric_adstock(), hill_saturation(), ndarray, Apply two-parameter Weibull adstock along ``axis``. Builds discrete Weibull…, Hill / Michaelis–Menten saturation mapped to ``[0, 1)``. Form:: y = x^S / (K^S… (+43 more)

### Community 1 - "Graphify watch exports"
Cohesion: 0.05
Nodes (46): Folder Watch Mode (--watch), needs_update Flag, URL Corpus Ingest (/graphify add), Watch Debounce, FalkorDB Export, GraphML Export (--graphml), MCP Graph Server, Neo4j Export (+38 more)

### Community 2 - "Path-C generator DGP"
Cohesion: 0.09
Nodes (38): Any, json, pandas, Path, pathlib, ground_truth.json, skipif, assert_valid() (+30 more)

### Community 3 - "STORY-101 data card"
Cohesion: 0.15
Nodes (18): archify, data/raw/, Path-C synthetic multi-channel DGP, STORY-101, geometric_adstock, hill_saturation, baseline_sales, Channel-day grain (+10 more)

### Community 4 - "Sprint branch + remotes"
Cohesion: 0.13
Nodes (17): github remote, martech-mmm-ai-allocator, mmt-mmm conda env, No leakage, origin remote, sprint-1-core-data-engine, STORY-103, Agentic explain layer (+9 more)

### Community 5 - "Plotly validation figures"
Cohesion: 0.16
Nodes (16): reports/figures/, STORY-102, Plotly Express over Jupyter for Sprint 1, plotly_express, build_geometric_figure(), build_hill_figure(), build_weibull_figure(), main() (+8 more)

### Community 6 - "Graphify pipeline steps"
Cohesion: 0.13
Nodes (15): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Step 1 - Ensure graphify is installed, Step 2.5 - Video and audio (only if video files detected), Step 2 - Detect files, Step 3 - Extract entities and relationships (+7 more)

### Community 7 - "Project skills conventions"
Cohesion: 0.20
Nodes (12): ELI5 Teacher, Four-Phase Teaching Structure, archify Skill, MMT&MMM Project Conventions, Secret/ Local-Only Path, Secret Hygiene, Agent Skills SKILL.md Format, Skill Author (+4 more)

### Community 8 - "Ponytail skill suite"
Cohesion: 0.27
Nodes (12): Ponytail Audit, ponytail: Comment Marker, Ponytail Debt, Ponytail Benchmark Medians, Ponytail Gain, Ponytail Intensity Levels (lite/full/ultra), Ponytail Help, Over-Engineering Review Tags (+4 more)

### Community 9 - "Semantic extraction spec"
Cohesion: 0.18
Nodes (11): Confidence Score Rubric, DEEP_MODE, Deterministic Node ID Format, Hyperedges, Semantic Extraction Spec, semantically_similar_to Relation, EXTRACTED/INFERRED/AMBIGUOUS Audit Trail, AST+Semantic Extraction Merge (Part C) (+3 more)

### Community 10 - "Transforms perf gate"
Cohesion: 0.27
Nodes (9): numpy, _panel(), ndarray, STORY-102 Step 6 — wall-time gate for transforms on ~2y daily data., Non-negative spend panel shaped ``(channels, days)``., DoD: geometric + Weibull + Hill on 730×4 panel finishes in <1s., _run_transforms(), test_transforms_two_years_daily_under_one_second() (+1 more)

### Community 11 - "Graphify extra exports"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 12 - "Graphify query path"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 13 - "Graphify add watch"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 14 - "Graphify commit hooks"
Cohesion: 0.50
Nodes (3): For git commit hook, For native AGENTS.md integration, graphify reference: commit hook and native AGENTS.md integration

### Community 15 - "Graphify incremental update"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 16 - "Graphify archify index"
Cohesion: 0.50
Nodes (3): archify, graphify, graphify + archify artifacts

## Knowledge Gaps
- **77 isolated node(s):** `Step 6b - Wiki (only if --wiki flag)`, `Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag)`, `Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag)`, `Step 7b - SVG export (only if --svg flag)`, `Step 7c - GraphML export (only if --graphml flag)` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 140 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `/graphify` connect `Graphify watch exports` to `Semantic extraction spec`, `STORY-101 data card`, `Graphify pipeline steps`?**
  _High betweenness centrality (0.298) - this node is a cross-community bridge._
- **Why does `STORY-101` connect `STORY-101 data card` to `Sprint branch + remotes`?**
  _High betweenness centrality (0.264) - this node is a cross-community bridge._
- **What connects `Step 6b - Wiki (only if --wiki flag)`, `Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag)`, `Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag)` to the rest of the system?**
  _77 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Transforms + unit tests` be split into smaller, more focused modules?**
  _Cohesion score 0.0660377358490566 - nodes in this community are weakly interconnected._
- **Should `Graphify watch exports` be split into smaller, more focused modules?**
  _Cohesion score 0.05365402405180388 - nodes in this community are weakly interconnected._
- **Should `Path-C generator DGP` be split into smaller, more focused modules?**
  _Cohesion score 0.09487179487179487 - nodes in this community are weakly interconnected._
- **Should `STORY-101 data card` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._