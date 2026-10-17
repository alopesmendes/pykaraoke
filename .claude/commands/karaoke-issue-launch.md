---
description: Launch every task of the issue linked to the current branch
argument-hint: "[issue-number]"
---

Launch all the tasks of a GitHub issue, working from the current branch.

## 1. Find the issue

- If `$ARGUMENTS` is a number, that is the issue.
- Otherwise read the branch: `git branch --show-current`. The issue is the number right after the
  type prefix, e.g. `chore/8-i18n-setup-fr-default-ja-secondary` → `8`.
- If neither gives a number, stop and ask which issue to use.

Fetch it: `gh issue view <number> --json number,title,body`.

## 2. Read the tasks

- Every unchecked item `- [ ] ...` in the issue body is a task, in order.
- Ignore the `**Learn**` section for work, but keep it for step 5.
- Print the task list back as a numbered plan before touching code.

## 3. Work through the tasks

For each unchecked task, in order:

1. Pick the owner from `CLAUDE.md` → "Where to look" (models, views, templates, settings, docs).
2. Make the change. Business logic goes in `services.py`. User-facing strings go through i18n.
3. Tick the item in the issue body only after the change is in place and checked.
4. Note anything that could not be done, and why. Do not skip silently.

Settings and i18n tasks: keep to the issue's wording. Do not add languages or middleware it does not name.

## 4. Verify

- Run `make check` (lint + tests + audit). If it fails, fix the cause, then rerun.
- Run the `verifier` agent on the result when the batch is large.
- Update the owning doc and `CHANGELOG.md` under `## [Unreleased]` for each behaviour change.

## 5. Close out

- Run `/learning-checklist` for the feature (required by `CLAUDE.md`).
- Report: tasks done, tasks left, check output, files changed.
- Do not commit or push unless the user asks. Do not edit the issue body beyond the checkboxes.
