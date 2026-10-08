# CLAUDE.md — MMT&MMM

Working brief for Claude/Cursor on **martech-mmm-ai-allocator** (Origin: `mario-mu-oz-dev/MMT-MMM`).

## Quick facts

| Item | Value |
| --- | --- |
| Product | Enterprise measurement + budget allocation (Bayesian MMM + touchpoint calibration) |
| Local path | `/home/mario/dev/MMT&MMM` |
| Language | Python 3.12 |
| Env | Conda env `mmt-mmm` from `environment.yml` (Miniconda at `~/miniconda3`) |
| Core libs | numpy, pandas, scipy, scikit-learn, pymc, arviz, matplotlib, jupyter, pyyaml, pydantic |
| Secrets | `Secret/` gitignored — never read into commits or paste into PRs |
| Docker | Later (deploy/CI); not required for local MMM work |
| Status | Early scaffold — env + agent docs; model code still to land |

## What we build

1. **Top-down Bayesian MMM** — decay, saturation, incremental lift; continuous updates from new performance data
2. **Bottom-up calibration** — touchpoint / funnel signals that keep the MMM honest vs platform attribution windows
3. **Allocator layer** — optimization scripts that turn posteriors into budget recommendations
4. **Agentic explain layer** — orchestrates scripts and narrates statistical outputs for C-suite (LLMs do not replace the Bayesian math)

## Layout (current)

```
MMT&MMM/
├── environment.yml      # conda env mmt-mmm
├── README.md            # setup + overview
├── CLAUDE.md            # this file
├── AGENTS.md            # agent entrypoint
├── .python-version      # 3.12
├── .gitignore           # includes Secret/, conda/python junk
├── Secret/              # local-only (gitignored)
└── .cursor/             # skills + rules (when present on branch)
```

## Key conventions

- Prefer Miniconda env `mmt-mmm`; do not install project packages into conda `base`
- Keep `environment.yml` lean — add deps when code needs them, not “just in case”
- No look-ahead / leakage in measurement: features and targets must be point-in-time honest
- Flag assumptions that inflate incremental lift or ROI
- Secrets stay in `Secret/`; document only that the folder is gitignored
- Small PRs; update `README.md` / `CLAUDE.md` / `AGENTS.md` when layout or env changes

## Activate and smoke-test

```bash
cd "/home/mario/dev/MMT&MMM"
conda activate mmt-mmm
python -c "import numpy, pandas, scipy, sklearn, pymc, arviz, matplotlib, yaml, pydantic; print('ok', pymc.__version__)"
```

See `AGENTS.md` for agent golden rules and the skills/rules index.
