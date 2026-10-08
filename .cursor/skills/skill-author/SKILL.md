---
name: skill-author
description: >-
  Authors Cursor Agent Skills using the open Agent Skills (SKILL.md) format.
  Use when the user asks to create a skill, write SKILL.md, package workflows
  for the agent, or mentions agentskills / Agent Skills specification.
---

# Skill author (Agent Skills format)

## When to use

The user wants a new reusable agent skill (instructions the agent loads on demand).

## Where to put skills in Cursor

| Scope | Path |
| --- | --- |
| Personal (all projects) | `~/.cursor/skills/<skill-name>/SKILL.md` |
| This repo only | `.cursor/skills/<skill-name>/SKILL.md` |

Never write into `~/.cursor/skills-cursor/` (Cursor built-ins).

## Required shape

```text
skill-name/
├── SKILL.md          # required
├── references/       # optional docs
├── scripts/          # optional helpers
└── assets/           # optional templates
```

`SKILL.md` frontmatter (minimum):

```yaml
---
name: skill-name          # lowercase, hyphens, max 64 chars
description: >-           # WHAT + WHEN; third person; max 1024 chars
  Does X. Use when the user mentions Y or asks to Z.
---
```

Default: set `disable-model-invocation: true` unless the skill should auto-attach from ambient context.

## Spec

Follow https://agentskills.io/specification and https://agentskills.io for progressive disclosure (name/description always; full body only when activated).

## Checklist before finishing

1. `name` + `description` present and trigger-rich
2. Instructions are step-by-step and testable
3. No secrets in the skill files
4. Skill lives under `~/.cursor/skills/` or `.cursor/skills/`, not `skills-cursor`
