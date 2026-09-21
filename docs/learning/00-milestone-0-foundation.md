# 00: Foundation & infrastructure

*What to learn from Milestone 0. Docs, AI workflow, then CI/CD.*

**Shipped:** a documented, agent-aware repo. Tooling and pipelines land chunk by chunk in Phase 0.2.
**Files:** `docs/`, `.github/`, `.claude/`, `CLAUDE.md`

---

## Concepts

Phases 0.1 and 0.3 (done. Skim these, you already know the shape):

- **Doc ownership**: every kind of change has exactly one doc that owns it. Drift happens when
  nobody can say which file should have been updated.
- **Skill vs agent vs rule**: a skill changes how the model works; an agent does a job in its own
  context and reports back; a rule is enforced by the harness and cannot be argued with.
- **Permission precedence**: `deny` → `ask` → `allow`, first match wins, specificity is
  irrelevant. A broad `deny` cannot carry an allowlist exception.

Phase 0.2 (coming. These are the ones to actually learn):

- **Lockfile vs version range**: `pyproject.toml` says what you accept; `uv.lock` says what you
  got. CI installs with `--locked` so it can never resolve something your machine did not see.
- **Dependency groups**: why `pytest` and `ruff` must not exist in the production image.
- **Twelve-factor config**: why a hardcoded `SECRET_KEY` in `settings.py` is a bandit finding and
  not just untidy.
- **Local gate vs CI gate**: pre-commit is fast and skippable; CI is slow and authoritative. Both
  exist on purpose.
- **Service containers and healthchecks**: why a test job without `pg_isready` fails
  intermittently rather than never.
- **Multi-stage Docker builds**: build tools in one stage, runtime in another, and why layer order
  decides your rebuild time.
- **Least-privilege `permissions:`**: why every workflow declares `contents: read` instead of
  inheriting the repository default.

## Docs to read

- [ ] [uv projects & lockfiles](https://docs.astral.sh/uv/concepts/projects/): `uv sync`,
      `uv.lock`, dependency groups
- [ ] [Ruff rules](https://docs.astral.sh/ruff/rules/): look up `DJ`, `B`, `S` specifically
- [ ] [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/):
      what `check --deploy` actually asserts
- [ ] [Django 6.1 release notes](https://docs.djangoproject.com/en/6.1/releases/6.1/): fetch modes
      and `FETCH_PEERS`
- [ ] [pytest-django](https://pytest-django.readthedocs.io/): `django_db`, `django_assert_num_queries`
- [ ] [GitHub Actions service containers](https://docs.github.com/actions/using-containerized-services/about-service-containers)
- [ ] [Claude Code permissions](https://code.claude.com/docs/en/permissions): rule syntax

## Hands-on

- [ ] Open `.claude/settings.json` and predict what happens for `git push origin master`. Then ask
      Claude to run it and confirm.
- [ ] Read one skill end to end (`clean-architecture` is the shortest) and find one rule you
      disagree with. Change it. It is your repo.
- [ ] After chunk 1: delete `.venv/`, run `uv sync`, time it.
- [ ] After chunk 1: add a deliberately bad line (`import os` unused, a bare `except:`) and run
      `uv run ruff check .`. Read the rule code it prints, then look that code up.
- [ ] After chunk 3: break the smoke test on purpose and read the pytest output top to bottom.
- [ ] After chunk 6: push a branch with a lint error and read the failing Actions log.

## Quiz

1. `deny` has `Bash(git push *)` and `allow` has `Bash(git push origin dev)`. What happens?
   <details><summary>Answer</summary>Denied. Deny is evaluated first and a match ends it. A
   narrower allow rule never gets a chance.</details>
2. Why does the Dockerfile copy `pyproject.toml` and `uv.lock` before the source code?
   <details><summary>Answer</summary>Docker caches per layer. Copying dependencies first means a
   source-only change reuses the cached install instead of reinstalling everything.</details>
3. What does `uv sync --locked` do that `uv sync` does not?
   <details><summary>Answer</summary>It fails if `uv.lock` is out of date with `pyproject.toml`
   instead of silently re-resolving. So CI can never install versions you never tested.</details>
4. What is the difference between a skill and an agent here?
   <details><summary>Answer</summary>A skill loads conventions into the current conversation and
   changes how Claude works. An agent runs in its own fresh context with a restricted toolset and
   returns only its report.</details>
5. Why 404 and not 403 for an invalid access token?
   <details><summary>Answer</summary>403 confirms the event exists. 404 leaks nothing.</details>
6. Why must `DJANGO_SECRET_KEY` come from the environment even for a private hobby site?
   <details><summary>Answer</summary>The repo is on GitHub. A committed key signs sessions, CSRF
   tokens and password resets. Anyone reading the repo can forge them.</details>

## Gotchas hit

*Filled in during Phase 0.2, as they happen.*

### Chunk 1: `pyproject.toml`

- **`ruff format` also formats Python code blocks inside Markdown.** Two `SKILL.md` files failed
  `ruff format --check` before a single line of app code existed. Kept on purpose: doc samples now
  obey the same style as real code. If a snippet must keep a hand-made line break, exclude that
  path in `[tool.ruff] extend-exclude`.
- **`S105` fired on the generated `SECRET_KEY` immediately**: `ruff check .` exits 1 on a
  brand-new Django project. That is not noise; it is chunk 2's whole reason for existing.
- **The venv runs Python 3.14.4 while `target-version = "py313"`.** Those are different things:
  `requires-python` picks the interpreter, `target-version` tells Ruff which syntax it may
  rewrite *to*. Setting py313 means generated fixes stay valid on 3.13 as well.
- **`uv sync --no-dev` genuinely removes the dev group**: verified: `import pytest` then raises
  `ModuleNotFoundError`. That is what keeps pytest and ruff out of the production image.

### Chunk 2: `settings.py` env wiring

- **`env.db(KEY, default=...)` only falls back when `KEY` is absent. Not when it is present and
  blank.** `DATABASE_URL=` in `.env` (nothing after `=`) counts as "set", so `default=` never
  fires. It parses to `ENGINE=''`, which Django's dummy backend rejects with
  `ImproperlyConfigured`. Fix: read the raw value first (`env("DATABASE_URL", default="")`) and
  treat the empty string as absent yourself: `value or default`. Same bug, same fix, for
  `env.email_url()`.
- **Django 6.1 replaced `EMAIL_BACKEND`/`EMAIL_HOST`/... with a single `MAILERS` dict**:
  genuinely new, not a hallucination (checked twice against the real Django 6.1 docs after the
  claim looked suspicious). `django-environ`'s `env.email_url()` still only understands the old
  flat keys, so its result has to be mapped into `MAILERS["default"]["OPTIONS"]` by hand.
- **A permission deny rule can be too broad in a way you only discover by hitting it.**
  `Read(./.env.*)` was meant to protect `.env`, but it also blocked writing `.env.example`. A
  file that is supposed to be committed. Fixing your own `.claude/settings.json` from inside a
  session is itself denied (self-modifying permissions is treated as risky), so that edit and the
  `.env.example` write both had to happen by hand, outside Claude.
- **`target-version = "py313"` vs the installed interpreter (3.14.4) are different knobs**: worth
  repeating from chunk 1, it came up again reasoning about which Python `manage.py` actually runs.

### Chunk 3: `tests/` smoke test

- **`call_command("check", deploy=True)` doesn't raise on warnings by default**: `check`'s
  `fail_level` defaults to `ERROR`. Without `fail_level="WARNING"` the test would pass even with
  every one of chunk 2's 6 warnings present; it would test nothing.
- **Django's test framework forces the mail backend to `locmem`, always, no opt-out**: so that
  `mail.outbox` works in any test. Under Django 6.1's `MAILERS` dict, `--deploy`'s `mail.E001`
  check correctly flags `locmem` as a dev-only backend. Meaning the unscoped `--deploy` check
  **cannot pass under any Django test suite, in any project**, not just this one. `--tag security`
  scopes the test to what it can actually prove; `--list-tags --deploy` shows the other 13
  available tags (`admin`, `caches`, `mail`, `models`, ...) for when they're needed.
- **A test that cannot fail is not a test.** Proved this one could: broke `SECURE_SSL_REDIRECT`
  on purpose, watched the exact test fail with the exact warning, then restored it and watched all
  three pass again.
- **`pytest-env` sets environment variables before Django imports `settings.py`.** This matters
  because `settings.py` calls `env(...)` at *import time*. A fixture or `monkeypatch` that runs
  after Django is already loaded is too late to affect `SECRET_KEY`, `DEBUG`, or `ALLOWED_HOSTS`.

**Flagged for Milestone 2, not hit yet:** `DJANGO_DEBUG=False` for the whole test session means
`SECURE_SSL_REDIRECT = not DEBUG` is `True` during every test. Django's test client makes plain
HTTP requests by default, so `SecurityMiddleware` will redirect them (301/302) instead of hitting
the view. A view test will need `client.get(url, secure=True)`, or it will look like the view is
broken when the middleware is actually doing its job.

### Chunk 4: `Makefile` + `.pre-commit-config.yaml` + `.gitignore`

- **bandit does not auto-discover `pyproject.toml`.** `bandit -qr .` alone ignored
  `[tool.bandit] exclude_dirs` entirely and tried to scan `.venv`'s ~8,400 files (timed out at
  120s). `bandit -qr . -c pyproject.toml`. The explicit `-c`. Is what actually reads the config;
  without it, `exclude_dirs` silently does nothing. Confirmed with `-v`: dependency count in
  "Files excluded" jumped from missing entirely to 8,404 once `-c` was added.
- **`--fail-level WARNING` belongs in a test with a simulated production environment, not in a
  local `make` target that runs against the real `.env`.** First draft of `make audit` used
  `--fail-level WARNING`, which meant `make check` could never pass in normal local development:
  `DEBUG=True` and a placeholder key are *correct* for dev and *are* 6 expected warnings. The
  strict version only makes sense where `pytest-env` (chunk 3) or a CI secret (chunk 7) actually
  supplies production-shaped values. Caught by running `make check` for real, not by reasoning
  about it. The exit code lied until it was actually invoked.
- **A hook installed by `pre-commit install` and one symlinked by hand coexist without conflict**,
  confirmed by installing `pre-commit`'s hook and checking that `prepare-commit-msg` (from the
  earlier chunk 1.5 fix) was untouched. They are different files in `.git/hooks/`, one per git
  hook *type*. This only works because core.hooksPath was deliberately left unset.
  `pre-commit install` would have refused to run at all if `core.hooksPath` pointed elsewhere.
- **`.uv/` is not a real thing**: corrected from the original plan. `uv`'s cache lives at
  `~/.cache/uv`, global, never inside the project. Added to `.gitignore` on faith once, removed
  once actually checked with `uv cache dir`.
- **Proved the hook does real work, not just that it exists.** Staged a file with an unused
  import and 2-space-then-tabs mess plus a file with trailing whitespace and no final newline, ran
  the installed hook directly (not `git commit`. That stays denied), and watched `ruff check
  --fix`, `ruff format`, `trailing-whitespace`, and `end-of-file-fixer` each report "files were
  modified by this hook" and actually fix them. Done in a disposable `git worktree`, removed after.
- **`pre-commit run --all-files` catches files the per-commit hook never saw.** `.env.example` was
  missing its trailing newline. Written before the hook existed, never re-committed since, so
  `end-of-file-fixer` never ran on it. `--all-files` is the retroactive sweep; from here on it runs
  at the end of every chunk, not only reactively when something looks off.

### Chunk 5: `Dockerfile` + `docker-compose.yml`

- **`.dockerignore` is a completely separate mechanism from `.gitignore`.** `COPY . .` in the
  Dockerfile does not consult `.gitignore` at all. Without `.dockerignore`, the real local `.env`
  (which exists on disk, gitignored or not) would have been copied straight into an image layer.
  Two different files, two different jobs: one controls commits, the other controls build context.
- **A registry's `tags/list` API is paginated, and the default page isn't alphabetical or
  chronological.** `ghcr.io/astral-sh/uv:python3.13-bookworm-slim` looked like a 404 waiting to
  happen. The first 100-tag page had `python3.12` as the newest unversioned "python3.NN" tag and
  no `3.13` at all. Requesting `?n=1000` surfaced it immediately. The lesson isn't "trust the tag
  name because it looks plausible". It's **query the registry with a page size large enough to
  not silently drop the answer**, since a small, wrong page can look exactly like "doesn't exist."
- **Multi-stage builds don't run any `manage.py` command at build time in this Dockerfile. Not
  even `collectstatic`.** `settings.py` (chunk 2) calls `env("DJANGO_SECRET_KEY")` with no default
  at import time, so *any* `manage.py` invocation during `docker build`. With no real secrets
  available yet. Would crash the build. `collectstatic` and `migrate` are deliberately deferred
  to a real deploy step in a later milestone, run with real runtime secrets, not baked into the
  image.
- **No `version:` key at the top of `docker-compose.yml`.** Older tutorials show `version: "3.8"`;
  Compose V2 ignores it entirely (it's obsolete, not merely optional) and can print a warning.
  Omitted on purpose, not forgotten.

### Chunk 6: `lint.yml` + `test.yml`

- **Not every GitHub Action publishes a floating major-version tag.** `actions/checkout`,
  `actions/cache`, and `actions/upload-artifact` all maintain one (`@v7`, `@v6`, `@v7`). But
  `astral-sh/setup-uv` only ever tags exact versions (`v10.0.0`, `v10.0.1`, `v10.1.0`, never a bare
  `v10`). Checked with `gh api repos/<owner>/<repo>/git/refs/tags` before writing the pin, not
  after CI failed on it. Same lesson as chunk 5's image-tag miss, different registry.
- **A marketplace action for a tool already in `uv.lock` can silently use a different version of
  that tool.** `pre-commit/action` installs its own `pre-commit` via `pip`, independent of the
  exact version this project pinned in `dependency-groups.dev`. Used `uv run pre-commit run
  --all-files` directly instead. The same command chunk 4 already runs locally, so CI can never
  disagree with a local run about what "lint" means.
- **`coverage.py` warns on every single run for a `source` package that was never imported.**
  `[tool.coverage.run] source = ["pykaraoke", "karaoke"]` listed an app that doesn't exist until
  Milestone 1. Caught by actually running `pytest --cov` before writing `test.yml`, not by
  re-reading `pyproject.toml`. Fixed by dropping `karaoke` until the app is real.
- **An artifact path that doesn't exist yet doesn't fail the job. It just uploads nothing.**
  `test.yml` requested `htmlcov/` in `upload-artifact` before the pytest command actually asked
  for an HTML report (`--cov-report=html`). Would have "succeeded" while silently uploading an
  empty artifact. The kind of bug that looks fine in a green CI run.
- **`actionlint` (via `uvx --from actionlint-py actionlint`) checks the workflow schema and
  expression syntax for real**. Plain `yaml.safe_load` only proves the file parses as YAML, not
  that GitHub Actions can run it. Both workflows passed clean, but this is now a standing check for
  every future workflow file.
- **Postgres was deliberately left out of `test.yml` for now.** The `github-actions` skill already
  documents the exact service-container block to add. This chunk chose *when*, not *whether*: it
  arrives with Milestone 2's first real model, not speculatively ahead of it.

### Chunk 7: `security.yml` + `deploy.yml`

- **A local reusable workflow needs `workflow_call:` added to its own `on:` before anything else
  can `uses:` it.** `lint.yml` and `test.yml` already existed from chunk 6 with only `push` and
  `pull_request` triggers; `deploy.yml` calling them via `uses: ./.github/workflows/lint.yml`
  would have failed without adding `workflow_call:` to each one's trigger list first. One file
  still defines "lint passes": `deploy.yml` just requires it, with zero duplicated steps.
- **`needs:` only grants access to outputs of jobs listed in *that job's own* `needs:` array, not
  transitively.** `deploy-production` depends on `deploy-staging`, which depends on `build`. But
  reading `needs.build.outputs.image` from `deploy-production` required listing `build` in
  `deploy-production`'s own `needs: [build, deploy-staging]`, even though the ordering already
  went through `deploy-staging`. Ordering and data access are two separate things `needs:` grants.
- **`docker/metadata-action`'s `type=sha` already defaults to `format=short` with a `sha-` prefix**
  (`sha-860c190`). Checked the actual README before adding a redundant `format=short` that would
  have changed nothing. Chunks 5 and 6 both caught a *wrong* assumption about a tool; this one was
  right, but verified anyway rather than assumed, which is the actual habit worth keeping.
- **`security.yml`'s Django deploy check reuses the exact throwaway `DJANGO_SECRET_KEY` string
  from `tests/test_smoke.py`'s `pytest-env` block**, not a new one. One throwaway value, one place
  it's defined in spirit. A second random string floating around would just be one more thing to
  explain later as "also not a real secret."
- **GitHub auto-creates an `environment:` the first time a workflow references it**: `staging`
  and `production` do not need to exist in repo settings before this workflow can run. What does
  **not** happen automatically: required-reviewer protection on `production`. That is a manual
  step in Settings → Environments, outside any file in this repo, and nothing enforces it until
  someone does it.

### Chunk 8: `docs/SETUP.md` + `docs/CI-CD.md`

- **Writing the "what's missing" section forced a real audit, not a guess.** Re-reading `deploy.yml`
  and `test.yml` to list every gap surfaced one already known (no Postgres in `test.yml`, chunk 6)
  and named several that had only existed as scattered mental notes until now: no branch
  protection, no dependency-update automation, no monitoring. Writing the doc *is* the check here.
- **Every command and value in a setup doc is a claim someone will run verbatim.** Cross-checked
  `docs/SETUP.md`'s `DATABASE_URL`/`EMAIL_URL` example values and every `make` target it names
  against the real `docker-compose.yml` and `Makefile` before calling the doc done. A copy-pasted
  wrong port number in a setup guide is a worse bug than one in code, because nothing lints prose.
- **A doc can honestly document a path that was never tested**, rather than presenting it as if it
  were. `docs/SETUP.md`'s Postgres section says outright that `make db-up` hasn't run on this
  project's own dev machine (no Docker installed). The same gap chunk 5 flagged, now visible to
  whoever actually tries that path instead of buried in a chat transcript.
- **The mermaid diagram forced a decision `deploy.yml`'s YAML never had to make explicitly**:
  drawing `DEPLOY -->|requires| LINT` and `DEPLOY -->|requires| TEST` as separate edges from
  `deploy.yml` to both reused workflows made the reusable-workflow relationship from chunk 7
  visible at a glance. Something the YAML expresses correctly but not legibly.

**Phase 0.2 complete.** All eight chunks built, verified, and logged: `pyproject.toml`/`uv.lock`,
env-wired `settings.py`, the test suite, `Makefile`/pre-commit/`.gitignore`, `Dockerfile`/compose,
`lint.yml`/`test.yml`, `security.yml`/`deploy.yml`, and these two docs. `make check` passes; every
workflow validates with `actionlint`; nothing is committed by Claude. That's still yours to do.

## Still unclear

*Add anything Claude wrote that you could not follow line by line.*

- `[tool.uv] package = false`: why an application needs it and a library does not.
- What `uv.lock`'s per-package hashes actually protect against.
- Why `django-environ` treats "present but empty" and "absent" as different states instead of
  normalizing an empty string to "use the default".
- The pre-commit hook test printed a `VIRTUAL_ENV=...does not match the project environment path`
  warning from `uv`, then created a fresh `.venv` inside the worktree anyway. Worth understanding
  exactly what `uv run` resolves to when invoked outside the directory holding `pyproject.toml`.
- How `astral-sh/setup-uv`'s `python-version` input actually gets Python onto the runner. Does it
  download and install that version itself (like `uv python install` would locally), or does it
  only select among Python versions the GitHub-hosted runner image already ships?
- What `cache-from: type=gha` / `cache-to: type=gha,mode=max` in `docker/build-push-action`
  actually store and where. Is this the same cache GitHub Actions uses for `actions/cache`, or a
  separate mechanism specific to `buildx`?
-
