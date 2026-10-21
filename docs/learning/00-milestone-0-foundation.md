# 00: Foundation & infrastructure

*What to learn from Milestone 0. Docs, AI workflow, then CI/CD.*

**Shipped:** a documented, agent-aware repo, with `uv`, Ruff, pytest, Docker and the CI/CD pipelines in place.
**Files:** `docs/`, `.github/`, `.claude/`, `CLAUDE.md`, `pyproject.toml`, `Makefile`, `Dockerfile`

---

## Concepts

- **Doc ownership**: every kind of change has exactly one doc that owns it. Drift happens when
  nobody can say which file should have been updated.
- **Skill vs agent vs rule**: a skill changes how the model works; an agent does a job in its own
  context and reports back; a rule is enforced by the harness and cannot be argued with.
- **Permission precedence**: `deny` → `ask` → `allow`, first match wins. A broad `deny` cannot
  carry an allowlist exception.
- **Lockfile vs version range**: `pyproject.toml` says what you accept; `uv.lock` says what you
  got. CI installs with `--locked` so it can never resolve something your machine did not see.
- **Dependency groups and twelve-factor config**: `pytest` stays out of the production image;
  a hardcoded `SECRET_KEY` is a bandit finding.
- **Local gate vs CI gate**: pre-commit is fast and skippable; CI is slow and authoritative. Both
  exist on purpose.

## Docs to read

- [ ] [uv projects & lockfiles](https://docs.astral.sh/uv/concepts/projects/): `uv sync`,
      `uv.lock`, dependency groups
- [ ] [Ruff rules](https://docs.astral.sh/ruff/rules/): look up `DJ`, `B`, `S` specifically
- [ ] [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/):
      what `check --deploy` actually asserts
- [ ] [pytest-django](https://pytest-django.readthedocs.io/): `django_db`, `django_assert_num_queries`
- [ ] [GitHub Actions service containers](https://docs.github.com/actions/using-containerized-services/about-service-containers)
- [ ] [Claude Code permissions](https://code.claude.com/docs/en/permissions): rule syntax

## Hands-on

- [ ] Open `.claude/settings.json` and predict what happens for `git push origin master`. Then ask
      Claude to run it and confirm.
- [ ] Delete `.venv/`, run `uv sync`, time it.
- [ ] Add a deliberately bad line (`import os` unused, a bare `except:`) and run
      `uv run ruff check .`. Read the rule code it prints, then look that code up.
- [ ] Break the smoke test on purpose and read the pytest output top to bottom.
- [ ] Push a branch with a lint error and read the failing Actions log.

## Quiz

Answer from memory. Open the answer only after committing to one.

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
5. Why must `DJANGO_SECRET_KEY` come from the environment even for a private hobby site?
   <details><summary>Answer</summary>The repo is on GitHub. A committed key signs sessions, CSRF
   tokens and password resets. Anyone reading the repo can forge them.</details>

## Gotchas hit

- **`env.db(KEY, default=...)` ignores the default when `KEY` is set but blank.** `DATABASE_URL=`
  parses to `ENGINE=''` → `ImproperlyConfigured`. Fix: read the raw value, then `value or default`.
  Same fix for `env.email_url()`.
- **Django 6.1 replaced `EMAIL_BACKEND`/`EMAIL_HOST` with a `MAILERS` dict.** `django-environ`
  still returns the old flat keys, so the result is mapped into `MAILERS` by hand.
- **`Read(./.env.*)` was meant to guard `.env` but also blocked writing `.env.example`.** Too
  broad a deny rule is found only by hitting it.
- **`call_command("check", deploy=True)` passes on warnings by default** (`fail_level` is
  `ERROR`). Without `fail_level="WARNING"` the test proves nothing. A test that cannot fail is not
  a test: break the setting on purpose and watch it fail.
- **Django's test runner forces `locmem` mail, so the unscoped `--deploy` check can never pass.**
  `--tag security` scopes it to what it can prove.
- **`pytest-env` sets variables before `settings.py` runs.** A `monkeypatch` after Django loads is
  too late for `SECRET_KEY`, `DEBUG` or `ALLOWED_HOSTS`.
- **bandit does not read `pyproject.toml` on its own.** Without `-c pyproject.toml`,
  `exclude_dirs` does nothing and `.venv` (~8,400 files) gets scanned.
- **`make audit` with `--fail-level WARNING` made `make check` impossible locally**, because
  `DEBUG=True` and a placeholder key are correct for dev. The strict check belongs where production-shaped values exist.
- **`.dockerignore` is separate from `.gitignore`.** `COPY . .` ignores `.gitignore`, so without
  `.dockerignore` the local `.env` would land in an image layer.
- **`astral-sh/setup-uv` tags only exact versions** (`v10.0.0`, never `v10`). Check the refs before
  pinning.

## Still unclear

- `[tool.uv] package = false`: why an application needs it and a library does not.
- What `uv.lock`'s per-package hashes actually protect against.
- Why `django-environ` treats "present but empty" and "absent" as different states.
- Whether `setup-uv`'s `python-version` downloads Python or only selects a preinstalled one.
- What `cache-from: type=gha` in `docker/build-push-action` stores, and whether it is the same
  cache as `actions/cache`.
