# syntax=docker/dockerfile:1

# --- builder --------------------------------------------------------------
# Has uv and a C toolchain. Only its built .venv reaches the runtime image.
# Copying pyproject.toml + uv.lock before the source means a source-only
# change reuses this layer instead of reinstalling everything.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# --- runtime ----------------------------------------------------------------
# Plain python:slim: no uv, no compiler, no dev dependencies. Non-root user:
# a container running as root is a finding, not a preference.
FROM python:3.13-slim-bookworm AS runtime
RUN useradd --create-home --uid 1000 app
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app . /app
ENV PATH="/app/.venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE="pykaraoke.settings.prod"
# Runs as root, so the files land root-owned and readable by the app user.
# The secret is a placeholder for this one command: collectstatic needs a
# key to load settings, not a real one, and it is not kept in the layer.
RUN DJANGO_SECRET_KEY=collectstatic-only python manage.py collectstatic --noinput
# The SQLite file lives next to manage.py, so the app user must own /app.
RUN chown app:app /app
USER app
EXPOSE 8000
# Render sets PORT. The probe sends the first ALLOWED_HOSTS entry as Host,
# because Django rejects an unknown Host with 400 and the probe would fail.
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; host = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')[0]; port = os.environ.get('PORT', '8000'); urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}/health/', headers={'Host': host}), timeout=2)"]
ENTRYPOINT ["/app/docker-entrypoint.sh"]
