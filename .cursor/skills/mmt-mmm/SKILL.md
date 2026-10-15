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

## Agent skills

Use `~/.cursor/skills/` when the skill already exists there. Do not copy it into this repo.

User skills (global): `ponytail` (+ audit/debt/gain/help/review), `graphify`, `eli5-teacher`, `skill-author`, `text-review-documentation`, `ai-workstation-advisor`.

Project skills under `.cursor/skills/<name>/SKILL.md`:

- `mmt-mmm` (this file)
- `secret-hygiene`
- `archify` — https://github.com/tt-a1i/archify (not in `~/.cursor/skills/`)

## Rules companion

Generic rules: `~/.cursor/rules/` (do not copy them here).
Repo-only: `.cursor/rules/graphify.mdc`, `.cursor/rules/secret-hygiene.mdc`.
