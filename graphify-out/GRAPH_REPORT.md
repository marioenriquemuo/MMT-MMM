# Graph Report - workspace  (2026-10-08)

## Corpus Check
- Corpus is ~7,488 words - fits in a single context window. You may not need a graph.

## Summary
- 89 nodes · 158 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- STORY-101 Generator Core
- MMM Product & Agents
- Ponytail Review Skills
- Generator Pytest Suite
- CSV Roundtrip Tests
- ELI5 & Doc Standards
- DATA_CARD & KPI Rules
- Ground Truth Writers

## God Nodes (most connected - your core abstractions)
1. `generate()` - 23 edges
2. `_baseline_sales()` - 8 edges
3. `assert_valid()` - 8 edges
4. `write_outputs()` - 8 edges
5. `test_write_outputs_roundtrip()` - 7 edges
6. `MMT&MMM Project Conventions` - 7 edges
7. `Ponytail Help` - 6 edges
8. `Ponytail` - 6 edges
9. `Agent Golden Rules` - 6 edges
10. `geometric_adstock()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `No Look-Ahead / Leakage Rule` --semantically_similar_to--> `baseline_sales KPI`  [INFERRED] [semantically similar]
  AGENTS.md → data/raw/DATA_CARD.md
- `test_baseline_sales_repeated_per_date()` --calls--> `generate()`  [EXTRACTED]
  tests/test_generator.py → src/data/generator.py
- `test_bounds_non_negative_no_nulls()` --calls--> `generate()`  [EXTRACTED]
  tests/test_generator.py → src/data/generator.py
- `test_committed_csv_matches_generator()` --calls--> `generate()`  [EXTRACTED]
  tests/test_generator.py → src/data/generator.py
- `test_different_seed_changes_output()` --calls--> `generate()`  [EXTRACTED]
  tests/test_generator.py → src/data/generator.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Ponytail Skill Suite** — _cursor_skills_ponytail_skill_ponytail, _cursor_skills_ponytail_review_skill_ponytail_review, _cursor_skills_ponytail_audit_skill_ponytail_audit, _cursor_skills_ponytail_debt_skill_ponytail_debt, _cursor_skills_ponytail_gain_skill_ponytail_gain, _cursor_skills_ponytail_help_skill_ponytail_help [EXTRACTED 1.00]
- **Bayesian MMM Measurement Stack** — claude_top_down_bayesian_mmm, claude_bottom_up_calibration, claude_allocator_layer, claude_agentic_explain_layer [EXTRACTED 1.00]
- **Secret Hygiene Across Project Docs** — _cursor_skills_secret_hygiene_skill_secret_hygiene, _cursor_skills_mmt_mmm_skill_secret_folder, agents_golden_rules [INFERRED 0.85]

## Communities (10 total, 2 thin omitted)

### Community 0 - "STORY-101 Generator Core"
Cohesion: 0.17
Nodes (7): assert_valid(), _baseline_sales(), coerce_integer_columns(), geometric_adstock(), hill_saturation(), _impressions_clicks(), _spend_series()

### Community 1 - "MMM Product & Agents"
Cohesion: 0.21
Nodes (15): archify Skill, MMT&MMM Project Conventions, Secret/ Local-Only Path, Secret Hygiene, Agent Skills SKILL.md Format, Skill Author, .cursor/skills/ Project Skills Layout, martech-mmm-ai-allocator (+7 more)

### Community 2 - "Ponytail Review Skills"
Cohesion: 0.27
Nodes (11): Ponytail Audit, ponytail: Comment Marker, Ponytail Debt, Ponytail Benchmark Medians, Ponytail Gain, Ponytail Intensity Levels (lite/full/ultra), Ponytail Help, Over-Engineering Review Tags (+3 more)

### Community 3 - "Generator Pytest Suite"
Cohesion: 0.27
Nodes (8): generate(), test_baseline_sales_repeated_per_date(), test_bounds_non_negative_no_nulls(), test_different_seed_changes_output(), test_ground_truth_documents_integer_postprocess(), test_integer_count_columns(), test_schema_and_shape(), test_seed_stability()

### Community 4 - "CSV Roundtrip Tests"
Cohesion: 0.33
Nodes (3): test_committed_csv_matches_generator(), test_committed_ground_truth_has_planted_params(), test_write_outputs_roundtrip()

### Community 5 - "ELI5 & Doc Standards"
Cohesion: 0.33
Nodes (5): ELI5 Teacher, AI Slop Writing Artifacts, 6th-Grade Flesch-Kincaid Target, NarraBench / StoryScope (arXiv:2604.03136), Text Review & Documentation Standards

### Community 6 - "DATA_CARD & KPI Rules"
Cohesion: 0.47
Nodes (6): No Look-Ahead / Leakage Rule, baseline_sales KPI, Channel-Day Grain, DATA_CARD for synthetic_ad_spend.csv, STORY-101 Path-C Synthetic Generator, synthetic_ad_spend.csv

### Community 7 - "Ground Truth Writers"
Cohesion: 0.33
Nodes (3): main(), planted_ground_truth(), write_outputs()

## Knowledge Gaps
- **3 isolated node(s):** `archify Skill`, `Ponytail Benchmark Medians`, `AI Slop Writing Artifacts`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 21 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `generate()` connect `Generator Pytest Suite` to `STORY-101 Generator Core`, `CSV Roundtrip Tests`, `Ground Truth Writers`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **What connects `archify Skill`, `Ponytail Benchmark Medians`, `AI Slop Writing Artifacts` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `Ponytail` connect `Ponytail Review Skills` to `MMM Product & Agents`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `MMT&MMM Project Conventions` connect `MMM Product & Agents` to `Ponytail Review Skills`, `ELI5 & Doc Standards`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._