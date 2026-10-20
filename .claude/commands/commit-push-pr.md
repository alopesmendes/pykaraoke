---
description: Commit the current work, push the branch and mark its draft PR ready for review
argument-hint: "[commit subject, optional]"
model: claude-haiku-5-5
effort: low
---

Ship the current branch: check, commit, push, mark the draft PR ready. The draft PR was opened
by `/karaoke-issue-launch` before any code, so this command never opens a new PR. Stop at the
first failing step and report it.

## 1. Check the branch

- Run `git branch --show-current` and `git status --short`.
- If the branch is `master`, stop and ask for a branch name. Do not commit on `master`.
- If there are no changes and no commits ahead of `master`, stop: nothing to ship.
- The issue number is the digits after the type prefix, e.g. `chore/11-learning-checklist-...` → `11`.
  If there is none, ask for it.
- Find the draft PR: `gh pr view --json number,url,isDraft`. If there is none, stop and say to run
  `/karaoke-issue-launch` first. The draft is the plan; do not make a PR without it.

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

## 5. Check the Requirements in the PR

Ready needs every box ticked. Ticks come from the orchestrator, so this step proves each item first.

1. Read the list to check: `gh pr view --json body` (Accept criteria and Tests) and
   `gh issue view N --json body` (the `## Requirements` section). Match each Requirement to its
   Tests line in the PR, the line that names the test proving it.
2. For each Requirement, check the evidence in the working tree, not the box:
   - Automated Tests line: run that test (`uv run pytest <path>::<name>` or `-k`). Pass or fail.
   - Non-test Requirement (settings, docs, CHANGELOG, agent or command file): check the file
     directly, for example the line the Requirement names exists and reads as the issue says.
   - Manual check, with no automated test: do not decide it yourself. Ask the user to confirm it
     passed, and wait for the answer.
3. Build a table: Requirement | Tests line | evidence | pass / fail / needs confirmation.
4. Passing items: delegate to `issue-orchestrator`, mode **sync**, with the Requirement texts that
   passed and the Tests lines that passed. It ticks the boxes; this command does not.
5. Any fail: stop, print the table, and do not tick or mark ready.
6. Once every Requirement and Tests line is ticked: delegate to `issue-orchestrator`, mode
   **ready**, with the PR number and the `make check` green report. It refuses if anything is
   still unticked, and names it.
7. If the PR is already ready, the orchestrator reports it and changes nothing.
8. The PR body is not rewritten here. It was generated from the issue when the draft was opened.

## 6. Report

- Print the PR URL, the commit SHA, the `make check` result line, and whether the PR is now ready.
- Note anything left open: unticked Requirements or Tests, a missing learning checklist, a skipped step.
