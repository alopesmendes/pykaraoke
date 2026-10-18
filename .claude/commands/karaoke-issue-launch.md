---
description: Launch the Requirements of the issue linked to the current branch
argument-hint: "[issue-number]"
model: claude-haiku-5-5
effort: low
---

Launch the work of a GitHub issue, working from the current branch. The issue is the spec, the
draft PR is the plan, the code comes last.

## 1. Find the issue

- If `$ARGUMENTS` is a number, that is the issue.
- Otherwise read the branch: `git branch --show-current`. The issue is the number right after the
  type prefix, e.g. `chore/8-i18n-setup-fr-default-ja-secondary` → `8`.
- If neither gives a number, stop and ask which issue to use.

## 2. Open the draft PR

Delegate to agent `issue-orchestrator`, mode **open**, with the issue number.

- It checks the gate (`status:ready`, current milestone), then the branch, the empty commit, the
  draft PR and the `status:in-progress` label.
- If it refuses, print its refusal and stop. Do not work around the gate.
- If the draft PR already exists, it does nothing new and reports the URL.

## 3. Read the Requirements

- Read only the `## Requirements` section of the issue body. Each `- [ ]` item in it is a task,
  in order. Items elsewhere in the body are not tasks.
- Keep the `**Learn**` section for step 7.
- Print the tasks back as a numbered plan before touching code.

## 4. Validate the tests (stop here)

- Print the Tests checklist from the draft PR: `gh pr view --json body`.
- **Stop.** Ask the user to validate it, or to edit it in the PR. No code is written until they
  say go. This is the plan review.

## 5. Work through the tasks

After the go-ahead, for each Requirement in order:

1. Write the test or tests that prove it first, from the Tests checklist (skill `testing`).
2. Pick the owner from `CLAUDE.md` → "Where to look" (models, views, templates, settings, docs).
3. Make the change. Business logic goes in `services.py`. User-facing strings go through i18n.
4. Run the tests for it. When they pass, have `issue-orchestrator` (mode **sync**) tick its
   Tests item and the Requirement.
5. Note anything that could not be done, and why. Do not skip silently.

Settings and i18n tasks: keep to the issue's wording. Do not add languages or middleware it does
not name.

## 6. Verify

- Run `make check` (lint + tests + audit). If it fails, fix the cause, then rerun.
- Run the `verifier` agent on the result when the batch is large.
- Update the owning doc and `CHANGELOG.md` under `## [Unreleased]` for each behaviour change
  (table in skill `docs-writing`).

## 7. Close out

- Run `/learning-checklist` for the feature (required by `CLAUDE.md`).
- Report: Requirements done, Requirements left, check output, files changed, PR URL.
- Do not commit, push or mark the PR ready here. That is `/commit-push-pr`, which hands the
  ready step to `issue-orchestrator`.
- Do not edit the issue body beyond the checkboxes.
