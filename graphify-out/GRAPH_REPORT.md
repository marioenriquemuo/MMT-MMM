# Graph Report - MMT&MMM  (2026-10-15)

## Corpus Check
- 80 files · ~51,410 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 27 file(s) not represented in the graph (top: (none) 9, .csv 9, .mdc 5)

## Summary
- 841 nodes · 1652 edges · 55 communities (42 shown, 13 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 56 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0753a7e2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ndarray
- /graphify
- generator.py
- test_csuite_brief.py
- Open gaps registry
- test_qa.py
- What You Must Do When Invoked
- MMT&MMM Project Conventions
- 02_model_spike.py
- Semantic Extraction Spec
- test_csuite_facts.py
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native AGENTS.md integration
- graphify reference: incremental update and cluster-only
- controls.py
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
- 04_csuite_brief.py
- Parameter recovery note (STORY-201)
- test_model_spike_helpers.py
- meridian_analysis
- meridian_model
- plot_adstock_validation.py
- 03_allocate_budget.py
- numpy
- weibull_adstock
- test_transformations.py
- MetricsJsonCurveProvider
- build_fact_pack
- allocator.py
- .mean_grid
- plot_allocation_teaching.py
- transformations.py
- test_curves.py
- sprint-1-core-data-engine
- curves.py
- brief.py
- view.py
- How to test this marketing mix modeling tool
- graphify-out artifacts
- notebooks/README.md

## God Nodes (most connected - your core abstractions)
1. `MetricsJsonCurveProvider` - 46 edges
2. `/graphify` - 33 edges
3. `build_fact_pack()` - 26 edges
4. `build_dashboard()` - 25 edges
5. `optimize_budget()` - 25 edges
6. `generate()` - 21 edges
7. `render_offline()` - 21 edges
8. `build_controls()` - 20 edges
9. `geometric_adstock()` - 20 edges
10. `weibull_adstock()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `GAP-501-API` --references--> `build_controls()`  [INFERRED]
  docs/learnings/open-gaps.md → src/data/controls.py
- `mmt-mmm` --semantically_similar_to--> `mmt-mmm conda env`  [INFERRED] [semantically similar]
  environment.yml → AGENTS.md
- `test_clamp_outside_range()` --uses--> `MetricsJsonCurveProvider`  [INFERRED]
  tests/test_curves.py → src/optimize/curves.py
- `test_exact_knots()` --uses--> `MetricsJsonCurveProvider`  [INFERRED]
  tests/test_curves.py → src/optimize/curves.py
- `test_midpoint_interpolation()` --uses--> `MetricsJsonCurveProvider`  [INFERRED]
  tests/test_curves.py → src/optimize/curves.py

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

## Communities (55 total, 13 thin omitted)

### Community 0 - "ndarray"
Cohesion: 0.13
Nodes (16): long_pulse(), pulse(), fixture, ndarray, normalize=False keeps raw PDF-style weights (pulse response ≠ pulse)., Larger scale stretches carryover — more mass in the late tail., shape < 1 peaks at lag 0; shape > 1 can peak after day 0., Impulse of 100 on day 0, zeros after (hand-checkable decay). (+8 more)

### Community 1 - "/graphify"
Cohesion: 0.11
Nodes (19): FalkorDB Export, GraphML Export (--graphml), Neo4j Export, SVG Export (--svg), Token Reduction Benchmark, Wiki Export (--wiki), AGENTS.md Graphify Integration, Cluster-Only Mode (+11 more)

### Community 2 - "generator.py"
Cohesion: 0.11
Nodes (34): ground_truth.json, assert_valid(), _baseline_sales(), coerce_integer_columns(), generate(), _impressions_clicks(), main(), planted_ground_truth() (+26 more)

### Community 3 - "test_csuite_brief.py"
Cohesion: 0.15
Nodes (25): CompletedProcess, build_messages(), Force the ``emit_brief`` tool, validate, then lock numbers. Raises…, System and user prompt. The user turn is the fact pack JSON only., render_live(), numbers_match(), True when the brief matches the fact pack. Structured fields use absolute…, emit_brief_json_schema() (+17 more)

### Community 4 - "Open gaps registry"
Cohesion: 0.05
Nodes (40): archify, graphify, graphify + archify artifacts, Closed / not listed, GAP-201-RANK, GAP-402-DOCKERIGNORE, GAP-402-LOOM, GAP-402-RENAME (+32 more)

### Community 5 - "test_qa.py"
Cohesion: 0.06
Nodes (66): pandas, pathlib, plotly_express, STORY-301 Step 1 — Plotly Express of synthetic fixture response curves. Usage…, _equal_room_baseline(), _kpi(), _long_frame(), main() (+58 more)

### Community 6 - "What You Must Do When Invoked"
Cohesion: 0.13
Nodes (15): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Step 1 - Ensure graphify is installed, Step 2.5 - Video and audio (only if video files detected), Step 2 - Detect files, Step 3 - Extract entities and relationships (+7 more)

### Community 7 - "MMT&MMM Project Conventions"
Cohesion: 0.12
Nodes (24): ELI5 Teacher, Four-Phase Teaching Structure, archify Skill, MMT&MMM Project Conventions, Secret/ Local-Only Path, Ponytail Audit, ponytail: Comment Marker, Ponytail Debt (+16 more)

### Community 8 - "02_model_spike.py"
Cohesion: 0.08
Nodes (46): InputData, matplotlib, matplotlib_pyplot, meridian_data_input_data, Namespace, _analyzer(), _build_mmm(), _core_rhat_rows() (+38 more)

### Community 9 - "Semantic Extraction Spec"
Cohesion: 0.25
Nodes (8): Confidence Score Rubric, DEEP_MODE, Deterministic Node ID Format, Hyperedges, Semantic Extraction Spec, semantically_similar_to Relation, EXTRACTED/INFERRED/AMBIGUOUS Audit Trail, Honesty Rules

### Community 10 - "test_csuite_facts.py"
Cohesion: 0.15
Nodes (21): BaseModel, pydantic, STORY-302 C-suite brief (fact pack, schema, offline and live render)., ChannelFact, ChannelShift, CsuiteBrief, FactPack, Pydantic schema for a future ``emit_brief`` tool (STORY-302 Step 1). The model… (+13 more)

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

### Community 16 - "controls.py"
Cohesion: 0.10
Nodes (41): Column, DatetimeIndex, pandera_pandas, _assert_matches_panel(), build_controls(), _count_col(), _counts(), _dated() (+33 more)

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

### Community 31 - "04_csuite_brief.py"
Cohesion: 0.13
Nodes (21): BaseException, json, re, build_parser(), _fail(), main(), Any, ArgumentParser (+13 more)

### Community 32 - "Parameter recovery note (STORY-201)"
Cohesion: 0.40
Nodes (4): Estimated iROAS (posterior mean, units per $), Parameter recovery note (STORY-201), Path-C planted signals, Rank comparison

### Community 33 - "test_model_spike_helpers.py"
Cohesion: 0.17
Nodes (8): importlib_util, pytest, _load_spike(), fixture, Unit tests for STORY-201 spike helpers (no Meridian MCMC)., Import scripts/02_model_spike.py without running main (no Meridian import)., spike(), xarray

### Community 36 - "plot_adstock_validation.py"
Cohesion: 0.19
Nodes (14): reports/figures/, STORY-102, Plotly Express over Jupyter for Sprint 1, build_geometric_figure(), build_hill_figure(), build_weibull_figure(), main(), _pulse_frame() (+6 more)

### Community 37 - "03_allocate_budget.py"
Cohesion: 0.24
Nodes (10): build_parser(), main(), _parse_spend_arg(), Any, ArgumentParser, Path, Library entrypoint (also used by tests). Writes JSON when ``out`` is set., STORY-301 Step 3 — allocate budget from offline response curves. Examples::… (+2 more)

### Community 38 - "numpy"
Cohesion: 0.21
Nodes (10): numpy, STORY-301 Step 0 — toy diminishing-returns curve (not Meridian, not optimizer).…, _panel(), ndarray, STORY-102 Step 6 — wall-time gate for transforms on ~2y daily data., Non-negative spend panel shaped ``(channels, days)``., DoD: geometric + Weibull + Hill on 730×4 panel finishes in <1s., _run_transforms() (+2 more)

### Community 39 - "weibull_adstock"
Cohesion: 0.17
Nodes (12): Shared modeling primitives (transforms, Meridian adapter, inference)., ndarray, Apply two-parameter Weibull adstock along ``axis``. Builds discrete Weibull…, Choose discrete lag support ``L`` for Weibull PDF weights. Default:…, Discrete Weibull PDF-style weights on lags ``0 .. L-1``. Evaluated at positive…, weibull_adstock(), _weibull_n_lags(), _weibull_pdf_weights() (+4 more)

### Community 40 - "test_transformations.py"
Cohesion: 0.13
Nodes (24): geometric_adstock(), hill_saturation(), Hill / Michaelis–Menten saturation mapped to ``[0, 1)``. Form:: y = x^S / (K^S…, Apply one-parameter geometric adstock along ``axis``. Recurrence (carryover of…, Tests for STORY-102 geometric + Weibull adstock + Hill (Steps 2–4)., At x = K, y ≈ 0.5 for any valid S., Larger S → steeper slope near K (higher |dy/dx| at half-sat)., Negative spend clipped to 0 → response 0 (documented). (+16 more)

### Community 41 - "MetricsJsonCurveProvider"
Cohesion: 0.15
Nodes (22): main(), optimize_budget(), Allocate spend across channels (maximize KPI or hit a KPI target). Exactly one…, MetricsJsonCurveProvider, Linear-interpolated curves from Meridian metrics or synthetic fixture JSON., fixture_provider(), fixture, Path (+14 more)

### Community 42 - "build_fact_pack"
Cohesion: 0.17
Nodes (19): decimal, math, _allowed_numbers(), _bound(), build_fact_pack(), _concentration_note(), _equal_room(), first_mismatch() (+11 more)

### Community 43 - "allocator.py"
Cohesion: 0.23
Nodes (20): scipy_optimize, _bounds_dict(), _bounds_gate(), _constraints(), _curve_max_spends(), _fail_result(), _feasible_start(), _maximize() (+12 more)

### Community 44 - ".mean_grid"
Cohesion: 0.40
Nodes (3): ndarray, Observed spend knots for ``channel`` (teaching / tests)., Observed mean incremental KPI knots for ``channel``.

### Community 45 - "plot_allocation_teaching.py"
Cohesion: 0.21
Nodes (14): argparse, plotly_subplots, _bar_frame(), build_curves_figure(), build_parser(), _curve_frame(), _equal_room_baseline(), main() (+6 more)

### Community 46 - "transformations.py"
Cohesion: 0.17
Nodes (16): archify, data/raw/, Path-C synthetic multi-channel DGP, STORY-101, geometric_adstock, hill_saturation, baseline_sales, Channel-day grain (+8 more)

### Community 47 - "test_curves.py"
Cohesion: 0.11
Nodes (24): CurveArrays, _extract_means_map(), load_curve_means(), load_curve_means_json(), _looks_like_arrays(), Any, Path, Load curve arrays from a JSON file path. (+16 more)

### Community 48 - "sprint-1-core-data-engine"
Cohesion: 0.13
Nodes (17): github remote, martech-mmm-ai-allocator, mmt-mmm conda env, No leakage, origin remote, sprint-1-core-data-engine, STORY-103, Agentic explain layer (+9 more)

### Community 49 - "curves.py"
Cohesion: 0.22
Nodes (7): ABC, CurveProvider, Offline response-curve providers for STORY-301 (Step 1). Reads Meridian…, Spend → incremental KPI per channel (offline or future live)., Channel names available on this provider., Interpolated incremental KPI at ``spend`` for ``channel``., Budget optimization helpers (STORY-301). Step 1: offline response-curve…

### Community 50 - "brief.py"
Cohesion: 0.30
Nodes (13): os, _field(), _fmt(), _headline(), _lift_bullet(), Any, C-suite brief (STORY-302 Steps 2–3). Builds a system+user prompt from the fact…, Fixed-point text within the prose lock's 1e-4 absolute tolerance. ``g``… (+5 more)

### Community 51 - "view.py"
Cohesion: 0.08
Nodes (55): _commentary(), main(), _clamp_max(), _clamp_min(), STORY-401 Streamlit layout. Sliders and number boxes set the total budget and…, Slider and number box on one session value. ``clamp`` runs on each edit., _redact(), _synced_number() (+47 more)

### Community 53 - "How to test this marketing mix modeling tool"
Cohesion: 0.25
Nodes (7): 1. What you are testing, 2. Install once, 3. Automated test, 4. Dashboard test, no API key, 5. Optional live test, 6. What a good result is not, How to test this marketing mix modeling tool

## Knowledge Gaps
- **115 isolated node(s):** `1. What you are testing`, `2. Install once`, `3. Automated test`, `4. Dashboard test, no API key`, `5. Optional live test` (+110 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 339 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `STORY-101` connect `transformations.py` to `sprint-1-core-data-engine`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Why does `/graphify` connect `/graphify` to `What You Must Do When Invoked`, `Semantic Extraction Spec`, `transformations.py`, `graphify-out artifacts`, `Incremental Update (--update)`, `Whisper Video/Audio Transcription`, `save-result Feedback Loop`, `graphify merge-graphs`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `MetricsJsonCurveProvider` (e.g. with `_bar_frame()` and `build_curves_figure()`) actually correct?**
  _`MetricsJsonCurveProvider` has 24 INFERRED edges - model-reasoned connections that need verification._
- **What connects `1. What you are testing`, `2. Install once`, `3. Automated test` to the rest of the system?**
  _115 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ndarray` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `/graphify` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `generator.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10634920634920635 - nodes in this community are weakly interconnected._