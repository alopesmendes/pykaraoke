---
name: devops
description: Local and deploy infrastructure for pykaraoke — uv, the Makefile, Docker and docker-compose, environment variables, Postgres, and the deploy skeleton. Use when changing Dockerfile or docker-compose.yml, adding an environment variable, setting up local Postgres or email, or wiring the deployment target.
---

# DevOps (pykaraoke)

Small private app. Priorities in order: **reproducible**, **cheap**, **easy to hand to future
you**. No Kubernetes, no Terraform.

## Toolchain

| Concern              | Tool                     | Why                                                |
|----------------------|--------------------------|----------------------------------------------------|
| Python + deps + venv | `uv`                     | One tool, `uv.lock` committed, fast CI cache       |
| Lint/format          | `ruff`                   | Replaces Black + Flake8 + isort                    |
| Task runner          | `make`                   | Already on every machine; self-documenting targets |
| Local services       | `docker compose`         | Postgres 17 + mailpit, disposable                  |
| Image                | multi-stage `Dockerfile` | Same artifact runs in CI and in prod               |

## Environment variables

Twelve-factor: **config comes from the environment, never from a committed file.**

| Variable               | Local default            | Notes                                           |
|------------------------|--------------------------|-------------------------------------------------|
| `DJANGO_SECRET_KEY`    | dev-only value in `.env` | Real value is a deploy secret. Never committed. |
| `DJANGO_DEBUG`         | `True`                   | Always `False` in staging and production        |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1`    | Comma-separated                                 |
| `DATABASE_URL`         | `sqlite:///db.sqlite3`   | `postgres://...` when compose is up             |
| `EMAIL_URL`            | `smtp://localhost:1025`  | mailpit locally, real SMTP in prod              |

`.env` is gitignored. `.env.example` is committed and lists every key with a safe placeholder —
when you add a variable, add it to `.env.example` **in the same change**, or the next person
gets a `ImproperlyConfigured` on a fresh clone.

`.claude/settings.json` denies reading `.env`, so Claude never sees real values.

## Local services

```yaml
services:
  postgres:
    image: postgres:17-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pykaraoke"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
  mailpit:
    image: axllent/mailpit
    ports: ["1025:1025", "8025:8025"]
```

- Postgres 17 because Django 6.1 requires PostgreSQL 15+.
- **Named volume**, not a bind mount — a bind mount on macOS is slow and permission-cursed.
- mailpit catches the confirmation emails and shows them at `http://localhost:8025`. No real mail
  is ever sent in development.
- `make db-up` / `make db-down`. Data survives `down`; `docker compose down -v` wipes it.

Docker is optional: `DATABASE_URL=sqlite:///db.sqlite3` runs the whole app with no daemon. Use
Postgres before shipping anything that relies on constraints or migrations behaving identically.

## Dockerfile shape

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

FROM python:3.13-slim-bookworm AS runtime
RUN useradd --create-home --uid 1000 app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app . /app
USER app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["gunicorn", "pykaraoke.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Four things that matter:
1. **Multi-stage** — build tools never reach the runtime image.
2. **Copy `pyproject.toml` + `uv.lock` before the source** so a code change does not bust the
   dependency layer.
3. **`--no-dev`** — pytest and ruff have no business in production.
4. **Non-root `USER`** — a container running as root is a finding, not a preference.

## Deploy skeleton

`deploy.yml` today: build the image, push to `ghcr.io/alopesmendes/pykaraoke`, then two gated jobs
(`staging` → `production`) whose provider step is a marked `TODO`. Nothing is wired to a host yet —
that decision lands in Milestone 3.

When a provider is chosen, the only edits should be inside those two steps. If a provider needs
changes anywhere else in the pipeline, that is a smell.

Production checklist before the first real deploy:
- [ ] `DJANGO_DEBUG=False`, real `DJANGO_SECRET_KEY`, real `DJANGO_ALLOWED_HOSTS`
- [ ] `python manage.py check --deploy` clean
- [ ] HTTPS, `SECURE_HSTS_SECONDS`, secure + `HttpOnly` cookies
- [ ] Managed Postgres with automated backups, reachable only on the private network
- [ ] `collectstatic` served by WhiteNoise or the platform's CDN
- [ ] The data-purge job scheduled (see `docs/SECURITY.md`)

## See also

- Pipeline YAML conventions: skill `github-actions`
- Data retention and secrets policy: `docs/SECURITY.md`
- Setup steps for a fresh machine: `docs/SETUP.md`
