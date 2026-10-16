# Graph Report - MMT&MMM  (2026-10-15)

## Corpus Check
- 69 files · ~43,934 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: .csv 10, (none) 8, .parquet 2)

## Summary
- 803 nodes · 1772 edges · 41 communities (31 shown, 10 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 56 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e0bd73e6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- weibull_adstock
- plot_story_302_concepts.py
- generator.py
- test_csuite_brief.py
- Open gaps registry
- test_qa.py
- test_meridian_data.py
- MMT&MMM Project Conventions
- 02_model_spike.py
- long_pulse
- test_curves.py
- CurveProvider
- _synced_number
- Parameter recovery note (STORY-201)
- controls.py
- data/__init__.py
- src/__init__.py
- Secret/
- test_etl.py
- load_client
- Parameter recovery note (STORY-201)
- pytest
- meridian_analysis
- meridian_model
- plot_adstock_validation.py
- transformations.py
- test_transformations.py
- hill_saturation
- MetricsJsonCurveProvider
- allocator.py
- .mean_grid
- plot_allocation_teaching.py
- curves.py
- sprint-1-core-data-engine
- view.py
- How to test this marketing mix modeling tool
- graphify-out artifacts
- notebooks/README.md

## God Nodes (most connected - your core abstractions)
1. `MetricsJsonCurveProvider` - 46 edges
2. `load_client()` - 35 edges
3. `build_fact_pack()` - 26 edges
4. `build_dashboard()` - 25 edges
5. `resolve_client_path()` - 25 edges
6. `optimize_budget()` - 25 edges
7. `build_controls()` - 22 edges
8. `generate()` - 21 edges
9. `render_offline()` - 21 edges
10. `geometric_adstock()` - 20 edges

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
- **Sprint 1 Core Data Engine stories** — agents_sprint_1_core_data_engine, agents_story_101, agents_story_102, agents_story_103 [EXTRACTED 1.00]
- **Secret Hygiene Across Project Docs** — _cursor_skills_secret_hygiene_skill_secret_hygiene, _cursor_skills_mmt_mmm_skill_secret_folder [INFERRED 0.85]

## Communities (41 total, 10 thin omitted)

### Community 0 - "weibull_adstock"
Cohesion: 0.14
Nodes (19): ndarray, Apply two-parameter Weibull adstock along ``axis``. Builds discrete Weibull…, Discrete Weibull PDF-style weights on lags ``0 .. L-1``. Evaluated at positive…, weibull_adstock(), _weibull_pdf_weights(), ndarray, Normalized weights sum to 1 → constant series stays at that level., normalize=False keeps raw PDF-style weights (pulse response ≠ pulse). (+11 more)

### Community 1 - "plot_story_302_concepts.py"
Cohesion: 0.21
Nodes (11): plotly_express, STORY-301 Step 0 — toy diminishing-returns curve (not Meridian, not optimizer).…, _equal_room_baseline(), _kpi(), _long_frame(), main(), DataFrame, Path (+3 more)

### Community 2 - "generator.py"
Cohesion: 0.07
Nodes (50): archify, data/raw/, Path-C synthetic multi-channel DGP, STORY-101, geometric_adstock, hill_saturation, baseline_sales, Channel-day grain (+42 more)

### Community 3 - "test_csuite_brief.py"
Cohesion: 0.06
Nodes (83): BaseModel, CompletedProcess, decimal, json, math, os, pydantic, build_messages() (+75 more)

### Community 4 - "Open gaps registry"
Cohesion: 0.05
Nodes (40): archify, graphify, graphify + archify artifacts, Closed / not listed, GAP-201-RANK, GAP-402-DOCKERIGNORE, GAP-402-LOOM, GAP-402-RENAME (+32 more)

### Community 5 - "test_qa.py"
Cohesion: 0.09
Nodes (47): detect_anomalies(), load_panel(), main(), _prior_activity(), DataFrame, Path, RuntimeError, STORY-104 media QA: detect + repair channel-day anomalies (pre-Meridian gate).… (+39 more)

### Community 6 - "test_meridian_data.py"
Cohesion: 0.16
Nodes (22): InputData, meridian_data_input_data, load_clean_panel(), load_meridian_input(), panel_to_national_wide(), DataFrame, Path, STORY-201: map QA'd ``clean_spend.parquet`` → Meridian national ``InputData``.… (+14 more)

### Community 7 - "MMT&MMM Project Conventions"
Cohesion: 0.67
Nodes (4): archify Skill, MMT&MMM Project Conventions, Secret/ Local-Only Path, Secret Hygiene

### Community 8 - "02_model_spike.py"
Cohesion: 0.05
Nodes (68): matplotlib, matplotlib_pyplot, Namespace, _analyzer(), _build_mmm(), _core_rhat_rows(), _jsonable(), main() (+60 more)

### Community 9 - "long_pulse"
Cohesion: 0.40
Nodes (5): long_pulse(), pulse(), fixture, Impulse of 100 on day 0, zeros after (hand-checkable decay)., Longer impulse for Weibull tail / peak-timing checks.

### Community 10 - "test_curves.py"
Cohesion: 0.14
Nodes (13): fixture_provider(), fixture, skipif, STORY-301 Step 1 — response curve provider (interpolation + loaders)., Fixture curves are concave / non-decreasing in spend., test_clamp_outside_range(), test_diminishing_nondecreasing(), test_exact_knots() (+5 more)

### Community 11 - "CurveProvider"
Cohesion: 0.29
Nodes (5): ABC, CurveProvider, Spend → incremental KPI per channel (offline or future live)., Channel names available on this provider., Interpolated incremental KPI at ``spend`` for ``channel``.

### Community 12 - "_synced_number"
Cohesion: 0.60
Nodes (5): Slider and number box on one session value. ``clamp`` runs on each edit., _synced_number(), _from_number(), _from_slider(), _store()

### Community 15 - "Parameter recovery note (STORY-201)"
Cohesion: 0.40
Nodes (4): Estimated iROAS (posterior mean, units per $), Parameter recovery note (STORY-201), Path-C planted signals, Rank comparison

### Community 16 - "controls.py"
Cohesion: 0.09
Nodes (45): Column, DatetimeIndex, pandera_pandas, build_figure(), main(), STORY-501 teaching figure: one month of date-level controls. Writes…, July 2023: quincena, holiday, and organic clicks on the same dates., _assert_matches_panel() (+37 more)

### Community 26 - "test_etl.py"
Cohesion: 0.14
Nodes (25): pandera_errors, align_date_channel_grid(), impute_panel(), load_raw(), DataFrame, Path, Apply locked STORY-103 fill rules on an aligned panel. * Media (``spend``,…, Load → align → impute → validate → write Parquet; return the clean frame. (+17 more)

### Community 31 - "load_client"
Cohesion: 0.06
Nodes (68): STORY-401 Streamlit layout. Sliders and number boxes set the total budget and…, _redact(), _update_insights(), argparse, BaseException, html, parametrize, pathlib (+60 more)

### Community 32 - "Parameter recovery note (STORY-201)"
Cohesion: 0.40
Nodes (4): Estimated iROAS (posterior mean, units per $), Parameter recovery note (STORY-201), Path-C planted signals, Rank comparison

### Community 33 - "pytest"
Cohesion: 0.18
Nodes (6): importlib_util, pytest, fixture, Unit tests for STORY-201 spike helpers (no Meridian MCMC)., spike(), xarray

### Community 36 - "plot_adstock_validation.py"
Cohesion: 0.19
Nodes (14): reports/figures/, STORY-102, Plotly Express over Jupyter for Sprint 1, build_geometric_figure(), build_hill_figure(), build_weibull_figure(), main(), _pulse_frame() (+6 more)

### Community 38 - "transformations.py"
Cohesion: 0.19
Nodes (12): numpy, STORY-102 media transforms (Steps 2–5: adstock + Hill saturation). Pure NumPy…, Choose discrete lag support ``L`` for Weibull PDF weights. Default:…, _weibull_n_lags(), _panel(), ndarray, STORY-102 Step 6 — wall-time gate for transforms on ~2y daily data., Non-negative spend panel shaped ``(channels, days)``. (+4 more)

### Community 39 - "test_transformations.py"
Cohesion: 0.23
Nodes (13): geometric_adstock(), Apply one-parameter geometric adstock along ``axis``. Recurrence (carryover of…, Tests for STORY-102 geometric + Weibull adstock + Hill (Steps 2–4)., 100 then zeros, theta=0.5 → 100, 50, 25, 12.5, …, Shape (channels, T) with axis=-1 adstocks each channel independently., test_2d_channels_by_time(), test_length_preserved(), test_matches_recursive_definition() (+5 more)

### Community 40 - "hill_saturation"
Cohesion: 0.14
Nodes (13): Shared modeling primitives (transforms, Meridian adapter, inference)., hill_saturation(), Hill / Michaelis–Menten saturation mapped to ``[0, 1)``. Form:: y = x^S / (K^S…, At x = K, y ≈ 0.5 for any valid S., Larger S → steeper slope near K (higher |dy/dx| at half-sat)., Negative spend clipped to 0 → response 0 (documented)., test_hill_bounds_in_unit_interval(), test_hill_clips_negative_x() (+5 more)

### Community 41 - "MetricsJsonCurveProvider"
Cohesion: 0.11
Nodes (27): Any, Path, Library entrypoint (also used by tests). Writes JSON when ``out`` is set., run_allocate(), main(), STORY-301 Step 1 — Plotly Express of synthetic fixture response curves. Usage…, optimize_budget(), Allocate spend across channels (maximize KPI or hit a KPI target). Exactly one… (+19 more)

### Community 43 - "allocator.py"
Cohesion: 0.23
Nodes (20): scipy_optimize, _bounds_dict(), _bounds_gate(), _constraints(), _curve_max_spends(), _fail_result(), _feasible_start(), _maximize() (+12 more)

### Community 44 - ".mean_grid"
Cohesion: 0.40
Nodes (3): ndarray, Observed spend knots for ``channel`` (teaching / tests)., Observed mean incremental KPI knots for ``channel``.

### Community 45 - "plot_allocation_teaching.py"
Cohesion: 0.23
Nodes (13): plotly_subplots, _bar_frame(), build_curves_figure(), build_parser(), _curve_frame(), _equal_room_baseline(), main(), ArgumentParser (+5 more)

### Community 47 - "curves.py"
Cohesion: 0.22
Nodes (13): CurveArrays, _extract_means_map(), load_curve_means(), load_curve_means_json(), _looks_like_arrays(), Any, Path, Offline response-curve providers for STORY-301 (Step 1). Reads Meridian… (+5 more)

### Community 48 - "sprint-1-core-data-engine"
Cohesion: 0.13
Nodes (17): github remote, martech-mmm-ai-allocator, mmt-mmm conda env, No leakage, origin remote, sprint-1-core-data-engine, STORY-103, Agentic explain layer (+9 more)

### Community 51 - "view.py"
Cohesion: 0.09
Nodes (46): _client_id(), _commentary(), main(), _clamp_max(), _clamp_min(), STORY-401 dashboard view (min/max bounds + optimizer, no Streamlit)., build_dashboard(), clamp_max_percent() (+38 more)

### Community 53 - "How to test this marketing mix modeling tool"
Cohesion: 0.25
Nodes (7): 1. What you are testing, 2. Install once, 3. Automated test, 4. Dashboard test, no API key, 5. Optional live test, 6. What a good result is not, How to test this marketing mix modeling tool

## Knowledge Gaps
- **58 isolated node(s):** `Estimated iROAS (posterior mean, units per $)`, `Path-C planted signals`, `Rank comparison`, `1. What you are testing`, `2. Install once` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 299 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Path-C synthetic multi-channel marketing panel` connect `generator.py` to `Open gaps registry`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `MetricsJsonCurveProvider` connect `MetricsJsonCurveProvider` to `plot_story_302_concepts.py`, `test_curves.py`, `CurveProvider`, `.mean_grid`, `plot_allocation_teaching.py`, `curves.py`, `view.py`, `load_client`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `load_client()` connect `load_client` to `02_model_spike.py`, `view.py`, `test_qa.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `MetricsJsonCurveProvider` (e.g. with `_bar_frame()` and `build_curves_figure()`) actually correct?**
  _`MetricsJsonCurveProvider` has 24 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Estimated iROAS (posterior mean, units per $)`, `Path-C planted signals`, `Rank comparison` to the rest of the system?**
  _58 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `weibull_adstock` be split into smaller, more focused modules?**
  _Cohesion score 0.14035087719298245 - nodes in this community are weakly interconnected._
- **Should `generator.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06862745098039216 - nodes in this community are weakly interconnected._