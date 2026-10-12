# Graph Report - MMT&MMM  (2026-10-12)

## Corpus Check
- 58 files · ~37,827 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 6, .mdc 5, .csv 3)

## Summary
- 578 nodes · 1025 edges · 47 communities (35 shown, 12 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `acb658c3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ndarray
- /graphify
- generate
- MetricsJsonCurveProvider
- Path-C synthetic multi-channel marketing panel
- test_qa.py
- What You Must Do When Invoked
- MMT&MMM Project Conventions
- 02_model_spike.py
- Semantic Extraction Spec
- test_meridian_data.py
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native AGENTS.md integration
- graphify reference: incremental update and cluster-only
- STORY-201 learnings — Meridian Bayesian MMM spike
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
- test_model_spike_helpers.py
- meridian_analysis
- meridian_model
- plot_adstock_validation.py
- load_curve_means
- transformations.py
- hill_saturation
- test_transformations.py
- optimize_budget
- plot_allocation_teaching.py
- allocator.py
- curves.py
- .mean_grid
- weibull_adstock

## God Nodes (most connected - your core abstractions)
1. `MetricsJsonCurveProvider` - 37 edges
2. `/graphify` - 33 edges
3. `optimize_budget()` - 22 edges
4. `generate()` - 21 edges
5. `geometric_adstock()` - 20 edges
6. `weibull_adstock()` - 20 edges
7. `hill_saturation()` - 18 edges
8. `_minimize_for_target()` - 15 edges
9. `repair_panel()` - 14 edges
10. `_maximize()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `mmt-mmm` --semantically_similar_to--> `mmt-mmm conda env`  [INFERRED] [semantically similar]
  environment.yml → AGENTS.md
- `/graphify` --conceptually_related_to--> `archify`  [INFERRED]
  .cursor/skills/graphify/SKILL.md → AGENTS.md
- `geometric_adstock` --semantically_similar_to--> `weibull_adstock`  [INFERRED] [semantically similar]
  CLAUDE.md → README.md
- `_curve_frame()` --uses--> `MetricsJsonCurveProvider`  [INFERRED]
  scripts/plot_allocation_teaching.py → src/optimize/curves.py
- `_bar_frame()` --uses--> `MetricsJsonCurveProvider`  [INFERRED]
  scripts/plot_allocation_teaching.py → src/optimize/curves.py

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

## Communities (47 total, 12 thin omitted)

### Community 0 - "ndarray"
Cohesion: 0.14
Nodes (15): long_pulse(), pulse(), fixture, ndarray, normalize=False keeps raw PDF-style weights (pulse response ≠ pulse)., Larger scale stretches carryover — more mass in the late tail., shape < 1 peaks at lag 0; shape > 1 can peak after day 0., Impulse of 100 on day 0, zeros after (hand-checkable decay). (+7 more)

### Community 1 - "/graphify"
Cohesion: 0.11
Nodes (19): FalkorDB Export, GraphML Export (--graphml), Neo4j Export, SVG Export (--svg), Token Reduction Benchmark, Wiki Export (--wiki), AGENTS.md Graphify Integration, Cluster-Only Mode (+11 more)

### Community 2 - "generate"
Cohesion: 0.11
Nodes (30): assert_valid(), coerce_integer_columns(), generate(), _impressions_clicks(), main(), planted_ground_truth(), Any, DataFrame (+22 more)

### Community 3 - "MetricsJsonCurveProvider"
Cohesion: 0.17
Nodes (14): main(), MetricsJsonCurveProvider, Linear-interpolated curves from Meridian metrics or synthetic fixture JSON., fixture_provider(), fixture, skipif, STORY-301 Step 1 — response curve provider (interpolation + loaders)., Fixture curves are concave / non-decreasing in spend. (+6 more)

### Community 4 - "Path-C synthetic multi-channel marketing panel"
Cohesion: 0.08
Nodes (32): archify, data/raw/, github remote, martech-mmm-ai-allocator, mmt-mmm conda env, No leakage, origin remote, Path-C synthetic multi-channel DGP (+24 more)

### Community 5 - "test_qa.py"
Cohesion: 0.07
Nodes (57): pandas, pandera_pandas, pathlib, plotly_express, ground_truth.json, RuntimeError, STORY-301 Step 0 — toy diminishing-returns curve (not Meridian, not optimizer).…, STORY-301 Step 1 — Plotly Express of synthetic fixture response curves. Usage… (+49 more)

### Community 6 - "What You Must Do When Invoked"
Cohesion: 0.13
Nodes (15): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Step 1 - Ensure graphify is installed, Step 2.5 - Video and audio (only if video files detected), Step 2 - Detect files, Step 3 - Extract entities and relationships (+7 more)

### Community 7 - "MMT&MMM Project Conventions"
Cohesion: 0.12
Nodes (24): ELI5 Teacher, Four-Phase Teaching Structure, archify Skill, MMT&MMM Project Conventions, Secret/ Local-Only Path, Ponytail Audit, ponytail: Comment Marker, Ponytail Debt (+16 more)

### Community 8 - "02_model_spike.py"
Cohesion: 0.15
Nodes (24): matplotlib, matplotlib_pyplot, Namespace, _analyzer(), _build_mmm(), _core_rhat_rows(), _jsonable(), main() (+16 more)

### Community 9 - "Semantic Extraction Spec"
Cohesion: 0.25
Nodes (8): Confidence Score Rubric, DEEP_MODE, Deterministic Node ID Format, Hyperedges, Semantic Extraction Spec, semantically_similar_to Relation, EXTRACTED/INFERRED/AMBIGUOUS Audit Trail, Honesty Rules

### Community 10 - "test_meridian_data.py"
Cohesion: 0.16
Nodes (22): InputData, meridian_data_input_data, load_clean_panel(), load_meridian_input(), panel_to_national_wide(), DataFrame, Path, STORY-201: map QA'd ``clean_spend.parquet`` → Meridian national ``InputData``.… (+14 more)

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

### Community 16 - "STORY-201 learnings — Meridian Bayesian MMM spike"
Cohesion: 0.12
Nodes (15): archify, graphify, graphify + archify artifacts, How to run, Likely investigation axes (post-POC), Meridian is a local pip library, National weekly adapter, Open issue — rank recovery vs Path-C is inconsistent (+7 more)

### Community 26 - "test_etl.py"
Cohesion: 0.13
Nodes (27): pandera_errors, align_date_channel_grid(), impute_panel(), load_raw(), main(), DataFrame, Path, Apply locked STORY-103 fill rules on an aligned panel. * Media (``spend``,… (+19 more)

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

### Community 33 - "test_model_spike_helpers.py"
Cohesion: 0.17
Nodes (8): importlib_util, pytest, _load_spike(), fixture, Unit tests for STORY-201 spike helpers (no Meridian MCMC)., Import scripts/02_model_spike.py without running main (no Meridian import)., spike(), xarray

### Community 36 - "plot_adstock_validation.py"
Cohesion: 0.19
Nodes (14): reports/figures/, STORY-102, Plotly Express over Jupyter for Sprint 1, build_geometric_figure(), build_hill_figure(), build_weibull_figure(), main(), _pulse_frame() (+6 more)

### Community 37 - "load_curve_means"
Cohesion: 0.18
Nodes (14): CurveArrays, _extract_means_map(), load_curve_means(), load_curve_means_json(), _looks_like_arrays(), Any, Path, Load curve arrays from a JSON file path. (+6 more)

### Community 38 - "transformations.py"
Cohesion: 0.23
Nodes (10): numpy, STORY-102 media transforms (Steps 2–5: adstock + Hill saturation). Pure NumPy…, _panel(), ndarray, STORY-102 Step 6 — wall-time gate for transforms on ~2y daily data., Non-negative spend panel shaped ``(channels, days)``., DoD: geometric + Weibull + Hill on 730×4 panel finishes in <1s., _run_transforms() (+2 more)

### Community 39 - "hill_saturation"
Cohesion: 0.12
Nodes (15): _baseline_sales(), National baseline + media contribution after adstock/Hill., Shared modeling primitives (transforms, Meridian adapter, inference)., hill_saturation(), Hill / Michaelis–Menten saturation mapped to ``[0, 1)``. Form:: y = x^S / (K^S…, At x = K, y ≈ 0.5 for any valid S., Larger S → steeper slope near K (higher |dy/dx| at half-sat)., Negative spend clipped to 0 → response 0 (documented). (+7 more)

### Community 40 - "test_transformations.py"
Cohesion: 0.23
Nodes (13): geometric_adstock(), Apply one-parameter geometric adstock along ``axis``. Recurrence (carryover of…, Tests for STORY-102 geometric + Weibull adstock + Hill (Steps 2–4)., 100 then zeros, theta=0.5 → 100, 50, 25, 12.5, …, Shape (channels, T) with axis=-1 adstocks each channel independently., test_2d_channels_by_time(), test_length_preserved(), test_matches_recursive_definition() (+5 more)

### Community 41 - "optimize_budget"
Cohesion: 0.18
Nodes (16): optimize_budget(), Allocate spend across channels (maximize KPI or hit a KPI target). Exactly one…, fixture_provider(), fixture, Path, STORY-301 Steps 2–3 — SLSQP allocator bounds, budget sum, target KPI., test_cli_run_allocate_writes_json(), test_infeasible_maxes_below_budget() (+8 more)

### Community 42 - "plot_allocation_teaching.py"
Cohesion: 0.23
Nodes (13): plotly_subplots, _bar_frame(), build_curves_figure(), build_parser(), _curve_frame(), _equal_room_baseline(), main(), ArgumentParser (+5 more)

### Community 43 - "allocator.py"
Cohesion: 0.17
Nodes (24): scipy_optimize, _bounds_dict(), _bounds_gate(), _constraints(), _curve_max_spends(), _fail_result(), _feasible_start(), _maximize() (+16 more)

### Community 44 - "curves.py"
Cohesion: 0.15
Nodes (15): ABC, argparse, json, build_parser(), main(), _parse_spend_arg(), Any, ArgumentParser (+7 more)

### Community 45 - ".mean_grid"
Cohesion: 0.40
Nodes (3): ndarray, Observed spend knots for ``channel`` (teaching / tests)., Observed mean incremental KPI knots for ``channel``.

### Community 47 - "weibull_adstock"
Cohesion: 0.20
Nodes (11): ndarray, Apply two-parameter Weibull adstock along ``axis``. Builds discrete Weibull…, Choose discrete lag support ``L`` for Weibull PDF weights. Default:…, Discrete Weibull PDF-style weights on lags ``0 .. L-1``. Evaluated at positive…, weibull_adstock(), _weibull_n_lags(), _weibull_pdf_weights(), Normalized weights sum to 1 → constant series stays at that level. (+3 more)

## Knowledge Gaps
- **89 isolated node(s):** `Meridian is a local pip library`, `Smoke vs full`, `R-hat`, `National weekly adapter`, `Warnings that are normal` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 242 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `/graphify` connect `/graphify` to `Path-C synthetic multi-channel marketing panel`, `What You Must Do When Invoked`, `Semantic Extraction Spec`, `Incremental Update (--update)`, `Whisper Video/Audio Transcription`, `save-result Feedback Loop`, `graphify merge-graphs`, `graphify-out artifacts`?**
  _High betweenness centrality (0.200) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `MetricsJsonCurveProvider` (e.g. with `_bar_frame()` and `build_curves_figure()`) actually correct?**
  _`MetricsJsonCurveProvider` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Meridian is a local pip library`, `Smoke vs full`, `R-hat` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ndarray` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Should `/graphify` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `generate` be split into smaller, more focused modules?**
  _Cohesion score 0.10967741935483871 - nodes in this community are weakly interconnected._
- **Should `Path-C synthetic multi-channel marketing panel` be split into smaller, more focused modules?**
  _Cohesion score 0.07661290322580645 - nodes in this community are weakly interconnected._