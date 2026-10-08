# AGENTS.md — MMT&MMM

Working guide for AI agents in this Origin repo (`mario-mu-oz-dev/MMT-MMM`).
Read `CLAUDE.md` and `README.md` before changing layout, env, or measurement code.

## What this repo is

**martech-mmm-ai-allocator** — Bayesian Marketing Mix Modeling fused with touchpoint calibration and an agentic layer that turns statistical outputs into budget allocation strategies.

Not a trading lab. Do not import forex-research lab protocol, DSR gates, or BacktestEngine conventions here.

## Golden rules

1. **Accuracy over agreement.** Challenge weak lift / ROI claims; cite data windows and model assumptions.
2. **No leakage.** Features, media, and outcomes must be point-in-time; never use future spend or conversions to fit today’s effect.
3. **Stats do the math.** LLMs orchestrate and explain; PyMC (or agreed Bayesian stack) estimates effects.
4. **Lean env.** Change `environment.yml` only when code needs a package; never pollute conda `base`.
5. **Secrets.** `Secret/` is local-only and **gitignored** — never commit, never paste into PRs or docs beyond “gitignored, never commit”.
6. **Small diffs.** Prefer surgical PRs; update these docs when paths or setup change.

## Layout agents should know

| Path | Role |
| --- | --- |
| `/home/mario/dev/MMT&MMM` | Canonical local checkout (quote the `&`) |
| `environment.yml` | Conda env `mmt-mmm` (Python 3.12 + Bayesian MMM baseline) |
| `README.md` | Human overview + Miniconda setup |
| `CLAUDE.md` | Project brief / conventions |
| `AGENTS.md` | This file — agent entrypoint |
| `.cursor/skills/` | Project Agent Skills (`SKILL.md` per skill) |
| `.cursor/rules/` | Always-on Cursor rules (`.mdc`) |
| `Secret/` | Local-only; **gitignored** — never commit |

## Skills

Cursor discovers project skills from `.cursor/skills/*/SKILL.md`.

Expected set (may land via a separate skills PR if not on your branch yet):

- Shared: `ponytail`, `ponytail-*`, `graphify`, `eli5-teacher`, `skill-author`, `text-review-documentation`
- Project: `mmt-mmm`, `secret-hygiene`
- Diagrams: `archify` (via `npx skills add`)

## Rules

Generic behavioral rules under `.cursor/rules/` (simplicity, terse comms, get-shit-done, Karpathy guidelines, graphify orientation, secret hygiene) — adapted without forex lab locks.

## PR conventions

- Branch from `main`: `cursor/<short-topic>-…`
- One concern per PR when practical (env, docs, model code)
- Origin remote: `https://origin.cursor.com/mario-mu-oz-dev/MMT-MMM.git`
- Do not commit `Secret/`, `.conda/`, `*.egg-info/`, or notebook checkpoints

## Local env

```bash
cd "/home/mario/dev/MMT&MMM"
conda env create -f environment.yml   # once
conda activate mmt-mmm
python -c "import numpy, pandas, scipy, sklearn, pymc, arviz, matplotlib, yaml, pydantic; print('ok', pymc.__version__)"
```

## Definition of done (agent tasks)

- [ ] Edited Python compiles / smoke imports pass in `mmt-mmm`
- [ ] No secrets or conda env trees committed
- [ ] `README.md` / `CLAUDE.md` / `AGENTS.md` updated if layout or setup changed
- [ ] Leakage / assumption risks called out when touching measurement code
