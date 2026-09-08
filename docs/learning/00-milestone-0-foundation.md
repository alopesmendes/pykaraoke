# 00 — Foundation & infrastructure

*What to learn from Milestone 0. Docs, AI workflow, then CI/CD.*

**Shipped:** a documented, agent-aware repo. Tooling and pipelines land chunk by chunk in Phase 0.2.
**Files:** `docs/`, `.github/`, `.claude/`, `CLAUDE.md`

---

## Concepts

Phases 0.1 and 0.3 (done — skim these, you already know the shape):

- **Doc ownership** — every kind of change has exactly one doc that owns it. Drift happens when
  nobody can say which file should have been updated.
- **Skill vs agent vs rule** — a skill changes how the model works; an agent does a job in its own
  context and reports back; a rule is enforced by the harness and cannot be argued with.
- **Permission precedence** — `deny` → `ask` → `allow`, first match wins, specificity is
  irrelevant. A broad `deny` cannot carry an allowlist exception.

Phase 0.2 (coming — these are the ones to actually learn):

- **Lockfile vs version range** — `pyproject.toml` says what you accept; `uv.lock` says what you
  got. CI installs with `--locked` so it can never resolve something your machine did not see.
- **Dependency groups** — why `pytest` and `ruff` must not exist in the production image.
- **Twelve-factor config** — why a hardcoded `SECRET_KEY` in `settings.py` is a bandit finding and
  not just untidy.
- **Local gate vs CI gate** — pre-commit is fast and skippable; CI is slow and authoritative. Both
  exist on purpose.
- **Service containers and healthchecks** — why a test job without `pg_isready` fails
  intermittently rather than never.
- **Multi-stage Docker builds** — build tools in one stage, runtime in another, and why layer order
  decides your rebuild time.
- **Least-privilege `permissions:`** — why every workflow declares `contents: read` instead of
  inheriting the repository default.

## Docs to read

- [ ] [uv — projects & lockfiles](https://docs.astral.sh/uv/concepts/projects/) — `uv sync`,
      `uv.lock`, dependency groups
- [ ] [Ruff rules](https://docs.astral.sh/ruff/rules/) — look up `DJ`, `B`, `S` specifically
- [ ] [Django — deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
      — what `check --deploy` actually asserts
- [ ] [Django 6.1 release notes](https://docs.djangoproject.com/en/6.1/releases/6.1/) — fetch modes
      and `FETCH_PEERS`
- [ ] [pytest-django](https://pytest-django.readthedocs.io/) — `django_db`, `django_assert_num_queries`
- [ ] [GitHub Actions — service containers](https://docs.github.com/actions/using-containerized-services/about-service-containers)
- [ ] [Claude Code — permissions](https://code.claude.com/docs/en/permissions) — rule syntax

## Hands-on

- [ ] Open `.claude/settings.json` and predict what happens for `git push origin master`. Then ask
      Claude to run it and confirm.
- [ ] Read one skill end to end (`clean-architecture` is the shortest) and find one rule you
      disagree with. Change it — it is your repo.
- [ ] After chunk 1: delete `.venv/`, run `uv sync`, time it.
- [ ] After chunk 1: add a deliberately bad line (`import os` unused, a bare `except:`) and run
      `uv run ruff check .`. Read the rule code it prints, then look that code up.
- [ ] After chunk 3: break the smoke test on purpose and read the pytest output top to bottom.
- [ ] After chunk 6: push a branch with a lint error and read the failing Actions log.

## Quiz

1. `deny` has `Bash(git push *)` and `allow` has `Bash(git push origin dev)`. What happens?
   <details><summary>Answer</summary>Denied. Deny is evaluated first and a match ends it — a
   narrower allow rule never gets a chance.</details>
2. Why does the Dockerfile copy `pyproject.toml` and `uv.lock` before the source code?
   <details><summary>Answer</summary>Docker caches per layer. Copying dependencies first means a
   source-only change reuses the cached install instead of reinstalling everything.</details>
3. What does `uv sync --locked` do that `uv sync` does not?
   <details><summary>Answer</summary>It fails if `uv.lock` is out of date with `pyproject.toml`
   instead of silently re-resolving — so CI can never install versions you never tested.</details>
4. What is the difference between a skill and an agent here?
   <details><summary>Answer</summary>A skill loads conventions into the current conversation and
   changes how Claude works. An agent runs in its own fresh context with a restricted toolset and
   returns only its report.</details>
5. Why 404 and not 403 for an invalid access token?
   <details><summary>Answer</summary>403 confirms the event exists. 404 leaks nothing.</details>
6. Why must `DJANGO_SECRET_KEY` come from the environment even for a private hobby site?
   <details><summary>Answer</summary>The repo is on GitHub. A committed key signs sessions, CSRF
   tokens and password resets — anyone reading the repo can forge them.</details>

## Gotchas hit

*Filled in during Phase 0.2, as they happen.*

### Chunk 1 — `pyproject.toml`

- **`ruff format` also formats Python code blocks inside Markdown.** Two `SKILL.md` files failed
  `ruff format --check` before a single line of app code existed. Kept on purpose: doc samples now
  obey the same style as real code. If a snippet must keep a hand-made line break, exclude that
  path in `[tool.ruff] extend-exclude`.
- **`S105` fired on the generated `SECRET_KEY` immediately** — `ruff check .` exits 1 on a
  brand-new Django project. That is not noise; it is chunk 2's whole reason for existing.
- **The venv runs Python 3.14.4 while `target-version = "py313"`.** Those are different things:
  `requires-python` picks the interpreter, `target-version` tells Ruff which syntax it may
  rewrite *to*. Setting py313 means generated fixes stay valid on 3.13 as well.
- **`uv sync --no-dev` genuinely removes the dev group** — verified: `import pytest` then raises
  `ModuleNotFoundError`. That is what keeps pytest and ruff out of the production image.

## Still unclear

*Add anything Claude wrote that you could not follow line by line.*

- `[tool.uv] package = false` — why an application needs it and a library does not.
- What `uv.lock`'s per-package hashes actually protect against.
-
