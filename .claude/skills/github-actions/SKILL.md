---
name: github-actions
description: GitHub Actions conventions for pykaraoke — workflow anatomy, uv caching, matrix builds, Postgres service containers, least-privilege permissions, environments and approval gates. Use when creating or editing anything under .github/workflows/, when CI is red or slow, or when adding a secret, an environment, or a deploy step.
---

# GitHub Actions (pykaraoke)

Four workflows, one job each unless stated: `lint.yml`, `test.yml`, `security.yml`, `deploy.yml`.
The pipeline as a whole is documented in `docs/CI-CD.md`.

## Every workflow starts the same way

```yaml
name: Lint

on:
  push:
    branches: [master]
  pull_request:

permissions:
  contents: read

concurrency:
  group: lint-${{ github.ref }}
  cancel-in-progress: true
```

Three rules behind that block:

1. **`permissions` is always explicit and always minimal.** Default `contents: read`. Add
   `packages: write` only in the job that pushes to GHCR, `id-token: write` only for OIDC.
   Never leave the repository default in place.
2. **`concurrency` with `cancel-in-progress`** so a force-push does not burn minutes on a stale
   commit. Never cancel in progress on `deploy.yml` — a half-cancelled deploy is worse than a
   wasted minute.
3. **`on.pull_request` without a branch filter**, `on.push` limited to `master`. Otherwise every
   PR runs twice.

## The uv setup block

```yaml
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Install dependencies
        run: uv sync --locked --all-groups
```

- `--locked` fails if `uv.lock` is out of date with `pyproject.toml`. That is the point: CI must
  never silently resolve different versions than your machine.
- `cache-dependency-glob: uv.lock` keys the cache on the lockfile, so the cache invalidates
  exactly when dependencies change.
- Pin actions to a major tag (`@v4`). Do not float on `@main`.

## Matrix

```yaml
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.13", "3.14"]
```

`fail-fast: false` so one Python version failing still tells you about the other. Matrix only on
`test.yml` — linting once is enough.

## Postgres service container

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
| Repository secret | `${{ secrets.X }}` | `DJANGO_SECRET_KEY` for the deploy job |
| Environment secret | `environment: production` + `${{ secrets.X }}` | provider token |
| Built-in | `${{ secrets.GITHUB_TOKEN }}` | pushing to GHCR — no PAT needed |

**Never `echo` a secret**, never put one in a job name or an artifact. GitHub masks known secrets
in logs, but not values you derive from them.

`environment:` gives two things worth having: scoped secrets, and **required reviewers** —
which is how `deploy-production` waits for a human click instead of a branch rule.

## Deploy gating

```yaml
  deploy-production:
    needs: deploy-staging
    environment:
      name: production
      url: ${{ steps.deploy.outputs.url }}
```

`needs:` chains the jobs; the `production` environment's protection rules hold the run until
approved. Configure the reviewers in **Settings → Environments**, not in YAML.

## Debugging a red run

1. `gh run list --limit 5` then `gh run view <id> --log-failed` — read the actual failure.
2. Reproduce locally first: `make check` runs the same gates.
3. `uv sync --locked` failing locally means the lockfile is stale → `uv lock` and commit it.
4. Only then touch the YAML.

## See also

- What each workflow gates: `docs/CI-CD.md`
- Docker image built by `deploy.yml`: skill `devops`
- Local equivalents of every CI gate: the `Makefile`
