# Open gaps registry

Single list of **current open gaps** for Sprint planning and future review.
Only items evidenced in-repo or in Project-store Bugbot/DoD notes. Status values: `open` | `closed`.

Baseline tip when this registry was first filled: `188e496` (Merge STORY-402 public-ready packaging).
Index: [`README.md`](README.md).

---

## GAP-201-RANK

| Field | Value |
| --- | --- |
| Story | STORY-201 |
| Status | `open` |
| Severity | High (measurement correctness vs Path-C ground truth) |
| Description | Meridian posterior iROAS channel order disagrees with Path-C contribution / `media_beta` order. Speaks to whether posteriors (and downstream allocator curves) recover planted channel strength. |
| Evidence | Deep dive: [`story-201-meridian.md`](story-201-meridian.md). Metrics at tip `188e496`: `reports/metrics.json` → `recovery_spearman: -0.6`, `dod.directional_recovery: false`. Also `reports/parameter_recovery.md`, README / CLAUDE / AGENTS / `data/raw/DATA_CARD.md` open-issue callouts. |
| Done when | A later recovery/calibration story produces documented channel-rank agreement (or an explicit accepted definitional mismatch with updated DoD), and this gap is closed with a citation to the new evidence. |

---

## GAP-402-LOOM

| Field | Value |
| --- | --- |
| Story | STORY-402 |
| Status | `open` |
| Severity | Medium (portfolio DoD gap; intentional) |
| Description | README still has a placeholder instead of a real 2-minute Loom walkthrough URL. |
| Evidence | `README.md` line: `Walkthrough: add a 2-minute Loom URL here.` Bugbot: Project store `docs/story-402-bugbot.md` (reviewed tip `188e496`) — DoD #2 PASS with gap. |
| Done when | Placeholder replaced with a working Loom (or equivalent) URL that demos the dashboard in ~2 minutes. |

---

## GAP-402-RENAME

| Field | Value |
| --- | --- |
| Story | STORY-402 |
| Status | `open` |
| Severity | Medium (portfolio DoD gap; intentional) |
| Description | Product name in prose is `martech-mmm-ai-allocator`, but the GitHub remote repo is still `marioenriquemuo/MMT-MMM`, not renamed to `marioenriquemuo/martech-mmm-ai-allocator`. |
| Evidence | `git remote -v` → `github` = `https://github.com/marioenriquemuo/MMT-MMM.git`. README Local workspace table + AGENTS remotes table. Bugbot `docs/story-402-bugbot.md` DoD #4 PASS with gap / intentional gap #1. |
| Done when | GitHub repository exists as `marioenriquemuo/martech-mmm-ai-allocator` (or remotes/docs updated to the chosen canonical name) without breaking dual-remote push. |

---

## GAP-402-VISIBILITY

| Field | Value |
| --- | --- |
| Story | STORY-402 |
| Status | `closed` (2026-10-14) |
| Severity | Medium (portfolio DoD gap; intentional) |
| Description | GitHub mirror was private; STORY-402 DoD asked for a public-ready publish path. Mario confirmed publish — repo is public. Rename remains a separate open gap (`GAP-402-RENAME`). |
| Evidence | GitHub public API `GET https://api.github.com/repos/marioenriquemuo/MMT-MMM` → `"private": false`, `full_name: marioenriquemuo/MMT-MMM`. README Local workspace table updated to public. Prior: Bugbot `docs/story-402-bugbot.md` intentional gap #3 at tip `188e496`. |
| Done when | Mario explicitly publishes (or documents a permanent private decision) and README/AGENTS visibility wording matches reality. **Met** 2026-10-14. |

---

## GAP-402-DOCKERIGNORE

| Field | Value |
| --- | --- |
| Story | STORY-402 |
| Status | `open` |
| Severity | Low (optional housekeeping; not DoD-blocking) |
| Description | `.dockerignore` excludes `Secret/`, `.git`, `.env`, `__pycache__`, `.conda`, but not `.pytest_cache` or `.cursor`. `Dockerfile` `COPY .` can still ship those into the image (noise/size only; not a secret leak). |
| Evidence | `.dockerignore` contents at tip `188e496`. Bugbot `docs/story-402-bugbot.md` optional Low finding. |
| Done when | `.dockerignore` lists `.pytest_cache` and `.cursor` (or equivalent), and a rebuild confirms they are absent from the image context. |

---

## GAP-COMM-KPI

| Field | Value |
| --- | --- |
| Story | Cross-cutting (STORY-301 / 302 / 401 / 402 communication) |
| Status | `open` |
| Severity | Standing caveat (measurement communication, not a code bug) |
| Description | Dashboard, briefs, and README figures are **incremental KPI**, not currency and not client revenue. Easy to misread as ROI dollars. Kept open so Sprint 3+ copy and UI keep the disclaimer visible until product language deliberately changes. |
| Evidence | README intro + STORY-301/302/401 caveats; CLAUDE Sprint 2 note (“Numbers are incremental KPI, not revenue”); AGENTS story caveats; Bugbot packaging review did not close this. |
| Done when | Either (a) product surfaces consistently prevent revenue/$ misreads and the caveat is retired as “handled,” or (b) a later story deliberately redefines output units and updates all user-facing copy. |

---

## Closed / not listed

- `GAP-402-VISIBILITY` — closed 2026-10-14; GitHub `marioenriquemuo/MMT-MMM` is public (`"private": false` via public API). See entry above. `GAP-402-RENAME` stays open.
- STORY-402 packaging paths (`app/streamlit_app.py`, `Dockerfile`, `LICENSE`, `requirements.txt`, `.env.example`, `docs/how-to-test.md`) — Bugbot PASS at `188e496`.
- Secret hygiene — Bugbot scanned clean; not an open gap.
- No other unfinished items were marked `open` in `docs/learnings/` beyond GAP-201-RANK’s deep dive.
