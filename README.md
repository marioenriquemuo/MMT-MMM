# MMT&MMM — martech-mmm-ai-allocator

Enterprise measurement and optimization engine: Unified Measurement Architecture that fuses top-down Bayesian Marketing Mix Modeling (MMM) with bottom-up touchpoint calibration, then turns incremental-lift estimates into plain-English budget allocation strategies.

## Product (short)

- Replaces platform-biased attribution windows with a unified measurement layer
- Learns decay, saturation, and incremental lift for segmented campaigns across the funnel
- Continuous Bayesian updating from new performance data (statistics, not LLMs doing the math)
- Agentic AI layer orchestrates Python optimization scripts and explains outputs for C-suite decisions

## Local workspace

| Item | Value |
| --- | --- |
| Path | `/home/mario/dev/MMT&MMM` (quote the `&` in shells) |
| Origin | [MMT-MMM](https://cursor.com/codebase/mario-mu-oz-dev/MMT-MMM) (private) — remote `origin` |
| GitHub | [MMT-MMM](https://github.com/marioenriquemuo/MMT-MMM) (private) — remote `github`; tip: `git push github main` |
| Secrets | `Secret/` — **gitignored; never commit** |
| Python env | Miniconda env `mmt-mmm` via `environment.yml` |
| Docker | Later (deploy/CI only) |

## Local setup (Miniconda)

Requires [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (or micromamba) on `PATH`. On Mario’s machine: `~/miniconda3` (`conda` 26.x).

```bash
cd "/home/mario/dev/MMT&MMM"

# Create the env (once)
conda env create -f environment.yml

# Activate
conda activate mmt-mmm

# Verify key imports
python -c "import numpy, pandas, scipy, sklearn, pymc, arviz, matplotlib, yaml, pydantic; print('ok', pymc.__version__)"
```

Recreate or refresh deps: `conda env update -f environment.yml --prune`.

Env name and Python pin: `mmt-mmm` / 3.12 (see `environment.yml`, `.python-version`).

## Docs for humans and agents

| File | Role |
| --- | --- |
| `README.md` | This overview + setup |
| `CLAUDE.md` | Project brief and conventions for Claude/Cursor |
| `AGENTS.md` | Agent entrypoint: layout, golden rules, skills/rules index |

## Skills, rules, and PRs

- Project Agent Skills: `.cursor/skills/*/SKILL.md` (see `AGENTS.md`)
- Always-on Cursor rules: `.cursor/rules/*.mdc`
- Prefer small feature branches (`cursor/<topic>-…`), focused commits, Origin PRs into `main`
- Never commit `Secret/`, credentials, or local conda env directories

## Stack direction

Python Bayesian MMM + optimization scripts (`pymc` / scientific stack in `environment.yml`). Docker is deferred; local work uses the conda env only.
