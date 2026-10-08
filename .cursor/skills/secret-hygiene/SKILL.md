---
name: secret-hygiene
description: >-
  Keep local Secret/ and credentials out of git and agent deliverables in
  MMT&MMM. Use when committing, opening PRs, writing docs, or handling sprint
  files, API keys, or anything under Secret/.
---

# Secret hygiene (MMT&MMM)

## Hard rules

1. Do not `git add` `Secret/`, files under it, or copies of their contents.
2. Confirm ignore: `git check-ignore -v Secret/` should match `/Secret/` in `.gitignore`.
3. Before every commit, run `git status` and `git diff --cached` — abort if any secret path appears.
4. Do not paste secret file contents into commits, PR bodies, README, skills, or Project store docs.
5. Prefer referring to secrets by path (`Secret/…`) rather than quoting values.

## If a secret was staged by mistake

```bash
git reset HEAD -- Secret/
# or unstage specific files, then confirm they remain ignored
git status
git check-ignore -v Secret/
```

Do not push until the index is clean of secrets.
