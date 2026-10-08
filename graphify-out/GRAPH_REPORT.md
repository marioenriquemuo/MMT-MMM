# Graph Report - MMT&MMM  (2026-10-08)

## Corpus Check
- 38 files · ~23,161 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 6, .mdc 5, .csv 2)

## Summary
- 331 nodes · 498 edges · 31 communities (21 shown, 10 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `65b3d419`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_transformations.py
- /graphify
- generator.py
- transformations.py
- sprint-1-core-data-engine
- plot_adstock_validation.py
- What You Must Do When Invoked
- MMT&MMM Project Conventions
- Ponytail Help
- Semantic Extraction Spec
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native AGENTS.md integration
- graphify reference: incremental update and cluster-only
- graphify + archify artifacts
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- extraction-spec.md
- data/__init__.py
- src/__init__.py
- Secret/
- test_etl.py
- Incremental Update (--update)
- Whisper Video/Audio Transcription
- save-result Feedback Loop
- graphify merge-graphs
- graphify-out artifacts

## God Nodes (most connected - your core abstractions)
1. `/graphify` - 33 edges
2. `generate()` - 21 edges
3. `geometric_adstock()` - 20 edges
4. `weibull_adstock()` - 20 edges
5. `hill_saturation()` - 18 edges
6. `run_etl()` - 12 edges
7. `What You Must Do When Invoked` - 12 edges
8. `load_raw()` - 9 edges
9. `Incremental Update (--update)` - 9 edges
10. `graphify reference: extra exports and benchmark` - 8 edges

## Surprising Connections (you probably didn't know these)
- `mmt-mmm` --semantically_similar_to--> `mmt-mmm conda env`  [INFERRED] [semantically similar]
  environment.yml → AGENTS.md
- `/graphify` --conceptually_related_to--> `archify`  [INFERRED]
  .cursor/skills/graphify/SKILL.md → AGENTS.md
- `geometric_adstock` --semantically_similar_to--> `weibull_adstock`  [INFERRED] [semantically similar]
  CLAUDE.md → README.md
- `graphify-out artifacts` --references--> `/graphify`  [EXTRACTED]
  docs/graphify-archify.md → .cursor/skills/graphify/SKILL.md
- `build_geometric_figure()` --calls--> `geometric_adstock()`  [EXTRACTED]
  scripts/plot_adstock_validation.py → src/models/transformations.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Dual remotes for sprint branch** — agents_origin_remote, agents_github_remote, agents_sprint_1_core_data_engine, claude_dual_remotes [EXTRACTED 1.00]
- **Path-C generator imports shared transforms** — src_data_generator, src_models_transformations, claude_geometric_adstock, claude_hill_saturation, readme_weibull_adstock [EXTRACTED 1.00]
- **Core Extraction Pipeline** — _cursor_skills_graphify_skill_structural_ast_extraction, _cursor_skills_graphify_skill_semantic_extraction, _cursor_skills_graphify_skill_extraction_merge [EXTRACTED 1.00]
- **Optional Export Suite** — _cursor_skills_graphify_references_exports_wiki_export, _cursor_skills_graphify_references_exports_neo4j_export, _cursor_skills_graphify_references_exports_falkordb_export, _cursor_skills_graphify_references_exports_svg_export, _cursor_skills_graphify_references_exports_graphml_export, _cursor_skills_graphify_references_exports_mcp_graph_server [EXTRACTED 1.00]
- **Query Feedback Loop** — _cursor_skills_graphify_references_query_constrained_query_expansion, _cursor_skills_graphify_references_query_bfs_traversal, _cursor_skills_graphify_references_query_save_result_feedback, _cursor_skills_graphify_references_query_work_memory_reflect [EXTRACTED 1.00]
- **Ponytail Skill Suite** — _cursor_skills_ponytail_skill_ponytail, _cursor_skills_ponytail_review_skill_ponytail_review, _cursor_skills_ponytail_audit_skill_ponytail_audit, _cursor_skills_ponytail_debt_skill_ponytail_debt, _cursor_skills_ponytail_gain_skill_ponytail_gain, _cursor_skills_ponytail_help_skill_ponytail_help [EXTRACTED 1.00]
- **Sprint 1 Core Data Engine stories** — agents_sprint_1_core_data_engine, agents_story_101, agents_story_102, agents_story_103 [EXTRACTED 1.00]
- **Secret Hygiene Across Project Docs** — _cursor_skills_secret_hygiene_skill_secret_hygiene, _cursor_skills_mmt_mmm_skill_secret_folder [INFERRED 0.85]

## Communities (31 total, 10 thin omitted)

### Community 0 - "test_transformations.py"
Cohesion: 0.06
Nodes (59): fixture, numpy, Shared modeling primitives (transforms, later likelihoods / inference)., geometric_adstock(), hill_saturation(), ndarray, Apply two-parameter Weibull adstock along ``axis``. Builds discrete Weibull…, Hill / Michaelis–Menten saturation mapped to ``[0, 1)``. Form:: y = x^S / (K^S… (+51 more)

### Community 1 - "/graphify"
Cohesion: 0.11
Nodes (19): FalkorDB Export, GraphML Export (--graphml), Neo4j Export, SVG Export (--svg), Token Reduction Benchmark, Wiki Export (--wiki), AGENTS.md Graphify Integration, Cluster-Only Mode (+11 more)

### Community 2 - "generator.py"
Cohesion: 0.09
Nodes (38): Any, json, pandas, pathlib, ground_truth.json, skipif, assert_valid(), _baseline_sales() (+30 more)

### Community 3 - "transformations.py"
Cohesion: 0.15
Nodes (18): archify, data/raw/, Path-C synthetic multi-channel DGP, STORY-101, geometric_adstock, hill_saturation, baseline_sales, Channel-day grain (+10 more)

### Community 4 - "sprint-1-core-data-engine"
Cohesion: 0.13
Nodes (17): github remote, martech-mmm-ai-allocator, mmt-mmm conda env, No leakage, origin remote, sprint-1-core-data-engine, STORY-103, Agentic explain layer (+9 more)

### Community 5 - "plot_adstock_validation.py"
Cohesion: 0.16
Nodes (16): reports/figures/, STORY-102, Plotly Express over Jupyter for Sprint 1, plotly_express, build_geometric_figure(), build_hill_figure(), build_weibull_figure(), main() (+8 more)

### Community 6 - "What You Must Do When Invoked"
Cohesion: 0.13
Nodes (15): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Step 1 - Ensure graphify is installed, Step 2.5 - Video and audio (only if video files detected), Step 2 - Detect files, Step 3 - Extract entities and relationships (+7 more)

### Community 7 - "MMT&MMM Project Conventions"
Cohesion: 0.20
Nodes (12): ELI5 Teacher, Four-Phase Teaching Structure, archify Skill, MMT&MMM Project Conventions, Secret/ Local-Only Path, Secret Hygiene, Agent Skills SKILL.md Format, Skill Author (+4 more)

### Community 8 - "Ponytail Help"
Cohesion: 0.27
Nodes (12): Ponytail Audit, ponytail: Comment Marker, Ponytail Debt, Ponytail Benchmark Medians, Ponytail Gain, Ponytail Intensity Levels (lite/full/ultra), Ponytail Help, Over-Engineering Review Tags (+4 more)

### Community 9 - "Semantic Extraction Spec"
Cohesion: 0.25
Nodes (8): Confidence Score Rubric, DEEP_MODE, Deterministic Node ID Format, Hyperedges, Semantic Extraction Spec, semantically_similar_to Relation, EXTRACTED/INFERRED/AMBIGUOUS Audit Trail, Honesty Rules

### Community 11 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 12 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 13 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 14 - "graphify reference: commit hook and native AGENTS.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native AGENTS.md integration, graphify reference: commit hook and native AGENTS.md integration

### Community 15 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 16 - "graphify + archify artifacts"
Cohesion: 0.50
Nodes (3): archify, graphify, graphify + archify artifacts

### Community 26 - "test_etl.py"
Cohesion: 0.11
Nodes (30): pandera_errors, pandera_pandas, pytest, align_date_channel_grid(), impute_panel(), load_raw(), main(), DataFrame (+22 more)

### Community 27 - "Incremental Update (--update)"
Cohesion: 0.27
Nodes (10): Folder Watch Mode (--watch), needs_update Flag, URL Corpus Ingest (/graphify add), Watch Debounce, Post-Commit Rebuild Hook, build_merge Replace-on-Re-extract, Code-Only Update Fast Path, Graph Diff After Update (+2 more)

### Community 28 - "Whisper Video/Audio Transcription"
Cohesion: 0.29
Nodes (7): MCP Graph Server, Domain Hint Whisper Prompt, Whisper Video/Audio Transcription, AST+Semantic Extraction Merge (Part C), God Nodes, No API Key Required, Semantic Extraction (Part B)

### Community 29 - "save-result Feedback Loop"
Cohesion: 0.29
Nodes (7): BFS Traversal, Constrained Query Expansion, Node Explain Query (/graphify explain), save-result Feedback Loop, Shortest Path Query (/graphify path), Work Memory Reflect (LESSONS.md), Fast Path Query

### Community 30 - "graphify merge-graphs"
Cohesion: 0.50
Nodes (4): Cross-Repo Graph, graphify clone, graphify merge-graphs, Per-Subfolder CLI Extract

## Knowledge Gaps
- **77 isolated node(s):** `For /graphify add and --watch`, `For /graphify query`, `For the commit hook and native AGENTS.md integration`, `For --update and --cluster-only`, `Interpreter guard for subcommands` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 150 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `/graphify` connect `/graphify` to `transformations.py`, `What You Must Do When Invoked`, `Semantic Extraction Spec`, `Incremental Update (--update)`, `Whisper Video/Audio Transcription`, `save-result Feedback Loop`, `graphify merge-graphs`, `graphify-out artifacts`?**
  _High betweenness centrality (0.287) - this node is a cross-community bridge._
- **Why does `STORY-101` connect `transformations.py` to `sprint-1-core-data-engine`?**
  _High betweenness centrality (0.263) - this node is a cross-community bridge._
- **What connects `For /graphify add and --watch`, `For /graphify query`, `For the commit hook and native AGENTS.md integration` to the rest of the system?**
  _77 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_transformations.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05764145954521417 - nodes in this community are weakly interconnected._
- **Should `/graphify` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `generator.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09487179487179487 - nodes in this community are weakly interconnected._
- **Should `transformations.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._