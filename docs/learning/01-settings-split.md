# 01: Settings split by environment

*What to learn from splitting `settings.py` into base, dev and prod. Milestone 1, issue #4.*

**Shipped:** `DEBUG` and the HTTPS block are fixed per environment, and CI checks the prod one.
**Files:** `pykaraoke/settings/{base,dev,prod}.py`, `manage.py`, `Dockerfile`, `pyproject.toml`,
`.github/workflows/security.yml`

---

## Concepts

- **`DJANGO_SETTINGS_MODULE`**: the env var that tells Django which module is "the settings".
  Whoever imports Django first picks it: `manage.py`, `wsgi.py`, pytest, the Dockerfile. If two
  of them disagree, you test one config and ship another.
- **`os.environ.setdefault`**: `manage.py` only sets the module if nothing set it already. That is
  why CI can override it, and why forgetting to override it silently gives you dev.
- **`from .base import *`**: dev and prod start from base and overwrite names. Last assignment
  wins. `# noqa: F403` silences Ruff's star-import rule, which is fine here on purpose.
- **Deploy check settings**: `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`,
  `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`, `DEBUG`. Each is only correct behind HTTPS.
- **HSTS**: a browser caches "https only" for `SECURE_HSTS_SECONDS`. Hard to undo, so dev sets 0.
- **Hardcode vs env var for `DEBUG`**: an env var can be forgotten or mistyped into prod. A prod
  module cannot.

## Docs to read

- [ ] [Deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/):
      what each warning asks for
- [ ] [Settings: `DJANGO_SETTINGS_MODULE`](https://docs.djangoproject.com/en/6.1/topics/settings/#designating-the-settings)
- [ ] [`SECURE_HSTS_SECONDS`](https://docs.djangoproject.com/en/6.1/ref/settings/#secure-hsts-seconds):
      read the warning about rollout
- [ ] [`SECURE_PROXY_SSL_HEADER`](https://docs.djangoproject.com/en/6.1/ref/settings/#secure-proxy-ssl-header):
      needed behind a proxy, not set yet

## Hands-on

- [ ] Run `uv run python manage.py check --deploy --tag security` and count the warnings. Rerun
      with `DJANGO_SETTINGS_MODULE=pykaraoke.settings.prod` and a throwaway secret key. Explain the
      difference.
- [ ] Set `SESSION_COOKIE_SECURE = True` in `dev.py`, log in to `/admin/` on `http://localhost`,
      and see what fails. Revert.
- [ ] Remove the `DJANGO_SETTINGS_MODULE` line from `security.yml` locally and read which five
      warnings come back.
- [ ] Find every place that names a settings module (`grep -rn SETTINGS_MODULE`). Which ones pick
      dev, which prod?

## Quiz

1. `manage.py` has `setdefault("DJANGO_SETTINGS_MODULE", "pykaraoke.settings.dev")`. CI sets the
   var to prod. Which one wins?
   <details><summary>Answer</summary>CI. `setdefault` does nothing when the key already exists.</details>
2. Why does the test suite run against prod settings and not dev?
   <details><summary>Answer</summary>So a regression in the security block fails a test before it
   ships. Dev has it all switched off.</details>
3. Why is `SESSION_COOKIE_SECURE = True` broken on `http://localhost`?
   <details><summary>Answer</summary>The browser refuses to send a Secure cookie over plain HTTP,
   so the session never comes back and login fails.</details>
4. What does `SECURE_HSTS_SECONDS = 31536000` make a browser do?
   <details><summary>Answer</summary>Refuse plain HTTP to that host for a year, even if the server
   is fixed.</details>
5. Why does `base.py` not set `DEBUG`?
   <details><summary>Answer</summary>Anything environment-specific in base could leak into prod.
   Each environment must state it explicitly.</details>

## Gotchas hit

- **CI deploy check showed W004, W008, W012, W016, W018** → `security.yml` still set the old
  `DJANGO_DEBUG=False`, which nothing reads now, and `manage.py` defaulted to dev → set
  `DJANGO_SETTINGS_MODULE: pykaraoke.settings.prod` in the step.
- **Lint and security jobs failed at `uv sync --locked`** (`psycopg-binary` has no `cp315`
  wheel) → those jobs did not set `python-version`, so `uv` took the newest CPython → pinned
  `"3.13"` in both, like the Dockerfile.
- **`make audit` still prints those warnings** → it runs on dev, on purpose → not a bug.

## Still unclear

- `SECURE_PROXY_SSL_HEADER`: needed once a reverse proxy terminates TLS, and only safe if the
  proxy overwrites the header. Decide with the deploy provider (Milestone 3).

## Decision

- **`ENV DJANGO_SETTINGS_MODULE=pykaraoke.settings.prod` in the Dockerfile.** If the variable is
  forgotten at runtime, `manage.py` would fall back to dev (`DEBUG=True`). Baking in prod makes
  the forgotten case the strict one. `docker run -e ...` still overrides it for a local dev run.
