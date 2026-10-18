---
description: Commit the current work, push the branch and open a PR against master
argument-hint: "[commit subject, optional]"
---

Ship the current branch: check, commit, push, open a PR. Stop at the first failing step and report it.

## 1. Check the branch

- Run `git branch --show-current` and `git status --short`.
- If the branch is `master`, stop and ask for a branch name. Do not commit on `master`.
- If there are no changes and no commits ahead of `master`, stop: nothing to ship.
- The issue number is the digits after the type prefix, e.g. `chore/11-learning-checklist-...` → `11`.
  If there is none, ask for it, or use `#` unnumbered.

## 2. Run the gate

- Run `make check` (lint, tests, audit). If it fails, fix the cause, then rerun. Do not commit red.

## 3. Commit

- Stage by name, never `git add -A` or `git add .`. Never stage `.env` or anything outside the change.
- Commit subject: `type(#N): summary`, lowercase, imperative, 50 chars or fewer. Use `$ARGUMENTS`
  as the summary when given.
- Body: wrap at about 72 columns; say why in one or two sentences. Skip the body if the subject says it all.
- End the message with the attribution line:

```
Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>
```

Use a HEREDOC so the message keeps its line breaks:

```bash
git commit -F - <<'EOF'
chore(#11): subject here

Why paragraph here.

Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>
EOF
```

## 4. Push

- `git push -u origin HEAD`. Never `--force`. If the push is refused, stop and report; do not rebase.

## 5. Open the PR

- Skip if a PR for this branch already exists: `gh pr view --json url`. Print its URL instead.
- Title: the commit subject, e.g. `chore(#11): add learning checklist for milestone 1`.
- Body follows `.github/pull_request_template.md`: `## What`, `## Why`, `## Checklist`.
  Fill the checklist from what is true; leave an unticked box unticked and say why in the body.
- Close with the attribution line:

```
🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

Create it against `master`:

```bash
gh pr create --base master --title "<title>" --body "$(cat <<'EOF'
## What

...

## Why

...

## Checklist
- [x] `make check` passes
- [ ] Docs updated (if behaviour changed)
- [ ] Learning checklist updated (`docs/learning/`)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## 6. Report

- Print the PR URL, the commit SHA, and the `make check` result line.
- Note anything left open: unticked checklist items, a missing learning checklist, a skipped step.
