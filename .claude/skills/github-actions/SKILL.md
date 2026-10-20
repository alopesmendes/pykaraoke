---
name: github-actions
description: GitHub Actions conventions for pykaraoke. Workflow anatomy, uv caching, Postgres service containers, least-privilege permissions, deploy gating on CI, environments and approval gates. Use when creating or editing anything under .github/workflows/, when CI is red or slow, or when adding a secret, an environment, or a deploy step.
---

# GitHub Actions (pykaraoke)

Four workflows. `ci.yml` checks the code: BUILD, LINT, TEST, ANALYSIS/SECURITY, plus pip-audit and
the coverage jobs. Two deploy workflows wait for it: `deploy-dev.yml` (after a push to master) and
`deploy-prod.yml` (manual, with a reviewer). The pipeline as a whole is documented in
`docs/CI-CD.md`.

## The workflow header

```yaml
name: CI

on:
  push:
    branches: [master]
  pull_request:
  schedule:
    - cron: "0 6 * * 1"

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

Three rules behind that block:

1. **`permissions` is always explicit and always minimal.** Default `contents: read`. Add
   `contents: write` only in a job that pushes: a deploy (the tag) and coverage-badge (the data
   branch). Jobs that run project code (TEST, ANALYSIS) stay read-only, so a compromised dependency
   or conftest never sees a write token. `id-token: write` only for OIDC. Never leave the repository
   default in place.
2. **`concurrency` cancels only pull request runs.** A force-push does not burn minutes on a stale
   commit. Pushes to `master` always finish, since the deploy waits on them. Deploy workflows have
   their own group with no `cancel-in-progress`: a half-cancelled deploy is worse than a wasted
   minute. Keep one workflow-level block per file; a second one would cancel a running deploy.
3. **`on.pull_request` without a branch filter**, `on.push` limited to `master`. Otherwise every
   PR runs twice.

## The uv setup block

```yaml
    steps:
      - uses: actions/checkout@v7

      - name: Install uv
        uses: astral-sh/setup-uv@v10.1.0
        with:
          python-version: "3.13"
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Install dependencies
        run: uv sync --locked --all-groups
```

- `--locked` fails if `uv.lock` is out of date with `pyproject.toml`. That is the point: CI must
  never silently resolve different versions than your machine.
- `python-version: "3.13"` is pinned on every `setup-uv` step. Unpinned, uv picks the newest CPython,
  and `psycopg-binary` has no wheel for 3.15. `tests/test_ci_workflow.py` fails if one drifts.
- `cache-dependency-glob: uv.lock` keys the cache on the lockfile, so the cache invalidates
  exactly when dependencies change.
- Pin actions to a major tag (`@v7`) when the maintainer publishes one. Do not float on `@main`.
  **Some don't publish one at all**: `astral-sh/setup-uv` only ever tags exact versions
  (`v10.1.0`, never a floating `v10`); a pin to `@v10` fails outright. Check
  `gh api repos/<owner>/<repo>/git/refs/tags` before writing the pin, not after CI fails on it.
- Third-party actions that run with a write token are pinned to a commit SHA. The coverage action is
  one: `py-cov-action/python-coverage-comment-action@<sha> # v4.5`.

## One Python version, no matrix

The project runs Python 3.13 only, the version in the `Dockerfile`. A second version would test an
interpreter production never runs. Linting once is enough.

## Postgres service container

Not in the `test` job yet. Today's `DATABASE_URL` is blank (SQLite fallback) and there are zero
models until Milestone 2. Add this block to the `test` job in `ci.yml` alongside the first real
migration, not speculatively ahead of it.

```yaml
    services:
      postgres:
        image: postgres:17-alpine
        env:
          POSTGRES_USER: pykaraoke
          POSTGRES_PASSWORD: pykaraoke
          POSTGRES_DB: pykaraoke_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
```

The `--health-cmd` block is not optional: without it the test step starts before Postgres accepts
connections and fails intermittently. The job then reaches it at
`DATABASE_URL: postgres://pykaraoke:pykaraoke@localhost:5432/pykaraoke_test`.

## Secrets and environments

| Kind | Where | Example |
|---|---|---|
| Non-secret config | `env:` in the workflow | `DJANGO_SETTINGS_MODULE` |
| Repository secret | `${{ secrets.X }}` | `RENDER_DEPLOY_HOOK_DEV`, `RENDER_DEPLOY_HOOK_PROD` |
| Environment secret | `environment: production` + `${{ secrets.X }}` | a token only prod may read |
| Built-in | `${{ secrets.GITHUB_TOKEN }}` | `gh` calls in a workflow, no PAT needed |

**Never `echo` a secret**, never put one in a job name or an artifact. GitHub masks known secrets
in logs, but not values you derive from them.

`environment:` gives two things worth having: scoped secrets, and **required reviewers**.
That is how `deploy-prod.yml` waits for a human click instead of a branch rule.

## Deploy gating on CI

Deploys are separate workflows, so they cannot run before CI has finished. Two ways to gate:

- **Push to master (dev):** `on: workflow_run` on the CI workflow, with
  `if: github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.event == 'push' && github.event.workflow_run.head_branch == 'master'`.
  Check out `ref: github.event.workflow_run.head_sha`, never the branch: master may have moved on.
  The `event` check matters: a scheduled CI run on master also has `head_branch: master`.
- **Manual (prod):** `on: workflow_dispatch`. A first job, `verify`, has no environment and reads the
  check runs for `github.sha`. It requires the jobs it depends on to be `success`. A second job,
  `deploy`, has `needs: verify` and `environment: production`, so the reviewer is asked only after
  the check passed.

```yaml
  verify:
    permissions:
      checks: read
    steps:
      - name: Check CI passed for this commit
        env:
          GH_TOKEN: ${{ github.token }}
          SHA: ${{ github.sha }}
        run: |
          for job in build lint test analysis; do
            conclusion="$(gh api "repos/$GITHUB_REPOSITORY/commits/$SHA/check-runs" --paginate \
              -q ".check_runs[] | select(.name == \"$job\") | .conclusion" | tail -n 1)"
            [ "$conclusion" = success ] || { echo "$job: ${conclusion:-no run}" >&2; exit 1; }
          done
```

`!cancelled()`, not `always()`, on the job that deploys. `always()` would also run it after a
cancelled run. The `needs.<job>.result` you read must be listed in that job's `needs:`. A job
whose `needs` failed is skipped, so the gate has to be an explicit `if:`.

The hook is an environment-independent repository secret in each deploy workflow, and the deploy
step passes it through `env:`. Configure the reviewers in **Settings → Environments**, not in YAML.
Only deploy jobs check out with `fetch-depth: 0`, because `next-version.sh` reads every tag.

## Verify a workflow before pushing it

`uvx --from actionlint-py actionlint .github/workflows/*.yml`. Real schema, expression syntax,
and shellcheck-on-`run:` checks, not just "is this valid YAML." Catches most mistakes with no
GitHub Actions minutes spent finding out the hard way.

## Debugging a red run

1. `gh run list --limit 5` then `gh run view <id> --log-failed`. Read the actual failure.
2. Reproduce locally first: `make check` runs the same gates.
3. `uv sync --locked` failing locally means the lockfile is stale → `uv lock` and commit it.
4. Only then touch the YAML.

## See also

- What each workflow gates: `docs/CI-CD.md`
- Dockerfile and the Render deploy flow (CI builds no image): skill `devops`
- Local equivalents of every CI gate: the `Makefile`
