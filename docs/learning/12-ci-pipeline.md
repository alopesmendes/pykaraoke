---
name: ci-pipeline
description: One CI workflow with chained stages, separate deploy workflows gated on CI, and coverage jobs with split permissions
branch: chore/31-split-ci-cd-into-build-lint-test-analysis-security
issue: 31
tools: Read, Glob, Grep, Bash, Edit, Write
model: claude-sonnet-5-5
effort: medium
memory: none
level: beginner
---

# 12: One CI pipeline with chained stages

*What to learn from the CI rework. Milestone 1.*

**Shipped:** `ci.yml` runs BUILD, LINT, TEST, ANALYSIS/SECURITY, pip-audit and coverage. `deploy-dev.yml`
deploys after a green CI on master. `deploy-prod.yml` is a manual run that checks CI first.
**Files:** `.github/workflows/ci.yml`, `deploy-dev.yml`, `deploy-prod.yml`, `tests/test_ci_workflow.py`,
`pyproject.toml`, `Makefile`

---

## Concepts

- **`needs:` and job results**: a job runs after its `needs:` jobs finish. If one failed, the next
  is skipped unless its `if:` says otherwise. `needs.<job>.result` reads the outcome. Without
  `needs:`, the jobs run in parallel and a red lint does not stop the tests.
- **`!cancelled()` vs `always()`**: `always()` runs a job even after the run was cancelled.
  `!cancelled()` runs it after failures but not after a cancel. Deploys use `!cancelled()`.
- **`workflow_run` trigger**: a workflow that starts when another one completes. It runs the
  workflow file from the default branch, and `github.sha` is the default branch tip, not the commit
  that was tested. Use `github.event.workflow_run.head_sha` for the tested commit.
- **Token permissions per job**: `permissions:` sets the token scope for one job. Only the jobs that
  push get `contents: write`. Jobs that run project code stay read-only, so a bad dependency never
  holds a write token.
- **Artifacts skip dotfiles**: `upload-artifact` ignores hidden files unless
  `include-hidden-files: true`. `.coverage` is hidden, so without it the comment job has no data.

## Docs to read

- [ ] [Workflow syntax: `jobs.<job_id>.needs`](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#jobsjob_idneeds). The chain rule.
- [ ] [Expressions: status check functions](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/evaluate-expressions-in-workflows-or-actions#status-check-functions). `always()`, `cancelled()`.
- [ ] [Events: `workflow_run`](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/events-that-trigger-workflows#workflow_run). Why `head_sha` matters.
- [ ] [Django: staticfiles storage](https://docs.djangoproject.com/en/6.1/ref/contrib/staticfiles/#manifeststaticfilesstorage). Why the manifest must exist before the tests run.

## Hands-on

Do these in this repo, without Claude.

- [ ] Open `ci.yml` and list every job, its `needs:`, and its `permissions:`. Say which jobs can write.
- [ ] Remove the `Collect static files` step from the TEST job on a scratch branch. Push it and read which test fails and why.
- [ ] Run `make check` with `staticfiles/` deleted. Then run it again. Explain why the first run failed.
- [ ] Delete `include-hidden-files: true` on a scratch branch and read the upload log. Explain what is missing.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. A job has `needs: [lint]` and lint fails. Does the job run?
   <details><summary>Answer</summary>No. It is skipped, unless its `if:` uses a status function such as `always()` or `!cancelled()`.</details>
2. Why does `deploy-dev.yml` check out `workflow_run.head_sha` instead of the default checkout?
   <details><summary>Answer</summary>The workflow runs on the master tip. If master moved after CI started, the default checkout would tag a commit CI never tested.</details>
3. Why is `if: always()` wrong on a deploy job?
   <details><summary>Answer</summary>It also runs after the whole run was cancelled, so a cancelled pipeline could still reach the deploy.</details>
4. Why does `ci.yml` not run `collectstatic` once and share the output with TEST?
   <details><summary>Answer</summary>Each job runs on its own runner with a fresh checkout. Files written by BUILD do not exist in TEST.</details>
5. The coverage comment job runs no project code. Why does that allow `pull-requests: write` without risk?
   <details><summary>Answer</summary>Untrusted code cannot run with the token. The only code that runs is the pinned coverage action.</details>

## Gotchas hit

- **TEST failed in CI, passed locally** → TEST never ran `collectstatic`, and the prod-settings test needs the manifest. Locally a leftover `staticfiles/` hid it → TEST now runs `collectstatic` first, and `make check` runs it before `test`.
- **`sed -i` with no file name silently did nothing and stopped the chain** → I wrote the command without the target file → use the Edit tool for one-line changes, and check the diff.
- **Manual prod deploy failed at TEST** → the coverage action needs a pull request or a push, and fails on `workflow_dispatch` → skip that step on dispatch.
- **`always()` allowed deploys after cancel** → use `!cancelled()`.
- **The first `ANALYSIS` gate let a manual run skip bandit** → the gate only checked pip-audit's result. Analysis now stays required on every deploy.
- **Deploy in `ci.yml` used the pushed commit, not the tested one** → moved deploys to their own workflows, and pinned checkout to `head_sha`.

## Still unclear

- GitHub's rule for queued runs in the same concurrency group. Two pending master runs can cancel each other, so a deploy may be dropped. Not fixed.
- Check-run names: the prod gate matches job ids (`build`, `lint`, `test`, `analysis`). Confirm on the first real prod run.
- The coverage action's Docker image is a mutable tag, so its commit pin does not fix what runs.
