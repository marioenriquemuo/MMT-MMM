# Learnings

Durable story learnings and the single registry of **open gaps** for future review and Sprint planning.

| File | Role |
| --- | --- |
| [`open-gaps.md`](open-gaps.md) | Registry of every current open gap (status, evidence, done criteria) |
| [`story-201-meridian.md`](story-201-meridian.md) | STORY-201 Meridian spike learnings + rank-recovery deep dive |

## Open gaps before Sprint 3

Use [`open-gaps.md`](open-gaps.md) as the checklist. At tip `188e496` (pre-registry), the open set is:

- [ ] `GAP-201-RANK` — Meridian iROAS rank vs Path-C (Spearman ≈ −0.6)
- [ ] `GAP-402-LOOM` — README Loom walkthrough still a placeholder
- [ ] `GAP-402-RENAME` — GitHub remote is still `marioenriquemuo/MMT-MMM` (not `martech-mmm-ai-allocator`)
- [x] `GAP-402-VISIBILITY` — closed 2026-10-14; GitHub `marioenriquemuo/MMT-MMM` is public
- [ ] `GAP-402-DOCKERIGNORE` — `.dockerignore` omits `.pytest_cache` / `.cursor` (Low)
- [ ] `GAP-COMM-KPI` — standing communication caveat: incremental KPI ≠ revenue dollars

Do not invent gaps here. Add a row only when README, CLAUDE/AGENTS, a learning doc, metrics, or a Bugbot review already evidences it.
