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
USER app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["gunicorn", "pykaraoke.wsgi:application", "--bind", "0.0.0.0:8000"]
