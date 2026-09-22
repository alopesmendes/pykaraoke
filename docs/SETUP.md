# Setup

*Fresh clone to a running dev server, step by step.*

## Prerequisites

| Tool | Required | Why |
|---|---|---|
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | yes | Python, the venv, and every dependency: one tool |
| git | yes | obviously |
| [Docker](https://docs.docker.com/get-docker/) + Compose | optional | Postgres + mailpit locally, instead of SQLite + console email |

Nothing else. No system Python version to manage: `uv` installs the interpreter
`pyproject.toml` asks for (`>=3.13`) if it isn't already on your machine.

## 1. Clone

```bash
git clone https://github.com/alopesmendes/pykaraoke.git
cd pykaraoke
```

## 2. Configure your environment

```bash
cp .env.example .env
```

Then generate a real secret key and put it in `.env`:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Replace `DJANGO_SECRET_KEY=change-me` with the generated value. Everything else in `.env.example`
already has a working local default:

| Variable | Default | Change it when |
|---|---|---|
| `DJANGO_SECRET_KEY` | `change-me` (must replace) | never commit a real one, dev-only |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | rarely, for local dev |
| `DATABASE_URL` | blank → SQLite | you want Postgres, see step 5 |
| `EMAIL_URL` | blank → console backend | you want mailpit, see step 5 |

`.env` is gitignored and `.claude/settings.json` denies Claude from ever reading it. Real
secrets never need to pass through an AI session.

`DEBUG` is no longer an env var: `manage.py` defaults `DJANGO_SETTINGS_MODULE` to
`pykaraoke.settings.dev`, `wsgi.py`/`asgi.py` (the deploy entrypoints) default to `.prod`, and
DEBUG is hardcoded in whichever one loads. Override `DJANGO_SETTINGS_MODULE` yourself only to
run one against the other's settings on purpose.

## 3. Install

```bash
make install
```

Runs `uv sync --all-groups` (creates `.venv`, installs every dependency group) and
`uv run pre-commit install` (activates the local git hook from `.pre-commit-config.yaml`).

## 4. Run migrations

```bash
make migrate
```

Applies Django's built-in migrations (admin, auth, sessions, ...) to `db.sqlite3`. There's
nothing app-specific to migrate yet. The `karaoke` app arrives in Milestone 1.

## 5. (Optional) Start Postgres + mailpit

Skip this to keep using SQLite and the console email backend. That's a complete, working setup.

```bash
make db-up
```

Then in `.env`:

```bash
DATABASE_URL=postgres://pykaraoke:pykaraoke@localhost:5432/pykaraoke
EMAIL_URL=smtp://localhost:1025
```

Re-run `make migrate` after switching. SQLite and Postgres are separate databases. Mailpit's web
UI is at <http://localhost:8025>; `make db-down` stops both containers (data survives; `docker
compose down -v` wipes it).

> **Not verified on this project's own dev machine**. Docker isn't installed there. If
> `make db-up` behaves unexpectedly, that's the untested path; the SQLite default is the one
> that's actually been run.

## 6. Run the dev server

```bash
make dev
```

Visit <http://localhost:8000/admin/>. Django's admin login page should load. There's no
superuser yet:

```bash
make superuser
```

## 7. Before opening a PR

```bash
make check
```

Runs lint, tests, and the security audit. The same gates CI runs in `lint.yml`, `test.yml`, and
`security.yml`. See [CI-CD.md](CI-CD.md) for what each one actually checks.

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `ImproperlyConfigured: Set the DJANGO_SECRET_KEY environment variable` | no `.env`, or it wasn't copied from `.env.example` | step 2 |
| `OperationalError: connection to server ... refused` on `migrate` | `.env` has a `DATABASE_URL` pointing at Postgres, but `make db-up` was never run | run `make db-up`, or blank `DATABASE_URL` to fall back to SQLite |
| `ModuleNotFoundError` after pulling new changes | dependencies changed and `.venv` is stale | `make install` again |
| A commit is rejected or silently rewritten | the local git hooks (`pre-commit`, `prepare-commit-msg`) are doing their job | see [CONTRIBUTING.md](../CONTRIBUTING.md) for the commit format they enforce |

## See also

- What each `make` target actually runs: the `Makefile`, or `make help`
- Env vars, Docker, and the deploy skeleton in depth: skill `devops`
- The CI pipeline these same checks run in: [CI-CD.md](CI-CD.md)
