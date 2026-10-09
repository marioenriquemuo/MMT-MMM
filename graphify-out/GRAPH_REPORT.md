# Graph Report - MMT&MMM  (2026-10-09)

## Corpus Check
- 45 files · ~31,132 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 6, .mdc 5, .csv 3)

## Summary
- 430 nodes · 715 edges · 33 communities (23 shown, 10 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bd47315a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_transformations.py
- /graphify
- generator.py
- transformations.py
- plot_adstock_validation.py
- test_qa.py
- What You Must Do When Invoked
- MMT&MMM Project Conventions
- test_meridian_data.py
- Semantic Extraction Spec
- 02_model_spike.py
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
- Parameter recovery note (STORY-201)

## God Nodes (most connected - your core abstractions)
1. `/graphify` - 33 edges
2. `generate()` - 21 edges
3. `geometric_adstock()` - 20 edges
4. `weibull_adstock()` - 20 edges
5. `hill_saturation()` - 18 edges
6. `repair_panel()` - 14 edges
7. `detect_anomalies()` - 13 edges
8. `main()` - 12 edges
9. `run_etl()` - 12 edges
10. `load_panel()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `mmt-mmm` --semantically_similar_to--> `mmt-mmm conda env`  [INFERRED] [semantically similar]
  environment.yml → AGENTS.md
- `/graphify` --conceptually_related_to--> `archify`  [INFERRED]
  .cursor/skills/graphify/SKILL.md → AGENTS.md
- `geometric_adstock` --semantically_similar_to--> `weibull_adstock`  [INFERRED] [semantically similar]
  CLAUDE.md → README.md
- `graphify-out artifacts` --references--> `/graphify`  [EXTRACTED]
  docs/graphify-archify.md → .cursor/skills/graphify/SKILL.md
- `main()` --calls--> `load_meridian_input()`  [EXTRACTED]
  scripts/02_model_spike.py → src/models/meridian_data.py

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

## Communities (33 total, 10 thin omitted)

### Community 0 - "test_transformations.py"
Cohesion: 0.06
Nodes (59): fixture, numpy, Shared modeling primitives (transforms, Meridian adapter, inference)., geometric_adstock(), hill_saturation(), ndarray, Apply two-parameter Weibull adstock along ``axis``. Builds discrete Weibull…, Hill / Michaelis–Menten saturation mapped to ``[0, 1)``. Form:: y = x^S / (K^S… (+51 more)

### Community 1 - "/graphify"
Cohesion: 0.11
Nodes (19): FalkorDB Export, GraphML Export (--graphml), Neo4j Export, SVG Export (--svg), Token Reduction Benchmark, Wiki Export (--wiki), AGENTS.md Graphify Integration, Cluster-Only Mode (+11 more)

### Community 2 - "generator.py"
Cohesion: 0.10
Nodes (37): Any, json, pathlib, ground_truth.json, assert_valid(), _baseline_sales(), coerce_integer_columns(), generate() (+29 more)

### Community 3 - "transformations.py"
Cohesion: 0.15
Nodes (18): archify, data/raw/, Path-C synthetic multi-channel DGP, STORY-101, geometric_adstock, hill_saturation, baseline_sales, Channel-day grain (+10 more)

### Community 4 - "plot_adstock_validation.py"
Cohesion: 0.08
Nodes (32): github remote, martech-mmm-ai-allocator, mmt-mmm conda env, No leakage, origin remote, reports/figures/, sprint-1-core-data-engine, STORY-102 (+24 more)

### Community 5 - "test_qa.py"
Cohesion: 0.10
Nodes (44): RuntimeError, detect_anomalies(), load_panel(), main(), _prior_activity(), DataFrame, Path, STORY-104 media QA: detect + repair channel-day anomalies (pre-Meridian gate).… (+36 more)

### Community 6 - "What You Must Do When Invoked"
Cohesion: 0.13
Nodes (15): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Step 1 - Ensure graphify is installed, Step 2.5 - Video and audio (only if video files detected), Step 2 - Detect files, Step 3 - Extract entities and relationships (+7 more)

### Community 7 - "MMT&MMM Project Conventions"
Cohesion: 0.12
Nodes (24): ELI5 Teacher, Four-Phase Teaching Structure, archify Skill, MMT&MMM Project Conventions, Secret/ Local-Only Path, Ponytail Audit, ponytail: Comment Marker, Ponytail Debt (+16 more)

### Community 8 - "test_meridian_data.py"
Cohesion: 0.15
Nodes (23): InputData, meridian_data_input_data, pandas, load_clean_panel(), load_meridian_input(), panel_to_national_wide(), DataFrame, Path (+15 more)

### Community 9 - "Semantic Extraction Spec"
Cohesion: 0.25
Nodes (8): Confidence Score Rubric, DEEP_MODE, Deterministic Node ID Format, Hyperedges, Semantic Extraction Spec, semantically_similar_to Relation, EXTRACTED/INFERRED/AMBIGUOUS Audit Trail, Honesty Rules

### Community 10 - "02_model_spike.py"
Cohesion: 0.15
Nodes (23): argparse, matplotlib, matplotlib_pyplot, meridian_analysis, meridian_model, Namespace, _analyzer(), _build_mmm() (+15 more)

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

### Community 32 - "Parameter recovery note (STORY-201)"
Cohesion: 0.40
Nodes (4): Estimated iROAS (posterior mean, units per $), Parameter recovery note (STORY-201), Path-C planted signals, Rank comparison

## Knowledge Gaps
- **80 isolated node(s):** `Estimated iROAS (posterior mean, units per $)`, `Path-C planted signals`, `Rank comparison`, `For /graphify add and --watch`, `For /graphify query` (+75 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 185 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `/graphify` connect `/graphify` to `transformations.py`, `What You Must Do When Invoked`, `Semantic Extraction Spec`, `Incremental Update (--update)`, `Whisper Video/Audio Transcription`, `save-result Feedback Loop`, `graphify merge-graphs`, `graphify-out artifacts`?**
  _High betweenness centrality (0.244) - this node is a cross-community bridge._
- **Why does `STORY-101` connect `transformations.py` to `plot_adstock_validation.py`?**
  _High betweenness centrality (0.233) - this node is a cross-community bridge._
- **What connects `Estimated iROAS (posterior mean, units per $)`, `Path-C planted signals`, `Rank comparison` to the rest of the system?**
  _80 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_transformations.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05764145954521417 - nodes in this community are weakly interconnected._
- **Should `/graphify` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `generator.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09716599190283401 - nodes in this community are weakly interconnected._
- **Should `transformations.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._