---
name: mmt-mmm
description: >-
  Project conventions for the MMT&MMM (martech MMM) Origin repo at
  /home/mario/dev/MMT&MMM. Use when working in this repository, setting up
  agents, planning sprints, or deciding what belongs in git vs local-only paths.
---

# MMT&MMM project conventions

## Paths

- Working directory on Mario’s machine: `/home/mario/dev/MMT&MMM` (quote the path — it contains `&`).
- Origin repo: `mario-mu-oz-dev/MMT-MMM`
- Browse: https://cursor.com/codebase/mario-mu-oz-dev/MMT-MMM

## Secrets

- Local `Secret/` is **gitignored** (`/Secret/` in `.gitignore`).
- Never stage, commit, push, or paste `Secret/` contents into PRs, cards, or chat logs.
- Treat sprint JSON and credentials under `Secret/` as machine-local only.

## Agent skills in this repo

Project skills live under `.cursor/skills/<name>/SKILL.md` (Cursor discovers them automatically).

Shared tooling vendored from Mario’s user skills (same set forex-research relies on via `~/.cursor/skills/`):

- `ponytail` (+ audit/debt/gain/help/review)
- `graphify`
- `eli5-teacher`
- `skill-author`
- `text-review-documentation`

Installed from GitHub:

- `archify` — https://github.com/tt-a1i/archify (`npx skills add tt-a1i/archify --skill archify --agent cursor --copy --yes`, then moved into `.cursor/skills/`)

Project-specific:

- `mmt-mmm` (this file)
- `secret-hygiene`

## Rules companion

Always-on agent rules live in `.cursor/rules/*.mdc` (simplicity, terse comms, Karpathy guidelines, graphify orientation, secret hygiene).
